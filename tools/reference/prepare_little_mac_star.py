"""Repack the complete original Punch-Out HUD star into Mac's pickup page.

Only the two star tile pairs and their record coordinates change. Body art,
palette indices, pickup bounds and the two-sprite budget are preserved.
"""
from pathlib import Path
import argparse
import hashlib
import json

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE_SHA256 = '0c9aeb8fea387765c67877114c4969b6a91c17b707fbe6ba4e13526dfdfbdcbf'
ROWS = (
    '.....#.....', '....###....', '....###....', '...#####...',
    '###########', '###########', '.#########.', '..#######..',
    '..#######..', '..###.###..', '.###...###.', '.##.....##.',
)
OLD_RECORD = '''LmStar:
 .byte 8
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_4}, 2, -16, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_4}, 2, 0, 0
'''
NEW_RECORD = '''LmStar:
 .byte 8
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_4}, 2, -6, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_4}, 2, -6, 8
'''


def sha(data):
    return hashlib.sha256(data).hexdigest()


def prepare(root=ROOT):
    source = root / 'reference/little-mac-star/source-40.png'
    assert sha(source.read_bytes()) == SOURCE_SHA256, 'Pinned original screenshot'
    image = Image.open(source).convert('RGB')
    rows = tuple(''.join('#' if image.getpixel((x, y)) == (255, 254, 255)
                         else '.' for x in range(16, 27)) for y in range(22, 34))
    assert rows == ROWS and sum(row.count('#') for row in rows) == 73
    encoded = bytearray()
    for bx in (0, 8):
        # An 8x16 hardware cell begins at the first opaque row, rather than
        # splitting the 12-row glyph across a 16-pixel-aligned grid.
        for half in (0, 8):
            for plane in (0, 1):
                for y in range(half, half + 8):
                    bits = sum(1 << (7-x) for x in range(8)
                               if plane == 1 and y < 12 and bx+x < 11
                               and rows[y][bx+x] == '#')
                    encoded.append(bits)
    assert len(encoded) == 64
    asset = root / 'chr/characters/little-mac.chr'
    before = asset.read_bytes()
    assert len(before) == 40960
    at = (704 - 668) * 1024
    assert not any(before[at+64:at+1024]), 'Star owns its otherwise empty page'
    after = before[:at] + encoded + before[at+64:]
    assert before[:at] == after[:at] and before[at+64:] == after[at+64:]
    record_path = root / 'src/little_mac_art.inc'
    text = record_path.read_text()
    assert text.count(OLD_RECORD) + text.count(NEW_RECORD) == 1
    record_path.write_text(text.replace(OLD_RECORD, NEW_RECORD))
    asset.write_bytes(after)
    return dict(source_screenshot_sha256=SOURCE_SHA256,
                original_rom_sha256='11b01730bc88173fd20a54bf327ff3a9db9a29e7a53c638359bbb30aac16a929',
                source='Original controller fight HUD, frame40; foreground RGB255,254,255',
                source_bounds=[16, 22, 27, 34], source_rows=rows,
                source_origin=[16, 28], opaque_pixels=73,
                source_nes_color=48, palette=2, palette_pixel=2,
                physical_chr_page=704, chr_byte_range=[at, at+64],
                chr_sha256=sha(after), source_tile_bytes_sha256=sha(bytes(encoded)),
                records=[[0, 2, -6, 0], [2, 2, -6, 8]], hardware_sprites=2,
                unchanged='All body/portrait CHR, all other CHR pages, source palette indices and pickup/collision code')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--workspace', type=Path, default=ROOT)
    args = p.parse_args()
    result = prepare(args.workspace.resolve())
    (args.workspace / 'reference/little-mac-star/manifest.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
