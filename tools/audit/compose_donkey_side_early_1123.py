"""Route classic Donkey Kong from the collision bank to the existing side guard."""

from functools import cache

import compose_donkey_side_shortcut_1123 as Old


PARENT = Old.CANDIDATE
CANDIDATE = 'ae28a3ece9725c3b35975e90f19e56287f15e243bf5cc7e980dd527321f85243'
Layout = Old.Parent.Layout
Epoch = Old.Parent.Epoch
BANK, HOOK, START, END = 33, 0xBEFD, 0xBFA4, 0xBFB5
JUNIOR_BRANCH = 0xBFFA
SOURCE = '''
FarLo=$016c
FarHi=$016d
OtherOwner=$bf99
Dispatch=$bfdc

.segment "HOOK"
 jmp ClassicSide

.segment "TAIL"
ClassicSide:
 cmp #28
 bne OtherOwner
 plp
 lda #$e6
 sta FarLo
 lda #$bc
 sta FarHi
 bne Dispatch
'''


@cache
def edits():
    old_hook = bytes.fromhex('4c99bf')
    old_tail = bytes.fromhex('4cb5bfb68d6c01a9b08d6d01a9c14c5a01')
    p = Layout.M.assemble(SOURCE, dict(HOOK=(HOOK, len(old_hook)), TAIL=(START, END - START)))
    assert p['used'] == dict(HOOK=3, TAIL=17)
    # The one native Jr. branch goes directly to the PC its old JMP selected.
    return ((BANK, HOOK, old_hook, p['images']['HOOK']),
            (BANK, START, old_tail, p['images']['TAIL']),
            (BANK, JUNIOR_BRANCH, bytes.fromhex('f0a8'), bytes.fromhex('f0b9')))


def compose(raw):
    assert Epoch.H(raw) == PARENT
    for bank, pc, signature in ((33, 0xBEA2, '08a9b08d6c01a9bf8d6d01ad0260d04b'),
                                (33, 0xBFDC, 'a9c14c5a01'), (33, 0xBFF8, 'c928f0a8'),
                                (65, 0xBCE6, '4cd8bf')):
        at = Layout.off(bank, pc)
        expected = bytes.fromhex(signature)
        assert raw[at:at + len(expected)] == expected
    code = raw[Layout.off(BANK, 0xA000):Layout.off(BANK, 0xA000) + 8192]
    assert b'\x20\xa4\xbf' not in code and b'\x4c\xa4\xbf' not in code
    candidate = Epoch.apply(raw, edits())
    assert Epoch.H(candidate) == CANDIDATE
    return candidate


def inverse(raw):
    assert Epoch.H(raw) == CANDIDATE
    parent = Epoch.apply(raw, ((bank, pc, after, before) for bank, pc, before, after in edits()))
    assert Epoch.H(parent) == PARENT
    return parent
