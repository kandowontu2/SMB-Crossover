"""Rebind frozen literal fixtures to actual composed E images and isolated logs."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';A=V/'agent49-samus-bill-arsenal-a';H=V/'root49-ice-integrated-e'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SPECS=[('cleanup','run_cleanup_dd.py','cleanup-core-dc.lua'),('state','run_state_cm.py','state-core-cl.lua'),('protocol','run_protocol_cw.py','protocol-core-cw.lua')]
GUARD='''def guard(label,reserve=30000000):
 sys.path.insert(0,str(R/'tools/playthroughs'))
 from roster_run import workspace_bytes
 total=workspace_bytes(R);size=sum(p.stat().st_size for p in H.rglob('*')if p.is_file())
 assert total+reserve<70000000000 and size+reserve+50000000<500000000,(label,total,size)
 (H/('budget-'+label+'.json')).write_text(json.dumps(dict(label=label,global_bytes=total,phase_bytes=size,phase_cap=500000000,final_reserve=50000000))+'\\n')
'''
DRIVER='''sys.path.insert(0,str(R/'tools'))
from types import SimpleNamespace
original_driver=R/'tools/run_mesen.py'
driver_text=original_driver.read_text();anchor="    output = ROOT / 'build/verification'\\n"
assert driver_text.count(anchor)==1
driver_text=driver_text.replace(anchor,'    output = ISOLATED_OUTPUT\\n')
driver_ns=dict(__file__=str(original_driver),__name__='_root_E_isolated',ISOLATED_OUTPUT=O/'runner-log')
exec(compile(driver_text,str(original_driver),'exec'),driver_ns)
run_mesen=SimpleNamespace(run=driver_ns['run'])'''
def main():
    marker=H/'native-preparation-ay.json';assert not marker.exists()
    b=json.loads((H/'build-review.json').read_text());assert b['status']=='PASS_FOUR_PRIVATE_BUILDS_EXACT_OWNED_BINARY_PATCH_OVER_D'
    f=json.loads((A/'ice-state-freeze-dj/freeze.json').read_text());cat=json.loads(Path(f['receipts']['path']).read_text())
    pre=json.loads((H/'preparation.json').read_text());(H/'source-catalog.json').write_text(json.dumps(pre['source_hashes'],indent=2)+'\n')
    changes=[]
    for group,script,core in SPECS:
        assert sha(A/script)==cat[script]['sha256']and sha(A/core)==cat[core]['sha256']
        shutil_source=A/core;target=H/core;target.write_bytes(shutil_source.read_bytes())
        text=(A/script).read_text();assert text.count('from storage_cg import guard')==1
        text=text.replace('from storage_cg import guard',GUARD)
        for token in['source-cy','source-ci']:text=text.replace("H/'"+token+"'","H/'source'")
        text=text.replace('source-catalog-cy.json','source-catalog.json').replace('source-catalog-ci.json','source-catalog.json')
        anchor="sys.path.insert(0,str(R/'tools'));import run_mesen";assert text.count(anchor)==1
        text=text.replace(anchor,DRIVER)
        anchor="R/'build/verification'/f'";assert text.count(anchor)==1
        text=text.replace(anchor,"O/'runner-log'/f'")
        adapter=H/script;compile(text,str(adapter),'exec');adapter.write_text(text)
        changes.append(dict(group=group,script=script,original_sha256=sha(A/script),adapter_sha256=sha(adapter),literal_core_sha256=sha(target)))
    marker.write_text(json.dumps(dict(status='PREPARED_ACTUAL_E_DYNAMIC_IMAGE_HOOKS_LITERAL_CORES',adapters=changes,
      source_catalog_sha256=sha(H/'source-catalog.json'),main_changed=False,
      allowed_adapter_changes=['actual E source/catalog/output binding','independent phase budget guard','isolated native driver logs'],goal_complete=False),indent=2)+'\n')
    results=[]
    for group,script,core in SPECS:
        for mp in['mmc3','mmc5']:
            print('START',group,mp,flush=True)
            with(H/f'native-{group}-{mp}-ay.log').open('wb')as log:run=subprocess.run([sys.executable,str(H/script),mp],cwd=R,stdout=log,stderr=subprocess.STDOUT)
            assert run.returncode==0,(group,mp,run.returncode)
            results.append(dict(group=group,mapper=mp,exit=run.returncode,host_log_sha256=sha(H/f'native-{group}-{mp}-ay.log')))
            (H/'native-progress-ay.json').write_text(json.dumps(dict(status='RUNNING'if len(results)<6 else'ALL_SIX_NATIVE_GROUPS_TERMINAL',results=results),indent=2)+'\n')
            print('END',group,mp,flush=True)
    print('DONE',len(results),flush=True)
if __name__=='__main__':main()
