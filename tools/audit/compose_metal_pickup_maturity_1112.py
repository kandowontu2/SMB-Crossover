"""Admit Metal native item overlap through its authenticated existing row23."""
from hashlib import sha256
import compose_metal_head_bridge_1112 as Head

R = Head.R
SOURCE = R / 'tools/reference/metal_pickup_maturity_1112.s'
HEAD_COOKIE = bytes.fromhex('a7232cd3586ce9901f54be4a259914ac')
ACTOR_TAIL = 0xbfb2
ORIGINAL_TAIL = bytes.fromhex('0868a8688da17d8d165198482860')


def transform(raw, reverse=False):
    data, labels = Head.Flower.inputs()
    row_pc = labels['Ms12CacheRows'] + 23 * 3
    assert data['native-actor.bin'][ACTOR_TAIL - 0xa000:0x1fc0] == ORIGINAL_TAIL
    chunks, symbols = Head.assemble_segments(SOURCE.read_text(),
        dict(MATURE=row_pc, BRIDGE_TAIL=ACTOR_TAIL),
        dict(CurrentBankC=labels['Ms11Host_CurrentBankC'], Enemy_State=0x1f))
    code = chunks['MATURE']
    mature_pc = symbols['MsMetalMaturity']
    tail = chunks['BRIDGE_TAIL'].ljust(len(ORIGINAL_TAIL), b'\xea')
    before = b'\x4c' + labels['Ms12Reject'].to_bytes(2, 'little')
    assert code == b'\x4c' + mature_pc.to_bytes(2, 'little')
    assert tail == bytes.fromhex('688da17d8d165160b51f0a60eaea')
    pages = (831, 500, 494)
    renderer = bytearray().join(raw[16 + 1048576 + page * 1024:16 + 1048576 + (page + 1) * 1024] for page in pages)
    row = row_pc - 0xcd00
    renderer[row:row + 3] = code
    cookie = bytes((0xa7, 35, 45)) + sha256(
        b'Metal real native pickup maturity 1112\x00' + HEAD_COOKIE + renderer + tail).digest()[:13]
    at = 16 + 1048576 + pages[row // 1024] * 1024 + row % 1024
    actor_at = 16 + 1048576 + 830 * 1024 + (ACTOR_TAIL & 1023)
    changes = [(at, before, code, 'existing authenticated maturity vector'),
               (actor_at, ORIGINAL_TAIL, tail, 'actor bridge carry-only tail and maturity worker')]
    for role, bank, offset in Head.Flower.RESIDENT:
        image = data[f'native-{role}.bin'].replace(data['native-cookie.bin'], HEAD_COOKIE)
        assert image.count(HEAD_COOKIE) == 1
        changes.append((16 + bank * 8192 + offset, image, image.replace(HEAD_COOKIE, cookie), role + ' full cookie'))
    result = bytearray(raw)
    for at, old, new, role in changes:
        if reverse: old, new = new, old
        assert raw[at:at + len(old)] == old, role
        result[at:at + len(new)] = new
    # Full head preimages authenticate every unchanged component, not just
    # this vector or a revision prefix. Unrelated source changes stay intact.
    head = bytes(result) if reverse else raw
    Head.transform(head, True)
    return bytes(result), dict(parent_SHA256=sha256(raw).hexdigest(),
        candidate_SHA256=sha256(result).hexdigest(), cookie=cookie.hex(),
        row_PC=hex(row_pc), maturity_PC=hex(mature_pc),
        changed_bytes=sum(a != b for a, b in zip(raw, result)), reverse=reverse,
        patches=[dict(offset=at, size=len(old), role=role) for at, old, _, role in changes],
        source_SHA256=sha256(SOURCE.read_bytes()).hexdigest())


def compose(raw):
    head, _ = Head.compose(raw)
    return transform(head)
