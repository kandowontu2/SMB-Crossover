"""Bound the retained lift sweep to its authored source-X domain."""

from collections import Counter
from itertools import product
import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory

import check_mini_lift_retention_1110_v1 as L
from check_mini_funded_actor_1108_v3 import slim_fork
from check_mini_movement_admission_1110_v1 import memory

N, M, R, OUT = L.N, L.M, L.R, L.OUT


def source_fixture(m, px, top):
    L.camera(m,px+100)
    N.put(m, Player_X_Position=px&255, Player_PageLoc=px>>8,
          Player_Y_Position=top-32, Player_Y_HighPos=1, Player_State=0,
          AreaParserTaskNum=7, ScrollThirtyTwo=0, SavedJoypadBits=0, SavedJoypad1Bits=0)
    m.ram[2][0x30d] = 0


def current_main(m, labels):
    # The native constructors in this arena have already created all three
    # actors. Use the actual GameCore to move them and consume source support.
    b = m.bundle
    result = []
    for index, slot in enumerate((5,4,3)):
        x = L.EDGES[index]+8
        bus = slim_fork(m)
        source_fixture(bus,x,L.snapshot(bus,slot)[5])
        calls = Counter()
        cpu = N.NesMPU

        class Trace(cpu):
            def step(self):
                if self.memory.rawtags[1] == 3 and self.pc == labels['MiniPlatformFloor']:
                    calls['floor'] += 1
                return cpu.step(self)

        rows = []
        N.NesMPU = Trace
        try:
            for _ in range(12):
                N.put(bus, FrameCounter=(N.get(bus,'FrameCounter')+1)&255,
                      VRAM_Buffer1_Offset=0, VRAM_Buffer_AddrCtrl=0)
                N.invoke(bus,'GameCoreRoutine',x=0,y=0)
                top = L.snapshot(bus,slot)[5]
                y = N.get(bus,'Player_Y_Position')
                source_y = int.from_bytes(bus.ram[2][0x252:0x254],'little')>>4
                assert bus.ram[2][0x30d]==slot+1, (index, rows, calls, y, top,source_y)
                assert abs((source_y+8)-top)<=1, (index, source_y, top)
                assert abs(y+32-top)<=1, (index, y, top)
                rows.append([top,y,source_y])
        finally:
            N.NesMPU = cpu
        assert calls['floor']==12 and len({row[0] for row in rows})>1
        result.append(dict(slot=slot,x=x,updates=len(rows),floor_calls=calls['floor'],
                           native_top_first_last=[rows[0][0],rows[-1][0]]))
    return result


def ownership(raw):
    text = (R/'src/level_tiles.s').read_text()
    stream = text.split('E_GroundArea6:\n',1)[1].split(';level',1)[0]
    packet = bytes(int(v,16) for v in re.findall(r'\$([0-9a-fA-F]{2})',stream))
    assert raw.count(packet)==1 and packet[-1]==255
    i = 0
    ids = []
    while packet[i] != 255:
        row = packet[i]&15
        if row not in (14,15):
            ids.append(packet[i+1]&63)
        i += 3 if row==14 else 2
    assert i==len(packet)-1 and 0x25 not in ids
    return dict(exact_enemy_stream_file_offset=raw.index(packet), actor_IDs=sorted(set(ids)),
                placed_lift_ranges=[[x-6,x+30] for x in L.EDGES],
                scope='Only authored Mini helpers have the native $25/$40 marker in this 1-1 actor stream. All source queries use the full committed subpixel X, so the pages2/3 guard includes the complete horizontal foot domain.')


def foreign(before, after):
    checks = 0
    for raw,x in product((0,5,6,24,36,37,39), (560,688,864)):
        pair = [L.fixture(b,0,False,False) for b in (before,after)]
        for m in pair:
            L.setup_main(m,x,0,0,5)
            N.put(m,SelectedCharacter=raw)
            L.camera(m,x+100)
        a,b = [N.invoke(m,'MiniLiftTick',a=0,x=0,y=0,p=0x31) for m in pair]
        left,right = [memory(m) for m in pair]
        assert all(a[n]==b[n] for n in 'AXYP') and left[:5]==right[:5]
        assert all(left[5][i]==right[5][i] for i in (0,1))
        assert left[6:]==right[6:] and all(m.ram[2][0x30c]==0 for m in pair)
        checks += 1
    return checks


def main():
    OUT.mkdir(exist_ok=True)
    # All compiler intermediates remain inside this single bounded task.
    with TemporaryDirectory(prefix='lift-guard-',dir=OUT) as folder:
        tmp = Path(folder)
        original_floor = L.FLOOR
        floor = original_floor.read_text()
        floor = floor.replace('    lda nocollide\n',
            '    lda MiniX+1\n    and #$e0\n    cmp #$20\n    bne @miss\n    lda nocollide\n',1)
        guard = tmp/'guard.inc'
        guard.write_text(floor)
        L.OUT,L.FLOOR = tmp,guard
        parent, image, patches, labels, size = L.build(L.BASE.read_bytes())
        assert size == 5120
        before,after = L.bundles(parent,image)
        witness = ownership(image)
        m,spawns = L.constructor(before,after)
        result = L.test_floor(m,labels['MiniPlatformFloor'])
        lanes = current_main(m,labels)
        preserved = foreign(before,after)
        # Persist only source, kernel and labels consumed by the root packet.
        for ext in ('bin','lbl','s'):
            (OUT/f'kernel-v2.{ext}').write_bytes((tmp/f'kernel.{ext}').read_bytes())
    refs = (Path(__file__),Path(L.__file__),L.CAMERA,L.KERNEL,L.KERNEL.with_suffix('.bin'),
            L.CONFIG, original_floor, L.ALLOCATOR, R/'src/object.s', R/'src/level_tiles.s',
            *(OUT/f'kernel-v2.{ext}' for ext in ('bin','lbl','s')))
    q = dict(passed=True, source_CPU_only=True, ROM_written=False,
        base_ROM_SHA256=M.sha(parent), expected_memory_only_SHA256=M.sha(image),
        patches=patches,kernel_bytes=size, labels=labels, constructors=spawns, floor=result,
        actual_GameCore_carry=lanes,foreign_dispatch_exact=preserved,ownership=witness,
        bindings={p.relative_to(R).as_posix():M.sha(p.read_bytes()) for p in refs})
    (OUT/'proof-v2.json').write_text(json.dumps(q,indent=2)+'\n')
    print(q['expected_memory_only_SHA256'],size,lanes,preserved,result,flush=True)


if __name__=='__main__':
    main()
