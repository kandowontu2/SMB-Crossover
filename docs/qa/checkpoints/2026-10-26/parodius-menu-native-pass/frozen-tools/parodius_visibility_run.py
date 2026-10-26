"""Run one frozen read-only Parodius observer under an explicit native grant."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--emulator',type=Path,required=True);p.add_argument('--timeout',type=int,default=180);a=p.parse_args();z=json.loads((a.packet/'preparation.json').read_text(encoding='utf-8'));script=Path(z['script']);out=script.parent
 assert all(sha(Path(n))==v for n,v in z['dependencies'].items());assert sha(script)==z['script_sha256']and sha(out/'candidate.nes')==z['ROM_sha256']
 assert not(out/'proof.json').exists()and not(out/'native-result.json').exists(),'New profile outputs only'
 with(out/'host.log').open('w',encoding='utf-8')as f:r=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out),'--emulator',str(a.emulator),str(script),str(out/'candidate.nes'),'--timeout',str(a.timeout),'--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false','--option=--nes.removeSpriteLimit=false'],stdout=f,stderr=subprocess.STDOUT)
 native=json.loads((out/'native-result.json').read_text(encoding='utf-8'))if(out/'native-result.json').exists()else{};unchanged=all(sha(Path(n))==v for n,v in z['dependencies'].items());passed=r.returncode==0 and native.get('passed',False)and unchanged
 q=dict(passed=passed,goal_complete=False,native=native,emulator_exit=r.returncode,emulator_sha256=sha(a.emulator),preparation_sha256=sha(a.packet/'preparation.json'),script_sha256=sha(script),runner_sha256=sha(Path(__file__)),dependencies_unchanged=unchanged,output_bindings={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.name!='proof.json'and p.suffix not in ['.nes','.dbg','.lbl','.map']},scope='One bounded native observer only; diagnostic failures remain passed=false. No private art candidate or stage-clear acceptance yet.')
 (out/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=passed,emulator_exit=r.returncode,native=native,proof_sha256=sha(out/'proof.json'))));raise SystemExit(0 if passed else 1)
if __name__=='__main__':main()
