"""Independently verify the frozen CF preload-name source checkpoint."""
from pathlib import Path
import hashlib
import json
import zipfile

R = Path(__file__).resolve().parents[2]
Q = R/'docs/qa/checkpoints/2026-10-31/cf-preload-name-source-v1'
O = R/'docs/qa/checkpoints/2026-10-31/cf-preload-name-root-review-v1'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    h = Q/'handoff.json'
    assert sha(h) == '416bd1b73c2704eaf1e71d0dc01730bd2b6bd81c38465064d35b80f05f6ccca6'
    q = json.loads(h.read_text())
    assert len(q['bindings']) == 10090
    for p, digest in q['bindings'].items():
        assert sha(p) == digest, p
    assert q['CF_pending'] and q['BT_pending'] and not q['admitted'] and not q['installed']
    zpath = Q/'source-only.zip'
    with zipfile.ZipFile(zpath) as z:
        assert len(z.namelist()) == len(set(z.namelist())) == 9069
        for item in z.infolist():
            p = (R/item.filename).resolve()
            assert p.is_relative_to(R) and not item.is_dir()
            data = z.read(item)
            assert data == p.read_bytes(), item.filename
            assert hashlib.sha256(data).hexdigest() == q['bindings'][str(p)], item.filename
    joint = Path(q['joint'])
    child = (joint/'candidate.nes').read_bytes()
    parent = (R/'build/cf-cold-warm-palette-source-v1/joint/candidate.nes').read_bytes()
    assert sha(joint/'candidate.nes') == q['candidate'] == '38a6259ca3abacccc10b8adb3b256f94a72f90307d44fb5ed5afe15114c372cd'
    assert len(child) == len(parent) == 2097168
    changes = [i for i, (a, b) in enumerate(zip(parent, child)) if a != b]
    assert len(changes) == 39
    assert all(16 <= i < 1048592 for i in changes), 'No CHR/header delta'
    O.mkdir(parents=True)
    receipt = dict(passed=True, reviewer='root', source=True, native=False, installed=False,
                   CF_and_BT_pending=True, handoff_sha256=sha(h), bindings_verified=10090,
                   source_archive_sha256=sha(zpath), source_archive_members_verified=9069,
                   candidate=q['candidate'], parent=q['parent'], changed_ROM_bytes=39,
                   changed_PRG_banks=sorted({(i-16)//8192 for i in changes}),
                   scope='Content and source-archive verification of the frozen preload-name/selector child. The bound caller/menu/parser/vector receipts retain their finite scopes; no native gameplay, P1 completion or unlock is inferred.',
                   bindings={str(p.resolve()): sha(p) for p in [Path(__file__), h, zpath, Q/'receipt.json']})
    (O/'review.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(passed=True, bindings_verified=10090, members_verified=9069,
                         changed_ROM_bytes=39, candidate=q['candidate'])))


if __name__ == '__main__':
    main()
