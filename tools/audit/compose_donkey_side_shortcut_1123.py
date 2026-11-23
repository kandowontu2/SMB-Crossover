"""Forward the native classic Donkey Kong side probe through its existing gate."""

from functools import lru_cache

import compose_prince_side_current_1123 as Parent


PARENT = Parent.CORRECTED
CANDIDATE = '84b3de865849ce01af78ee9a71b3fdc922d6f24acc39c22fe018b50801c914b6'
BANK, ENTRY, HOOK, END, TAIL = 89, 0xBC58, 0xBC68, 0xBC7E, 0xBC9F
OLD = bytes.fromhex('ad6a01288d6a01a9d98d6c01a9aa8d6d01a9fc4c5a01')
TAIL_OLD = b'\xea' * 10
SOURCE = '''
FarLo=$016c
FarHi=$016d
FarCall=$015a

.segment "ENTRY"
 cmp #28
 beq Donkey
 ; No branch above writes SafecallA. Leave the caller's value there.
 lda #$d9
 sta FarLo
 lda #$aa
 sta FarHi
 lda #$fc
Dispatch:
 plp
 jmp FarCall

.segment "TAIL"
Donkey:
 ; The PRG 33 side entry just selected BC58. The prefix in this bank
 ; leaves the high target byte BC unchanged until this dispatch.
 lda #$e6
 sta FarLo
 lda #$c1
 bne Dispatch
'''


@lru_cache(maxsize=1)
def edits():
    assemble = Parent.Layout.M.assemble
    program = assemble(SOURCE, dict(ENTRY=(HOOK, END-HOOK), TAIL=(TAIL, len(TAIL_OLD))))
    assert len(OLD) == END-HOOK and program['used'] == dict(ENTRY=20, TAIL=9)
    return tuple((BANK, pc, old, program['images'][part].ljust(len(old), b'\xea'))
                 for part, pc, old in (('ENTRY', HOOK, OLD), ('TAIL', TAIL, TAIL_OLD)))


def compose(raw):
    assert Parent.Epoch.H(raw) == PARENT
    at = Parent.Layout.off
    for bank, pc, hex_bytes in ((33, 0xBED8, '6828a9588d6c01a9bc8d6d01a9d94c5a01'),
                                (89, ENTRY, '08ad0260c913d004284c9cabc90ff016'),
                                (89, TAIL-3, '4c70bf'),
                                (65, 0xBCE6, '4cd8bf')):
        start = at(bank, pc)
        expected = bytes.fromhex(hex_bytes)
        assert raw[start:start+len(expected)] == expected, (bank, hex(pc))
    code = raw[at(BANK, 0xA000):at(BANK, 0xA000)+8192]
    assert b'\x20\x58\xbc' not in code and b'\x4c\x58\xbc' not in code
    candidate = Parent.Epoch.apply(raw, edits())
    assert Parent.Epoch.H(candidate) == CANDIDATE
    return candidate, CANDIDATE


def inverse(raw):
    assert Parent.Epoch.H(raw) == CANDIDATE
    parent = Parent.Epoch.apply(raw, ((bank, pc, new, old) for bank, pc, old, new in edits()))
    assert Parent.Epoch.H(parent) == PARENT
    return parent
