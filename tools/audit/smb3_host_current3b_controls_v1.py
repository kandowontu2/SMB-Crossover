"""Finite current-host source recurrence, transition, foreign and borrowing controls."""
from pathlib import Path
import argparse,hashlib,json,traceback
from smb3_host_current3b_cpu_v1 import Fixture,HostMemory,ROLES,D,R,sha,put,projected
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(exist_ok=False,parents=True);b=scoped_load(a.packet/'candidate.nes');old=scoped_load(D/'root-current-roster-composition-v1/candidate.nes');rows=[];trans=[];foreign=[]
 try:
  reference=json.loads((D/'smb3-original-music-closure-v3/proof.json').read_text())['roles']
  for role,(name,bit,track)in ROLES.items():
   f=Fixture(b,0,0);limit=reference[role]['exact_call_boundary_state_repeat']['repeat_tick'];cost=[f.invoke((name,bit))]
   for _ in range(limit):cost.append(f.invoke())
   assert f.q.get('RgAudioSong')==track
   row=dict(role=role,calls=len(cost),source_APU_stores=sum(x['APU_stores']for x in f.sourcecalls),source_payload_checks=f.m.samplechecks,whole_cold=cost[0],whole_play_mean=sum(cost[1:])/limit,whole_peak=max(cost[1:]),minimum_SP=f.minsp);rows.append(row);print(json.dumps(row),flush=True)
  for mode in [0,1]:
   for variant in [0,1]:
    f=Fixture(b,mode,variant);f.invoke(('AreaMusicQueue',1))
    for _ in range(8):f.invoke()
    before=len(f.sourcecalls);state=projected(f.m,b);f.q.set('GamePauseStatus',1)
    for _ in range(3):f.invoke()
    assert len(f.sourcecalls)==before and projected(f.m,b)==state and not f.m.hwdmc and f.m.banks[3]==127
    f.q.set('GamePauseStatus',0);f.invoke();assert len(f.sourcecalls)==before+1
    # Modeled peripheral fetch completion, not a waveform or DMA-clock simulation.
    f.q.put(BassDmcActive=4,Cv3DmcPriority=128,GuestNativeEnable=31,GuestCombinedEnable=31);f.m.hwdmc=False;f.m.page(3,70);f.m[0x4011]=47
    f.q.invoke('GuestDmcStatus',a=31);assert f.q.get('BassDmcActive')==0 and f.q.get('Cv3DmcPriority')==0 and f.m.banks[3]==127 and f.m.hw[17]==47
    f.invoke(('EventMusicQueue',1));assert f.q.get('RgAudioSong')==43 and f.sourcecalls[-1]['kind']=='init'
    for _ in range(4):f.invoke()
    before=len(f.sourcecalls);f.invoke(('EventMusicQueue',128));assert len(f.sourcecalls)==before and not f.m.hwdmc and f.m.banks[3]==127
    f.invoke(('AreaMusicQueue',4));assert f.q.get('RgAudioSong')==12 and f.sourcecalls[-1]['kind']=='init'
    # Real vanilla route after character/title change owns cleanup in already-mappedA5.
    f.q.put(OperMode=0,BassDmcActive=4,Cv3DmcPriority=128);f.m.page(3,70);f.m.hwdmc=True;f.invoke();assert f.q.get('XgAudioCharacter')==255 and f.q.get('BassDmcActive')==0 and f.m.banks[3]==127 and not f.m.hwdmc
    f.q.put(OperMode=1);f.invoke(('AreaMusicQueue',1));assert f.sourcecalls[-1]['kind']=='init'
    trans.append(dict(mode=mode,variant=variant,pause_resume_death_silence_area_title_reentry=True,DMC_completion_DAC_held=47,minimum_SP=f.minsp))
  # Same inputs across every actual identity slot, excluding newly-owned17.
  ids=list(range(20));count=0
  for char in ids:
   if char==17:continue
   for mode in [0,1]:
    for variant in ([0,1,2,3]if char==18 else[0]):
     pair=[]
     for bundle in [old,b]:
      q=Arena(bundle,char);q.put(CrossoverBehaviorVersion=mode,OperMode=1,AreaMusicQueue=1,EventMusicQueue=0,XgAudioCharacter=255,GuestAudioCharacter=255,GamePauseStatus=0)
      if char==18:q.set('VvVariant',variant)
      c,t=q.invoke('AudioUpdate');pair.append((q,c,t))
     q0,c0,t0=pair[0];q1,c1,t1=pair[1]
     assert[c0.a,c0.x,c0.y,c0.p&207,c0.sp]==[c1.a,c1.x,c1.y,c1.p&207,c1.sp],('ForeignABI',char,mode,variant)
     writes=lambda t:[(r['address'],r['value'])for r in t if not 0x100<=r['address']<0x200]
     assert writes(t0)==writes(t1),('Foreign ordered state/APU/mapper writes',char,mode,variant)
     foreign.append(dict(character=char,mode=mode,variant=variant,cycle_delta=c1.processorCycles-c0.processorCycles));count+=1
  # Measure exact compiled unrolled six-byte borrow/restore call costs.
  f=Fixture(b,0,0);f.q.put(CurrentBankC=166);f.m.page(2,38);borrow=[]
  for name in ['B3Borrow','B3Restore']:
   c,_=f.q.invoke(name);borrow.append(dict(entry=name,body_including_RTS=c.processorCycles,with_call_JSR=c.processorCycles+6))
  put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,ROM_sha256=sha(a.packet/'candidate.nes'),parent_ROM_sha256=sha(D/'root-current-roster-composition-v1/candidate.nes'),roles=rows,source_call_total=sum(q['calls']for q in rows),ordered_source_APU_total=sum(q['source_APU_stores']for q in rows),source_payload_total=sum(q['source_payload_checks']for q in rows),lifecycle=trans,foreign=foreign,borrow_costs=borrow,checker_sha256=sha(__file__),limits='Modeled DMC status/fetch completion only; no actual DMC DMA/waveforms/NMI/IRQ/render timing. Complete foreground-history/IRQ and build/layout controls remain separate.'))
 except Exception as e:
  put(a.output/'failure.json',dict(passed=False,roles=rows,lifecycle=trans,foreign=foreign,error=str(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
