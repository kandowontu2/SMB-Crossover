"""Compare old/new non-Meta rotor behavior at actual native draw boundaries."""
from pathlib import Path
import argparse
import csv
import hashlib
import importlib.util
import json

ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--before',type=Path,required=True)
    p.add_argument('--after',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    spec=importlib.util.spec_from_file_location('rotor_mesen',ROOT/'tools/run_mesen.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    fixture=ROOT/'tests/meta-rotor-differential.lua';report={}
    for name,slot,char in [('bill',3,3),('kirby',12,13)]:
        records={}
        for label,rom in [('before',a.before.resolve()),('after',a.after.resolve())]:
            d=out/f'{name}-{label}';d.mkdir();script=d/'rotor.lua'
            script.write_text(f'ROTOR_SLOT={slot}\nROTOR_CHARACTER={char}\n'+fixture.read_text())
            runner.ROOT=d
            code=runner.run(script,rom,timeout=60,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
            assert code==0,(name,label,'Native fixture failed')
            rows=list(csv.DictReader((d/'build/verification/rotor.csv').open()))
            assert len(rows)==2016
            records[label]=rows
        assert records['before']==records['after'],(name,'Non-Meta rotor changed')
        report[name]=dict(cases=2016,identical=True)
    proof=dict(passed=True,before_sha256=sha(a.before),after_sha256=sha(a.after),fixture_sha256=sha(fixture),
               cases=report,total_native_draws=8064,
               scope='Cold controller Bill/ordinary Kirby entry. Two existing rotor counters explicitly seeded at real DrawAll entry; native old/new post-selector bytes compared for all2016legal used/front pairs per identity. Actors/OAM/CHR/code/CPU untouched; not a campaign/performance pass.')
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))


if __name__=='__main__':main()
