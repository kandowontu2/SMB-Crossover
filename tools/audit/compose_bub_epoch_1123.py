"""Test Bub and Bob's repeated cache checks against the November 23 nightly."""

import compose_bub_native_palette_current_1115 as Bub
import compose_prince_epoch_current_1123 as Shared


H = Shared.H
PARENT = 'cb6fcb50dc9db8dda53eb542078c92226d8fd2942a275bf02497e4efd1e41de7'
CANDIDATE = 'e5cb1367ecfa022b610b2705a91280ac47b2aec943c6eb84cf036f50f2879c88'
HEADER = bytes.fromhex('a7270204f17b913651e715c871ed8765')
STAMP = 0xC3FF
STAMP_CODE = 0xB470
CHR = Bub.A.CH


def assemble(source, address, **symbols):
    return Shared.Reach.L.assemble(source, symbols, address)[0]


def static_edits(raw):
    off = Shared.Shared.S.off
    selector = assemble('''
 cpx #0
 beq FullCheck
 cpx #5
 beq FullCheck
 sty $016c
 jmp CheckEpoch
''', 0xA76B, FullCheck=0xA779, CheckEpoch=0xA738)

    _, old_reader, old_scope = Shared.readers(raw)
    reader = assemble('''
 cpx #38
 beq Foreground
 cpx #39
 beq Foreground
 cpx #41
 lda $c8ff
 bcc EpochLoaded
 lda $c3f0
 jmp EpochLoaded
''', 0xB08F, EpochLoaded=0xB075, Foreground=0xB0BF)

    # Keep the existing foreground checks and Prince behavior. Bub and Bob
    # use their own cache byte, written by the fully checked movement entry.
    old_tail = bytes.fromhex('adaac0f097ada9c04c75b0')
    assert old_scope.endswith(old_tail)
    new_tail = assemble('''
 cpx #39
 beq BubEpoch
 lda $c0aa
 beq BadEpoch
 lda $c0a9
 jmp EpochLoaded
BubEpoch:
 lda Stamp
 jmp EpochLoaded
''', 0xB0E3, BadEpoch=0xB07F, EpochLoaded=0xB075, Stamp=STAMP)
    scope = old_scope[:-len(old_tail)] + new_tail
    assert len(reader) <= 0xB0B0 - 0xB08F
    assert len(scope) <= 0xB0FE - 0xB0BF
    mirror = Shared.MIRROR * 22

    movement = assemble('''
 php
 pha
 lda $0e
 sta Stamp
 pla
 plp
 jmp $be61
''', STAMP_CODE, Stamp=STAMP)
    redirect = assemble('jmp StampCode', 0xA000, StampCode=STAMP_CODE)

    return (
        (off(65, 0xA76B), bytes.fromhex('e0048a69004a90068c6c01b0c0ea'), selector),
        (off(85, 0xB08F), old_reader + mirror[len(old_reader):len(reader)], reader),
        (off(85, 0xB0BF), old_scope + mirror[len(old_scope):len(scope)], scope),
        (CHR + 301 * 1024, bytes.fromhex('4c61be'), redirect),
        (CHR + 440 * 1024 + 0x70, b'\xff' * len(movement), movement),
    )


def apply(raw, edits):
    out = bytearray(raw)
    for offset, old, new in edits:
        assert len(old) == len(new) and out[offset:offset + len(old)] == old, hex(offset)
        out[offset:offset + len(old)] = new
    return bytes(out)


def compose(raw):
    assert H(raw) == PARENT and Bub.cookie(raw) == HEADER and raw.count(HEADER) == 1
    out = apply(raw, static_edits(raw))
    candidate = apply(out, [(Bub.COOKIE, HEADER, Bub.cookie(out))])
    assert H(candidate) == CANDIDATE
    return candidate


def inverse(raw):
    assert H(raw) == CANDIDATE
    original = apply(raw, [(Bub.COOKIE, Bub.cookie(raw), HEADER)])
    original = apply(original, [(offset, new, old) for offset, old, new in static_edits(original)])
    assert H(original) == PARENT
    return original
