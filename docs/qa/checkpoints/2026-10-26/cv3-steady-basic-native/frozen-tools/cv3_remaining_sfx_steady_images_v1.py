"""Original ordered voice images plus exact private cache ownership on steady successor."""
from pathlib import Path
import argparse,hashlib,itertools,json,re
from check_tmnt_render_oa import load,address,Memory
from check_tmnt_audio_fallback_oc import qualified
from cv3_remaining_sfx_queue256_support_v1 import init,sound,EVENTS,source_voices,target_voices
from cv3_remaining_sfx_steady_mute_v1 import detailed
from cv3_primary_sfx_source_v1 import Original,CV3
from cv3_dmc_complete_cpu_v1 import apu,regs
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
class Watch(Memory):
 def __getitem__(self,at):
  if getattr(self,'watching',False)and isinstance(at,int)and at==self.target:self.reads.append(at)
  return super().__getitem__(at)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);b=load(a.rom);labels=qualified(a.rom);rows=[]
 for event,mode in itertools.product([0x13,0x15,0x24,0x21,0x1e,0x2f],[0,1]):
  q=init(b,2 if event in[0x24,0x21,0x1e]else 3);q.put(CrossoverBehaviorVersion=mode);sound(q,event);o=Original(CV3.read_bytes());o.call(0xe227);o.call(0xe25f,a=event)
  for frame in range(100):
   voices=source_voices(o);o.m.trace=[];o.call(0xe24e);image,hardware=detailed(q,labels)
   for own,regs0 in[(voices[0],[0x4000,0x4001,0x4002,0x4003]),(voices[1],[0x400c,0x400e,0x400f])]:
    if own:assert[(at,v)for at,v in image if at in regs0]==[(r['address'],r['value'])for r in o.m.trace if r['address']in regs0],('Ordered source voice image',event,mode,frame,image,o.m.trace)
   assert target_voices(q)==source_voices(o)
  rows.append(dict(event=event,mode=mode,whole_updates=100,original_ordered_voice_images_exact=True,complete_composed_hardware_exact=True))
 (a.output/'ordered-images.json').write_text(json.dumps(rows,indent=2)+'\n')
 # Enumerate all direct aliases of the selected-family slab; only this file
 # references offset52. Imported CV1 wrapper borrows exactly24, all other shared
 # families are mutually exclusive and cold-reset. No unbounded indirect claim.
 mentions=[];direct=[]
 for f in(a.source/'src').rglob('*'):
  if not f.is_file()or f.suffix not in['.s','.inc']:continue
  for line,t in enumerate(f.read_text().splitlines(),1):
   if 'Cv3FxSavedA'in t:direct.append(dict(path=f.relative_to(a.source).as_posix(),line=line,text=t.strip()))
   if 'RgAudioZp'in t:mentions.append(dict(path=f.relative_to(a.source).as_posix(),line=line,text=t.strip(),sha256=sha(f)))
 assert len(direct)==6 and all(r['path']=='src/cv3_remaining_source_fx.s'for r in direct),direct
 fx=(a.source/'src/cv3_remaining_source_fx.s').read_text();dispatch=fx[fx.index('.proc Cv3FxResidentDispatch'):fx.index('.proc Cv3FxResidentNoise')];assert dispatch.index('sta Cv3FxSavedA')<dispatch.index('Generic:')<dispatch.index('lda Cv3FxSavedA')
 assert fx.count('ldy Cv3FxSavedA')==1 and fx.index('sty Cv3FxSavedA')<fx.index('ldy Cv3FxSavedA')
 driver=a.source/'src/audio/roster/castlevania.inc';assert 'RgAudioZp'not in driver.read_text();roster=(a.source/'src/roster_audio.s').read_text();assert '.if Kind=2\n  ZpCount=24'in roster
 scans=[]
 for area,event in[(1<<i,0)for i in range(7)]+[(0,1<<i)for i in range(7)]+[(128,0),(0,128)]:
  qs=[init(b,2)for _ in range(2)]
  for seed,q in enumerate(qs):
   m=Watch(b);list.__setitem__(m,slice(None),list(q.m));m.banks=list(q.m.banks);m.target=address(b,'Cv3FxSavedA');m.reads=[];m.watching=False;q.m=m;q.set('Cv3FxSavedA',seed*181+37);q.put(GuestAudioCharacter=255,RgAudioCharacter=255,AreaMusicQueue=area,EventMusicQueue=event)
  for frame in range(256):
   cs=[]
   for q in qs:
    q.m.reads=[];q.m.watching=True;c,_=q.invoke('AudioUpdate');q.m.watching=False;cs.append(c);assert not q.m.reads,('Ordinary source music reads dead52',area,event,frame,q.m.reads);q.put(AreaMusicQueue=0,EventMusicQueue=0)
   assert apu(qs[0])==apu(qs[1])and regs(cs[0])==regs(cs[1])and qs[0].m.banks==qs[1].m.banks
  scans.append(dict(area=area,event=event,updates=512,actual_dead52_reads=0,hardware_AXYP_banks_independent=True))
 r=dict(passed=True,accepted=False,native_executed=False,ROM_sha256=sha(a.rom),original_ROM_sha256=sha(CV3),original_ordered_source_whole_updates=1200,full_composed_hardware_whole_updates=1200,source_register_400F_never_masked=True,legacy1F_contract='Unchanged adapter buffered order and complete baseline hardware; separate CPU/native regression controls. This original ordered-image claim excludes1F.',direct_saved52_references=direct,all_slab_mentions=mentions,actual_ordinary_music_dead52_profiles=scans,actual_ordinary_music_updates=8192,source_scope='Saved52 reads are dominated by their own Generic bank-cache write or steady savedY write. No imported direct slab reference; selectedKind2 borrows only24 bytes. Actual complete music menus under two52 values never read it. This bounded runtime indirect-read coverage is not an unbounded claim about every future song phase.',tool_sha256=sha(__file__))
 (a.output/'proof.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items()if k not in['all_slab_mentions','actual_ordinary_music_dead52_profiles']},indent=2))
if __name__=='__main__':main()
