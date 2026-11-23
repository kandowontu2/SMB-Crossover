"""Compose the Prince's stock-lift trial using his existing cold carrier pages."""

from functools import lru_cache
import struct

from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

import prince_cold_packet_1111 as Packet
import probe_prince_wram1_cold_route_1123 as Lift

H, W = Lift.H, Lift.W
PARENT = Lift.B.PIN
BOOT_BYTES = 97
WORKER_START = 0xC100
WORKER_CODE_END = 0xC220
OLD_CONFIG = 0xC22B
WRAP = 0xC280
STAGING = 0xC300
STREAM_ORDER = (0, 1, 3, 2)
PARENT_LOADER = bytes.fromhex('''
08682904f059ad0260c926d052ad7507f04dad7a072918d046ad39011041ade0df0de0bfd039adabc00d0ec6
d031a200bdbfd29d00c1dd00c1d024e8d0f2bdbfd39d00c2dd00c2d016e8d0f2bd60d19d00c0dd00c0d008e8
e0fed0f04c00c11860a000201ec12000c0a008201ec12000c0a010201ec1a9bf48a9a2484c00c08c20c2ad28
c28d25c2ad29c28d26c2ad2ac28d27c2a9918d7ec1ac20c2b92bc28daac08503c8b92bc28dabc08504c8b92b
c28d21c2c8b92bc28d22c2c8b92bc28d23c2c8b92bc28d24c2c8b92bc28decc0c8b92bc28dedc0a00020f9c1
20dbc19103d103d053e603d010e604a504c9dcd008a9808503a9c28504ad23c2d003ce24c2ce23c2ad23c20d
24c2d0d0ad7ec1c9d1f01aa9d18d7ec1ad25c28d28c2ad26c28d29c2ad27c28d2ac24c38c1ad21c28503ad22
c285046068681860ad2ac2c910d00bee28c2a90c8d2ac220f9c1ad0720ee29c2d003ee2ac260ae28c2bd52c2
8d3051bd43c28d2351a9008d30512c0220ad2ac28d0620ad29c28d0620ad072060000000000000000001200c
00c500a04319df1f95c900c86b17e01700c300c1ef044706696b6d6f7173b2b3b4b5b71b2302490202020202
02020202020203010201
''')


def _word(data, number):
    data.extend(number.to_bytes(2, 'little'))


def _stage_spec(chunks, packed):
    lengths = tuple(map(len, packed))
    return tuple(zip((0xC500, 0xE100 - lengths[1], STAGING, STAGING),
                     (0xA000, 0xC800, 0xC100, 0xA000),
                     lengths, map(len, chunks), strict=True))


def _backing(image):
    return b''.join(image[Packet.CHR + page * 1024:Packet.CHR + (page + 1) * 1024]
                    for page in Packet.PAGES)


def _install_packet(image, chunks, payload):
    assert len(payload) <= len(Packet.PAGES) * 1024
    cookie = Packet.cookie(chunks, payload)
    out = bytearray(image)
    out[Packet.COOKIE:Packet.COOKIE + len(cookie)] = cookie
    for i, page in enumerate(Packet.PAGES):
        at = Packet.CHR + page * 1024
        out[at:at + 1024] = payload[i * 1024:(i + 1) * 1024].ljust(1024, b'\xff')
    return bytes(out), cookie


def _loader(old, bundle, config):
    assert len(old) == 450
    boot, body = old[:BOOT_BYTES], old[BOOT_BYTES:]
    assert len(body) == 353 and WORKER_START + len(body) == 0xC261
    assert body[0x10:0x15] == bytes.fromhex('a010201ec1')
    cut = WORKER_START + 0x10
    rows_end = OLD_CONFIG + 24
    stage = 0xC11E
    vector = W.address(bundle, 'FarcallJmpTarget_SMC') + 1
    bank_call = W.address(bundle, 'FarCallCommon')

    # The first two decodes and the finalizer keep their existing entry ABI.
    # Stage the new stream between metadata and state. The state stream must
    # stay last because it overwrites the worker during its decode.
    prelude = bytearray((0xA0, 24, 0x20))
    _word(prelude, stage + 20)
    prelude.extend((0xA9, 0, 0x8D))
    _word(prelude, vector)
    prelude.extend((0xA9, 0xC0, 0x8D))
    _word(prelude, vector + 1)
    prelude.extend((0xA9, 1, 0x20))
    _word(prelude, bank_call)
    assert len(prelude) == 20

    def moved(address):
        return address + (20 if address >= cut else 0) + (8 if address >= rows_end else 0)

    original = bytearray(65536)
    original[WORKER_START:WORKER_START + len(body)] = body
    dis = Disassembler(MPU(memory=original))
    size = len(boot) + len(body) + len(prelude) + 8
    out = bytearray(size)
    out[:len(boot)] = boot
    out[BOOT_BYTES + cut - WORKER_START:BOOT_BYTES + moved(cut) - WORKER_START] = prelude

    pc = WORKER_START
    while pc < WORKER_CODE_END:
        width, instruction = dis.instruction_at(pc)
        assert instruction != '???'
        data = bytearray(original[pc:pc + width])
        if width == 3:
            operand = int.from_bytes(data[1:], 'little')
            if WORKER_START <= operand < WORKER_START + len(body):
                data[1:] = moved(operand).to_bytes(2, 'little')
        elif data[0] & 31 == 16:
            target = pc + 2 + int.from_bytes(data[1:], 'little', signed=True)
            data[1:] = (moved(target) - moved(pc) - 2).to_bytes(1, 'little', signed=True)
        cursor = BOOT_BYTES + moved(pc) - WORKER_START
        out[cursor:cursor + width] = data
        pc += width
    assert pc == WORKER_CODE_END

    cells = BOOT_BYTES + moved(WORKER_CODE_END) - WORKER_START
    table = BOOT_BYTES + moved(OLD_CONFIG) - WORKER_START
    variables = bytearray(original[WORKER_CODE_END:OLD_CONFIG])
    assert variables[-3:] == bytes.fromhex('01200c')
    first_stream = Packet.LOADER + size
    source_page, source_offset = divmod(first_stream, 1024)
    variables[-3] = source_page - (len(Packet.PAGES) - 15)
    variables[-2:] = (0x0C00 + source_offset).to_bytes(2, 'little')
    out[cells:table] = variables
    struct.pack_into('<16H', out, table, *(field for row in config for field in row))
    out[-30:] = body[-30:]
    assert first_stream == Packet.LOADER + 478 and WORKER_START + size - BOOT_BYTES <= WRAP
    return bytes(out)


def extract(image):
    """Authenticate and decode the four streams in their declared config order."""
    assert len(image) == 2097168
    data = _backing(image)
    first_stream = Packet.LOADER + 478
    head = data[:first_stream]
    assert head[Packet.LOADER + BOOT_BYTES + 0x10:Packet.LOADER + BOOT_BYTES + 0x15] == (
        bytes.fromhex('a0182032c1'))
    numbers = struct.unpack_from('<16H', head, first_stream - 62)
    rows = tuple(tuple(numbers[i:i + 4]) for i in range(0, 16, 4))
    assert tuple(row[0] for row in rows) == (0xC500, 0xE100 - rows[1][2], STAGING, STAGING)
    assert tuple(row[1] for row in rows) == (0xA000, 0xC800, 0xC100, 0xA000)
    position = first_stream
    chunks = [None] * 4
    for i in STREAM_ORDER:
        size, decoded = rows[i][2:]
        chunks[i] = Packet.decode(data[position:position + size], decoded)
        position += size
    assert data[position:] == b'\xff' * (len(data) - position)
    cookie = image[Packet.COOKIE:Packet.COOKIE + 16]
    assert Packet.cookie(chunks, data[:position]) == cookie
    return tuple(chunks), rows, cookie, position


@lru_cache(maxsize=2)
def compose(raw, planner=Lift.plan):
    assert H(raw) == PARENT
    blob, _, originals, packed, plan = planner(raw)
    chunks = originals + (blob,)
    head, _, _ = Packet.extract(raw)
    assert head[Packet.LOADER:] == PARENT_LOADER
    bundle = dict(W.Symbols.bundle(), raw=raw)
    config = _stage_spec(chunks, packed)
    assert config[0][2] <= (0xDC00 - 0xC500) + (0xC500 - WRAP)
    assert config[1][0] >= 0xC900 and all(STAGING + config[i][2] < 0xC800 for i in (2, 3))
    loader = _loader(head[Packet.LOADER:], bundle, config)
    payload = head[:Packet.LOADER] + loader + b''.join(packed[i] for i in STREAM_ORDER)
    image, cookie = _install_packet(raw, chunks, payload)
    assert extract(image) == (chunks, config, cookie, len(payload))

    overlay = dict(passed=True, parent_SHA256=PARENT, expected_memory_only_SHA256=H(image),
                   decoded=chunks, cookie=cookie.hex(),
                   lift=dict(id=37, left=1008, width=32, initial_top=192),
                   packed_bytes=tuple(map(len, packed)), support=plan,
                   boot_and_worker_bytes=len(loader),
                   spare_bytes=len(Packet.PAGES) * 1024 - len(payload), patches=[])
    for at, length in [(Packet.COOKIE, len(cookie))] + [
            (Packet.CHR + page * 1024, 1024) for page in Packet.PAGES]:
        old, new = raw[at:at + length], image[at:at + length]
        if old != new:
            overlay['patches'].append(dict(file_offset=at, old_hex=old.hex(), new_hex=new.hex()))
    assert inverse(image, overlay) == raw
    assert recover_parent(image) == raw
    return image, overlay


def inverse(image, overlay):
    assert H(image) == overlay['expected_memory_only_SHA256']
    raw = bytearray(image)
    for patch in overlay['patches']:
        at = patch['file_offset']
        old, new = bytes.fromhex(patch['old_hex']), bytes.fromhex(patch['new_hex'])
        assert len(old) == len(new) and raw[at:at + len(new)] == new
        raw[at:at + len(new)] = old
    assert H(raw) == overlay['parent_SHA256'] == PARENT
    return bytes(raw)


def recover_parent(image):
    """Restore the exact original packet from the new image alone."""
    (core, metadata, state, lift), _, _, _ = extract(image)
    action = lift[-31:]
    assert H(action) == Lift.ACTION_SHA
    core = bytearray(core)
    core[0x6F6:0x6F9] = bytes.fromhex('20d1d6')
    core[0x6FC:0x71B] = action
    core[0x13D1:0x13E1] = Lift.IMPORT_OLD
    chunks = bytes(core), metadata, state
    packed = tuple(map(Packet.encode, chunks))
    assert tuple(map(len, packed)) == (6467, 5995, 1263)
    payload = _backing(image)[:Packet.LOADER] + PARENT_LOADER + b''.join(packed)
    parent, _ = _install_packet(image, chunks, payload)
    assert H(parent) == PARENT
    return parent
