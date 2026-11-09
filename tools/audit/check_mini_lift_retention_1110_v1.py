"""Retain simultaneous camera-spawned lifts and use actual native floor contact."""

from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path

from check_mini_camera_lifts_1110 import BASE, M, PIN, ROOT as R
from check_mini_funded_actor_1108_v3 import install, run, slim_fork
from check_mini_lift_admission_fast_1108_v1 import setup_main
from measure_mini_kernel_transport_1109 import compile_source, replace_one
from profile_mini_busy_1108_v1 import fixture

OUT = R / 'build/mini-lift-retention-1110'
CAMERA = R / 'build/mini-camera-lifts-v2-1110/proof.json'
KERNEL = R / 'build/mini-kernel-transport-1109/v2/kernel.s'
CONFIG = R / 'build/mini-fireball-gbc-1108/mini-lift.cfg'
FLOOR = R / 'tools/reference/mini_lift_floor_retention_1110_v1.inc'
ALLOCATOR = R / 'tools/reference/mini_lift_retention_1110_v1.inc'
CODE, COOKIE = 1048592 + 962 * 1024, 16 + 65 * 8192 + 0x1003
N = M.N
FIELDS = ('Enemy_Flag', 'Enemy_ID', 'Enemy_State', 'Enemy_X_Position',
          'Enemy_PageLoc', 'Enemy_Y_Position', 'Enemy_Y_HighPos', 'Enemy_BoundBoxCtrl',
          'Enemy_Y_Speed', 'Enemy_Y_MoveForce', 'YPlatformTopYPos', 'YPlatformCenterYPos')
EDGES = (560, 688, 864)


def patch(raw, offset, replacement, role):
    return dict(file_offset=offset, old_hex=raw[offset:offset+len(replacement)].hex(),
                new_hex=replacement.hex(), role=role)


def build(raw):
    data = json.loads(CAMERA.read_text())
    parent = install(raw, data['patches'])
    assert M.sha(raw) == data['parent_SHA256'] == PIN
    assert M.sha(parent) == data['expected_memory_only_SHA256']
    before = KERNEL.with_suffix('.bin').read_bytes()
    assert len(before) == 5117
    old_gate = bytes.fromhex('a55c38e902c902b0')
    camera_gate = bytes.fromhex('ad1e0729fec902d0')
    assert before.count(old_gate) == 1
    assert parent[CODE:CODE+5120] == before.replace(old_gate,camera_gate).ljust(5120,b'\xff')
    original = KERNEL.read_text()
    camera = replace_one(original,
        ' lda Player_PageLoc\n sec\n sbc #2\n cmp #2\n bcs @epoch',
        ' lda $071e\n and #$fe\n cmp #2\n bne @epoch')
    first, last = camera.index('MiniPlatformFloor:\n'), camera.index('MiniHostImportX:\n')
    proposed = camera[:first]+FLOOR.read_text()+camera[last:]
    code, labels = compile_source(OUT, proposed, CONFIG)
    assert len(code) <= 5120 and labels['MiniVectors'] == 0xa000
    assert labels['MiniPlatformFloor'] == 0xb0b7
    code = code.ljust(5120, b'\xff')
    assert parent[COOKIE:COOKIE+3] == bytes([167,41,1])
    digest = lambda payload:hashlib.sha256(payload).digest()[:13]
    assert parent[COOKIE+3:COOKIE+16] == digest(parent[CODE:CODE+7168])
    fullcookie = parent[COOKIE:COOKIE+3] + digest(code+parent[CODE+5120:CODE+7168])
    at = 16 + 36*8192 + 0x16d0
    assert parent[at:at+48] == bytes.fromhex(data['patches'][1]['new_hex'])
    allocator, _ = M.assemble(OUT/'allocate', ALLOCATOR.read_text(), 0xb6d0, 48)
    patches = [patch(parent, at, allocator.ljust(48,b'\xff'), 'allocate only a free native slot'),
               patch(parent, CODE, code, 'existing five Mini source code pages'),
               patch(parent, COOKIE, fullcookie, 'existing complete Mini payload cookie')]
    new = install(parent, patches)
    return parent, new, patches, labels, len(code.rstrip(b'\xff'))


def bundles(before, after):
    pair = [M.bundle(raw) for raw in (before, after)]
    for b in pair:
        b['segs']['lift'] = dict(start=str(0xbbcf),ooffs=str(16+24*8192+0x1bcf))
        b['syms']['MiniLiftTick'] = dict(val=str(0xbbcf),seg='lift')
    return pair


def snapshot(m, slot):
    return tuple(N.get(m,name,slot) for name in FIELDS)


def camera(m, right):
    N.put(m,ScreenLeft_X_Pos=(right-255)&255,ScreenLeft_PageLoc=(right-255)>>8,
          ScreenRight_X_Pos=right&255,ScreenRight_PageLoc=right>>8,CurrentBankC=2)
    m[0x5116] = 2


def spawn(m, right):
    camera(m, right)
    return N.invoke(m,'MiniLiftTick',a=0,x=0,y=0,p=0x31)


def constructor(old, new):
    worlds = [fixture(b,0,False,False) for b in (old, new)]
    m = worlds[1]
    setup_main(m, 420, 0, 0, 5)
    m[M.address(new,'Enemy_Flag')] = 1
    m[M.address(new,'Enemy_ID')] = 6
    natural = snapshot(m,0)
    history, existing = [], {}
    for index,right in enumerate((528,656,832)):
        spawn(m,right)
        assert all(snapshot(m,s)==v for s,v in existing.items()) and snapshot(m,0)==natural
        slot = m.ram[2][0x30b]-1
        assert slot not in existing and slot == 5-index
        state = snapshot(m,slot)
        assert state[:8] == (1,0x25,0x40,EDGES[index]&255,EDGES[index]>>8,192,1,5), state
        assert m.ram[2][0x30c] == (1<<(index+1))-1
        existing[slot] = state
        history.append(dict(right=right,slot=slot,world_x=EDGES[index],initial_top=192))
    for right in (532,660,836,913):
        spawn(m,right)
        assert all(snapshot(m,s)==v for s,v in existing.items())

    # The retained negative reproduces the old destructive reuse, on the
    # actual 1-1 native constructor and the exact camera admission path.
    previous = worlds[0]
    setup_main(previous,420,0,0,5)
    spawn(previous,528)
    old_slot = previous.ram[2][0x30b]-1
    spawn(previous,656)
    assert previous.ram[2][0x30b]-1 == old_slot
    assert (snapshot(previous,old_slot)[3]+256*snapshot(previous,old_slot)[4]) == 688

    # An occupied slot may be retried only once it is genuinely free and
    # still in the active camera window; no full-slot actor is rewritten.
    full = fixture(new,0,False,False)
    setup_main(full,420,0,0,5)
    for slot in range(6):
        full[M.address(new,'Enemy_Flag')+slot] = 1
        full[M.address(new,'Enemy_ID')+slot] = 6
    native = [snapshot(full,s) for s in range(6)]
    spawn(full,528)
    assert not full.ram[2][0x30c] and all(snapshot(full,s)==v for s,v in enumerate(native))
    full[M.address(new,'Enemy_Flag')+2] = 0
    spawn(full,533)
    assert full.ram[2][0x30c] == 1 and full.ram[2][0x30b] == 3
    assert all(snapshot(full,s)==v for s,v in enumerate(native) if s != 2)
    return m, history


def floor(seed, pc):
    m = seed
    m.raw_page(1,3)
    m.raw_page(2,2)
    c = N.NesMPU(memory=m,pc=pc)
    c.sp = 224
    c.stPushWord(0x5aff)
    run(c,lambda q:(q.pc,q.sp)==(0x5b00,224))
    return c


def test_floor(seed, pc):
    stats, samples = Counter(), Counter()
    native = seed.bundle
    old_slots = [5,4,3]
    for index, dx, previous, projected, latch, pose in product(
            range(3), [-7,-6,-1,0,30,31], [-1,0,1], [-1,0,1], [0,1,2],
            ['valid','disabled','other_kind','foreign_marker','culled']):
        m = slim_fork(seed)
        slot, edge = old_slots[index], EDGES[index]
        top = snapshot(m,slot)[5]
        if pose in ('other_kind','foreign_marker','culled'):
            name,v = {'other_kind':('Enemy_ID',6), 'foreign_marker':('Enemy_State',0),
                      'culled':('Enemy_Flag',0)}[pose]
            m[M.address(native,name)+slot] = v
        m.ram[2][0x227] = int(pose=='disabled')
        m.ram[2][0x250:0x252] = ((edge+dx)*16+15).to_bytes(2,'little')
        want = top-8
        m.ram[2][0x270:0x272] = ((want+projected)*16+15).to_bytes(2,'little')
        m.ram[2][0x30d] = 0 if latch==0 else slot+1 if latch==1 else old_slots[(index+1)%3]+1
        N.put(m,Player_Y_Position=top-32+previous,Player_Y_HighPos=1)
        c = floor(m,pc)
        hit = bool(c.p&1)
        expected = pose=='valid' and -6<=dx<=30 and (latch==1 or previous<=0<=projected)
        assert hit==expected, (index, dx, previous, projected, latch, pose, hit)
        assert m.ram[2][0x30d] == (slot+1 if hit else 0)
        assert int.from_bytes(m.ram[2][0x270:0x272],'little') == (want*16 if hit else (want+projected)*16+15)
        stats[index,pose,hit] += 1
        samples[hit] = max(samples[hit],c.processorCycles)
    return dict(cases=sum(stats.values()), supported_by_oldest=stats[0,'valid',True],
                supported_by_middle=stats[1,'valid',True], supported_by_latest=stats[2,'valid',True],
                worst_miss_cycles=samples[False],worst_hit_cycles=samples[True])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    before, after, patches, labels, size = build(BASE.read_bytes())
    previous, candidate = bundles(before,after)
    m, spawns = constructor(previous,candidate)
    result = test_floor(m,labels['MiniPlatformFloor'])
    refs = (Path(__file__), CAMERA, KERNEL, KERNEL.with_suffix('.bin'), CONFIG, FLOOR,
            ALLOCATOR, R/'src/object.s', R/'src/level_tiles.s')
    report = dict(passed=True, base_ROM_SHA256=M.sha(before), expected_memory_only_SHA256=M.sha(after),
        patches=patches, kernel_bytes=size, labels=labels, constructors=spawns, floor=result,
        source_CPU_only=True, ROM_written=False, native_qualification=False,
        scope='Exact ordinary constructors and genuine source floor across all three simultaneous lifts. Hardware cadence and actual native route are separate.',
        bindings={p.relative_to(R).as_posix():M.sha(p.read_bytes()) for p in refs})
    (OUT/'proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(M.sha(after),size,spawns,result,flush=True)


if __name__ == '__main__':
    main()
