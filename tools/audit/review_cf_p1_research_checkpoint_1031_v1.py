"""Independently verify and stage the finite CF experiment research packet."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

R = Path(__file__).resolve().parents[2]
Q = R/'docs/qa/checkpoints/2026-10-31/contra-force-p1-source-experiment-v1'
O = R/'docs/qa/checkpoints/2026-10-31/contra-force-p1-research-root-review-v1'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def git(*args):
    return subprocess.run(['git',*args],cwd=R,capture_output=True,text=True,check=True).stdout


def main():
    assert not O.exists() and not git('diff','--cached','--name-only').strip()
    assert sha(Q/'handoff.json') == '1bbd755533e0728bded606850ca620b41012da6512881928865a7ea1fbe3c7fb'
    h = json.loads((Q/'handoff.json').read_text())
    assert len(h['bindings']) == 191 and not h['restore67_linked_in_cartridge']
    assert not h['native'] and not h['ready'] and not h['admitted'] and not h['installed']
    for p,digest in h['bindings'].items():
        assert sha(p) == digest,p
    stage = R/'build/contra-force-p1-cart-v2/source-stage.json'
    d = json.loads(stage.read_text());assert len(d['bindings']) == 9344
    for p,digest in d['bindings'].items():
        assert sha(p) == digest,p
    with zipfile.ZipFile(Q/'source-only.zip') as z:
        assert len(z.namelist()) == len(set(z.namelist())) == 184
        for item in z.infolist():
            p = (R/item.filename).resolve()
            assert p.is_relative_to(R) and not item.is_dir()
            data = z.read(item)
            assert data == p.read_bytes() and hashlib.sha256(data).hexdigest() == h['bindings'][str(p)],item.filename
    O.mkdir(parents=True)
    out = dict(passed=True, reviewer='root', source=True, native=False, installed=False,
        handoff_sha256=sha(Q/'handoff.json'), direct_bindings_verified=191,
        actual_prior_source_stage_bindings_verified=9344, source_archive_members_verified=184,
        source_archive_sha256=sha(Q/'source-only.zip'), CF_pending=True,
        scope='Content/source archive rehash. Finite positives and retained negatives are accurately separated; synthetic restore is not a linked cart, vector/segment/source-join work remains incomplete.',
        bindings={str(p.resolve()):sha(p) for p in [Path(__file__),Q/'handoff.json',Q/'source-only.zip',stage]})
    (O/'review.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    owned=json.loads((Q/'owned-files.json').read_text())['files']
    paths=[*owned,Path(__file__).relative_to(R).as_posix(),(O/'review.json').relative_to(R).as_posix()]
    assert all((R/p).is_file() and Path(p).suffix.lower() not in ['.nes','.o','.dbg','.lbl','.exe'] for p in paths)
    assert 'docs/qa/current-roster-progress-2026-10-27.json' not in paths
    git('add','--',*paths)
    staged=git('diff','--cached','--name-only').splitlines()
    assert set(staged)<=set(paths)
    print(json.dumps(dict(passed=True,source_bindings=9344+191,archive_members=184,staged_files=len(staged))))


if __name__ == '__main__':
    main()
