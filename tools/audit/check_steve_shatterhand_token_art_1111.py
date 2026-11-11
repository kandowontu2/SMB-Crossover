"""Read the original Shatterhand Alpha/Beta glyphs through its live HUD."""

from hashlib import sha256
import json

import trace_steve_shatterhand_donor_1111 as Donor


HUD_Y = 16
HUD_X = (96, 120, 144)
PAIRS = ((0x21, 0x21), (0x23, 0x25), (0x27, 0x29))
ART_PAGE, ART_OFFSET = 64, 544
ART_PINS = ('470dffb4558db5a4cfefa2dc9b32f74ad940cbf9a82b2cc2fd5bec3502010a61',
            '727bfc020a687b516b887b3d9b70ce5b9d95cd4a4439e3cfa658d89a859850b5')


def original_art(raw):
    assert sha256(raw).hexdigest() == Donor.PIN
    start = 16 + 0x20000 + ART_PAGE * 1024 + ART_OFFSET
    art = {symbol: raw[start+(symbol-1)*64:start+symbol*64] for symbol in (1, 2)}
    assert tuple(sha256(data).hexdigest() for data in art.values()) == ART_PINS
    return art


def glyphs(seed):
    art = {}
    for pattern in (0x15, 0x2a, 0x19, 0x26):
        cpu = Donor.fork(seed)
        bus = cpu.memory
        # The actual renderer owns the presentation. Direct only its already
        # committed symbols, and suppress the combination countdown.
        bus[0x05c4] = pattern & 0x0f
        for _ in range(4):
            Donor.frame(cpu, 0)
        assert bus.ppu_ctrl & 0x20
        rows = [tuple(bus.oam[i:i+4]) for i in range(0, 256, 4)]
        for index, x in enumerate(HUD_X):
            symbol = bus[0x05c4] >> (2*index) & 3
            expected = PAIRS[symbol]
            cells = [(tile, attr) for at in (x, x+8) for y, tile, attr, left in rows
                     if y == HUD_Y and left == at]
            assert tuple(tile for tile, _ in cells) == expected, (pattern, index, cells)
            if symbol == 0:
                continue
            assert [attr for _, attr in cells] == [1, 1], cells
            data = bytearray()
            for tile, _ in cells:
                address = ((tile & 1) << 12) | ((tile & 0xfe) << 4)
                data.extend(bus.ppu_read(address + byte) for byte in range(32))
            assert any(data)
            assert art.setdefault(symbol, bytes(data)) == data, (symbol, index)
    assert set(art) == {1, 2} and art[1] != art[2]
    return art


def main():
    raw = Donor.DONOR.read_bytes()
    assert sha256(raw).hexdigest() == Donor.PIN
    seed = Donor.boot(raw)
    art = glyphs(seed)
    assert art == original_art(raw)
    print(json.dumps(dict(passed=True, donor=Donor.PIN, sprites_per_symbol=2, sprite_height=16,
                          glyphs={symbol: {'sha256': sha256(data).hexdigest(), 'bytes': data.hex()}
                                  for symbol, data in art.items()}, output_files=0)), flush=True)


if __name__ == '__main__':
    main()
