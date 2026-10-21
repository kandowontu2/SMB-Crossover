"""Losslessly store exact completed pre-48 compiler debug metadata as gzip.

No route, source, ROM, native log, recording, or negative is eligible. Historical
tools that require a raw .dbg must restore that exact file before replaying.
"""
from pathlib import Path
import argparse
import datetime
import gzip
import hashlib
import json
import os
import re

ROOT = Path(__file__).resolve().parents[2]
PRIOR = ROOT / 'build/verification/agent47-nonroute-metadata-inventory-a'
OWN = ROOT / 'build/verification/root-completed-debug49-compaction-a'
digest = lambda data: hashlib.sha256(data).hexdigest()
sha = lambda path: digest(path.read_bytes())


def eligible():
    assert sha(PRIOR / 'freeze.json') == 'bab593abfa00541a21b65cddeea37fc5ca47ad5989d40e33420254684deba048'
    frozen = json.loads((PRIOR / 'freeze.json').read_text())
    for row in frozen['files']:
        path = Path(row['path'])
        assert path.resolve().is_relative_to(PRIOR.resolve())
        assert sha(path) == row['sha256'], path
    seen, rows, skipped = set(), [], []
    for prior in json.loads((PRIOR / 'allowlist.json').read_text()):
        path = (ROOT / prior['sibling_rom']).with_suffix('.dbg')
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        relative = path.relative_to(ROOT).as_posix()
        assert path.resolve().is_relative_to(ROOT.resolve())
        assert not re.search(r'(?<!\d)(?:48|49)(?!\d)', relative)
        assert not any(x in relative.lower() for x in ('roster-through-2-2', 'playthrough', 'route', 'negative', 'failure', 'failed', 'capture', 'recording'))
        assert not Path(str(path) + '.gz').exists()
        assert sha(ROOT / prior['sibling_rom']) == prior['sibling_rom_sha256']
        completion = prior['completion']
        assert sha(ROOT / completion['path']) == completion['sha256']
        canonical = prior['canonical']
        assert sha(ROOT / canonical['manifest']) == canonical['manifest_sha256']
        assert sha(ROOT / canonical['rom']) == prior['sibling_rom_sha256']
        other = (ROOT / canonical['rom']).with_suffix('.dbg')
        storage = 'raw' if other.is_file() else 'gzip'
        if storage == 'gzip':
            other = Path(str(other) + '.gz')
        contents = other.read_bytes()
        decoded = gzip.decompress(contents) if storage == 'gzip' else contents
        raw = path.read_bytes()
        if raw != decoded:
            skipped.append({'path': relative, 'reason': 'debug-bytes-differ-from-canonical; untouched', 'sha256': digest(raw)})
            continue
        stat = path.stat()
        archive = gzip.compress(raw, compresslevel=9, mtime=0)
        assert gzip.decompress(archive) == raw
        rows.append(dict(raw=relative, archive=relative + '.gz', raw_bytes=len(raw), raw_sha256=digest(raw),
                         gzip_bytes=len(archive), gzip_sha256=digest(archive), mtime_ns=stat.st_mtime_ns, mode=stat.st_mode,
                         sibling_rom=prior['sibling_rom'], sibling_rom_sha256=prior['sibling_rom_sha256'], completion=completion,
                         canonical=dict(manifest=canonical['manifest'], manifest_sha256=canonical['manifest_sha256'],
                                        rom=canonical['rom'], rom_sha256=canonical['rom_sha256'], debug_path=other.relative_to(ROOT).as_posix(),
                                        debug_storage=storage, debug_sha256=digest(decoded))))
    assert rows and all(row['raw_bytes'] > row['gzip_bytes'] for row in rows)
    return rows, skipped


def protect(rows):
    changed = {row['raw'] for row in rows}
    return [dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=sha(p))
            for parent in sorted({(ROOT / row['raw']).parent for row in rows})
            for p in sorted(parent.iterdir()) if p.is_file() and p.relative_to(ROOT).as_posix() not in changed]


def check_protected(plan):
    for row in plan['protected']:
        path = ROOT / row['path']
        assert path.is_file() and path.stat().st_size == row['bytes'] and sha(path) == row['sha256'], row['path']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'compact', 'verify', 'restore-one'))
    parser.add_argument('--expected-plan-sha256')
    parser.add_argument('--path')
    args = parser.parse_args()
    plan_path = OWN / 'plan.json'
    if args.action == 'prepare':
        assert not OWN.exists()
        rows, skipped = eligible()
        plan = dict(status='prepared-not-applied', utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    script_sha256=sha(Path(__file__)), prior_inventory_freeze_sha256=sha(PRIOR / 'freeze.json'),
                    scope='Exact completed pre-48 non-route compiler .dbg only. Preserve all source, ROMs, logs, traces, negatives, routes and current48/49.',
                    historical_dependency='Restore exact raw .dbg before any historical caller or prior protected-file verifier that opens it. No historical caller or receipt is changed.',
                    rows=rows, skipped=skipped, protected=protect(rows))
        plan['summary'] = dict(files=len(rows), raw_bytes=sum(x['raw_bytes'] for x in rows), gzip_bytes=sum(x['gzip_bytes'] for x in rows))
        plan['summary']['saved_bytes'] = plan['summary']['raw_bytes'] - plan['summary']['gzip_bytes']
        OWN.mkdir(exist_ok=False)
        plan_path.write_text(json.dumps(plan, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(dict(plan_sha256=sha(plan_path), **plan['summary'])), flush=True)
        return
    assert args.expected_plan_sha256 and sha(plan_path) == args.expected_plan_sha256
    plan = json.loads(plan_path.read_text())
    assert plan['script_sha256'] == sha(Path(__file__))
    check_protected(plan)
    if args.action == 'compact':
        assert not (OWN / 'receipt.json').exists()
        rows, skipped = eligible()
        assert rows == plan['rows'] and skipped == plan['skipped']
        stage = OWN / 'stage'
        stage.mkdir(exist_ok=False)
        for i, row in enumerate(rows):
            raw = ROOT / row['raw']
            archive = gzip.compress(raw.read_bytes(), compresslevel=9, mtime=0)
            assert len(archive) == row['gzip_bytes'] and digest(archive) == row['gzip_sha256']
            backup = stage / f'{i}.gz'
            with backup.open('xb') as out:
                out.write(archive)
                out.flush()
                os.fsync(out.fileno())
            assert sha(backup) == row['gzip_sha256']
            assert digest(gzip.decompress(backup.read_bytes())) == row['raw_sha256']
        check_protected(plan)
        # All durable exact backups exist before replacing any raw metadata.
        for i, row in enumerate(rows):
            raw, target = ROOT / row['raw'], ROOT / row['archive']
            assert raw.resolve().is_relative_to(ROOT.resolve()) and sha(raw) == row['raw_sha256']
            assert not target.exists()
            (stage / f'{i}.gz').replace(target)
            assert sha(target) == row['gzip_sha256']
            assert digest(gzip.decompress(target.read_bytes())) == row['raw_sha256']
            raw.unlink()
        stage.rmdir()  # Exact empty staging directory, no recursive removal.
        check_protected(plan)
        receipt = dict(status='PASS', action='lossless-completed-debug-metadata-storage', plan_sha256=sha(plan_path),
                       all_backups_durable_before_raw_unlink=True, all_roundtrips_exact=True, protected_files_exact=len(plan['protected']),
                       summary=plan['summary'], route_files_changed=0, native_evidence_changed=0, current48_49_files_changed=0)
        (OWN / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    elif args.action == 'restore-one':
        matches = [row for row in plan['rows'] if row['raw'] == args.path]
        assert len(matches) == 1
        row = matches[0]
        raw, target = ROOT / row['raw'], ROOT / row['archive']
        assert not raw.exists() and sha(target) == row['gzip_sha256']
        data = gzip.decompress(target.read_bytes())
        assert len(data) == row['raw_bytes'] and digest(data) == row['raw_sha256']
        with raw.open('xb') as out:
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
        os.chmod(raw, row['mode'])
        os.utime(raw, ns=(row['mtime_ns'], row['mtime_ns']))
        assert sha(raw) == row['raw_sha256']
    for row in plan['rows']:
        target = ROOT / row['archive']
        assert sha(target) == row['gzip_sha256']
        data = gzip.decompress(target.read_bytes())
        assert len(data) == row['raw_bytes'] and digest(data) == row['raw_sha256']
        raw = ROOT / row['raw']
        if raw.exists():
            assert sha(raw) == row['raw_sha256']
    check_protected(plan)
    print(json.dumps(dict(status='PASS', action=args.action, plan_sha256=sha(plan_path), **plan['summary'])), flush=True)


if __name__ == '__main__':
    main()
