"""Pack a four-by-seven NES menu without repacking ordinary mapper assets.

The existing native portrait thumbnails are decoded from the previous menu;
new portraits come from authenticated source renderers. Only explicitly ready
slots receive art or navigation. The full-size colored preview stays native.
"""
from pathlib import Path
import hashlib, json, re, sys
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import prepare_ice_climbers_assets_v1 as ice


def digest(data):
    return hashlib.sha256(data).hexdigest()


def tile_pixel(data, tile, x, y):
    at = tile * 16 + y
    return ((data[at] >> (7-x)) & 1) | (((data[at+8] >> (7-x)) & 1) << 1)


def encode(values):
    return bytes(sum(((values[y][x] >> plane) & 1) << (7-x) for x in range(8))
                 for plane in range(2) for y in range(8))


def position(slot):
    assert 0 <= slot < 28
    return 4 + (slot // 7) * 4, 3 + (slot % 7) * 4


def navigation(slots):
    rows = {r: [s for s in slots if s//7 == r] for r in range(4)}
    live = [r for r in rows if rows[r]]
    result = {}
    for s in slots:
        row = rows[s//7]
        i = row.index(s)
        result[s] = dict(left=row[(i-1) % len(row)], right=row[(i+1) % len(row)])
        for name, delta in [('up', -1), ('down', 1)]:
            target = live[(live.index(s//7) + delta) % len(live)]
            result[s][name] = min(rows[target], key=lambda v: (abs(v%7-s%7), v))
    seen = {slots[0]}
    while True:
        more = seen | {v for s in seen for v in result[s].values()}
        if more == seen:
            break
        seen = more
    assert seen == set(slots), 'Every playable profile must be reachable'
    return result


def main():
    old_nt = (ROOT/'chr/raw/x5-character-select.bin').read_bytes()
    packed = (ROOT/'chr/characters/packed-mmc5-expanded.chr').read_bytes()
    # The checked-in standalone prepack can predate an expanded-only art
    # patch. Decode the actual cartridge pages, rather than regenerating it.
    old_chr = packed[4*1024:8*1024]
    assert len(old_chr) == 4096 and len(old_nt) == 1024
    text = (ROOT/'src/chr_map_mmc5.inc').read_text().split('ChrPhysicalMap:', 1)[1].split('.popseg', 1)[0]
    mapping = [int(v) for line in text.splitlines() if '.byte' in line for v in line.split('.byte')[1].split(',')]
    assert [i for i, v in enumerate(mapping) if 4 <= v <= 7] == list(range(60, 64))
    portraits = {}
    for slot in range(19):
        row, col = (slot//6, 2+(slot%6)*5) if slot < 12 else (2, 2+(slot-12)*4)
        top = 4 + row*5
        pic = Image.new('RGBA', (24, 32))
        for y in range(32):
            for x in range(24):
                t = old_nt[(top+y//8)*32+col+x//8]
                color = tile_pixel(old_chr, t, x%8, y%8)
                if color:
                    v = (0, 72, 160, 248)[color]
                    pic.putpixel((x, y), (v, v, v, 255))
        assert pic.getbbox(), slot
        portraits[slot] = pic
    native, _, _ = ice.render(ice.original(), 0, 0, 1)
    minx, miny = min(x for x, y in native), min(y for x, y in native)
    pic = Image.new('RGBA', (max(x for x,y in native)-minx+1, max(y for x,y in native)-miny+1))
    for (x, y), color in native.items():
        pic.putpixel((x-minx, y-miny), [(0,0,0,0), (248,248,248,255), (40,96,192,255), (248,176,104,255)][color])
    portraits[19] = pic
    # Alex/Ryan remain absent until the corrected native colors and the full
    # actor movement/collision bridge have passed their integration checks.
    slots = sorted(portraits)
    nav = navigation(slots)
    nt = bytearray([0x24]*960 + [0]*64)
    def put(row, col, value):
        for i, c in enumerate(value):
            nt[row*32+col+i] = 0x24 if c == ' ' else ord(c)-55
    put(1, 8, 'CHOOSE YOUR HERO')
    put(27, 5, 'A OR START PLAY  B BACK')
    put(28, 10, 'D PAD CHOOSE')
    for col in range(2, 30):
        nt[3*32+col] = 0xfc
    for row in range(19, 25):
        nt[row*32+12:row*32+20] = bytes([0xfe])*8
    # Palette1 white UI, palette2 gold UI, palette3 blue preview card.
    nt[960:968] = bytes([0xa5])*8
    nt[960+6*8:960+7*8] = bytes([0x55])*8
    nt[960+7*8:] = bytes([0x55])*8
    for ar in (4, 5):
        for ac in (3, 4):
            nt[960+ar*8+ac] = 0xf0 if ar == 4 else 0xff
    chr_data = bytearray(old_chr)
    chr_data[64*16:252*16] = bytes((252-64)*16)
    pool = {bytes(16): 0x24}
    next_tile = 64
    for s, original in portraits.items():
        picture = original.crop(original.getbbox())
        scale = min(1, 16/picture.width, 24/picture.height)
        if scale < 1:
            picture = picture.resize((max(1, round(picture.width*scale)), max(1, round(picture.height*scale))), Image.Resampling.NEAREST)
        canvas = Image.new('RGBA', (16, 24))
        canvas.alpha_composite(picture, ((16-picture.width)//2, 24-picture.height))
        top, col = position(s)
        for ty in range(3):
            for tx in range(2):
                values = []
                for y in range(8):
                    line = []
                    for x in range(8):
                        r, g, b, a = canvas.getpixel((tx*8+x, ty*8+y))
                        light = .299*r+.587*g+.114*b
                        line.append(0 if a < 128 else 1 if light < 95 else 2 if light < 200 else 3)
                    values.append(line)
                data = encode(values)
                if data not in pool:
                    assert next_tile < 252
                    pool[data] = next_tile
                    next_tile += 1
                t = pool[data]
                nt[(top+ty)*32+col+tx] = t
                chr_data[t*16:(t+1)*16] = data
    chr_data[252*16:253*16] = encode([[1 if y == 3 else 0 for x in range(8)] for y in range(8)])
    chr_data[253*16:254*16] = encode([[3 if 1 <= x <= 5 and abs(y-3) <= 5-x else 0 for x in range(8)] for y in range(8)])
    chr_data[254*16:255*16] = encode([[1]*8 for _ in range(8)])
    characters = [0,1,2,3,4,5,6,7,12,9,10,11,13,14,15,16,17,18,19,20]
    lines = ['; Staged expansion: absent profiles have no portrait or navigation.']
    for direction in ('left', 'right', 'up', 'down'):
        lines += ['X5Menu'+direction.title()+':', ' .byte '+','.join(str(nav[s][direction]) if s in nav else '0' for s in range(28))]
    for name, values in [
        ('Characters', characters+[0]*(28-len(characters))),
        ('Present', [int(s in nav) for s in range(28)]),
        ('CursorLo', [((position(s)[0]+1)*32+position(s)[1]-1) & 255 for s in range(28)]),
        ('CursorHi', [32+((position(s)[0]+1)*32+position(s)[1]-1)//256 for s in range(28)])]:
        lines += ['X5Menu'+name+':', ' .byte '+','.join(map(str, values))]
    (ROOT/'src/roster_expansion_menu.inc').write_text('\n'.join(lines)+'\n')
    (ROOT/'chr/characters/roster-expansion-menu.chr').write_bytes(chr_data)
    (ROOT/'chr/raw/roster-expansion-menu.bin').write_bytes(nt)
    changed = bytearray(packed)
    changed[4096:8192] = chr_data
    assert changed[:4096] == packed[:4096] and changed[8192:] == packed[8192:]
    (ROOT/'chr/characters/packed-mmc5-roster-expanded.chr').write_bytes(changed)
    palette = [(0,0,0), (72,72,72), (160,160,160), (248,248,248)]
    ui = [(0,0,0), (248,248,248), (248,248,248), (248,248,248)]
    gold = [(0,0,0), (248,184,0), (248,184,0), (248,184,0)]
    blue = [(0,0,0), (60,124,248), (0,88,248), (60,124,248)]
    page = Image.new('RGB', (256,240))
    for y in range(240):
        for x in range(256):
            t = nt[y//8*32+x//8]
            attr = nt[960+(y//32)*8+x//32]
            shift = ((y//16)%2)*4+((x//16)%2)*2
            colors = [palette, ui, gold, blue][(attr >> shift) & 3]
            page.putpixel((x,y), colors[tile_pixel(chr_data,t,x%8,y%8)])
    page.resize((768,720), Image.Resampling.NEAREST).save(ROOT/'chr/characters/roster-expansion-menu-review.png')
    report = dict(playable_slots=slots, absent_slots=[s for s in range(28) if s not in nav], navigation=nav,
        portrait_tiles=next_tile-64, thumbnail_size=[16,24], original_packed_sha256=digest(packed),
        expanded_packed_sha256=digest(changed), only_physical_pages_changed=[4,5,6,7],
        ordinary_assets_untouched=True, scope='Private integration menu, not a full-level qualification or release.')
    (ROOT/'build/roster-expansion-menu.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['playable_slots','portrait_tiles','expanded_packed_sha256']}))


if __name__ == '__main__':
    main()
