"""Complete per-voice original schedules/priority, real abilities and lifecycle CPU."""
from pathlib import Path
import argparse,csv,hashlib,itertools,json
from check_tmnt_render_oa import load,address
from cv3_dmc_complete_cpu_v1 import LaneArena,apu,regs
from cv3_primary_sfx_source_v1 import Original,CV3
EVENTS={0x13:1,0x15:2,0x24:3,0x21:4,0x1e:5,0x1f:6,0x2f:None}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def init(b,variant=3):
 q=LaneArena(b,5);q.put(Cv3Variant=variant,AreaMusicQueue=1);q.invoke('AudioUpdate');q.put(AreaMusicQueue=0);return q
def sound(q,event):
 if event==0x2f:
  q.put(Cv3Bat=0,Cv3AttackAge=0,Cv3HurtAge=0,Cv3Fresh=0x80,SavedJoypadBits=4);q.set('Cv3Hearts',10,2);q.invoke('Cv3BatUpdate')
 else:q.invoke('Cv3Spawn',a=EVENTS[event])
 # Owners no longer matter to audio after the real successful release. Free
 # fixture projectile slots so repeated request controls do not become pool tests.
 q.array('Cv3ShotType',[0]*4)
def source_voices(o):return(o.m[0x10a],o.m[0x10d])
def target_voices(q):
 noise=q.get('Cv3FxNoiseID')
 if q.get('Cv3NoiseActive')==1:noise=0x1f if q.get('Cv3NoiseIndex')<28 else 0
 return(q.get('Cv3FxPulseID'),noise)
def exact(qs):
 allowed=set(range(0x100,0x200))|set(range(address(qs[1].b,'RgAudioZp')+36,address(qs[1].b,'RgAudioZp')+56))
 assert all(qs[0].m[i]==qs[1].m[i]for i in range(0x8000)if i not in allowed),[(hex(i),qs[0].m[i],qs[1].m[i])for i in range(0x8000)if i not in allowed and qs[0].m[i]!=qs[1].m[i]][:15]
 assert apu(qs[0])==apu(qs[1])and qs[0].m.banks==qs[1].m.banks
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--golden',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=[load(a.prepared/(n+'.nes'))for n in['baseline','candidate']];gold=json.loads((a.golden/'proof.json').read_text());captures=[];raw=CV3.read_bytes()
 for event,mode in itertools.product(EVENTS,[0,1]):
  q=init(new,2 if event in[0x24,0x21,0x1e]else 3);q.put(CrossoverBehaviorVersion=mode);sound(q,event);o=Original(raw);o.call(0xe227);o.call(0xe25f,a=event)
  rows=list(csv.DictReader((a.golden/f'event-{event:02x}-apu.csv').open()));last=max(int(r['frame'])for r in rows);ends={voice:max([int(r['frame'])for r in rows if (int(r['address'])<0x4004)==(voice=='pulse')],default=-1)for voice in['pulse','noise']};cost=[]
  for frame in range(last+3):
   c,_=q.invoke('AudioUpdate');cost.append(c.processorCycles);o.m.trace=[];o.call(0xe24e)
   for voice,index,reg in [('pulse',0,[0x4000,0x4001,0x4002,0x4003]),('noise',1,[0x400c,0x400e,0x400f])]:
    if frame<=ends[voice]:
     actual=sorted((at,v)for at,v in apu(q)if at in reg);expected=sorted((int(r['address']),int(r['value']))for r in rows if int(r['frame'])==frame and int(r['address'])in reg);assert actual==expected,(hex(event),mode,frame,voice,actual,expected)
   assert target_voices(q)==source_voices(o),(hex(event),mode,frame,target_voices(q),source_voices(o))
  assert q.get('Cv3FxOwned')==q.get('Cv3NoiseActive')==0
  captures.append(dict(source_id=event,mode=mode,frames=last+3,exact_same_source_frame_APU_values_and_voice_priority=True,whole_AudioUpdate_cycles=[min(cost),max(cost)]))
 (a.output/'capture-cases.json').write_text(json.dumps(captures,indent=2)+'\n');priorities=[]
 for current,incoming,age in itertools.product(EVENTS,EVENTS,[0,1,5,12,16,27,42,63,88]):
  q=init(new);sound(q,current);o=Original(raw);o.call(0xe227);o.call(0xe25f,a=current)
  for _ in range(age):q.invoke('AudioUpdate');o.call(0xe24e)
  before=source_voices(o);assert target_voices(q)==before if age else True
  sound(q,incoming);o.call(0xe25f,a=incoming);wanted=source_voices(o);o.m.trace=[];o.call(0xe24e)
  try:q.invoke('AudioUpdate')
  except Exception as error:raise AssertionError(('Actual priority update failure',hex(current),hex(incoming),age,{n:q.get(n)for n in['Cv3NoiseActive','Cv3NoiseIndex','Cv3FxNoiseID','Cv3FxPulseID','Cv3FxOwned','Cv3FxNoisePtr','Cv3FxPulsePtr']}))from error
  # Only the voice retained/admitted as a source cue is compared with the
  # source executable. A released voice restores the independently advancing
  # host CV1 music image, whose writes are intentionally not source silence.
  for index,reg in[(0,[0x4000,0x4001,0x4002,0x4003]),(1,[0x400c,0x400e,0x400f])]:
   if wanted[index]:
    expected=sorted((r['address'],r['value'])for r in o.m.trace if r['address']in reg);actual=sorted((at,v)for at,v in apu(q)if at in reg)
    assert actual==expected,(hex(current),hex(incoming),age,index,actual,expected)
  assert target_voices(q)==source_voices(o),(hex(current),hex(incoming),age,target_voices(q),source_voices(o));priorities.append(dict(current=current,incoming=incoming,age=age,before=before,request_admitted=wanted,after_update=target_voices(q)))
 owners=[]
 for variant,sub,mode in itertools.product([1,2,3],[1,2,3],[0,1]):
  qs=[init(b,variant)for b in[old,new]]
  for q in qs:q.put(CrossoverBehaviorVersion=mode,Cv3Fresh=0x40,SavedJoypadBits=0x48);q.set('Cv3Hearts',10,variant-1);q.set('Cv3Subweapon',sub,variant-1);q.invoke('Cv3WeaponsGate');q.put(Cv3AttackAge=14,Cv3Fresh=0,SavedJoypadBits=0)
  cs=[q.invoke('Cv3WeaponsGate')[0]for q in qs];assert regs(cs[0])==regs(cs[1]);types=[q.get('Cv3ShotType',i)for i in range(4)];newq=qs[1];event=([0x24,0x21,0x1e][sub-1]if variant==2 else[0x13,0x15,None][sub-1]);expected={0x13:27,0x15:28,0x24:29,0x21:30,0x1e:31,None:0}[event];assert newq.get('AvAudioRequest')==expected
  for symbol,count in[('Cv3ShotType',4),('Cv3ShotX',4),('Cv3ShotY',4),('Cv3ShotPage',4),('Cv3Hearts',3)]:assert[qs[0].get(symbol,i)for i in range(count)]==[qs[1].get(symbol,i)for i in range(count)]
  owners.append(dict(variant=variant,subweapon=sub,mode=mode,types=types,request=expected))
 lifecycle=[]
 for event,mode,kind in itertools.product(EVENTS,[0,1],['pause','scene','death','music','menu','character']):
  q=init(new,2 if event in[0x24,0x21,0x1e]else 3);q.put(CrossoverBehaviorVersion=mode);sound(q,event);q.invoke('AudioUpdate');before=(target_voices(q),q.get('Cv3NoiseIndex'),q.get('Cv3FxPulseFrame'),q.get('Cv3FxOwned'))
  if kind=='pause':
   q.put(GamePauseStatus=1);q.invoke('AudioUpdate');assert before==(target_voices(q),q.get('Cv3NoiseIndex'),q.get('Cv3FxPulseFrame'),q.get('Cv3FxOwned'));q.put(GamePauseStatus=0);q.invoke('AudioUpdate')
  elif kind=='scene':q.invoke('Cv3NoiseSceneReset');q.invoke('AudioUpdate');assert target_voices(q)==(0,0)and q.get('Cv3FxOwned')==0
  elif kind=='death':
   q.invoke('KillPlayer');assert target_voices(q)==(0,0);q.invoke('AudioUpdate');q.put(EventMusicQueue=1);q.invoke('AudioUpdate');assert target_voices(q)==(0,0)and q.get('Cv3FxOwned')==0
  elif kind=='music':q.put(AreaMusicQueue=2);q.invoke('AudioUpdate');assert target_voices(q)==(0,0)and q.get('Cv3FxOwned')==0
  elif kind=='menu':
   # Menu's real AudioUpdate takes vanilla audio; private phases are dormant,
   # not evidence of audible continuation. Exercise actual scene reset and
   # subsequent real music owner, which must cancel before guest audio resumes.
   q.put(OperMode=0);q.invoke('AudioUpdate');assert before==(target_voices(q),q.get('Cv3NoiseIndex'),q.get('Cv3FxPulseFrame'),q.get('Cv3FxOwned'))
   q.invoke('Cv3ResetGate');assert target_voices(q)==(0,0);q.put(OperMode=1,AreaMusicQueue=1);q.invoke('AudioUpdate');assert target_voices(q)==(0,0)and q.get('Cv3FxOwned')==0
  else:q.put(SelectedCharacter=4);q.invoke('GuestAudioBegin');assert target_voices(q)==(0,0)and q.get('Cv3FxOwned')==0
  lifecycle.append(dict(event=event,mode=mode,kind=kind,passed=True))
 legacy=[]
 for mode in[0,1]:
  qs=[init(b)for b in[old,new]]
  for q in qs:q.put(CrossoverBehaviorVersion=mode);sound(q,0x1f)
  for frame in range(40):
   cs=[q.invoke('AudioUpdate')[0]for q in qs];exact(qs);assert regs(cs[0])==regs(cs[1]);legacy.append(cs[1].processorCycles-cs[0].processorCycles)
 result=dict(passed=True,accepted=False,ROM_sha256=sha(a.prepared/'candidate.nes'),baseline_ROM_sha256=sha(a.prepared/'baseline.nes'),source_frame_cases=captures,original_independent_voice_priority_cases=len(priorities),mixed_raw_APU_bytes_strict_including400F=True,actual_armed_subweapon_release_cases=owners,actual_death_pause_scene_music_menu_character_controls=len(lifecycle),legacy1F_complete_AudioUpdate_cases=len(legacy),legacy1F_cycle_deltas=sorted(set(legacy)),source_flush_order='Original ordered goldens retained; common target ascending hardware flush remains adaptation.',scope='Actual original executable and assembled ability/music/death CPU components only. No native bus/DMA/PPU/cadence, audible waveform, installation or gameplay certification.',tool_sha256=sha(__file__))
 (a.output/'priorities.json').write_text(json.dumps(priorities,separators=(',',':'))+'\n');(a.output/'lifecycle.json').write_text(json.dumps(lifecycle,indent=2)+'\n');(a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
