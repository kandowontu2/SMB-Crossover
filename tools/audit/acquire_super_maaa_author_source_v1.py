"""Fetch bounded, commit-pinned SuperMaaa author source leaves; no ROMs."""
from pathlib import Path
import hashlib
import json
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'build/source-acquisition/super-maaa-author-2026-10-29'
COMMIT = '472735118e2b4fa1b9d3cc36395b947fed466e80'
TREE_SHA256 = 'b4b68aff59c9934ca7a654b8c294632e25ae889a9a8a752be5e96881fd18aa40'
FILES = [
    'CMakeLists.txt', 'cmake/GenerateLinkerScript.cmake', 'cmake/cc65-toolchain.cmake',
    'inc/charmap.inc', 'inc/common.inc', 'inc/constants.inc', 'inc/globals.inc',
    'inc/memory.inc', 'inc/mmc3.inc', 'inc/nes2header.inc', 'inc/player.inc',
    'src/chr.s', 'src/collision.s', 'src/common.s', 'src/gamecore.s', 'src/gamemode.s',
    'src/memory.s', 'src/mmc3.s', 'src/nes.cfg', 'src/nesheader.s', 'src/player.s',
    'src/reset.s', 'src/sprite_render.s', 'chr/lanky_mario.chr',
    'chr/lanky_mario_5px.chr', 'chr/mario_edit.chr', 'chr/neck.chr',
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    raw = (OUT / 'tree.json').read_bytes()
    assert sha(raw) == TREE_SHA256
    tree = json.loads(raw)
    assert not tree.get('truncated')
    by_path = {row['path']: row for row in tree['tree'] if row['type'] == 'blob'}
    assert len(FILES) <= 30 and sum(by_path[name]['size'] for name in FILES) < 1_000_000
    records = []
    for name in FILES:
        row = by_path[name]
        path = OUT / 'source' / name
        url = f'https://raw.githubusercontent.com/jroweboy/smb1base/{COMMIT}/{name}'
        if path.exists():
            data = path.read_bytes()
        else:
            request = urllib.request.Request(url, headers={'User-Agent': 'SMBCrossover-source-audit'})
            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read(row['size'] + 1)
        assert len(data) == row['size'], name
        assert hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == row['sha'], name
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        records.append(dict(path=str(path), source_path=name, url=url, bytes=len(data),
                            git_blob_sha1=row['sha'], sha256=sha(data)))
    manifest = dict(status='PINNED_AUTHOR_SOURCE_ACQUIRED_NOT_YET_MATCHED_TO_USER_ROM',
                    listing='https://www.smbarena.com/hack?id=2279',
                    author='jroweboy', repository='https://github.com/jroweboy/smb1base',
                    branch='neckyboi', commit=COMMIT,
                    tree=dict(path=str(OUT / 'tree.json'), sha256=TREE_SHA256),
                    files=records, total_bytes=sum(row['bytes'] for row in records),
                    scope='Selected source and CHR leaves only; no ROM download, full clone, or source execution.')
    target = OUT / 'acquisition.json'
    encoded = (json.dumps(manifest, indent=2) + '\n').encode()
    if target.exists():
        assert target.read_bytes() == encoded
    else:
        target.write_bytes(encoded)
    print(json.dumps(dict(manifest=str(target), sha256=sha(encoded),
                          files=len(records), bytes=manifest['total_bytes'])))


if __name__ == '__main__':
    main()
