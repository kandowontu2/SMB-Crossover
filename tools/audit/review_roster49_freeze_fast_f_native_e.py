"""Reexecute fresh F lifecycle/protocol/ISR captures with original frozen assertions."""
from pathlib import Path
import hashlib,json,traceback
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-freeze-render-fast-f'
A=V/'agent49-samus-bill-arsenal-a';O=H/'native-review-e'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
COMMANDS=[('review_state_ct.py',"O=H/('state-cm-'+mp)",'state-cm-','state-lifecycle-protocol-review-ct.json'),
 ('review_protocol_cx.py',"O=H/('protocol-cw-'+mp)",'protocol-cw-','protocol-constructor-review-cx.json'),
 ('review_state_cq.py',"O=H/('state-'+tag+'-'+mp)",'state-cm-','state-caller-review-cq.json')]
def main():
    assert not O.exists();O.mkdir()
    p=json.loads((H/'native-progress-d.json').read_text());assert p['status']=='ALL_FOUR_F_NATIVE_GROUPS_TERMINAL'
    pre=json.loads((H/'preparation-b.json').read_text());br=json.loads((H/'build-review.json').read_text())
    for n,h in pre['source_hashes'].items():assert sha(H/'source'/n)==h,n
    for z in br['builds']:
        for q in z['artifacts'].values():assert sha(R/q['path'])==q['sha256']
    frozen=json.loads((A/'ice-state-freeze-dj/freeze.json').read_text());oldcat=json.loads(Path(frozen['receipts']['path']).read_text())
    native={}
    for group in ['state-cm','protocol-cw']:
        for mp in ['mmc3','mmc5']:
            q=H/(group+'-'+mp);assert json.loads((q/'host.json').read_text())==dict(exit=0,source_exact=True,rom_exact=True)
            for f in q.rglob('*'):
                if f.is_file():native[str(f.relative_to(H))]=dict(sha256=sha(f),bytes=f.stat().st_size)
    (O/'native-receipts.json').write_text(json.dumps(native,indent=2)+'\n')
    reports=[]
    try:
        for script,anchor,group,output in COMMANDS:
            original=A/script;assert sha(original)==oldcat[script]['sha256']
            code=original.read_text();assert code.count(anchor)==1
            code=code.replace(anchor,'O=Path('+repr(str(H))+')/('+repr(group)+'+mp)')
            target="H/'"+output+"'";assert code.count(target)==1
            code=code.replace(target,'Path('+repr(str(O/output))+')')
            q=O/script;q.write_text(code)
            print('START',script,flush=True)
            exec(compile(code,str(original),'exec'),dict(__file__=str(original),__name__='__main__'))
            r=json.loads((O/output).read_text());assert r['status'].startswith('PASS'),r['status']
            reports.append(dict(script=script,original_sha256=sha(original),adapter_sha256=sha(q),
              report=output,sha256=sha(O/output),status=r['status']))
            (O/'progress.json').write_text(json.dumps(dict(status='RUNNING',reports=reports),indent=2)+'\n')
            print('END',script,flush=True)
        for n,q in native.items():assert sha(H/n)==q['sha256']
        for n,h in pre['source_hashes'].items():assert sha(H/'source'/n)==h,n
        maincp=R/'build/checkpoints/roster-audit-v49-ice-over-sophia-e/manifest.json'
        for n,h in json.loads(maincp.read_text())['source_hashes'].items():assert sha(R/n)==h,n
        result=dict(status='PASS_F_ACTUAL_NATIVE_LIFECYCLE_OAM_NSF_AND_WHOLE_CALLER_ISR_REEXECUTION',
          script_sha256=sha(__file__),native_files=len(native),native_receipts_sha256=sha(O/'native-receipts.json'),
          build_review_sha256=sha(H/'build-review.json'),leaf_review_sha256=sha(H/'leaf-review-c.json'),
          reports=reports,main_changed=False,goal_complete=False,
          scope='Actual F hooks/images and literal original cases, models and assertions. Only native-data/output paths rebound. No masks/tolerance/flag or timing assertions weakened. Seeded components, no ordinary acquisition, full route or final media claim.')
        (O/'review.json').write_text(json.dumps(result,indent=2)+'\n');print('DONE',sha(O/'review.json'),flush=True)
    except Exception as ex:
        (O/'negative.json').write_text(json.dumps(dict(status='FAIL_RETAINED_NO_ADMISSION',error=repr(ex),traceback=traceback.format_exc(),completed=reports),indent=2)+'\n');raise
if __name__=='__main__':main()
