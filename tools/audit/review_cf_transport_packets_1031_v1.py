"""Root review of exact frozen transport/retirement/loader packet contents."""
from pathlib import Path
import hashlib
import json
import zipfile

R=Path(__file__).resolve().parents[2]
PACKETS=[('cf-bt-shared-transport-v3','a994d02be0cc399b602f457bcb43360f0c9d4b1892d95093d54cd2aa1630ab7c',6538,5667),
    ('contra-force-retire-qualified-v1','01a85af928d1e9151ce2e1c7d4cfadd0578b20d24e368487f2760a670817c419',4867,29),
    ('contra-force-checkpoint-loader-qualified-v1','60a5bd7c8765180d85661a3f77551f1b2f0eeb1f0f2e4a3d8d8ba35e907f2321',4920,24)]


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    destination=R/'docs/qa/checkpoints/2026-10-31/cf-transport-root-review-v1'
    assert not destination.exists()
    rows=[]
    for name,expected,nfiles,nmembers in PACKETS:
        p=R/'build'/name/'handoff.json';assert sha(p)==expected
        d=json.loads(p.read_text());assert len(d['bindings'])==nfiles
        for filename,digest in d['bindings'].items():assert sha(filename)==digest,filename
        archive=next(Path(x) for x in d['bindings'] if Path(x).parent==p.parent and x.endswith('.zip'))
        members=[]
        with zipfile.ZipFile(archive) as z:
            assert len(z.infolist())==nmembers and len(set(z.namelist()))==nmembers
            for member in z.infolist():
                target=(R/member.filename).resolve()
                assert target.is_relative_to(R) and not member.is_dir()
                payload=z.read(member)
                assert payload==target.read_bytes(),member.filename
                assert str(target) in d['bindings'],('Unbound archive member',member.filename)
                assert hashlib.sha256(payload).hexdigest()==d['bindings'][str(target)]
                members.append(dict(path=member.filename,bytes=len(payload),sha256=d['bindings'][str(target)]))
        rows.append(dict(packet=str(p),handoff_sha256=expected,candidate=d['candidate'],
            bindings_verified=nfiles,archive=str(archive),archive_sha256=sha(archive),
            archive_members_verified=nmembers,members=members,
            native=False,installed=False,CF_pending=True,BT_pending=True))
    destination.mkdir(parents=True)
    receipt=dict(passed=True,reviewer='root',scope='Independently rehashed every bound file and compared every source archive member to its bound source bytes. Packet content review only; not new runtime or native gameplay qualification.',
        packets=rows,installed_build_unchanged=True,
        bindings={str(Path(__file__)):sha(__file__)})
    (destination/'review.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(passed=True,packets=len(rows),bindings=sum(r['bindings_verified'] for r in rows),
        archive_members=sum(r['archive_members_verified'] for r in rows),receipt=str(destination/'review.json'))))


if __name__=='__main__':main()
