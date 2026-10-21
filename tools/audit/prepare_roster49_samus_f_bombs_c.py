"""Time intrinsic bombs from actual approaching enemy distance and grounded pose."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    record=H/'preparation-c.json';assert not record.exists()
    old=H/'policy-b.lua';s=old.read_text()
    a="local phase,age='morph',0";assert s.count(a)==1;s=s.replace(a,a+'\nlocal started=false')
    a='local live=0;local active=0';assert s.count(a)==1;s=s.replace(a,a+';local nearest=9999')
    a='then live=live+1 end';assert s.count(a)==1;s=s.replace(a,'then live=live+1;nearest=math.min(nearest,x-c.x)end')
    a='b.b=c.poll%8<4';assert s.count(a)==1
    s=s.replace(a,"if not started and nearest<=46 and c.grounded then started=true end\n  b.b=started and c.grounded and c.poll%8<4")
    policy=H/'policy-c.lua';policy.write_text(s.replace('first-bombs-b.csv','first-bombs-c.csv'))
    parent=R/'build/roster-through-2-2/root49-f-samus-route-b-2-v0-mmc3';m=json.loads((parent/'manifest.json').read_text())
    assert m['result']['failure']=='death'and m['result']['frames']==8328
    pre=json.loads((H/'preparation-a.json').read_text());pre['policy_sha256']=sha(policy)
    (H/'preparation-c-run.json').write_text(json.dumps(pre,indent=2)+'\n')
    runner=(H/'run-b.py').read_text().replace('native-b.log','native-c.log').replace('native-result-b.json','native-result-c.json').replace('allocation-b.json','allocation-c.json').replace('preparation-b-run.json','preparation-c-run.json').replace('policy-b.lua','policy-c.lua').replace('root49-f-samus-route-b','root49-f-samus-route-c')
    a="total=workspace_bytes(R);size=sum(q.stat().st_size for q in H.rglob('*')if q.is_file())";assert runner.count(a)==1
    runner=runner.replace(a,"total=workspace_bytes(R);owned={q for q in H.rglob('*')if q.is_file()}\n    for p in(R/'build/roster-through-2-2').glob('root49-f-samus-*'):owned.update(q for q in p.rglob('*')if q.is_file())\n    owned.update(V.glob('smb-crossover-*-run-root49-f-samus-*.log'))\n    size=sum(q.stat().st_size for q in owned)")
    (H/'run-c.py').write_text(runner)
    record.write_text(json.dumps(dict(status='PREPARED_REAL_ENEMY_APPROACH_TIMED_GROUNDED_BOMBS',script_sha256=sha(__file__),
      parent_manifest_sha256=sha(parent/'manifest.json'),parent_bomb_trace_sha256=sha(parent/'first-bombs-b.csv'),policy_sha256=sha(policy),runner_sha256=sha(H/'run-c.py'),
      diagnosis='B bombs genuinely spawned and bomb-boosted Samus; early ground bombs exploded while first enemy was too far, following bombs spawned high during the boost. Enemyhealth remained lazyzero. Hold first bombs until actual46px approach, spawn only grounded; source58-update fuse/82-update expiry unchanged.',
      emulated_writes=False,source_changed=False,goal_complete=False),indent=2)+'\n')
    print('PREPARED',sha(record),flush=True)
if __name__=='__main__':main()
