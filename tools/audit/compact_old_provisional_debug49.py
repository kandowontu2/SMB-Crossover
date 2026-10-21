"""Reversibly gzip only exact manifest-bound old v36..38 prototype compiler debug files.

These include development/provisional checkpoints; this does not accept them.
Routes, ROMs, source, native evidence, and current checkpoints are untouched.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import os

ROOT = Path(__file__).resolve().parents[2]
OWN = ROOT / 'build/verification/root-old-provisional-debug49-compaction-a'
CP = ROOT / 'build/checkpoints'
digest = lambda data: hashlib.sha256(data).hexdigest()
sha = lambda p: digest(p.read_bytes())


def protected(rows):
    allowed = {r['raw'] for r in rows}
    return {str(p.relative_to(ROOT)): sha(p)
            for parent in sorted({(ROOT / r['raw']).parent for r in rows})
            for p in sorted(parent.rglob('*')) if p.is_file() and str(p.relative_to(ROOT)) not in allowed}


def verify_protected(plan):
    assert all((ROOT / n).is_file() and sha(ROOT / n) == h for n, h in plan['protected'].items())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'compact', 'verify'))
    parser.add_argument('--plan-sha256')
    args = parser.parse_args()
    plan_path = OWN / 'plan.json'
    if args.action == 'prepare':
        assert not OWN.exists()
        rows = []
        for version, suffix in [(36, x) for x in 'abc'] + [(37, x) for x in 'ab'] + [(38, x) for x in 'abcde']:
            folder = CP / f'roster-audit-v{version}-provisional-{suffix}'
            manifest_path = folder / 'manifest.json'
            if not manifest_path.is_file():
                continue
            manifest = json.loads(manifest_path.read_text())
            roms = manifest.get('roms', manifest)
            for mapper in ('mmc3', 'mmc5'):
                rom = folder / f'smb-crossover-{mapper}.nes'
                raw = rom.with_suffix('.dbg')
                if not raw.is_file():
                    continue
                assert raw.resolve().is_relative_to(CP.resolve())
                assert not Path(str(raw) + '.gz').exists()
                assert sha(rom) == roms.get(rom.name, roms.get(mapper))
                data = raw.read_bytes()
                assert data.startswith(b'version\tmajor=2,minor=0\n') or data.startswith(b'version\tmajor=2,minor=0\r\n')
                assert b'file\t' in data and b'seg\t' in data and b'sym\t' in data
                zipped = gzip.compress(data, compresslevel=9, mtime=0)
                assert gzip.decompress(zipped) == data
                stat = raw.stat()
                rows.append(dict(raw=str(raw.relative_to(ROOT)), archive=str(raw.relative_to(ROOT)) + '.gz',
                                 raw_bytes=len(data), raw_sha256=digest(data), gzip_bytes=len(zipped), gzip_sha256=digest(zipped),
                                 mtime_ns=stat.st_mtime_ns, mode=stat.st_mode, version=version,
                                 manifest=str(manifest_path.relative_to(ROOT)), manifest_sha256=sha(manifest_path),
                                 checkpoint_status=manifest.get('status', 'not specified; no acceptance inferred'),
                                 sibling_rom=str(rom.relative_to(ROOT)), sibling_rom_sha256=sha(rom),
                                 completion='Manifest-bound sibling ROM plus complete ca65 compiler debug structure; not a gameplay acceptance claim.'))
        assert rows and all(r['gzip_bytes'] < r['raw_bytes'] for r in rows)
        plan = dict(status='prepared-not-applied', script_sha256=sha(Path(__file__)), rows=rows,
                    scope=__doc__, historical_dependency='Restore exact raw DBG from sibling gzip before a historical caller requires it. Existing receipts and callers are unchanged.',
                    protected=protected(rows))
        plan['summary'] = dict(files=len(rows), raw_bytes=sum(r['raw_bytes'] for r in rows), gzip_bytes=sum(r['gzip_bytes'] for r in rows))
        plan['summary']['saved_bytes'] = plan['summary']['raw_bytes'] - plan['summary']['gzip_bytes']
        OWN.mkdir()
        plan_path.write_text(json.dumps(plan, indent=2) + '\n')
        print(json.dumps(dict(plan_sha256=sha(plan_path), **plan['summary'])), flush=True)
        return
    assert args.plan_sha256 and sha(plan_path) == args.plan_sha256
    plan = json.loads(plan_path.read_text())
    assert sha(Path(__file__)) == plan['script_sha256']
    verify_protected(plan)
    if args.action == 'compact':
        assert not (OWN / 'receipt.json').exists()
        stage = OWN / 'stage'
        stage.mkdir()
        for i, row in enumerate(plan['rows']):
            raw = ROOT / row['raw']
            assert raw.resolve().is_relative_to(CP.resolve()) and 36 <= row['version'] <= 38
            assert sha(raw) == row['raw_sha256']
            assert sha(ROOT / row['manifest']) == row['manifest_sha256']
            assert sha(ROOT / row['sibling_rom']) == row['sibling_rom_sha256']
            data = gzip.compress(raw.read_bytes(), compresslevel=9, mtime=0)
            assert digest(data) == row['gzip_sha256']
            backup = stage / f'{i}.gz'
            with backup.open('xb') as out:
                out.write(data)
                out.flush()
                os.fsync(out.fileno())
            assert digest(gzip.decompress(backup.read_bytes())) == row['raw_sha256']
        verify_protected(plan)
        for i, row in enumerate(plan['rows']):
            raw, target = ROOT / row['raw'], ROOT / row['archive']
            assert raw.resolve().is_relative_to(CP.resolve()) and sha(raw) == row['raw_sha256']
            assert not target.exists()
            (stage / f'{i}.gz').replace(target)
            assert sha(target) == row['gzip_sha256']
            assert digest(gzip.decompress(target.read_bytes())) == row['raw_sha256']
            raw.unlink()
        stage.rmdir()
    verify_protected(plan)
    for row in plan['rows']:
        archive = ROOT / row['archive']
        assert sha(archive) == row['gzip_sha256']
        assert digest(gzip.decompress(archive.read_bytes())) == row['raw_sha256']
    receipt = dict(status='PASS-exact-reversible-compiler-storage', action=args.action,
                   plan_sha256=sha(plan_path), all_roundtrips_exact=True, all_backups_durable_before_raw_unlink=True,
                   summary=plan['summary'], current48_49_changed=0, routes_changed=0, native_evidence_changed=0,
                   acceptance_inferred=False)
    destination = OWN / ('receipt.json' if args.action == 'compact' else 'verification.json')
    assert not destination.exists()
    destination.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
