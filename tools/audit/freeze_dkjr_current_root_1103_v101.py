"""Preserve the private DK Jr service/bounds milestone without ROM copies."""
import hashlib,json,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/dkjr-root-freeze-1103-v101'
D=R/'docs/qa/checkpoints/2026-11-03/dkjr-items-bounds-v70'
def main():
    O.mkdir(exist_ok=True);root=R/'build/dkjr-native-source-1102-v2';manifest=root/'native-bbox-v70.json';q=json.loads(manifest.read_text())
    archive=R/q['archive'];assert q['passed']and not q['qualified']and not q['installed']and not q['shared_grant']
    assert archive.stat().st_size==q['archive_bytes']==140860 and sha(archive)==q['archive_SHA256']
    with zipfile.ZipFile(archive)as z:
        assert len(z.namelist())==len(q['members'])==38
        for row in q['members']:
            name=row['path'].replace('\\','/');blob=z.read(name)
            assert len(blob)==row['bytes']and hashlib.sha256(blob).hexdigest()==row['SHA256']
            assert(R/name).read_bytes()==blob,name
    assert len(q['source_files'])==10
    D.mkdir(parents=True);(D/'inputs.zip').write_bytes(archive.read_bytes());(D/'helper-manifest.json').write_bytes(manifest.read_bytes())
    receipt=dict(passed=True,installed=False,qualified=False,checkpoint=D.relative_to(R).as_posix(),archive_SHA256=sha(D/'inputs.zip'),archive_bytes=q['archive_bytes'],members=38,source_files=q['source_files'],scope='Exact private source60..69 service/status/native collector fixtures and source bbox proposal, compiled gate closure and379IRQ+379genuineFF+859nestedIRQ minSP130. Shared gate/native raw40 admission and actual gameplay remain ungranted/incomplete; no ROM, native clear, helpers or current-positive-foreign claim. Original15px jump retained. Prior score-tail source59 checkpoint remains a compact independent dependency.',bindings={f.relative_to(R).as_posix():sha(f)for f in[Path(__file__),manifest,D/'inputs.zip',D/'helper-manifest.json']})
    (D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    p=R/'docs/qa/continuation-current.json';h=json.loads(p.read_text());h['dkjr_current_source_1102'].update(items_bounds_checkpoint=D.relative_to(R).as_posix(),items_bounds_status='PRIVATE_SOURCE_SERVICE_AND_BBOX_PROPOSAL_FROZEN_NO_NATIVE_ADMISSION',items_bounds_scope=receipt['scope']);p.write_text(json.dumps(h,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items()if k!='bindings'}))
if __name__=='__main__':main()
