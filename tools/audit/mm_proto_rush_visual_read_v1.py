"""Read-only Rush animation/CHR/icon classification from the completed Mega unit."""
from pathlib import Path
import argparse
import ast
import collections
import csv
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
SRC = D / 'root-current-roster-composition-v1/source'
N = D / 'mm-proto-weapon-boundary-v1/native-ready-v3/native'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def original_functions():
    ns = {'Image': Image, 'json': json}
    for name, file in [('extract', 'build_special_art.py'), ('frames', 'prepare_crossover.py')]:
        path = SRC / 'tools/reference' / file
        node = next(n for n in ast.parse(path.read_text()).body
                    if isinstance(n, ast.FunctionDef) and n.name == name)
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), ns)
    return ns


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    a = parser.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(R)
    out.mkdir(parents=True, exist_ok=False)
    ns = original_functions()
    xml = R / 'reference/crossover2/main.xml'
    bitmap = R / 'reference/crossover2/images/412_com.smbc.graphics.skins.BmdInfo_Bass000.png'
    items = list(ET.parse(xml).getroot().iter('item'))
    symbols = {}
    for tag in items:
        if tag.get('type') in ('SymbolClassTag', 'ExportAssetsTag'):
            ids, names = tag.find('tags'), tag.find('names')
            if ids is not None and names is not None:
                symbols.update({n.text: i.text for i, n in zip(ids, names)})
    sprites = {q.get('spriteId'): q for q in items if q.get('type') == 'DefineSpriteTag'}
    image = Image.open(bitmap).convert('RGBA')
    rush_timeline = ns['frames'](sprites[symbols['Rush']])
    pickup_timeline = ns['frames'](sprites[symbols['MegaManPickup']])
    assert pickup_timeline[9]['labels'] == ['rushCoil']
    original = ns['extract'](rush_timeline, 24, image)
    pickup = ns['extract'](pickup_timeline, 24, image)[9].crop((40, 32, 56, 48))
    ref_sheet = Image.new('RGB', (4 * 288, 4 * 316), '#8f8bff')
    draw = ImageDraw.Draw(ref_sheet)
    for i, pic in enumerate(original):
        x, y = i % 4 * 288, i // 4 * 316
        scaled = pic.resize((288, 288), Image.Resampling.NEAREST)
        ref_sheet.paste(scaled, (x, y + 28), scaled)
        draw.text((x + 8, y + 8), 'Rush ' + str(i + 1) + ' ' + '/'.join(rush_timeline[i]['labels']), fill='black')
    ref_sheet.save(out / 'original-rush-reference-PRIVATE.png')
    pickup.resize((256, 256), Image.Resampling.NEAREST).save(out / 'original-rush-icon-PRIVATE.png')
    # Prove exact generator quantization for the icon and actual dumped HUD bank.
    colors = [(252, 252, 252), (60, 188, 252), (0, 0, 0)]
    pixels = [[0 if pickup.getpixel((x, y))[3] < 128 else min(range(1, 4), key=lambda c:
               sum((pickup.getpixel((x, y))[k] - colors[c - 1][k]) ** 2 for k in range(3)))
               for x in range(16)] for y in range(16)]
    hud = (SRC / 'chr/characters/inventory-hud.chr').read_bytes()[7 * 2048:7 * 2048 + 1024]
    dumped = (N / 'diagnostic-CHR-0243.bin').read_bytes()
    assert hud == dumped
    for tile, dx, dy in [(0x2a, 0, 0), (0x2b, 8, 0), (0x2c, 0, 8), (0x2d, 8, 8)]:
        expected = bytes(sum(((pixels[y + dy][x + dx] >> plane) & 1) << (7 - x)
                             for x in range(8)) for plane in range(2) for y in range(8))
        assert hud[tile * 16:(tile + 1) * 16] == expected
    families = [int(x) for x in re.search(r'SsArtFamilies:\s*\.byte ([0-9,]+)',
                 (SRC / 'src/special_art.inc').read_text()).group(1).split(',')]
    physical = [int(x) for x in re.search(r'SsPhysicalBanks:\s*\.byte ([0-9,]+)',
                 (SRC / 'src/chr_map_mmc5.inc').read_text()).group(1).split(',')]
    config = json.loads((N / 'config.json').read_text())
    epochs = [json.loads(line) for line in (N / 'ability-dma-epochs.jsonl').read_text().splitlines()]
    hardware = {q['stamp']['frame']: q for q in epochs if q['kind'] == 'startFrame-hardware'}
    diagnostic = [json.loads(line) for line in (N / 'bass-diagnostic.jsonl').read_text().splitlines()]
    visible = {q['stamp']['frame']: q for q in diagnostic if q['kind'] == 'actual-visible-startFrame-font-hardware'}
    packed = (SRC / 'chr/characters/special-weapons-mmc5.chr').read_bytes()
    raw = (N / 'actual-ppu.argb').read_bytes()
    frames = list(csv.DictReader((N / 'actual-ppu-index.csv').open(newline='')))
    indices = {int(q['ppu_frame']): i for i, q in enumerate(frames)}
    sheet = Image.new('RGB', (4 * 512, 9 * 508), '#151923')
    draw = ImageDraw.Draw(sheet)
    rows = []
    for i, frame in enumerate(range(850, 886)):
        q, state = hardware[frame], visible[frame]
        assert state['stamp']['observed_ctrl'] & 0x20, 'Actual captured sprites are 16 high'
        oam = [q['hardware'][j:j + 4] for j in range(0, 256, 4)]
        remaining = collections.Counter(tuple(p) for p in oam)
        candidates = []
        for art in range(43, 56):
            record = config['effect_records'][art][0]['bytes']
            parts = [record[j:j + 4] for j in range(1, 1 + record[0], 4)]
            tile, attr, dy, dx = parts[0]
            dx = dx - 256 if dx >= 128 else dx
            dy = dy - 256 if dy >= 128 else dy
            for first in oam:
                if first[1:3] != [tile, attr]:
                    continue
                origin = (first[3] - dx, first[0] - dy)
                expected = []
                for tile, attr, py, px in parts:
                    px = px - 256 if px >= 128 else px
                    py = py - 256 if py >= 128 else py
                    expected.append((origin[1] + py, tile, attr, origin[0] + px))
                wanted = collections.Counter(expected)
                bank = physical[families[art]] | 1
                if wanted <= remaining and origin[0] == 140 and bank == state['state']['actualChr'][4]:
                    candidate = dict(art=art, original_frame=art - 42, origin=list(origin), family=families[art],
                                     physical_CHR=bank, parts=expected)
                    if candidate not in candidates:
                        candidates.append(candidate)
        assert candidates, frame
        bank = candidates[0]['physical_CHR']
        assert all(c['physical_CHR'] == bank for c in candidates)
        actual_chr = (N / ('diagnostic-CHR-%04d.bin' % bank)).read_bytes()
        family = candidates[0]['family']
        assert actual_chr == packed[family * 2048 + 1024:(family + 1) * 2048]
        part_indices = [next(j for j, p in enumerate(oam) if tuple(p) == tuple(part))
                        for part in candidates[0]['parts']]
        selected = {y: [j for j, p in enumerate(oam) if p[0] < 239 and p[0] + 1 <= y < p[0] + 17][:8]
                    for y in range(240)}
        rejected_rows = {str(j): [y for y in range(max(0, oam[j][0] + 1), min(240, oam[j][0] + 17))
                                 if j not in selected[y]] for j in part_indices}
        rejected_rows = {j: ys for j, ys in rejected_rows.items() if ys}
        index = indices[frame]
        data = raw[index * 245760:(index + 1) * 245760]
        image = Image.frombytes('RGBA', (256, 240), data, 'raw', 'BGRA').convert('RGB')
        x, y = i % 4 * 512, i // 4 * 508
        sheet.paste(image.resize((512, 480), Image.Resampling.NEAREST), (x, y + 28))
        draw.text((x + 8, y + 5), 'PPU %d | original Rush %s | CHR%d' %
                  (frame, '/'.join(str(c['original_frame']) for c in candidates), bank), fill='white')
        rows.append(dict(PPU_frame=frame, actual_pixel_sha256=hashlib.sha256(data).hexdigest(),
                         hardware_stamp=q['stamp'], source_update_at_visible=state['stamp']['updates'],
                         captured_PPUCTRL=state['stamp']['observed_ctrl'], native_palette=state['state']['palette'],
                         native_SsChrPhysical=state['state']['SsChrPhysical'], pose_candidates=candidates,
                         Rush_physical_indices=part_indices, hardware_first8_rejected_rows=rejected_rows))
    sheet.save(out / 'rush-850-885-actual-whole-images.png', optimize=True)
    (out / 'actual-rows.json').write_text(json.dumps(rows, indent=2) + '\n')
    bound = [xml, bitmap, SRC / 'tools/reference/build_special_art.py', SRC / 'tools/reference/prepare_crossover.py',
             SRC / 'src/special_art.inc', SRC / 'src/chr_map_mmc5.inc', SRC / 'src/special_weapons.s',
             SRC / 'src/inventory.s', SRC / 'chr/characters/inventory-hud.chr',
             SRC / 'chr/characters/special-weapons-mmc5.chr', N / 'config.json', N / 'ability-dma-epochs.jsonl',
             N / 'bass-diagnostic.jsonl', N / 'actual-ppu.argb', N / 'actual-ppu-index.csv']
    proof = dict(passed=True, read_only=True, native_launches=0,
                 exact_ROM='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287',
                 original_timeline=[dict(frame=q['frame'], labels=q['labels']) for q in rush_timeline],
                 original_Rush_symbol=symbols['Rush'], original_bitmap=24,
                 Rush_HUD_pickup_frame=10, Rush_HUD_pickup_label=pickup_timeline[9]['labels'],
                 native_HUD_physical_bank=243, native_four_icon_tiles=[42, 43, 44, 45],
                 icon_exact_original_generator_and_dump=True, frames_read=36,
                 actual_rows_sha256=sha(out / 'actual-rows.json'),
                 actual_sheet_sha256=sha(out / 'rush-850-885-actual-whole-images.png'),
                 source_and_raw_bindings={str(p): sha(p) for p in bound}, tool_sha256=sha(__file__),
                 limits='Existing native observations only. Actual Rush SsMode/SsArt arrays were not serialized per frame; pose candidates are reconstructed from complete captured hardware OAM geometry, actual CHR banks/dumps and linked records, with ambiguity retained. First-eight rejection uses actual 16-high PPUCTRL and transparent sprite halves consume slots; this does not prove per-pixel color output or every omitted opaque pixel. Original SWF skin pixels are before GraphicsManager runtime recoloring; native palette quantization is an adaptation, not proof of exact Flash final colors. No gameplay, matched performance, new native or graphics-fix claim.')
    (out / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps({k: v for k, v in proof.items() if k != 'source_and_raw_bindings'}, indent=2))


if __name__ == '__main__':
    main()
