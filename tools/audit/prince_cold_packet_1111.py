"""Read or reassemble Prince's three cold streams from a pinned MMC5 image."""

from hashlib import sha256
import json
from pathlib import Path
import struct

from measure_prince_lzdict_1102_v9 import encode


R = Path(__file__).resolve().parents[2]
PAGES = tuple(json.loads((R / 'docs/qa/allocations/prince-logical-support-1110-v8.json')
                         .read_bytes())['carrier_pages'])
CHR = 16 + 128 * 8192
COOKIE = 535471
LOADER = 31072 + 254
STREAMS = LOADER + 446
CONFIG = LOADER + 392
PREFIX = bytes((0xa7, 38, 2))


def decode(data, size):
    """Unpack the same little-endian tokens used by the on-cartridge decoder."""
    dictionary = data[:16]
    tokens = int.from_bytes(data[16:], 'little')
    left = 8 * (len(data) - 16)

    def take(count):
        nonlocal tokens, left
        assert 0 < count <= left
        value = tokens & ((1 << count) - 1)
        tokens >>= count
        left -= count
        return value

    output = bytearray()
    while len(output) < size:
        if take(1):
            low, high_length = take(8), take(8)
            distance = low + ((high_length & 0xf0) << 4)
            length = (high_length & 0x0f) + 3
            assert 0 < distance <= len(output) and len(output) + length <= size
            for _ in range(length):
                output.append(output[-distance])
        else:
            output.append(dictionary[take(4)] if take(1) else take(8))
    assert left < 8 and tokens == 0
    return bytes(output)


def cookie(chunks, payload):
    return PREFIX + sha256(b''.join(chunks) + payload).digest()[:13]


def _extract_layout(image, data, loader_bytes):
    streams = LOADER + loader_bytes
    config = streams - 54  # Twelve words, followed by the two15-byte page tables.
    fields = struct.unpack_from('<12H', data, config)
    inputs = fields[0::4]
    destinations = fields[1::4]
    lengths = fields[2::4]
    sizes = fields[3::4]
    assert inputs == (0xc500, 0xe100-lengths[1], 0xc300)
    assert destinations == (0xa000, 0xc800, 0xc100)
    assert PAGES[-15:] == tuple(lo+256*hi for lo, hi in zip(data[streams-30:streams-15], data[streams-15:streams]))
    end = streams + sum(lengths)
    assert data[end:] == b'\xff' * (len(data) - end)
    chunks = []
    cursor = streams
    for length, size in zip(lengths, sizes):
        chunks.append(decode(data[cursor:cursor+length], size))
        cursor += length
    assert cookie(chunks, data[:end]) == image[COOKIE:COOKIE+16]
    return data[:streams], tuple(chunks), lengths


def extract(image):
    assert len(image) == 2097168 and len(PAGES) == len(set(PAGES)) == 45
    data = b''.join(image[CHR+page*1024:CHR+(page+1)*1024] for page in PAGES)
    # Preserve the446B form exactly. The450B form adds the four-byte C280
    # staging-wrap low-byte store; both must authenticate the complete cookie.
    for loader_bytes in (446, 450):
        try:
            return _extract_layout(image, data, loader_bytes)
        except (AssertionError, struct.error):
            pass
    raise AssertionError('No authenticated446B/450B Prince cold packet')


def rebuild(image, mutate):
    head, before, lengths = extract(image)
    after = tuple(map(bytes, mutate(*map(bytearray, before))))
    assert len(after) == 3 and tuple(map(len, before)) == tuple(map(len, after))
    assert before != after
    packed = tuple(map(encode, after))
    sizes = tuple(map(len, packed))
    assert len(head) + sum(sizes) <= len(PAGES)*1024
    header = bytearray(head)
    assert len(header) in (LOADER + 446, LOADER + 450)
    struct.pack_into('<12H', header, len(header)-54, 0xc500,0xa000,sizes[0],len(after[0]),
                     0xe100-sizes[1],0xc800,sizes[1],len(after[1]),
                     0xc300,0xc100,sizes[2],len(after[2]))
    payload = bytes(header) + b''.join(packed)
    new = bytearray(image)
    new[COOKIE:COOKIE+16] = cookie(after, payload)
    for i, page in enumerate(PAGES):
        new[CHR+page*1024:CHR+(page+1)*1024] = payload[i*1024:(i+1)*1024].ljust(1024,b'\xff')
    new = bytes(new)
    assert extract(new) == (bytes(header), after, sizes)
    return new, dict(cookie=new[COOKIE:COOKIE+16].hex(), packed_bytes=sizes,
                     old_packed_bytes=lengths, spare=len(PAGES)*1024-len(payload))
