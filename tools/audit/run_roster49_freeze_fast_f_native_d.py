"""Use unchanged lifecycle/protocol native fixtures with actual faster-F hooks."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-freeze-render-fast-f';E=V/'root49-ice-integrated-e'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    marker=H/'native-preparation-d.json';assert not marker.exists()
    leaf=json.loads((H/'leaf-review-c.json').read_text());assert leaf['status']=='PASS_EXACT_SINGLE_LEAF_OUTPUTS_ALL_ORDERED_WRITES_AND_LOWER_CYCLES'
    pre=json.loads((H/'preparation-b.json').read_text())
    for n,h in pre['source_hashes'].items():assert sha(H/'source'/n)==h,n
    (H/'source-catalog.json').write_text(json.dumps(pre['source_hashes'],indent=2)+'\n')
    specs=[('state','run_state_cm.py','state-core-cl.lua'),('protocol','run_protocol_cw.py','protocol-core-cw.lua')];adapters=[]
    for group,script,core in specs:
        q=H/core
        if q.exists():assert sha(q)==sha(E/core)
        else:q.write_bytes((E/core).read_bytes())
        code=(E/script).read_text();assert code.count('500000000')==2
        code=code.replace('500000000','300000000')
        p=H/script;p.write_text(code)
        adapters.append(dict(group=group,E_adapter_sha256=sha(E/script),F_adapter_sha256=sha(p),literal_core_sha256=sha(q),
          allowed_changes='Own __file__ binds actual F source/output; phase500MB becomes300MB. Original scenarios/assertions/core are literal.'))
    marker.write_text(json.dumps(dict(status='PREPARED_F_FOUR_LITERAL_NATIVE_GROUPS',script_sha256=sha(__file__),
      source_catalog_sha256=sha(H/'source-catalog.json'),leaf_review_sha256=sha(H/'leaf-review-c.json'),adapters=adapters,main_changed=False),indent=2)+'\n')
    results=[]
    for group,script,core in specs:
        for mp in ['mmc3','mmc5']:
            print('START',group,mp,flush=True)
            log=H/f'native-{group}-{mp}-d.log'
            with log.open('wb')as f:q=subprocess.run([sys.executable,str(H/script),mp],cwd=R,stdout=f,stderr=subprocess.STDOUT)
            results.append(dict(group=group,mapper=mp,exit=q.returncode,host_log_sha256=sha(log)))
            (H/'native-progress-d.json').write_text(json.dumps(dict(status='RUNNING'if len(results)<4 else'ALL_FOUR_F_NATIVE_GROUPS_TERMINAL',results=results),indent=2)+'\n')
            assert q.returncode==0,(group,mp,q.returncode)
            print('END',group,mp,flush=True)
    print('DONE',len(results),flush=True)
if __name__=='__main__':main()
