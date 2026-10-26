"""Actual queue command boundaries, pending/cold lifecycle and full caller ABI."""
from pathlib import Path
import argparse,hashlib,itertools,json
from check_tmnt_render_oa import load,address
from cv3_dmc_complete_cpu_v1 import LaneArena,apu,regs
from cv3_remaining_sfx_queue256_support_v1 import init,sound,EVENTS,target_voices
from cv3_remaining_sfx_queue256_cpu_v1 import setup,start,finish,nmi,slot

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);b=load(a.rom);old=load(a.rom.parent/'baseline.nes');negatives=[]
 # Preserve actual failures from prior drafts, rather than silently replace
 # their receipts or label their old incomplete protocol as passing.
 for tag,rom in [('menu',D/'cv3-remaining-queue-v6/candidate.nes'),('Y',D/'cv3-remaining-queue-v7/candidate.nes')]:
  if tag=='menu':
   q=init(load(rom),2);q.put(OperMode=0)
   for _ in range(512):q.invoke('Cv3NoiseSceneReset')
   assert slot(q)==64 and q.get('Cv3FxQueueOverflow')==192;negatives.append(dict(kind=tag,ROM_sha256=sha(rom),reset_calls=512,occupancy=slot(q),overflow_byte=q.get('Cv3FxQueueOverflow'),expected_failure=True))
  else:
   qs=[LaneArena(z,2)for z in [old,load(rom)]]
   for q in qs:q.put(AreaMusicQueue=1);q.invoke('AudioUpdate');q.put(GamePauseStatus=1,AreaMusicQueue=0)
   cs=[q.invoke('AudioUpdate')[0]for q in qs];assert regs(cs[0])!=regs(cs[1]);negatives.append(dict(kind=tag,ROM_sha256=sha(rom),character=2,parent_AXYP=regs(cs[0]),draft_AXYP=regs(cs[1]),expected_failure=True))
 (a.output/'retained-negatives.json').write_text(json.dumps(negatives,indent=2)+'\n')
 menu=[]
 for event in [None,0x1f,0x21]:
  q=init(b,2)
  if event:sound(q,event)
  q.put(OperMode=0)
  for count in range(512):
   q.invoke('Cv3NoiseSceneReset');q.invoke('AudioUpdate');assert slot(q)<=2 and q.get('Cv3FxQueueOverflow')==0
  occupancy=slot(q);q.put(OperMode=1,AreaMusicQueue=1);q.invoke('AudioUpdate');assert slot(q)==0 and target_voices(q)==(0,0)and q.get('Cv3FxOwned')==0
  menu.append(dict(pending_event=event,real_scene_resets=512,real_vanilla_audio_updates=512,largest_bound=2,final_menu_occupancy=occupancy,resume_music_flush=True))
 lives=[]
 for event,mode,kind in itertools.product(EVENTS,[0,1],['pause','scene','death','music','menu','character']):
  q=init(b,2 if event in[0x24,0x21,0x1e]else 3);q.put(CrossoverBehaviorVersion=mode);sound(q,event);q.invoke('AudioUpdate');before=(target_voices(q),q.get('Cv3NoiseIndex'),q.get('Cv3FxPulseFrame'),q.get('Cv3FxOwned'))
  if kind=='pause':
   q.put(GamePauseStatus=1);q.invoke('AudioUpdate');assert before==(target_voices(q),q.get('Cv3NoiseIndex'),q.get('Cv3FxPulseFrame'),q.get('Cv3FxOwned'));q.put(GamePauseStatus=0);q.invoke('AudioUpdate')
  elif kind=='scene':q.invoke('Cv3NoiseSceneReset');assert slot(q)==1;q.invoke('AudioUpdate');assert target_voices(q)==(0,0)and q.get('Cv3FxOwned')==0
  elif kind=='death':q.invoke('KillPlayer');assert slot(q)==1;q.invoke('AudioUpdate');q.put(EventMusicQueue=1);q.invoke('AudioUpdate');assert target_voices(q)==(0,0)and q.get('Cv3FxOwned')==0
  elif kind=='music':q.put(AreaMusicQueue=2);q.invoke('AudioUpdate');assert target_voices(q)==(0,0)and q.get('Cv3FxOwned')==0 and slot(q)==0
  elif kind=='menu':q.put(OperMode=0);q.invoke('AudioUpdate');q.invoke('Cv3ResetGate');q.put(OperMode=1,AreaMusicQueue=1);q.invoke('AudioUpdate');assert target_voices(q)==(0,0)and q.get('Cv3FxOwned')==0 and slot(q)==0
  else:q.put(SelectedCharacter=4);q.invoke('GuestAudioBegin');assert target_voices(q)==(0,0)and q.get('Cv3FxOwned')==0 and slot(q)==0
  lives.append(dict(event=event,mode=mode,kind=kind,passed=True))
 (a.output/'lifecycle.json').write_text(json.dumps(lives,indent=2)+'\n')
 # Full successful/failed Cv3Spawn caller, including every live output flag.
 callers=[];private=set(range(address(b,'RgAudioZp')+36,address(b,'RgAudioZp')+160))|set(range(address(b,'Cv3FxQueue'),address(b,'Cv3FxQueue')+256))|{address(b,'AvAudioRequest'),address(b,'Cv3NoiseActive')}
 for typ,face,crouch,flags,pool in itertools.product(range(1,7),[1,2],[0,1],[0x20,0x21,0x60,0x69,0xa0,0xe1],[False,True]):
  qs=[init(z,2)for z in [old,b]]
  for q in qs:
   q.put(PlayerFacingDir=face,Cv3AttackCrouch=crouch)
   if pool:q.array('Cv3ShotType',[1]*4)
  cs=[q.invoke('Cv3Spawn',a=typ,x=0x71,y=0xa5,flags=flags)[0]for q in qs];assert regs(cs[0])==regs(cs[1]),('outer ABI',typ,face,crouch,flags,pool,regs(cs[0]),regs(cs[1]))
  changes=[(hex(i),qs[0].m[i],qs[1].m[i])for i in range(0x8000)if not 0x100<=i<0x200 and i not in private and qs[0].m[i]!=qs[1].m[i]];assert not changes,changes[:10];assert qs[0].m.banks==qs[1].m.banks
  assert slot(qs[1])==(0 if pool else 1);callers.append(dict(typ=typ,face=face,crouch=crouch,flags=flags,pool_full=pool,old_cycles=cs[0].processorCycles,new_cycles=cs[1].processorCycles))
 (a.output/'full-caller.json').write_text(json.dumps(callers,separators=(',',':'))+'\n')
 boundaries=[]
 for event,age,counter,command,prior_cancel in itertools.product([None,0x1f,0x21],[0,12],[0,255],[7,8],[False,True]):
  def make():
   q=setup(b,age,event,counter)
   if prior_cancel:q.invoke('Cv3FxCancel')
   return q
  probe=make();c=start(probe,'Cv3FxQueueCommand',command);published=False;trace=[]
  for _ in range(300):
   if c.pc==0x5b00:break
   at=len(probe.m.writes);pc=c.pc;c.step();published|=any(ad==address(b,'Cv3FxQueueHead')for ad,v in probe.m.writes[at:]);trace.append(dict(pc=pc,committed=published))
  else:raise AssertionError('command producer timeout')
  for boundary in range(len(trace)+1):
   q=make();c=start(q,'Cv3FxQueueCommand',command)
   for _ in range(boundary):c.step()
   committed=trace[boundary-1]['committed']if boundary else False;receipt=nmi(q,c);finish(c);ref=make();d=start(ref,'Cv3FxQueueCommand',command)
   if committed:finish(d);expected=nmi(ref,d)
   else:expected=nmi(ref,d);finish(d)
   assert receipt['APU']==expected['APU'],('command NMI APU',event,age,counter,command,prior_cancel,boundary)
   # A second CANCEL after the earlier committed CANCEL has been consumed is
   # idempotent. The ring sequence count may differ, but no source request,
   # source tick, APU register store, phase, or unrelated RAM may differ.
   q.invoke('AudioUpdate');ref.invoke('AudioUpdate');assert apu(q)==apu(ref)
   queue=set(range(address(b,'Cv3FxQueue'),address(b,'Cv3FxQueue')+256))|{address(b,'Cv3FxQueueHead'),address(b,'Cv3FxQueueTail')}
   changes=[(hex(i),q.m[i],ref.m[i])for i in range(0x8000)if not 0x100<=i<0x200 and i not in queue and q.m[i]!=ref.m[i]];assert not changes,('command RAM',event,age,counter,command,prior_cancel,boundary,changes[:10])
   assert q.m.banks==ref.m.banks and q.get('Cv3FxQueueOverflow')==0
   boundaries.append(dict(current=event,age=age,counter=counter,command=command,prior_cancel=prior_cancel,boundary=boundary,committed=committed,actual_NMI_instructions=receipt['instructions'],actual_NMI_cycles=receipt['cycles']))
 (a.output/'command-nmi-boundaries.json').write_text(json.dumps(boundaries,separators=(',',':'))+'\n')
 result=dict(passed=True,accepted=False,ROM_sha256=sha(a.rom),held_parent_ROM_sha256=sha(a.rom.parent/'baseline.nes'),actual_menu_resets=sum(r['real_scene_resets']for r in menu),menu=menu,actual_lifecycle_cases=len(lives),whole_Cv3Spawn_caller_AXYP_gameplay_RAM_cases=len(callers),actual_full_lag_NMI_command_boundaries=len(boundaries),consecutive_pending_CANCEL_only_idempotency=True,source_effect_events_coalesced=False,retained_negatives=negatives,scope='Source/CPU protocol and actual owner components. No native cadence, audible playback, OAM/CHR, full-game or adoption claim. Remaining generic-world/ordinary/IRQ/source-layout/cost controls separate.',tool_sha256=sha(__file__))
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
