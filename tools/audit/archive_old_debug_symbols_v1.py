"""Losslessly archive old build debug symbols, with verified exact restoration.

Native captures, source, ROMs, labels and recent/current debug symbols are never
selected. Every archive is decompressed and hashed before its original is removed.
"""
from pathlib import Path
import argparse
import datetime
import gzip
import hashlib
import json
import os

R = Path(__file__).resolve().parents[2]
B = R / 'build'
A = B / 'debug-symbol-archive-v1'
J = A / 'journal.jsonl'
KEEP = {'smb-crossover-mmc5-expanded.dbg', 'bill_capsule_hud44204.dbg',
        'bill_inert_pool.dbg', 'zelda2_easy_glove.dbg', 'bill_walk_clock.dbg'}


def digest(path, compressed=False):
    h = hashlib.sha256()
    with (gzip.open(path, 'rb') if compressed else path.open('rb')) as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def journal():
    return [json.loads(s) for s in J.read_text().splitlines()] if J.exists() else []


def eligible():
    cutoff = datetime.datetime(2026, 10, 27).timestamp()
    return sorted(p for p in B.rglob('*.dbg') if p.relative_to(B).as_posix() not in KEEP
                  and not (p.parent == B and p.name.startswith('smb-crossover-'))
                  and not p.is_relative_to(A)
                  and p.stat().st_mtime < cutoff)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    op = ap.add_mutually_exclusive_group(required=True)
    op.add_argument('--plan', action='store_true')
    op.add_argument('--archive', action='store_true')
    op.add_argument('--restore', metavar='BUILD_RELATIVE_PATH')
    op.add_argument('--verify', action='store_true')
    args = ap.parse_args()
    if args.plan:
        files = eligible()
        print(json.dumps(dict(files=len(files), bytes=sum(p.stat().st_size for p in files),
            cutoff_local='2026-10-27T00:00:00', protected=sorted(KEEP),
            never_selected=['captures', 'source', 'ROMs', 'labels', 'recent symbols'])))
        return
    if args.archive:
        A.mkdir(exist_ok=True)
        files = eligible()
        assert len(files) <= 750
        prior = journal()
        done = {q['name'] for q in prior}
        total_saved = 0
        for i, p in enumerate(files):
            assert p.resolve().is_relative_to(B.resolve()) and p.suffix == '.dbg'
            name = p.relative_to(B).as_posix()
            if name in done:
                q = next(q for q in reversed(prior) if q['name'] == name)
                assert digest(p) == q['sha256'], 'Restored file changed; leave it alone'
                continue
            stat = p.stat()
            original_hash = digest(p)
            dest = A / (hashlib.sha256(name.encode()).hexdigest()[:20] + '-' + p.name + '.gz')
            assert not dest.exists(), 'Preserve unjournaled archive for investigation'
            tmp = dest.with_suffix('.gz.partial')
            assert not tmp.exists()
            with p.open('rb') as src, tmp.open('wb') as disk:
                with gzip.GzipFile(filename='', mode='wb', fileobj=disk, mtime=0, compresslevel=6) as out:
                    while chunk := src.read(1024 * 1024):
                        out.write(chunk)
            assert digest(tmp, True) == original_hash
            assert digest(p) == original_hash and p.stat().st_mtime_ns == stat.st_mtime_ns
            os.replace(tmp, dest)
            q = dict(name=name, sha256=original_hash, bytes=stat.st_size,
                     mtime_ns=stat.st_mtime_ns, archive=dest.name,
                     archive_sha256=digest(dest), archive_bytes=dest.stat().st_size,
                     decompressed_verified=True)
            # Durable recovery metadata precedes removal; all paths stay in build.
            with J.open('a', encoding='utf-8', newline='\n') as f:
                f.write(json.dumps(q) + '\n')
                f.flush()
                os.fsync(f.fileno())
            assert p.resolve().is_relative_to(B.resolve())
            p.unlink()
            total_saved += q['bytes'] - q['archive_bytes']
            if (i + 1) % 20 == 0:
                print(json.dumps(dict(archived=i + 1, selected=len(files), saved_bytes=total_saved)), flush=True)
        print(json.dumps(dict(finished=True, selected=len(files), saved_bytes=total_saved,
                              journal=str(J), captures_removed=0)), flush=True)
        return
    rows = journal()
    assert rows
    if args.verify:
        for q in rows:
            dest = A / q['archive']
            assert digest(dest) == q['archive_sha256'] and digest(dest, True) == q['sha256']
        print(json.dumps(dict(passed=True, verified_archives=len(rows),
                              original_bytes=sum(q['bytes'] for q in rows),
                              archived_bytes=sum(q['archive_bytes'] for q in rows))))
        return
    assert not Path(args.restore).is_absolute() and args.restore.endswith('.dbg')
    q = next(q for q in rows if q['name'] == args.restore)
    dest = B / q['name']
    assert dest.resolve().is_relative_to(B.resolve())
    if dest.exists():
        assert digest(dest) == q['sha256']
        print(json.dumps(dict(already_restored=True, path=str(dest))))
        return
    src = A / q['archive']
    assert digest(src) == q['archive_sha256']
    tmp = dest.with_suffix('.dbg.restoring')
    assert not tmp.exists()
    with gzip.open(src, 'rb') as packed, tmp.open('wb') as out:
        while chunk := packed.read(1024 * 1024):
            out.write(chunk)
    assert tmp.stat().st_size == q['bytes'] and digest(tmp) == q['sha256']
    os.replace(tmp, dest)
    os.utime(dest, ns=(q['mtime_ns'], q['mtime_ns']))
    print(json.dumps(dict(restored=True, path=str(dest), sha256=digest(dest))))


if __name__ == '__main__':
    main()
