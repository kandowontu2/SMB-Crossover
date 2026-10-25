"""Re-run existing meaningful source-audio fixtures on the integrated ROM."""
from pathlib import Path
import argparse
import concurrent.futures
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
OB=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-native-audio-ob')
CASES=['samus-audio-effects','megaman-audio-effects','bass-water-audio',
       'bill-audio-isolation','link-audio-isolation','simon-audio-isolation','samus-audio-cold-ob']


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    def run(name):
        d=a.output/name;d.mkdir();fixture=ROOT/f'tests/{name}.lua'
        prefix=''if name=='samus-audio-cold-ob'else 'dofile('+json.dumps((ROOT/'tests/menu-bootstrap.lua').as_posix())+')\n'
        script=d/'run.lua';script.write_text(prefix+fixture.read_text())
        if name.endswith('audio-isolation'):
            (d/'roster-audio-isolation.lua').write_bytes((ROOT/'tests/roster-audio-isolation.lua').read_bytes())
        z=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(d),str(script),str(a.rom),
            '--timeout','60','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false',
            '--option=--nes.randomizeMapperPowerOnState=false'],capture_output=True,text=True)
        (d/'host.log').write_text(z.stdout+z.stderr)
        q=dict(passed=z.returncode==0,exit=z.returncode,fixture_sha256=sha(fixture),bound_script_sha256=sha(script),host_log_sha256=sha(d/'host.log'))
        if name=='samus-audio-cold-ob'and z.returncode==0:
            before=OB/'samus-native-baseline-v1/audio.csv'
            q['all_4096_native_audio_rows_exact']=before.read_bytes()==(d/'audio.csv').read_bytes()
            q['baseline_audio_csv_sha256']=sha(before);q['audio_csv_sha256']=sha(d/'audio.csv')
            q['passed']&=q['all_4096_native_audio_rows_exact']
            q['native_result']=json.loads((d/'result.json').read_text())
        return name,q
    with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:cases=dict(pool.map(run,CASES))
    q=dict(passed=all(v['passed']for v in cases.values()),ROM_sha256=sha(a.rom),cases=cases,
           bootstrap_sha256=sha(ROOT/'tests/menu-bootstrap.lua'),shared_isolation_sha256=sha(ROOT/'tests/roster-audio-isolation.lua'),
           scope='Existing source-specific beam/charge/Water Shield DMA and cleanup fixtures, Bill/Link/Simon live-state isolation, and a cold Samus4096-call original-state/hardware differential. Explicit component arrangements; separate from complete character campaigns.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2));return 0 if q['passed']else 1


if __name__=='__main__':raise SystemExit(main())
