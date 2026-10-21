"""Adopt the source-bound strengthened Ice/passive fixture and execute both maps."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-current-f-samus-passives-bc'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=H/'adoption-e.json';assert not out.exists()
    p=json.loads((H/'preparation.json').read_text());fixture=R/'tests/samus-passives-202.lua'
    assert sha(fixture)==sha(H/'original-samus-passives-202.lua')==p['dependencies']['tests/samus-passives-202.lua']
    d=json.loads((H/'thaw-d-review.json').read_text());assert d['status']=='PASS_FIRST_FREEZE_LAZY_HEALTH_ACTUAL_THAW_DAMAGE_FROZEN_PLATFORM_AND_SCREW'
    for g in d['groups']:
        assert g['exit']==0
        for name,h in g['files'].items():assert sha(H/name)==h,name
    body=H/'thaw-d/passives.lua';assert sha(body)==d['body_sha256']
    s=body.read_text();needle="OUTPUT..'thaw-result.json'";assert s.count(needle)==1
    s=s.replace(needle,"OUTPUT..ROM_NAME..'-samus-thaw-result.json'")
    s='''-- Pinned2.02 Enemy.confirmedHitProj/checkAttackProps: first FREEZE returns
-- before takeDamage. Native health0 is a lazy75HP sentinel; an actual second
-- Ice hit must thaw and initialize/subtract40, leaving35HP. No outcome is seeded.
'''+s
    fixture.write_text(s)
    (H/'adoption-preparation-e.json').write_text(json.dumps(dict(script_sha256=sha(__file__),original_sha256=p['dependencies']['tests/samus-passives-202.lua'],private_validated_body_sha256=sha(body),adopted_sha256=sha(fixture),
      differences_from_private_D='Explanatory source comment and mapper-specific diagnostic filename only; assertions, inputs and authored setup are identical.',shared_runtime_changed=False),indent=2)+'\n')
    cp=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/manifest.json';c=json.loads(cp.read_text());groups=[]
    for mapper in ['mmc3','mmc5']:
        for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
        o=H/f'adopted-e-{mapper}';o.mkdir()
        q=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(o),str(fixture),str(cp.parent/f'smb-crossover-{mapper}.nes'),'--timeout','60'],cwd=R,capture_output=True,text=True)
        log=H/f'adopted-e-{mapper}-host.log';log.write_text(q.stdout+q.stderr)
        groups.append(dict(mapper=mapper,exit=q.returncode,host_log_sha256=sha(log),files={str(f.relative_to(H)):sha(f)for f in o.iterdir()if f.is_file()}))
    r=dict(status='PASS_ADOPTED_SOURCE_CORRECT_STRENGTHENED_SAMUS_PASSIVES_BOTH_F_MAPPERS'if all(g['exit']==0 for g in groups)else'RETAINED_ADOPTED_PASSIVE_FIXTURE_FAILURE',script_sha256=sha(__file__),adopted_fixture_sha256=sha(fixture),private_review_sha256=sha(H/'thaw-d-review.json'),preparation_sha256=sha(H/'adoption-preparation-e.json'),groups=groups,
      exact_proven_scope='Real controller first Ice freezes360 without damage; native lazy health stays0. Real second Ice thaws and leaves35HP. Original frozen immobility, native platform landing, no-injury and acquired Screw protection/defeat assertions pass.',
      limits=['Explicit Hard arena state/ownership setup; not natural acquisition or a full route.','Native platform/contact fixtures do not prove source bitmap/anchor/phase equivalence.','No full historical688/73 suite rerun or green claim.'],production_ROM_changed=False,goal_complete=False)
    out.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],sha(out),flush=True)
    return 0 if all(g['exit']==0 for g in groups)else 1
if __name__=='__main__':raise SystemExit(main())
