"""Root independently rehashes actual cold source and own palette/name packets."""
from pathlib import Path
import hashlib
import json
import zipfile

R=Path(__file__).resolve().parents[2]
PACKETS=[('cf-cold-warm-source-v3','95e76dd28d532910a64a317d422440035790f476da3ee22f16ec6d988a16abb8',8397,7569,
    R/'docs/qa/checkpoints/2026-10-31/cf-cold-warm-source-v1/source-only.zip'),
    ('contra-force-palette-names-qualified-v1','e82eafd5f921793c7eebde4cefde7ab2f46ffc223c027b45d7712b1394114547',7556,58,
    R/'build/contra-force-palette-names-qualified-v1/source-delta-only.zip')]


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    dest=R/'docs/qa/checkpoints/2026-10-31/cf-final-source-root-review-v1';assert not dest.exists()
    rows=[]
    for name,expected,count,members,archive in PACKETS:
        p=R/'build'/name/'handoff.json';assert sha(p)==expected
        d=json.loads(p.read_text());assert len(d['bindings'])==count
        for filename,digest in d['bindings'].items():assert sha(filename)==digest,filename
        if str(archive) in d['bindings']:
            assert sha(archive)==d['bindings'][str(archive)]
        else:
            # The full cold archive is written after its handoff, avoiding
            # a self-referential digest. Every member must still match an
            # exact source binding in that independently pinned handoff.
            assert name=='cf-cold-warm-source-v3'
        with zipfile.ZipFile(archive) as z:
            assert len(z.namelist())==len(set(z.namelist()))==members
            for item in z.infolist():
                target=(R/item.filename).resolve();assert target.is_relative_to(R) and not item.is_dir()
                payload=z.read(item);assert payload==target.read_bytes(),item.filename
                assert str(target) in d['bindings'] and hashlib.sha256(payload).hexdigest()==d['bindings'][str(target)]
        rows.append(dict(packet=str(p),handoff_sha256=expected,candidate=d['candidate'],bindings_verified=count,
            archive=str(archive),archive_sha256=sha(archive),archive_members_verified=members))
    dest.mkdir(parents=True)
    receipt=dict(passed=True,reviewer='root',source=True,native=False,installed=False,CF_and_BT_pending=True,
        scope='Actual content/archive rehash. Bound sibling runtime tests retain their exact finite scopes; no P1 lease, readiness, native gameplay or admission is inferred.',
        packets=rows,bindings={str(Path(__file__)):sha(__file__)})
    (dest/'review.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(passed=True,bindings=sum(x['bindings_verified'] for x in rows),archive_members=sum(x['archive_members_verified'] for x in rows))))


if __name__=='__main__':main()
