"""One-time, reversible archive for the user's 30 GB workspace request.

Only historical build evidence moves, by same-volume directory rename. Source,
current checkpoints, current root replay work, and all posting videos stay put.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import stat

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-22-workspace-cleanup')
REPORT = ROOT / 'build/verification/workspace-cleanup-hz'
CAP = 30_000_000_000


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def inventory(directory, *, skip_reparse=False):
    pending = [directory]
    while pending:
        with os.scandir(pending.pop()) as entries:
            for e in entries:
                info = e.stat(follow_symlinks=False)
                if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
                    if skip_reparse:
                        continue
                    raise RuntimeError(f'Reparse point requires separate review: {e.path}')
                if stat.S_ISDIR(info.st_mode):
                    pending.append(Path(e.path))
                elif stat.S_ISREG(info.st_mode):
                    yield Path(e.path), info.st_size, info.st_mtime_ns


def bounded(path, parent):
    resolved = path.resolve()
    relative = resolved.relative_to(parent.resolve())
    assert relative.parts, 'Cannot move the root itself'
    return resolved


def main():
    assert ROOT.resolve() == Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover').resolve()
    assert not ARCHIVE.resolve().is_relative_to(ROOT.resolve())
    assert ROOT.drive.lower() == ARCHIVE.drive.lower(), 'Same-volume atomic moves only'
    assert not (REPORT / 'receipt.json').exists(), 'Already archived; do not repeat'
    REPORT.mkdir(parents=True, exist_ok=True)
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    roots = []
    roster = ROOT / 'build/roster-through-2-2'
    roots += [p for p in roster.iterdir() if p.is_dir()
              and p.name != 'search' and not p.name.startswith('root-')]
    roots += [p for p in (roster / 'search').iterdir() if p.is_dir()
              and not p.name.startswith('bass-')]
    roots += [ROOT / 'build' / n for n in ('playthroughs', 'profiling', 'checkpoint-tests')]
    retained_checkpoints = {'roster-audit-v49-green-suite',
                            'roster-audit-v49-sophia-block-origin-hu',
                            'roster-audit-v49-menu-options-s2'}
    roots += [p for p in (ROOT / 'build/checkpoints').iterdir() if p.is_dir()
              and p.name.startswith('roster-audit-v') and p.name not in retained_checkpoints]
    roots.sort()
    all_files = {}
    before_bytes = sum(size for _, size, _ in inventory(ROOT, skip_reparse=True))
    protected = {}
    for directory in ('src', 'inc', 'chr', 'audio', 'tools', 'tests', 'reference'):
        for path, _, _ in inventory(ROOT / directory):
            protected[path.relative_to(ROOT).as_posix()] = sha(path)
    for name in ('README.md', 'smb1base.cfg', 'build_options.ini',
                 'build/smb-crossover-mmc3.nes', 'build/smb-crossover-mmc5.nes',
                 'build/checkpoints/ryu-overlap-hr/manifest.json',
                 'build/checkpoints/weapons-source-go/manifest.json',
                 'build/checkpoints/rygar-world-palette-ga/manifest.json'):
        protected[name] = sha(ROOT / name)
    (REPORT / 'protected-before.json').write_text(json.dumps(protected, indent=2) + '\n')
    plan = []
    for source in roots:
        source = bounded(source, ROOT / 'build')
        rel = source.relative_to(ROOT)
        destination = bounded(ARCHIVE / rel, ARCHIVE)
        assert not destination.exists(), f'Archive destination already exists: {destination}'
        files = list(inventory(source))
        for p, size, mtime in files:
            key = p.relative_to(ROOT).as_posix()
            assert key not in all_files
            all_files[key] = (size, mtime)
        plan.append(dict(relative=rel.as_posix(), bytes=sum(v[1] for v in files), files=len(files)))
    planned = sum(p['bytes'] for p in plan)
    assert before_bytes - planned < 27_000_000_000, 'Need useful headroom below 30 GB'
    (REPORT / 'plan.json').write_text(json.dumps(dict(workspace_bytes_before=before_bytes,
        archive=str(ARCHIVE), archive_bytes=planned, directories=plan), indent=2) + '\n')
    with (ARCHIVE / 'file-inventory.jsonl').open('x', encoding='utf-8') as f:
        for rel, (size, mtime) in sorted(all_files.items()):
            f.write(json.dumps(dict(path=rel, bytes=size, mtime_ns=mtime)) + '\n')
    print(f'Validated plan: {len(plan)} directories, {len(all_files)} files, {planned:,} bytes', flush=True)
    with (ARCHIVE / 'moves.jsonl').open('x', encoding='utf-8') as journal:
        for n, item in enumerate(plan, 1):
            source = bounded(ROOT / item['relative'], ROOT / 'build')
            destination = bounded(ARCHIVE / item['relative'], ARCHIVE)
            assert source.is_dir() and not destination.exists()
            destination.parent.mkdir(parents=True, exist_ok=True)
            # Atomic same-volume rename preserves the directory and file contents.
            os.rename(source, destination)
            journal.write(json.dumps(item) + '\n')
            journal.flush()
            if n % 250 == 0:
                print(f'Archived {n}/{len(plan)} directories', flush=True)
    found = {}
    media_hashes = {}
    for item in plan:
        for p, size, mtime in inventory(ARCHIVE / item['relative']):
            rel = p.relative_to(ARCHIVE).as_posix()
            assert all_files[rel] == (size, mtime), f'Archived metadata mismatch: {rel}'
            found[rel] = (size, mtime)
            if p.suffix.lower() in ('.avi', '.wav', '.mkv', '.mp4'):
                media_hashes[rel] = sha(p)
    assert found == all_files, 'Archive file census must be complete'
    assert all(sha(ROOT / rel) == digest for rel, digest in protected.items()), 'Protected file changed'
    (ARCHIVE / 'media-sha256.json').write_text(json.dumps(media_hashes, indent=2) + '\n')
    after_bytes = sum(size for _, size, _ in inventory(ROOT, skip_reparse=True))
    assert after_bytes < CAP
    receipt = dict(schema=1, utc=datetime.now(timezone.utc).isoformat(),
        workspace=str(ROOT), archive=str(ARCHIVE), cap_bytes=CAP,
        workspace_bytes_before=before_bytes, workspace_bytes_after=after_bytes,
        archived_bytes=planned, archived_files=len(all_files), directories=plan,
        deleted_files=0, lossless_recordings_retained=True,
        all_archived_file_sizes_and_mtimes_verified=True,
        media_sha256_files=len(media_hashes), protected_files_verified=len(protected),
        inventory_sha256=sha(ARCHIVE / 'file-inventory.jsonl'))
    text = json.dumps(receipt, indent=2) + '\n'
    (ARCHIVE / 'receipt.json').write_text(text)
    (REPORT / 'receipt.json').write_text(text)
    (ROOT / 'workspace-archive.json').write_text(text)
    print(json.dumps({k:v for k,v in receipt.items() if k != 'directories'}, indent=2), flush=True)


if __name__ == '__main__':
    main()
