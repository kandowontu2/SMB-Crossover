"""Losslessly store manifest-bound compiler metadata from checkpoints <=45.

Only .lst/.lbl/.map compiler outputs are eligible. This never accepts an old
prototype or changes ROMs, source, routes, native evidence, or current48/49.
Restore exact raw bytes before an old consumer requires a literal filename.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import os
import re

ROOT = Path(__file__).resolve().parents[2]
CP = ROOT / 'build/checkpoints'
OWN = ROOT / 'build/verification/root-old-canonical-metadata49-compaction-a'
digest = lambda b: hashlib.sha256(b).hexdigest()
sha = lambda p: digest(p.read_bytes())


def protected(rows):
    allowed = {r['raw'] for r in rows}
    return {p.relative_to(ROOT).as_posix(): sha(p)
            for parent in sorted({(ROOT / r['raw']).parent for r in rows})
            for p in sorted(parent.rglob('*'))
            if p.is_file() and p.relative_to(ROOT).as_posix() not in allowed}


def verify_protected(plan):
    for n, h in plan['protected'].items():
        assert (ROOT / n).is_file() and sha(ROOT / n) == h, n


def old_plan_overlaps(rows):
    """Record composition with immutable earlier storage receipts, not edit them."""
    by_path = {str((ROOT / r['raw']).resolve()): r for r in rows}
    overlaps = []
    for p in sorted((ROOT / 'build/verification').glob('*compaction*/plan.json')):
        if p.parent == OWN:
            continue
        data = json.loads(p.read_text(encoding='utf-8'))
        entries = data.get('protected', {})
        if isinstance(entries, dict):
            entries = [dict(path=n, sha256=h) for n, h in entries.items()]
        matches = []
        for e in entries:
            n = e.get('path', e.get('raw', ''))
            r = by_path.get(str((ROOT / n).resolve()))
            if r:
                h = e.get('sha256', e.get('raw_sha256'))
                assert h == r['raw_sha256'], (str(p), n)
                matches.append(dict(raw=r['raw'], sha256=h))
        if matches:
            overlaps.append(dict(plan=p.relative_to(ROOT).as_posix(),
                                 sha256=sha(p), exact_logical_paths=matches))
    return overlaps


def verify_composition(plan):
    rows = {r['raw']: r for r in plan['rows']}
    for previous in plan['earlier_immutable_plan_composition']:
        assert sha(ROOT / previous['plan']) == previous['sha256']
        for e in previous['exact_logical_paths']:
            row = rows[e['raw']]
            p = ROOT / row['raw']
            data = p.read_bytes() if p.is_file() else gzip.decompress((ROOT / row['archive']).read_bytes())
            assert digest(data) == e['sha256'] == row['raw_sha256']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'compact', 'verify', 'restore-one'))
    parser.add_argument('--plan-sha256')
    parser.add_argument('--path')
    args = parser.parse_args()
    target = OWN / 'plan.json'
    if args.action == 'prepare':
        assert not OWN.exists()
        rows = []
        skipped = []
        for folder in sorted(CP.iterdir()):
            match = re.fullmatch(r'roster-audit-v(\d+)(?:-provisional-[a-z])?', folder.name)
            if not folder.is_dir() or not match or not 1 <= int(match[1]) <= 45:
                continue
            manifest_path = folder / 'manifest.json'
            if not manifest_path.is_file():
                skipped.append(dict(folder=folder.name, reason='No manifest; excluded.'))
                continue
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            roms = manifest.get('roms', manifest)
            for mapper in ('mmc3', 'mmc5'):
                rom = folder / f'smb-crossover-{mapper}.nes'
                expected = roms.get(rom.name, roms.get(mapper))
                if not isinstance(expected, str) or not rom.is_file() or sha(rom) != expected:
                    skipped.append(dict(folder=folder.name, mapper=mapper, reason='No exact manifest ROM binding; excluded.'))
                    continue
                assert rom.read_bytes()[:4] == b'NES\x1a'
                for suffix, header in (('.lst', b'ca65 '), ('.lbl', b'al '), ('.map', b'Modules list:')):
                    raw = rom.with_suffix(suffix)
                    if not raw.is_file() or Path(str(raw) + '.gz').exists():
                        continue
                    assert raw.resolve().is_relative_to(CP.resolve())
                    data = raw.read_bytes()
                    assert data.startswith(header), str(raw)
                    archive = gzip.compress(data, compresslevel=9, mtime=0)
                    assert gzip.decompress(archive) == data and len(archive) < len(data)
                    st = raw.stat()
                    rows.append(dict(raw=raw.relative_to(ROOT).as_posix(), archive=raw.relative_to(ROOT).as_posix()+'.gz',
                                     raw_bytes=len(data), raw_sha256=digest(data), gzip_bytes=len(archive), gzip_sha256=digest(archive),
                                     mtime_ns=st.st_mtime_ns, mode=st.st_mode, version=int(match[1]),
                                     manifest=manifest_path.relative_to(ROOT).as_posix(), manifest_sha256=sha(manifest_path),
                                     sibling_rom=rom.relative_to(ROOT).as_posix(), sibling_rom_sha256=expected,
                                     checkpoint_status=manifest.get('status', 'unspecified; acceptance not inferred')))
        assert rows and len({r['raw'] for r in rows}) == len(rows)
        plan = dict(status='prepared-not-applied', script_sha256=sha(Path(__file__)), scope=__doc__,
                    rows=rows, skipped=skipped, protected=protected(rows),
                    earlier_immutable_plan_composition=old_plan_overlaps(rows),
                    historical_dependency='Restore the exact raw bytes before invoking historical raw-filename/hash consumers; no old receipt is rewritten.')
        plan['summary'] = dict(files=len(rows), raw_bytes=sum(r['raw_bytes'] for r in rows), gzip_bytes=sum(r['gzip_bytes'] for r in rows))
        plan['summary']['saved_bytes'] = plan['summary']['raw_bytes'] - plan['summary']['gzip_bytes']
        OWN.mkdir()
        target.write_text(json.dumps(plan, indent=2)+'\n', encoding='utf-8')
        verify_composition(plan)
        print(json.dumps(dict(plan_sha256=sha(target), **plan['summary'])), flush=True)
        return
    assert args.plan_sha256 and sha(target) == args.plan_sha256
    plan = json.loads(target.read_text(encoding='utf-8'))
    assert sha(Path(__file__)) == plan['script_sha256']
    verify_protected(plan)
    verify_composition(plan)
    if args.action == 'compact':
        assert not (OWN / 'receipt.json').exists()
        stage = OWN / 'stage'
        stage.mkdir()
        for i, row in enumerate(plan['rows']):
            raw = ROOT / row['raw']
            assert raw.resolve().is_relative_to(CP.resolve()) and 1 <= row['version'] <= 45
            assert sha(raw) == row['raw_sha256']
            assert sha(ROOT / row['manifest']) == row['manifest_sha256']
            assert sha(ROOT / row['sibling_rom']) == row['sibling_rom_sha256']
            archive = gzip.compress(raw.read_bytes(), compresslevel=9, mtime=0)
            assert digest(archive) == row['gzip_sha256']
            backup = stage / f'{i}.gz'
            with backup.open('xb') as f:
                f.write(archive)
                f.flush()
                os.fsync(f.fileno())
            assert digest(gzip.decompress(backup.read_bytes())) == row['raw_sha256']
        verify_protected(plan)
        for i, row in enumerate(plan['rows']):
            raw, archive = ROOT / row['raw'], ROOT / row['archive']
            assert raw.resolve().is_relative_to(CP.resolve()) and sha(raw) == row['raw_sha256']
            assert not archive.exists()
            (stage / f'{i}.gz').replace(archive)
            assert sha(archive) == row['gzip_sha256']
            assert digest(gzip.decompress(archive.read_bytes())) == row['raw_sha256']
            raw.unlink()  # Exact compiler output, durable validated backup already exists.
        stage.rmdir()  # Empty staging directory only.
    elif args.action == 'restore-one':
        matches = [r for r in plan['rows'] if r['raw'] == args.path]
        assert len(matches) == 1
        row = matches[0]
        raw = ROOT / row['raw']
        assert not raw.exists()
        archive = ROOT / row['archive']
        assert sha(archive) == row['gzip_sha256']
        data = gzip.decompress(archive.read_bytes())
        assert digest(data) == row['raw_sha256']
        with raw.open('xb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(raw, row['mode'])
        os.utime(raw, ns=(row['mtime_ns'], row['mtime_ns']))
    verify_protected(plan)
    verify_composition(plan)
    for row in plan['rows']:
        archive = ROOT / row['archive']
        assert sha(archive) == row['gzip_sha256']
        assert digest(gzip.decompress(archive.read_bytes())) == row['raw_sha256']
        if (ROOT / row['raw']).exists():
            assert sha(ROOT / row['raw']) == row['raw_sha256']
    receipt = dict(status='PASS-exact-reversible-old-compiler-metadata', action=args.action,
                   plan_sha256=sha(target), summary=plan['summary'], all_roundtrips_exact=True,
                   all_backups_durable_before_raw_unlink=True, earlier_plan_logical_hashes_exact=True,
                   current48_49_changed=0, route_files_changed=0, native_evidence_changed=0, acceptance_inferred=False)
    output = OWN / ('receipt.json' if args.action == 'compact' else 'verification.json' if args.action == 'verify' else 'restore-receipt.json')
    assert not output.exists()
    output.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
