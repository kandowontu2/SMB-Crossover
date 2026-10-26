"""Launch one explicitly frozen cold-menu observation, at most once."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('role',choices=['baseline','candidate']);a=p.parse_args()
    out=D/'root-chip-native-audio-v2'/a.role
    assert not (out/'launch-started.json').exists()
    prep=json.loads((out/'preparation.json').read_text())
    assert prep['candidate']==(a.role=='candidate') and prep['bounded_wall_frames']==1300
    assert sha(out/'manifest.json')==prep['manifest_sha256']
    manifest=json.loads((out/'manifest.json').read_text())
    for name,digest in manifest.items():assert sha(name)==digest,name
    rom=D/'root-chip-native-adapter-v5/candidate.nes' if prep['candidate'] else ROOT/'build/smb-crossover-mmc5-expanded.nes'
    assert sha(rom)==prep['ROM_sha256']
    marker=dict(preparation_sha256=sha(out/'preparation.json'),runner_sha256=sha(__file__),role=a.role)
    (out/'launch-started.json').write_text(json.dumps(marker,indent=2)+'\n')
    cmd=[sys.executable,'-B',str(ROOT/'tools/audit/run_mesen_isolated.py'),
         '--output',str(out),'--emulator',prep['emulator'],str(out/'run.lua'),str(rom),'--timeout','180',
         '--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros',
         '--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false',
         '--option=--nes.removeSpriteLimit=false']
    with (out/'host.log').open('w')as f:
        proc=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    result=marker|dict(exit=proc.returncode,ROM_sha256=prep['ROM_sha256'],bounded_launches=1,retries=0)
    for name in ['audio-native.json','ownership-guards.json']:
        if (out/name).exists():result[name]=json.loads((out/name).read_text())
    result['passed']=proc.returncode==0 and all(result.get(name,{}).get('passed')for name in ['audio-native.json','ownership-guards.json'])
    result['settings_unchanged']=all(sha(path)==digest for path,digest in manifest.items()if Path(path).name=='settings.json')
    assert result['settings_unchanged']
    (out/'launch.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
    raise SystemExit(0 if result['passed'] else 1)


if __name__=='__main__':main()
