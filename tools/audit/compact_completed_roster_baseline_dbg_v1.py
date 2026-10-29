"""Losslessly compress twelve completed baseline debug outputs, never candidates."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'build/verification/roster-old-baseline-debug-compaction-v1.json'
FOLDERS = ['dragon-power-admission-v1', 'dragon-power-gameplay-v1',
           'dragon-power-hud-budget-v1', 'dragon-power-movement-v1',
           'dragon-power-platform-v1', 'pit-retold-host-v2']
BASELINES = {
    'ordinary-mmc3': 'd444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb',
    'ordinary-mmc5': 'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833',
}


def sha(path, compressed=False):
    result = hashlib.sha256()
    with (gzip.open if compressed else open)(path, 'rb') as source:
        for data in iter(lambda: source.read(1_048_576), b''):
            result.update(data)
    return result.hexdigest()


def safe(path):
    assert path.resolve().is_relative_to(ROOT / 'build')
    for parent in (path, *path.parents):
        if parent == ROOT:
            break
        assert not parent.is_symlink() and not parent.is_junction()
    assert path.parent.name in FOLDERS
    assert path.name in {name + suffix for name in BASELINES for suffix in ['.dbg', '.dbg.gz']}
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--restore', action='store_true')
    args = parser.parse_args()
    if args.restore:
        receipt = json.loads(OUT.read_text())
        assert receipt['completed'] and len(receipt['entries']) == 12
        for row in receipt['entries']:
            original, archive = safe(ROOT / row['original']), safe(ROOT / row['archive'])
            assert not original.exists() and sha(archive, True) == row['original_sha256']
            with gzip.open(archive, 'rb') as source, original.open('xb') as dest:
                for data in iter(lambda: source.read(1_048_576), b''):
                    dest.write(data)
            assert sha(original) == row['original_sha256']
        print('Restored twelve exact original debug outputs; archives retained')
        return
    assert not OUT.exists()
    protected = {}
    targets = []
    for folder in FOLDERS:
        parent = ROOT / 'build' / folder
        for name, expected in BASELINES.items():
            path = safe(parent / (name + '.dbg'))
            assert path.exists() and not path.with_suffix('.dbg.gz').exists()
            rom = path.with_suffix('.nes')
            assert sha(rom) == expected
            targets.append(path)
        for name in ['candidate.nes', 'candidate.dbg', 'candidate.lbl', 'handoff.json',
                     'ordinary-mmc3.nes', 'ordinary-mmc5.nes']:
            path = parent / name
            assert path.exists()
            protected[str(path.relative_to(ROOT))] = sha(path)
    assert len(targets) == 12
    receipt = dict(completed=False, entries=[], protected=protected,
                   scope='Only ordinary flag-off baseline DBG outputs in six completed private units. '
                         'All candidate triples, source, receipts, ROMs and lossless gameplay remain. '
                         'Older receipts referencing raw baseline DBGs require --restore before direct path verification.')
    def save():
        OUT.write_text(json.dumps(receipt, indent=2) + '\n')
    save()
    for path in targets:
        raw_sha, raw_bytes = sha(path), path.stat().st_size
        archive = safe(path.with_suffix('.dbg.gz'))
        with path.open('rb') as source, gzip.open(archive, 'xb', compresslevel=6) as dest:
            for data in iter(lambda: source.read(1_048_576), b''):
                dest.write(data)
        assert sha(archive, True) == raw_sha and archive.stat().st_size < raw_bytes
        row = dict(original=str(path.relative_to(ROOT)), original_sha256=raw_sha,
                   original_bytes=raw_bytes, archive=str(archive.relative_to(ROOT)),
                   archive_sha256=sha(archive), archive_bytes=archive.stat().st_size,
                   status='roundtrip-verified-original-present')
        receipt['entries'].append(row)
        save()
        assert sha(safe(path)) == raw_sha
        path.unlink()
        row['status'] = 'losslessly-compressed'
        save()
    assert all(sha(ROOT / name) == expected for name, expected in protected.items())
    assert all(sha(ROOT / row['archive'], True) == row['original_sha256'] for row in receipt['entries'])
    receipt.update(completed=True, bytes_saved=sum(
        row['original_bytes'] - row['archive_bytes'] for row in receipt['entries']))
    save()
    print(json.dumps(dict(receipt=str(OUT), files=12, bytes_saved=receipt['bytes_saved'])))


if __name__ == '__main__':
    main()
