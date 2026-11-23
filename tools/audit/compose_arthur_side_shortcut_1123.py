"""Route Arthur to the existing authenticated terrain dispatcher."""

from hashlib import sha256

import compose_donkey_side_early_1123 as Prior
import compose_kirby_spiny_sound_1123 as Current


PIN = Current.CANDIDATE
BANK = 89
LAYOUT = {'GUARD': (0xBC68, 22), 'MAC_BRANCH': (0xBC93, 2), 'TAIL': (0xBC9F, 33)}
PREIMAGE = {
    'GUARD': 'c91cf033a9d98d6c01a9aa8d6d01a9fc284c5a01eaea',
    'MAC_BRANCH': 'f014',
    'TAIL': 'a9e68d6c01a9c1d0d0ea68284caebc8d6a01a9c78d6c01a9a78d6d01a9dd4c5a01',
}
SOURCE = '''
FarLo=$016c
FarHi=$016d
FarCall=$015a

.segment "GUARD"
 cmp #32
 beq Arthur
 lda #$d9
 sta FarLo
 lda #$aa
 sta FarHi
 lda #$fc
Dispatch:
 plp
 jmp FarCall
 nop
 nop

.segment "MAC_BRANCH"
 beq MacUnwind

.segment "TAIL"
Arthur:
 ; Enter the same owning dispatcher selected by NrSide. In particular,
 ; keep its cache-header check, rejection path and probe wrapper.
 lda #$e0
 sta FarLo
 lda #$b6
 sta FarHi
 lda #$cf
 bne Dispatch
MacUnwind:
 pla
 plp
 sta $016a
 lda #$c7
 sta FarLo
 lda #$a7
 sta FarHi
 jmp $bd6d
 nop
'''


def at(bank, pc):
    return 16 + bank * 8192 + (pc & 8191)


def compose(raw):
    assert sha256(raw).hexdigest() == PIN
    for bank, pc, signature in (
        (33, 0xBED8, '6828a9588d6c01a9bc8d6d01a9d94c5a01'),
        (33, 0xBEFD, '4ca4bf'),
        (33, 0xBFA4, 'c91cd0f128a9e68d6c01a9bc8d6d01d027'),
        (89, 0xBC58, '08ad0260c913d004284c9cabc90ff016'),
        (89, 0xBCAE, '8d6a01'),
        (89, 0xBD6D, 'a9dd4c5a01'),
        (79, 0xB6E0, '8d6a01089848a00e4c40b8'),
        (26, 0xBD3D, 'a9014c42bd48ad0260c920'),
    ):
        start = at(bank, pc)
        expected = bytes.fromhex(signature)
        assert raw[start:start + len(expected)] == expected, (bank, hex(pc))

    program = Prior.Layout.M.assemble(SOURCE, LAYOUT)
    assert program['used'] == {role: size for role, (_, size) in LAYOUT.items()}
    assert program['symbols']['MacUnwind'] == 0xBCAD
    edits = tuple((BANK, pc, bytes.fromhex(PREIMAGE[role]), program['images'][role])
                  for role, (pc, _) in LAYOUT.items())
    return Prior.Epoch.apply(raw, edits)
