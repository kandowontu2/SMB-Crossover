"""Reversibly archive the superseded NH checkpoint to keep the 30 GB cap."""
from pathlib import Path
import datetime
import json
import os
from archive_workspace_hz import ROOT, ARCHIVE, bounded, inventory, sha


def records(folder):
    return {p.relative_to(folder).as_posix(): dict(bytes=n, mtime_ns=t, sha256=sha(p))
            for p, n, t in inventory(folder)}


def main():
    source = bounded(ROOT / 'build/checkpoints/meta-knight-nh', ROOT)
    target = bounded(ARCHIVE / 'build/checkpoints/meta-knight-nh', ARCHIVE)
    assert source.is_dir() and not target.exists()
    assert source.drive.lower() == target.drive.lower()
    assert not ARCHIVE.resolve().is_relative_to(ROOT.resolve())
    receipt = json.loads((ROOT / 'workspace-archive.json').read_text())
    assert Path(receipt['archive']).resolve() == ARCHIVE.resolve()
    relative = source.relative_to(ROOT).as_posix()
    assert all(item['relative'] != relative for item in receipt['directories'])
    before = records(source)
    report = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  source=str(source), target=str(target), files=before,
                  bytes=sum(record['bytes'] for record in before.values()),
                  reason='Superseded native Meta checkpoint; current NU remains local and intact.', deleted_files=0)
    out = ROOT / 'build/verification/roster-audio-nv'
    (out / 'historical-checkpoint-archive-plan.json').write_text(json.dumps(report, indent=2) + '\n')
    target.parent.mkdir(parents=True, exist_ok=True)
    os.rename(source, target)
    assert records(target) == before
    item = dict(relative=relative, bytes=report['bytes'], files=len(before))
    receipt['directories'].append(item); receipt['archived_bytes'] += item['bytes']; receipt['archived_files'] += item['files']
    receipt.setdefault('additional_archives', []).append(dict(
        utc=report['utc'], archive=str(ARCHIVE), moves=[item], archived_bytes=item['bytes'],
        all_files_sha256_verified=True, deleted_files=0))
    (ROOT / 'workspace-archive.json').write_text(json.dumps(receipt, indent=2) + '\n')
    report['all_files_sha256_verified'] = True
    (out / 'historical-checkpoint-archive-receipt.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(archived_bytes=report['bytes'], files=len(before), all_files_sha256_verified=True, deleted_files=0)))


if __name__ == '__main__':
    main()
