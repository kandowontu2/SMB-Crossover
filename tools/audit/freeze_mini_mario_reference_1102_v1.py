"""Preserve only the verified small Mini Mario source input packet."""
import hashlib,json,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/mini-mario-reference-checkpoint-1102-v1'
D=R/'docs/qa/checkpoints/2026-11-02/mini-mario-reference-v1'
def main():
    p=R/'build/mini-mario-reference-1102-v1';q=json.loads((p/'receipt.json').read_text())
    assert q['passed']and q['private_reference_only']and q['selected_files']==15
    assert sha(p/'reference.zip')==q['archive_SHA256']=='bd61928508a253037e420a1bbd18a8ee7e68679a5632b9ded23b2aa84a8dc543'
    with zipfile.ZipFile(p/'reference.zip')as z:
        assert set(z.namelist())==set(q['files'])
        for name,meta in q['files'].items():
            data=z.read(name);assert len(data)==meta['bytes']and hashlib.sha256(data).hexdigest()==meta['SHA256']
            assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==meta['git_blob']
    assert not D.exists();D.mkdir(parents=True)
    for source,name in[(p/'reference.zip','reference.zip'),(p/'receipt.json','receipt.json')]:
        (D/name).write_bytes(source.read_bytes());assert sha(D/name)==sha(source)
    O.mkdir(exist_ok=True);(O/'receipt.json').write_text(json.dumps(dict(passed=True,checkpoint=D.relative_to(R).as_posix(),archive_bytes=q['archive_bytes'],verified_members=15),indent=2)+'\n')
    print(json.dumps(dict(passed=True,verified_members=15,archive_bytes=q['archive_bytes'])))
if __name__=='__main__':main()
