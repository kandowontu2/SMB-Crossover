"""Compose the private DK Jr. rectangle, scene and sprite-list changes in memory."""

from functools import lru_cache
from hashlib import sha256

import compose_dkjr_rect_read_current_1123 as Rect
import compose_kirby_spiny_sound_1123 as Current


Head = Rect.Head
PIN = Current.CANDIDATE
SOURCE = Head.R / 'tools/reference/dkjr_scene_hot_1123.s'
LAYOUT = {
    'COLUMNS': (0xABC6, 0x20),
    'ROWS': (0xABE6, 0x5C),
    'DRAW_DISPATCH': (0xBEC4, 0x13),
    'DRAW_TILES': (0xBF50, 7),
}
PREIMAGE = {
    'COLUMNS': 'ad02c0ae08c0a0012068ad186901c8482065a8293f2068ad68c8c8c8cad0e960',
    'ROWS': 'a000ae06c0ad01c08d09c0ad09c00848ad04c08d0bacad05c0c908b00209c08d0cac682899ffff1869088d09c0c8c8c8ad00c00848ad04c08d30acad05c0c908b00209c08d31ac682899ffffc8cad0bb1869088d00c0ce07c0d0a760',
    'DRAW_DISPATCH': 'a007b950bfcdecc8f0058810f53020980a0970',
    'DRAW_TILES': 'f1f25ef3f4f5f6',
}


@lru_cache(maxsize=1)
def program(raw):
    assert sha256(raw).hexdigest() == PIN
    old_rect, new_rect, _ = Rect.program(raw, PIN)
    code = Head.assemble('SkipTile=$bef3\n' + SOURCE.read_text(), LAYOUT)
    assert code['symbols']['ColumnEmit'] == 0xABC6
    assert code['symbols']['RowEmit'] == 0xABE6
    assert all(code['used'][role] == size for role, (_, size) in LAYOUT.items() if role != 'ROWS')

    packet = Head.payload(raw)
    # Both entry points are reached after the common caller sets the virtual
    # destination page to 2. Even an indexed page crossing cannot reach the
    # pointer fields at C004/C005 or the scratch fields at C000..C009.
    for address, signature in (
        (0xAB38, 'a9028d05c0'),
        (0xAB68, '20c6ab'),
        (0xAB88, '20e6ab'),
        (0xA87B, 'b9ffff60'),
        (0xAD7E, '99ffff60'),
        (0xBED7, '8decc8'),
    ):
        data = bytes.fromhex(signature)
        offset = Head.offset(address)
        assert packet[offset:offset + len(data)] == data
    patches = [(Head.RECT_START, old_rect['images']['RECT'], new_rect['images']['RECT'])]
    for role, (address, size) in LAYOUT.items():
        old = bytes.fromhex(PREIMAGE[role])
        new = code['images'][role].ljust(size, b'\xea')
        assert len(old) == len(new) == size
        patches.append((address, old, new))
    for address, old, new in patches:
        offset = Head.offset(address)
        assert packet[offset:offset + len(old)] == old
    return patches, old_rect, new_rect


def compose(raw):
    patches, _, _ = program(raw)
    result = bytearray(raw)
    for address, old, new in patches:
        for at, data in Rect.chunks(address, new):
            result[at:at + len(data)] = data
    at = Head.Base.COOKIE_AT
    prefix = b'\xa7\x28\x01'
    assert raw[at:at + 16] == prefix + sha256(Head.payload(raw)).digest()[:13]
    result[at:at + 16] = prefix + sha256(Head.payload(result)).digest()[:13]
    return bytes(result)
