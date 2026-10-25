"""Pending/exit/pool controls and strict raw512-update original mixed chains."""
from pathlib import Path
import argparse,hashlib,itertools,json,random
from check_tmnt_render_oa import load
from cv3_primary_sfx_source_v1 import Original,CV3
from cv3_remaining_sfx_complete_cpu_v1 import init,sound,source_voices,target_voices,EVENTS
from cv3_dmc_complete_cpu_v1 import apu
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);b=load(a.rom);pending=[];bat=[];pool=[]
 for event,mode,kind in itertools.product(EVENTS,[0,1],['pause','scene','death','menu-reset','character']):
  q=init(b);q.put(CrossoverBehaviorVersion=mode);sound(q,event);before={n:q.get(n)for n in['AvAudioRequest','Cv3FxOwned','Cv3FxPendingNoise','Cv3FxPendingPulse','Cv3NoiseActive','Cv3NoiseIndex','Cv3FxPulseFrame']}
  if kind=='pause':
   q.put(GamePauseStatus=1);q.invoke('AudioUpdate');assert before=={n:q.get(n)for n in before};q.put(GamePauseStatus=0);q.invoke('AudioUpdate');assert any(target_voices(q))
  elif kind=='scene':q.invoke('Cv3NoiseSceneReset');q.invoke('AudioUpdate');assert target_voices(q)==(0,0)and q.get('AvAudioRequest')==0 and q.get('Cv3FxOwned')==0
  elif kind=='death':q.invoke('KillPlayer');q.invoke('AudioUpdate');q.put(EventMusicQueue=1);q.invoke('AudioUpdate');assert target_voices(q)==(0,0)and q.get('AvAudioRequest')==0 and q.get('Cv3FxOwned')==0
  elif kind=='menu-reset':q.put(OperMode=0);q.invoke('AudioUpdate');q.invoke('Cv3ResetGate');q.put(OperMode=1,AreaMusicQueue=1);q.invoke('AudioUpdate');assert target_voices(q)==(0,0)and q.get('AvAudioRequest')==0 and q.get('Cv3FxOwned')==0
  else:q.put(SelectedCharacter=4);q.invoke('AudioUpdate');assert q.get('Cv3FxOwned')==q.get('Cv3NoiseActive')==0 and q.get('AvAudioRequest')==0
  pending.append(dict(event=event,mode=mode,kind=kind,passed=True))
 for mode,kind in itertools.product([0,1],['manual-exit','exhaust','no-hearts','busy']):
  q=init(b);q.put(CrossoverBehaviorVersion=mode)
  if kind in['manual-exit','exhaust']:
   sound(q,0x2f);q.invoke('AudioUpdate');before=target_voices(q);q.put(Cv3Bat=2,Cv3Fresh=0x80 if kind=='manual-exit'else 0,SavedJoypadBits=4 if kind=='manual-exit'else 0,Cv3BatDrain=1,Player_X_Position=64,Player_Y_Position=128)
   if kind=='exhaust':q.set('Cv3Hearts',0,2)
   q.invoke('Cv3BatUpdate');assert q.get('Cv3Bat')==3 and q.get('AvAudioRequest')==0 and target_voices(q)==before
  else:
   q.put(Cv3Fresh=0x80,SavedJoypadBits=4,Cv3AttackAge=1 if kind=='busy'else 0);q.set('Cv3Hearts',10 if kind=='busy'else 0,2);q.invoke('Cv3BatUpdate');assert q.get('Cv3Bat')==q.get('AvAudioRequest')==q.get('Cv3FxOwned')==0
  bat.append(dict(mode=mode,kind=kind,passed=True))
 for typ,pending_request,full in itertools.product(range(1,7),[0,1,21,22,25],[0,1]):
  q=init(b);q.put(AvAudioRequest=pending_request)
  if full:q.array('Cv3ShotType',[1]*4)
  q.invoke('Cv3Spawn',a=typ)
  if pending_request or full:assert q.get('AvAudioRequest')==pending_request and q.get('Cv3FxOwned')==0
  else:assert q.get('AvAudioRequest')==26 if typ==6 else q.get('AvAudioRequest')==typ+26
  pool.append(dict(type=typ,ordinary_pending=pending_request,pool_full=full,passed=True))
 q=init(b);o=Original(CV3.read_bytes());o.call(0xe227);rng=random.Random(0xc03);mixed=[]
 for frame in range(512):
  requests=[]
  if frame==0 or rng.randrange(4)==0:
   for _ in range(1+rng.randrange(2)):
    event=rng.choice(list(EVENTS));sound(q,event);o.call(0xe25f,a=event);requests.append(event)
  wanted=source_voices(o);o.m.trace=[];o.call(0xe24e);q.invoke('AudioUpdate')
  for voice,reg in[(0,[0x4000,0x4001,0x4002,0x4003]),(1,[0x400c,0x400e,0x400f])]:
   if wanted[voice]:
    expected=sorted((r['address'],r['value'])for r in o.m.trace if r['address']in reg);actual=sorted((at,v)for at,v in apu(q)if at in reg);assert actual==expected,(frame,requests,voice,actual,expected)
  assert target_voices(q)==source_voices(o),(frame,requests,target_voices(q),source_voices(o));mixed.append(dict(frame=frame,requests=requests,source_voices=source_voices(o)))
 result=dict(passed=True,accepted=False,ROM_sha256=hashlib.sha256(a.rom.read_bytes()).hexdigest(),pending_controls=len(pending),bat_exit_no_retrigger_and_rejection_controls=len(bat),pool_and_ordinary_queue_controls=len(pool),strict_raw_continued_original_mixed_chain_updates=len(mixed),raw400F_included_without_mask=True,scope='Assembled source/owner components; explicitly seeded pending/scene and manual bat clearance actors. Actual menu uses vanilla audio and a genuine scene-reset/new-music chain is exercised before guest resume. No native cadence, controller campaign, bus or waveform acceptance.')
 for name,rows in [('pending',pending),('bat',bat),('pool',pool),('mixed',mixed)]: (a.output/(name+'.json')).write_text(json.dumps(rows,indent=2)+'\n')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
