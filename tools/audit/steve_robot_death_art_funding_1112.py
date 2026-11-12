"""Fund two robot explosion cells by aliasing identical native item cells."""
import json
from hashlib import sha256
import check_steve_shatterhand_robot_death_1112 as Death


def edits(raw, donor):
    assert sha256(donor).hexdigest() == Death.D.PIN
    chr_start = 16+1048576

    def prg(bank, pc):
        return 16+bank*8192+(pc & 8191)

    # Shared JnDraw publishes both pages before the item readers execute.
    for pc, expected in (
            (0xa924, 'a9c6a2028d6a01a9898d6c01a9a28d6d01a9be205a01'),
            (0xa93a, 'a9c7a202a0058d6a01a9758d6c01a9a28d6d01a9be205a01'),
            (0xa9fb, 'b94ec0'), (0xaa00, 'b95cc0')):
        expected = bytes.fromhex(expected)
        at = prg(98, pc)
        assert raw[at:at+len(expected)] == expected, hex(pc)
    record = bytes.fromhex('085f02000061020008')
    at = prg(97, 0xc210)
    assert raw[at:at+9] == record
    for item in (9, 13):
        pointer = raw[prg(97, 0xc04e)+item] + 256*raw[prg(97, 0xc05c)+item]
        assert pointer == 0xc210
    readers = set()
    records = 0
    for start, end in ((0xc000, 0xc032), (0xc10e, 0xc307)):
        pc = start
        while pc < end:
            size = raw[prg(97, pc)]
            if pc == 0xc1ec:
                assert size == 0  # Disabled Laser item retains its payload.
                size = 8
            assert size % 4 == 0 and pc+size+1 <= end, hex(pc)
            for offset in range(1, size+1, 4):
                if raw[prg(97, pc+offset)] in (0x5f, 0x61):
                    readers.add(pc)
            records += 1
            pc += size+1
        assert pc == end
    assert records == 71 and readers == {0xc210}, (records, readers)
    for old, alias in ((0x1e0, 0x280), (0x200, 0x2a0)):
        assert raw[chr_start+711*1024+old:chr_start+711*1024+old+32] == raw[chr_start+710*1024+alias:chr_start+710*1024+alias+32]
    cells = b''.join(Death.Art.original_cell(donor, 87, tile) for tile in (0x51, 0x53))
    art_at = chr_start+711*1024+0x1e0
    return ((at+1, b'\x5f', b'\x29'), (at+5, b'\x61', b'\x2b'),
            (art_at, raw[art_at:art_at+64], cells))


def main():
    raw, donor = Death.D.HOST.read_bytes(), Death.D.DONOR.read_bytes()
    patched = bytearray(raw)
    changes = edits(raw, donor)
    for at, old, new in changes:
        assert patched[at:at+len(old)] == old and len(old) == len(new)
        patched[at:at+len(new)] = new
    chr_start = 16+1048576

    def pixels(image, tile):
        page = 710 if tile < 0x40 else 711
        at = chr_start+page*1024+(tile & 0x3e)*16
        return image[at:at+32]

    for old, new in ((0x5f, 0x29), (0x61, 0x2b)):
        assert pixels(raw, old) == pixels(patched, new)
    for tile, host in ((0x51, 0x5f), (0x53, 0x61)):
        assert pixels(patched, host) == Death.Art.original_cell(donor, 87, tile)
    print(json.dumps(dict(item_pixel_aliases=2, original_explosion_cells=2,
                          edits=[dict(offset=hex(at), bytes=len(old)) for at, old, _ in changes],
                          mounted=False, output_files=0)))


if __name__ == '__main__':
    main()
