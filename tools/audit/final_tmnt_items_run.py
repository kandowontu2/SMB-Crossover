"""Run one already frozen turtle lifecycle profile using one native worker."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--packet',type=Path,required=True)
    p.add_argument('--variant',type=int,choices=range(4),required=True)
    p.add_argument('--mode',choices=['easy','hard'],required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--emulator',type=Path,required=True)
    p.add_argument('--timeout',type=int,default=900)
    a=p.parse_args();z=json.loads((a.packet/'preparation.json').read_text())
    profile=next(q for q in z['profiles'] if q['variant']==a.variant and q['mode']==a.mode)
    source=Path(profile['script']);frozen=a.packet/'frozen-current'
    assert sha(source)==profile['script_sha256']
    assert sha(frozen/'candidate.nes')==z['ROM_sha256']
    assert sha(frozen/'final_tmnt_items_native.lua')==z['fixture_sha256']
    rendered=source.read_text().splitlines()[0]
    assert '["hard"]='+('true'if a.mode=='hard'else'false')in rendered
    assert '["mode_value"]='+str(int(a.mode=='hard'))in rendered
    a.output.mkdir(parents=True,exist_ok=False)
    for ext in ['.nes','.dbg','.lbl','.map']:
        shutil.copy2(frozen/('candidate'+ext),a.output/('candidate'+ext))
    shutil.copy2(source,a.output/'run.lua')
    shutil.copy2(source.parent/'config.json',a.output/'config.json')
    shutil.copy2(frozen/'final_tmnt_items_native.lua',a.output/'final_tmnt_items_native.lua')
    with(a.output/'host.log').open('w') as stream:
        result=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),
            '--output',str(a.output),'--emulator',str(a.emulator),str(a.output/'run.lua'),
            str(a.output/'candidate.nes'),'--timeout',str(a.timeout),
            '--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros',
            '--option=--nes.randomizeCpuPpuAlignment=false',
            '--option=--nes.randomizeMapperPowerOnState=false'],stdout=stream,stderr=subprocess.STDOUT)
    f=a.output/'native-result.json'
    native=json.loads(f.read_text()) if f.exists() else {}
    receipt=dict(passed=result.returncode==0 and native.get('passed',False)and native.get('actual_mode_readback')==int(a.mode=='hard')and native.get('hard')==(a.mode=='hard'),goal_complete=False,
                 emulator_exit=result.returncode,ROM_sha256=z['ROM_sha256'],
                 identity=profile['identity'],variant=a.variant,mode=a.mode,
                 packet=str(a.packet),preparation_sha256=sha(a.packet/'preparation.json'),
                 source_ledger_sha256=z['source_ledger_sha256'],fixture_sha256=z['fixture_sha256'],
                 runner_sha256=sha(Path(__file__)),script_sha256=sha(a.output/'run.lua'),
                 emulator_sha256=sha(a.emulator),native=native,
                 first_failure=json.loads((a.output/'first-failure.json').read_text())
                    if(a.output/'first-failure.json').exists()else None,
                 scope='One actual native profile; all retained failures explicit. No campaign/full-roster completion claim.')
    (a.output/'proof.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(passed=receipt['passed'],identity=receipt['identity'],mode=a.mode,
                         updates=native.get('updates'),eligible_defeats=native.get('eligible_defeats'),
                         first_failure=receipt['first_failure'],output=str(a.output))))
    raise SystemExit(0 if receipt['passed']else 1)


if __name__=='__main__':main()
