"""Execute one immutable prepared numeric-mode profile, sequential worker only."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prepared',type=Path,required=True)
    p.add_argument('--emulator',type=Path,required=True)
    p.add_argument('--timeout',type=int,default=180)
    a=p.parse_args();out=a.prepared
    assert not(out/'proof.json').exists(),'Never overwrite a prior execution receipt'
    z=json.loads((out/'preparation.json').read_text());cfg=json.loads((out/'config.json').read_text())
    assert sha(out/'candidate.nes')==z['ROM_sha256'] and sha(out/'run.lua')==z['script_sha256']
    assert type(cfg['hard']) is bool and cfg['mode_value']==int(cfg['hard'])==z['numeric_mode_requested']
    rendered=(out/'run.lua').read_text().splitlines()[0]
    assert '["hard"]='+('true'if cfg['hard']else'false')in rendered
    assert '["mode_value"]='+str(cfg['mode_value'])in rendered
    with(out/'host.log').open('w')as stream:
        r=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),
            '--output',str(out),'--emulator',str(a.emulator),str(out/'run.lua'),
            str(out/'candidate.nes'),'--timeout',str(a.timeout),
            '--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros',
            '--option=--nes.randomizeCpuPpuAlignment=false',
            '--option=--nes.randomizeMapperPowerOnState=false'],stdout=stream,stderr=subprocess.STDOUT)
    raw=out/('native-progressive.json'if z['suite']=='progression'else'native-abilities.json')
    n=json.loads(raw.read_text())if raw.exists()else{}
    z.update(passed=r.returncode==0 and n.get('passed',False)and n.get('actual_mode_readback')==cfg['mode_value']and n.get('hard')==cfg['hard'],
             status='native_finished',emulator_exit=r.returncode,emulator_sha256=sha(a.emulator),
             execution_runner_sha256=sha(Path(__file__)),native=n)
    (out/'proof.json').write_text(json.dumps(z,indent=2)+'\n')
    print(json.dumps(dict(passed=z['passed'],ROM_sha256=z['ROM_sha256'],family=z['family'],
                         suite=z['suite'],mode=z['mode'],actual_mode=n.get('actual_mode_readback'),
                         cases=len(n.get('cases',n.get('abilities',[]))),updates=n.get('updates'),
                         output=str(out))))
    raise SystemExit(0 if z['passed']else 1)


if __name__=='__main__':main()
