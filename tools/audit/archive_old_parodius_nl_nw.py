"""Reversible archive of superseded NL; retain newer NR/NS checkpoints locally."""
from pathlib import Path
import datetime
import json
import os
from archive_workspace_hz import ROOT, ARCHIVE, bounded, inventory, sha


def records(folder):
    return {p.relative_to(folder).as_posix(): dict(bytes=n, mtime_ns=t, sha256=sha(p))
            for p, n, t in inventory(folder)}


def main():
    relative = 'build/checkpoints/parodius-integration-nl'
    source = bounded(ROOT / relative, ROOT); target = bounded(ARCHIVE / relative, ARCHIVE)
    assert source.is_dir() and not target.exists() and source.drive.lower() == target.drive.lower()
    assert not ARCHIVE.resolve().is_relative_to(ROOT.resolve())
    receipt = json.loads((ROOT / 'workspace-archive.json').read_text())
    assert Path(receipt['archive']).resolve() == ARCHIVE.resolve()
    assert all(item['relative'] != relative for item in receipt['directories'])
    files = records(source); total = sum(item['bytes'] for item in files.values())
    qa = ROOT / 'build/verification/vic-hud-nw'; qa.mkdir(exist_ok=True)
    report = dict(source=str(source), target=str(target), utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  bytes=total, files=files, deleted_files=0,
                  reason='Historical initial Parodius integration; newer NR/NS and current NU/NV remain local.')
    (qa / 'historical-archive-plan.json').write_text(json.dumps(report, indent=2) + '\n')
    target.parent.mkdir(parents=True, exist_ok=True); os.rename(source, target)
    assert records(target) == files
    item = dict(relative=relative, bytes=total, files=len(files))
    receipt['directories'].append(item); receipt['archived_bytes'] += total; receipt['archived_files'] += len(files)
    receipt.setdefault('additional_archives', []).append(dict(utc=report['utc'], archive=str(ARCHIVE), moves=[item],
        archived_bytes=total, all_files_sha256_verified=True, deleted_files=0))
    (ROOT / 'workspace-archive.json').write_text(json.dumps(receipt, indent=2) + '\n')
    report['all_files_sha256_verified'] = True
    (qa / 'historical-archive-receipt.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(archived_bytes=total, files=len(files), deleted_files=0, all_files_sha256_verified=True)))


if __name__ == '__main__':
    main()
