"""Mount a Prince-only pipe approach control using his existing cold decoder."""

import struct

import compose_bub_epoch_1123 as Nightly
import compose_prince_oneup_lift_1123 as Cold


Packet, H = Cold.Packet, Cold.H
PARENT = Nightly.CANDIDATE
CANDIDATE = 'd38c42bf5073b3b81a9cbc39bbf5e5b82c4316a5521970f6f0cc9583ac2c6ba8'
PAGE = 931
PAGES = (*Packet.PAGES, PAGE)
GATE = 0xB39F
OLD_GATE = bytes.fromhex('a9038d2cc0a5dc8d0ac42092ab4c83c3')
OLD_WORKER_SIZE = 476
HEAD = Packet.LOADER + OLD_WORKER_SIZE
TABLE = HEAD - 30
HIGH_PAGE_READ = Packet.LOADER + Cold.BOOT_BYTES + 0x10E
ORIGINAL_RAW1_SIZE = 608
SOURCE = Packet.R / 'tools/reference/prince_pipe_approach_1123.s'


def split_packed(data, position, rows):
    packed = [None] * 4
    for index in Cold.STREAM_ORDER:
        size = rows[index][2]
        packed[index] = data[position:position + size]
        position += size
    return packed, position


def extract(image):
    start = Packet.CHR + PAGE * 1024
    data = Cold._backing(image) + image[start:start + 1024]
    header = data[:HEAD + 2]
    table = header[TABLE:]
    assert PAGES[-16:] == tuple(lo | (hi << 8) for lo, hi in zip(table[:16], table[16:], strict=True))
    rows = tuple(struct.iter_unpack('<4H', header[TABLE-32:TABLE]))
    packed, position = split_packed(data, len(header), rows)
    chunks = tuple(Packet.decode(value, row[3]) for value, row in zip(packed, rows, strict=True))
    assert data[position:] == b'\xff' * (len(data) - position)
    cookie = Packet.cookie(chunks, data[:position])
    assert image[Packet.COOKIE:Packet.COOKIE + len(cookie)] == cookie
    return chunks, rows, cookie, position


def write_packet(raw, header, chunks, packed, pages):
    payload = bytes(header) + b''.join(packed[i] for i in Cold.STREAM_ORDER)
    assert len(payload) <= len(pages) * 1024
    image = bytearray(raw)
    cookie = Packet.cookie(chunks, payload)
    image[Packet.COOKIE:Packet.COOKIE + len(cookie)] = cookie
    for i, page in enumerate(pages):
        at = Packet.CHR + page * 1024
        image[at:at + 1024] = payload[i*1024:(i+1)*1024].ljust(1024, b'\xff')
    return bytes(image), cookie, len(payload)


def compose(raw):
    assert H(raw) == PARENT
    page_at = Packet.CHR + PAGE * 1024
    assert PAGE not in Packet.PAGES and raw[page_at:page_at + 1024] == b'\xff' * 1024
    chunks, old_config, _, used = Cold.extract(raw)
    assert used == len(Packet.PAGES) * 1024 - 1
    core, metadata, state, lift = chunks
    assert len(lift) == ORIGINAL_RAW1_SIZE
    bundle = dict(Cold.W.Symbols.bundle(), raw=raw)
    names = ('SavedJoypad1Bits', 'Player_X_Position', 'Player_PageLoc', 'Player_Y_Position', 'BlockBufferAddr')
    symbols = {name: Cold.W.address(bundle, name) for name in names}
    assert tuple(symbols.values()) == (0xDC, 0x75, 0x5C, 0xBD, 0x95D8)
    entry = 0xA000 + len(lift)
    source = SOURCE.read_text(encoding='ascii')
    _, labels = Cold.Lift.assemble(source, dict(symbols, ReadPipeOperand=entry), entry)
    variables = dict(ReadPipeOperand=labels['ReadPipe'] + 1, ClimbStartY=labels['ClimbTime'] + 1)
    controls, labels = Cold.Lift.assemble(source, dict(symbols, **variables), entry)
    controls += bytes(2)
    assert labels['PrincePipeControls'] == entry
    start = GATE - 0xA000
    assert core[start:start + len(OLD_GATE)] == OLD_GATE
    gate = Cold.Lift.gateway(entry, bundle).ljust(len(OLD_GATE), b'\xea')
    core = core[:start] + gate + core[start + len(gate):]
    chunks = (core, metadata, state, lift + controls)

    # Preserve the original physical bitstream for the two unchanged middle
    # inputs. The resize only moves its starting offset within the carrier.
    backing = Cold._backing(raw)
    old_packed, position = split_packed(backing, HEAD, old_config)
    assert position == used
    packed = (Packet.encode(core), old_packed[1], old_packed[2], Packet.encode(chunks[3]))
    config = Cold._stage_spec(chunks, packed)
    assert config[0][2] <= 0xDC00 - 0xC500 + 0xC500 - Cold.WRAP
    assert config[1][0] >= 0xC900 and all(Cold.STAGING + config[i][2] < 0xC800 for i in (2, 3))
    assert Cold.WORKER_START + OLD_WORKER_SIZE + 2 - Cold.BOOT_BYTES <= Cold.WRAP

    header = bytearray(backing[:HEAD])
    # The worker already increments the page index after a 1 KiB read. Its
    # parallel table grows by one entry, moving the high-byte table by one.
    assert bytes(header[HIGH_PAGE_READ:HIGH_PAGE_READ + 3]) == bytes.fromhex('bd6cc2')
    header[HIGH_PAGE_READ + 1] += 1
    assert header[TABLE - 35:TABLE - 32] == bytes.fromhex('013a0c')
    header[TABLE - 34] += 2
    struct.pack_into('<16H', header, TABLE - 32, *(field for row in config for field in row))
    header[TABLE:] = bytes(p & 255 for p in PAGES[-16:]) + bytes(p >> 8 for p in PAGES[-16:])
    image, cookie, used = write_packet(raw, header, chunks, packed, PAGES)
    assert len(Packet.PAGES) * 1024 < used
    assert extract(image) == (chunks, config, cookie, used) and H(image) == CANDIDATE
    return image


def inverse(image):
    assert H(image) == CANDIDATE
    (core, metadata, state, lift), rows, _, _ = extract(image)
    start = GATE - 0xA000
    core = core[:start] + OLD_GATE + core[start + len(OLD_GATE):]
    lift = lift[:ORIGINAL_RAW1_SIZE]
    page = Packet.CHR + PAGE * 1024
    data = Cold._backing(image) + image[page:page + 1024]
    packed, _ = split_packed(data, HEAD + 2, rows)
    packed[0], packed[3] = Packet.encode(core), Packet.encode(lift)
    chunks = (core, metadata, state, lift)
    config = Cold._stage_spec(chunks, packed)
    header = bytearray(data[:TABLE])
    header[HIGH_PAGE_READ + 1] -= 1
    header[TABLE - 34] -= 2
    struct.pack_into('<16H', header, TABLE - 32, *(field for row in config for field in row))
    header.extend(bytes(p & 255 for p in Packet.PAGES[-15:]))
    header.extend(bytes(p >> 8 for p in Packet.PAGES[-15:]))
    raw, _, _ = write_packet(image, header, chunks, packed, Packet.PAGES)
    raw = raw[:page] + b'\xff' * 1024 + raw[page + 1024:]
    assert H(raw) == PARENT
    return raw
