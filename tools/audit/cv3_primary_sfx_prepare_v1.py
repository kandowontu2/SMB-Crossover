"""Private source-only Alucard original noise-SFX integration, frozen inputs."""
from pathlib import Path
import argparse,csv,difflib,hashlib,json,shutil,subprocess,sys
from check_tmnt_render_oa import load,address,location

ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--parent',type=Path,required=True);p.add_argument('--capture',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
 source=out/'baseline-source';source.mkdir()
 for name in ('src','inc','chr','audio'):shutil.copytree(ROOT/name,source/name)
 shutil.copytree(ROOT/'build/generated',source/'build/generated')
 for q in [ROOT/'build_options.ini',*ROOT.glob('*.cfg')]:shutil.copy2(q,source/q.name)
 frozen={str(q.relative_to(source)):sha(q)for q in source.rglob('*')if q.is_file()}
 (out/'frozen-inputs.json').write_text(json.dumps(frozen,indent=2)+'\n')
 builder=ROOT/'tools/build_mmc5_expanded.py';compiler=ROOT/'tools/Windows/cc65/bin/cl65.exe'
 def build(stage,name):
  r=subprocess.run([sys.executable,str(builder),'--workspace',str(stage),'--compiler',str(compiler),
      '--output',str(out/(name+'.nes'))],cwd=stage,capture_output=True,text=True)
  (out/(name+'.host.log')).write_text(r.stdout+r.stderr)
  assert not r.returncode,r.stdout+r.stderr
 build(source,'baseline');assert sha(out/'baseline.nes')==sha(a.parent)
 stage=out/'source';shutil.copytree(source,stage)

 proof=json.loads((a.capture/'proof.json').read_text())
 event=next(x for x in proof['event_captures']if x['id']==31)
 trace=a.capture/event['trace_file'];assert sha(trace)==event['trace_sha256']
 rows=[{k:int(v)for k,v in r.items()}for r in csv.DictReader(trace.open())]
 assert len(rows)==28 and all(0x400c<=r['address']<=0x400f for r in rows)
 last=max(r['frame']for r in rows);assert last==27
 stream=[];write_ends=[]
 for frame in range(last+1):
  frame_rows=[r for r in rows if r['frame']==frame]
  for r in frame_rows:stream.extend((r['address']-0x4000,r['value']))
  stream.append(254)
  if frame_rows:write_ends.append(len(stream))
 stream.append(255)

 helper='''; Original USA CV3 event1F: Alucard's central fireball noise cue.
; No new RAM, driver, invented tone, music substitution, or DMC sample.
.pushseg
.segment "CV3_COMBAT"
.proc Cv3SpawnAudioType
 sta Cv3ShotType,x
 cmp #6
 bne Done
 lda AvAudioRequest
 bne Done
 lda #26
 sta AvAudioRequest
Done:rts
.endproc

; The existing A7 audio tail has29 free bytes. This23-byte non-SMC wrapper
; temporarily maps C28 for the decoder's extended lookups, then restores it.
; All old fixed-bank samples and Samus helpers retain their original PCs.
.segment "SOPHIA_LAND_AUDIO"
.proc Cv3AudioTick
 lda CurrentBankC
 pha
 lda #$9c
 sta CurrentBankC
 sta $5116
 jsr Cv3AudioFrame
 pla
 sta CurrentBankC
 sta $5116
 rts
.endproc
.assert * <= $c000, lderror, "CV3 audio trampoline must fit existing A7 tail"
.segment "CV_WRAP"
.proc Cv3AudioLo
 cpx #25
 beq Source
 lda SophiaAvSfxLo,x
 rts
Source:lda #<Cv3AlucardSfx
 rts
.endproc
.proc Cv3AudioHi
 cpx #25
 beq Source
 lda SophiaAvSfxHi,x
 rts
Source:lda #>Cv3AlucardSfx
 rts
.endproc
.proc Cv3AudioMask
 cpx #25
 beq Source
 lda SophiaAvSfxMasks,x
 rts
Source:lda #8
 rts
.endproc
.proc Cv3AudioFrame
 jsr RemainingAudioTick
 php
 pha
 phx
 lda AvAudioId
 cmp #26
 bne Done
 ; Never retrigger the noise envelope/length on source-silent updates.
 lda #0
 sta GuestNativeDirty+12
 sta GuestNativeDirty+13
 sta GuestNativeDirty+14
 sta GuestNativeDirty+15
 lda GamePauseStatus
 and #1
 bne Done
 lda OperMode
 beq Done
 lda AvAudioPtr
 cmp #<Cv3AlucardSfxFinal
 beq Volume
 ldx #8
Loop:cmp EndPointers,x
 beq All
 dex
 bpl Loop
 bmi Done
All:lda #1
 sta GuestNativeDirty+14
 sta GuestNativeDirty+15
Volume:lda #1
 sta GuestNativeDirty+12
Done:plx
 pla
 plp
 rts
EndPointers:.byte '''+','.join('<(Cv3AlucardSfx+'+str(v)+')'for v in write_ends[:-1])+'''
.endproc
.align $100
Cv3AlucardSfx:
 .byte '''+','.join(map(str,stream))+'''
Cv3AlucardSfxEnd:
Cv3AlucardSfxFinal=Cv3AlucardSfxEnd-1
.assert >Cv3AlucardSfx = >Cv3AlucardSfxFinal, lderror, "Source update pointer must stay within one page"
.popseg
'''
 changes={}
 def edit(name,old,new):
  f=stage/name;s=f.read_text();assert s.count(old)==1,(name,old)
  n=s.replace(old,new);f.write_text(n);changes[name]=(s,n)
 edit('src/cv3_combat.s','Found:pla\n sta Cv3ShotType,x\n','Found:pla\n jsr Cv3SpawnAudioType\n')
 # Every old PC and table address is retained by same-width calls.
 for name in ('Lo','Hi','Mask'):
  f=stage/'src/remaining_audio.s';s=f.read_text()
  old='  lda SophiaAvSfx'+('Masks'if name=='Mask'else name)+',x\n'
  assert s.count(old)==1
  n=s.replace(old,'.if ::ENABLE_MMC5_EXPANDED\n  jsr Cv3Audio'+name+'\n.else\n'+old+'.endif\n')
  original=changes.get('src/remaining_audio.s',(s,s))[0]
  changes['src/remaining_audio.s']=(original,n);f.write_text(n)
 edit('src/sophia_land_audio.s','  jsr RemainingAudioTick\n','.if ::ENABLE_MMC5_EXPANDED\n  jsr Cv3AudioTick\n.else\n  jsr RemainingAudioTick\n.endif\n')
 f=stage/'src/entrypoint.s';s=f.read_text();n=s+'\n.if ::ENABLE_MMC5_EXPANDED\n.include "cv3_source_audio.s"\n.endif\n'
 f.write_text(n);changes['src/entrypoint.s']=(s,n)
 (stage/'src/cv3_source_audio.s').write_text(helper);changes['src/cv3_source_audio.s']=('',helper)
 patch=''.join(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),
     fromfile=('a/'+name if old else '/dev/null'),tofile='b/'+name))for name,(old,new)in changes.items())
 (out/'implementation.patch').write_text(patch)
 build(stage,'candidate')
 before,after=load(out/'baseline.nes'),load(out/'candidate.nes')
 ol={q[2]:q[1]for line in(out/'baseline.lbl').read_text().splitlines()if len(q:=line.split())==3}
 nl={q[2]:q[1]for line in(out/'candidate.lbl').read_text().splitlines()if len(q:=line.split())==3}
 assert all(nl.get(n)==v for n,v in ol.items()),'An existing exported label moved'
 assert before['raw'][:16]==after['raw'][:16]
 assert before['raw'][16+1048576:]==after['raw'][16+1048576:]
 diffs=[i for i,(x,y)in enumerate(zip(before['raw'],after['raw']))if x!=y]
 assert all(sha(source/n)==h for n,h in frozen.items())
 report=dict(prepared=True,accepted=False,baseline_sha256=sha(out/'baseline.nes'),
     candidate_sha256=sha(out/'candidate.nes'),source_trace_sha256=sha(trace),
     event=31,frames=last+1,stream_bytes=len(stream),changed_bytes=len(diffs),
     changed_banks=sorted({(i-16)//8192 for i in diffs}),
     all_existing_exported_PC_RAM_CHR_exact=True,new_RAM_bytes=0,
     source_effect='Original CV3 Alucard noise, frame-quantized within existing source mixer. Voice write ordering remains common flush ordering; instruction-entry source trace retained.',
     remaining='Grant/Sypha primary DMC, spells/subweapon/transform/hurt cues remain outside this bounded proposal. No target native IRQ/APU/waveform acceptance; CPU test required next.')
 (out/'prepare.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
