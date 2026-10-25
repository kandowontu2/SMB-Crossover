"""One native worker qualifies the combined reported-contact/pause candidate."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
ARCHIVE=Path('C:/Users/kando/Videos/SMB Crossover Archive')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);rom=a.rom.resolve();digest=sha(rom)
    report=dict(passed=False,complete=False,ROM_sha256=digest,jobs=[],routes=[],goal_complete=False,native_workers=1)
    def save():(a.output/'progress.json').write_text(json.dumps(report,indent=2)+'\n')
    def invoke(key,args):
        assert sha(rom)==digest
        with (a.output/(key+'.log')).open('w') as log:z=subprocess.run([sys.executable,*map(str,args)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        report['jobs'].append(dict(name=key,exit=z.returncode));save();print(key,z.returncode,flush=True)
        return z.returncode
    save()
    invoke('contacts',[ROOT/'tools/audit/run_reported_contacts_pp.py','--rom',rom,'--output',a.output/'contacts'])
    invoke('pause',[ROOT/'tools/audit/run_zelda_pause_pq.py','--rom',rom,'--output',a.output/'pause'])
    invoke('entries',[ROOT/'tools/audit/check_full_roster_entry.py','--complete','--rom',rom,'--output',a.output/'entries'])
    driver=ARCHIVE/'2026-10-24-roster-pe/matrix-v1/bound-runner.py'
    assert sha(driver)=='d6ab9cc1e938923797525704cf6d0e99e16fda6f007b98da1024cb167f00f167'
    # Prioritize the previously failing scrolling path before other routes.
    for name in ['zelda2','kirby','meta','mike','sypha']:
        policy=ARCHIVE/('2026-10-24-roster-pg/controls-v2/policy.lua' if name=='zelda2' else '2026-10-24-roster-pe/policy-v1/policy.lua')
        for mode in ['easy','hard']:
            key=name+'-'+mode;folder=a.output/('discover-'+key)
            code=invoke('discover-'+key,[driver,name,'--rom',rom,'--output',folder,'--behavior',mode,
                '--frames','10000','--capture','12','--chr-commit','--policy',policy,'--timeout','180'])
            row=dict(identity=name,mode=mode,discovery_exit=code,folder=str(folder),policy_sha256=sha(policy),passed=False)
            m=json.loads((folder/'manifest.json').read_text()) if (folder/'manifest.json').exists() else {}
            row.update(frames=m.get('result',{}).get('frames'),failure=m.get('result',{}).get('failure'))
            if code==0 and m.get('result',{}).get('cleared') and m['result'].get('deaths')==0:
                batch=a.output/('replay-'+key)
                index=a.output/('discovery-index-'+key+'.json')
                index.write_text(json.dumps(dict(ROM_sha256=digest,phase='discover',runs=[dict(
                    identity=name,mode=mode,passed=True,folder=str(folder),manifest_sha256=sha(folder/'manifest.json'))]),indent=2)+'\n')
                rc=invoke('replay-'+key,[ROOT/'tools/audit/replay_roster_pf.py','--rom',rom,
                    '--output',batch,'--discoveries',index])
                row.update(replay_exit=rc,replay_folder=str(batch),passed=rc==0)
            report['routes'].append(row);save()
    report.update(complete=True,passed=all(j['exit']==0 for j in report['jobs'])and all(q['passed']for q in report['routes']))
    save();print(json.dumps(dict(complete=True,passed=report['passed'],routes=len(report['routes']))),flush=True)
    return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
