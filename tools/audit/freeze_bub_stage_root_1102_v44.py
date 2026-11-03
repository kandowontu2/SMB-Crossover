"""Verify and preserve the helper's explicit current-stage source packet."""
import hashlib,json,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/bub-stage-root-freeze-1102-v44'
D=R/'docs/qa/checkpoints/2026-11-02/bub-stage-source-v44'

def main():
    owner=R/'build/bub-menu-candidate-1102-v2';src=owner/'landing-fullstage-source-v44.json';q=json.loads(src.read_text());archive=owner/'landing-fullstage-source-v44.zip'
    assert q['passed']and q['Bub_full1_1_passed']and not q['Bob_full1_1_passed']and q['Bob_v42_native_pending']
    assert sha(archive)==q['archive_SHA256']=='269dedb9ffda1c200386e508854f74e10cf48e6a98c4f1bdc82ed59822354a26'
    with zipfile.ZipFile(archive)as z:
        assert set(z.namelist())==set(q['files'])and len(z.namelist())==63 and sum(i.file_size for i in z.infolist())<3_000_000
        for name,meta in q['files'].items():
            assert not Path(name).is_absolute()and'..'not in Path(name).parts and not name.endswith(('.nes','.mp4','.zip'))
            data=z.read(name);assert len(data)==meta['bytes']and hashlib.sha256(data).hexdigest()==meta['SHA256']
            assert(R/name).read_bytes()==data,name
    assert not D.exists();D.mkdir(parents=True)
    for a,name in[(archive,'inputs.zip'),(src,'receipt.json'),(owner/'landing-fullstage-commit-files-v44.txt','source-files.txt')]:
        (D/name).write_bytes(a.read_bytes());assert sha(D/name)==sha(a)
    # Current successful candidate receipts remain loose because the exact
    # delivery recipe binds them. The recorded removal list is permission to
    # prune later after recipes switch to compact evidence, not a mandate.
    O.mkdir(exist_ok=True);(O/'receipt.json').write_text(json.dumps(dict(passed=True,verified_members=63,archive_SHA256=sha(D/'inputs.zip'),checkpoint=D.relative_to(R).as_posix(),removed_files=0,scope='Helper v44 historical Bob-pending source/evidence packet preserved unchanged. Subsequent Bob v42 pass recorded separately. No ROM/capture generation or cleanup.'),indent=2)+'\n')
    print(json.dumps(dict(passed=True,verified_members=63,archive_SHA256=sha(D/'inputs.zip'),removed_files=0)))

if __name__=='__main__':main()
