"""Reversibly gzip four specifically bound old, non-route compiler output sets.

Candidates are not accepted by this storage operation. Explicit rejected sets,
routes, native captures, current48/49, source, ROMs and all receipts stay literal.
Restore exact raw filenames before any historical metadata consumer runs.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import importlib.util
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[2]
CP = ROOT/'build/checkpoints'
OWN = ROOT/'build/verification/root-old-candidate-metadata49-compaction-a'
SETS = {'roster-audit-v40-provisional-a': 'unaccepted-prototype',
        'roster-audit-v41-provisional-a': 'unaccepted-functional-candidate',
        'roster-audit-v42-provisional-c': 'provisional-not-accepted',
        'roster-audit-v45-provisional-a': 'provisional-not-accepted'}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
digest = lambda b: hashlib.sha256(b).hexdigest()
HELPER = ROOT/'tools/audit/compact_old_canonical_metadata49.py'
spec = importlib.util.spec_from_file_location('composition', HELPER)
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
old.OWN = OWN


def verify(plan):
    assert sha(Path(__file__)) == plan['script_sha256'] and sha(HELPER) == plan['helper_sha256']
    old.verify_protected(plan)
    old.verify_composition(plan)
    for row in plan['rows']:
        assert sha(ROOT/row['candidate']) == row['candidate_sha256']
        assert sha(ROOT/row['sibling_rom']) == row['sibling_rom_sha256']


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('action', choices=('prepare', 'compact', 'verify', 'restore-one'))
    ap.add_argument('--plan-sha256')
    ap.add_argument('--path')
    a = ap.parse_args()
    target = OWN/'plan.json'
    if a.action == 'prepare':
        assert not OWN.exists()
        rows = []
        for name, status in SETS.items():
            folder = CP/name
            c = folder/'candidate.json'
            m = json.loads(c.read_text())
            assert m['status'] == status
            assert not any('reject' in q.name.lower() or 'negative' in q.name.lower() for q in folder.iterdir())
            for mapper in ('mmc3', 'mmc5'):
                rom = folder/f'smb-crossover-{mapper}.nes'
                expected = m['roms'][mapper]
                expected = expected['sha256'] if isinstance(expected, dict) else expected
                assert sha(rom) == expected and rom.read_bytes().startswith(b'NES\x1a')
                for suffix, header in (('.dbg', b'version\tmajor=2,minor=0'), ('.lst', b'ca65 '),
                                       ('.lbl', b'al '), ('.map', b'Modules list:')):
                    p = rom.with_suffix(suffix)
                    assert p.resolve().is_relative_to(CP.resolve()) and p.is_file()
                    assert not Path(str(p)+'.gz').exists()
                    raw = p.read_bytes()
                    assert raw.startswith(header)
                    if suffix == '.dbg':
                        assert all(t in raw for t in (b'file\t', b'seg\t', b'sym\t'))
                    zipped = gzip.compress(raw, compresslevel=9, mtime=0)
                    assert gzip.decompress(zipped) == raw and len(zipped) < len(raw)
                    st = p.stat()
                    rows.append(dict(raw=p.relative_to(ROOT).as_posix(), archive=p.relative_to(ROOT).as_posix()+'.gz',
                                     raw_bytes=len(raw), raw_sha256=digest(raw), gzip_bytes=len(zipped),
                                     gzip_sha256=digest(zipped), mtime_ns=st.st_mtime_ns, mode=st.st_mode,
                                     candidate=c.relative_to(ROOT).as_posix(), candidate_sha256=sha(c),
                                     checkpoint_status=status, sibling_rom=rom.relative_to(ROOT).as_posix(),
                                     sibling_rom_sha256=expected))
        assert len(rows) == 32 and len({r['raw'] for r in rows}) == 32
        plan = dict(status='prepared-not-applied', script_sha256=sha(Path(__file__)), helper_sha256=sha(HELPER),
                    scope=__doc__, rows=rows, protected=old.protected(rows),
                    earlier_immutable_plan_composition=old.old_plan_overlaps(rows))
        plan['summary'] = dict(files=len(rows), raw_bytes=sum(r['raw_bytes'] for r in rows),
                               gzip_bytes=sum(r['gzip_bytes'] for r in rows))
        plan['summary']['saved_bytes'] = plan['summary']['raw_bytes']-plan['summary']['gzip_bytes']
        OWN.mkdir()
        target.write_text(json.dumps(plan, indent=2)+'\n')
        verify(plan)
        print(json.dumps(dict(plan_sha256=sha(target), **plan['summary'])), flush=True)
        return
    assert a.plan_sha256 and sha(target) == a.plan_sha256
    plan = json.loads(target.read_text())
    verify(plan)
    if a.action == 'compact':
        assert not (OWN/'receipt.json').exists()
        sys.path.insert(0, str(ROOT/'tools/playthroughs'))
        from roster_run import workspace_bytes
        used = workspace_bytes(ROOT)
        assert used+plan['summary']['gzip_bytes']+2_000_000 < 30_000_000_000
        stage = OWN/'stage'
        stage.mkdir()
        # All32 durable, exact backups must exist before any raw output is unlinked.
        for i, row in enumerate(plan['rows']):
            p = ROOT/row['raw']
            assert p.resolve().parent.name in SETS and p.resolve().is_relative_to(CP.resolve())
            assert sha(p) == row['raw_sha256']
            zipped = gzip.compress(p.read_bytes(), compresslevel=9, mtime=0)
            assert digest(zipped) == row['gzip_sha256']
            with (stage/f'{i}.gz').open('xb') as f:
                f.write(zipped); f.flush(); os.fsync(f.fileno())
            assert digest(gzip.decompress((stage/f'{i}.gz').read_bytes())) == row['raw_sha256']
        verify(plan)
        for i, row in enumerate(plan['rows']):
            p, archive = ROOT/row['raw'], ROOT/row['archive']
            assert p.resolve().parent.name in SETS and p.resolve().is_relative_to(CP.resolve())
            assert sha(p) == row['raw_sha256'] and not archive.exists()
            (stage/f'{i}.gz').replace(archive)
            assert sha(archive) == row['gzip_sha256']
            assert digest(gzip.decompress(archive.read_bytes())) == row['raw_sha256']
            p.unlink()
        stage.rmdir()  # Empty directory only.
    elif a.action == 'restore-one':
        matches = [r for r in plan['rows'] if r['raw'] == a.path]
        assert len(matches) == 1
        row = matches[0]
        p, archive = ROOT/row['raw'], ROOT/row['archive']
        assert not p.exists() and sha(archive) == row['gzip_sha256']
        raw = gzip.decompress(archive.read_bytes())
        assert digest(raw) == row['raw_sha256']
        with p.open('xb') as f:
            f.write(raw); f.flush(); os.fsync(f.fileno())
        os.chmod(p, row['mode']); os.utime(p, ns=(row['mtime_ns'], row['mtime_ns']))
    verify(plan)
    for row in plan['rows']:
        assert sha(ROOT/row['archive']) == row['gzip_sha256']
        assert digest(gzip.decompress((ROOT/row['archive']).read_bytes())) == row['raw_sha256']
        if (ROOT/row['raw']).exists():
            assert sha(ROOT/row['raw']) == row['raw_sha256']
    out = OWN/('receipt.json' if a.action == 'compact' else 'verification.json' if a.action == 'verify' else 'restore-receipt.json')
    assert not out.exists()
    receipt = dict(status='PASS_EXACT_REVERSIBLE_OLD_CANDIDATE_COMPILER_STORAGE', action=a.action,
                   plan_sha256=sha(target), summary=plan['summary'], all32_roundtrips_exact=True,
                   all_backups_durable_before_unlink=True, historical_raw_restore_required=True,
                   previous_immutable_plan_logical_hashes_exact=True, current48_49_changed=0,
                   route_native_source_ROM_receipt_files_changed=0, candidate_acceptance_inferred=False)
    out.write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
