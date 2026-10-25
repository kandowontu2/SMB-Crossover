"""Scoped native regressions of the private immediate HUD candidate."""
from pathlib import Path
import concurrent.futures
import argparse
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
O = R / 'build/verification/hud-tail-regressions-ew'
C = R / 'build/verification/hud-tail-dz/source'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    global O, C
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,default=C)
    parser.add_argument('--tag',default='hud-tail-regressions-ew')
    parser.add_argument('--tests',default='cheats-menu,character-select,score-popup-location,terrain-coin-publication,firebar-budget-fairness,cannon-cooldown,bill-flagpole-full,bass-special-enemies,megaman-projectiles-overload')
    args=parser.parse_args()
    O=R/'build/verification'/args.tag
    C=args.candidate
    assert not O.exists()
    O.mkdir()
    names=tuple(args.tests.split(','))
    roms = {m:sha(C / f'build/smb-crossover-{m}.nes') for m in ('mmc3','mmc5')}
    fixtures = {n:sha(R / f'tests/{n}.lua') for n in names}

    def run(pair):
        mapper, name = pair
        folder = O / f'{mapper}-{name}'
        folder.mkdir()
        command = [sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(folder),
                   str(R/f'tests/{name}.lua'),str(C/f'build/smb-crossover-{mapper}.nes'),'--timeout','90']
        with (folder/'host.log').open('wb') as log:
            result = subprocess.run(command,cwd=R,stdout=log,stderr=subprocess.STDOUT)
        print(mapper,name,result.returncode,flush=True)
        return dict(mapper=mapper,test=name,passed=result.returncode==0,exit=result.returncode,
                    ROM_sha256=roms[mapper],log_sha256=sha(folder/f'smb-crossover-{mapper}-{name}.log'),fixture_sha256=fixtures[name])

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(run,[(m,n) for m in roms for n in names]))
    assert fixtures == {n:sha(R / f'tests/{n}.lua') for n in names}
    report = dict(passed=all(z['passed'] for z in results),results=results,ROMs=roms,goal_complete=False)
    (O/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    assert report['passed']


if __name__ == '__main__':
    main()
