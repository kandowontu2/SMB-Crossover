"""Exercise same-cell skips with real IRQ and negative-NMI handlers."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import re

from check_mini_busy_fire_interrupts_1108_v3 import lag_pcs
from measure_mini_kernel_transport_1109 import BASE, CODE, PIN, R, sha
from prepare_mini_mario_native_power_1103_v56 import N, address, bundle
from prepare_mini_side_alias_1108 import compare_memory
from profile_mini_busy_1108_v1 import fixture


def image(proof_path):
    proof = json.loads(proof_path.read_text())
    assert proof['passed'] and proof['parent_SHA256'] == sha(BASE) == PIN
    for path,digest in proof['bindings'].items():
        assert sha(Path(path)) == digest,path
    raw = BASE.read_bytes()
    successor = bytearray(raw)
    for row in proof['patches']:
        offset = row['offset']
        before,after = (bytes.fromhex(row[field]) for field in ('preimage','replacement'))
        assert len(before) == len(after) and raw[offset:offset+len(before)] == before
        successor[offset:offset+len(before)] = after
    return raw,bytes(successor),proof


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof',type=Path,required=True)
    args = parser.parse_args()
    raw,successor,proof = image(args.proof)
    new_path = args.proof.with_name('kernel.lbl')
    labels = {name:int(pc,16) for pc,name in
              re.findall(r'^al ([\da-fA-F]+) \.(\w+)$',new_path.read_text(),re.M)}
    old,new = map(bundle,(raw,successor))
    read_write = set()
    for name in ('Block_Buffer_1','Block_Buffer_2'):
        first = address(new,name)
        read_write.update(range(first,first+208))
    native = N.NesMPU
    counts = Counter()
    deepest = {}
    minimum = 255
    foreground = 255
    worst_nmi = None
    exclusions = {2:[(0x1fe3,0x1ff0)],3:[(0,5120),(0x1fe3,0x1ff0)]}

    class ProtectedBus(N.Bus):
        def __getitem__(self,at):
            assert not isinstance(at,int) or at not in read_write,('interrupt terrain read',hex(at))
            return super().__getitem__(at)

        def __setitem__(self,at,value):
            assert not isinstance(at,int) or at not in read_write,('interrupt terrain write',hex(at))
            super().__setitem__(at,value)

    def clone(c):
        m = N.fork(c.memory)
        z = native(memory=m,pc=c.pc)
        z.a,z.x,z.y,z.p,z.sp = c.a,c.x,c.y,c.p,c.sp
        return z

    def stable(c):
        m = c.memory
        return ((c.a,c.x,c.y,c.p&0xef,c.sp,c.pc),m.rawtags[:],tuple(map(bytes,m.ram)),
                bytes(m[3:11]),bytes(m[0x15a:0x17b]),bytes(m[0x101+c.sp:0x200]),len(m.ram_writes))

    def interrupt(c,kind):
        nonlocal minimum,worst_nmi
        z = clone(c)
        m = z.memory
        before = stable(z)
        skipped = N.get(m,'NmiSkipped')
        if kind == 'IRQ':
            assert z.p&4 == 0
            z.irq()
        else:
            assert N.get(m,'NmiDisable') == 255
            z.nmi()
        m.__class__ = ProtectedBus
        hits = 0
        for _ in range(20000):
            if (z.pc,z.sp) == (c.pc,c.sp):
                break
            minimum = min(minimum,z.sp)
            if kind == 'NMI':
                assert z.pc != regular
                hits += z.pc == lag
                if not z.p&4 and (worst_nmi is None or z.sp < worst_nmi.sp):
                    worst_nmi = clone(z)
            assert m[z.pc] != 0,(kind,hex(z.pc))
            z.step()
        else:
            raise AssertionError((kind,hex(c.pc),hex(z.pc)))
        assert stable(z) == before,(kind,hex(c.pc))
        assert hits == (kind == 'NMI')
        assert N.get(m,'NmiSkipped') == (skipped+(kind=='NMI'))&255
        counts[kind] += 1

    class Trace(native):
        def step(self):
            nonlocal foreground
            if 0xa000 <= self.pc < 0xa000+5120 and self.memory.rawtags[1] == 3:
                foreground = min(foreground,self.sp)
                key = self.pc,self.p&4
                if key not in deepest or self.sp < deepest[key]:
                    deepest[key] = self.sp
                    interrupt(self,'NMI')
                    if not self.p&4:
                        interrupt(self,'IRQ')
            return super().step()

    rows = []
    for tier,page in product([0,2],[0,1]):
        pair = [fixture(im,2,False,False) for im in (old,new)]
        lag,regular = lag_pcs(pair[1])
        for m in pair:
            N.put(m,PlayerStatus=tier,PlayerSize=int(tier==0),Player_PageLoc=page,
                  Player_X_Position=251,ScreenLeft_X_Pos=176,ScreenLeft_PageLoc=page,
                  ScreenRight_X_Pos=175,ScreenRight_PageLoc=page+1)
            # Preserve an ordinary floor. Place native special/vine/solid
            # cells around both page boundaries for real movement probes.
            for name in ('Block_Buffer_1','Block_Buffer_2'):
                start = address(new,name)
                for column,tile in [(0,0xc3),(1,0x26),(2,0x10),(15,0xc2)]:
                    m[start+9*16+column] = tile
        costs = []
        for frame in range(2,36):
            held = (1 if frame<20 else 2) | (128 if 8<=frame<21 else 0)
            results = []
            for slot,m in enumerate(pair):
                N.put(m,FrameCounter=frame,SavedJoypadBits=held,SavedJoypad1Bits=held,
                      NmiDisable=255,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0)
                N.NesMPU = Trace if slot else native
                try:
                    results.append(N.invoke(m,'GameCoreRoutine',x=0,y=0,p=0x25 if frame&1 else 0x21))
                finally:
                    N.NesMPU = native
            assert all(results[0][reg] == results[1][reg] for reg in ('A','X','Y','P')),results
            compare_memory(*pair,ram_exclusions=exclusions)
            costs.append(results[0]['CPU']-results[1]['CPU'])
        rows.append(dict(tier=tier,page=page,updates=len(costs),min_saved=min(costs),
                         max_saved=max(costs),average_saved=sum(costs)/len(costs)))
    assert worst_nmi is not None
    interrupt(worst_nmi,'IRQ')
    assert minimum > 0x7a and min(counts.values()) > 100
    report = dict(passed=True,base_SHA256=PIN,proof_SHA256=sha(args.proof),
        image_SHA256=__import__('hashlib').sha256(successor).hexdigest(),actual_lag_PC=lag,
        forbidden_regular_NMI_PC=regular,foreground_cuts=len(deepest),interrupts=dict(counts),
        IRQ_nested_in_deepest_NMI=True,min_foreground_SP=foreground,min_ISR_SP=minimum,
        IRQ_NMI_no_native_terrain_reads_or_writes=True,source_kernel_reached=labels['MiniStep'] in {pc for pc,_ in deepest},
        additional_GameCore=rows,ROM_written=False,Mesen_run=False)
    assert report['image_SHA256'] == proof['expected_memory_only_SHA256']
    args.proof.with_name('irq.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
