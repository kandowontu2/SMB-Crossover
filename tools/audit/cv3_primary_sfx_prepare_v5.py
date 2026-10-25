"""Compensate native cue work by an equivalent CV1 private-ZP restore leaf."""
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
 f=stage/'src/roster_audio.s';s=f.read_text()
 old='''Restore:
  ldy #ZpCount-1
Load:
  ldx ZpAddresses,y
  lda $00,x
  sta RgAudioZp,y
  lda RgAudioCpuZp,y
  sta $00,x
  dey
  cpy #$ff
  bne Load
  lda #0
'''
 new='''Restore:
.if Kind=2 .and ::ENABLE_MMC5_EXPANDED
  jsr Cv3RestoreAudioZp
  jmp AudioRestored
  .res 14,$ea ; old20-byte loop footprint: no original following PC moves
.else
  ldy #ZpCount-1
Load:
  ldx ZpAddresses,y
  lda $00,x
  sta RgAudioZp,y
  lda RgAudioCpuZp,y
  sta $00,x
  dey
  cpy #$ff
  bne Load
.endif
AudioRestored:
  lda #0
'''
 assert s.count(old)==1;s=s.replace(old,new);f.write_text(s)
 helper=stage/'src/cv3_source_audio.s';s=helper.read_text();i=s.rindex('.popseg')
 addresses=[*range(0xba,0xc0),*range(0xe0,0xf0),0x22,0x60]
 leaf='.segment "CV_WRAP"\n.proc Cv3RestoreAudioZp\n'
 for idx in range(23,-1,-1):
  z=addresses[idx]
  leaf+=f' lda ${z:02x}\n sta RgAudioZp+{idx}\n lda RgAudioCpuZp+{idx}\n sta ${z:02x}\n'
 leaf+=' ldx #$ba\n ldy #$ff\n cpy #$ff ; match original final comparison and restored registers\n rts\n.endproc\n'
 helper.write_text(s[:i]+leaf+s[i:])
 with(out/'build.log').open('w')as log:
  r=subprocess.run([sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),'--workspace',str(stage),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/'candidate.nes')],cwd=stage,stdout=log,stderr=subprocess.STDOUT)
 assert not r.returncode,(out/'build.log').read_text()[-4000:]
 oldb,newb=load(a.previous/'baseline.nes'),load(out/'candidate.nes')
 ol={q[2]:q[1]for line in(a.previous/'baseline.lbl').read_text().splitlines()if len(q:=line.split())==3};nl={q[2]:q[1]for line in(out/'candidate.lbl').read_text().splitlines()if len(q:=line.split())==3}
 assert all(nl.get(n)==v for n,v in ol.items()),'Existing exported PC/RAM moved'
 assert oldb['raw'][:16]==newb['raw'][:16]and oldb['raw'][16+1048576:]==newb['raw'][16+1048576:]
 diff=[i for i,(x,y)in enumerate(zip(oldb['raw'],newb['raw']))if x!=y];patch=''
 for name in ['src/entrypoint.s','src/cv3_combat.s','src/cv3_core.s','src/roster_audio.s','src/cv3_source_audio.s','build/generated/guest-audio/castlevania.inc']:
  before=(frozen/name).read_text()if(frozen/name).exists()else'';after=(stage/name).read_text()
  patch+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+name if before else'/dev/null',tofile='b/'+name))
 (out/'implementation.patch').write_text(patch)
 for suffix in ['.nes','.lbl','.dbg','.map']:shutil.copyfile(a.previous/('baseline'+suffix),out/('baseline'+suffix))
 (out/'prepare.json').write_text(json.dumps(dict(prepared=True,accepted=False,baseline_sha256=sha(out/'baseline.nes'),candidate_sha256=sha(out/'candidate.nes'),changed_bytes=len(diff),changed_banks=sorted({(i-16)//8192 for i in diff}),old_exported_PC_RAM_CHR_exact=True,new_RAM_bytes=0,existing_unused_private_roster_bytes=8,restore_addresses=addresses,source_effect='Original28-update source register tables; independent noise cache, literal old mixer and same24 ZP restore values with equivalent flags/register contract.'),indent=2)+'\n');print((out/'prepare.json').read_text())
if __name__=='__main__':main()
