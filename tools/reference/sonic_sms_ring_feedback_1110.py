"""In-memory Sonic ring presentation on the existing body page and a typed row."""
from hashlib import sha256
from pathlib import Path

from sonic_sms_compact_cold_worker_1110 import assemble

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'tools/reference/sonic_sms_ring_feedback_1110.s'
DONOR_PIN = '6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b'
ART_PAGE, CODE_PAGE, CODE = 224, 334, 0xd800
BODY = (0, 2, 32, 34)


def unpack_art(blob):
    """Decode the four-byte blocks read by SMS load_art at $043A..$04E0."""
    tokens, literals, count = (int.from_bytes(blob[i:i + 2], 'little') for i in (2, 4, 6))
    assert tokens == 8 + (count + 7) // 8 and tokens <= literals < len(blob)
    output = bytearray()
    token, literal = tokens, literals
    for index in range(count):
        if blob[8 + index // 8] & (1 << (index & 7)):
            item = blob[token]
            token += 1
            if item >= 0xf0:
                item = (item - 0xf0) * 256 + blob[token]
                token += 1
            at = literals + item * 4
        else:
            at = literal
            literal += 4
        assert at + 4 <= len(blob)
        output.extend(blob[at:at + 4])
    assert token == literals and literal == len(blob)
    return bytes(output)


def pixels(tile):
    assert len(tile) == 32
    return tuple(tuple(sum((tile[y * 4 + p] >> (7 - x) & 1) << p for p in range(4))
                       for x in range(8)) for y in range(8))


def nes_pair(top, bottom, colors):
    image = bytearray()
    for block in (top, bottom):
        for p in (0, 1):
            for row in pixels(block):
                image.append(sum((colors[c] >> p & 1) << (7 - x) for x, c in enumerate(row)))
    return bytes(image)


def original_art(rom):
    assert sha256(rom).hexdigest() == DONOR_PIN
    common = unpack_art(rom[0x2f92e:0x2fcf0])
    assert len(common) == 0x40 * 32
    tiles = [common[i:i+32] for i in range(0, len(common), 32)]
    order = tuple(rom[0x23f9:0x23ff])
    assert order == (5, 4, 3, 2, 1, 0)
    frames = []
    for n in order:
        at = 0x2fcf0 + n * 128
        frames.append(tuple(rom[at+i:at+i+32] for i in range(0, 128, 32)))
    return tiles, frames


def atlas(old, rom):
    """Keep the four live standing/portrait pairs and fill only retired poses."""
    assert len(old) == 1024
    common, world = original_art(rom)
    stage = unpack_art(rom[0x2a12a:0x2a12a+2835])
    sprite_colors = (0, 3, 3, 3, 3, 3, 1, 2) + (0,) * 8
    world_colors = (0,) * 13 + (1, 3, 2)
    image = bytearray(old)
    available = iter(n for n in range(0, 64, 2) if n not in BODY)
    placed = {}

    def put(top, bottom, colors):
        data = nes_pair(top, bottom, colors)
        if not any(data):
            return 255
        if data not in placed:
            tile = next(available)
            image[tile*16:tile*16+32] = data
            placed[data] = tile
        return placed[data]

    def common_pair(n):
        return put(common[n-0x80], common[n-0x7f], sprite_colors)

    digits = tuple(common_pair(0x80 + 2*n) for n in range(10))
    glyphs = tuple(common_pair(n) for n in (0xa6, 0xa8))
    assert len(set(digits)) == 10
    world_pair = tuple(put(world[0][i], world[0][i+2], world_colors) for i in (0, 1))
    spark = (put(stage[0x5a*32:0x5b*32], stage[0x5b*32:0x5c*32], sprite_colors), common_pair(0xb2))
    drops = []
    for index in (0x1c, 0x1d):
        frame = rom[0x20000+index*288:0x20000+(index+1)*288]
        for sprite in range(6):
            at = 48*sprite
            top, bottom = frame[at:at+24], frame[at+24:at+48]
            expand = lambda tile: bytes(v for y in range(8) for v in (*tile[y*3:y*3+3], 0))
            drops.append(put(expand(top), expand(bottom), sprite_colors))
    assert len(placed) <= 28 and 255 not in (*digits, *glyphs, *world_pair, *spark)
    assert all(image[t*16:t*16+32] == old[t*16:t*16+32] for t in BODY)
    return bytes(image), dict(digits=digits, glyphs=glyphs, world=world_pair, spark=spark, drops=tuple(drops), pairs=len(placed))


def make_tenth(p):
    old = p['ring_boot']
    base = old['source']
    needle = 'RingColdMore:\n cmp #8\n bne RingColdDone\n'
    assert base.count(needle) == 1
    base = base.replace(needle, '''RingColdMore:
 cmp #10
 bcs RingColdDone
 cmp #8
 bne RingColdContiguous
''')
    needle = ' sta R1\n jmp NextRow\nRingColdDone:'
    assert base.count(needle) == 1
    base = base.replace(needle, ' sta R1\nRingColdContiguous:\n jmp NextRow\nRingColdDone:')
    assert base.rstrip().endswith(',333')
    result = assemble(base.rstrip() + ',334\n', {'SONIC_COLD': (0xd25e, 139), 'COLD_TAIL': (0xd31f, 225)})
    assert result['used']['SONIC_COLD'] == 124 and result['used']['COLD_TAIL'] == 37
    return result


def build(p, bundle, body, rom):
    old = p['packet']
    assert old['cookie'].hex() == 'a72b01986e0ad768012091a2a511fedc'
    art, placement = atlas(body, rom)
    boot = make_tenth(p)
    ring = p['ring_program']['symbols']
    native = p['metadata']['symbols']
    fields = ('GameEngineSubroutine', 'OperMode', 'OperMode_Task', 'WorldNumber', 'LevelNumber',
              'AreaAddrsLOffset', 'FrameCounter', 'CurrentOAMOffset', 'GuestOamRotationActive',
              'RgOamRotation', 'Sprite_Y_Position', 'Sprite_Tilenumber', 'Sprite_Attributes',
              'Sprite_X_Position', 'ScreenLeft_X_Pos', 'ScreenLeft_PageLoc')
    definitions = {name: int(bundle['syms'][name]['val'], 0) for name in fields}
    definitions.update({name: ring[name] for name in ('RingProject', 'RingBCD', 'DropRecord', 'SceneTiles',
                                                    'SparkX', 'SparkY', 'SparkTimer', 'HostReady')})
    definitions.update({name: native[name] for name in ('MetaDraw', 'DrawIndex', 'DrawFlip', 'DrawAttr')})
    for key in ('glyphs', 'world', 'spark'):
        definitions.update({f'{key}{i}': tile for i, tile in enumerate(placement[key])})
    data = '\n'.join(f'{key}: .byte '+','.join(str(n) for n in placement[key]) for key in ('digits', 'drops'))
    preamble = '\n'.join(f'{name} = ${at:04x}' for name, at in definitions.items())
    output = assemble(preamble+'\n'+SOURCE.read_text(encoding='ascii')+'\n'+data,
                      {'RING_FEEDBACK': (CODE, 1024)})
    code = output['images']['RING_FEEDBACK'].ljust(1024, b'\xff')
    metadata, kernel = (bytearray(old[key]) for key in ('metadata', 'kernel'))
    for segment, pc in (('SONIC_COLD', 0xd25e), ('COLD_TAIL', 0xd31f)):
        before = p['ring_boot']['images'][segment]
        at = pc - 0xd000
        assert metadata[at:at+len(before)] == before
        new = boot['images'][segment]
        assert metadata[at+len(before):at+len(new)] == b'\xff'*(len(new)-len(before))
        metadata[at:at+len(new)] = new
    draw = native['MetaDraw']
    assert metadata[0x106:0x109] == b'\x4c'+draw.to_bytes(2, 'little')
    metadata[0x107:0x109] = output['symbols']['DrawFeedback'].to_bytes(2, 'little')
    project = p['service']['symbols']['HostProject'] - 0xa000
    assert kernel[project:project+3] == b'\x4c'+ring['RingProject'].to_bytes(2, 'little')
    kernel[project+1:project+3] = output['symbols']['SparkTick'].to_bytes(2, 'little')
    cookie = bytes((0xa7, 43, 1)) + sha256(kernel+metadata+old['ring_extension']+code+art).digest()[:13]
    packet = dict(old, kernel=bytes(kernel), metadata=bytes(metadata), cookie=cookie,
                  startup=dict(image=boot['images']['SONIC_COLD'], symbols=boot['symbols'],
                               tail=boot['images']['COLD_TAIL'], tail_address=0xd31f),
                  ring_feedback=code, ring_feedback_page=CODE_PAGE, ring_art=art)
    return dict(p, packet=packet, feedback_program=output, feedback_atlas=placement)
