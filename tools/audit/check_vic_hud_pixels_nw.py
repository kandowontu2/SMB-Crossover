"""Compare actual native power-bar pixels with their committed font/nametable."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expect-clean', action='store_true')
    args = parser.parse_args(); folder = args.run
    raw = (folder / 'hud-expected-masks.bin').read_bytes()
    rows = list(csv.DictReader((folder / 'hud-mask-index.csv').open(newline='')))
    compared = []; bad = []
    for row in rows:
        # As with the existing DMA audit, a snapshot at endFrame belongs to
        # the next completed screenshot. Use one fixed alignment for every
        # frame, including both level entrances and all cursor/VRAM changes.
        frame = int(row['frame']) + 1; image = folder / 'frames' / f'{frame:06d}.png'
        if not image.exists(): continue
        at, size = int(row['offset']), int(row['bytes'])
        assert size == 192 and len(raw[at:at + size]) == size
        expected = [bool(value & (128 >> bit)) for value in raw[at:at + size] for bit in range(8)]
        with Image.open(image) as source:
            rgb = source.convert('RGB'); background = rgb.getpixel((0, 8))
            crop = rgb.crop((32, 8, 224, 16))
            pixels = getattr(crop, 'get_flattened_data', crop.getdata)()
            actual = [pixel != background for pixel in pixels]
        different = sum(a != b for a, b in zip(expected, actual))
        item = dict(frame=frame, different_pixels=different)
        compared.append(item)
        if different: bad.append(item)
    publication = list(csv.DictReader((folder / 'hud-publication.csv').open(newline='')))
    counts = {}
    invalid_publications = []; late_fonts = []
    for row in publication:
        if row['active'] == '1' and row['gameplay'] == '1':
            key = row['physical']; counts[key] = counts.get(key, 0) + 1
            if key not in ('0', '394'): invalid_publications.append(row)
            if key == '394' and 'scanline' in row and 8 <= int(row['scanline']) < 241: late_fonts.append(row)
    report = dict(passed=bool(compared) and not bad and not invalid_publications and not late_fonts,
                  native_frames_compared=len(compared),
                  pixels_compared=len(compared) * 1536, mismatched_frames=len(bad),
                  mismatched_pixels=sum(item['different_pixels'] for item in bad), mismatches=bad,
                  native_background_publications=counts,
                  invalid_background_publications=len(invalid_publications), late_HUD_font_publications=len(late_fonts),
                  expected_font_mask_sha256=hashlib.sha256(raw).hexdigest(),
                  endFrame_snapshot_to_completed_screenshot_offset=1,
                  scope='Actual native screenshots: x32..223/y8..15 opaque mask versus physical CHR394 and the live PPU nametable. Palette hue/layout and other HUD regions are separate.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'mismatches'}))
    if args.expect_clean: assert report['passed'], 'Retained native HUD pixels must equal the committed font masks'


if __name__ == '__main__':
    main()
