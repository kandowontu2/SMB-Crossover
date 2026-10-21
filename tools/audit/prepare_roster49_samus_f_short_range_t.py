"""Bring actual short-beam combat into its source-bounded practical range."""
from pathlib import Path
import csv,hashlib,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=H/'preparation-t.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-f-samus-route-s-2-v0-mmc3';m=json.loads((parent/'manifest.json').read_text());assert m.get('result')is None
    pose=next(z for z in csv.DictReader((parent/'trace.csv').open())if z['frame']=='26730');assert pose['state']=='0'and pose['y']=='176'and 2730<int(pose['x'])<2750
    lines=(parent/'inputs.csv').read_text().splitlines();prefix=H/'prefix-26730-t.csv';prefix.write_text('\n'.join(lines[:26731])+'\n')
    body=(H/'policy-r.lua').read_text();assert body.count('dx<=76')==1 and body.count('x-c.x<=78')==1
    body=body.replace('dx<=76','dx<=56').replace('x-c.x<=78','x-c.x<=58').replace('pipe-beams-r.csv','pipe-beams-t.csv')
    policy=H/'policy-t.lua';policy.write_text(body)
    pre=json.loads((H/'preparation-a.json').read_text());pre.update(policy_sha256=sha(policy),prefix_sha256=sha(prefix));(H/'preparation-t-run.json').write_text(json.dumps(pre,indent=2)+'\n')
    sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
    owned={q for q in H.rglob('*')if q.is_file()}
    for p in(R/'build/roster-through-2-2').glob('root49-f-samus-*'):owned.update(q for q in p.rglob('*')if q.is_file())
    owned.update(V.glob('smb-crossover-*-run-root49-f-samus-*.log'));size=sum(p.stat().st_size for p in owned);total=workspace_bytes(R)
    assert size+60000000+100000000<900000000 and total+60000000<70000000000
    allocation=dict(old_cap=800000000,new_cap=900000000,actual_phase_bytes=size,global_bytes=total,global_cap=70000000000,final_reserve=100000000,
      basis='Actual Samus discovery phase plus60MB next discovery,60MB independent proof and100MB reserve requires expansion beyond800MB. User already authorized raised storage with all lossless retained. Preserve all original phase/allocation receipts.')
    (H/'allocation-extension-t.json').write_text(json.dumps(allocation,indent=2)+'\n')
    runner=(H/'run-s.py').read_text()
    for a,b in [('native-s.log','native-t.log'),('native-result-s.json','native-result-t.json'),('allocation-s.json','allocation-t.json'),('preparation-s-run.json','preparation-t-run.json'),('policy-s.lua','policy-t.lua'),('prefix-25380-s.csv','prefix-26730-t.csv'),('root49-f-samus-route-s','root49-f-samus-route-t'),('800000000','900000000')]:runner=runner.replace(a,b)
    (H/'run-t.py').write_text(runner)
    source=R/'reference/crossover2/extracted/scripts/com/smbc/projectiles/SamusShot.as'
    report=dict(status='PREPARED_ACTUAL_SHORT_BEAM_RANGE_CONTROLLER',script_sha256=sha(__file__),parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),policy_sha256=sha(policy),runner_sha256=sha(H/'run-t.py'),actual_prefix_pose=pose,allocation=allocation,
      mechanism='S reaches fourth plant at2824 but starts stationary combat from2748..2750,74px away. It never initializes targetHP in899 polls. Pinned2.02 SamusShot SHORT_BEAM_DISTANCE100 and X_OFFSET25 use half-size NES coordinates. Prior actual Q56px stationary beam succeeds. T approaches to48..56px before stopping; source2000/600 controller bounds unchanged.',
      source_SamusShot_sha256=sha(source),runtime_changed=False,emulated_writes=False,state_loads=False,goal_complete=False)
    out.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],sha(out),size,total,flush=True)
if __name__=='__main__':main()
