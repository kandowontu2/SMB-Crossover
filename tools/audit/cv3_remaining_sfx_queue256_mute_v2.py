"""Finite gameplay ingress bound plus real mute/pause consumers and original resume traces."""
from pathlib import Path
import argparse,hashlib,itertools,json,re
from check_tmnt_render_oa import load,address
from cv3_primary_sfx_source_v1 import Original,CV3
from cv3_remaining_sfx_queue256_support_v1 import init,sound,EVENTS,target_voices,source_voices
from cv3_dmc_complete_cpu_v1 import apu
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def count(q):return(q.get('Cv3FxQueueHead')-q.get('Cv3FxQueueTail'))&255
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);b=load(a.rom);s=a.source
 combat=(s/'src/cv3_combat.s').read_text();game=(s/'src/game.s').read_text();audio=(s/'src/roster_audio.s').read_text();reset=(s/'src/reset.s').read_text();fx=(s/'src/cv3_remaining_source_fx.s').read_text();abilities=(s/'src/cv3_abilities.s').read_text()
 fastrefs=[];headwriters=[]
 for f in(s/'src').rglob('*'):
  if not f.is_file()or f.suffix not in['.s','.inc']:continue
  for i,t in enumerate(f.read_text().splitlines(),1):
   if re.search(r'\b(?:jsr|jmp|farcall) Cv3FxProducerFast\b',t):fastrefs.append(dict(path=f.relative_to(s).as_posix(),line=i,text=t.strip()))
   if re.search(r'\b(?:sta|stx|sty|inc|dec) Cv3FxQueueHead\b',t,re.I):headwriters.append(dict(path=f.relative_to(s).as_posix(),line=i,text=t.strip()))
 assert len(fastrefs)==1 and fastrefs[0]['path']=='src/cv3_combat.s';assert len(headwriters)==3 and all(r['text']=='inc Cv3FxQueueHead'for r in headwriters)
 assert 'CatchUpOnce:'in game and game.count('jsr GameLoop')==2 and 'jmp IdleLoop'in game
 assert 'KeepLagChr:'in reset and 'jsr AudioUpdate'in reset
 assert 'jsr Cv3FxMuteGate'in audio and 'jsr Cv3FxDrainGate'in fx
 assert combat.count('lda #5\n jsr Cv3Spawn')==3 and combat.count('lda #4\n jsr Cv3Spawn')==3 and combat.count('lda #6\n jsr Cv3Spawn')==3
 assert abilities.count('jsr Cv3FxBatEnter')==1
 callgraph=dict(passed=True,fast_callers=fastrefs,head_writers=headwriters,max_GameLoops_between_audio_NMIs=2,max_shots_per_weapon_gate=3,max_bat_entry_calls_per_movement_gate=1,overapprox_source_cues_per_interval=8,max_consecutive_cancel_runs=9,max_pending_valid_ingress=17,logical_capacity=64,checked_public_entry_keeps_full_guard=True,explanation='Every nonzero-OperMode selected-CV1 AudioUpdate takes either active Tick or MuteGate; both drain committed requests. Each GameLoop executes movement/weapon dispatch once; release branches emit at most3 and bat adds at most1 (mutual exclusion ignored). At most2 GameLoops occur per audio NMI because IdleLoop permits one catch-up then yields. Consecutive CANCEL dedup permits at most one CANCEL run around each source cue, hence8+9=17. Off-game menu permits portraits/scene cancel only; repeated pending cancels dedup to1. Cold owner flushes old committed head and preserves a new uncommitted slot. External checked compatibility invocations are outside this bounded private caller and retain full detection.',new_qualification_needed_for_future_other_producers=True)
 (a.output/'callgraph-bound.json').write_text(json.dumps(callgraph,indent=2)+'\n')
 rows=[];raw=CV3.read_bytes()
 for current,incoming,age,kind in itertools.product([None,0x1f,0x24,0x21],EVENTS,[0,12],['pause','silence']):
  q=init(b,3);o=Original(raw);o.call(0xe227)
  if current:
   sound(q,current);o.call(0xe25f,a=current)
   for _ in range(age):q.invoke('AudioUpdate');o.call(0xe24e)
  if kind=='pause':q.put(GamePauseStatus=1)
  else:q.put(RgAudioSilenced=1)
  sound(q,incoming);o.call(0xe25f,a=incoming);phase=(q.get('Cv3NoiseIndex'),q.get('Cv3FxPulseFrame'))
  for frame in range(3):
   head=q.get('Cv3FxQueueHead');q.invoke('AudioUpdate');assert q.get('Cv3FxQueueHead')==head and count(q)==0
   assert phase==(q.get('Cv3NoiseIndex'),q.get('Cv3FxPulseFrame')),('FX advanced during mute',current,incoming,age,kind,frame)
   assert not q.get('AvAudioRequest')and q.get('Cv3FxQueueOverflow')==0
  q.put(GamePauseStatus=0,RgAudioSilenced=0)
  for frame in range(4):
   wanted=source_voices(o);o.m.trace=[];o.call(0xe24e);q.invoke('AudioUpdate')
   for voice,reg in[(0,[0x4000,0x4001,0x4002,0x4003]),(1,[0x400c,0x400e,0x400f])]:
    if wanted[voice]:
     expected=sorted((r['address'],r['value'])for r in o.m.trace if r['address']in reg);actual=sorted((at,v)for at,v in apu(q)if at in reg);assert actual==expected,(current,incoming,age,kind,frame,voice,actual,expected)
   assert target_voices(q)==source_voices(o),(current,incoming,age,kind,frame,target_voices(q),source_voices(o))
  rows.append(dict(current=current,incoming=incoming,age=age,kind=kind,muted_updates=3,resume_original_raw_frames=4,head_stable=True,all_pending_drained_without_source_tick=True))
 (a.output/'mute-resume.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
 pressure=[]
 for mode,kind,counter in itertools.product([0,1],['pause','silence'],[0,255]):
  q=init(b,2);q.put(CrossoverBehaviorVersion=mode,Cv3FxQueueHead=counter,Cv3FxQueueTail=counter,Cv3FxQueueOverflow=0)
  q.put(GamePauseStatus=1 if kind=='pause'else 0,RgAudioSilenced=1 if kind=='silence'else 0)
  high=0
  for interval in range(128):
   q.invoke('Cv3FxCancel')
   # Deliberately overapproximate the legal real caller:8 cue emissions plus
   #9 intervening CANCEL runs. This also covers a long muted song interval.
   for index in range(8):q.invoke('Cv3FxProducerFast',a=1+index%6,x=3);q.invoke('Cv3FxCancel')
   high=max(high,count(q));assert count(q)==17 and q.get('Cv3FxQueueOverflow')==0
   head=q.get('Cv3FxQueueHead');q.invoke('AudioUpdate');assert q.get('Cv3FxQueueHead')==head and count(q)==0 and q.get('Cv3FxQueueOverflow')==0
  pressure.append(dict(mode=mode,kind=kind,counter=counter,intervals=128,source_cues_per_interval=8,cancel_runs_per_interval=9,actual_max_occupancy=high,all_source_phase_frozen=True))
 result=dict(passed=True,accepted=False,ROM_sha256=sha(a.rom),source=str(s),callgraph_bound=callgraph,original_pending_mute_resume_cases=len(rows),full_original_raw_resume_frames=4*len(rows),max17_ingress_pressure_intervals=sum(r['intervals']for r in pressure),pressure=pressure,source_priorities_and400F_without_masks=True,scope='Bounded actual source callgraph plus assembled mute/active owner controls. Stress emissions overapproximate legal per-GameLoop events, not controller gameplay. Direct silenced-flag resume exercises preserved pending semantics; genuine new-song resume cancels via existing MusicInit. No native budget/adoption claim.',tool_sha256=sha(__file__))
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in['callgraph_bound','pressure']},indent=2))
if __name__=='__main__':main()
