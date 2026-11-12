"""Bind the original Laserbot sprites to the crossover's active Steve CHR pages."""

from hashlib import sha256
import json

import check_steve_shatterhand_companion_live_1111 as Live


DONOR_PAGE = 90
HOST_PAGES = (710, 711)
CELLS = {0x41: 0x39, 0x43: 0x3b, 0x45: 0x3d, 0x47: 0x3f,
         0x57: 0x41, 0x59: 0x7b, 0x5b: 0x7d, 0x5d: 0x7f}
PLACEHOLDER = bytes.fromhex('084102000041020008')


def flipped(tile):
    def plane(data):
        return bytes(int(f'{byte:08b}'[::-1], 2) for byte in reversed(data))

    return b''.join(plane(tile[i:i+8]) for i in (16, 24, 0, 8))


def edits(raw, donor):
    assert sha256(donor).hexdigest() == Live.DONOR.PIN
    donor_chr = Live.DONOR.ShatterhandBus(donor).chr

    def original(tile):
        at = DONOR_PAGE * 1024 + (tile & 0x3e) * 16
        return donor_chr[at:at+32]

    assert original(0x5f) == flipped(original(0x5d))
    lo = Live.C.offset(97, 0xc04e)
    hi = Live.C.offset(97, 0xc05c)
    ptr = raw[lo] + 256 * raw[hi]
    assert ptr == 0xc1ec
    record = Live.C.offset(97, ptr)
    assert raw[record:record+len(PLACEHOLDER)] == PLACEHOLDER
    changes = [(record, PLACEHOLDER[:1], b'\0')]
    for donor_tile, host_tile in CELLS.items():
        page = HOST_PAGES[(host_tile >> 6) & 1]
        at = Live.C.CHR + 1024 * page + (host_tile & 0x3e) * 16
        cell = original(donor_tile)
        assert len(cell) == 32 and any(cell)
        assert raw[at:at+32] == bytes(32), (page, host_tile)
        changes.append((at, bytes(32), cell))
    return tuple(changes)


def apply(raw, changes):
    image = bytearray(raw)
    for at, old, new in changes:
        assert len(old) == len(new) and image[at:at+len(old)] == old
        image[at:at+len(new)] = new
    return bytes(image)


def main():
    raw, info = Live.on_nightly(Live.Ingress.S.Donor.HOST.read_bytes())
    changes = edits(raw, Live.DONOR.DONOR.read_bytes())
    image = apply(raw, changes)
    assert apply(image, ((at, new, old) for at, old, new in changes)) == raw
    foreign = Live.Draw.foreign_item_sprites(raw, image)
    _, control = Live.natural(raw, info)
    _, patched = Live.natural(image, info)
    assert control == patched
    print(json.dumps(dict(passed=True, parent=Live.C.digest(raw), candidate=Live.C.digest(image),
                          exact_art_bytes=len(CELLS)*32, native_pickup_checks=foreign,
                          first_companion_shot_updates=patched['uninterrupted_shot_updates'],
                          output_files=0)), flush=True)


if __name__ == '__main__':
    main()
