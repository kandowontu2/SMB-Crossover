"""Actual hardware vectors for the conditional329 Prince cold and hot floor."""
import argparse
from collections import Counter
import json
from unittest.mock import patch

import check_prince_floor_carrier_1110 as Q
import check_sonic_seventh_cold_vectors_1110 as Existing

C,N,I=Q.C,Q.N,Q.I
V=Existing.V


def cold_vectors(trial,chunks,layout):
    m=Q.Sonic.O.blank(trial);Q.Sonic.O.scene(m,38);cpu=V.entry(m)
    seen=set();counts=Counter();minimum=224;starts=0;resumed=set()
    for _ in range(4_000_000):
        if cpu.pc==V.STOP:break
        tag=m.rawtags[(cpu.pc-0x8000)//8192] if cpu.pc>=0x8000 else m.rawtags[1]
        if tag==2 and cpu.pc==0xc000:starts+=1
        used=(tag==2 and (0xc000<=cpu.pc<0xc25d or 0xd25e<=cpu.pc<0xd2bf)) or (
            tag==193 and 0xae00<=cpu.pc<0xb013) or 0x15a<=cpu.pc<0x17b
        if used:
            worker=tag==2 and 0xc100<=cpu.pc<0xc21c
            row=m.ram[2][0x224] if worker else None
            stage=m.ram[2][0x21c] if worker else starts
            # DataOp is a real copy/independent-reread opcode inside C100.
            data_op=m.ram[2][layout['data_op_PC']-0xc000] if worker else None
            edges=(0,1,layout['new_page_payload_bytes']-1,layout['new_page_payload_bytes'])
            edge=(edges.index(m.ram[2][0x225]) if m.ram[2][0x225] in edges else 4) if row==14 else None
            phase=m.ram[2][0x1fe0],m.ram[3][0x1fe0]
            key=(tag,cpu.pc,cpu.sp,cpu.p&4,stage,row,data_op,edge,phase)
            if key not in seen:
                seen.add(key)
                for kind in ('FF','IRQ') if not cpu.p&4 else ('FF',):
                    minimum=min(minimum,V.interrupt(Existing.clone(cpu),kind));counts[kind]+=1
                    if row==14:counts['append_'+kind]+=1
                if len(seen)%500==0:print('COLD_VECTOR_PROGRESS '+json.dumps(dict(contexts=len(seen),counts=dict(counts))),flush=True)
            boundary=(tag,cpu.pc,stage,row,data_op,edge)
            if ((tag,cpu.pc) in ((2,0xd25e),(2,0xc000)) or (row==14 and edge in (0,1,2,3))) and boundary not in resumed:
                resumed.add(boundary);minimum=min(minimum,V.interrupt(cpu,'FF'))
        V.step(cpu)
    else:raise AssertionError('actual new Prince cold vector bound')
    assert cpu.p&1 and cpu.sp==224 and starts==3
    assert Q.Sonic.O.headers(m)==(bytes.fromhex(layout['Prince_cookie']),)*2
    assert bytes(m.ram[3][:len(chunks[0])])==Q.P.live(chunks[0])
    assert bytes(m.ram[2][0x800:0x800+len(chunks[1])])==chunks[1]
    assert counts['append_FF']>0 and counts['FF']>100 and counts['IRQ']>0
    return dict(counts=dict(counts),minimum_SP=minimum,original_trace_resumed_FF=len(resumed),
        contexts='Actual PC/SP/I/stage/source-row/copy-verify/append-first-last/header-phase',
        both_headers_valid=True)


def hot_vectors(trial):
    env,seed,labels=C.fixture(trial)
    N.put(seed,CrossoverBehaviorVersion=0);N.consume(seed)
    Q.Foot.F.REAL_NMI=True;_,seed=Q.Foot.F.authored(seed)
    real=C.Route.controls;held=None;tick=-1
    class Done(Exception):pass
    def retain(e,m,l,pad):
        nonlocal held,tick
        tick+=1
        if tick==102:held=N.fork(m);raise Done()
        return real(e,m,l,pad)
    with patch.object(C.Route,'controls',retain):
        try:Q.Foot.F.trial(env,seed,labels,'roll-up')
        except Done:pass
    assert held is not None
    N.put(held,NmiDisable=255)
    report=C.Camera.Funded.Life.stress('Actual admitted Prince fourth-pipe floor update',held,
        lambda m:real(env,m,labels,8)['regs'],
        [(2,0xd4d7,Q.ADMISSION_PC+layout_admission_size(trial)),(3,0xbd3e,0xbd42),(3,0xb310,0xb36e)])
    return report


def layout_admission_size(trial):return len(Q.admission_code(trial))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--hot',action='store_true');p.add_argument('--both',action='store_true');args=p.parse_args()
    _,trial,chunks,layout,_,_,_=Q.proposal()
    if args.both:
        cold=cold_vectors(trial,chunks,layout);print('COLD_REAL_VECTORS '+json.dumps(cold),flush=True)
        result=dict(cold=cold,hot=hot_vectors(trial))
    else:result=hot_vectors(trial) if args.hot else cold_vectors(trial,chunks,layout)
    print('REAL_VECTORS '+json.dumps(dict(in_memory_SHA256=layout['in_memory_SHA256'],
        ROM_written=False,outputs_written=0,result=result)),flush=True)


if __name__=='__main__':main()
