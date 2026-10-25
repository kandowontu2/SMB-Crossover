"""Inline the native special-draw leaf in the existing exact-ID gate."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
BASE=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-combined-pu/candidate-v6')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 assert sha(BASE/'candidate.nes')=='75564e8cf7fce3b71d197f02276158b6cb84d05407e9b8f5222c3c6ed5e6c5b0'
 s=a.output/'source';shutil.copytree(BASE/'source',s);f=s/'src/tmnt_audio_resident.s';v=f.read_text()
 old=' pla\n plp\n farcall TnSpecialDrawDispatch,jmp\n::TnFastSpecialLegacy:';assert v.count(old)==1
 v=v.replace(old,''' pla
 plp
 ; TnSpecialDrawDispatch's exact-ID native leaf has no other work.
 ; Its LDA/CMP admission leaves C=1; source LDA#0 supplies N/Z.
::TnFastSpecialNativeLeaf:
 lda #0
 sta a:SsChrActive
 sec
 rts
 .res 11,$ea ; retain the replaced18-byte farcall footprint
 .assert *-TnFastSpecialNativeLeaf=18,error,"Retain native leaf footprint"
::TnFastSpecialLegacy:''');f.write_text(v)
 z=subprocess.run([sys.executable,str(s/'tools/build_mmc5_expanded.py'),'--workspace',str(s),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')],cwd=s,capture_output=True,text=True)
 (a.output/'build.log').write_text(z.stdout+z.stderr);assert z.returncode==0,(z.stdout+z.stderr)[-2500:]
 q=dict(prepared=True,accepted=False,ROM_sha256=sha(a.output/'candidate.nes'),parent_ROM_sha256=sha(BASE/'candidate.nes'),changed_source='src/tmnt_audio_resident.s',scope='One exact-ID native leaf; 18-byte footprint preserved, no new RAM, no source music or game-state change. Pending differential/native timing checks.')
 (a.output/'preparation.json').write_text(json.dumps(q,indent=2)+'\n');print(q['ROM_sha256'])
if __name__=='__main__':main()
