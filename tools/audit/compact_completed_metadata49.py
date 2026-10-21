"""Reversibly gzip an exact completion-bound non-route compiler metadata list."""
from pathlib import Path
import argparse
import datetime
import gzip
import hashlib
import json
import os
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
PROPOSAL = ROOT / 'build/verification/agent47-nonroute-metadata-inventory-a'
OWN = ROOT / 'build/verification/root-completed-metadata49-compaction-a'
SHA = lambda data: hashlib.sha256(data).hexdigest()
sha = lambda path: SHA(path.read_bytes())


def sources():
    frozen = json.loads((PROPOSAL / 'freeze.json').read_text(encoding='utf-8'))
    assert sha(PROPOSAL / 'freeze.json') == 'bab593abfa00541a21b65cddeea37fc5ca47ad5989d40e33420254684deba048'
    rows = json.loads((PROPOSAL / 'allowlist.json').read_text(encoding='utf-8'))
    assert len(rows) == 370 and sum(r['bytes'] for r in rows) == 352298640
    assert len({r['path'] for r in rows}) == len(rows)
    for row in rows:
        relative = row['path']
        path = ROOT / relative
        assert path.resolve().is_relative_to(ROOT.resolve())
        assert str(path) == row['absolute_path']
        assert not re.search(r'(?<!\d)(?:48|49)(?!\d)', relative)
        assert not any(x in relative.lower() for x in ('roster-through-2-2', 'playthrough', 'route', 'negative', 'failure', 'failed', 'capture', 'recording'))
        assert path.suffix in ('.lst', '.lbl', '.map') and path.is_file()
        assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256']
        assert sha(ROOT / row['sibling_rom']) == row['sibling_rom_sha256']
        canonical = row['canonical']
        assert sha(ROOT / canonical['manifest']) == canonical['manifest_sha256']
        assert sha(ROOT / canonical['rom']) == canonical['rom_sha256'] == row['sibling_rom_sha256']
        metadata = canonical['metadata']
        counterpart = ROOT / metadata['path']
        contents = gzip.decompress(counterpart.read_bytes()) if metadata['storage'] == 'existing-gzip' else counterpart.read_bytes()
        assert SHA(contents) == metadata['sha256'] == row['sha256']
        assert sha(ROOT / row['completion']['path']) == row['completion']['sha256']
        for ref in row['direct_sibling_receipt_references']:
            assert sha(ROOT / ref['path']) == ref['sha256']
        assert not Path(str(path) + '.gz').exists()
    return rows


def protected_files(rows):
    allowed = {row['path'] for row in rows}
    protected = []
    parents = sorted({(ROOT / row['path']).parent for row in rows})
    # Sibling files only; no recursive operation or traversal into route folders.
    for parent in parents:
        for path in sorted(parent.iterdir()):
            if path.is_file() and path.relative_to(ROOT).as_posix() not in allowed:
                protected.append({'path': path.relative_to(ROOT).as_posix(), 'bytes': path.stat().st_size, 'sha256': sha(path)})
    return protected


def verify_protected(plan):
    for row in plan['protected']:
        path = ROOT / row['path']
        assert path.is_file() and path.stat().st_size == row['bytes'] and sha(path) == row['sha256']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'compact', 'verify', 'restore-one'))
    parser.add_argument('--expected-plan-sha256')
    parser.add_argument('--path', help='One exact allowlisted original path for restore-one')
    args = parser.parse_args()
    if args.action == 'prepare':
        assert not OWN.exists()
        rows = sources()
        protected = protected_files(rows)
        prepared = []
        for row in rows:
            path = ROOT / row['path']
            raw = path.read_bytes()
            archive = gzip.compress(raw, compresslevel=9, mtime=0)
            assert gzip.decompress(archive) == raw
            stat = path.stat()
            prepared.append(dict(raw=row['path'], archive=row['path'] + '.gz', raw_sha256=row['sha256'], raw_bytes=len(raw), gzip_sha256=SHA(archive), gzip_bytes=len(archive), mtime_ns=stat.st_mtime_ns, mode=stat.st_mode, provenance=row))
        plan = dict(status='prepared-not-applied', utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), workspace=str(ROOT), script_sha256=sha(Path(__file__)), proposal_freeze_sha256=sha(PROPOSAL / 'freeze.json'), proposal_allowlist_sha256=sha(PROPOSAL / 'allowlist.json'), scope='Exactly 370 completed old non-route compiler metadata files; current48/49, route, source, native evidence and negatives excluded.', entries=prepared, protected=protected)
        plan['summary'] = dict(files=len(prepared), raw_bytes=sum(e['raw_bytes'] for e in prepared), gzip_bytes=sum(e['gzip_bytes'] for e in prepared))
        plan['summary']['saved_bytes'] = plan['summary']['raw_bytes'] - plan['summary']['gzip_bytes']
        OWN.mkdir()
        target = OWN / 'plan.json'
        target.write_text(json.dumps(plan, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(dict(plan_sha256=sha(target), **plan['summary'])), flush=True)
        return
    target = OWN / 'plan.json'
    assert args.expected_plan_sha256 and sha(target) == args.expected_plan_sha256
    plan = json.loads(target.read_text(encoding='utf-8'))
    assert plan['script_sha256'] == sha(Path(__file__))
    assert plan['proposal_allowlist_sha256'] == sha(PROPOSAL / 'allowlist.json')
    verify_protected(plan)
    if args.action == 'compact':
        assert not (OWN / 'receipt.json').exists()
        sources()  # Revalidate every identity and completion before any mutation.
        stage = OWN / 'stage'
        stage.mkdir(exist_ok=False)
        # Every backup is validated before any raw file is unlinked.
        for index, row in enumerate(plan['entries']):
            raw = ROOT / row['raw']
            archive = gzip.compress(raw.read_bytes(), compresslevel=9, mtime=0)
            assert len(archive) == row['gzip_bytes'] and SHA(archive) == row['gzip_sha256']
            backup = stage / f'{index}.gz'
            with backup.open('xb') as file:
                file.write(archive)
                file.flush()
                os.fsync(file.fileno())
            assert sha(backup) == row['gzip_sha256']
            restored = gzip.decompress(backup.read_bytes())
            assert len(restored) == row['raw_bytes'] and SHA(restored) == row['raw_sha256']
        verify_protected(plan)
        for index, row in enumerate(plan['entries']):
            raw = ROOT / row['raw']
            archive = ROOT / row['archive']
            assert raw.resolve().is_relative_to(ROOT.resolve()) and sha(raw) == row['raw_sha256']
            assert not archive.exists()
            (stage / f'{index}.gz').replace(archive)
            assert sha(archive) == row['gzip_sha256']
            restored = gzip.decompress(archive.read_bytes())
            assert len(restored) == row['raw_bytes'] and SHA(restored) == row['raw_sha256']
            raw.unlink()  # Exact allowlisted file only, validated durable sibling backup exists.
        stage.rmdir()  # Empty staging directory only.
        verify_protected(plan)
        receipt = dict(status='PASS', action='lossless-completed-metadata-compaction', utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), plan_sha256=sha(target), script_sha256=sha(Path(__file__)), all_backups_validated_before_any_raw_unlink=True, every_archive_roundtrip_exact=True, protected_files_exact=len(plan['protected']), summary=plan['summary'], route_files_changed=0, current48_49_files_changed=0, native_evidence_changed=0)
        (OWN / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    elif args.action == 'restore-one':
        matches = [row for row in plan['entries'] if row['raw'] == args.path]
        assert len(matches) == 1
        row = matches[0]
        raw = ROOT / row['raw']
        archive = ROOT / row['archive']
        assert not raw.exists() and sha(archive) == row['gzip_sha256']
        restored = gzip.decompress(archive.read_bytes())
        assert len(restored) == row['raw_bytes'] and SHA(restored) == row['raw_sha256']
        with raw.open('xb') as file:
            file.write(restored)
            file.flush()
            os.fsync(file.fileno())
        os.chmod(raw, row['mode'])
        os.utime(raw, ns=(row['mtime_ns'], row['mtime_ns']))
        assert sha(raw) == row['raw_sha256']
        # Keep the validated archive as a backup. No recursive delete or move.
    for row in plan['entries']:
        raw = ROOT / row['raw']
        archive = ROOT / row['archive']
        assert archive.is_file() and sha(archive) == row['gzip_sha256']
        restored = gzip.decompress(archive.read_bytes())
        assert len(restored) == row['raw_bytes'] and SHA(restored) == row['raw_sha256']
        if raw.exists():
            assert sha(raw) == row['raw_sha256']
    verify_protected(plan)
    print(json.dumps(dict(status='PASS', action=args.action, plan_sha256=sha(target), **plan['summary'])), flush=True)


if __name__ == '__main__':
    main()
