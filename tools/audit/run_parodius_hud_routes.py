"""Run existing qualified ship controllers on the graphical-HUD candidate."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
from check_tmnt_render_oa import load, address, location
from observe_chip_committed_write import lua

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--archive', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    out = args.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(exist_ok=False)
    d = args.archive.resolve()
    driver = d / 'mmc3-ship-lives-v25/native-routes-v1/bound-mmc3-runner.py'
    sources = json.loads((d/'native-probes-qa-v2/full-roster-aggregate-v1/proof.json').read_text())
    original = (d/'mmc3-static-call-v37/full-roster-v1/native-guard.lua').read_text()
    b = load(args.rom)
    names = ['OperMode','OperMode_Task','GameEngineSubroutine','WorldNumber','LevelNumber',
             'Player_X_Position','Player_PageLoc','Player_Y_Position','ScreenLeft_X_Pos','ScreenLeft_PageLoc']
    delta = int(b['syms']['GameLoop']['size'],0)-1
    at = location(b,'GameLoop')+delta
    assert b['raw'][at] == 0x60
    hook = dict(address=address(b,'GameLoop')+delta, physical_bank=(at-16)//8192,
                bytes=list(b['raw'][at:at+8]))
    guard = out/'native-guard.lua'
    guard.write_text('OUTPUT=ROSTER_CONFIG.out\nMOTION_RAM='+lua({n:address(b,n)for n in names})
                     +'\nMOTION_HOOK='+lua(hook)+'\n'
                     +original[original.index('local checks,maxWorld,maxCamera='):])
    report = dict(passed=False, complete=False, goal_complete=False, ROM_sha256=sha(args.rom),
                  driver_sha256=sha(driver), runs=[],
                  scope='Fresh ordinary-controller full1-1 ship routes with unchanged qualified policies. Native actual body-CHR, OAM/source render observer, audio/scroll audit and completed-loop world<=8/camera0..4. Actual1-2 entry/continued movement covers the scene transition. PPU HUD pixels/cursors are separately verified in native UI components. No source-identical audio/every-upgrade/all-roster release claim.')
    for name in ['octopus','twinbee','pentarou']:
        row = next(r for r in sources['runs']if r['identity']==name)
        source = Path(row['discovery']).parent
        policy = out/(name+'-policy.lua')
        policy.write_text('dofile('+lua(guard.as_posix())+')\n'+(source/'policy.lua').read_text())
        folder = out/(name+'-'+row['mode'])
        with (out/(name+'-host.log')).open('w') as log:
            result = subprocess.run([sys.executable,str(driver),name,'--rom',str(args.rom.resolve()),
                                     '--output',str(folder),'--mapper','mmc5','--behavior',row['mode'],
                                     '--frames','16000','--capture','12','--policy',str(policy),
                                     '--chr-commit','--parodius-render','--timeout','240'],
                                    cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        manifest=json.loads((folder/'manifest.json').read_text())
        motion=json.loads((folder/'completed-loop-motion.json').read_text()) if(folder/'completed-loop-motion.json').exists()else{}
        native=manifest.get('result')or{}
        entry=dict(identity=name,mode=row['mode'],folder=str(folder),exit=result.returncode,
                   result=native,motion=motion,manifest_sha256=sha(folder/'manifest.json'),
                   source_policy_sha256=sha(source/'policy.lua'),
                   passed=bool(result.returncode==0 and native.get('cleared')and native.get('deaths')==0
                               and motion.get('passed')and manifest.get('chr_commit',{}).get('passed')))
        report['runs'].append(entry)
        (out/'progress.json').write_text(json.dumps(report,indent=2))
        print(json.dumps(entry),flush=True)
    report.update(complete=True,passed=all(r['passed']for r in report['runs']))
    (out/'proof.json').write_text(json.dumps(report,indent=2))
    raise SystemExit(0 if report['passed']else 1)


if __name__=='__main__':
    main()
