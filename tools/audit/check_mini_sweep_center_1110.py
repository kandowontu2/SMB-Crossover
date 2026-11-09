"""Remove unused span setup from the source Mini's center-only head probe."""

import argparse
from collections import Counter, defaultdict
from itertools import product
import json
from pathlib import Path

import check_mini_lift_retention_1110_v1 as L
import check_mini_lift_retention_1110_v2 as G
from check_mini_funded_actor_1108_v3 import install, registers, run, slim_fork
from compose_mini_frame_budget_1108 import check_full_cpu
from measure_mini_kernel_transport_1109 import compile_source, replace_one
from prepare_mini_side_alias_1108 import compare_memory


N, M, R = L.N, L.M, L.R
RETENTION = L.OUT/'proof-v2.json'
KERNEL = L.OUT/'kernel-v2.s'
PIN = '68a1c8165cf0456f0e3a99771e4d20a344f3b64069a9879974a659db174290dc'
MASKS = {2: [(0x1fe3, 0x1ff0)], 3: [(0, 5120), (0x1fe3, 0x1ff0)]}


def transform(source):
    # The left path is reachable only with carry clear from the 16-bit
    # comparison. The two aligned scan wraps retain carry from ADC #8.
    source = replace_one(source, '    lda MiniLeft\n    jmp @xbound\n@right:',
                         '    lda MiniLeft\n    bcc @xbound\n@right:')
    for coordinate, loop in (('Y','@xloop'),('X','@yloop')):
        source = replace_one(source, f'    inc MiniScan{coordinate}+1\n    jmp {loop}',
                             f'    inc MiniScan{coordinate}+1\n    bcs {loop}')

    # In jump ascent the donor scans only the center. The old setup wrote
    # MiniSaved, MiniCoord, MiniScanX and MiniEnd, then overwrote all of them
    # before the first tile query. All other movement keeps the full span.
    first = '    jsr MiniHostPixelX\n    ; Ground\'s original running probes'
    check = '''    ; Jump ascent checks only the head center, unlike fall/ground/crouch.
    lda MiniFamily
    cmp #1
    bne @yloop
    lda MiniNegative
    beq @yloop
'''
    assert source.count(first)==source.count(check)==source.count('@yloop:\n')==1
    start, at, end = (source.index(s) for s in (first,check,'@yloop:\n'))
    span, center = source[start:at], source[at+len(check):end]
    assert center.startswith('    clc\n    lda MiniLeft\n')
    decision = check.replace('@yloop','@yspan')
    return source[:start]+decision+center+'    jmp @yloop\n@yspan:\n'+span+source[end:]


def original_image():
    proof = json.loads(RETENTION.read_text())
    camera = json.loads(L.CAMERA.read_text())
    raw = L.BASE.read_bytes()
    assert M.sha(raw) == L.PIN == camera['parent_SHA256']
    before = install(raw, camera['patches'])
    assert M.sha(before) == proof['base_ROM_SHA256']
    before = install(before, proof['patches'])
    assert M.sha(before) == proof['expected_memory_only_SHA256']
    old = KERNEL.with_suffix('.bin').read_bytes()
    assert len(old) == 5120 and M.sha(old) == PIN and old == before[L.CODE:L.CODE+5120]
    assert M.sha(KERNEL.read_bytes()) == proof['bindings'][KERNEL.relative_to(R).as_posix()]
    return before, proof


def successor_image(output):
    before, previous = original_image()
    code, labels = compile_source(output, transform(KERNEL.read_text()), L.CONFIG)
    assert len(code) == 5120 and labels == previous['labels']
    assert before[L.COOKIE:L.COOKIE+3] == bytes([167,41,1])
    digest = lambda data: bytes.fromhex(M.sha(data))[:13]
    assert before[L.COOKIE+3:L.COOKIE+16] == digest(before[L.CODE:L.CODE+7168])
    cookie = digest(code + before[L.CODE+5120:L.CODE+7168])
    patches = [L.patch(before, L.CODE, code, 'existing five Mini source code pages'),
               L.patch(before, L.COOKIE+3, cookie, 'existing Mini payload digest')]
    return before, install(before, patches), patches, labels


def u16(ram, at, value):
    ram[at:at+2] = (value & 65535).to_bytes(2, 'little')


def step_input(m, state, x, y, vx, vy, keys, tier, tile):
    m.raw_page(1, 3)
    m.raw_page(2, 2)
    N.put(m, CurrentBank=3, CurrentBankC=2)
    ram = m.ram[2]
    ram[0x228] = state
    ram[0x244] = tier
    ram[0x245] = 3 if vx < 0 else 1
    ram[0x248] = keys
    ram[0x249] = keys
    ram[0x254:0x258] = bytes([1,6,1 if tier == 0 else 249,7])
    # Deliberately distinct initial scratch values to catch a skipped writer.
    ram[0x270:0x27f] = bytes(range(0x51,0x60))
    u16(ram, 0x200, vx)
    u16(ram, 0x220, vy)
    u16(ram, 0x250, x)
    u16(ram, 0x252, y)
    u16(ram, 0x258, 0)
    u16(ram, 0x25a, 0x7ff0)
    for name in ('Block_Buffer_1','Block_Buffer_2'):
        start = M.address(m.bundle, name)
        # Mix actual raw tile classes across both native buffers. Keep the
        # original dedicated floor rows at the bottom of each buffer.
        m[start:start+176] = bytes(tile if i%3 else 0 for i in range(176))


def source_step(m, labels):
    c = N.NesMPU(memory=m, pc=labels['MiniStep'])
    c.a, c.x, c.y, c.p, c.sp = 53, 11, 29, 0x61, 224
    c.stPushWord(0x5aff)
    observations = []
    pending = None

    def watch(z):
        nonlocal pending
        if pending == (z.pc,z.sp):
            observations.append(('return',registers(z),bytes(z.memory.ram[2][0x2e0:0x2ea])))
            pending = None
        if z.pc == labels['MiniNativeTile']:
            ram = z.memory.ram[2]
            # The routine's initial Y-range CMP overwrites C before use.
            # Out-of-range high Y takes Tile_Invalid, which also writes C.
            observations.append(('entry',registers(z,0xfe),bytes(ram[0x270:0x27f]),bytes(ram[0x2e0:0x2ea])))
            stack = z.memory[0x101+z.sp:0x103+z.sp]
            pending = (int.from_bytes(stack,'little')+1,z.sp+2)

    run(c, lambda z:(z.pc,z.sp)==(0x5b00,224), watch)
    assert pending is None
    return registers(c), observations, c.processorCycles


def differential(before, after, labels):
    images = L.bundles(before, after)
    seeds = [L.fixture(b,0,False,False) for b in images]
    results = defaultdict(list)
    for state, (x, y), (vx,vy,keys), (tier,tile) in product(
            (1,4,7,10,12,13),
            ((40*16+3,64*16), (251*16+15,135*16+8), (255*16+15,16*16),
             (512*16,200*16+15), (1024*16+3,215*16), (1511*16+11,159*16)),
            ((-5602,-12288,0xc2), (5602,-6144,0xc1), (3665,0,1), (0,8192,0)),
            ((0,0),(0,0x26),(1,0x54),(1,0xc2),(1,0xc3))):
        pair = [slim_fork(m) for m in seeds]
        for m in pair:
            step_input(m,state,x,y,vx,vy,keys,tier,tile)
        a,b = [source_step(m,labels) for m in pair]
        case = (state,x,y,vx,vy,keys,tier,tile)
        assert a[:2] == b[:2], (case,a,b)
        compare_memory(*pair,ram_exclusions=MASKS)
        assert pair[0][0x15a:0x17b] == pair[1][0x15a:0x17b],case
        results[state].append(a[2]-b[2])
    return [dict(source_state=state,cases=len(cycles),min_saved=min(cycles),max_saved=max(cycles),
                 center_sweeps=sum(v>300 for v in cycles)) for state,cycles in sorted(results.items())]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    args.output.mkdir(exist_ok=True)
    before, after, patches, labels = successor_image(args.output)
    direct = differential(before,after,labels)
    whole = check_full_cpu(before, after, MASKS)
    old, new = L.bundles(before,after)
    camera = install(L.BASE.read_bytes(),json.loads(L.CAMERA.read_text())['patches'])
    camera_old, _ = L.bundles(camera,before)
    old_lifts, old_spawns = L.constructor(camera_old,old)
    new_lifts, new_spawns = L.constructor(camera_old,new)
    assert old_spawns == new_spawns
    lift = G.current_main(old_lifts,labels)
    assert lift == G.current_main(new_lifts,labels)
    refs = (Path(__file__),RETENTION,KERNEL,KERNEL.with_suffix('.bin'),L.CAMERA,L.CONFIG,
            *(args.output/f'kernel.{ext}' for ext in ('bin','s','lbl')))
    proof = dict(passed=True,source_CPU_only=True,ROM_written=False,
        parent_SHA256=M.sha(before),expected_memory_only_SHA256=M.sha(after),
        kernel_bytes=5120,labels=labels,patches=patches,step=direct,whole_GameCore=whole,
        tile_entry_scope='All query scratch and registers exact except incoming C, overwritten by Y-range CMP (or cleared by Tile_Invalid). All outgoing AXYP exact.',
        retained_lift_lanes=lift,bindings={p.resolve().relative_to(R).as_posix():M.sha(p.read_bytes()) for p in refs})
    (args.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:v for k,v in proof.items() if k not in ('patches','bindings','labels')}),flush=True)


if __name__=='__main__':
    main()
