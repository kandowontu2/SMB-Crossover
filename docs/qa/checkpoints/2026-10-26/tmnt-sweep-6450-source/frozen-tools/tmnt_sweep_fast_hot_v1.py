"""Full source calls with native188-byte binding and disclosed shared cue.

The historical capture did not save a complete mixer RAM snapshot. These are
arranged BEFORE-call shared effect/physical-status inputs, never relabelled as
literal native407 reconstruction or recovered draws.
"""
from pathlib import Path
from collections import Counter
import argparse
import csv
import json
from check_tmnt_render_oa import load,address,location
from verify_native_relocation import NesMPU
from tmnt_native_storage_multiply import MathMemory
from tmnt_native_storage_driver import ROOT,sha
from tmnt_sweep_fast_outer_v1 import outcome


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['baseline','candidate','storage','output']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--cue-tick',type=int,required=True);a=p.parse_args()
    assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT);a.output.mkdir(parents=True)
    native=a.storage/'parser-native-pilot-v1/candidate-easy/source-state.csv'
    states={int(r['sourceTick']):bytes.fromhex(r['ZP14_RAM174_hex'])for r in csv.DictReader(native.open())}
    machines=[]
    for rom in [a.baseline,a.candidate]:
        b=load(rom);m=MathMemory(b);m.page(2,38)
        for n,v in dict(SelectedCharacter=19,TnVariant=0,OperMode=1,CrossoverBehaviorVersion=0,
                       AreaMusicQueue=1,CurrentBank=215,CurrentBankC=166,XgAudioCharacter=255).items():m[address(b,n)]=v
        machines.append((b,m,NesMPU(memory=m)))
    rows=[];calls=[]
    hooks=['AudioUpdate','ExpandedAudioUpdate','GuestAudioBegin','BassAudioBegin','GuestAudioFinish',
           'GuestExpansionFlush','GuestExpansionSweepClock','GuestExpansionSweepTarget',
           'TnExpansionSweepGate','TnExpansionFlushFast']
    for tick in range(506):
        times=[];profiles=[]
        for b,m,c in machines:
            m[0x4015]=m[0x4015]&15
            if tick==a.cue_tick:m[address(b,'Square1SoundQueue')]=32
            c.pc,c.a,c.x,c.y,c.p,c.sp=address(b,'AudioUpdate'),85,3,7,32,253
            m[510],m[511]=255,126;m.writes=[];m.math_events=[];start=c.processorCycles
            keys={((location(b,n)-16)//8192,address(b,n)):n for n in hooks if n in b['syms']}
            frames=[];spans=[];gate={};own=Counter()
            for _ in range(50000):
                bank=lambda pc:m.banks[(pc-0x8000)//8192]if pc>=0x8000 else -1
                if tick in[407,505]:
                    while frames and(c.pc,c.sp,bank(c.pc))==(frames[-1]['ret'],frames[-1]['sp'],frames[-1]['bank']):
                        f=frames.pop();f['cycles']=c.processorCycles-f.pop('start');spans.append(f)
                if c.pc==0x7f00:break
                if tick in[407,505]:
                    name=keys.get((bank(c.pc),c.pc))
                    if name:
                        ret=(m[0x100+(c.sp+1)%256]+256*m[0x100+(c.sp+2)%256]+1)&65535
                        frames.append(dict(name=name,ret=ret,sp=(c.sp+2)&255,bank=bank(ret),start=c.processorCycles))
                        if name in['GuestExpansionFlush','TnExpansionSweepGate']:
                            gate={n:m[address(b,n)]for n in['BassDmcActive','GuestMixMask','GuestSweepControl','GuestSweepDivider','GuestSweepReload']}
                            gate['period']=m[address(b,'GuestSweepPeriod')]+256*m[address(b,'GuestSweepPeriod')+1]
                            gate['dirty123']=[m[address(b,'GuestFxDirty')+i]for i in[1,2,3]]
                    owner=frames[-1]['name']if frames else'outer';before=c.processorCycles
                m.executing_PC=c.pc;c.step()
                if tick in[407,505]:own[owner]+=c.processorCycles-before
            else:raise AssertionError(('Hot full source timeout',tick,hex(c.pc)))
            state=bytes(m[address(b,'TnAudioZp'):address(b,'TnAudioZp')+14]+m[address(b,'TnAudioRam'):address(b,'TnAudioRam')+174])
            assert state==states[tick],('Original188byte native state',tick)
            times.append(c.processorCycles-start)
            if tick in[407,505]:profiles.append(dict(full_cycles=times[-1],spans=spans,exclusive=dict(own),sweep_entry=gate))
        assert outcome(machines[0][2],machines[0][1])==outcome(machines[1][2],machines[1][1]),('Full source/state/ordered APU difference',tick)
        assert machines[0][1].math_events==machines[1][1].math_events
        calls.append(dict(tick=tick,parent=times[0],candidate=times[1],delta=times[1]-times[0]))
        if tick in[407,505]:rows.append(calls[-1]|dict(profiles=profiles))
    proof=dict(passed=True,source_only=True,native_run=False,baseline_ROM_sha256=sha(a.baseline),candidate_ROM_sha256=sha(a.candidate),
               full_calls=506,all_original188byte_native_states_exact=True,full_AXYP_SP_RAM_SMC_banks_ordered_APU_exact=True,
               arranged_shared_fireball_before_call=a.cue_tick,arranged_physical4015_status_cleared_before_each_call=True,
               literal_full_native_snapshot=False,actual_native_source_state_sha256=sha(native),hot_calls=rows,
               total_delta=sum(r['delta']for r in calls),delta_range=[min(r['delta']for r in calls),max(r['delta']for r in calls)],
               checker_sha256=sha(Path(__file__)),native_deadline_recovery_claim=False)
    (a.output/'all-calls.json').write_text(json.dumps(calls,indent=2)+'\n')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(passed=True,hot_calls=[{k:v for k,v in r.items()if k!='profiles'}for r in rows],total_delta=proof['total_delta'],range=proof['delta_range'])))


if __name__=='__main__':main()
