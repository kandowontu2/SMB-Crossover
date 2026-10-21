"""Prepare a separate reversible plan for sixteen old accepted debug files."""
from pathlib import Path
import ast
import datetime
import gzip
import hashlib
import io
import json
import os
import zlib

ROOT = Path(__file__).resolve().parents[2]
CP = ROOT / 'build/checkpoints'
OWN = ROOT / 'build/verification/root-accepted-dbg48-compaction-preparation-a'
OLD = ROOT / 'build/verification/mm-owned-accepted-checkpoint-lst-plan-20261018'
CHUNK = 256 * 1024


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as file:
        for data in iter(lambda: file.read(CHUNK), b''):
            h.update(data)
    return h.hexdigest()


def walk(folder):
    with os.scandir(folder) as entries:
        for entry in sorted(entries, key=lambda item: item.name):
            path = Path(entry.path)
            assert not entry.is_symlink()
            assert not (hasattr(entry, 'is_junction') and entry.is_junction())
            if entry.is_dir(follow_symlinks=False):
                yield from walk(path)
            elif entry.is_file(follow_symlinks=False):
                yield path
            else:
                raise AssertionError(str(path))


def main():
    assert not OWN.exists(), 'Never overwrite a prepared plan'
    assert digest(OLD / 'compact_restore.py') == '39bc38779092ffbd1a5022cc2278b848a144ff160fe83f1eeb504f27625613c4'
    assert digest(OLD / 'allowlist.json') == '741971120e7512807f18b7440f6a5543acb7ff3b22a5de3aa47e51e880f0d164'
    old = json.loads((OLD / 'allowlist.json').read_text())
    selected = []
    for previous in old['allowlist']:
        entry = {key: previous[key] for key in ('checkpoint', 'version', 'manifest', 'manifest_sha256', 'status', 'rom', 'rom_sha256')}
        raw = ROOT / previous['raw'].replace('.lst', '.dbg')
        assert raw.resolve().is_relative_to(CP.resolve())
        assert raw.parent.name == entry['checkpoint'] and raw.suffix == '.dbg'
        assert raw.is_file() and not Path(str(raw) + '.gz').exists()
        assert digest(ROOT / entry['manifest']) == entry['manifest_sha256']
        assert digest(ROOT / entry['rom']) == entry['rom_sha256']
        stat = raw.stat()
        buffer = io.BytesIO()
        with gzip.GzipFile(filename='', fileobj=buffer, mode='wb', mtime=0, compresslevel=9) as archive:
            with raw.open('rb') as source:
                for data in iter(lambda: source.read(CHUNK), b''):
                    archive.write(data)
        compressed = buffer.getvalue()
        original_sha = digest(raw)
        restored = gzip.decompress(compressed)
        assert len(restored) == stat.st_size and hashlib.sha256(restored).hexdigest() == original_sha
        relative = raw.relative_to(ROOT).as_posix()
        entry.update(raw=relative, archive=relative + '.gz', raw_bytes=stat.st_size,
            raw_sha256=original_sha, raw_mode=stat.st_mode, raw_mtime_ns=stat.st_mtime_ns,
            gzip_bytes=len(compressed), gzip_sha256=hashlib.sha256(compressed).hexdigest())
        selected.append(entry)
    assert len(selected) == 16
    allowed = {entry['raw'] for entry in selected}
    protected = []
    for path in walk(CP):
        relative = path.relative_to(ROOT).as_posix()
        if relative not in allowed:
            protected.append(dict(path=relative, bytes=path.stat().st_size, sha256=digest(path)))
    raw_bytes = sum(entry['raw_bytes'] for entry in selected)
    gzip_bytes = sum(entry['gzip_bytes'] for entry in selected)
    plan = dict(workspace=str(ROOT), created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        status='prepared-not-applied', scope='Exactly sixteen canonical old accepted35,36,37,39,40,41,42,43 DBG files; no route artifacts or negatives.',
        compression=dict(kind='gzip', level=9, mtime=0, zlib=zlib.ZLIB_VERSION),
        allowlist=selected, protected_files=protected,
        summary=dict(raw_bytes=raw_bytes, estimated_gzip_bytes=gzip_bytes,
            estimated_savings_bytes=raw_bytes-gzip_bytes))
    OWN.mkdir()
    plan_path = OWN / 'allowlist.json'
    plan_path.write_text(json.dumps(plan, indent=2) + '\n')
    script = (OLD / 'compact_restore.py').read_text()
    script = script.replace(str(OLD.relative_to(ROOT)).replace('\\', '/'), str(OWN.relative_to(ROOT)).replace('\\', '/'))
    script = script.replace('741971120e7512807f18b7440f6a5543acb7ff3b22a5de3aa47e51e880f0d164', digest(plan_path))
    script = script.replace('lst', 'dbg').replace('LST', 'DBG').replace('listing', 'debug')
    script_path = OWN / 'compact_restore.py'
    ast.parse(script)
    script_path.write_text(script)
    # Confirm the generated script is still restricted to canonical old DBG paths.
    assert 'mmc[35]\\.dbg' in script and 'raw.unlink()' in script
    receipt = dict(status='prepared-not-applied', script_sha256=digest(script_path),
        allowlist_sha256=digest(plan_path), count=len(selected), protected_files=len(protected),
        summary=plan['summary'], preparation_script_sha256=digest(Path(__file__)),
        constraints='Root reviews before execution; no recursive deletion; all sixteen validated gzip backups before raw unlink; exact-byte restore; current checkpoint/ROM/source/negative/route files protected.')
    (OWN / 'receipt-plan.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
