"""Freeze source-derived pickup pixels for the hardware OAM regression.

Run explicitly when the pinned 2.02 input changes. The emulator test never
reads generated metasprites/CHR to decide what the icons should look like.
"""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/reference'))
from build_special_art import extract
from prepare_crossover import frames


def main():
    items = list(ET.parse(ROOT/'reference/crossover2/main.xml').getroot().iter('item'))
    symbols = {}
    for tag in items:
        if tag.get('type') in ('SymbolClassTag', 'ExportAssetsTag') and tag.find('tags') is not None:
            symbols.update({name.text: ident.text for ident, name in zip(tag.find('tags'), tag.find('names'))})
    sprite = next(i for i in items if i.get('spriteId') == symbols['MegaManPickup'])
    sheet = Image.open(ROOT/'reference/crossover2/images/412_com.smbc.graphics.skins.BmdInfo_Bass000.png').convert('RGBA')
    images = extract(frames(sprite), 24, sheet)
    # Fixed world palettes: red/white/orange; black/skin/brown. These are
    # the NES adaptation's six available stable colors, independent of suit.
    colors = {0x16:(216,40,0), 0x30:(252,252,252), 0x27:(252,152,56),
              0x0f:(0,0,0), 0x37:(252,216,168), 0x17:(164,80,0)}
    lines = ['-- Pinned 2.02 source pixels, quantized to stable NES world palettes.', 'return {']
    for number in (3,4,5,6,7,8,13,1,2,14,15,16,17):
        pic = images[number-1].crop((40,32,56,48))
        pixels = [255 if p[3]<128 else min(colors, key=lambda c:sum((p[k]-colors[c][k])**2 for k in range(3)))
                  for p in pic.get_flattened_data()]
        lines.append(f' [{number}]={{'+','.join(str(p) for p in pixels)+'},')
    lines.append(' hud={')
    hudcolors={1:(252,252,252),2:(60,188,252),3:(0,0,0)}
    for item,number in enumerate((3,4,5,6,7,8,13),1):
        pic=images[number-1].crop((40,32,56,48))
        pixels=[0 if p[3]<128 else min(hudcolors,key=lambda c:sum((p[k]-hudcolors[c][k])**2 for k in range(3)))
                for p in pic.get_flattened_data()]
        lines.append(f' [{item}]={{'+','.join(str(p) for p in pixels)+'},')
    lines.extend([' },','}'])
    (ROOT/'tests/fixtures/bass-pickup-pixels.lua').write_text('\n'.join(lines)+'\n')


if __name__ == '__main__':
    main()
