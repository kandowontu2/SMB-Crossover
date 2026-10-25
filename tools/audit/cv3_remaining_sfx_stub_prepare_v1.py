"""Private authentic source-frame native stubs, no new banks/RAM or source ticks."""
from pathlib import Path
import argparse,collections,csv,difflib,hashlib,json,shutil,subprocess,sys
from check_tmnt_render_oa import load,address
from check_tmnt_audio_fallback_oc import qualified
from cv3_primary_sfx_source_v1 import Original,CV3,CV3_SHA
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE=D/'cv3-remaining-decoder-v1/qualified-v1'
GOLD=D/'cv3-remaining-sfx-v1/source-v2'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
WRITERS="""
; Native frame packets keep original C/F/E or pulse source image-store order.
; Only a currently owned frame dispatches here; outer Cv3FxTick preserves AXY/P.
; Existing R0/R1 borrow is restored by Cv3FxService on every return.
.proc Cv3FxFrameNoiseFull
 sta GuestNativeApu+12
 sta Cv3NoiseApu
 lda #1
 sta GuestNativeDirty+12
 lda Cv3FxSourceHigh
 ora #8
 sta GuestNativeApu+15
 sta Cv3NoiseApu+3
 lda #1
 sta GuestNativeDirty+15
 txa
 sta GuestNativeApu+14
 sta Cv3NoiseApu+2
 lda #1
 sta GuestNativeDirty+14
 ldy #7
 jmp Cv3FxFrameAdvance
.endproc
.proc Cv3FxFrameNoiseVolume
 sta GuestNativeApu+12
 sta Cv3NoiseApu
 lda #1
 sta GuestNativeDirty+12
 ldy #5
 jmp Cv3FxFrameAdvance
.endproc
.proc Cv3FxFrameQuiet
 ldy #3
 jmp Cv3FxFrameAdvance
.endproc
.proc Cv3FxFramePulseFull
 sta GuestNativeApu
 sta Cv3FxPulseApu
 lda #1
 sta GuestNativeDirty
 tya
 sta GuestNativeApu+3
 sta Cv3FxPulseApu+3
 and #7
 sta Cv3FxSourceHigh
 lda #1
 sta GuestNativeDirty+3
 txa
 sta GuestNativeApu+2
 sta Cv3FxPulseApu+2
 lda #1
 sta GuestNativeDirty+2
 ldy #9
 jmp Cv3FxFrameAdvance
.endproc
.proc Cv3FxFramePulseVolumePeriod
 sta GuestNativeApu
 sta Cv3FxPulseApu
 lda #1
 sta GuestNativeDirty
 txa
 sta GuestNativeApu+2
 sta Cv3FxPulseApu+2
 lda #1
 sta GuestNativeDirty+2
 ldy #7
 jmp Cv3FxFrameAdvance
.endproc
.proc Cv3FxFramePulseVolumeSweep
 sta GuestNativeApu
 sta Cv3FxPulseApu
 lda #1
 sta GuestNativeDirty
 lda #127
 sta GuestNativeApu+1
 sta Cv3FxPulseApu+1
 lda #1
 sta GuestNativeDirty+1
 ldy #5
 jmp Cv3FxFrameAdvance
.endproc
.proc Cv3FxFramePulseSweepFull
 pha
 lda #127
 sta GuestNativeApu+1
 sta Cv3FxPulseApu+1
 lda #1
 sta GuestNativeDirty+1
 pla
 jmp Cv3FxFramePulseFull
.endproc
.proc Cv3FxFramePulseSweepVolumePeriod
 pha
 lda #127
 sta GuestNativeApu+1
 sta Cv3FxPulseApu+1
 lda #1
 sta GuestNativeDirty+1
 pla
 jmp Cv3FxFramePulseVolumePeriod
.endproc
.proc Cv3FxFrameAdvance
 tya
 clc
 adc R0
 sta R0
 bcc Done
 inc R1
Done:rts
.endproc
"""
STREAMS=[(0x1f,'Noise'),(0x13,'Noise'),(0x15,'Noise'),(0x24,'Noise'),(0x24,'Pulse'),(0x21,'Noise'),(0x21,'Pulse'),(0x2f,'Noise'),(0x2f,'Pulse')]
def produce(original):
 assert sha(CV3)==CV3_SHA
 auth=json.loads((GOLD/'proof.json').read_text());captures={r['id']:r for r in auth['captures']};events={}
 for event in sorted({e for e,v in STREAMS}):
  f=GOLD/f'event-{event:02x}-apu.csv';assert sha(f)==captures[event]['trace_sha256'];rows=[{k:int(v)for k,v in r.items()}for r in csv.DictReader(f.open())]
  o=Original(CV3.read_bytes());o.call(0xe227);o.m.trace=[];o.m.frame=0;o.call(0xe25f,a=event)
  for frame in range(180):o.m.frame=frame;o.call(0xe24e)
  assert[[r[k]for k in['frame','pc','bank','address','value']]for r in rows]==[[r[k]for k in['frame','pc','bank','address','value']]for r in o.m.trace]
  events[event]=rows
 code='';records=[];plans=[];legacy=[];total=0
 for event,voice in STREAMS:
  rows=[r for r in events[event]if(r['address']<0x4004)==(voice=='Pulse')];last=max(r['frame']for r in rows);frames=collections.defaultdict(list)
  for r in rows:frames[r['frame']].append((r['address']-0x4000,r['value']))
  label=f'Cv3Fx{event:02X}{voice}';code+=label+':\n';old_offset=offset=0;patterns=collections.Counter()
  for frame in range(last+1):
   writes=frames[frame];pattern=tuple(r for r,v in writes);values=dict(writes);patterns[str(pattern)]+=1;name=label+f'Frame{frame:03d}';body=''
   if not writes:writer='Cv3FxFrameQuiet';size=3
   elif voice=='Noise':
    assert pattern in[(12,15,14),(12,)]
    body+=f' lda #{values[12]}\n';writer='Cv3FxFrameNoiseVolume';size=5
    if len(writes)==3:body+=f' ldx #{values[14]}\n';writer='Cv3FxFrameNoiseFull';size=7
   else:
    assert all(v==127 for r,v in writes if r==1)
    assert pattern in[(1,0,3,2),(0,3,2),(0,2),(0,1),(1,0,2)]
    body+=f' lda #{values[0]}\n';size=5
    if 2 in values:body+=f' ldx #{values[2]}\n';size+=2
    if 3 in values:body+=f' ldy #{values[3]}\n';size+=2
    writer={(1,0,3,2):'Cv3FxFramePulseSweepFull',(0,3,2):'Cv3FxFramePulseFull',(0,2):'Cv3FxFramePulseVolumePeriod',(0,1):'Cv3FxFramePulseVolumeSweep',(1,0,2):'Cv3FxFramePulseSweepVolumePeriod'}[pattern]
   code+=name+':\n'+body+' jmp '+writer+'\n';records.append(dict(stream=label,voice=voice,event=event,frame=frame,new_label=name,old_PC=address(original,label)+old_offset,stub_bytes=size,original_ordered_writes=writes))
   if(event,voice)==(0x1f,'Noise'):legacy.append(offset)
   old_offset+=len(writes)*2+1;offset+=size
  end=label+'End';code+=end+': .byte $ff\n';records.append(dict(stream=label,voice=voice,event=event,frame=last+1,new_label=end,old_PC=address(original,label)+old_offset,end=True))
  if(event,voice)==(0x1f,'Noise'):legacy.append(offset)
  plans.append(dict(event=event,voice=voice,frames=last+1,stub_bytes=offset+1,patterns=dict(patterns)));total+=offset+1
 assert total==1458 and max(legacy)<256
 code+='Cv3FxNoiseLo:.byte <Cv3Fx1FNoise,<Cv3Fx13Noise,<Cv3Fx15Noise,<Cv3Fx24Noise,<Cv3Fx21Noise,<Cv3Fx21Noise,<Cv3Fx2FNoise\nCv3FxNoiseHi:.byte >Cv3Fx1FNoise,>Cv3Fx13Noise,>Cv3Fx15Noise,>Cv3Fx24Noise,>Cv3Fx21Noise,>Cv3Fx21Noise,>Cv3Fx2FNoise\nCv3FxPulseLo:.byte 0,0,0,<Cv3Fx24Pulse,<Cv3Fx21Pulse,<Cv3Fx21Pulse,<Cv3Fx2FPulse\nCv3FxPulseHi:.byte 0,0,0,>Cv3Fx24Pulse,>Cv3Fx21Pulse,>Cv3Fx21Pulse,>Cv3Fx2FPulse\nCv3FxLegacyOffsets:.byte '+','.join(map(str,legacy))+'\n'
 return WRITERS+code,records,plans,captures

def main():
 pa=argparse.ArgumentParser(description=__doc__);pa.add_argument('--output',type=Path,required=True);a=pa.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False);assert sha(BASE/'candidate.nes')=='5ad6abfe3dc2fb279b7ab5e29954f2f1bd32f56fe4517d8513a34ef3282e54c1';old=load(BASE/'candidate.nes');body,records,plans,captures=produce(old)
 stage=out/'source';shutil.copytree(BASE/'source-final',stage);f=stage/'src/cv3_remaining_source_fx.s';before=f.read_bytes();assert sha(f)=='bbafa47e1a1175806ae1da636960f596e7baadcc45980058a78efe704d34a826';s=before.decode();start=s.index('Decode:ldy #0');end=s.index('Read:jsr Peek',start);s=s[:start]+'Decode:jmp (R0) ; every target is a genuine mappedA82 source-frame stub\n'+s[end:];start=s.index('Cv3Fx1FNoise:.byte');end=s.index('.assert *<=$c000',start);s=s[:start]+body+s[end:];f.write_bytes(s.encode());assert produce(old)[0]==body
 frozen=out/'producer';frozen.mkdir();shutil.copyfile(__file__,frozen/Path(__file__).name);(frozen/'inputs.json').write_text(json.dumps(dict(original_ROM_sha256=CV3_SHA,source_goldens={str(k):v['trace_sha256']for k,v in captures.items()},parent_ROM_sha256=sha(BASE/'candidate.nes'),parent_source_sha256=hashlib.sha256(before).hexdigest(),produced_source_sha256=sha(f),producer_sha256=sha(__file__)),indent=2)+'\n')
 cmd=[sys.executable,str(stage/'tools/build_mmc5_expanded.py'),'--workspace',str(stage),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/'candidate.nes')]
 with(out/'build.log').open('w')as log:r=subprocess.run(cmd,cwd=stage,stdout=log,stderr=subprocess.STDOUT)
 assert not r.returncode,(out/'build.log').read_text()[-6000:];new=load(out/'candidate.nes');mapping=[]
 for rec in records:rec['new_PC']=address(new,rec['new_label']);mapping.append(rec)
 assert len({r['old_PC']for r in mapping})==len(mapping)and len({r['new_PC']for r in mapping})==len(mapping)
 for n in range(128):
  oldbank=old['raw'][16+n*8192:16+(n+1)*8192];newbank=new['raw'][16+n*8192:16+(n+1)*8192]
  assert n==82 or oldbank==newbank
 assert old['raw'][:16]==new['raw'][:16]and old['raw'][1048592:]==new['raw'][1048592:]
 for ext in['nes','dbg','lbl','map']:shutil.copyfile(D/'cv3-remaining-decoder-v1'/('baseline.'+ext),out/('baseline.'+ext))
 q0,q1=qualified(out/'baseline.nes'),qualified(out/'candidate.nes');delta={k:(v,q1.get(k))for k,v in q0.items()if q1.get(k)!=v};assert delta=={('Cv3SpawnAudioType','Done'):(0xb3eb,None),('_FARCALL_COUNT',):(q0[('_FARCALL_COUNT',)],q0[('_FARCALL_COUNT',)]+1)},delta
 seg=next(v for v in new['segs'].values()if v['name'].strip('"')=='CV3_GRIP');size=int(seg['size'],0);end=int(seg['start'],0)+size;assert end<=0xc000
 (out/'pointer-translation.json').write_text(json.dumps(mapping,indent=2)+'\n');(out/'source-frame-plan.json').write_text(json.dumps(plans,indent=2)+'\n');(out/'implementation-increment.patch').write_text(''.join(difflib.unified_diff(before.decode().splitlines(True),s.splitlines(True),fromfile='a/src/cv3_remaining_source_fx.s',tofile='b/src/cv3_remaining_source_fx.s')),newline='\n')
 result=dict(passed=True,accepted=False,status='SOURCE_NATIVE_STUBS_COMPILED_CPU_NATIVE_PENDING',ROM_sha256=sha(out/'candidate.nes'),baseline_ROM_sha256=sha(out/'baseline.nes'),held_parent_ROM_sha256=sha(BASE/'candidate.nes'),source_file_sha256=sha(f),original_source_pinned_and_fresh_executed=True,deterministic_producer=True,producer_sha256=sha(__file__),frame_stub_bytes=1458,frame_boundary_translations=len(mapping),CV3_GRIP_bank=82,CV3_GRIP_end=end,CV3_GRIP_free=0xc000-end,only82_changes_from_held=True,new_RAM_CHR_bytes=0,all_adopted50b_ABI_exact_except_old_Done_FARCALL=True,stream_pointer_translation_sha256=sha(out/'pointer-translation.json'),scope='Native-code frame compilation only, not new worker/native acceptance. Every source write/tick/priority/raw400F/lifecycle/IRQ/ABI and ordinary/DMC control requires fresh CPU qualification before any native grant.')
 (out/'composition.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
