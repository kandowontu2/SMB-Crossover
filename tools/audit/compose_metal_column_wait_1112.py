"""Make the original Metal column handoff synchronous on the SMB host."""
from hashlib import sha256

import compose_metal_pickup_maturity_1112 as Maturity

Head = Maturity.Head
SOURCE = Head.R / 'tools/reference/metal_column_wait_1112.s'
MATURITY_COOKIE = bytes.fromhex('a7232d995a879e8aa0286241ee56f524')


def transform(raw, reverse=False):
    data, labels = Head.Flower.inputs()
    pc = labels['Ms_BA86']
    assert pc == 0xb0a3 and labels['Ms_BA8A'] == pc + 5
    original = data['native-actor.bin'][pc - 0xa000:pc - 0xa000 + 5]
    assert original == bytes.fromhex('adedc0f0fb')
    chunks, _ = Head.assemble_segments(SOURCE.read_text(), dict(ACKNOWLEDGED=pc), {})
    code = chunks['ACKNOWLEDGED']
    assert code == bytes.fromhex('a901eaeaea')
    at = 16 + 1048576 + 827 * 1024 + (pc & 1023)
    cookie = bytes((0xa7, 35, 46)) + sha256(
        b'Metal host column acknowledgment 1112\x00' + MATURITY_COOKIE + code).digest()[:13]
    changes = [(at, original, code, 'donor PPU acknowledgment wait')]
    for role, bank, offset in Head.Flower.RESIDENT:
        image = data[f'native-{role}.bin'].replace(data['native-cookie.bin'], MATURITY_COOKIE)
        assert image.count(MATURITY_COOKIE) == 1
        changes.append((16 + bank * 8192 + offset, image,
                        image.replace(MATURITY_COOKIE, cookie), role + ' full cookie'))
    result = bytearray(raw)
    for at, old, new, role in changes:
        if reverse:
            old, new = new, old
        assert raw[at:at + len(old)] == old, role
        result[at:at + len(new)] = new
    maturity = bytes(result) if reverse else raw
    Maturity.transform(maturity, True)
    return bytes(result), dict(parent_SHA256=sha256(raw).hexdigest(),
        candidate_SHA256=sha256(result).hexdigest(), cookie=cookie.hex(),
        changed_bytes=sum(a != b for a, b in zip(raw, result)),
        wait_PC=hex(pc), original=original.hex(), replacement=code.hex(), reverse=reverse,
        patches=[dict(offset=at, size=len(old), role=role) for at, old, _, role in changes],
        source_SHA256=sha256(SOURCE.read_bytes()).hexdigest())


def compose(raw):
    maturity, _ = Maturity.compose(raw)
    return transform(maturity)
