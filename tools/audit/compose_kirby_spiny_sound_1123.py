"""Keep the needle launch cue when some projectile slots are occupied."""

from hashlib import sha256

import compose_donkey_side_early_1123 as Nightly


PARENT = Nightly.CANDIDATE
CANDIDATE = '2f1e4b8dd1edd4b6d8d1097c600a4123253c10f34b2d01ee76f6d1bce129ab15'
BANK, PC = 74, 0xA482
OFFSET = 16 + BANK * 8192 + (PC & 8191)
SPAWN_AND_AIM = bytes.fromhex('a0008c775ca9032093a490f3a90b9d675cac775cb98da49d4f5cb990a49d555c')
BEFORE = bytes.fromhex('c8c00390dda9208d050160')
# Run the same cue stores inside the loop after Spawn succeeds. The short
# branch still returns to A464. A failed first Spawn still skips the cue.
AFTER = bytes.fromhex('a9208d0501c8c00390d860')


def compose(raw):
    assert sha256(raw).hexdigest() == PARENT
    assert raw[OFFSET - len(SPAWN_AND_AIM):OFFSET] == SPAWN_AND_AIM
    assert raw[OFFSET:OFFSET + len(BEFORE)] == BEFORE
    candidate = raw[:OFFSET] + AFTER + raw[OFFSET + len(BEFORE):]
    assert sha256(candidate).hexdigest() == CANDIDATE
    return candidate


def inverse(raw):
    assert sha256(raw).hexdigest() == CANDIDATE
    assert raw[OFFSET:OFFSET + len(AFTER)] == AFTER
    parent = raw[:OFFSET] + BEFORE + raw[OFFSET + len(AFTER):]
    assert sha256(parent).hexdigest() == PARENT
    return parent
