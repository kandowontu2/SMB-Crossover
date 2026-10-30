"""Fit the user-corrected Kamikaze V1 CHR to the native Mario tile layout."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[1]
O = R / 'build/kamikaze-v1-skin-art-1030-v1'
SOURCE = Path('C:/NES/the stash/Kamikaze_V1_SMB1_Hack.nes')
BASE = Path('C:/NES/Super Mario Bros. (World).nes')
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def flip(data, horizontal, vertical):
    result = []
    for plane in [0, 8]:
        rows = data[plane:plane + 8]
        for value in rows[::-1] if vertical else rows:
            result.append(int(f'{value:08b}'[::-1], 2) if horizontal else value)
    return bytes(result)


def main():
    assert not O.exists()
    O.mkdir()
    raw, base = SOURCE.read_bytes(), BASE.read_bytes()
    assert sha(SOURCE) == '7085f9fbfda4bee8da1c451f14e3880453466eefdf6d9579f91e5a3b8d27a877'
    assert sha(BASE) == '0b3d9e1f01ed1668205bab34d6c82b0e281456e137352e4f36a9b2cfa3b66dea'
    assert raw[4:7] == bytes([2, 1, 1])
    source_chr, base_chr = raw[32784:40976], base[32784:40976]
    native = R / 'chr/mmc5/sprites_mario.chr'
    data = bytearray(native.read_bytes())
    assert len(data) == 4096
    records, ambiguities = [], []
    for page in range(4):
        for local in range(60):
            at = (page * 64 + local) * 16
            pattern = bytes(data[at:at + 16])
            matches = []
            for tile in range(256):
                for horizontal, vertical in [(False, False), (True, False), (False, True), (True, True)]:
                    if flip(base_chr[tile * 16:tile * 16 + 16], horizontal, vertical) == pattern:
                        replacement = flip(source_chr[tile * 16:tile * 16 + 16], horizontal, vertical)
                        matches.append((tile, horizontal, vertical, replacement))
            assert matches, ('No original Mario source tile', page, local)
            if len({v[3] for v in matches}) != 1:
                ambiguities.append(dict(page=page, tile=local,
                                        candidates=[[t, h, v, hashlib.sha256(p).hexdigest()]
                                                    for t, h, v, p in matches]))
                continue
            tile, horizontal, vertical, replacement = matches[0]
            data[at:at + 16] = replacement
            records.append(dict(page=page, tile=local, source_tile=tile,
                                H=horizontal, V=vertical))
    result = dict(passed=not ambiguities, source_ROM=sha(SOURCE), source=str(SOURCE),
                  source_header=list(raw[:16]), matched_tiles=len(records), ambiguities=ambiguities,
                  pixel_index_remap=False, host_code_or_palette_change=False,
                  records=records, bindings={str(p): sha(p) for p in [SOURCE, BASE, native, Path(__file__)]})
    if not ambiguities:
        (O / 'kamikaze-mario-v1.chr').write_bytes(data)
        result['art_sha256'] = sha(O / 'kamikaze-mario-v1.chr')
    (O / 'art.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ['records', 'bindings', 'ambiguities']}, indent=2))
    assert not ambiguities, ('Ambiguous source pixels require a real pose mapping', len(ambiguities))


if __name__ == '__main__':
    main()
