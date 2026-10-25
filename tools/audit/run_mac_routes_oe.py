"""Cold Little Mac clear/replay with his previously verified controller policy."""
from pathlib import Path
import argparse
import concurrent.futures
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--phase',choices=['discover','replay'],required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True);assert not(a.output/f'{a.phase}-results.json').exists()
    runner=ROOT/'tools/playthroughs/new_roster_run_nd.py';policy=ROOT/'tools/playthroughs/mac_easy_policy_nv.lua'
    assert sha(policy)=='010ed8dae921d160a98f4228fc496b92e21b0bff0f15e73cd93ee404e711838d'
    def run(mode):
        folder=a.output/f'{a.phase}-mac-{mode}-v1';discovery=a.output/f'discover-mac-{mode}-v1'
        command=[sys.executable,str(runner),'mac','--rom',str(a.rom.resolve()),'--output',str(folder.resolve()),
                 '--behavior',mode,'--policy',str(policy),'--frames','8000','--capture','1'if a.phase=='replay'else'12',
                 '--chr-commit','--timeout','90']
        if a.phase=='replay':command+=['--replay',str(discovery/'inputs.csv')]
        z=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);(a.output/f'{a.phase}-{mode}-host.log').write_text(z.stdout+z.stderr)
        manifest=json.loads((folder/'manifest.json').read_text())if(folder/'manifest.json').exists()else{}
        result=manifest.get('result',{});same={}
        if a.phase=='replay'and z.returncode==0:same={n:(folder/n).read_bytes()==(discovery/n).read_bytes()for n in ['inputs.csv','trace.csv']}
        passed=z.returncode==0 and result.get('cleared')and result.get('deaths')==0 and manifest.get('chr_commit',{}).get('passed')and all(same.values())
        return dict(identity='mac',mode=mode,passed=bool(passed),exit=z.returncode,frames=result.get('frames'),deaths=result.get('deaths'),
                    folder=str(folder.resolve()),exact_discovery_bytes=same,failure=result.get('failure'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:runs=list(pool.map(run,['easy','hard']))
    q=dict(passed=all(r['passed']for r in runs),ROM_sha256=sha(a.rom),phase=a.phase,runs=runs,controller_only=True,memory_writes=False,
           runner_sha256=sha(runner),policy_sha256=sha(policy),scope='Actual cold menus, zero-death1-1 and movable1-2. Separate physical-item, visual and whole-roster gates remain.')
    (a.output/f'{a.phase}-results.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))
    return 0 if q['passed']else 1


if __name__=='__main__':raise SystemExit(main())
