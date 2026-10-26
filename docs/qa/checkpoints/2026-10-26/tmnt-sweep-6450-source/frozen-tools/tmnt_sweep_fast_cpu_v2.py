"""Paired real compiled sweep/gate and complete mixer outcomes, source only."""
from pathlib import Path
import argparse
from collections import Counter
import itertools
import json
from check_tmnt_render_oa import load, Memory, address
from verify_native_relocation import NesMPU
from tmnt_native_storage_driver import ROOT, sha


def snapshot(c,m):
    return (c.a,c.x,c.y,c.p&207,c.sp,bytes(m[:0x1a0])+bytes(m[0x200:0x8000]),list(m.banks),
            [(k,v)for k,v in m.writes if 0x4000<=k<=0x4017 or 0x5000<=k<=0x5015])


def run(b,entry,period,flags,**kw):
    m=Memory(b);m.page(1,29);m.page(2,kw.get('cbank',38));at=lambda n:address(b,n)
    seed=dict(SelectedCharacter=kw.get('char',19),OperMode=1,GuestAudioCharacter=kw.get('char',19),
              CurrentBank=157,CurrentBankC=kw.get('cbank',38)|128,BassDmcActive=kw.get('owner',0),
              GuestMixMask=kw.get('mask',1),GuestMixChanged=kw.get('changed',0),
              GuestSweepControl=kw.get('control',153),GuestSweepDivider=kw.get('divider',0),
              GuestSweepReload=kw.get('reload',0),GuestSweepTicks=221,
              GuestSweepPeriod=period&255,GuestSweepDelta=83)
    for n,v in seed.items():m[at(n)]=v
    m[0x5115]=157;m[0x5116]=kw.get('cbank',38)|128
    m[at('GuestSweepPeriod')+1]=period>>8;m[at('GuestSweepDelta')+1]=149
    for i,v in enumerate([158,153,period&255,248|(period>>8&7),37,73,109,145]):m[at('GuestFxApu')+i]=v
    for i in range(16):
        m[at('GuestFxDirty')+i]=(kw.get('dirty',0)>>i)&1
        m[at('GuestExpansionLast')+i%8]=((i*31+kw.get('last',0))&255)
    # Coherent hardware status/mapper shadows, no outcome injection in a run.
    m[0x4015]=kw.get('status',16 if kw.get('owner',0) else 0)
    m[510],m[511]=255,126;m.writes=[]
    c=NesMPU(memory=m,pc=at(entry));c.a,c.x,c.y,c.p,c.sp=85,kw.get('x',3),kw.get('y',7),flags,253
    for _ in range(8000):
        if c.pc==0x7f00:break
        c.step()
    else:raise AssertionError(('Sweep timeout',entry,period,flags,kw,hex(c.pc)))
    return c,m


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['baseline','candidate','output']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--quick',action='store_true');a=p.parse_args()
    assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT);a.output.mkdir(parents=True)
    old,new=load(a.baseline),load(a.candidate);flags=[32|(i&15)|((i&16)<<2)|((i&32)<<2)for i in range(64)]
    costs=Counter();count=0
    periods=[18,19,31,32,127,128,255,256,257,511,512,1023,1024,2047]if a.quick else range(18,2048)
    def pair(period,pin,entry='GuestExpansionFlush',target='TnExpansionSweepGate',**kw):
        c,m=run(old,entry,period,pin,**kw);d,n=run(new,target,period,pin,**kw)
        assert snapshot(c,m)==snapshot(d,n),('Sweep outcome mismatch',period,pin,kw,
                (c.a,c.x,c.y,c.p,c.sp),(d.a,d.x,d.y,d.p,d.sp))
        return d.processorCycles-c.processorCycles
    for period in periods:
        for pin in flags:
            costs[pair(period,pin)]+=1;count+=1
    controls=0;other=Counter()
    for period,control,divider,reload,dirty,owner,mask in itertools.product(
            [0,7,8,17,18,128,2047,2048,4095,8191,65535],
            [0,8,129,153,255],[0,1,7],[0,1],[0,2,4,8,14],[0,2,3,4],[0,1,2,3,8]):
        # Full Cartesian is deliberately bounded separately from64-flag math.
        if not ((control==153 and divider==0 and reload==0)or(period in [7,18,128,8191]and dirty in[0,14])):continue
        delta=pair(period,0x79,control=control,divider=divider,reload=reload,dirty=dirty,owner=owner,mask=mask)
        other[delta]+=1;controls+=1
    mixer=0;mixcost=Counter()
    for char,owner,paused,queue,control in itertools.product(range(20),[0,2,3,4],[0,1],[0,2,32,128],[0,153]):
        # Full GuestAudioFinish call exercises its real clone/gate continuation.
        def finish(b):
            # Configure independent source-effect queues BEFORE the call only.
            m=Memory(b);m.page(1,29);m.page(2,38)
            seed=dict(SelectedCharacter=char,OperMode=1,GamePauseStatus=paused,BassDmcActive=owner,
                      CurrentBank=157,CurrentBankC=166,GuestSweepControl=control,GuestSweepPeriod=128)
            for n,v in seed.items():m[address(b,n)]=v
            m[0x5115],m[0x5116],m[0x4015]=157,166,16 if owner else 0
            m[address(b,'GuestWorldQueues')]=queue;m[510],m[511]=255,126;m.writes=[]
            c=NesMPU(memory=m,pc=address(b,'GuestAudioFinish'));c.a,c.x,c.y,c.p,c.sp=85,3,7,0x79,253
            for _ in range(12000):
                if c.pc==0x7f00:break
                c.step()
            else:raise AssertionError(('Mixer timeout',char,owner,paused,queue,hex(c.pc)))
            return c,m
        c,m=finish(old);d,n=finish(new)
        assert snapshot(c,m)==snapshot(d,n),('Full mixer mismatch',char,owner,paused,queue,control,
                (c.a,c.x,c.y,c.p,c.sp),(d.a,d.x,d.y,d.p,d.sp))
        mixcost[d.processorCycles-c.processorCycles]+=1;mixer+=1
    status_controls=0
    for owner,status,mask,control,pin in itertools.product([0,1,2,3,4,5,255],[0,15,16,31],[0,1,2,3,8],[0,153],flags):
        pair(128,pin,owner=owner,status=status,mask=mask,control=control);status_controls+=1
    proof=dict(passed=True,native_run=False,baseline_ROM_sha256=sha(a.baseline),candidate_ROM_sha256=sha(a.candidate),
               math_cases=count,period_range=[18,2047],bounded_timer_bits=11,physical_P_contexts=64,
               complete_gate_AXYP_SP_RAM_SMC_banks_ordered_APU_exact=True,guarded_cases=controls,
               complete_mixer_cases=mixer,physical_DMC_status_guard_cases=status_controls,math_cycle_delta_histogram=dict(sorted(costs.items())),
               guard_cycle_delta_histogram=dict(sorted(other.items())),mixer_cycle_delta_histogram=dict(sorted(mixcost.items())),
               checker_sha256=sha(Path(__file__)),native_recovery_claim=False)
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))


if __name__=='__main__':main()
