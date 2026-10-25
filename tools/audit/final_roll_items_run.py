"""Execute one frozen Roll profile only after a native worker is granted."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys

ROOT=Path(__file__).resolve().parents[2]
TARGET='8ff245ae662059abbc77c5de517260032775b7ba881a5201b8b54686ccf08277'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--packet',type=Path,required=True)
    p.add_argument('--mode',choices=['easy','hard'],required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--emulator',type=Path,required=True)
    p.add_argument('--expected-sha256',default=TARGET)
    p.add_argument('--timeout',type=int,default=1800)
    a=p.parse_args();packet=json.loads((a.packet/'preparation.json').read_text(encoding='utf-8'))
    assert packet['ROM_sha256']==a.expected_sha256
    profile=next(q for q in packet['profiles']if q['mode']==a.mode)
    frozen=a.packet/'frozen-current';script=Path(profile['script'])
    assert sha(frozen/'candidate.nes')==a.expected_sha256 and sha(script)==profile['script_sha256']
    assert sha(frozen/'final_roll_items_native.lua')==packet['fixture_sha256']
    assert '["hard"]='+('true'if a.mode=='hard'else'false')in script.read_text(encoding='utf-8').splitlines()[1]
    assert '["mode_value"]='+str(int(a.mode=='hard'))in script.read_text(encoding='utf-8').splitlines()[1]
    dependencies={str(q.relative_to(ROOT)).replace('\\','/'):sha(q)for q in [ROOT/'tools/run_mesen.py',ROOT/'tools/audit/run_mesen_isolated.py']}
    a.output.mkdir(parents=True,exist_ok=False)
    for ext in ['.nes','.dbg','.lbl','.map']:shutil.copy2(frozen/('candidate'+ext),a.output/('candidate'+ext))
    for name in ['final_roll_items_native.lua']:shutil.copy2(frozen/name,a.output/name)
    shutil.copy2(script,a.output/'run.lua');shutil.copy2(script.parent/'config.json',a.output/'config.json')
    with(a.output/'host.log').open('w',encoding='utf-8')as log:
        result=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),
            '--output',str(a.output),'--emulator',str(a.emulator),str(a.output/'run.lua'),str(a.output/'candidate.nes'),
            '--timeout',str(a.timeout),'--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros',
            '--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],stdout=log,stderr=subprocess.STDOUT)
    assert dependencies=={n:sha(ROOT/n)for n in dependencies},'Shared launch helper changed during native run; retain outputs and re-audit.'
    f=a.output/'native-result.json';native=json.loads(f.read_text(encoding='utf-8'))if f.exists()else{}
    fail=a.output/'first-failure.json'
    receipt=dict(passed=result.returncode==0 and native.get('passed',False)and native.get('actual_mode_readback')==int(a.mode=='hard')and native.get('hard')==(a.mode=='hard'),goal_complete=False,emulator_exit=result.returncode,ROM_sha256=a.expected_sha256,mode=a.mode,packet=str(a.packet),preparation_sha256=sha(a.packet/'preparation.json'),source_ledger_sha256=packet['source_ledger_sha256'],fixture_sha256=packet['fixture_sha256'],runner_sha256=sha(Path(__file__)),script_sha256=sha(a.output/'run.lua'),emulator_sha256=sha(a.emulator),launch_helper_bindings=dependencies,native=native,first_failure=json.loads(fail.read_text(encoding='utf-8'))if fail.exists()else None,scope='One bounded native profile; source staging/retained failures explicit. No mobile gameplay timing/audio or all-roster completion claim.')
    (a.output/'proof.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=receipt['passed'],mode=a.mode,updates=native.get('updates'),first_failure=receipt['first_failure'],output=str(a.output))))
    raise SystemExit(0 if receipt['passed']else 1)


if __name__=='__main__':main()
