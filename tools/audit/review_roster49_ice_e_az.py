"""Review actual composed-E native captures with the frozen instruction oracles."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
A=V/'agent49-samus-bill-arsenal-a';E=V/'root49-ice-integrated-e';O=E/'root-review-az'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
COMMANDS=[('review_cleanup_df.py',"O=H/('cleanup-dd-'+mp)",'cleanup-dd-', 'cleanup-review-df.json'),
 ('review_state_ct.py',"O=H/('state-cm-'+mp)",'state-cm-', 'state-lifecycle-protocol-review-ct.json'),
 ('review_protocol_cx.py',"O=H/('protocol-cw-'+mp)",'protocol-cw-', 'protocol-constructor-review-cx.json'),
 ('review_state_cq.py',"O=H/('state-'+tag+'-'+mp)",'state-cm-', 'state-caller-review-cq.json')]

def exact_source(pre):
    for n,h in pre['source_hashes'].items():assert sha(E/'source'/n)==h,n
    for n,h in pre['generated11'].items():assert sha(E/'source/build/generated'/n)==h,n
    cp=R/'build/checkpoints/roster-audit-v49-sophia-head-axis-d/manifest.json'
    for n,h in json.loads(cp.read_text())['source_hashes'].items():assert sha(R/n)==h,('main changed',n)

def main():
    assert not O.exists();O.mkdir()
    pre=json.loads((E/'preparation.json').read_text());exact_source(pre)
    br=json.loads((E/'build-review.json').read_text())
    assert br['status']=='PASS_FOUR_PRIVATE_BUILDS_EXACT_OWNED_BINARY_PATCH_OVER_D'
    for b in br['builds']:
        for z in b['artifacts'].values():assert sha(R/z['path'])==z['sha256']
    nr=json.loads((E/'native-progress-ay.json').read_text());assert nr['status']=='ALL_SIX_NATIVE_GROUPS_TERMINAL'
    f=json.loads((A/'ice-state-freeze-dj/freeze.json').read_text())
    receipts=json.loads(Path(f['receipts']['path']).read_text())
    for n,z in receipts.items():assert sha(A/n)==z['sha256'],n
    native={}
    for group in ['cleanup-dd','state-cm','protocol-cw']:
        for mp in ['mmc3','mmc5']:
            q=E/(group+'-'+mp);host=json.loads((q/'host.json').read_text())
            assert host==dict(exit=0,source_exact=True,rom_exact=True),(q,host)
            for p in q.rglob('*'):
                if p.is_file():native[str(p.relative_to(E))]=dict(sha256=sha(p),bytes=p.stat().st_size)
    (O/'native-receipts.json').write_text(json.dumps(native,indent=2)+'\n')
    done=[]
    try:
        for script,anchor,group,output in COMMANDS:
            p=A/script;assert sha(p)==receipts[script]['sha256'],script
            code=p.read_text();assert code.count(anchor)==1,(script,anchor)
            code=code.replace(anchor,'O=Path('+repr(str(E))+')/('+repr(group)+'+mp)')
            target="H/'"+output+"'";assert code.count(target)==1,(script,target)
            code=code.replace(target,'Path('+repr(str(O/output))+')')
            adapter=O/script;adapter.write_text(code)
            print('START',script,flush=True)
            # The original __file__ retains original helper modules and source
            # oracles; only the actual native data and report paths are rebound.
            exec(compile(code,str(p),'exec'),dict(__file__=str(p),__name__='__main__'))
            r=json.loads((O/output).read_text());assert r['status'].startswith('PASS'),r['status']
            done.append(dict(script=script,original_sha256=sha(p),adapter_sha256=sha(adapter),
              report=output,report_sha256=sha(O/output),status=r['status']))
            (O/'progress.json').write_text(json.dumps(dict(status='RUNNING',reports=done),indent=2)+'\n')
            print('END',script,flush=True)
        for n,z in native.items():assert sha(E/n)==z['sha256'],n
        for n,z in receipts.items():assert sha(A/n)==z['sha256'],n
        exact_source(pre)
        sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
        total=workspace_bytes(R);size=sum(p.stat().st_size for p in E.rglob('*')if p.is_file())
        assert total<70000000000 and size+50000000<500000000,(total,size)
        report=dict(status='PASS_ACTUAL_COMPOSED_E_NATIVE_INSTRUCTION_LIFECYCLE_PROTOCOL_REVIEWS',
          script_sha256=sha(__file__),build_review_sha256=sha(E/'build-review.json'),
          native_preparation_sha256=sha(E/'native-preparation-ay.json'),
          native_receipts_sha256=sha(O/'native-receipts.json'),native_files=len(native),reports=done,
          interpretation='Actual composed E captures; frozen original assertions, instruction models and source oracles. No assertion, timing tolerance, RAM, flags, stack, mapper or ordered-write mask added.',
          workspace_bytes=total,phase_bytes=size,phase_cap=500000000,reserve=50000000,
          main_changed=False,goal_complete=False,
          limits='Seeded component checks, not natural acquisition/all-arsenal/full-route/final-movie proof. Existing route proofs remain scoped to their actual source images.')
        (O/'review.json').write_text(json.dumps(report,indent=2)+'\n')
        print('DONE',sha(O/'review.json'),flush=True)
    except Exception as ex:
        (O/'negative.json').write_text(json.dumps(dict(status='FAIL_RETAINED_NO_ADOPTION',
          error=repr(ex),traceback=traceback.format_exc(),completed=done),indent=2)+'\n')
        raise
if __name__=='__main__':main()
