"""Private same-PC unrolled CV1 ZP Save proposal on held e6b; no native worker."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/cv3-dmc-complete-v1')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def replace(p,a,b):
 raw=p.read_bytes();nl='\r\n'if b'\r\n'in raw else'\n';s=raw.decode().replace('\r\n','\n');assert s.count(a)==1;s=s.replace(a,b);p.write_bytes(s.replace('\n',nl).encode())
def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--output',type=Path,required=True);q=a.parse_args();out=q.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False);source=out/'source';donor=D/'final-current8ff-v1';assert sha(donor/'candidate.nes')=='e6baf465a4fb3981dc1d9f1bea64a129f1dbb8d2a8276f934a38eb9c00c0728c';shutil.copytree(donor/'source-final',source)
 old='''Save:
  ldx ZpAddresses,y
  lda $00,x
  sta RgAudioCpuZp,y
  lda RgAudioZp,y
  sta $00,x
  dey
  cpy #$ff
  bne Save
'''
 new='''Save:
.if Kind=2 .and ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
  ; Keep the real original Save entry and all following PCs. Same descending
  ; memory operations and final A/X/Y/P; no shared mapper/SMC work is added.
  jsr Cv3SaveAudioZp
  jmp SavedPrivate
  .res 12,$ea ; exact original18-byte Save body
SavedPrivate:
.else
  ldx ZpAddresses,y
  lda $00,x
  sta RgAudioCpuZp,y
  lda RgAudioZp,y
  sta $00,x
  dey
  cpy #$ff
  bne Save
.endif
'''
 replace(source/'src/roster_audio.s',old,new)
 addresses=[0xba,0xbb,0xbc,0xbd,0xbe,0xbf]+list(range(0xe0,0xf0))+[0x22,0x60]
 helper='''
; The source CV1 image ends atD836. This is recorded unused same-C28 slack,
; before the fixedDC00 wrapper; all original driver bytes/entrypoints stay exact.
.pushseg
.segment "CV_AUDIO"
.proc Cv3SaveAudioZp
'''
 for i in reversed(range(len(addresses))):helper+=f' lda ${addresses[i]:02x}\n sta RgAudioCpuZp+{i}\n lda RgAudioZp+{i}\n sta ${addresses[i]:02x}\n'
 helper+=' ldx #$ba\n ldy #$ff\n cpy #$ff ; exact final indexed-loop register/status contract\n rts\n.endproc\n.assert Cv3SaveAudioZp=$d837,lderror,"Recorded unused source-CV1 slack start"\n.assert *<=$dc00,lderror,"Preserve fixed wrapper and every existing source byte"\n.popseg\n'
 p=source/'src/cv3_dmc_complete.s';raw=p.read_bytes();nl='\r\n'if b'\r\n'in raw else'\n';p.write_bytes(raw+helper.replace('\n',nl).encode())
 for name in ['candidate.nes','candidate.dbg','candidate.lbl','candidate.map']:shutil.copyfile(donor/name,out/('held-'+name))
 base=D/'proposal-current8ff-v4'
 for name in ['baseline.nes','baseline.dbg','baseline.lbl','baseline.map']:shutil.copyfile(base/name,out/name)
 command=[sys.executable,str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/'candidate.nes')]
 with(out/'build.host.log').open('w')as f:r=subprocess.run(command,cwd=source,stdout=f,stderr=subprocess.STDOUT)
 assert not r.returncode,(out/'build.host.log').read_text()[-6000:]
 proof=dict(candidate_sha256=sha(out/'candidate.nes'),held_donor_sha256=sha(donor/'candidate.nes'),baseline_sha256=sha(out/'baseline.nes'),modified_from_held={n:sha(source/n)for n in ['src/roster_audio.s','src/cv3_dmc_complete.s']},native_worker_used=False,accepted=False)
 (out/'proposal.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
