"""Freeze uncompressed 2.02 Sophia cannon pixels independently of NES packing."""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET
from PIL import Image
from build_remaining_art import extract
from prepare_crossover import frames

ROOT = Path(__file__).resolve().parents[2]
items = list(ET.parse(ROOT / 'reference/crossover2/main.xml').getroot().iter('item'))
symbols = {}
for t in items:
    if t.get('type') in ('SymbolClassTag', 'ExportAssetsTag'):
        ids, names = t.find('tags'), t.find('names')
        if ids is not None and names is not None:
            symbols.update({n.text: i.text for i, n in zip(ids, names)})
sprite = next(i for i in items if i.get('type') == 'DefineSpriteTag' and i.get('spriteId') == symbols['SophiaBullet'])
path = next((ROOT / 'reference/crossover2/images').glob('*_Sophia000.png'))
pictures = extract(frames(sprite), 44, Image.open(path).convert('RGBA'))
lines = ['-- Frozen source SWF matrix pixels; no NES CHR or metasprite tables are read.', 'return {']
indices = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
for index in indices:
    pic = pictures[index - 1]
    pic = pic.crop(pic.getbbox())
    pal, colors = 0, [(228, 0, 88), (255, 255, 255), (0, 0, 0)]
    pixels = []
    for rgba in pic.getdata():
        if rgba[3] < 128:
            pixels.append(255)
        else:
            color = min(range(3), key=lambda c: sum((rgba[k] - colors[c][k]) ** 2 for k in range(3))) + 1
            pixels.append(16 + pal * 4 + color)
    lines.append(f' [{index}]={{width={pic.width},height={pic.height},pixels={{{",".join(map(str,pixels))}}}}},')
lines.append('}')
target = ROOT / 'tests/fixtures/sophia-cannon-pixels.lua'
target.write_text('\n'.join(lines) + '\n')
target.with_suffix('.json').write_text(json.dumps({'source_sheet_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'source_swf_sha256': hashlib.sha256((ROOT / 'reference/crossover2/source.swf').read_bytes()).hexdigest(), 'frames': list(indices), 'oracle_sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'comparison': 'Cropped source shape and NES palette indices, before CHR packing'}, indent=2) + '\n')

explosion = next(i for i in items if i.get('type') == 'DefineSpriteTag' and i.get('spriteId') == symbols['SophiaExplosion'])
pictures = extract(frames(explosion), 44, Image.open(path).convert('RGBA'))
lines = ['-- Independent uncompressed source impact pixels; blank frame2 is intentional.', 'return {']
for index in range(1, 6):
    pic = pictures[index - 1]
    bbox = pic.getbbox()
    if not bbox:
        lines.append(f' [{index}]={{width=0,height=0,pixels={{}}}},')
        continue
    pic = pic.crop(bbox)
    colors = [(228, 0, 88), (255, 255, 255), (0, 0, 0)]
    pixels = [255 if rgba[3] < 128 else 17 + min(range(3), key=lambda c: sum((rgba[k] - colors[c][k]) ** 2 for k in range(3))) for rgba in pic.getdata()]
    lines.append(f' [{index}]={{width={pic.width},height={pic.height},pixels={{{",".join(map(str,pixels))}}}}},')
lines.append('}')
target = ROOT / 'tests/fixtures/sophia-impact-pixels.lua'
target.write_text('\n'.join(lines) + '\n')
target.with_suffix('.json').write_text(json.dumps({'source_sheet_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'source_swf_sha256': hashlib.sha256((ROOT / 'reference/crossover2/source.swf').read_bytes()).hexdigest(), 'frames': list(range(1,6)), 'oracle_sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'comparison': 'Source SWF masks and matrices before NES packing'}, indent=2) + '\n')
