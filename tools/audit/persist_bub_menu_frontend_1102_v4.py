"""Verify and persist the passed, still-gated frontend without a ROM copy."""
from pathlib import Path
import hashlib,json,zipfile

R=Path(__file__).resolve().parents[2]
O=R/'build/bub-menu-candidate-1102-v2'
D=R/'docs/qa/checkpoints/2026-11-02/bub-static-frontend-native-v4'
PIN='9192bb0e1c0bae0ce9798dd2b664b8918810aa46b84e04dbea364e46564ec339'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(R).as_posix()

def exact_write(path,data):
    if path.exists():assert path.read_bytes()==data,path
    else:path.write_bytes(data)

def main():
    frozen=O/'frontend-current-freeze-v3.json'
    q=json.loads(frozen.read_text());archive=R/q['archive']
    assert q['passed'] and q['private_frontend_native_pass']
    assert not q['menu_admitted'] and not q['backend_native'] and not q['installed']
    assert q['archive_SHA256']==PIN and sha(archive)==PIN
    assert len(q['new_source_files_to_stage'])==8
    for name,digest in q['bindings'].items():assert sha(R/name)==digest,name
    with zipfile.ZipFile(archive)as z:
        assert set(z.namelist())==set(q['bindings'])
        assert z.testzip() is None
        for name,digest in q['bindings'].items():
            assert hashlib.sha256(z.read(name)).hexdigest()==digest,name
    result=O/'native-menu3/capture/result.json'
    native=json.loads(result.read_text())
    assert native==q['native_result'] and native['passed']
    assert native['positions']==33 and native['observations']==55
    assert not native['gameplay_launch'] and native['screenshots']==4
    D.mkdir(parents=True,exist_ok=True)
    exact_write(D/'inputs.zip',archive.read_bytes())
    exact_write(D/'receipt.json',frozen.read_bytes())
    files=q['new_source_files_to_stage']+[rel(Path(__file__))]
    files +=[rel(D/name)for name in['inputs.zip','receipt.json','manifest.json','commit-files.txt']]
    staging=('\n'.join(files)+'\n').encode()
    exact_write(D/'commit-files.txt',staging)
    manifest=dict(passed=True,checkpoint=rel(D),archive_SHA256=PIN,
        exact_new_source_files=8,exact_archived_bindings=len(q['bindings']),
        private_frontend_ROM_SHA256=q['ROM_SHA256'],frontend_changed_bytes=1249,
        native_menu=native,menu_admitted=False,backend_native=False,installed=False,
        negative_packets_preserved=q['negative_packets'],
        next_composition_base_SHA256='1966a4883a888a5e62f90c4d3e96d25ecf028ddd7d714214727793418d633243',
        next_composition_requires_exact_backend_and_native_candidate_grants=True,
        bindings={rel(D/name):sha(D/name)for name in['inputs.zip','receipt.json','commit-files.txt']},
        source_recipe=dict(path=rel(Path(__file__)),SHA256=sha(Path(__file__))))
    exact_write(D/'manifest.json',(json.dumps(manifest,indent=2)+'\n').encode())
    exact_write(O/'commit-files-frontend-v4.txt',staging)
    receipt=dict(passed=True,durable_checkpoint=rel(D),files_to_stage=files,
        verified_archive_SHA256=PIN,verified_current_bindings=len(q['bindings']),
        durable_bytes=sum(p.stat().st_size for p in D.iterdir()),
        durable_files=len(list(D.iterdir())),ROM_created=False,Git_used=False)
    exact_write(O/'frontend-persistence-v4.json',(json.dumps(receipt,indent=2)+'\n').encode())
    own=[p for p in O.rglob('*')if p.is_file()]
    assert sum(p.stat().st_size for p in own)<32000000 and len(own)<=128
    print(json.dumps(dict(passed=True,checkpoint=rel(D),archive_SHA256=PIN,
        current_bytes=sum(p.stat().st_size for p in own),current_files=len(own),
        durable_bytes=receipt['durable_bytes'],durable_files=receipt['durable_files'])))

if __name__=='__main__':main()
