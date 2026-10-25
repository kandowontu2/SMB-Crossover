"""Independently verify the frozen, uninstalled TMNT storage handoff.

This checks reproducible bytes and the stated scope. It grants no native,
performance, music-fidelity, or release acceptance.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
STUDY = D / 'tmnt-native-storage-current50b5-v1'
BASE = '50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
NEW = '8e2fa5de95edc5be33bbb20fa9262c2f58e3ebfcb793d82a740275a16409b790'
RECEIPT = 'db0b2c00a82d4459ae8349dd84220a2421c74bd82b2b8263ace1c5aed903b47d'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT) and not out.exists()
    ready = STUDY / 'ready-v1'
    assert sha(ready / 'receipt.json') == RECEIPT
    receipt = json.loads((ready / 'receipt.json').read_text())
    assert receipt['passed'] and not receipt['accepted'] and not receipt['native_run']
    frozen = json.loads((STUDY / 'current-baseline-v1/frozen-source.json').read_text())
    baseline = frozen['source_files']
    changes = json.loads((ready / 'changed-source.json').read_text())
    assert changes == receipt['changed_source_files'] and len(changes) == 14
    assert len(baseline) == 650
    assert all(sha(ROOT / name) == value for name, value in baseline.items())
    assert sha(ROOT / 'build/smb-crossover-mmc5-expanded.nes') == BASE
    assert sha(Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes')) == BASE
    assert sha(ready / 'candidate.nes') == NEW
    assert sha(ready / 'roundtrip.nes') == NEW
    assert sha(ready / 'source.zip') == receipt['source_zip_sha256']
    assert sha(ready / 'review.patch') == receipt['review_patch_sha256']
    report = ROOT / 'docs/qa/tmnt-native-storage-2026-10-25.txt'
    assert sha(report) == receipt['report_sha256']
    for name, row in changes.items():
        assert row['before_sha256'] == baseline.get(name)
    expected = baseline | {name: row['after_sha256'] for name, row in changes.items()}
    out.mkdir(parents=True)
    source = out / 'source'
    with zipfile.ZipFile(ready / 'source.zip') as z:
        assert len(z.namelist()) == len(set(z.namelist())) == len(expected) == 656
        assert set(z.namelist()) == set(expected)
        for info in z.infolist():
            destination = (source / info.filename).resolve()
            assert destination.is_relative_to(source.resolve())
            data = z.read(info)
            assert hashlib.sha256(data).hexdigest() == expected[info.filename]
            assert data == (ready / 'source' / info.filename).read_bytes()
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
    for label, row in receipt['proofs'].items():
        path = Path(row['path'])
        assert sha(path) == row['sha256'], label
        assert json.loads(path.read_text())['passed'], label
    for name, value in receipt['owned_tools'].items():
        assert sha(ROOT / 'tools/audit' / name) == value
        assert sha(ready / 'tools' / name) == value
    old = (ROOT / 'build/smb-crossover-mmc5-expanded.nes').read_bytes()
    new = (ready / 'candidate.nes').read_bytes()
    assert len(old) == len(new) == 2097168
    assert old[:16] == new[:16] and old[1048592:] == new[1048592:]
    bank = lambda raw, n: raw[16 + 8192*n:16 + 8192*(n+1)]
    deltas = {str(n): sum(x != y for x, y in zip(bank(old, n), bank(new, n))) for n in range(128)}
    deltas = {n: count for n, count in deltas.items() if count}
    assert deltas == receipt['changed_PRG_bytes']
    assert bank(old, 99)[:138] == bank(new, 99)[:138]
    for n in (115, 123, 124, 126):
        assert bank(old, n) == bank(new, n)
    command = [sys.executable, '-B', str(source / 'tools/build_mmc5_expanded.py'),
               '--workspace', str(source), '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'),
               '--output', str(out / 'rebuilt.nes')]
    process = subprocess.run(command, cwd=source, capture_output=True, text=True)
    (out / 'build.log').write_text(process.stdout + process.stderr)
    assert process.returncode == 0, (process.stdout + process.stderr)[-4000:]
    assert sha(out / 'rebuilt.nes') == NEW
    assert all(sha(ROOT / name) == value for name, value in baseline.items())
    assert all(sha(source / name) == value for name, value in expected.items())
    result = dict(passed=True, accepted=False, native_run=False, production_changes=False,
                  goal_complete=False, installed_ROM_sha256=BASE, candidate_ROM_sha256=NEW,
                  receipt_sha256=RECEIPT, frozen_ROOT_inputs=len(baseline),
                  source_archive_files=len(expected), changed_source_files=len(changes),
                  changed_PRG_bytes=deltas, exact_fresh_build=True,
                  external_packet=ready.as_posix(), source_archive_sha256=sha(ready / 'source.zip'),
                  tool_sha256=sha(Path(__file__)),
                  limits='Storage/source-byte review only. Native DMC, IRQ/NMI/DMA, gameplay cadence, '
                         'remaining dispatcher overhead and final composition remain unqualified.')
    (out / 'proof.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
