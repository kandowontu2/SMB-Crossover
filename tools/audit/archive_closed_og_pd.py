"""Retain superseded OG externally before another private source checkpoint."""
from pathlib import Path
import datetime
import json
import os
from archive_workspace_hz import ROOT, ARCHIVE, bounded, inventory, sha


def records(folder):
    return {p.relative_to(folder).as_posix(): dict(bytes=n, mtime_ns=t, sha256=sha(p))
            for p, n, t in inventory(folder)}


def main():
    qa = ROOT / 'build/verification/smb3-shrink-pc'
    qa.mkdir(exist_ok=True)
    assert not (qa / 'historical-archive-receipt.json').exists()
    receipt = json.loads((ROOT / 'workspace-archive.json').read_text())
    assert Path(receipt['archive']).resolve() == ARCHIVE.resolve()
    assert not ARCHIVE.resolve().is_relative_to(ROOT.resolve())
    protected = {str(p): sha(p) for p in [
        ROOT / 'build/checkpoints/render-dispatch-ov/candidate.nes', ROOT / 'build/checkpoints/render-dispatch-ov/source.zip',
        ROOT / 'build/checkpoints/collision-dispatch-oj/candidate.nes', ROOT / 'build/checkpoints/collision-dispatch-oj/source.zip',
        ROOT / 'build/checkpoints/injury-page-of/candidate.nes', ROOT / 'build/checkpoints/injury-page-of/source.zip',
        *[ROOT / f'build/smb-crossover-{name}.nes' for name in ('mmc3', 'mmc5', 'mmc3-oversized', 'mmc5-expanded')]]}
    relative = 'build/checkpoints/inventory-stack-og'
    source = bounded(ROOT / relative, ROOT / 'build/checkpoints')
    target = bounded(ARCHIVE / relative, ARCHIVE)
    assert source.is_dir() and not target.exists() and source.drive.lower() == target.drive.lower()
    assert not any(r['relative'] == relative for r in receipt['directories'])
    files = records(source)
    size = sum(r['bytes'] for r in files.values())
    report = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), source=str(source), target=str(target),
                  relative=relative, bytes=size, files=files, deleted_files=0,
                  reason='OG is superseded by current OV and its immediate parent OJ. Both remain local, along with OF, live source, public ROMs and the guide. Every archived byte remains available through workspace_storage.py.')
    (qa / 'historical-archive-plan.json').write_text(json.dumps(report, indent=2) + '\n')
    target.parent.mkdir(parents=True, exist_ok=True)
    os.rename(source, target)
    assert records(target) == files
    assert all(sha(Path(p)) == h for p, h in protected.items())
    move = dict(relative=relative, bytes=size, files=len(files))
    receipt['directories'].append(move)
    receipt['archived_bytes'] += size
    receipt['archived_files'] += len(files)
    receipt.setdefault('additional_archives', []).append(dict(utc=report['utc'], archive=str(ARCHIVE), moves=[move],
        archived_bytes=size, all_files_sha256_verified=True, deleted_files=0))
    (ROOT / 'workspace-archive.json').write_text(json.dumps(receipt, indent=2) + '\n')
    report.update(all_files_sha256_verified=True, protected_files=protected)
    (qa / 'historical-archive-receipt.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(archived_bytes=size, files=len(files), deleted_files=0, all_files_sha256_verified=True), indent=2))


if __name__ == '__main__':
    main()
