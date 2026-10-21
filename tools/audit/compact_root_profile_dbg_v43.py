"""Losslessly archive explicit inactive root-owned profiling DBG duplicates."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / 'build/verification/root-profiling-dbg-plan-20261018/inventory.json'
OUT = ROOT / 'build/verification/root-profile-dbg-compaction-v43'
sys.path.insert(0, str(ROOT / 'tools/playthroughs'))
from roster_run import workspace_bytes


def sha(path, opener=open):
    h = hashlib.sha256()
    with opener(path, 'rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def safe(relative, namespace):
    path = ROOT / relative
    resolved = path.resolve(strict=True)
    assert resolved.is_relative_to(ROOT / namespace) and resolved == path.absolute()
    for parent in (path, *path.parents):
        if parent == ROOT:
            break
        assert not parent.is_symlink() and not parent.is_junction(), parent
    return path


def main():
    assert sha(PLAN) == '6a89ac924e602b60fc7bdb77aa1ce5eddc86e8dcebd0d4753c39a3fd2ac6e86e'
    plan = json.loads(PLAN.read_text())
    targets = plan['allowlist']
    assert len(targets) == 180 and all(t['owner_confirmed'] for t in targets)
    assert not OUT.exists(), 'Never overwrite a compaction receipt'
    OUT.mkdir()
    files = {safe(t['path'], 'build/profiling') for t in targets}
    assert len(files) == 180
    roots = {safe(t['manifest'], 'build/profiling').parent for t in targets}
    protected = {p for folder in roots for p in folder.rglob('*') if p.is_file() and p not in files}
    for target in targets:
        canonical = target['canonical']
        protected.add(safe(canonical['rom'], 'build/checkpoints'))
        protected.add(safe(canonical['dbg'], 'build/checkpoints'))
    originals = {str(p.relative_to(ROOT)): dict(bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(protected)}
    before = workspace_bytes(ROOT)
    report = dict(scope=__doc__, plan_sha256=sha(PLAN), workspace_before=before,
                  excluded='All routes, canonical checkpoints, older ownership-unconfirmed profiles, active43 jobs, all non-DBG evidence and the earlier rejected routes deletion scope.',
                  protected_files=originals, entries=[], completed=False)
    receipt = OUT / 'receipt.json'
    receipt.write_text(json.dumps(report, indent=2) + '\n')
    for i, target in enumerate(targets, 1):
        path = safe(target['path'], 'build/profiling')
        canonical = target['canonical']
        assert path.stat().st_size == target['bytes'] and sha(path) == target['sha256'] == canonical['dbg_sha256']
        assert sha(safe(target['adjacent_rom'], 'build/profiling')) == target['rom_sha256'] == canonical['rom_sha256']
        assert sha(safe(canonical['rom'], 'build/checkpoints')) == canonical['rom_sha256']
        assert sha(safe(canonical['dbg'], 'build/checkpoints')) == canonical['dbg_sha256']
        assert sha(safe(target['manifest'], 'build/profiling')) == target['manifest_sha256']
        assert sha(safe(target['completion_log'], 'build/profiling')) == target['completion_log_sha256']
        archive = ROOT / target['prospective_gzip_path']
        assert archive == path.with_suffix('.dbg.gz') and not archive.exists()
        with path.open('rb') as source, gzip.open(archive, 'xb', compresslevel=6) as destination:
            for block in iter(lambda: source.read(1048576), b''):
                destination.write(block)
        assert sha(archive, gzip.open) == target['sha256'], 'Verified lossless recovery before replacing raw duplicate'
        assert archive.stat().st_size < path.stat().st_size
        row = dict(path=target['path'], archive=str(archive.relative_to(ROOT)), raw_sha256=target['sha256'],
                   raw_bytes=target['bytes'], archive_bytes=archive.stat().st_size, archive_sha256=sha(archive),
                   canonical=canonical, status='roundtrip-verified-raw-still-present')
        report['entries'].append(row)
        receipt.write_text(json.dumps(report, indent=2) + '\n')
        assert path.resolve(strict=True).is_relative_to(ROOT / 'build/profiling')
        path.unlink()  # One explicitly allowlisted duplicate; archive and canonical both verified.
        row['status'] = 'replaced-with-lossless-archive'
        receipt.write_text(json.dumps(report, indent=2) + '\n')
        if i % 20 == 0:
            print('Verified', i, 'of180 lossless debug archives', flush=True)
    for name, prior in originals.items():
        path = ROOT / name
        assert path.stat().st_size == prior['bytes'] and sha(path) == prior['sha256'], name
    assert all(sha(ROOT / row['archive'], gzip.open) == row['raw_sha256'] for row in report['entries'])
    report.update(completed=True, protected_files_unchanged=True,
                  raw_bytes=sum(t['raw_bytes'] for t in report['entries']),
                  archived_bytes=sum(t['archive_bytes'] for t in report['entries']))
    report['bytes_saved'] = report['raw_bytes'] - report['archived_bytes']
    report['workspace_after'] = workspace_bytes(ROOT)
    assert report['workspace_after'] < 30000000000
    receipt.write_text(json.dumps(report, indent=2) + '\n')
    print('PASS lossless compaction', report['bytes_saved'], 'bytes saved;', len(originals), 'protected files unchanged', flush=True)


if __name__ == '__main__':
    main()
