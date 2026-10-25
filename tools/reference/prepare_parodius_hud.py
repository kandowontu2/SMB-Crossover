"""Repack all three original seven-cell Parodius bars into private HUD fonts."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path('C:/NES/Parodius Da! (Japan).nes')
SOURCE_SHA = 'ef1dd05ad5b6095d1d8e9a9f81fcb549b5cf0248779d4e76eb7bd9b139de4c9a'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-captures', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    out = args.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    original = SOURCE.read_bytes()
    assert sha(original) == SOURCE_SHA
    capture = json.loads((args.source_captures / 'capture.json').read_text())
    assert capture['source_ROM_sha256'] == SOURCE_SHA
    source_chr = original[16 + 131072:]
    reference_font = (ROOT / 'chr/mmc5/bg_ground.chr').read_bytes()[:1024]
    # These fonts exist only while a Parodius alternate owns the stage HUD.
    # Keep every digit and every glyph used by all three names and fixed HUD
    # labels, plus native blank/dash/multiply/coin. Other profiles use their
    # own original font. A full alphabet would exhaust the64-tile window.
    letters = set('OCTOPUSTWINBEEPENTAROUWORLDTIMESCOREHP')
    keep = set(range(10)) | {ord(c)-ord('A')+10 for c in letters} | {0x24, 0x28, 0x29, 0x2e}
    pages, tables, rows = [], [], []
    for variant in [1, 2, 3]:
        folder = args.source_captures / str(variant)
        # The original mapper changes its font just for the HUD scanlines;
        # the mapped CHR at endFrame is not the font that drew this bar.
        native_ppu = (folder / 'hud-ppu.bin').read_bytes()
        source_pixels = np.frombuffer((folder / 'screen.argb').read_bytes(), dtype='<u4').reshape(240, 256)
        state = dict(line.split('=', 1) for line in (folder / 'source-state.txt').read_text().splitlines())
        assert int(state['variant_008f']) == variant and int(state['skin_0087']) == variant
        assert len(native_ppu) == 16384
        actual_mask = source_pixels[216:224, 8:232] != source_pixels[216, 0]
        matches = []
        for pattern_base in [0, 0x1000]:
            patterns, cells, decoded, provenance = [], [], [], []
            for column in range(1, 29):
                # Original raster split displays second nametable row2 at
                # screenY216; the ordinary first nametable row27 is blank.
                tile = native_ppu[0x2440 + column]
                attribute = native_ppu[0x27c0 + column//4]
                palette = (attribute >> (4 + 2*((column % 4)//2))) & 3
                raw = native_ppu[pattern_base + tile*16:pattern_base + tile*16 + 16]
                source_offsets = [n for n in range(0, len(source_chr), 16) if source_chr[n:n+16] == raw]
                if not source_offsets:
                    break
                mask = []
                for y in range(8):
                    line = []
                    for x in range(8):
                        value = ((raw[y] >> (7-x)) & 1) | (((raw[y+8] >> (7-x)) & 1) << 1)
                        color = native_ppu[0x3f00 + (palette*4+value if value else 0)] & 0x3f
                        line.append((color & 15) not in [13, 14, 15])
                    mask.append(line)
                decoded.append(np.array(mask, dtype=bool))
                patterns.append(bytes(sum(int(v) << (7-x) for x, v in enumerate(line)) for line in mask) + bytes(8))
                cells.append(tile)
                provenance.append(dict(tile=tile, palette=palette, original_CHR_offsets=source_offsets))
            if len(decoded) == 28 and np.array_equal(np.concatenate(decoded, axis=1), actual_mask):
                matches.append((pattern_base, patterns, cells, provenance))
        assert len(matches) == 1, (variant, 'Original bar mask must match every actual PPU pixel', len(matches))
        base, patterns, cells, provenance = matches[0]
        font = bytearray(reference_font)
        free = sorted(set(range(64)) - keep)
        pool = {bytes(font[t*16:t*16+16]): t for t in keep}
        mapped = []
        for pattern in patterns:
            if pattern not in pool:
                assert free, (variant, 'Private HUD glyph capacity exceeded')
                tile = free.pop(0)
                pool[pattern] = tile
                font[tile*16:tile*16+16] = pattern
            mapped.append(pool[pattern])
        assert all(font[t*16:t*16+16] == reference_font[t*16:t*16+16] for t in keep)
        pages.append(bytes(font)); tables.extend(mapped)
        preview = np.concatenate([np.array([[(font[t*16+y] >> (7-x)) & 1 for x in range(8)] for y in range(8)]) for t in mapped], axis=1)
        Image.fromarray(np.repeat((preview*255).astype(np.uint8)[:, :, None], 3, axis=2)).resize((896, 32), Image.Resampling.NEAREST).save(out / f'bar-{variant}.png')
        rows.append(dict(variant=variant, intended_physical_page=395+variant,
                         actual_native_pixels_verified=224*8, pattern_base=base,
                         native_cells=cells, mapped_cells=mapped, tile_provenance=provenance,
                         remaining_private_tiles=len(free), kept_HUD_tiles=sorted(keep)))
    (out / 'parodius-hud.chr').write_bytes(b''.join(pages))
    lines = ['; Exact original Parodius seven-cell frame/label pixel masks.', 'PnHudCells:']
    lines += [' .byte ' + ','.join(f'${v:02x}' for v in tables[i:i+28]) for i in range(0, len(tables), 28)]
    (out / 'parodius_hud.inc').write_text('\n'.join(lines) + '\n')
    report = dict(prepared=True, integrated=False, source_ROM_sha256=SOURCE_SHA,
                  source_capture_sha256=sha((args.source_captures / 'capture.json').read_bytes()),
                  chr_sha256=sha(b''.join(pages)), chr_bytes=len(b''.join(pages)), rows=rows,
                  adaptation='Original rendered frame/letter masks retained exactly; nonblack source colors use the HUD foreground. Private per-ship fonts retain all glyphs used by current Parodius stage names/status, not the unused full alphabet. No global palette or game-source changes. Publication/cursor/exit behavior still needs native integration checks.')
    (out / 'manifest.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(dict(prepared=True, integrated=False, rows=[{k:v for k,v in row.items() if k not in ['tile_provenance','native_cells','mapped_cells','kept_HUD_tiles']} for row in rows])), flush=True)


if __name__ == '__main__':
    main()
