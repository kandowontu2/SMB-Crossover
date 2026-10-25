"""Pack original NES Meta Knight OAM/CHR beside Kirby, without redrawing pixels.

Original boss sprite window1 is physical page $A4, beginning at tile $80.
Keep its body and sword palette identities instead of painting both blue.
"""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path("C:/NES/Kirby's Adventure (USA) (Rev 1).nes")
OUT = ROOT/'reference/meta-knight'


def main():
    original = SOURCE.read_bytes()
    assert hashlib.sha256(original).hexdigest() == 'a7a742f5288cd4ab220f530ee7c8d0e3714b8bf107e89c9bf03039217fec5829'
    prg, chr_data = original[16:524304], original[524304:]
    read = lambda address: prg[0x31*8192+(address&8191)]
    word = lambda address: read(address)+256*read(address+1)
    sign = lambda value: value if value < 128 else value-256
    path = ROOT/'chr/characters/kirby.chr'
    kirby = path.read_bytes()[:16384]
    assert hashlib.sha256(kirby).hexdigest() == '94936eb3b3a3bd090da9fba0770cc0d1013e798625b2560cb2b9c1edfe1879e6'
    # Meta Knight never owns Kirby's copy shots or dropped-copy star. Only
    # the three health glyphs at the original indices11..13 are resident.
    # Reuse the other slots for his native sword frames without growing CHR.
    common = [None]*11 + [kirby[i*32:i*32+32] for i in range(11,14)]
    fixed = kirby[1024:2048]
    buckets, frames = [], []
    # Include complete spin and upper-slash sequences, through native pose59.
    # The old66-frame cut stopped midway through the eight-frame spin.
    for pose in range(0x5a):
        pointer = word(0x8000+pose*2)
        count = read(pointer)
        assert 0 < count < 12
        parts, required, sword_pixels = [], [], set()
        for part in range(count):
            x, y, tile, attr = [read(pointer+1+part*4+k) for k in range(4)]
            assert not tile&1 and tile>=128
            page = 0xa4
            at = page*1024+((tile&254)-128)*16
            pixels = chr_data[at:at+32]
            assert len(pixels) == 32
            palette = attr&3
            assert palette in (1,3)
            if palette==1:
                # Keep the native sword's three distinct shades using SMB's
                # stable weapon palette: white30, gold27, edge16. Its source
                # shades are30/37/17; this declared world-palette adaptation
                # avoids recoloring native enemies and pickups.
                converted=bytearray(32)
                for yy in range(16):
                    offset=yy//8*16+yy%8
                    for xx in range(8):
                        q=(pixels[offset]>>(7-xx)&1)|((pixels[offset+8]>>(7-xx)&1)<<1)
                        v=(0,2,3,1)[q]
                        converted[offset]|=(v&1)<<(7-xx)
                        converted[offset+8]|=(v>>1)<<(7-xx)
                        if q:
                            dx=7-xx if attr&64 else xx
                            dy=15-yy if attr&128 else yy
                            sword_pixels.add((sign(x)+8+dx,sign(y)+25+dy))
                pixels=bytes(converted)
            if pixels not in required:
                required.append(pixels)
            parts.append((sign(x)+8, sign(y)+25, pixels, (attr&0xc0)|(2 if palette==1 else 0)))
        choices = [(sum(tile in bank for tile in required), i)
                   for i, bank in enumerate(buckets)
                   if len(set(t for t in bank+required if t is not None)) <= 32]
        if choices:
            bank_index = max(choices)[1]
        else:
            bank_index = len(buckets)
            buckets.append(common.copy())
        bank = buckets[bank_index]
        for pixels in required:
            if pixels not in bank:
                if None in bank:bank[bank.index(None)]=pixels
                else:bank.append(pixels)
        assert len(bank)<=32
        bounds = ([min(x for x,y in sword_pixels), min(y for x,y in sword_pixels),
                   max(x for x,y in sword_pixels)-min(x for x,y in sword_pixels)+1,
                   max(y for x,y in sword_pixels)-min(y for x,y in sword_pixels)+1]
                  if sword_pixels else [0,0,0,0])
        frames.append(dict(pose=pose, pointer=pointer, physical_chr=356+2*bank_index,
                           parts=[dict(dx=x, dy=y, tile=bank.index(pixels)*2, attr=attr)
                                  for x,y,pixels,attr in reversed(parts)], sword_bounds=bounds))
    packed = b''.join(b''.join(t or bytes(32) for t in bank).ljust(1024,b'\0')+fixed for bank in buckets)
    assert len(kirby)+len(packed) <= 24576, 'Stay within the actual24KiB linked Kirby reservation'
    path.write_bytes((kirby+packed).ljust(24576,b'\0'))
    lines = ['; Generated from original Kirby Adventure Meta Knight OAM/CHR.',
             '.pushseg', '.segment "KIRBY_GFX"']
    for field, value in [('Chr', lambda f: str(f['physical_chr']&255)),
                         ('Lo', lambda f: '<MkPose'+format(f['pose'],'02x')),
                         ('Hi', lambda f: '>MkPose'+format(f['pose'],'02x'))]:
        lines.append('MkBody'+field+':')
        for i in range(0,len(frames),12):
            lines.append(' .byte '+','.join(value(f) for f in frames[i:i+12]))
    for frame in frames:
        lines += ['MkPose'+format(frame['pose'],'02x')+':', ' .byte '+str(len(frame['parts'])*4)]
        lines += [' .byte '+','.join(str(p[key]&255) for key in ('tile','attr','dy','dx'))
                  for p in frame['parts']]
    for index,field in enumerate(('Left','Top','Width','Height')):
        lines.append('MkSword'+field+':')
        for i in range(0,len(frames),12):
            lines.append(' .byte '+','.join(str(f['sword_bounds'][index]&255) for f in frames[i:i+12]))
    # Native bank2B attack poses/durations. The boss's post-attack AI waits
    # are shortened to8 updates for player control; active sequences retain
    # their source timing. Spin/plunge duration is bounded by player landing.
    actions=[
        [(8,4),(0x18,8),(0x1a,1),(0x1c,1),(0x1e,1),(0x20,1),(0x22,2),(0x24,1),(0x26,3),(0x28,4),(0x2a,4),(8,8)],
        ([(0x18,1),(0x1a,1),(0x1c,1),(0x20,1),(0x22,1),(0x26,2),(0x22,1),(0x20,1),(0x1c,1),(0x1a,1)]*3)+[(0x26,15),(8,8)],
        [(0x2c,8),(0x2e,2),(0x30,48),(8,8)],
        [(p,1) for _ in range(4) for p in range(0x3e,0x46)],
        [(0x3c,64)],
        [(0x0e,4),(0x0c,2),(0x0a,4),(0x0c,2),(0x0e,4),(0x10,2),(0x12,4),(0x10,2)]*2,
        [(0x32,12),(8,8)],
    ]
    for field,op in (('Lo','<'),('Hi','>')):
        lines.extend(['MkAction'+field+':',' .byte '+','.join(op+'MkAction'+str(i) for i in range(len(actions)))])
    expanded=[[pose for pose,duration in action for _ in range(duration)] for action in actions]
    lines.extend(['MkActionLength:',' .byte '+','.join(str(len(a)) for a in expanded)])
    for i,action in enumerate(expanded):
        lines.append('MkAction'+str(i)+':')
        for j in range(0,len(action),16):lines.append(' .byte '+','.join(str(p) for p in action[j:j+16]))
    lines.append('.popseg')
    (ROOT/'src/meta_knight_art.inc').write_text('\n'.join(lines)+'\n')
    OUT.mkdir(exist_ok=True)
    manifest = dict(source=str(SOURCE), source_sha256=hashlib.sha256(original).hexdigest(),
                    table_bank=0x31, table_address=0x8000, chr_window=[0x80,0xa4],
                    first_chr=356, bytes=len(packed), family_bytes=len(kirby)+len(packed),
                    original_pixels=True, source_body_palette=[0x36,0x14,0x0f],
                    source_sword_palette=[0x30,0x37,0x17], sword_world_palette=[0x30,0x27,0x16],
                    palette_policy='Exact body colors; original sword silhouettes/three shades remapped to stable world weapon palette2. This is not exact sword hue parity.',
                    flight=False, health_indices_preserved=[11,12,13], frames=frames,
                    descriptor_policy='Reverse native forward-OAM descriptors for the port descending emitter; preserve native overlap priority.',
                    actions=[dict(kind=i,poses=expanded[i]) for i in range(len(actions))],
                    sha256=hashlib.sha256(packed).hexdigest())
    (OUT/'art-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    image = Image.new('RGB',(12*64,8*64),(72,72,72))
    draw = ImageDraw.Draw(image)
    colors = {0:[(0,0,0),(254,204,197),(131,25,153),(0,0,0)],
              2:[(0,0,0),(181,49,32),(255,254,255),(254,174,50)]}
    for index, frame in enumerate(frames):
        ox,oy = index%12*64,index//12*64
        draw.text((ox+2,oy+2),format(index,'02X'),fill='white')
        bank = buckets[(frame['physical_chr']-356)//2]
        # The descending port emitter gives the LAST packed descriptor the
        # lowest hardware slot, hence the highest native foreground priority.
        for part in frame['parts']:
            tile = bank[part['tile']//2]
            for y in range(16):
                sy = 15-y if part['attr']&128 else y
                for x in range(8):
                    sx = x if part['attr']&64 else 7-x
                    v = (tile[sy//8*16+sy%8]>>sx&1)|((tile[sy//8*16+sy%8+8]>>sx&1)<<1)
                    if v:
                        px,py=ox+20+sign(part['dx']&255)+x,oy+10+sign(part['dy']&255)+y
                        if 0<=px<image.width and 0<=py<image.height:
                            image.putpixel((px,py),colors[part['attr']&3][v])
    image.save(OUT/'native-animation-contact.png')
    print(json.dumps({k:manifest[k] for k in ('bytes','family_bytes','sha256')}))


if __name__ == '__main__':
    main()
