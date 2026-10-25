"""Source executable lifecycle and exact per-voice storage/owner feasibility."""
from pathlib import Path
import argparse, csv, hashlib, itertools, json, shutil
from cv3_primary_sfx_source_v1 import Original, CV3, CV3_SHA
from cv3_remaining_sfx_noise_cpu_v1 import init, sound
from cv3_dmc_complete_cpu_v1 import apu
from check_tmnt_render_oa import load, address, location
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--golden',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False);assert sha(CV3)==CV3_SHA
 old,new=[load(a.prepared/(n+'.nes'))for n in['baseline','candidate']];gold=json.loads((a.golden/'proof.json').read_text());raw=CV3.read_bytes();streams=[];controls=[]
 for event in[0x13,0x14,0x15,0x24,0x21,0x1e,0x2f,0x1f]:
  f=a.golden/f'event-{event:02x}-apu.csv';assert sha(f)==next(r['trace_sha256']for r in gold['captures']if r['id']==event);rows=list(csv.DictReader(f.open()))
  for voice,regs in [('pulse',[0x4000,0x4001,0x4002,0x4003]),('noise',[0x400c,0x400e,0x400f])]:
   writes=[(int(r['frame']),int(r['address']),int(r['value']))for r in rows if int(r['address'])in regs]
   if not writes:continue
   last=max(r[0]for r in writes);encoded=[]
   for frame in range(last+1):
    for fr,at,val in writes:
     if fr==frame:encoded +=[at-0x4000,val]
    encoded.append(254)
   encoded.append(255);file=out/f'event-{event:02x}-{voice}.bin';file.write_bytes(bytes(encoded))
   decoded=[];frame=0;i=0
   while encoded[i]!=255:
    if encoded[i]==254:frame+=1;i+=1;continue
    decoded.append((frame,0x4000+encoded[i],encoded[i+1]));i+=2
   assert decoded==writes
   active=next(r['source_voice_active_frames'][voice]for r in gold['captures']if r['id']==event)
   streams.append(dict(source_id=event,voice=voice,bytes=len(encoded),sha256=sha(file),last_APU_frame=last,priority_last_active_frame=max(active)if active else None,priority_clears_on_frame=last,ordered_source_APU_roundtrip_exact=True))
 # Source source-ID priority is independent for the two effect voices.
 # Music init intentionally clears ordinary effects; selected requested cues
 # are not the original1UP exception. Pause is a distinct requested voice.
 for current,age,request in itertools.product([0x13,0x15,0x24,0x21,0x1e,0x2f,0x1f],[0,1,5],[0x06,0x4d,0x4e,0x4f]):
  o=Original(raw);o.call(0xe227);o.call(0xe25f,a=current)
  for _ in range(age):o.call(0xe24e)
  before=[o.m[0x107+i]for i in range(7)];o.m.trace=[];o.call(0xe25f,a=request);after=[o.m[0x107+i]for i in range(7)]
  if request in[0x4e,0x4f]:assert after[3]==after[6]==0
  if request==0x06:
   # Source6 requests both effect voices. Lower priority must leave each
   # already active higher voice; an idle voice can independently accept6.
   assert all(after[i]==(6 if before[i]<=6 else before[i])for i in[3,6])
  controls.append(dict(current_source_id=current,age=age,request=request,source_instruments_before=before,source_instruments_after=after,launch_APU=o.m.trace))
 lifecycle=[]
 for event,variant,mode in itertools.product([0x13,0x15,0x1f],[1,3],[0,1]):
  #1F onGrant is a source-lane control; actualGrant primary remains DMC72.
  q=init(new,variant);q.put(CrossoverBehaviorVersion=mode);sound(q,event);q.invoke('AudioUpdate');before=dict(active=q.get('Cv3NoiseActive'),index=q.get('Cv3NoiseIndex'),cue=q.get('Cv3NoiseCue'))
  q.invoke('KillPlayer');dead=dict(active=q.get('Cv3NoiseActive'),index=q.get('Cv3NoiseIndex'),cue=q.get('Cv3NoiseCue'),flag=q.get('MmDeathFlag'),subroutine=q.get('GameEngineSubroutine'),event=q.get('EventMusicQueue'));assert dead['flag']==1 and dead['subroutine']==11
  q.invoke('AudioUpdate');muted=dict(active=q.get('Cv3NoiseActive'),index=q.get('Cv3NoiseIndex'),cue=q.get('Cv3NoiseCue'));assert muted==before
  # Explicitly stage the delayed real death-song request at the music owner;
  # this is an assembled cold-owner test, not a measured native delay.
  q.put(EventMusicQueue=1);q.invoke('AudioUpdate');resumed=dict(active=q.get('Cv3NoiseActive'),index=q.get('Cv3NoiseIndex'),cue=q.get('Cv3NoiseCue'),APU=apu(q));assert resumed['active']==1 and resumed['index']==before['index']+1
  lifecycle.append(dict(event=event,variant=variant,mode=mode,before=before,after_actual_KillPlayer=dead,after_silence_update=muted,after_staged_real_death_music_request=resumed,source_lifecycle_difference_observed=True))
 # Confirm this lifecycle gap predates new cues in adopted4c70 existing1F.
 q=init(old,3);sound(q,0x1f);q.invoke('AudioUpdate');q.invoke('KillPlayer');q.invoke('AudioUpdate');q.put(EventMusicQueue=1);q.invoke('AudioUpdate');assert q.get('Cv3NoiseActive')==1 and q.get('Cv3NoiseIndex')==2
 gaps=dict(existing4c70_1F_same_death_resume_observed=True,proposal13_15_lifecycle_not_complete=True,actual_death_cases=lifecycle,scope='Assembled actual KillPlayer call chain; explicitly staged delayed music request. No native physical delay, audible artifact or playthrough claim.')
 segs={v['name'].strip('"'):v for v in new['segs'].values()};storage=[]
 for name,limit in [('CV_AUDIO',0xdc00),('CV3_GRIP',0xc000),('X5_AUDIO_MIX',0xc000)]:
  s=segs[name];start=int(s['start'],0);size=int(s['size'],0);pos=int(s['ooffs'],0);end=start+size;free=limit-end;bank=(pos-16)//8192;assert free>=0;storage.append(dict(segment=name,bank=bank,linked_begin=start,linked_end_exclusive=end,available_end_exclusive=limit,free_bytes=free,free_bytes_sha256=digest(new['raw'][pos+size:pos+size+free])))
 # Full multi-voice plan shares actual identical21/1E byte streams but retains
 # distinct request/priority IDs; cross14 has no companion owner and is omitted.
 selected=[r for r in streams if r['source_id']not in[0x14,0x1e]];total=sum(r['bytes']for r in selected);assert total==1072
 assert all(next(x for x in streams if x['source_id']==0x21 and x['voice']==voice)['sha256']==next(x for x in streams if x['source_id']==0x1e and x['voice']==voice)['sha256']for voice in['pulse','noise'])
 available=next(r['free_bytes']for r in storage if r['segment']=='CV3_GRIP');metadata=60;assert available>total+metadata
 ownerrefs=[]
 for name,entry,kind in [('dagger','Cv3SpawnSub','sub1 Grant/Alucard'),('axe','Cv3SpawnSub','sub2 Grant/Alucard'),('flame','Cv3SpawnSub','sub1 Sypha'),('ice','Cv3SpawnSub','sub2 Sypha three actors'),('lightning','Cv3SpawnSub','sub3 Sypha three actors'),('bat-enter','Cv3BatUpdate','Down+A activation only'),('baseSimon-cross','AvSimonRelease','existing CV1 typed5 retained')]:ownerrefs.append(dict(event=name,entry=entry,address=address(new,entry),bank=(location(new,entry)-16)//8192,scope=kind))
 # Audit explicit source uses; new offsets belong to the selected-family slab,
 # not globally unused RAM. Gradius has an independent selected-family image.
 slabrefs=[]
 for f in sorted((a.prepared/'source/src').glob('*.s')):
  for lineno,line in enumerate(f.read_text().splitlines(),1):
   if any(n in line for n in['RgAudioZp','RgAudioCpuZp','Cv3Noise','Cv3Dmc']):slabrefs.append(dict(path=f.name,line=lineno,text=line.strip()))
 (out/'slab-and-audio-references.json').write_text(json.dumps(slabrefs,indent=2)+'\n');(out/'original-music-pause-controls.json').write_text(json.dumps(controls,indent=2)+'\n');(out/'target-death-lifecycle-gap.json').write_text(json.dumps(gaps,indent=2)+'\n')
 result=dict(passed=True,accepted=False,source_ROM_sha256=CV3_SHA,target_baseline_sha256=sha(a.prepared/'baseline.nes'),private_proposal_sha256=sha(a.prepared/'candidate.nes'),source_receipt_sha256=sha(a.golden/'proof.json'),per_voice_streams=streams,source_music_pause_controls=len(controls),lifecycle_gap_receipt_sha256=sha(out/'target-death-lifecycle-gap.json'),linked_storage=storage,full_multi_voice_plan=dict(feasible_storage_only=True,implementation_complete=False,data_bytes=total,metadata_reserved_bytes=metadata,code_budget_after_data_metadata=available-total-metadata,bank=82,stream_priority_ids=[0x13,0x15,0x1f,0x24,0x21,0x1e,0x2f],shared_exact_data_ids=[0x21,0x1e],cross14_omitted_reason='No CV3 companion cross owner. BaseSimon retains existing original-family CV1 cross.',state_offsets=dict(NoiseID=36,PulseID=37,OwnedMask=38,PulseFrame=39,PulseImage=[40,44],PulseMusicCache=[44,48],NoisePointer=[48,50],PulsePointer=[50,52],SavedA=52),new_allocated_RAM=0,ownership='Selected CV3 family only. Existing CV1 offsets0..23, noise24..31 and DMC32..35 retained. Reinitialize each newly borrowed field on character/newscene; pause holds voice phase.',cold_service='Bank28 C-window bracket maps A82 using its private SavedA and exact CurrentBank/5115 restore; no shared five-SMC farcall during audio. Code bytes/IRQ/cycles are not yet implemented or qualified.',dirty_policy='Cache CV1 native music writes separately; suppress only currently owned voice registers. Decode only exact source writes, never mark4003 dirty merely because pulse is owned. Restore each voice separately on its genuine final source frame.',priority_policy='Original independent per-voice source IDs; incoming>=active admits, equal retriggers. Voice priority clears on original final-silence frame even if mixer image restoration happens nextupdate.',lifecycle='Cold universal guest-death/new-music bridge must cancel pending/owned private effects, preserving scene/pause and unrelated DMC owners. Existing1F gap explicitly retained. No invented bat-exit cue.',performance='Require zero new ordinary idle overhead; measure full active original1F and new multi-voice costs, then strict paired native pressure. No performance or waveform acceptance from capacity arithmetic.'),actual_ability_entries=ownerrefs,tool_sha256=sha(__file__),scope='Pinned original executable/source and target CPU feasibility only. Private noise candidate remains unadopted with explicit lifecycle/native/cadence gaps. Multi-voice implementation is a placement/state/hook plan, not completed gameplay.')
 (out/'proof.json').write_text(json.dumps(result,indent=2)+'\n');shutil.copyfile(Path(__file__),out/Path(__file__).name);print(json.dumps(dict(passed=True,stream_bytes=total,code_budget=available-total-metadata,original_lifecycle_controls=len(controls),target_death_gap_cases=len(lifecycle),proof_sha256=sha(out/'proof.json')),indent=2))
if __name__=='__main__':main()
