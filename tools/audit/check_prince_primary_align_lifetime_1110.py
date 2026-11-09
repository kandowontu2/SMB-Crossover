"""Audit the saved primary alignment lifetime and real interrupted returns."""

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import check_prince_primary_align_1110 as Check
from check_prince_climb_funded_irq_1109_v2 import stress


R, Route, Pair, N, I = Check.R,Check.Route,Check.Pair,Check.N,Check.I
ROOT = R/'build/prince-d6c0-align-1110'
PROOF_SHA = '49e0a7036dd03c2b4cc4e6d99447c5cd9889584b25c001dc270b8414e50f57b2'
FIRST, SECOND = Check.FIRST,Check.SECOND
SAVED = range(0xc0a1,0xc0a4)


def fixture(seed,snap,record,code,entries):
    retained = None
    real = I.invoke

    def keep(m,*args):
        nonlocal retained
        assert retained is None
        retained = N.fork(m)
        return real(m,*args)

    with patch.object(I,'invoke',keep):
        result,_ = Check.host(seed,snap,record['local_x'],record['facing'],record['alternate'],record['origin'],
                              record['wall'],record['back_floor'],code,entries)
    assert retained is not None and result['actor']==record['after']['actor']
    return retained


def audit(seed,args):
    m = N.fork(seed)
    bus = type(m)
    read,write = bus.__getitem__,bus.__setitem__
    cpu = N.NesMPU
    current,window = None,False
    hits = Counter()
    accesses = []

    class Trace(cpu):
        def step(self):
            nonlocal current,window
            if self.memory is not m:
                return super().step()
            pc = self.pc
            tag = m.rawtags[(pc-0x8000)//8192] if pc>=0x8000 else None
            if tag==3 and pc in (FIRST,FIRST+3,SECOND,SECOND+3):
                hits[pc]+=1
                if pc==FIRST+3:
                    window=True
                if pc==SECOND:
                    window=False
            current = (tag,pc,window)
            try:
                return super().step()
            finally:
                current = None

    def reader(self,key):
        if self is m and current and isinstance(key,int) and key in SAVED:
            accesses.append([*current,'read',key])
        return read(self,key)

    def writer(self,key,value):
        if self is m and current and isinstance(key,int) and key in SAVED:
            accesses.append([*current,'write',key])
        return write(self,key,value)

    with patch.object(bus,'__getitem__',reader),patch.object(bus,'__setitem__',writer),patch.object(N,'NesMPU',Trace):
        out = I.invoke(m,3,Check.ENTRY,args)
    assert hits[FIRST]==hits[FIRST+3]==1
    assert not any(row[2] for row in accesses),accesses
    assert hits[SECOND]==hits[SECOND+3] in (0,1)
    assert hits[SECOND]==sum(1 for row in accesses if row[1]==Check.TEST_ADDRESS+17 and row[3]=='read')//3
    return dict(calls=dict(hits),accesses=accesses,return_regs=out['regs'])


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    out = cli.parse_args().output.resolve()
    path = out/'lifetime.json'
    assert out==ROOT and not path.exists()
    primary = ROOT/'proof.json'
    assert sha256(primary.read_bytes()).hexdigest()==PROOF_SHA
    read = Pair.Second.First.Pit.Current.read
    proof = read(primary)
    code = bytes.fromhex(proof['worker'])
    entries = {'PpSavePrimaryAlign':Check.TEST_ADDRESS,'PpRestorePrimaryAlign':Check.TEST_ADDRESS+15}
    template,_,_ = Pair.Second.First.Pit.Current.current()
    base = dict(template,raw=Route.ROM.read_bytes())
    assert sha256(base['raw']).hexdigest()==Route.PIN
    seed,_ = Check.P.Q.C.C.cold(base,38)
    snap = read(Check.WRITER)['retained_D17A_inputs']['190']
    args = tuple(snap['registers'][:4])
    cases,holds = [],[]
    for r in proof['cases']:
        m = fixture(seed,snap,r,code,entries)
        live = audit(m,args)
        assert live['return_regs']==r['after']['return_regs']
        cases.append(dict(name=r['name'],**live))
        if r['name'] in ('right authentic coordinates','left alternate low-byte wrap','right original solid-back control'):
            holds.append((r['name'],m))
    print('No intervening reads or writes in any of the five reached branches.',flush=True)
    results = []
    for name,m in holds:
        report = stress(name,m,lambda q:I.invoke(q,3,Check.ENTRY,args)['regs'],
                        [(2,Check.TEST_ADDRESS,Check.TEST_ADDRESS+len(code)),(3,FIRST,SECOND+4),
                         (2,0xc40b,0xc491)])
        print(name,report['cuts'],report['minimum_SP'],flush=True)
        results.append(report)
    refs = (Path(__file__),Path(Check.__file__),primary,Check.ASM,Route.ROM,Path(stress.__code__.co_filename))
    result = dict(passed=True,ROM_written=False,Mesen_run=False,ROM_SHA256=Route.PIN,
                  saved_address_half_open=[SAVED.start,SAVED.stop],before_second_call_accesses=0,
                  actual_accesses=cases,real_interrupts=results,execution_funding_granted=False,
                  scope='Actual original D634 through D6C0 or return on the five captured terrain cases. '
                        'Both reachable saved aliases and all overlay/scratch/SMC/maps/AXYP are observed under '
                        'individual real IRQ and FF lag NMI. This is the isolated prototype location, not cold integration.',
                  bindings={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest() for p in refs})
    path.write_text(json.dumps(result,separators=(',',':'))+'\n',encoding='utf-8')


if __name__=='__main__':
    main()
