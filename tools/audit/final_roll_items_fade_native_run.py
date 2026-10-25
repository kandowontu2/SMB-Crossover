"""Run exactly one granted, frozen Roll fade profile, retaining diagnostics."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--packet',type=Path,required=True);p.add_argument('--role',choices=['baseline','candidate'],required=True)
    p.add_argument('--mode',type=int,choices=[0,1],required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--emulator',type=Path,required=True);p.add_argument('--timeout',type=int,default=900)
    a=p.parse_args();z=json.loads((a.packet/'preparation.json').read_text(encoding='utf-8'))
    q=next(x for x in z['profiles']if x['role']==a.role and x['mode_value']==a.mode)
    assert all(sha(ROOT/n)==v for n,v in z['dependencies'].items()),'Dependency changed since freeze'
    script=Path(q['script']);assert sha(script)==q['script_sha256'] and sha(script.parent/'config.json')==q['config_sha256']
    assert sha(a.packet/a.role/'candidate.nes')==q['ROM_sha256']
    a.output.mkdir(parents=True,exist_ok=False)
    for ext in ['.nes','.dbg','.lbl','.map']:shutil.copy2(a.packet/a.role/('candidate'+ext),a.output/('candidate'+ext))
    shutil.copy2(script,a.output/'run.lua');shutil.copy2(script.parent/'config.json',a.output/'config.json')
    with(a.output/'host.log').open('w',encoding='utf-8')as f:
        result=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(a.output),'--emulator',str(a.emulator),str(a.output/'run.lua'),str(a.output/'candidate.nes'),'--timeout',str(a.timeout),'--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],stdout=f,stderr=subprocess.STDOUT)
    native=json.loads((a.output/'native-result.json').read_text(encoding='utf-8'))if(a.output/'native-result.json').exists()else{}
    unchanged=all(sha(ROOT/n)==v for n,v in z['dependencies'].items())
    failure=json.loads((a.output/'first-failure.json').read_text(encoding='utf-8'))if(a.output/'first-failure.json').exists()else None
    passed=result.returncode==0 and unchanged and native.get('mechanics_passed',False)and native.get('actual_mode_readback')==a.mode and native.get('fade_policy_passed',False)
    proof=dict(passed=passed,goal_complete=False,emulator_exit=result.returncode,dependencies_unchanged=unchanged,emulator_sha256=sha(a.emulator),runner_sha256=sha(Path(__file__)),preparation_sha256=sha(a.packet/'preparation.json'),profile=q,native=native,first_failure=failure,captures={f.name:sha(f)for f in sorted(a.output.glob('*.argb'))})
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=passed,role=a.role,mode=a.mode,mechanics=native.get('mechanics_passed'),fade=native.get('fade_policy_passed'),first_failure=failure,proof_sha256=sha(a.output/'proof.json'))))
    raise SystemExit(0 if passed else 1)
if __name__=='__main__':main()
