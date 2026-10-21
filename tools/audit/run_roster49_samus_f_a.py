"""Execute the bounded controller-only F Samus candidate with its own allocation."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=H/'native-a.log';assert not out.exists()
    p=json.loads((H/'preparation-a.json').read_text());cp=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/manifest.json'
    assert sha(cp)==p['checkpoint_sha256'];c=json.loads(cp.read_text())
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    assert sha(H/'policy-a.lua')==p['policy_sha256']and sha(H/'observer-a.lua')==p['observer_sha256']
    assert sha(H/'prefix-8110-a.csv')==p['prefix_sha256']
    sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
    total=workspace_bytes(R);size=sum(q.stat().st_size for q in H.rglob('*')if q.is_file())
    assert size+60000000+100000000<500000000 and total+60000000<70000000000,(size,total)
    (H/'allocation-a.json').write_text(json.dumps(dict(phase=size,phase_cap=500000000,reserve=100000000,global_bytes=total,global_cap=70000000000))+'\n')
    args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','2','--mapper','mmc3',
      '--rom',str(cp.parent/'smb-crossover-mmc3.nes'),'--tag','root49-f-samus-route-a',
      '--policy',str(H/'policy-a.lua'),'--prefix',str(H/'prefix-8110-a.csv'),
      '--frames','45000','--timeout','600','--workspace-cap-gb','70']
    with out.open('wb')as log:q=subprocess.run(args,cwd=R,stdout=log,stderr=subprocess.STDOUT)
    run=R/'build/roster-through-2-2/root49-f-samus-route-a-2-v0-mmc3'
    m=json.loads((run/'manifest.json').read_text())
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    (H/'native-result-a.json').write_text(json.dumps(dict(exit=q.returncode,host_log_sha256=sha(out),manifest_sha256=sha(run/'manifest.json'),result=m.get('result'),
      full_clear=m.get('verified_through_2_2'),goal_complete=False),indent=2)+'\n')
    print(json.dumps(dict(exit=q.returncode,result=m.get('result'))),flush=True)
    return q.returncode
if __name__=='__main__':raise SystemExit(main())
