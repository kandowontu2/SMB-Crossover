"""Extract supplied Super Sunny World player art without an emulator launch.

Native pointer tables, animation descriptors, palette data and the actual
6502 OAM interpreter are authenticated by the complete supplied ROM hash.
Only sunny* assets and src/sunny_art.inc are generated. No stock Mario art.
"""
from pathlib import Path
import hashlib
import json
import sys
from PIL import Image, ImageDraw

R = Path(__file__).resolve().parents[1]
A = R / 'chr/characters'
SOURCE = Path('C:/Users/kando/Downloads/sunny_rc_1_0_2026_04_26.nes')
EXPECTED = 'b9487289afa9a2f2023886f1e5ffb9b5a32d4fe786eeca3b77350c87ac3622d2'
sha = lambda b: hashlib.sha256(b).hexdigest()
FIRST = 724
# Global frame0..16: native small table.17..34: native large table.
POSES = ['idle', 'walk0', 'walk1', 'walk2', 'skid', 'jump', 'fall',
         'crouch', 'swim0', 'swim1', 'swim2', 'climb0', 'climb1',
         'death', 'throw', 'growth', 'portrait']
SMALL = [0, 3, 4, 3, 2, 5, 5, 10, 12, 13, 12, 15, 16, 6, 8, 0, 0]
BIG = [17, 20, 21, 22, 19, 23, 24, 33, 27, 28, 29, 31, 32, 25, 30, 17, 17]


def pixel(chr_data, page, tile, x, y):
    at = page * 1024 + tile * 16
    return ((chr_data[at+y] >> (7-x)) & 1) | (((chr_data[at+y+8] >> (7-x)) & 1) << 1)


def record(prg, pointer):
    at = 7*8192 + pointer-0x8000
    start = at
    parts = []
    while prg[at] != 0x80:
        assert len(parts) < 32
        x, y, tile, attr = prg[at:at+4]
        parts.append((x-256 if x & 128 else x, y-256 if y & 128 else y, tile, attr))
        at += 4
    return parts, start, prg[start:at+1]


def native_oam(prg, pointer, face):
    """Execute the actual source $F557 interpreter, including native mirror."""
    sys.path.insert(0, str(R / 'tools/audit'))
    from verify_native_relocation import NesMPU
    m = [0] * 65536
    m[0x8000:0xa000] = prg[7*8192:8*8192]
    m[0xe000:] = prg[63*8192:]
    m[0x6b] = 0
    m[0x6c] = 7
    m[0x700:0x702] = [100, 100]  # real software-stack y/x arguments
    m[0x3c] = int(face == 2)
    m[0x3d] = 8
    m[0x3e] = 0
    m[0x3f] = 255  # preserve the source record's own palette attributes
    cpu = NesMPU(memory=m, pc=0xf557)
    cpu.a, cpu.x, cpu.sp = pointer & 255, pointer >> 8, 253
    cpu.stPushWord(0x5aff)
    before = cpu.processorCycles
    for _ in range(6000):
        if cpu.pc == 0x5b00:
            break
        cpu.step()
    assert cpu.pc == 0x5b00 and cpu.sp == 253
    return [tuple(m[0x200+i:0x204+i]) for i in range(0, m[0x29], 4)], cpu.processorCycles-before


def native_pixels(chr_data, page, oam):
    out = {}
    for y, tile, attr, x in oam:
        for yy in range(8):
            for xx in range(8):
                v = pixel(chr_data, page, tile, 7-xx if attr & 64 else xx,
                          7-yy if attr & 128 else yy)
                if v:
                    out[x-100+xx, y-100+yy] = v
    return out


def encode_cell(pixels, x0, y0):
    return bytes(sum(((pixels.get((x0+x, y0+half+y), 0) >> plane) & 1) << (7-x)
                     for x in range(8))
                 for half in (0, 8) for plane in (0, 1) for y in range(8))


def main():
    raw = SOURCE.read_bytes()
    assert sha(raw) == EXPECTED and raw[:4] == b'NES\x1a'
    assert raw[4:6] == bytes([32, 32])
    prg, chr_data = raw[16:0x80010], raw[0x80010:]
    # Exact current parent free bytes, not a high-water inference.
    base = R / 'build/smb-crossover-mmc5-expanded.nes'
    parent = base.read_bytes()
    spans = [('core', 16+81*8192+0x1200, 16+82*8192, 255),
             ('art', 16+94*8192+0xe00, 16+95*8192, 255),
             ('chr', 16+128*8192+FIRST*1024, 16+128*8192+(FIRST+16)*1024, 0)]
    extent = {}
    for name, lo, hi, fill in spans:
        b = parent[lo:hi]
        assert len(b) == hi-lo and b == bytes([fill]) * len(b), ('Occupied Sunny span', name)
        extent[name] = dict(file_offset=lo, bytes=len(b), fill=fill, sha256=sha(b))
    # Player animation descriptors: duration,count,8 frame slots,CHR page.
    descriptors = []
    for n in range(24):
        at = 0x2f5c + n*2
        ptr = int.from_bytes(prg[at:at+2], 'little')
        d = prg[0x2000+ptr-0x8000:0x2000+ptr-0x8000+11]
        assert 1 <= d[1] <= 8 and d[10] in [4, 12, 24]
        descriptors.append(dict(id=n, pointer=ptr, duration=d[0], frames=list(d[2:2+d[1]]),
                                CHR_page=d[10], bytes=d.hex()))
    palette_pointers = [int.from_bytes(prg[0x1064a+i*2:0x1064c+i*2], 'little') for i in range(5)]
    palettes = [prg[0x10000+p-0x8000:0x10000+p-0x8000+16] for p in palette_pointers]
    assert all(p[1:4] == bytes([4, 0x26, 0x36]) for p in palettes)
    assert prg[0xe3b5:0xe3c9] == bytes.fromhex('a9122056eca9264cc683a9122056eca92a2099f4')
    output = bytearray(16*1024)
    page = 0
    slots = {}
    frames = []
    tests = []
    native_images = []
    for large, count, table in [(False, 17, 0x8115), (True, 18, 0x8309)]:
        for n in range(count):
            at = 7*8192+table-0x8000+n*2
            ptr = int.from_bytes(prg[at:at+2], 'little')
            # These are the actual descriptor-derived source bank choices.
            source_page = 4 if not large else (12 if n <= 7 or n in [10, 11, 12] else 24)
            parts, source_at, source_record = record(prg, ptr)
            right_oam, right_cycles = native_oam(prg, ptr, 1)
            left_oam, left_cycles = native_oam(prg, ptr, 2)
            pixels = native_pixels(chr_data, source_page, right_oam)
            native_left = native_pixels(chr_data, source_page, left_oam)
            assert pixels
            assert native_left == {(15-x, y):v for (x, y), v in pixels.items()}
            # Native player anchor has feet+20. SMB player anchor feet+32.
            # Exact pixels are shifted+12Y, never scaled or recolored.
            host = {(x, y+12):v for (x, y), v in pixels.items()}
            minx, maxx = min(x for x, y in host), max(x for x, y in host)
            miny, maxy = min(y for x, y in host), max(y for x, y in host)
            cells = []
            for y in range(miny, maxy+1, 16):
                for x in range(minx, maxx+1, 8):
                    cell = encode_cell(host, x, y)
                    if any(cell):
                        cells.append((x, y, cell))
            needed = len({c for x, y, c in cells if c not in slots})
            if len(slots)+needed > 32:
                page += 1
                slots = {}
            assert page < 16 and len(cells) <= 8
            packed = []
            for x, y, cell in cells:
                if cell not in slots:
                    slots[cell] = len(slots)
                tile = slots[cell]*2
                output[page*1024+tile*16:page*1024+tile*16+32] = cell
                packed.append(dict(x=x, y=y, tile=tile))
            decoded = {}
            for part in packed:
                for y in range(16):
                    for x in range(8):
                        v = pixel(output, page, part['tile']+(y//8), x, y%8)
                        if v:
                            decoded[part['x']+x, part['y']+y] = v
            assert decoded == host, ('Packed native pixel mismatch', large, n)
            decoded_left = {}
            for part in packed:
                for y in range(16):
                    for x in range(8):
                        v = pixel(output, page, part['tile']+(y//8), 7-x, y%8)
                        if v:
                            decoded_left[8-part['x']+x, part['y']+y] = v
            assert decoded_left == {(x, y+12):v for (x, y), v in native_left.items()}
            frames.append(dict(id=len(frames), native_large=large, native_index=n,
                               native_pointer=ptr, native_PRG_offset=source_at,
                               native_record=source_record.hex(), native_CHR_page=source_page,
                               physical_page=FIRST+page, parts=packed,
                               opaque_bounds=[minx, miny, maxx+1, maxy+1],
                               pixels=len(pixels), indexed_pixel_sha256=sha(bytes(v for k,v in sorted(host.items())))))
            tests.append(dict(frame=len(frames)-1, native_right_cycles=right_cycles,
                              native_left_cycles=left_cycles, native_OAM_parts=len(right_oam),
                              packed_parts=len(packed), raster_exact=True, mirror_exact=True))
            native_images.append(host)
    (A/'sunny.chr').write_bytes(output)
    lines = ['; Exact Super Sunny World RC1 supplied-ROM pixels; Matt Hughson / Kenneth Fejer.',
             '; Native8x8 records repacked losslessly to host8x16; +12Y anchor translation.',
             '.pushseg', '.segment "SUNNY_ART"', 'SunnyArtBegin:']
    for frame in frames:
        for face in ['R', 'L']:
            lines += [f'SunnyFrame{frame["id"]}{face}:', f' .byte {len(frame["parts"])*4}']
            for part in frame['parts']:
                x = part['x'] if face == 'R' else 8-part['x']
                attr = 0 if face == 'R' else 64
                lines.append(f' .byte MetaspriteVramOffset{{${part["tile"]:02x}}}, {{SPRITE_BANK_0}}, ${attr:02x}, {part["y"]}, {x}')
    for face in ['R', 'L']:
        for name, sigil in [('Lo', '<'), ('Hi', '>')]:
            lines += [f'Sunny{face}{name}:', ' .byte '+','.join(f'{sigil}SunnyFrame{f["id"]}{face}' for f in frames)]
    lines += ['SunnyChrLow:', ' .byte '+','.join(str(f['physical_page'] & 255) for f in frames),
              'SunnySemanticSmall:', ' .byte '+','.join(map(str, SMALL)),
              'SunnySemanticBig:', ' .byte '+','.join(map(str, BIG)),
              'SunnyArtEnd:', '.assert SunnyArtEnd-SunnyArtBegin<=$1200,error,"Sunny C94 CE00..DFFF overflow"', '.popseg', '']
    (R/'src/sunny_art.inc').write_text('\n'.join(lines), newline='\n')
    sheet = Image.new('RGB', (7*130, 5*158), (35, 40, 48))
    draw = ImageDraw.Draw(sheet)
    # Standard preview RGB approximation of actual native NES palette04/26/36.
    colors = {1:(68,0,100), 2:(255,120,170), 3:(255,205,180)}
    for i, pixels in enumerate(native_images):
        x0, y0 = (i%7)*130, (i//7)*158
        f = frames[i]
        draw.text((x0+4, y0+3), f'{"large" if f["native_large"] else "small"}{f["native_index"]} / CHR{f["native_CHR_page"]}', fill='white')
        for (x, y), v in pixels.items():
            draw.rectangle((x0+28+x*3, y0+24+y*3, x0+30+x*3, y0+26+y*3), fill=colors[v])
    sheet.save(A/'sunny-review.png')
    manifest = dict(source_ROM=str(SOURCE), source_sha256=EXPECTED,
        source_header=raw[:16].hex(), mapper=4, source_PRG_bytes=len(prg), source_CHR_bytes=len(chr_data),
        credit='Super Sunny World: Matt Hughson; lead artist Kenneth Fejer. Supplied RC1 ROM; not a stock Mario recolor.',
        credit_url='https://mhughson.itch.io/super-sunny-world',
        requested_gameplay='Separate ID23; existing Mario-family behavior pending ROOT route integration. No original Sunny powers imported or invented.',
        source_regions=dict(small_pointer_table=dict(bank=7, address=0x8115, count=17),
          large_pointer_table=dict(bank=7,address=0x8309,count=18),
          animation_table=dict(bank=1,address=0x8f5c,count=24),
          native_OAM_interpreter=dict(bank=63,address=0xf557,end=0xf5ea,sha256=sha(prg[0x7f557:0x7f5ea])),
          palette_pointer_table=dict(bank=8,address=0x864a,count=5)),
        source_control_tools={str(p.relative_to(R)).replace('\\','/'):sha(p.read_bytes()) for p in
            [Path(__file__),R/'tools/audit/verify_native_relocation.py']},
        normal_NES_palette=[4,0x26,0x36], alternate_power_NES_palette=[4,0x2a,0x36],
        fire_palette_scope='Mario Fire tier uses source native alternate power colors; original Sunny Fire ability is not claimed.',
        native_animation_descriptors=descriptors, native_area_sprite_palettes=[p.hex() for p in palettes],
        source_frame_count=len(frames), frames=frames, semantic_poses=POSES,
        small_semantic_frames=SMALL, big_and_fire_semantic_frames=BIG,
        semantic_scope='Mario pose categories select genuine Sunny source frames. No claim that source Sunny originally implements SMB fireball/swim/skid/growth mechanics. Portrait is genuine native standing body, no invented face crop.',
        coordinate_translation=dict(x=0,y=12,native_anchor_feet=20,host_anchor_feet=32),
        CHR_bytes=len(output), physical_pages=[FIRST,FIRST+15], used_pages=page+1,
        maximum_body_parts=max(len(f['parts']) for f in frames),
        all35_native_interpreter_and_raster_controls=tests,
        no_native_emulator=True, current_parent=dict(path=str(base),sha256=sha(parent),free_extents=extent),
        generated_files={str(p.relative_to(R)).replace('\\','/'):sha(p.read_bytes()) for p in
                         [A/'sunny.chr',A/'sunny-review.png',R/'src/sunny_art.inc']})
    (A/'sunny-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', newline='\n')
    print(json.dumps(dict(manifest=str(A/'sunny-manifest.json'),sha256=sha((A/'sunny-manifest.json').read_bytes()),
                         frames=len(frames),CHR_bytes=len(output),used_pages=page+1,
                         max_parts=manifest['maximum_body_parts'])))


if __name__ == '__main__':
    main()
