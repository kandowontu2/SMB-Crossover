"""Continue independent combat checks after the retained high-ID arena error."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
R=Path(__file__).resolve().parents[2]
H=R/'build/verification/agent49-menu-combat-root-w'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert sha(H/'freeze.json')=='ddbeb052c7cef4336c809ed11bec6e7eaafb819849ea74f70b3d5db8cf239fd0'
    original=H/'root-summary.json';negative=json.loads(original.read_text())
    assert negative['status']=='NEGATIVE_SELECTED_MENU_COMBAT_MATRIX'
    out=H/'root-nonhazards-summary.json';assert not out.exists()
    plan=json.loads((H/'plan.json').read_text())
    result=dict(status='RUNNING_NONHAZARD_MENU_COMBAT_MATRIX',cases=[],script_sha256=sha(Path(__file__)),original_negative_sha256=sha(original),plan_sha256=sha(H/'plan.json'),full_roster_route_claim=False,qualification='High-ID21 arena never entered ordinary body handler; original negative retained. All four hazard groups require a separately corrected setup and are excluded here.')
    def save():out.write_text(json.dumps(result,indent=2)+'\n')
    save()
    for case in plan['cases']:
        if case['group']=='hazards':continue
        name=case['case'];receipt=Path(case['binding_path']).parent/'root-native-receipt.json'
        if receipt.exists():
            assert json.loads(receipt.read_text())['status']=='PASS_BOUNDED_SEEDED_NATIVE_COMPONENT'
            result['cases'].append(dict(case=name,exit=0,receipt=str(receipt),receipt_sha256=sha(receipt),retained_prior_positive=True))
            save();continue
        log=H/(name+'-root-driver.log');assert not log.exists()
        t=time.monotonic()
        with log.open('wb')as f:
            p=subprocess.run([sys.executable,str(H/'run_root.py'),'--case',name,'--execute'],cwd=R,stdout=f,stderr=subprocess.STDOUT)
        result['cases'].append(dict(case=name,exit=p.returncode,elapsed_seconds=time.monotonic()-t,log_sha256=sha(log),receipt=str(receipt),receipt_sha256=sha(receipt)if receipt.exists()else None))
        save();print(name,'PASS'if p.returncode==0 else'FAIL',flush=True)
        if p.returncode:
            result['status']='NEGATIVE_NONHAZARD_MENU_COMBAT_MATRIX';save();return 1
    result['status']='PASS_NONHAZARD_MENU_COMBAT_MATRIX';save()
    print(result['status'],len(result['cases']),sha(out),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
