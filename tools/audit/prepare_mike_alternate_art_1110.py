"""Inspect original Jay/Steve donor CHR without copying source ROMs."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from PIL import Image, ImageDraw

R = Path(__file__).resolve().parents[2]
OUT = R / 'build/mike-alternate-prototypes-1110'
DONORS = {
    'jay': (Path('C:/NES/Journey to Silius (USA).nes'),
            '12f5c5e413a2aa5bff75b5077e4477497d7e49aa432560c2e8c3fd3cc71910cc'),
    'steve': (Path('C:/NES/Shatterhand (USA).nes'),
              'fbdfaab40aedda270d7473be37566b59e68811d932740c105d84fa6b1a7f19e1'),
}


def decode(tile):
    return [[((tile[y] >> (7-x)) & 1) | (((tile[y+8] >> (7-x)) & 1) << 1)
             for x in range(8)] for y in range(8)]


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', required=True, type=Path)
    cli.add_argument('--extract', action='store_true')
    args = cli.parse_args()
    assert args.output.resolve() == OUT.resolve()
    if args.extract:
        extract()
        return
    assert not OUT.exists()
    OUT.mkdir()
    rows = {}
    for name, (path, pin) in DONORS.items():
        raw = path.read_bytes()
        assert sha256(raw).hexdigest() == pin and raw[:4] == b'NES\x1a'
        first = 16 + raw[4]*16384
        chr_data = raw[first:]
        assert len(chr_data) == 131072
        atlas = Image.new('RGB', (16*68, 8*80), (38, 42, 48))
        draw = ImageDraw.Draw(atlas)
        colors = [(0, 0, 0), (90, 90, 90), (175, 175, 175), (255, 255, 255)]
        for page in range(128):
            x0, y0 = (page%16)*68, (page//16)*80
            draw.text((x0, y0), f'{page:02X}', fill=(230, 160, 80))
            for tile in range(64):
                pixels = decode(chr_data[page*1024+tile*16:page*1024+(tile+1)*16])
                for y in range(8):
                    for x in range(8):
                        atlas.putpixel((x0+(tile%8)*8+x, y0+14+(tile//8)*8+y), colors[pixels[y][x]])
        atlas.save(OUT / f'{name}-original-chr.png')
        rows[name] = dict(path=str(path), SHA256=pin, CHR_start=first, CHR_bytes=len(chr_data))
    (OUT / 'art-inspection.json').write_text(json.dumps(dict(donors=rows,
        scope='Original donor CHR inspection only; actor/OAM/palette provenance and host extraction pending.'), indent=2)+'\n')


def extract():
    roots = {
        'jay': R/'build/mike-donor-openings-v2-1110/jay/capture',
        'steve': R/'build/mike-donor-steve-v3-1110/steve/capture',
    }
    tiles = {
        'jay': {'idle': (8, 24, 10, 26), 'walk': (68, 84, 70, 86), 'jump': (40, 56, 42, 58)},
        'steve': {'idle': (1, 3, 7, 9), 'walk': (1, 3, 13, 15), 'jump': (1, 3, 7, 9)},
    }
    target = {'idle': ((0,2,4,6),(16,18,20,22),(32,34,36,38)),
              'walk': ((8,10,12,14),), 'jump': ((24,26,28,30),)}
    rgb = {7:(160,80,20),15:(0,0,0),32:(255,255,255),33:(100,176,255),
           41:(76,218,72),54:(248,184,248)}
    preview = Image.new('RGB',(3*80,2*150),(35,39,46))
    draw = ImageDraw.Draw(preview)
    receipts = {}
    for row, (hero, root) in enumerate(roots.items()):
        report = json.loads((root/'result.json').read_bytes())
        assert report['passed'] and report['controller_only'] and not report['script_RAM_writes']
        assert report['ROM_sha256'] == DONORS[hero][1]
        art = bytearray(1024)
        used = {}
        palettes = []
        for col, record in enumerate(report['records']):
            pose = record['pose']
            oam = [tuple(bytes.fromhex(record['oam'])[at:at+4]) for at in range(0,256,4)]
            core = []
            wanted = tiles[hero][pose]
            for y, tile, attr, x in oam:
                if y >= 240 or tile != wanted[0] or attr != 0:
                    continue
                expected = [(y,wanted[0],0,x),(y,wanted[1],0,x+8),
                            (y+16,wanted[2],0 if hero=='jay' else 1,x),
                            (y+16,wanted[3],0 if hero=='jay' else 1,x+8)]
                if all(part in oam for part in expected):
                    core = expected
                    break
            assert len(core) == 4, (hero,pose)
            source = (root/f'{pose}.chr').read_bytes()
            assert len(source) == 8192 and record['control'] & 32
            palette = bytes.fromhex(record['palette'])
            palettes.append(palette[17:20])
            pairs = [source[0x1000*(tile&1)+16*(tile&254):0x1000*(tile&1)+16*(tile&254)+32]
                     for tile in wanted]
            for destination in target[pose]:
                for tile, pair in zip(destination,pairs,strict=True):
                    at = tile*16
                    assert not any(art[at:at+32])
                    art[at:at+32] = pair
            pixels = [[0]*16 for _ in range(32)]
            for part, pair in enumerate(pairs):
                for half in range(2):
                    block = decode(pair[half*16:half*16+16])
                    for y in range(8):
                        for x in range(8):
                            pixels[(part//2)*16+half*8+y][(part%2)*8+x] = block[y][x]
            draw.text((col*80+4,row*150+4),f'{hero} {pose}',fill=(240,240,240))
            for y in range(32):
                for x in range(16):
                    value = pixels[y][x]
                    color = rgb.get(palette[16+value],(180,180,180)) if value else (35,39,46)
                    draw.rectangle((col*80+8+x*3,row*150+28+y*3,col*80+10+x*3,row*150+30+y*3),fill=color)
            used[pose] = dict(frame=record['frame'], source_OAM=core,
                             source_CHR_SHA256=sha256(source).hexdigest(),
                             pair_SHA256=[sha256(pair).hexdigest() for pair in pairs],
                             target_groups=target[pose], original_palette=palette.hex())
        assert palettes[0] == palettes[1] == palettes[2]
        (OUT/f'{hero}-native.chr').write_bytes(art)
        receipts[hero] = dict(art_SHA256=sha256(art).hexdigest(), player_palette=list(palettes[0]),
                             poses=used, original_capture_SHA256=sha256((root/'result.json').read_bytes()).hexdigest(),
                             limitation='Original16x32core only; Steve wider arm and extra jump part omitted. '
                                        'Steve lower palette21/30 is rendered as29/36 in this prototype.' if hero=='steve' else
                                        'Original16x32body only; original weapon arm and donor abilities pending.')
    preview.save(OUT/'native-core-poses.png')
    (OUT/'native-art.json').write_text(json.dumps(dict(passed=True, original_pixels=True,
        images=receipts, source_SHA256=sha256(Path(__file__).read_bytes()).hexdigest(),
        scope='Exact actual original hardware OAM core, CHRpairbytes and source palettes; '
              'prototype native body uses Mike geometry/animation and temporary Steve palette reduction.'),indent=2)+'\n')


if __name__ == '__main__':
    main()
