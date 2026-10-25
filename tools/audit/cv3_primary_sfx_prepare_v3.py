"""Dedicated CV1-wrapper noise lane: no generic-mixer or non-CV3 overhead."""
from pathlib import Path
import argparse,difflib,hashlib,json,shutil,subprocess,sys
from check_tmnt_render_oa import load
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--previous',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
 frozen=out/'baseline-source';shutil.copytree(a.previous/'baseline-source',frozen)
 stage=out/'source';shutil.copytree(frozen,stage)
 prev=(a.previous/'source/src/cv3_source_audio.s').read_text()
 stream=prev[prev.index('.align $100\n'):prev.rindex('.popseg')]
 stream=stream[:stream.index('Cv3AlucardSfxFinal=')]+'.assert >Cv3AlucardSfx = >(Cv3AlucardSfxEnd-1), lderror, "Source stream within one page"\n'
 helper='''; Actual original USA CV3 event1F, isolated noise image in the existing
;160-byte roster-private ZP slab. Kind2 uses only the first24 bytes; kinds0/1
;use17. Bytes24..31 are private to this lane and consume no additional RAM.
Cv3NoiseApu=RgAudioZp+24
Cv3NoiseActive=RgAudioZp+25 ; unused APU noise register13
Cv3NoiseIndex=RgAudioZp+28
Cv3NoiseMusicVolume=RgAudioZp+29
Cv3NoiseMusicPeriod=RgAudioZp+30
Cv3NoiseMusicHigh=RgAudioZp+31
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
.segment "CV3_GRIP"
.proc Cv3NoiseSceneReset
 php
 lda AvAudioRequest
 cmp #26
 bne Owner
 lda #0
 sta AvAudioRequest
Owner:lda Cv3NoiseActive
 beq Variant
 lda #$80 ; stop at the next audio owner update, restoring its music image
 sta Cv3NoiseActive
Variant:plp
 lda Cv3Variant
 rts
.endproc
.segment "CV_WRAP"
.proc Cv3MusicAndNoiseTick
 lda Cv3NoiseActive
 beq Music
 ; Restore only the underlying native music noise image before its driver.
 lda Cv3NoiseMusicVolume
 sta GuestNativeApu+12
 lda Cv3NoiseMusicPeriod
 sta GuestNativeApu+14
 lda Cv3NoiseMusicHigh
 sta GuestNativeApu+15
 lda Cv3NoiseActive
 bpl Music
 lda #0
 sta Cv3NoiseActive
 lda #1
 sta GuestNativeDirty+12
 sta GuestNativeDirty+14
 sta GuestNativeDirty+15
Music:jsr CvAudioPlay
 lda AvAudioRequest
 cmp #26
 bne Continue
 lda #0
 sta AvAudioRequest
 sta Cv3NoiseIndex
 lda #1
 sta Cv3NoiseActive
Continue:lda Cv3NoiseActive
 beq Done
 ; The remaining generic/world mixer keeps its original independent owner.
 lda GuestNativeApu+12
 sta Cv3NoiseMusicVolume
 lda GuestNativeApu+14
 sta Cv3NoiseMusicPeriod
 lda GuestNativeApu+15
 sta Cv3NoiseMusicHigh
 lda #0
 sta GuestNativeDirty+12
 sta GuestNativeDirty+14
 sta GuestNativeDirty+15
 ldy Cv3NoiseIndex
Read:lda Cv3AlucardSfx,y
 iny
 cmp #254
 beq Mix
 cmp #255
 beq End
 tax
 lda Cv3AlucardSfx,y
 iny
 sta Cv3NoiseApu-12,x
 lda #1
 sta GuestNativeDirty,x
 jmp Read
Mix:sty Cv3NoiseIndex
 lda Cv3NoiseApu
 sta GuestNativeApu+12
 lda Cv3NoiseApu+2
 sta GuestNativeApu+14
 lda Cv3NoiseApu+3
 sta GuestNativeApu+15
Done:rts
End:lda #0
 sta Cv3NoiseActive
 lda #1
 sta GuestNativeDirty+12
 sta GuestNativeDirty+14
 sta GuestNativeDirty+15
 rts
.endproc
'''+stream+'.popseg\n'
 changes={}
 def edit(name,old,new):
  f=stage/name;s=f.read_text();assert s.count(old)==1,(name,old)
  n=s.replace(old,new);f.write_text(n);changes[name]=(s,n)
 edit('src/cv3_combat.s','Found:pla\n sta Cv3ShotType,x\n','Found:pla\n jsr Cv3SpawnAudioType\n')
 edit('src/cv3_core.s','  lda Cv3Variant\n  sta Cv3ActiveVariant\n','  jsr Cv3NoiseSceneReset\n  sta Cv3ActiveVariant\n')
 edit('src/roster_audio.s','.else\n  jsr CvAudioPlay\n.endif\n  jmp Restore\n','.else\n.if ::ENABLE_MMC5_EXPANDED\n  jsr Cv3MusicAndNoiseTick\n.else\n  jsr CvAudioPlay\n.endif\n.endif\n  jmp Restore\n')
 f=stage/'src/entrypoint.s';s=f.read_text();n=s+'\n.if ::ENABLE_MMC5_EXPANDED\n.include "cv3_source_audio.s"\n.endif\n';f.write_text(n);changes['src/entrypoint.s']=(s,n)
 (stage/'src/cv3_source_audio.s').write_text(helper);changes['src/cv3_source_audio.s']=('',helper)
 with(out/'build.log').open('w')as log:
  r=subprocess.run([sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),'--workspace',str(stage),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/'candidate.nes')],cwd=stage,stdout=log,stderr=subprocess.STDOUT)
 assert not r.returncode,(out/'build.log').read_text()[-4000:]
 old,new=load(a.previous/'baseline.nes'),load(out/'candidate.nes')
 ol={q[2]:q[1]for line in(a.previous/'baseline.lbl').read_text().splitlines()if len(q:=line.split())==3}
 nl={q[2]:q[1]for line in(out/'candidate.lbl').read_text().splitlines()if len(q:=line.split())==3}
 assert all(nl.get(n)==v for n,v in ol.items()),'Existing exported PC/RAM moved'
 assert old['raw'][:16]==new['raw'][:16]and old['raw'][16+1048576:]==new['raw'][16+1048576:]
 changes_bytes=[i for i,(x,y)in enumerate(zip(old['raw'],new['raw']))if x!=y]
 patch=''.join(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+name if before else'/dev/null',tofile='b/'+name))for name,(before,after)in changes.items())
 (out/'implementation.patch').write_text(patch)
 for suffix in ['.nes','.lbl','.dbg','.map']:shutil.copyfile(a.previous/('baseline'+suffix),out/('baseline'+suffix))
 (out/'prepare.json').write_text(json.dumps(dict(prepared=True,accepted=False,baseline_sha256=sha(out/'baseline.nes'),candidate_sha256=sha(out/'candidate.nes'),changed_bytes=len(changes_bytes),changed_banks=sorted({(i-16)//8192 for i in changes_bytes}),old_exported_PC_RAM_CHR_exact=True,new_RAM_bytes=0,existing_unused_private_roster_bytes=8,source_effect='Original28-update event1F inside already mapped CV1 wrapper; native music noise is restored before driver/save then source overlays. Generic/world mixers and every non-CV3 audio route stay literal.'),indent=2)+'\n')
 print((out/'prepare.json').read_text())
if __name__=='__main__':main()
