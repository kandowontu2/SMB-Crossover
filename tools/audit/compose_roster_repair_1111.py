"""Compose the independently qualified Mini, Giant and Prince repairs."""

from hashlib import sha256

import bisect_giant_cold_start_1111 as Giant
import check_mini_menu_palette_1111 as Mini
import compose_prince_question_ledge_1111 as Prince
import deliver_steve_move_1111 as Parent


def digest(data):
    return sha256(data).hexdigest()


def proposal(raw):
    assert digest(raw) == Parent.PIN
    prince, layout = Prince.proposal(raw)
    updates = (('prince', prince), ('giant', Giant.proposal(raw)), ('mini', Mini.proposal(raw)))
    assert digest(prince) == '99eeae726f5cb7b5af35c4e59421ea110cd3365336e76e65114b49c75c11018e'
    assert digest(updates[2][1]) == '98131f7d3c4a2c953693a3a467be3491b4f855af142ec9b0fe462f8a161dee7b'
    image = bytearray(raw)
    touched = set()
    counts = {}
    for name, revision in updates:
        changes = {index: after for index, (before, after) in enumerate(zip(raw, revision, strict=True))
                   if before != after}
        assert changes and not touched.intersection(changes), name
        for index, value in changes.items():
            image[index] = value
        touched.update(changes)
        counts[name] = len(changes)
    return bytes(image), dict(layout, changed_bytes=counts)


def recover_parent(image):
    # Each component retains its own exact preimages, independently of the other two.
    raw = bytearray(image)
    for pc, hexbytes in Mini.PREIMAGE.values():
        offset = 16 + Mini.BANK * 8192 + (pc - 0xa000)
        original = bytes.fromhex(hexbytes)
        raw[offset:offset+len(original)] = original
    for offset, _, replacement in Mini.spans(raw):
        assert image[offset:offset+len(replacement)] == replacement
    at = Giant.offset(84, 0xbef8)
    assert raw[at:at+8] == Giant.COMPACT
    raw[at:at+8] = Giant.LEGACY
    restored, _ = Prince.replace(bytes(raw), Prince.source_workers()[0], inverse=True)
    assert digest(restored) == Parent.PIN
    assert proposal(restored)[0] == image
    return restored
