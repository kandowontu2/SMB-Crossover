"""Inspect actual menu OAM and silhouettes for all Select identities, without Mesen."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

from PIL import Image, ImageDraw

import check_prince_brick_support_1111 as Host
import check_hogan_current_bounded_v1 as M
import assess_dkjr_menu_current_1103_v11 as UI
from inventory_playable_menu_1101_v3 import menu_name
from check_tmnt_render_oa import address, location


R = Path(__file__).resolve().parents[2]
NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
CHR = 16 + 0x100000


def seed(bundle):
    model = M.fresh(bundle)
    M.put(model, CrossoverMenuState=1, Mirror_PPUMASK=0, DisableScreenFlag=1,
          SavedJoypad1Bits=0, SavedJoypad2Bits=0)
    M.invoke(model, 'CrossoverMenuInput')
    M.consume(model)
    assert M.get(model, 'CrossoverMenuState') == 2
    assert any(model.vram[0x2000:0x23c0])
    return model


def palette():
    raw = (R/'tools/Windows/NEXXT 3.0/defaults/nes.pal').read_bytes()
    return [tuple(raw[i:i+3]) for i in range(0, 192, 3)]


def pixel(raw, page, offset, x, y):
    start = CHR + page*1024 + offset + (y//8)*16 + y % 8
    return ((raw[start] >> (7-x)) & 1) | (((raw[start+8] >> (7-x)) & 1) << 1)


def sprite_image(model, raw, colors):
    result = Image.new('RGBA', (256, 256))
    cells = []
    for start in reversed(range(0, 256, 4)):
        y, tile, attr, x = model[0x200+start:0x204+start]
        if y >= 240:
            continue
        cells.append((y, tile, attr, x))
        pattern = (tile & 1)*4096 + (tile & 254)*16
        page = model.chr_latches[pattern//1024]
        for dy in range(16):
            py = 15-dy if attr & 128 else dy
            for dx in range(8):
                px = 7-dx if attr & 64 else dx
                value = pixel(raw, page, pattern % 1024, px, py)
                if value and x+dx < 256 and y+dy+1 < 256:
                    color = model.vram[0x3f10+4*(attr & 3)+value] & 63
                    result.putpixel((x+dx, y+dy+1), (*colors[color], 255))
    box = result.getbbox()
    return result.crop(box) if box else Image.new('RGBA', (1, 1)), cells


def silhouette(model, raw, slot, colors):
    top, left = 4+(slot//8)*4, 4+(slot % 8)*3
    result = Image.new('RGBA', (16, 24))
    for y in range(24):
        for x in range(16):
            tile = model.vram[0x2000+(top+y//8)*32+left+x//8]
            page = model.chr_latches[8+(tile//64)]
            value = pixel(raw, page, (tile % 64)*16, x % 8, y % 8)
            if value:
                result.putpixel((x, y), (*((72, 72, 72), (160, 160, 160),
                                          (248, 248, 248))[value-1], 255))
    return result


def audit(raw, *, sheet=None, force_facing=None, include_images=False):
    bundle = Host.C.Start.W.bundle(raw)
    origin = seed(bundle)
    colors = palette()
    rows, images = [], []
    for slot in range(32):
        model = M.fork(origin)
        M.put(model, CrossoverMenuIndex=slot, CmActive=0, VRAM_Buffer1_Offset=0,
              NmiDisable=255, FamilyMainCommit=1)
        model[0x5ffe] = 0
        M.invoke(model, 'MenuResolveCharacter')
        M.invoke(model, 'QueueSelection')
        seen = set()
        for cycle in range(32):
            name, tiles = menu_name(model)
            if not name and cycle:
                break  # A non-alternate slot emits no new name after Select.
            identity = name, tuple(tiles), M.get(model, 'SelectedCharacter')
            if identity in seen:
                break
            assert name, (slot, cycle)
            seen.add(identity)
            before = M.get(model, 'PlayerFacingDir')
            if force_facing is not None:
                M.put(model, PlayerFacingDir=force_facing)
                M.invoke(model, 'DrawSelectionPreview')
            M.consume(model)
            portrait, cells = sprite_image(model, raw, colors)
            thumb = silhouette(model, raw, slot, colors)
            rows.append(dict(slot=slot, cycle=cycle, name=name,
                             owner=M.get(model, 'SelectedCharacter'),
                             facing_before=before, facing_after=M.get(model, 'PlayerFacingDir'),
                             sprite_count=len(cells),
                             portrait_SHA256=sha256(portrait.tobytes()).hexdigest(),
                             portrait_size=list(portrait.size),
                             silhouette_SHA256=sha256(thumb.tobytes()).hexdigest()))
            images.append((thumb, portrait))
            # Match the ordinary GameLoop guard before its next native input
            # call; consume() deliberately releases the preceding NMI guard.
            M.put(model, NmiDisable=255, FamilyMainCommit=1)
            UI.key(model, 32)
        else:
            raise AssertionError(('Select cycle did not wrap', slot))
    assert len(rows) == 101, len(rows)
    if sheet:
        sheet = Path(sheet)
        assert sheet.parent.resolve().is_relative_to((R/'build').resolve())
        assert not sheet.exists()
        sheet.parent.mkdir(parents=True, exist_ok=True)
        canvas = Image.new('RGB', (1600, 104*((len(rows)+9)//10)), (30, 32, 38))
        draw = ImageDraw.Draw(canvas)
        for index, (row, (thumb, portrait)) in enumerate(zip(rows, images, strict=True)):
            x, y = (index % 10)*160, (index//10)*104
            draw.text((x+3, y+2), f"{index+1:03} {row['name']}", fill='white')
            draw.text((x+3, y+15), f"{row['slot']}:{row['cycle']} face {row['facing_after']}",
                      fill=(175, 180, 190))
            canvas.paste(thumb.resize((32, 48), Image.Resampling.NEAREST), (x+4, y+38),
                         thumb.resize((32, 48), Image.Resampling.NEAREST))
            scale = min(2, 105/max(1, portrait.width), 67/max(1, portrait.height))
            sized = portrait.resize((max(1, round(portrait.width*scale)),
                                     max(1, round(portrait.height*scale))), Image.Resampling.NEAREST)
            canvas.paste(sized, (x+43+(110-sized.width)//2, y+30+67-sized.height), sized)
        canvas.save(sheet)
    return (rows, images) if include_images else rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, default=NIGHTLY)
    parser.add_argument('--sheet', type=Path)
    parser.add_argument('--force-facing', type=int, choices=(1, 2))
    args = parser.parse_args()
    raw = args.rom.read_bytes()
    rows = audit(raw, sheet=args.sheet, force_facing=args.force_facing)
    print(json.dumps(dict(passed=True, ROM_SHA256=sha256(raw).hexdigest(),
                          identities=len(rows), rows=rows, output_files=int(bool(args.sheet)),
                          scope='Actual menu input/native renderer/NMI in CPU peripheral model; '
                                'pixel inspection still required to classify inherent art orientation.')),
          flush=True)


if __name__ == '__main__':
    main()
