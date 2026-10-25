"""Private dedicated noise owner; preserve55 and the failed generic proposal."""
from pathlib import Path
import argparse,difflib,hashlib,json,shutil,subprocess,sys
from check_tmnt_render_oa import load
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--previous',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
 frozen=out/'baseline-source';shutil.copytree(a.previous/'baseline-source',frozen)
 stage=out/'source';shutil.copytree(a.previous/'source',stage)
 # No change to generic25-effect decoder or its music snapshot owner.
 shutil.copyfile(frozen/'src/remaining_audio.s',stage/'src/remaining_audio.s')
 oldhelper=(stage/'src/cv3_source_audio.s').read_text()
 stream=oldhelper[oldhelper.index('.align $100\n'):oldhelper.rindex('.popseg')]
 header=oldhelper[:oldhelper.index('.proc Cv3AudioLo')]
 helper=header+'''
.proc Cv3AudioFrame
 jsr RemainingAudioSupported
 bcc Done
 lda AvAudioId
 cmp #26
 beq Source
 lda AvAudioRequest
 cmp #26
 beq Source
 jmp RemainingAudioTick
Source:lda GamePauseStatus
 and #1
 bne Done
 lda OperMode
 beq Done
 lda AvAudioRequest
 cmp #26
 bne Decode
 lda #0
 sta AvAudioRequest
 sta AvAudioPtr
 sta AvAudioOldMask
 lda #>Cv3AlucardSfx
 sta AvAudioPtr+1
 lda #26
 sta AvAudioId
 lda #8
 sta AvAudioMask
Decode:ldy AvAudioPtr
Read:lda Cv3AlucardSfx,y
 iny
 cmp #254
 beq Frame
 cmp #255
 beq End
 tax
 lda Cv3AlucardSfx,y
 iny
 sta AvAudioSfx,x
 lda #1
 sta GuestFxDirty,x
 jmp Read
Frame:sty AvAudioPtr
 lda GuestNativeEnable
 and #8
 bne Done
 lda GuestNativeEnable
 ora #8
 jsr GuestNativeStatusSTA
Done:rts
End:sty AvAudioPtr
 lda #0
 sta AvAudioId
 sta AvAudioMask
 lda #$80
 sta AvAudioOldMask ; one-update source release, consumed by the final mixer
 rts
.endproc
'''+stream+'''
.segment "X5_AUDIO_MIX"
.proc Cv3AudioNoiseOwner
 lda AvAudioId
 cmp #26
 bne Release
 lda GuestMixMask
 and #8
 bne Ordinary ; real shared world noise keeps its existing priority
 ldx #3
Copy:lda AvAudioSfx+12,x
 sta GuestFxApu+12,x
 dex
 bpl Copy
 lda #8
 sta GuestMixMask
 rts
Release:lda AvAudioOldMask
 bpl Ordinary
 lda #0
 sta AvAudioOldMask
 lda GuestMixChanged
 ora #8
 sta GuestMixChanged
Ordinary:lda GuestMixMask
 ora GuestMixChanged
 rts
.endproc
.assert * <= $c000, lderror, "Dedicated noise owner must fit existing A29 tail"
.popseg
'''
 (stage/'src/cv3_source_audio.s').write_text(helper)
 f=stage/'src/guest_audio.s';s=f.read_text();needle='.proc X5NativeNoiseMask\n ora GuestMixChanged\n and #8\n rts\n'
 assert s.count(needle)==1;f.write_text(s.replace(needle,'.proc X5NativeNoiseMask\n jsr Cv3AudioNoiseOwner\n and #8\n rts\n'))
 # Generic bank bracket remains23 bytes; the dedicated source never touches
 # GuestNativeApu/AvAudioMusic and never pauses/rewinds the source song.
 with(out/'build.log').open('w')as log:
  r=subprocess.run([sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),'--workspace',str(stage),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/'candidate.nes')],cwd=stage,stdout=log,stderr=subprocess.STDOUT)
 assert not r.returncode,(out/'build.log').read_text()[-4000:]
 old,new=load(a.previous/'baseline.nes'),load(out/'candidate.nes')
 ol={q[2]:q[1]for line in(a.previous/'baseline.lbl').read_text().splitlines()if len(q:=line.split())==3}
 nl={q[2]:q[1]for line in(out/'candidate.lbl').read_text().splitlines()if len(q:=line.split())==3}
 assert all(nl.get(n)==v for n,v in ol.items()),'Existing exported PC/RAM moved'
 assert old['raw'][:16]==new['raw'][:16]and old['raw'][16+1048576:]==new['raw'][16+1048576:]
 changes=[i for i,(x,y)in enumerate(zip(old['raw'],new['raw']))if x!=y]
 patch=''
 for name in ['src/entrypoint.s','src/cv3_combat.s','src/sophia_land_audio.s','src/guest_audio.s','src/cv3_source_audio.s']:
  before=(frozen/name).read_text()if(frozen/name).exists()else'';after=(stage/name).read_text()
  patch+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+name if before else'/dev/null',tofile='b/'+name))
 (out/'implementation.patch').write_text(patch)
 for suffix in ['.nes','.lbl','.dbg','.map']:shutil.copyfile(a.previous/('baseline'+suffix),out/('baseline'+suffix))
 (out/'prepare.json').write_text(json.dumps(dict(prepared=True,accepted=False,baseline_sha256=sha(out/'baseline.nes'),candidate_sha256=sha(out/'candidate.nes'),changed_bytes=len(changes),changed_banks=sorted({(i-16)//8192 for i in changes}),old_exported_PC_RAM_CHR_exact=True,new_RAM_bytes=0,source_effect='Original28-update event1F; dedicated noise owner borrows common FX image, higher-priority world noise retained, source music image untouched.'),indent=2)+'\n')
 print((out/'prepare.json').read_text())
if __name__=='__main__':main()
