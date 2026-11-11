"""Pack Sonic Vol.2 1.7 standing poses into the native MMC5 body cells."""

import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path

from PIL import Image


SHEET = Path('C:/Users/kando/Downloads/504880.png')
SHEET_SHA = 'ad0b0c40441f647f2b8305545e1c0200947c8295339a611c88668df00e95e33c'
SOURCE_URL = 'https://www.spriters-resource.com/nes/sonicthehedgehogimprovement/asset/504880/'
NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
NORMAL_CHR, SUPER_CHR = 224, 226
CHR_START = 1048592
COOKIE_AT = 1034472
COOKIE_PREFIX = bytes.fromhex('a72b01')
COOKIE_PAGES = (*range(321, 328), 330, 328, 333, 334, NORMAL_CHR)
BODY_TILES = (0x00, 0x02, 0x20, 0x22)
BACKGROUND = {(0, 128, 128), (0, 98, 98)}
NORMAL_COLORS = {(216, 40, 0): 1, (0, 0, 168): 2, (0, 112, 236): 2, (252, 188, 176): 3}
SUPER_COLORS = {(200, 76, 12): 1, (252, 152, 56): 2, (252, 216, 168): 3}


def decode_sheet(data):
    assert sha256(data).hexdigest() == SHEET_SHA
    source = Image.open(BytesIO(data)).convert('RGB')
    assert source.size == (800, 512)
    return source


def pose(source, bounds, palette):
    cell = source.crop(bounds)
    pixels = [cell.getpixel((x, y)) for y in range(cell.height) for x in range(cell.width)]
    assert set(pixels) <= BACKGROUND | palette.keys(), (bounds, set(pixels)-BACKGROUND-palette.keys())
    indexed = Image.frombytes('L', cell.size, bytes(palette.get(pixel, 0) for pixel in pixels))
    tight = indexed.getbbox()
    assert tight is not None
    indexed = indexed.crop(tight)
    assert 16 <= indexed.width <= 30 and 24 <= indexed.height <= 36
    indexed = indexed.resize((16, min(indexed.height, 32)), Image.Resampling.NEAREST)
    native = Image.new('L', (16, 32))
    native.paste(indexed, (0, 32-indexed.height))
    assert set(native.tobytes()) == {0, 1, 2, 3}
    return native


def tile_pair(image, x, y):
    data = bytearray()
    for top in (0, 8):
        for plane in (0, 1):
            for row in range(8):
                pixels = (image.getpixel((x+col, y+top+row)) for col in range(8))
                data.append(sum(((pixel >> plane) & 1) << (7-col)
                                for col, pixel in enumerate(pixels)))
    return bytes(data)


def body_cells(source):
    normal = pose(source, (0, 0, 32, 48), NORMAL_COLORS)
    super_sonic = pose(source, (396, 0, 428, 48), SUPER_COLORS)
    return tuple(tuple(tile_pair(image, x, y) for y in (0, 16) for x in (0, 8))
                 for image in (normal, super_sonic))


def pages(normal_stock, sheet_data):
    """Retain the normal ring, HUD and effect cells on both form pages."""
    assert len(normal_stock) == 1024
    result = []
    for cells in body_cells(decode_sheet(sheet_data)):
        page = bytearray(normal_stock)
        for tile, data in zip(BODY_TILES, cells, strict=True):
            start = tile * 16
            page[start:start+32] = data
        result.append(bytes(page))
    return tuple(result)


def chr_page(rom, page):
    start = CHR_START + 1024*page
    return bytes(rom[start:start+1024])


def transport_cookie(rom, *, super_sonic=False):
    pages = COOKIE_PAGES + ((SUPER_CHR,) if super_sonic else ())
    digest = sha256(b''.join(chr_page(rom, page) for page in pages)).digest()
    return COOKIE_PREFIX + digest[:13]


def apply_art(stock, sheet, *, candidate=None, super_sonic=False):
    """Apply body art after any roster and resident-code edits in memory."""
    old_cookie = transport_cookie(stock)
    assert stock[COOKIE_AT:COOKIE_AT+16] == old_cookie and stock[:CHR_START].count(old_cookie) == 1
    current = bytearray(stock if candidate is None else candidate)
    assert len(current) == len(stock) and current[COOKIE_AT:COOKIE_AT+16] == old_cookie
    for page in (NORMAL_CHR, SUPER_CHR):
        assert chr_page(current, page) == chr_page(stock, page)
    art = pages(chr_page(stock, NORMAL_CHR), sheet)
    targets = (NORMAL_CHR, SUPER_CHR) if super_sonic else (NORMAL_CHR,)
    for page, data in zip(targets, art[:len(targets)], strict=True):
        start = CHR_START + 1024*page
        current[start:start+1024] = data
    current[COOKIE_AT:COOKIE_AT+16] = transport_cookie(current, super_sonic=super_sonic)
    return bytes(current)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sheet', type=Path, default=SHEET)
    parser.add_argument('--native-output', type=Path)
    args = parser.parse_args()
    art = args.sheet.read_bytes()
    source = decode_sheet(art)
    normal, super_sonic = body_cells(source)
    assert all(any(cell) for cell in (*normal, *super_sonic)) and normal != super_sonic
    stock = NIGHTLY.read_bytes()
    body = {index for tile in BODY_TILES for index in range(tile*16, tile*16+32)}
    revised = apply_art(stock, art)
    dual = apply_art(stock, art, super_sonic=True)
    original = chr_page(stock, NORMAL_CHR)
    for page in (NORMAL_CHR, SUPER_CHR):
        updated = chr_page(dual, page)
        assert all(updated[i] == original[i] for i in range(1024) if i not in body)
    assert chr_page(revised, NORMAL_CHR) == chr_page(dual, NORMAL_CHR)
    assert chr_page(revised, SUPER_CHR) == chr_page(stock, SUPER_CHR)
    assert revised[COOKIE_AT:COOKIE_AT+16] != dual[COOKIE_AT:COOKIE_AT+16]
    result = dict(passed=True, sheet_SHA256=SHEET_SHA, tile_pairs=BODY_TILES,
                  normal_SHA256=sha256(b''.join(normal)).hexdigest(),
                  super_SHA256=sha256(b''.join(super_sonic)).hexdigest(),
                  art_only_normal_SHA256=sha256(revised).hexdigest(),
                  art_only_dual_SHA256=sha256(dual).hexdigest(), output_files=0)
    if args.native_output:
        from check_sonic_ring_physical_1110 import RING
        from run_stdout_mesen_1110 import R, run

        output = args.native_output.resolve()
        assert output == R / 'build/sonic-vol2-normal-native-1111'
        output.mkdir(exist_ok=True)
        rom = output / 'candidate.nes'
        rom.write_bytes(revised)
        receipt = run(RING, rom, output / 'capture', result['art_only_normal_SHA256'], 180,
                      extra_env={'SMB_STDOUT_IMAGES': '0',
                                 'SMB_SONIC_COOKIE': transport_cookie(revised).hex()})
        assert receipt['passed'], receipt['receipt']
        result.update(native_receipt_SHA256=receipt['receipt_SHA256'], output_files=1)
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
