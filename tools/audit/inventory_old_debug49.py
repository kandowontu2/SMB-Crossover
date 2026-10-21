"""Read-only inventory of non-route old compiler debug storage candidates."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import re

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'build/verification/root-old-debug49-storage-inventory-b.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def walk(folder):
    with os.scandir(folder) as entries:
        for e in entries:
            if e.is_symlink() or e.stat(follow_symlinks=False).st_file_attributes & 0x400:
                continue
            if e.is_dir(follow_symlinks=False):
                yield from walk(e.path)
            elif e.is_file(follow_symlinks=False):
                yield Path(e.path)


def main():
    assert not OUT.exists()
    canonical = {}
    for version in range(1, 48):
        folder = ROOT / f'build/checkpoints/roster-audit-v{version}'
        manifest = folder / 'manifest.json'
        if not manifest.exists():
            continue
        data = json.loads(manifest.read_text())
        roms = data.get('roms', data)
        for mapper in ('mmc3', 'mmc5'):
            rom = folder / f'smb-crossover-{mapper}.nes'
            if not rom.exists():
                continue
            rh = sha(rom)
            if roms.get(rom.name, roms.get(mapper)) != rh:
                continue
            debug = rom.with_suffix('.dbg')
            storage = 'raw'
            if not debug.exists():
                debug = Path(str(debug) + '.gz')
                storage = 'gzip'
            if not debug.exists():
                continue
            raw = debug.read_bytes()
            if storage == 'gzip':
                raw = gzip.decompress(raw)
            canonical.setdefault(rh, []).append(dict(version=version, ROM=str(rom.relative_to(ROOT)),
                manifest=str(manifest.relative_to(ROOT)), manifest_sha256=sha(manifest),
                debug=str(debug.relative_to(ROOT)), debug_storage=storage, debug_sha256=hashlib.sha256(raw).hexdigest()))
    rows = []
    for raw in walk(ROOT / 'build'):
        if raw.suffix != '.dbg' or raw.stat().st_size < 1_000_000:
            continue
        n = str(raw.relative_to(ROOT))
        if re.search(r'(?<!\d)(?:48|49)(?!\d)', n):
            continue
        if any(t in n.lower() for t in ('roster-through-2-2', 'playthrough', 'route', 'negative', 'failure', 'failed', 'capture', 'recording')):
            continue
        rom = raw.with_suffix('.nes')
        if not rom.exists():
            continue
        rh = sha(rom)
        if rh not in canonical:
            continue
        dh = sha(raw)
        same = [r for r in canonical[rh] if r['debug_sha256'] == dh]
        rows.append(dict(path=n, bytes=raw.stat().st_size, sha256=dh, sibling_ROM=str(rom.relative_to(ROOT)),
                         ROM_sha256=rh, canonical=same or canonical[rh],
                         exact_debug_counterpart=bool(same), completion_not_yet_qualified=True))
    report = dict(status='read-only-inventory-not-a-compaction-plan', files=len(rows),
                  bytes=sum(r['bytes'] for r in rows), exact_debug_files=sum(r['exact_debug_counterpart'] for r in rows),
                  exact_debug_bytes=sum(r['bytes'] for r in rows if r['exact_debug_counterpart']), rows=rows,
                  files_changed=0, deletion_authorized=False)
    OUT.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'rows'}))


if __name__ == '__main__':
    main()
