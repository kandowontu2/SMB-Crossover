"""Pack original DK background/sprite poses into native 8x16 sprite records."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'build/dk-source-assets-v1'
ROM = Path('C:/NES/Donkey Kong (World) (Rev 1).nes')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def bound(path):
    path = Path(path).resolve()
    data = path.read_bytes()
    return dict(path=str(path), bytes=len(data), sha256=digest(data))


def decode(tile):
    return bytes(((tile[y] >> (7-x)) & 1) | (((tile[y+8] >> (7-x)) & 1) << 1)
                 for y in range(8) for x in range(8))


def main():
    assert not (OUT / 'handoff.json').exists(), 'Frozen source asset unit'
    match = ROOT / 'build/dk-original-source-match-v1/proof.json'
    proof = json.loads(match.read_text())
    assert proof['passed'] and proof['full_PRG_CHR_payload_exact']
    raw = ROM.read_bytes()
    assert digest(raw) == proof['original']['sha256']
    prg, chrdata = raw[16:16+16384], raw[16+16384:]
    # Reset and SetInitRegsAndClearScreen select BG$1000; native falling DK
    # uses sprite$0000. Records are column-major, six columns of four tiles.
    frames = [
        ('pickup-barrel', 0xC60C), ('holding-barrel', 0xC625),
        ('side-toss', 0xC63E), ('idle', 0xC657),
        ('chest-left', 0xC670), ('chest-right', 0xC689),
        ('defeated-1', 0xC71C), ('defeated-2', 0xC735),
    ]
    source_frames = []
    for name, address in frames:
        record = prg[address-0xC000:address-0xC000+25]
        assert len(record) == 25 and record[0] == 0x46
        source_frames.append(dict(name=name, source_address=hex(address), table=list(record),
                                  pattern_base=0x1000, tiles=list(record[1:])))
    source_frames.append(dict(name='native-falling-sprite', source_address='CODE_CDCA/F080',
                              pattern_base=0, tiles=list(range(0x40, 0x58))))
    pages = []
    records = []
    for frame in source_frames:
        pixels = bytearray(48*32)
        tiles = frame['tiles']
        for column in range(6):
            for row in range(4):
                tile = tiles[column*4+row]
                offset = frame['pattern_base'] + tile*16
                pattern = decode(chrdata[offset:offset+16])
                for y in range(8):
                    start = (row*8+y)*48 + column*8
                    pixels[start:start+8] = pattern[y*8:y*8+8]
        parts = []
        for column in range(6):
            for pair_row in range(2):
                top, bottom = tiles[column*4+pair_row*2:column*4+pair_row*2+2]
                base = frame['pattern_base']
                pair = chrdata[base+top*16:base+top*16+16] + chrdata[base+bottom*16:base+bottom*16+16]
                if any(pair):
                    parts.append((pair, column*8-16, pair_row*16-1))
        patterns = {pair for pair, _, _ in parts}
        candidates = [(len(patterns-set(page)), i) for i, page in enumerate(pages)
                      if len(set(page)|patterns) <= 32]
        if candidates:
            _, page_index = min(candidates)
        else:
            page_index = len(pages)
            pages.append([])
        page = pages[page_index]
        for pair in sorted(patterns):
            if pair not in page:
                page.append(pair)
        packed = [len(parts)*4]
        reconstructed = bytearray(48*32)
        for pair, x, y in parts:
            index = page.index(pair)
            packed += [index*2, 0, y & 255, x & 255]
            # Prove bitplane/position equality of the actual packed records,
            # including the OAM display-Y+1 convention and transparent pixels.
            for half in range(2):
                tile_pixels = decode(page[index][half*16:half*16+16])
                for yy in range(8):
                    at = (y+1+half*8+yy)*48 + (x+16)
                    reconstructed[at:at+8] = tile_pixels[yy*8:yy*8+8]
        assert reconstructed == pixels, frame['name']
        records.append(dict(**frame, relative_CHR_page=page_index, descriptor=packed,
                            colored_pixels=sum(v != 0 for v in pixels), parts=len(parts),
                            source_pixel_SHA256=digest(pixels), pixel_exact=True,
                            _pixels=bytes(pixels)))
    assert len(pages) <= 4
    patterns = b''.join(b''.join(page) + bytes((32-len(page))*32) for page in pages)
    patterns += bytes(4096-len(patterns))
    # Original stage25M palette2 and falling-sprite palette3 share these roles.
    palette = list(prg[0xF55B-0xC000+3+8:0xF55B-0xC000+3+12])
    assert palette == [0x0F, 0x30, 0x36, 0x06]
    OUT.mkdir(exist_ok=True)
    (OUT / 'dk.chr').write_bytes(patterns)
    lines = ['; Original NES DK source pixels, native8x16 descriptors; no host hooks.',
             '.segment "DONKEY_KONG_ART"', 'DkArtStart:', 'DkPosePages:',
             ' .byte '+','.join(str(r['relative_CHR_page']) for r in records),
             'DkPoseLo:', ' .byte '+','.join('<DkPose'+str(i) for i in range(len(records))),
             'DkPoseHi:', ' .byte '+','.join('>DkPose'+str(i) for i in range(len(records)))]
    for i, record in enumerate(records):
        lines += ['DkPose'+str(i)+':', ' .byte '+','.join(str(v) for v in record['descriptor'])]
    lines += ['DkPalette: .byte '+','.join('$%02x' % v for v in palette), 'DkArtEnd:']
    (OUT / 'dk-art.inc').write_text('\n'.join(lines)+'\n')
    image = Image.new('RGB', (3*192, 3*156), '#18242c')
    draw = ImageDraw.Draw(image)
    colors = [(24,36,44), (252,252,252), (248,164,192), (108,6,0)]
    for i, record in enumerate(records):
        left, top = (i%3)*192, (i//3)*156
        draw.text((left+6, top+4), record['name'], fill='white')
        for y in range(32):
            for x in range(48):
                value = record['_pixels'][y*48+x]
                if value:
                    draw.rectangle((left+24+x*3, top+32+y*3, left+26+x*3, top+34+y*3), fill=colors[value])
        record.pop('_pixels')
    image.save(OUT / 'original-dk-poses.png')
    result = dict(status='Original-source authenticated packed assets; no host implementation/native claim',
                  original=bound(ROM), source_match=bound(match), tool=bound(__file__),
                  source_repository='https://github.com/RussianManSMWC/Donkey-Kong-NES-Disassembly/tree/343f4c81880a253c0e8ede81fe7c21f205815280',
                  frames=records, used_1KB_pages=len(pages), pattern_pairs_per_page=[len(p) for p in pages],
                  proposed_CHR=[820, 823], original_palette=palette,
                  palette_preview='Approximate NES RGB display of exact source indices, not an emulated all-area palette proof',
                  original_geometry='48x32, six8x8 columns converted without scaling into native8x16 pairs',
                  new_playable_policy='Original DK is a non-player enemy, not Jumpman. Playable controls, collision bounds, traversal, pickups and walk selection still require an explicit crossover adaptation; no original DK player physics claim.',
                  open=['Full host menu/lives/graphics/collision/combat/lifecycle/audio integration', 'Actual native OAM/scanline/graphics/1-1 and earned-powerup tests'],
                  outputs=[bound(OUT / n) for n in ['dk.chr', 'dk-art.inc', 'original-dk-poses.png']], native=False)
    (OUT / 'handoff.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(frames=len(records), pages=len(pages), CHR_bytes=len(patterns),
                          handoff=bound(OUT / 'handoff.json'))))


if __name__ == '__main__':
    main()
