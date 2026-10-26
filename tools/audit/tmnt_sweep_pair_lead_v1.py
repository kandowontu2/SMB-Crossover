"""Exhaustive actual $99 sweep-pair contract at the real output continuation.

This is a source arithmetic/control lead, not a changed implementation or a
promise that its storage/routing/guards recover a native publication deadline.
"""
from pathlib import Path
import argparse
import json
from check_tmnt_render_oa import load,Memory,address
from check_tmnt_audio_fallback_oc import qualified
from verify_native_relocation import NesMPU
from tmnt_native_storage_driver import ROOT,sha


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert not a.output.exists() and not a.output.resolve().is_relative_to(ROOT)
    b=load(a.rom);q=qualified(a.rom);a.output.mkdir(parents=True)
    assert sha(a.rom)=='9a791d0e13015ff362ffc9e460aaac8c8a0a5b6f73e990959dee4e074da473fd'
    m=Memory(b);m.page(1,29)
    c=NesMPU(memory=m)
    at=lambda n:address(b,n)
    flags=[0x20|(i&15)|((i&16)<<2)|((i&32)<<2) for i in range(64)]
    output=q['GuestExpansionFlush','Output'];costs=set();count=0
    for period in range(18,2048):
        first=(period-1)>>1;second=(first-1)>>1
        for fi,pin in enumerate(flags):
            for i in range(8):m[at('GuestFxApu')+i]=[158,153,period&255,248|(period>>8),37,73,109,145][i]
            for i in range(16):m[at('GuestFxDirty')+i]=0
            for name,value in dict(GuestSweepControl=153,GuestSweepDivider=0,GuestSweepReload=0,
                                   GuestSweepPeriod=period&255,GuestSweepDelta=83,GuestMixMask=1).items():m[at(name)]=value
            m[at('GuestSweepPeriod')+1]=period>>8;m[at('GuestSweepDelta')+1]=149
            m[510],m[511]=255,126;m.writes=[]
            c.pc,c.a,c.x,c.y,c.p,c.sp=at('GuestExpansionFlush'),85,fi*3&255,fi*5&255,pin,253
            begin=c.processorCycles
            for _ in range(1000):
                if c.pc==output:break
                c.step()
            else:raise AssertionError(('Sweep pair timeout',period,pin,hex(c.pc)))
            expected_flags=(pin&12)|0xa1
            assert (c.a,c.x,c.y,c.p&207,c.sp)==(second>>8,fi*3&255,0,expected_flags&207,253),(period,pin,c.a,c.x,c.y,c.p)
            expected=dict(GuestSweepPeriod=first&255,GuestSweepDelta=second&255,GuestSweepDivider=0,
                          GuestSweepReload=0,GuestSweepTicks=0,GuestSweepControl=153)
            assert all(m[at(n)]==v for n,v in expected.items())
            assert m[at('GuestSweepPeriod')+1]==first>>8 and m[at('GuestSweepDelta')+1]==second>>8
            assert m[at('GuestExpansionApu')+2]==first&255 and m[at('GuestExpansionApu')+3]==248|(first>>8)
            assert [(k,v) for k,v in m.writes if k<0x8000 and not 0x100<=k<0x200 and not at('GuestExpansionApu')<=k<at('GuestExpansionApu')+8 and not at('GuestSweepPeriod')<=k<=at('GuestSweepTicks')]==[(0x5015,1)]
            costs.add(c.processorCycles-begin);count+=1
        if period%256==255:print(period,count,flush=True)
    proof=dict(passed=True,implementation=False,native_run=False,ROM_sha256=sha(a.rom),compiled_full_caller_prefix_cases=count,
        initial_unsigned13bit_period_range=[18,2047],all_physical_P_contexts=64,clock_control99_divider0_reload0_only=True,
        exact_two_source_halfclocks_period_formula='P1=(P0-1)>>1; finalDelta=(P1-1)>>1',
        complete_output_continuation_AXYP_SP_and_final_sweep_image_contract=True,
        actual_entry_to_output_CPUcycles=sorted(costs),new_CPUcycle_savings_not_measured=True,
        checker_sha256=sha(Path(__file__)),
        limits='No patch/helper/canonical build, changed caller routing or recovery timing is asserted. This proves only the guarded source arithmetic and final actual continuation contract. Other controls/divider/reload/periods must retain the original path. Storage, source implementation, full mixer/other identities and real IRQ/native/DMC controls remain required.')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(proof))


if __name__=='__main__':main()
