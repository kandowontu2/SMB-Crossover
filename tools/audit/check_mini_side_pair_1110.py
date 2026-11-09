"""Deduplicate the actual Mini native side pairs in their existing route span."""

import argparse
from collections import Counter, defaultdict
from itertools import product
import hashlib
import inspect
import json
from pathlib import Path
import re

import check_mini_side_direct_entry_1110 as D
from prepare_mini_mario_native_power_1103_v56 import address, location


R, N, BASE, PIN = D.R, D.N, D.BASE, D.PIN
F = D.Async.F
NATIVE = 0x958b
LEGACY = 0xaad9
DIRECT = 0xad9b
FILTER = 0xadad


def find(raw, pattern):
    return [(m.start()//8192, m.start()&8191) for m in
            re.finditer(re.escape(bytes.fromhex(pattern)),raw[16:1048592])]


def image():
    raw, _ = D.image()
    assert find(raw,'2097e4')==[(126,0x1c85),(126,0x1cac)]
    assert not find(raw,'4c97e4')
    assert find(raw,'4c9bad')==[(124,0xad9)] and not find(raw,'209bad')
    assert find(raw,'a9d98d6c01a9aa8d6d01a9fc4c5a01')==[(89,0x1c6f)]
    assert find(raw,'a9588d6c01a9bc8d6d01a9d94c5a01')==[(33,0x1ed0)]
    assert find(raw,'4c58bc')==[(4,0x1b97),(4,0x1b9f),(65,0x1c52)]
    assert find(raw,'4cd9aa')==[(82,0x9f0)]
    assert not find(raw,'2058bc') and not find(raw,'20d9aa')
    # Those raw JMP hits are in switchable banks with different destinations.
    # Neither physical89 nor a resident bank reaches TnFastSideGate directly.
    b = D.bind(raw)
    assert find(raw,'20e490')==[(23,0x197b),(23,0x1993)]
    assert (address(b,'sound_2e_part_03'), address(b,'sound_2e_part_04'))==(0xb96a,0xb9a1)
    assert all((location(b,n)-16)//8192==23 for n in ('sound_2e_part_03','sound_2e_part_04'))
    for name,values in [('BlockBuffer_X_Adder',(2,2,13,13)),
                        ('BlockBuffer_Y_Adder',(24,24,24,24))]:
        at=location(b,name)+17
        assert raw[at:at+4]==bytes(values)
    # The original upper and lower ingress limits; these also leave V alone.
    assert raw[D.offset(126,0x9c7b):D.offset(126,0x9c88)].hex()=='a5bdc920901dc9e4b0302097e4'
    assert raw[D.offset(126,0x9c9e):D.offset(126,0x9caf)].hex()=='ac0601c8a5bdc908900dc9d0b0092097e4'
    patches=[]
    out=bytearray(raw)
    for pc,before,after in (
        (LEGACY,'4c9bad','8d6a01'),
        # TYA/LSR leaves V untouched. On a real lower duplicate restore C1
        # from the native vertical SBC before the unchanged filter's PHP.
        (DIRECT,'8d6a0108ad0260c929f0034c84aa28208b95','984ab00ba5bdc9209005a50638b003208b95'),
    ):
        at=D.offset(124,pc)
        assert len(before)==len(after) and raw[at:at+len(before)//2].hex()==before
        out[at:at+len(after)//2]=bytes.fromhex(after)
        patches.append(dict(bank=124,pc=pc,file_offset=at,old_hex=before,new_hex=after))
    return raw,bytes(out),patches


def run_bg(m):
    cpu=N.NesMPU
    owner=N.get(m,'SelectedCharacter')
    visits=Counter()
    prior=None
    geometry=[]

    class Trace(cpu):
        def step(self):
            nonlocal prior
            tag=self.memory.rawtags[1]
            if owner==41 and tag==252 and self.pc==DIRECT:
                prior=(self.y,N.get(m,'Player_Y_Position'))
                visits['calls']+=1
                if self.y&1==0 and prior[1]>=32:
                    visits['eligible']+=1
            if owner==41 and tag==252 and self.pc==NATIVE:
                visits['reads']+=1
            if tag==252 and self.pc==FILTER:
                assert prior==(self.y,N.get(m,'Player_Y_Position'))
                geometry.append((prior,tuple(m[5:11]),self.a,self.p&0x41))
            if tag==252 and self.pc==LEGACY:
                visits['foreign']+=1
            return cpu.step(self)

    N.NesMPU=Trace
    try:
        out=N.invoke(m,'PlayerBGCollision',a=0,x=0,y=0,p=0x31)
    finally:
        N.NesMPU=cpu
    return tuple(out[k] for k in ('A','X','Y','P')),out['CPU'],visits,geometry


def pairs(before,after):
    seeds=[F.F.fixture(D.bind(raw),0,False,False) for raw in (before,after)]
    rows=defaultdict(list)
    tiles=(0,0x12,0x26,0x54,0xc2,0xc3)
    cases=[*product((41,),(8,),(112,135,176),(1511,1520,1530),tiles),
           *product((41,),(8,),(16,31,32,152,206),(1530,),tiles),
           *product((41,),(4,7),(31,135),(1511,),tiles),
           *product((0,2,6,15,19,32),(4,8),(31,135),(1511,),(0,0x54,0xc2))]
    for owner,engine,height,x,tile in cases:
        group = [N.fork(m) for m in seeds]
        for m in group:
            F.setup(m,x,height,0,0,actor=owner)
            N.put(m,GameEngineSubroutine=engine)
            # Write the actual small-side right and left cells. Cases around
            # X=1536 cover the true two-buffer low-byte carry.
            for delta,value in ((2,0),(13,tile)):
                px=x+delta
                base=0x3d0 if px&256 else 0x300
                at=base+((px>>4)&15)+((height+24)&0xf0)-32
                m[at]=value
        a,b=(run_bg(m) for m in group)
        case=(owner,engine,height,x,tile)
        assert a[0]==b[0] and a[3]==b[3],(case,a,b)
        D.compare_memory(*group)
        assert bytes(group[0][0x15a:0x17b])==bytes(group[1][0x15a:0x17b]),case
        assert a[2]['calls']==b[2]['calls'] and a[2]['foreign']==b[2]['foreign'],case
        assert a[2]['reads']-b[2]['reads']==a[2]['eligible'],(case,a,b)
        kind=('Mini' if owner==41 else 'foreign')
        rows[kind,a[2]['eligible']].append(a[1]-b[1])
    assert len(rows['Mini',2])>0
    return [dict(group=kind,duplicate_queries=alias,cases=len(v),cycles_saved=[min(v),max(v)])
            for (kind,alias),v in sorted(rows.items())]


def interrupts(image):
    source=inspect.getsource(D.Async.check)
    anchor="                elif tag==161 and 0xbea2<=pc<0xbf00:\n"
    assert source.count(anchor)==1
    source=source.replace(anchor,"                elif tag==252 and 0xad9b<=pc<0xadce:\n"
        "                    role='Mini_pair'\n"
        "                elif tag==252 and 0xaad9<=pc<0xaadc:\n"
        "                    role='foreign_NrSide'\n"+anchor)
    env=dict(vars(D.Async))
    exec(compile(source,str(Path(__file__)),"exec"),env)
    return env['check'](image,head=True,adder=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(exist_ok=True)
    before,after,patches=image()
    cases=pairs(before,after)
    print(json.dumps(cases),flush=True)
    irq=interrupts(after)
    refs=(Path(__file__),Path(D.__file__),Path(D.Async.__file__),BASE,D.SOURCE,D.FILTER,
          R/'src/collision.s',R/'src/characters.s',R/'src/mmc5.s',R/'src/new_roster_dispatch.s',
          R/'src/tmnt_probe_gates.s')
    q=dict(passed=True,source_CPU_only=True,ROM_written=False,parent_SHA256=PIN,
        expected_memory_only_SHA256=hashlib.sha256(after).hexdigest(),patches=patches,cases=cases,
        interrupt=irq,bindings={str(p.resolve()):D.sha(p) for p in refs})
    (args.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:q[k] for k in ('expected_memory_only_SHA256','interrupt')}))


if __name__=='__main__':
    main()
