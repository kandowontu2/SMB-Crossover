"""Run the already bound focused menu contact matrix, preserving every result."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
R=Path(__file__).resolve().parents[2]
H=R/'build/verification/agent49-menu-combat-root-w'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert sha(H/'freeze.json')=='ddbeb052c7cef4336c809ed11bec6e7eaafb819849ea74f70b3d5db8cf239fd0'
    out=H/'root-summary.json';assert not out.exists()
    plan=json.loads((H/'plan.json').read_text())
    result=dict(status='RUNNING_SELECTED_MENU_COMBAT_MATRIX',cases=[],script_sha256=sha(Path(__file__)),plan_sha256=sha(H/'plan.json'),full_roster_route_claim=False)
    def save():out.write_text(json.dumps(result,indent=2)+'\n')
    save()
    for case in plan['cases']:
        name=case['case'];log=H/(name+'-root-driver.log');assert not log.exists()
        t=time.monotonic()
        with log.open('wb')as f:
            p=subprocess.run([sys.executable,str(H/'run_root.py'),'--case',name,'--execute'],cwd=R,stdout=f,stderr=subprocess.STDOUT)
        receipt=Path(case['binding_path']).parent/'root-native-receipt.json'
        result['cases'].append(dict(case=name,exit=p.returncode,elapsed_seconds=time.monotonic()-t,log_sha256=sha(log),receipt=str(receipt),receipt_sha256=sha(receipt)if receipt.exists()else None))
        save();print(name,'PASS'if p.returncode==0 else'FAIL',flush=True)
        if p.returncode:
            result['status']='NEGATIVE_SELECTED_MENU_COMBAT_MATRIX';save();return 1
    result['status']='PASS_SELECTED_MENU_COMBAT_MATRIX';save()
    print(result['status'],len(result['cases']),sha(out),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
