"""Actual IRQ and negative-NMI cuts of the cold-backed Prince pose and ledge code."""

import argparse
from collections import Counter
import json
from pathlib import Path

import prepare_prince_climb_funded_1109_v1 as P


N, I, E = P.N, P.I, P.EDGE


def lag_branch(m):
    code=bytes(m[0xe000:0x10000])
    at,=[i for i in range(len(code)-8) if code[i:i+4]==bytes.fromhex('ad390110')
         and code[i+5:i+8]==bytes.fromhex('ee3a01')]
    rel=code[at+4]
    return 0xe000+at+5,0xe000+at+5+(rel-256 if rel&128 else rel)


def state(m):
    return (tuple(map(bytes,m.ram)),bytes(m[3:11]),bytes(m[0x15a:0x17b]),m.rawtags[:])


def inject(cpu,native,kind):
    m=cpu.memory
    regs=(cpu.a,cpu.x,cpu.y,cpu.p&0xef,cpu.sp,cpu.pc)
    original=state(m)
    writes=len(m.ram_writes)
    skipped=N.get(m,'NmiSkipped')
    if kind=='IRQ':
        assert cpu.p&4==0
        cpu.irq()
    else:
        assert N.get(m,'NmiDisable')==255
        cpu.nmi()
    lag,regular=lag_branch(m)
    low=255
    hits=0
    for _ in range(80000):
        low=min(low,cpu.sp)
        if (cpu.sp,cpu.pc)==regs[-2:]:break
        assert cpu.pc!=regular
        hits+=cpu.pc==lag
        assert m[cpu.pc]!=0,(kind,hex(cpu.pc))
        native.step(cpu)
    else:raise AssertionError(('Actual ISR bound',kind,hex(cpu.pc)))
    assert (cpu.a,cpu.x,cpu.y,cpu.p&0xef,cpu.sp,cpu.pc)==regs
    assert state(m)==original and len(m.ram_writes)==writes
    assert hits==(kind=='lagNMI') and N.get(m,'NmiSkipped')==(skipped+(kind=='lagNMI'))&255
    return low


def observe(seed,run,watch,cut=None):
    m=N.fork(seed)
    native=N.NesMPU
    cuts={}
    low=255
    injected=False
    class Trace(native):
        def step(self):
            nonlocal low,injected
            tag=self.memory.rawtags[(self.pc-0x8000)//8192] if self.pc>=0x8000 else -1
            low=min(low,self.sp)
            if any(tag==bank and lo<=self.pc<hi for bank,lo,hi in watch):
                key=(tag,self.pc,self.p&4)
                value=(*key,self.sp)
                if key not in cuts or cuts[key][3]>self.sp:cuts[key]=value
                if cut and not injected and value==cut[1]:
                    injected=True
                    low=min(low,inject(self,native,cut[0]))
            return native.step(self)
    N.NesMPU=Trace
    try:
        regs=run(m)
    finally:
        N.NesMPU=native
    assert injected==(cut is not None)
    return m,regs,list(cuts.values()),low


def stress(name,seed,run,watch):
    ref,regs,cuts,_=observe(seed,run,watch)
    expected=state(ref),bytes(ref[0x200:0x300]),ref.chr_latches[:]
    counts=Counter()
    low=255
    for point in cuts:
        for kind in ('IRQ','lagNMI'):
            if kind=='IRQ' and point[2]:continue
            m,ret,_,depth=observe(seed,run,watch,(kind,point))
            assert ret==regs,(name,kind,point,regs,ret)
            assert (state(m),bytes(m[0x200:0x300]),m.chr_latches[:])==expected,(name,kind,point)
            counts[kind]+=1
            low=min(low,depth)
    assert min(counts.values())>10
    return dict(name=name,cuts=counts,minimum_SP=low)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    receipt=args.output/'result.json'
    q=json.loads(receipt.read_text())
    filename,pin=P.PARENTS['a08d']
    raw=bytearray((P.R/filename).read_bytes())
    assert P.sha(raw)==pin==q['parent_SHA256']
    for patch in q['patches']:
        at=patch['offset']
        old=bytes.fromhex(patch['preimage']);new=bytes.fromhex(patch['replacement'])
        assert raw[at:at+len(old)]==old
        raw[at:at+len(new)]=new
    assert P.sha(raw)==q['expected_memory_only_SHA256']
    template,_=P.Q.M.OLD.image()
    base=dict(template,raw=bytes(raw))
    seed,_=P.Q.C.C.cold(base,38)
    _,seed,lab=P.Q.loaded(base,seed)
    N.put(seed,NmiDisable=255,DisableScreenFlag=0,Mirror_PPUMASK=30,GameEngineSubroutine=8,OperMode=1)
    art=json.loads((P.V.O/'source-art.json').read_text())['poses']
    def tag(frame):return int.from_bytes(seed.ram[2][0x800+2*frame:0x802+2*frame],'little')
    pose=max((p for p in art if tag(p['source_frame'])&0xc000==0xc000),key=lambda p:len(p['parts_8x16']))
    draw=N.fork(seed);draw.raw_page(2,2);N.put(draw,CurrentBankC=2,CurrentOAMOffset=0,
                       GuestOamRotationActive=1,RgOamRotation=0)
    draw.ram[2][0x617]=pose['source_frame'];draw.ram[2][0x615]=pose['source_facing']
    I.invoke(draw,3,lab['PpHostProject'],(83,71,109,0x61))
    I.invoke(draw,3,0xc383,(83,71,109,0x61))
    result=[stress('actual native compact pose draw',draw,
                   lambda m:I.invoke(m,3,lab['PpHostDraw'],(83,71,109,0x61))['regs'],
                   [(2,*q['layout']['compact_half_open'])])]
    for roof in (False,True):
        climb=N.fork(seed);climb.raw_page(1,3);climb.raw_page(2,2)
        N.put(climb,CurrentBank=3,CurrentBankC=2)
        E.put(climb,0xc60f,433);E.put(climb,0xc084,203)
        climb[0xc615]=255;climb[0xc616]=24;climb[0xc618]=2;climb[0xc617]=91;climb[0xc611]=128
        E.put(climb,0xc078,413);climb[0xc07a]=9;climb[0xc4b1]=19
        E.put(climb,0xc07f,208);climb[0xc081]=1;E.put(climb,0xc089,77);climb[0xc6d1]=5
        climb[0x300:0x4a0]=bytes(0x1a0)
        climb[E.block(448,179)]=0x54
        if roof:climb[E.block(448,175)]=0x54
        def call(m):
            cpu=N.NesMPU(memory=m,pc=E.PC)
            cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=24,64,24,0x61,186
            for _ in range(2200):
                if cpu.pc==E.PC+3:break
                assert m[cpu.pc]!=0
                cpu.step()
            else:raise AssertionError('Backed ledge call bound')
            assert E.word(m,0xc60f)==(408 if roof else 440)
            return cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp
        result.append(stress('actual F801 blocked roof' if roof else 'actual F801 open ledge',climb,call,
                             [(2,*q['layout']['worker_half_open'])]))
    for bank in (2,3):
        for i in range(16):
            m=N.fork(seed);m.ram[bank][0x1fe0+i]^=1
            initial=tuple(map(bytes,m.ram))
            x=I.invoke(m,193,0xb08c,(83,71,109,0x21))
            assert not x['regs'][3]&1 and tuple(map(bytes,m.ram))==initial
    report=dict(passed=True,ROM_written=False,image_SHA256=q['expected_memory_only_SHA256'],
                original_proof_SHA256=P.sha(receipt.read_bytes()),scenarios=result,
                render_source_frame=pose['source_frame'],render_source_parts=len(pose['parts_8x16']),
                bad_header_bytes_rejected=32,
                scope='Genuine cold-backed worker and real native draw, isolated typed fixtures. Actual IRQ and FF '
                      'lag branch restore the complete owner overlays, native scratch, SMC, AXYP/SP and maps. '
                      'No native climb traversal or nested IRQ-in-NMI claim.')
    (args.output/'irq.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':main()
