"""Validate lifecycle oracle with actual assembled audio, including mute resume/mixed ownership."""
from pathlib import Path
import argparse,copy,hashlib,json
from check_tmnt_render_oa import load,address,location
from check_tmnt_audio_fallback_oc import qualified
from cv3_remaining_sfx_queue256_support_v1 import init,sound
from verify_native_relocation import NesMPU
from cv3_remaining_sfx_lifecycle_verify_v1 import composed_source

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run_audio(q,labels,epoch,base_cycle):
 b=q.b;name='AudioUpdate';pc=address(b,name);bank=(location(b,name)-16)//8192;window=(pc-0x8000)//8192;q.m.page(window,bank)
 if window in[1,2]:q.set('CurrentBank'if window==1 else'CurrentBankC',bank|128)
 c=NesMPU(memory=q.m,pc=pc);c.processorCycles=base_cycle;c.sp=253;c.stPushWord(0x5aff);q.m.writes=[];life=[];events=[];images=[];image_scope=None;tick_scope=None;mix_scope=None
 def row(kind,**kw):return dict(kind=kind,cpuCycle=c.processorCycles,audioEpoch=epoch,**kw)
 def ret():return(((q.m[0x100+c.sp+1]|q.m[0x100+c.sp+2]<<8)+1)&65535,(c.sp+2)&255)
 def at(n):
  proc,sep,leaf=n.partition('::');pc=labels[(proc,leaf)]if sep else address(b,n);bank=(location(b,proc)-16)//8192
  return c.pc==pc and q.m.banks[(pc-0x8000)//8192]==bank
 for _ in range(100000):
  if image_scope and(c.pc,c.sp)==image_scope:image_scope=None
  if tick_scope and(c.pc,c.sp)==tick_scope:life.append(row('source-tick-return'));tick_scope=None
  if mix_scope and(c.pc,c.sp)==mix_scope[0]:life.append(row('actual-mixer-flush',**mix_scope[1]));mix_scope=None
  if c.pc==0x5b00:assert c.sp==253;return life,events,images,c.processorCycles
  if at('Cv3FxMusicInit'):life.append(row('actual-music-init'))
  if at('Cv3FxDrain'):
   head,tail=q.get('Cv3FxQueueHead'),q.get('Cv3FxQueueTail');cues=[]
   while tail!=head:cues.append(q.get('Cv3FxQueue',tail));tail=(tail+1)&255
   events.append(row('drain-return',cues=cues)) # Read exact committed commands at atomic consumer entry; same order as return.
  if at('Cv3FxTick'):assert tick_scope is None;tick_scope=ret()
  if at('Cv3FxService::Decode')or at('Cv3FxResidentBody::Emit'):
   assert image_scope is None;image_scope=ret()
  if at('Cv3MusicAndNoiseTick::Continue')and q.get('Cv3NoiseActive')==1 and q.get('Cv3NoiseIndex')<28:
   assert image_scope is None;image_scope=ret()
  if at('GuestAudioNativeFlush')or at('GuestAudioFinish::MixedChannels'):
   assert mix_scope is None
   z=dict(owner='native'if at('GuestAudioNativeFlush')else'mixed',mask=q.get('GuestMixMask'),changed=q.get('GuestMixChanged'),hardware=[])
   for key,n in[('image','GuestNativeApu'),('last','GuestApuLast'),('dirty','GuestNativeDirty'),('fx','GuestFxApu'),('fxDirty','GuestFxDirty')]:z[key]=[q.get(n,i)for i in range(16)]
   mix_scope=(ret(),z)
  i=len(q.m.writes);c.step()
  for loc,v in q.m.writes[i:]:
   if image_scope and address(b,'GuestNativeApu')<=loc<address(b,'GuestNativeApu')+16:images.append(dict(audioEpoch=epoch,address=0x4000+loc-address(b,'GuestNativeApu'),value=v))
   if mix_scope and 0x4000<=loc<=0x400f:mix_scope[1]['hardware'].append([loc,v])
 raise AssertionError('Audio timeout')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);b=load(a.rom);labels=qualified(a.rom);cases=[];rejects=[]
 schedules={
  'axe-retrigger':{0:('sound',0x15),12:('sound',0x15)},
  'ice-to-lightning':{0:('sound',0x21),32:('sound',0x1e)},
  'pause-resume':{0:('sound',0x21),1:('pause',1),50:('pause',0)},
  'death-cancel':{0:('sound',0x2f),20:('death',0)},
  'scene-cancel':{0:('sound',0x2f),49:('scene',0)},
  'ordinary-noise-overlap':{0:('sound',0x15),6:('worldnoise',1)},
  'legacy-retrigger':{i:('sound',0x1f)for i in range(0,220,32)},
  'idle':{}}
 for name,schedule in schedules.items():
  q=init(b);life=[];events=[];images=[];cycle=100000
  for epoch in range(1,241 if name=='legacy-retrigger'else141):
   f=epoch-1
   if f in schedule:
    k,v=schedule[f]
    if k=='sound':sound(q,v)
    elif k=='pause':q.put(GamePauseStatus=v)
    elif k=='death':q.invoke('KillPlayer')
    elif k=='scene':q.invoke('Cv3NoiseSceneReset')
    else:q.put(NoiseSoundQueue=v)
   l,e,i,cycle=run_audio(q,labels,epoch,cycle+1000);life+=l;events+=e;images+=i
  oracle=composed_source(life,events,images,name=='legacy-retrigger')
  if name=='pause-resume':assert len([e for e in life if e['kind']=='actual-mixer-flush'])==91
  if name=='ordinary-noise-overlap':assert any(e['kind']=='actual-mixer-flush'and e['owner']=='mixed'and e['mask']&8 for e in life)
  dest=a.output/name;dest.mkdir();packet=dict(lifecycle=life,queue_events=events,source_images=images,oracle=oracle);(dest/'trace.json').write_text(json.dumps(packet,separators=(',',':'))+'\n');cases.append(dict(name=name,trace_sha256=sha(dest/'trace.json'),source_frames=oracle['original_frames'],mixer_flushes=len(oracle['complete_flushes'])))
  if name in['ice-to-lightning','pause-resume']:
   bad=copy.deepcopy(images);next(r for r in bad if r['address']==0x400f)['value']^=1
   try:composed_source(life,events,bad)
   except AssertionError:rejects.append(name+'-raw400F-corruption')
   else:raise AssertionError('Raw400F corruption accepted')
  if name=='pause-resume':
   bad=copy.deepcopy(life);resume=next(e for e in bad if e['kind']=='actual-mixer-flush'and e['audioEpoch']==51);assert resume['hardware'];resume['hardware'].pop()
   try:composed_source(bad,events,images)
   except AssertionError:rejects.append('missing-resume-hardware-store')
   else:raise AssertionError('Missing resume store accepted')
 result=dict(passed=True,native_executed=False,ROM_sha256=sha(a.rom),cases=cases,rejected_controls=rejects,original_ROM_sha256=sha(__import__('cv3_primary_sfx_source_v1').CV3),tool_sha256=sha(__file__),oracle_sha256=sha(Path(__file__).with_name('cv3_remaining_sfx_lifecycle_verify_v1.py')),scope='Actual assembled AudioUpdate and authentic effect producers, controlled source-component pause/death/scene/shared-noise schedules. Exact original source requests and all complete hardware mixer flushes incl restore/resume and raw400F. No native bus/controller/PPU/deadline verdict; natural controller/actor feasibility is separately bound.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
