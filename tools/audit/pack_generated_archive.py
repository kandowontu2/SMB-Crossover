"""Losslessly compact closed, generated evidence; never restore deleted files.

Each ZIP member carries the source SHA-256/size/mtime. Verify every member
before removing any extracted copy, then recheck each source before unlinking.
Active dependencies, video containers and ROM files stay expanded.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import time
import zipfile

from capture_budget import ARCHIVE, MINIMUM_FREE, capture_lease

D = '2026-10-24-native-rest-py/'
KEEP = tuple(D+p for p in (
    'root-current-roster-composition-v1',
    'root-render-audio-palette-hud-union-v2',
    'root-sound-test-menu-v7',
    'current3b-cheats-four-draft-v8',
    'currentce635-default-HUD-handoff-v1',
    'bass-hard-corner-source-geometry-v1',
    'bass-hard-displacement-diagnostic-final-v1',
    'bass-hard-displacement-diagnostic-ready-v3/native',
    'mmc3-flag-fix-v23/script-budget-probe-v2/emulator',
    'mmc3-flag-fix-v23/script-budget-probe-v2/proof.json',
    'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1',
    'final-tmnt-items-v1/lua-parser-deps-v1',
))
KEEP_SUFFIX = {'.nes', '.mp4', '.mkv', '.mov', '.avi', '.swf'}
PACKED = ARCHIVE/'_packed-evidence-2026-10-26'
ZIP_CAP = 8_000_000_000


def sha_stream(stream):
    digest = hashlib.sha256()
    while chunk := stream.read(1024*1024):
        digest.update(chunk)
    return digest.hexdigest()


def sha(path):
    with path.open('rb') as stream:
        return sha_stream(stream)


def kept(path):
    relative = path.relative_to(ARCHIVE).as_posix()
    return path.suffix.lower() in KEEP_SUFFIX or any(
        relative == p or relative.startswith(p+'/') for p in KEEP)


def bounded(path):
    resolved = path.resolve()
    assert resolved != ARCHIVE.resolve() and resolved.is_relative_to(ARCHIVE.resolve())
    return resolved


def files(root):
    pending = [root]
    while pending:
        with os.scandir(pending.pop()) as entries:
            for entry in entries:
                if entry.is_symlink() or os.path.isjunction(entry.path):
                    continue
                path = Path(entry.path)
                if kept(path):
                    continue
                if entry.is_dir(follow_symlinks=False):
                    pending.append(path)
                elif entry.is_file(follow_symlinks=False):
                    yield bounded(path)


def pack(root):
    root = bounded(root)
    assert root.parent == ARCHIVE.resolve() and root.is_dir()
    assert re.fullmatch(r'2026-10-(24|26)-[a-zA-Z0-9-]+|play-vic-turtles-nd', root.name)
    PACKED.mkdir(exist_ok=True)
    final = PACKED/(root.name+'.zip')
    partial = final.with_suffix('.partial')
    receipt = final.with_suffix('.json')
    assert not final.exists() and not partial.exists() and not receipt.exists(), 'Never overwrite a compaction.'
    counts = dict(files=0, source_bytes=0, removed_files=0, removed_bytes=0)
    last = time.monotonic()
    with zipfile.ZipFile(partial, 'x', compression=zipfile.ZIP_DEFLATED,
                         compresslevel=1, allowZip64=True) as archive:
        for path in files(root):
            before = path.stat()
            name = path.relative_to(ARCHIVE).as_posix()
            member = zipfile.ZipInfo(name)
            member.compress_type = zipfile.ZIP_DEFLATED
            member.compress_level = 1
            digest = hashlib.sha256()
            with path.open('rb') as source, archive.open(member, 'w', force_zip64=True) as dest:
                while chunk := source.read(1024*1024):
                    digest.update(chunk)
                    dest.write(chunk)
                    if archive.fp.tell() > ZIP_CAP or shutil.disk_usage(PACKED).free < MINIMUM_FREE:
                        raise RuntimeError('Compaction output/free-space limit reached; no source removed.')
            assert path.stat().st_size == before.st_size and path.stat().st_mtime_ns == before.st_mtime_ns
            member.comment = json.dumps(dict(sha256=digest.hexdigest(), bytes=before.st_size,
                                            mtime_ns=before.st_mtime_ns), separators=(',', ':')).encode()
            counts['files'] += 1
            counts['source_bytes'] += before.st_size
            assert counts['files'] <= 2_000_000, 'Bounded compaction inventory exceeded; no source removed.'
            if time.monotonic()-last > 25:
                print(json.dumps(dict(group=root.name, phase='packing', **counts)), flush=True)
                last = time.monotonic()
    # No extraction/deletion is permitted until the COMPLETE archive is verified.
    with zipfile.ZipFile(partial) as archive:
        for member in archive.infolist():
            expected = json.loads(member.comment)
            with archive.open(member) as stream:
                assert sha_stream(stream) == expected['sha256'], member.filename
            assert member.file_size == expected['bytes']
    assert partial.stat().st_size <= ZIP_CAP
    partial.rename(final)
    changed = []
    with zipfile.ZipFile(final) as archive:
        for member in archive.infolist():
            path = bounded(ARCHIVE/member.filename)
            assert path.is_relative_to(root) and not kept(path)
            expected = json.loads(member.comment)
            if not path.exists():
                continue  # Do not restore anything the user removed during packing.
            current = path.stat()
            if (current.st_size != expected['bytes'] or current.st_mtime_ns != expected['mtime_ns']
                    or sha(path) != expected['sha256']):
                changed.append(member.filename)
                continue
            path.unlink()
            counts['removed_files'] += 1
            counts['removed_bytes'] += expected['bytes']
    # Empty generated directories only; keep paths and reparse targets untouched.
    def empty_dirs(folder):
        with os.scandir(folder) as entries:
            children = [Path(e.path) for e in entries if e.is_dir(follow_symlinks=False)
                        and not e.is_symlink() and not os.path.isjunction(e.path)]
        for child in children:
            if not kept(child):
                empty_dirs(bounded(child))
        if not kept(folder):
            try:
                bounded(folder).rmdir()
            except OSError:
                pass  # Nonempty folders contain retained ROMs/video/changed files.
    empty_dirs(root)
    result = dict(schema=1, root=str(root), archive=str(final), archive_bytes=final.stat().st_size,
                  archive_sha256=sha(final), all_members_sha256_verified=True, changed_sources_retained=changed,
                  active_paths_kept=KEEP, video_and_rom_files_kept=True, user_deleted_files_restored=0, **counts)
    receipt.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument('--group')
    choice.add_argument('--all-closed', action='store_true',
                        help='Pack existing generated groups, respecting all active keepers.')
    args = parser.parse_args()
    if args.group:
        assert Path(args.group).name == args.group
        groups = [ARCHIVE/args.group]
    else:
        groups = sorted(p for p in ARCHIVE.iterdir() if p.is_dir() and re.fullmatch(
            r'2026-10-(24|26)-[a-zA-Z0-9-]+|play-vic-turtles-nd', p.name))
    with capture_lease():
        for group in groups:
            if not group.exists():
                continue
            if (PACKED/(group.name+'.json')).exists():
                continue  # An immutable completed receipt is never overwritten.
            pack(group)


if __name__ == '__main__':
    main()
