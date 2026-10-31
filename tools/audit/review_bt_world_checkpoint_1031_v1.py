"""Rehash the final pending BT/CF common source and stage its owned checkpoint."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

R = Path(__file__).resolve().parents[2]
Q = R/'docs/qa/checkpoints/2026-10-31/bt-current-cold-world-source-v1'
O = R/'docs/qa/checkpoints/2026-10-31/bt-cold-world-root-review-v1'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def git(*args):
    return subprocess.run(['git',*args],cwd=R,capture_output=True,text=True,check=True).stdout


def main():
    assert not O.exists() and not git('diff','--cached','--name-only').strip()
    assert sha(Q/'handoff.json') == 'b5dd615ae4b0af7ecc4b12c949c45084ce519b5b4fbc0492d27027346c46820e'
    h = json.loads((Q/'handoff.json').read_text())
    assert len(h['bindings']) == 11734 and h['CF_pending'] and h['BT_pending']
    assert not h['native'] and not h['installed'] and h['ready'] == 66
    for p,digest in h['bindings'].items():
        assert sha(p) == digest,p
    with zipfile.ZipFile(Q/'source-only.zip') as z:
        assert len(z.namelist()) == len(set(z.namelist())) == 10542
        for item in z.infolist():
            p = (R/item.filename).resolve()
            assert p.is_relative_to(R) and not item.is_dir()
            data = z.read(item)
            assert data == p.read_bytes() and hashlib.sha256(data).hexdigest() == h['bindings'][str(p)],item.filename
    O.mkdir(parents=True)
    out = dict(passed=True, reviewer='root', source=True, native=False, installed=False,
        handoff_sha256=sha(Q/'handoff.json'), candidate=h['candidate'],
        source_bindings_verified=11734, source_archive_members_verified=10542,
        source_archive_sha256=sha(Q/'source-only.zip'), BT_and_CF_pending=True,
        scope='Content/archive verification for the finite source controls. Genuine row32 caller evidence and projected parser evidence retain their distinct scopes; no native readiness/admission or current68 composition is inferred.',
        next='Genuine cumulative e54 M3 source graft, then byte-identical section-layout experiment, then independently qualified CF restore producer and native admission.',
        bindings={str(p.resolve()):sha(p) for p in [Path(__file__),Q/'handoff.json',Q/'source-only.zip',Q/'receipt.json']})
    (O/'review.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    paths=[p.strip() for p in (Q/'owned-files.txt').read_text().splitlines() if p.strip()]
    paths += [Path(__file__).relative_to(R).as_posix(),(O/'review.json').relative_to(R).as_posix()]
    assert all((R/p).is_file() and Path(p).suffix.lower() not in ['.nes','.o','.dbg','.lbl','.exe'] for p in paths)
    assert 'docs/qa/current-roster-progress-2026-10-27.json' not in paths
    git('add','--',*paths)
    staged=git('diff','--cached','--name-only').splitlines();assert set(staged)<=set(paths)
    print(json.dumps(dict(passed=True, bindings=11734, archive_members=10542, staged_files=len(staged))))


if __name__ == '__main__':
    main()
