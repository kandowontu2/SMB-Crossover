"""Actual assembled noise owners, original source schedules, priorities and lifecycle."""
from pathlib import Path
import argparse,csv,hashlib,itertools,json
from cv3_dmc_complete_cpu_v1 import LaneArena,apu,regs
from cv3_primary_sfx_source_v1 import Original,CV3
from check_tmnt_render_oa import load,address
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def init(b,variant=3):
 q=LaneArena(b,5);q.put(Cv3Variant=variant,AreaMusicQueue=1);q.invoke('AudioUpdate');q.put(AreaMusicQueue=0);return q
def sound(q,event):
 q.invoke('Cv3Spawn',a={0x13:1,0x15:2,0x1f:6}[event])
def noise(q):return sorted((a,v)for a,v in apu(q)if a in[0x400c,0x400e,0x400f])
def live(q):
 return 0 if q.get('Cv3NoiseActive')==0 or q.get('Cv3NoiseIndex')>=28 else(q.get('Cv3NoiseCue')or 0x1f)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--golden',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=[load(a.prepared/(n+'.nes'))for n in['baseline','candidate']];gold=json.loads((a.golden/'proof.json').read_text());raw=CV3.read_bytes();captures=[];legacy=[]
 for event,variant,mode in itertools.product((0x13,0x15,0x1f),(1,3),(0,1)):
  q=init(new,variant);q.put(CrossoverBehaviorVersion=mode);source=list(csv.DictReader((a.golden/f'event-{event:02x}-apu.csv').open()));last=max(int(r['frame'])for r in source);sound(q,event)
  assert q.get('AvAudioRequest')=={0x13:27,0x15:28,0x1f:26}[event]
  for frame in range(last+1):
   q.invoke('AudioUpdate');expected=sorted((int(r['address']),int(r['value']))for r in source if int(r['frame'])==frame);assert noise(q)==expected,(event,variant,mode,frame,noise(q),expected)
  assert q.get('Cv3NoiseActive')==1 and q.get('Cv3NoiseIndex')==28
  q.invoke('AudioUpdate');assert q.get('Cv3NoiseActive')==0 and q.get('AvAudioRequest')==0
  captures.append(dict(event=event,variant=variant,mode=mode,source_frames=last+1,exact_same_frame_source_register_values=True,common_flush_order='ASC C/E/F; source executable C/F/E retained in golden'))
 # Existing1F actual whole music/mixer remains state/hardware exact except the
 # new unused cue byte and reset helper. Record its active cost honestly.
 cost=[]
 for mode in(0,1):
  qs=[init(b)for b in[old,new]]
  for q in qs:q.put(CrossoverBehaviorVersion=mode);sound(q,0x1f)
  for frame in range(40):
   cs=[q.invoke('AudioUpdate')[0]for q in qs];assert apu(qs[0])==apu(qs[1])and regs(cs[0])==regs(cs[1])and qs[0].m.banks==qs[1].m.banks
   assert all(qs[0].m[i]==qs[1].m[i]for i in range(0x8000)if not 0x100<=i<0x200 and i!=address(new,'Cv3NoiseCue'))
   cost.append(cs[1].processorCycles-cs[0].processorCycles)
 priorities=[]
 for current,incoming,age in itertools.product((0x13,0x15,0x1f),(0x13,0x15,0x1f),(0,1,5,12,13,16,17,27,28,32)):
  o=Original(raw);o.call(0xe227);o.call(0xe25f,a=current)
  for _ in range(age):o.call(0xe24e)
  before=o.m[0x10d];o.call(0xe25f,a=incoming);source_result=o.m[0x10d]
  q=init(new);sound(q,current)
  for _ in range(age):q.invoke('AudioUpdate')
  assert live(q)==before if age else q.get('AvAudioRequest')!=0
  sound(q,incoming);q.invoke('AudioUpdate');o.m.trace=[];o.m.frame=0;o.call(0xe24e);expected=sorted((r['address'],r['value'])for r in o.m.trace if r['address']in[0x400c,0x400e,0x400f]);assert noise(q)==expected,(current,incoming,age,noise(q),expected)
  assert live(q)==o.m[0x10d],(current,incoming,age,source_result,live(q),o.m[0x10d]);priorities.append(dict(current=current,incoming=incoming,age=age,original_before=before,original_request_result=source_result,actual_next_owner=live(q)))
 owners=[]
 for variant,sub,mode in itertools.product((1,3),(1,2),(0,1)):
  qs=[init(b,variant)for b in[old,new]]
  for q in qs:q.put(CrossoverBehaviorVersion=mode,Cv3Fresh=0x40,SavedJoypadBits=0x48);q.set('Cv3Hearts',10,variant-1);q.set('Cv3Subweapon',sub,variant-1);q.invoke('Cv3WeaponsGate');q.put(Cv3Fresh=0,SavedJoypadBits=0,Cv3AttackAge=14)
  cs=[q.invoke('Cv3WeaponsGate')[0]for q in qs];assert regs(cs[0])==regs(cs[1])
  assert qs[0].get('AvAudioRequest')==0 and qs[1].get('AvAudioRequest')==26+sub
  allow=set(range(0x100,0x200))|{address(new,'AvAudioRequest')};assert all(qs[0].m[i]==qs[1].m[i]for i in range(0x8000)if i not in allow);owners.append(dict(variant=variant,subweapon=sub,mode=mode,actual_release_request=qs[1].get('AvAudioRequest')))
 # No projectile, no sound; existing common typed queues preserve precedence.
 controls=[]
 for typ,pending,full in itertools.product((1,2,6),(0,1,21,22,25),(0,1)):
  q=init(new);q.put(AvAudioRequest=pending)
  if full:q.array('Cv3ShotType',[1]*4)
  q.invoke('Cv3Spawn',a=typ);expected=pending if pending or full else{1:27,2:28,6:26}[typ];assert q.get('AvAudioRequest')==expected;controls.append(dict(type=typ,pending=pending,pool_full=full,after=expected))
 lifecycle=[]
 for event,kind in itertools.product((0x13,0x15),('pause','scene-pending','scene-active','character')):
  q=init(new);sound(q,event)
  if kind!='scene-pending':q.invoke('AudioUpdate')
  if kind=='pause':
   before=(q.get('Cv3NoiseActive'),q.get('Cv3NoiseIndex'),q.get('Cv3NoiseCue'));q.put(GamePauseStatus=1);q.invoke('AudioUpdate');assert before==(q.get('Cv3NoiseActive'),q.get('Cv3NoiseIndex'),q.get('Cv3NoiseCue'));q.put(GamePauseStatus=0);q.invoke('AudioUpdate');assert q.get('Cv3NoiseIndex')==before[1]+1
  elif kind.startswith('scene'):
   q.invoke('Cv3NoiseSceneReset');assert q.get('AvAudioRequest')==0;q.invoke('AudioUpdate');assert q.get('Cv3NoiseActive')==0
  else:q.put(SelectedCharacter=4);q.invoke('GuestAudioBegin');assert q.get('Cv3NoiseActive')==0 and q.get('Cv3NoiseCue')==0
  lifecycle.append(dict(event=event,kind=kind,passed=True))
 result=dict(passed=True,accepted=False,ROM_sha256=sha(a.prepared/'candidate.nes'),baseline_sha256=sha(a.prepared/'baseline.nes'),actual_source_trace_cases=len(captures),source_trace_cases=captures,existing1F_full_AudioUpdate_cases=80,existing1F_cycle_delta_values=sorted(set(cost)),original_per_voice_priority_cases=len(priorities),actual_armed_delayed_release_owner_cases=len(owners),pool_and_ordinary_queue_controls=len(controls),lifecycle_cases=lifecycle,new_private_existing_slab_bytes=1,new_RAM_allocation=0,scope='Actual assembled whole music/mixer and weapon payment/release chains. Sparse original same-frame APU values and original priority are authenticated; common ascending hardware flush order remains adapted. No native worker, waveform or campaign acceptance.')
 (a.output/'priority.json').write_text(json.dumps(priorities,indent=2)+'\n');(a.output/'actual-owners.json').write_text(json.dumps(owners,indent=2)+'\n');(a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
