"""Add original barrel frames and a disclosed compact menu portrait to DK's packed art."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw
from prepare_original_dk_assets_v1 import ROOT, ROM, bound, decode

OUT = ROOT/'build/dk-playable-assets-v2'


def encode(values):
    raw = bytearray(32)
    for y in range(16):
        for x in range(8):
            v = values[y*8+x]
            at = (y//8)*16+y%8
            raw[at] |= (v & 1) << (7-x)
            raw[at+8] |= (v >> 1) << (7-x)
    return bytes(raw)


def main():
    assert not (OUT/'handoff.json').exists(), 'Frozen assets require a successor'
    parent = ROOT/'build/dk-source-assets-v1/handoff.json'
    assert bound(parent)['sha256'] == '98735ef49db1a04275796265c78abd79db1d0dae750c9306ec2f3f1bb922a39b'
    manifest = json.loads(parent.read_text())
    for p in manifest['outputs']:
        assert bound(p['path'])['sha256'] == p['sha256']
    raw = ROM.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == manifest['original']['sha256']
    original_chr = raw[16400:]
    pixels = bytearray((parent.parent/'dk.chr').read_bytes())
    counts = manifest['pattern_pairs_per_page']
    page = [bytes(pixels[3072+i*32:3072+(i+1)*32]) for i in range(counts[3])]
    entries = []
    images = []
    for first in [0x80, 0x84, 0x88, 0x8c, 0x90, 0x94]:
        records, raster = [], bytearray(256)
        for col in range(2):
            pair = original_chr[(first+col*2)*16:(first+col*2+2)*16]
            if pair not in page:
                page.append(pair)
            index = page.index(pair)
            records += [index*2, 0, 255, col*8]
            for half in range(2):
                values = decode(pair[half*16:half*16+16])
                for y in range(8):
                    start = (half*8+y)*16+col*8
                    raster[start:start+8] = values[y*8:y*8+8]
        entries.append(dict(source_first_tile=first, record=[len(records)]+records,
                            source_pixel_sha256=hashlib.sha256(raster).hexdigest()))
        images.append((16, 16, raster))
    # The menu has a 32-pixel cell. Keep the complete 48x32 original body,
    # sampled at half size, rather than hiding half of it behind a neighbor.
    idle = manifest['frames'][3]
    full = bytearray(48*32)
    for col in range(6):
        for row in range(4):
            tile = idle['tiles'][col*4+row]
            values = decode(original_chr[4096+tile*16:4096+(tile+1)*16])
            for y in range(8):
                start = (row*8+y)*48+col*8
                full[start:start+8] = values[y*8:y*8+8]
    small = bytes(full[(y*2)*48+x*2] for y in range(16) for x in range(24))
    portrait = []
    for col in range(3):
        pair = encode(bytes(small[y*24+col*8+x] for y in range(16) for x in range(8)))
        if pair not in page:
            page.append(pair)
        portrait += [page.index(pair)*2, 0, 15, col*8-4]
    assert len(page) <= 32, len(page)
    pixels[3072:] = b''.join(page).ljust(1024, b'\0')
    # No authenticated original body pair changes, including the existing
    # first twelve pairs in the fourth page.
    old = (parent.parent/'dk.chr').read_bytes()
    assert pixels[:3072+counts[3]*32] == old[:3072+counts[3]*32]
    for row, (_, _, expected) in zip(entries, images):
        got = bytearray(256)
        rec = row['record']
        for at in range(1, len(rec), 4):
            tile, attr, dy, dx = rec[at:at+4]
            assert attr == 0 and dy == 255
            for half in range(2):
                values = decode(pixels[3072+tile*16+half*16:3072+tile*16+(half+1)*16])
                for y in range(8):
                    start = (half*8+y)*16+dx
                    got[start:start+8] = values[y*8:y*8+8]
        assert got == expected
    OUT.mkdir(exist_ok=True)
    (OUT/'dk.chr').write_bytes(pixels)
    art = (parent.parent/'dk-art.inc').read_text().replace('DkArtEnd:', '')
    art += '\nDkBarrelLo: .byte '+','.join('<DkBarrel'+str(i) for i in range(6))+'\n'
    art += 'DkBarrelHi: .byte '+','.join('>DkBarrel'+str(i) for i in range(6))+'\n'
    for i, row in enumerate(entries):
        art += 'DkBarrel'+str(i)+': .byte '+','.join(map(str, row['record']))+'\n'
    art += 'DkMenuRecord: .byte '+','.join(map(str, [len(portrait)]+portrait))+'\nDkArtEnd:\n'
    (OUT/'dk-art.inc').write_text(art)
    sheet = Image.new('RGB', (7*80, 104), '#18242c')
    draw = ImageDraw.Draw(sheet)
    colors = ['#18242c', '#fcfcfc', '#f8a4c0', '#6c0600']
    for i, (w, h, raster) in enumerate(images+[(24,16,small)]):
        draw.text((i*80+2,2), hex(entries[i]['source_first_tile']) if i<6 else 'menu', fill='white')
        for y in range(h):
            for x in range(w):
                value = raster[y*w+x]
                if value:
                    draw.rectangle((i*80+x*3+4,y*3+24,i*80+x*3+6,y*3+26), fill=colors[value])
    sheet.save(OUT/'barrels-and-menu.png')
    result = dict(status='Authentic original DK body/barrel pixels plus disclosed half-size menu adaptation; no host/native admission',
        parent=bound(parent), original=manifest['original'], tool=bound(__file__),
        body_frames=9, barrel_frames=entries, barrel_pixel_exact=True,
        portrait=dict(source_pose='original idle C657', source_size=[48,32], size=[24,16],
            adaptation='Nearest-neighbor half-size sample, complete silhouette, source palette retained'),
        palette=manifest['original_palette'], CHR_pages=[820,823], pairs_per_page=counts[:3]+[len(page)],
        original_body_patterns_unchanged=True, native_run=False,
        outputs=[bound(OUT/n) for n in ['dk.chr','dk-art.inc','barrels-and-menu.png']])
    (OUT/'handoff.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(handoff=bound(OUT/'handoff.json'), pairs=result['pairs_per_page'])))


if __name__ == '__main__':
    main()
