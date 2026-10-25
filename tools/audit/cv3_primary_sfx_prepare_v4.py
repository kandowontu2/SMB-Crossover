"""Keep a private source noise image; update cached music only on driver writes."""
from pathlib import Path
import argparse,csv,difflib,hashlib,json,shutil,subprocess,sys
from check_tmnt_render_oa import load
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--previous',type=Path,required=True);p.add_argument('--capture',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
 frozen=out/'baseline-source';shutil.copytree(a.previous/'baseline-source',frozen)
 stage=out/'source';shutil.copytree(a.previous/'source',stage)
 rows=[{k:int(v)for k,v in r.items()}for r in csv.DictReader((a.capture/'event-1f-apu.csv').open())]
 volumes=[];periods=[];flags=[];v=0x30;period=0
 for frame in range(28):
  rr=[r for r in rows if r['frame']==frame]
  for r in rr:
   if r['address']==0x400c:v=r['value']
   if r['address']==0x400e:period=r['value']
  flags.append(3 if len(rr)==3 else 1 if rr else 0);volumes.append(v);periods.append(period)
 helper=stage/'src/cv3_source_audio.s';s=helper.read_text();start=s.index('.proc Cv3MusicAndNoiseTick');end=s.index('.align $100',start)
 body='''.proc Cv3MusicAndNoiseTick
 jsr CvAudioPlay
 lda Cv3NoiseActive
 beq Request
 lda GuestNativeDirty+12
 beq Period
 lda GuestNativeApu+12
 sta Cv3NoiseMusicVolume
 lda Cv3NoiseApu
 sta GuestNativeApu+12
 lda #0
 sta GuestNativeDirty+12
Period:lda GuestNativeDirty+14
 beq High
 lda GuestNativeApu+14
 sta Cv3NoiseMusicPeriod
 lda Cv3NoiseApu+2
 sta GuestNativeApu+14
 lda #0
 sta GuestNativeDirty+14
High:lda GuestNativeDirty+15
 beq Request
 lda GuestNativeApu+15
 sta Cv3NoiseMusicHigh
 lda Cv3NoiseApu+3
 sta GuestNativeApu+15
 lda #0
 sta GuestNativeDirty+15
Request:lda Cv3NoiseActive
 bmi End
 lda AvAudioRequest
 cmp #26
 bne Continue
 lda Cv3NoiseActive
 bne Reset
 lda GuestNativeApu+12
 sta Cv3NoiseMusicVolume
 lda GuestNativeApu+14
 sta Cv3NoiseMusicPeriod
 lda GuestNativeApu+15
 sta Cv3NoiseMusicHigh
Reset:lda #0
 sta AvAudioRequest
 sta Cv3NoiseIndex
 lda #1
 sta Cv3NoiseActive
Continue:lda Cv3NoiseActive
 beq Done
 ldy Cv3NoiseIndex
 cpy #28
 beq End
 inc Cv3NoiseIndex
 lda Cv3NoiseFlags,y
 beq Done
 cmp #3
 bne Volume
 lda Cv3NoisePeriods,y
 sta Cv3NoiseApu+2
 sta GuestNativeApu+14
 lda #8
 sta Cv3NoiseApu+3
 sta GuestNativeApu+15
 lda #1
 sta GuestNativeDirty+14
 sta GuestNativeDirty+15
Volume:lda Cv3NoiseVolumes,y
 sta Cv3NoiseApu
 sta GuestNativeApu+12
 lda #1
 sta GuestNativeDirty+12
Done:rts
End:lda #0
 sta Cv3NoiseActive
RestoreMusic:lda Cv3NoiseMusicVolume
 sta GuestNativeApu+12
 lda Cv3NoiseMusicPeriod
 sta GuestNativeApu+14
 lda Cv3NoiseMusicHigh
 sta GuestNativeApu+15
 lda #1
 sta GuestNativeDirty+12
 sta GuestNativeDirty+14
 sta GuestNativeDirty+15
 rts
.endproc
; The imported driver's one unmarked direct volume store also participates
; in the private music cache. Preserve its original A/X/Y/status contract.
.proc Cv3NoiseVolumeStore
 sta GuestNativeApu+12
 php
 pha
 lda Cv3NoiseActive
 beq Done
 inc GuestNativeDirty+12
Done:pla
 plp
 rts
.endproc
Cv3NoiseFlags:.byte '''+','.join(map(str,flags))+'''
Cv3NoiseVolumes:.byte '''+','.join(map(str,volumes))+'''
Cv3NoisePeriods:.byte '''+','.join(map(str,periods))+'''
'''
 helper.write_text(s[:start]+body+'.popseg\n')
 gen=stage/'build/generated/guest-audio/castlevania.inc';s=gen.read_text();old='  STA ::GuestNativeApu+$0c\n'
 assert s.count(old)==1
 gen.write_text(s.replace(old,'.if ::ENABLE_MMC5_EXPANDED\n  JSR ::Cv3NoiseVolumeStore\n.else\n'+old+'.endif\n'))
 with(out/'build.log').open('w')as log:
  r=subprocess.run([sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),'--workspace',str(stage),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/'candidate.nes')],cwd=stage,stdout=log,stderr=subprocess.STDOUT)
 assert not r.returncode,(out/'build.log').read_text()[-4000:]
 oldb,new=load(a.previous/'baseline.nes'),load(out/'candidate.nes')
 ol={q[2]:q[1]for line in(a.previous/'baseline.lbl').read_text().splitlines()if len(q:=line.split())==3};nl={q[2]:q[1]for line in(out/'candidate.lbl').read_text().splitlines()if len(q:=line.split())==3}
 assert all(nl.get(n)==v for n,v in ol.items()),'Existing exported PC/RAM moved'
 assert oldb['raw'][:16]==new['raw'][:16]and oldb['raw'][16+1048576:]==new['raw'][16+1048576:]
 diff=[i for i,(x,y)in enumerate(zip(oldb['raw'],new['raw']))if x!=y]
 patch=''
 for name in ['src/entrypoint.s','src/cv3_combat.s','src/cv3_core.s','src/roster_audio.s','src/cv3_source_audio.s','build/generated/guest-audio/castlevania.inc']:
  before=(frozen/name).read_text()if(frozen/name).exists()else'';after=(stage/name).read_text()
  patch+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+name if before else'/dev/null',tofile='b/'+name))
 (out/'implementation.patch').write_text(patch)
 for suffix in ['.nes','.lbl','.dbg','.map']:shutil.copyfile(a.previous/('baseline'+suffix),out/('baseline'+suffix))
 (out/'prepare.json').write_text(json.dumps(dict(prepared=True,accepted=False,baseline_sha256=sha(out/'baseline.nes'),candidate_sha256=sha(out/'candidate.nes'),changed_bytes=len(diff),changed_banks=sorted({(i-16)//8192 for i in diff}),old_exported_PC_RAM_CHR_exact=True,new_RAM_bytes=0,existing_unused_private_roster_bytes=8,source_effect='Original28-update source register tables; cache underlying native music only on driver writes; generic/world mixers remain independent.'),indent=2)+'\n');print((out/'prepare.json').read_text())
if __name__=='__main__':main()
