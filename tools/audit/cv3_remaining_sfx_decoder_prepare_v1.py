"""Source-equivalent indexed stream decoder, private exact50b+aaa4 proposal only."""
from pathlib import Path
import argparse,difflib,hashlib,json,shutil,subprocess,sys
from check_tmnt_audio_fallback_oc import qualified
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT=D/'cv3-remaining-current50b-v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
 assert sha(PARENT/'candidate.nes')=='aaa4ce1d08b1a31518eeef375dc5256e0d399ac6254852994cc991856a3bca12'
 stage=out/'source';shutil.copytree(PARENT/'source',stage);f=stage/'src/cv3_remaining_source_fx.s';old=f.read_bytes();assert hashlib.sha256(old).hexdigest()=='2efd8c494d647b6d3ec051fa776e372b75c75a0321db2ba5a8a1003330835619'
 text=old.decode();start=text.index('Decode:jsr Read');end=text.index('Read:jsr Peek',start)
 after=text[start:end].replace('Decode:jsr Read','Decode:ldy #0\nNextByte:lda (R0),y\n iny').replace(' jsr Read\n cpx #15',' lda (R0),y\n iny\n cpx #15').replace(' jmp Decode',' jmp NextByte').replace('Decoded:rts','Decoded:tya\n clc\n adc R0\n sta R0\n bcc PointerDone\n inc R1\nPointerDone:rts')
 assert after.count('lda (R0),y')==2 and 'jsr Read'not in after
 text=text[:start]+after+text[end:];f.write_bytes(text.encode());cmd=[sys.executable,str(stage/'tools/build_mmc5_expanded.py'),'--workspace',str(stage),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/'candidate.nes')]
 with(out/'build.log').open('w')as log:r=subprocess.run(cmd,cwd=stage,stdout=log,stderr=subprocess.STDOUT)
 assert not r.returncode,(out/'build.log').read_text()[-5000:]
 oldraw=(PARENT/'candidate.nes').read_bytes();newraw=(out/'candidate.nes').read_bytes();banks=[]
 for n in range(128):
  x=oldraw[16+n*8192:16+(n+1)*8192];y=newraw[16+n*8192:16+(n+1)*8192]
  if x!=y:banks.append(n)
 assert banks==[82];assert oldraw[:16]==newraw[:16]and oldraw[1048592:]==newraw[1048592:]
 # All ADOPTED50b public PCs remain; symbols newly introduced by unadopted
 # aaa4 are permitted to move inside their own new helper/data span.
 baseq=qualified(PARENT/'baseline.nes');newq=qualified(out/'candidate.nes');delta={k:(v,newq.get(k))for k,v in baseq.items()if newq.get(k)!=v};assert delta=={('Cv3SpawnAudioType','Done'):(0xb3eb,None),('_FARCALL_COUNT',):(baseq[('_FARCALL_COUNT',)],baseq[('_FARCALL_COUNT',)]+1)},delta
 shutil.copyfile(PARENT/'baseline.nes',out/'baseline.nes')
 for ext in['dbg','lbl','map']:shutil.copyfile(PARENT/('baseline.'+ext),out/('baseline.'+ext))
 (out/'implementation-increment.patch').write_text(''.join(difflib.unified_diff(old.decode().splitlines(True),text.splitlines(True),fromfile='a/src/cv3_remaining_source_fx.s',tofile='b/src/cv3_remaining_source_fx.s')),newline='\n')
 proof=dict(passed=True,accepted=False,status='SOURCE_ONLY_CPU_NATIVE_PENDING',ROM_sha256=sha(out/'candidate.nes'),baseline_ROM_sha256=sha(out/'baseline.nes'),held_parent_ROM_sha256=sha(PARENT/'candidate.nes'),changed_banks_from_held=banks,all_adopted_symbols_exact_except_legitimate_Done_FARCALL=True,source_file_sha256=sha(f),increment_patch_sha256=sha(out/'implementation-increment.patch'),retained_Read_and_Peek_are_genuine_callable_routines=True,new_RAM_CHR_bytes=0,scope='Only indexed stream reads/pointer commit optimized; all original stream byte order/value/ticks and public owner/mapper contracts still require exact fresh CPU and native qualification. Old aaa4 held packet is immutable.')
 (out/'composition.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
