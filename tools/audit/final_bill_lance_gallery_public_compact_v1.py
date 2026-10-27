"""Keep the9MB native receipt external; publish its exact binding and outcome summary."""
from pathlib import Path
import argparse,json,shutil
from final_bill_lance_hard_gallery_source_v1 import D,ROOT,SHA,sha,put


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=False)
    prior=ROOT/'docs/qa/checkpoints/2026-10-26/bill-lance-hard-native-final-v1';old=json.loads((prior/'manifest.json').read_text());rows=[]
    for row in old['payloads']:
        f=prior/row['path'];assert sha(f)==row['sha256']
        if row['path']=='Lance-original-native-PASS.json':continue
        shutil.copyfile(f,a.output/row['path']);rows.append(row)
    native=D/'final-bill-lance-hard-gallery-ready-v5/profiles/lance-hard/native/proof.json';n=json.loads(native.read_text())
    assert n['passed']and sha(native)=='afc53f44b536ec8d9521f698237be5c22c9dd5e8f8352926cd32dd318f2df60b'
    name='Lance-original-native-PASS-external-summary.json'
    summary={k:v for k,v in n.items()if k not in ['analysis','bindings']}
    summary.update(analysis_passed=n['analysis']['passed'],analysis_errors=n['analysis']['errors'],
        original_receipt=dict(path=str(native),sha256=sha(native),bytes=native.stat().st_size),
        scope='Compact extracted summary only. Original entire9MB proof remains external byte-exact; actual per-case outcomes/reparse and raw bindings accompany this checkpoint.')
    put(a.output/name,summary);rows.append(dict(path=name,source=str(native)+' [explicit extraction, not byte copy]',sha256=sha(a.output/name),bytes=(a.output/name).stat().st_size))
    owned=[Path(ROOT/z['path'])for z in old['stable_owned_files']]+[Path(__file__)]
    (a.output/'OWNED-FILES.txt').write_text('\n'.join(str(f.relative_to(ROOT)).replace('\\','/')for f in owned)+'\n'+str(a.output.relative_to(ROOT)).replace('\\','/')+'/\n',encoding='utf-8')
    (a.output/'README.txt').write_text((prior/'README.txt').read_text()+'\nCompaction: previous generated public-v1 duplicated the original9MB host receipt; that unpublished copy is retained but excluded from this Git-ready directory. This v2 retains exact external path/hash/size and an explicitly extracted summary. Source/native/first-FALSE receipts unchanged.\n',encoding='utf-8')
    put(a.output/'REVIEW-FILES.json',dict(native_receipt='Lance-original-native-PASS-external-summary.json',actual_outcomes='Lance-outcomes-and-reparse.json',visual=['Lance-whole-frame-review-1.png','Lance-whole-frame-review-2.png'],scope_and_correction='current-consolidated-report.txt'))
    put(a.output/'manifest.json',dict(ROM_sha256=SHA,payloads=rows,freeze_sha256=old['freeze_sha256'],prior_public_manifest_sha256=sha(prior/'manifest.json'),
        stable_owned_files=[dict(path=str(f.relative_to(ROOT)).replace('\\','/'),sha256=sha(f),bytes=f.stat().st_size)for f in owned],original_large_receipt_external_summary_only=True))
    print(json.dumps(dict(public_manifest_sha256=sha(a.output/'manifest.json'),public_bytes=sum(f.stat().st_size for f in a.output.rglob('*')if f.is_file()),owned_files=len(owned))))


if __name__=='__main__':main()
