"""Correct the independent native barrel palette; retain the V2 preview negative."""
import hashlib
import json
import re
from PIL import Image, ImageDraw
from prepare_original_dk_assets_v1 import ROOT, ROM, bound, decode

OUT = ROOT/'build/dk-playable-assets-v3'


def main():
    assert not (OUT/'handoff.json').exists()
    parent = ROOT/'build/dk-playable-assets-v2/handoff.json'
    assert bound(parent)['sha256'] == 'fb4f4f927f2b0152199ff615e76ff87782e3f0a99920067a8e7bb4787c819127'
    p = json.loads(parent.read_text())
    for row in p['outputs']:
        assert bound(row['path'])['sha256'] == row['sha256']
    original = ROM.read_bytes()
    assert hashlib.sha256(original).hexdigest() == p['original']['sha256']
    # 25M's literal3F00/20 palette packet: sprite palette3 follows BG16B
    # and three preceding sprite palettes. It differs from BG2/main DK.
    at = 16+0xf55b-0xc000
    palette = list(original[at+3+28:at+3+32])
    assert palette == [0x0f,0x06,0x27,0x02]
    art = (parent.parent/'dk-art.inc').read_text()
    for i, row in enumerate(p['barrel_frames']):
        before = row['record'][:]
        after = before[:]
        for k in range(2,len(after),4):
            after[k] = 1  # Source palette3 remapped to native guest weapon1.
        needle = 'DkBarrel'+str(i)+': .byte '+','.join(map(str,before))
        assert art.count(needle) == 1
        art = art.replace(needle,'DkBarrel'+str(i)+': .byte '+','.join(map(str,after)))
        row['record'] = after
    art = art.replace('DkArtEnd:', 'DkBarrelPalette: .byte $0f,$06,$27,$02\nDkArtEnd:')
    OUT.mkdir(exist_ok=True)
    (OUT/'dk.chr').write_bytes((parent.parent/'dk.chr').read_bytes())
    (OUT/'dk-art.inc').write_text(art)
    sheet = Image.open(parent.parent/'barrels-and-menu.png').convert('RGB')
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0,20,479,103),fill='#18242c')
    colors = ['#18242c','#6c0600','#fc9838','#0000bc']
    for i,row in enumerate(p['barrel_frames']):
        first=row['source_first_tile']
        for col in range(2):
            for half in range(2):
                tile=first+col*2+half
                values=decode(original[16400+tile*16:16400+(tile+1)*16])
                for y in range(8):
                    for x in range(8):
                        value=values[y*8+x]
                        if value:
                            xx=i*80+(col*8+x)*3+4;yy=(half*8+y)*3+24
                            draw.rectangle((xx,yy,xx+2,yy+2),fill=colors[value])
    sheet.save(OUT/'barrels-and-menu.png')
    p.update(status='Native barrel palette corrected; source pixel/compact portrait component only, no host/native admission',
        parent=bound(parent), tool=bound(__file__), body_palette=p.pop('palette'),
        barrel_palette=palette, source_barrel_palette=3, native_barrel_palette=1,
        palette_correction='V2 incorrectly previewed barrels with the DK body palette. Source25M sprite3 is0F/06/27/02; no source color quantization. Original falling DK uses its separate explicit3F1D/3 palette packet.',
        outputs=[bound(OUT/n) for n in ['dk.chr','dk-art.inc','barrels-and-menu.png']])
    (OUT/'handoff.json').write_text(json.dumps(p,indent=2)+'\n')
    print(json.dumps(dict(handoff=bound(OUT/'handoff.json'),barrel_palette=palette)))


if __name__ == '__main__':
    main()
