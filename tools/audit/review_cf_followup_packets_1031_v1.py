"""Independently rehash the frozen joined lifecycle and own presentation."""
from pathlib import Path
import hashlib
import json
import zipfile

R=Path(__file__).resolve().parents[2]
PACKETS=[('cf-owner-retirement-v2','ca66a6190f035f85d6335127538986190bd1b599cb5e59d32204c245b3955431',7450,6736),
    ('contra-force-presentation-qualified-v1','c410478926bbccea55957d82c55957119960d2e63c359a7b08eb783597e23d0f',6638,51)]


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    destination=R/'docs/qa/checkpoints/2026-10-31/cf-followup-root-review-v1'
    assert not destination.exists();rows=[]
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
                payload=z.read(member);assert payload==target.read_bytes(),member.filename
                assert str(target) in d['bindings'],('Unbound archive member',member.filename)
                assert hashlib.sha256(payload).hexdigest()==d['bindings'][str(target)]
                members.append(dict(path=member.filename,bytes=len(payload),sha256=d['bindings'][str(target)]))
        rows.append(dict(packet=str(p),handoff_sha256=expected,
            candidate=d['candidate'] if 'candidate' in d else d['API']['candidate'],
            bindings_verified=nfiles,archive=str(archive),archive_sha256=sha(archive),
            archive_members_verified=nmembers,members=members,native=False,installed=False,CF_pending=True,BT_pending=True))
    destination.mkdir(parents=True)
    receipt=dict(passed=True,reviewer='root',scope='Content rehash/archive comparison of the exact source packets. Runtime qualification remains limited to the bound sibling tests; no native gameplay, palette admission or installed change.',
        packets=rows,bindings={str(Path(__file__)):sha(__file__)})
    (destination/'review.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(passed=True,bindings=sum(r['bindings_verified'] for r in rows),
        archive_members=sum(r['archive_members_verified'] for r in rows))))


if __name__=='__main__':main()
