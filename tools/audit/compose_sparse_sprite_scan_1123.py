"""Try the shared empty object-draw shortcut on the exact MMC5 nightly."""

from functools import lru_cache

import compose_prince_side_current_1123 as Parent


HOOK, POSITIVE, NEGATIVE, DONE = 0xA155, 0xA170, 0xA19C, 0xA1C6
ALT_HOOK, ALT_POSITIVE, ALT_NEGATIVE = 0xA038, 0xA053, 0xA074
SCAN, SCAN_SIZE = 0xAFC0, 54
ADVANCE, ADVANCE_SIZE = 0xAFFC, 58
WORK_BANK = 125
OLD_HOOK = bytes.fromhex('a917850bad e006186913c9189002e9188de006a50e4aade006902c')
OAM_CLEAR, LEGACY_CLEAR = 0xA32C, 0xA24B
OAM_BEFORE = b''.join(bytes((0x8D, 4*i, 2)) for i in range(64)) + b'\x60'
LEGACY_BEFORE = bytes.fromhex('684a850b4a650b692c850ba9a3850c4cb285')

SOURCE = '''
Sprites=$06e1
Shuffle=$06e0
LoopCount=$0b
Frame=$0e
EnemyID=$17
FirebarSlot=$7eb4
FarLo=$016c
FarHi=$016d
FarCall=$015a
Negative=$a19c
DrawLater=$a1c6

.segment "HOOK"
 lda #<ScanEmpty
 sta FarLo
 lda #>ScanEmpty
 sta FarHi
 lda #$fd
 jsr FarCall
 bpl Original
 and #$7f
 dec LoopCount
 jmp DrawLater
Original:
 bcc Negative

.segment "SCAN"
ScanEmpty:
 ; A bare ID can admit a world draw even if a flag was just cleared.
 lda EnemyID
 ora EnemyID+1
 ora EnemyID+2
 ora EnemyID+3
 ora EnemyID+4
 ora EnemyID+5
 bne UseOriginal
 txa
 pha
 ldx #8
 lda #0
Check:
 ; Include the last bubble slot conservatively. Slot zero is the player.
 ora Sprites,x
 ora Sprites+8,x
 ora Sprites+16,x
 dex
 bne Check
 tax
 pla
 cpx #0
 beq Empty
 tax
UseOriginal:
 lda #23
 sta LoopCount
 jmp Normalize
Empty:
 jmp EmptyDraw
MarkEmpty:
 ora #$80
 rts

.segment "ADVANCE"
Normalize:
 lda Shuffle
 clc
 adc #19
 cmp #24
 bcc StoreShuffle
 sbc #24
StoreShuffle:
 sta Shuffle
 pha
 lda Frame
 lsr
 pla
 rts
EmptyDraw:
 jsr Normalize
 ldx #$ff
 stx FirebarSlot
 inx
 stx LoopCount
 tay
 bne Nonzero
 ; The original list visited slot zero last and leaves the previous Y.
 ldy #13
 bcc LastWorld
 ldy #11
LastWorld:
 dex
 clc
 bcc MarkEmpty
Nonzero:
 bcc SetCarry
 ; Forward traversal ends with carry set when the final index wrapped.
 eor #$ff
 cmp #$f3
 eor #$7f
 rts
SetCarry:
 sec
 bcs MarkEmpty
'''


@lru_cache(maxsize=1)
def program():
    assert len(OLD_HOOK) == POSITIVE - HOOK
    out = Parent.Layout.M.assemble(SOURCE, dict(HOOK=(HOOK, len(OLD_HOOK)),
                                              SCAN=(SCAN, SCAN_SIZE), ADVANCE=(ADVANCE, ADVANCE_SIZE)))
    assert out['symbols']['ScanEmpty'] == SCAN
    return out


def compose_benchmark(raw):
    """Timing experiment only. The bank 125 fixed/audio mirror must ship intact."""
    assert Parent.Epoch.H(raw) == Parent.CORRECTED
    images = program()['images']
    edits = ((4, HOOK, OLD_HOOK, images['HOOK'].ljust(len(OLD_HOOK), b'\xea')),
             (WORK_BANK, SCAN, bytes(len(images['SCAN'])), images['SCAN']),
             (WORK_BANK, ADVANCE, bytes(len(images['ADVANCE'])), images['ADVANCE']))
    return Parent.Epoch.apply(raw, edits)


RESIDENT = '''
Sprites=$06e1
Shuffle=$06e0
LoopCount=$0b
Frame=$0e
EnemyID=$17
FirebarSlot=$7eb4
Negative=$a19c
DrawLater=$a1c6

.segment "HOOK"
 jsr ScanEmpty
 bpl Original
 and #$7f
 dec LoopCount
 jmp DrawLater
Original:
 bcc Negative

.segment "ALTERNATE"
 jsr ScanEmpty
 bpl OriginalAlternate
 and #$7f
 dec LoopCount
 jmp DrawLater
OriginalAlternate:
 bcc $a074

.segment "LEGACY"
 pla
 sta $0b
 txa
 pha
 lda $0b
 and #$fc
 tax
 jmp LegacyFromOffset

.segment "OAM"
ClearAll:
 php
 txa
 pha
 ldx #0
 jsr ClearGroups
 pla
 tax
 lda #$f8
 plp
 rts

; The old indirect jump entered the middle of an unrolled clear. The
; replacement takes the same saved offset and writes exactly that suffix.
LegacyFromOffset:
 lsr
 sta $0b
 lsr
 adc $0b
 adc #<ClearAll
 sta $0b
 lda #>ClearAll
 sta $0c
 jsr ClearFromX
 pla
 tax
 lda #$f8
 clc
 clv
 jmp $85b8

ClearFromX:
 txa
 and #$1f
 beq ClearGroups
Partial:
 lda #$f8
 sta $0200,x
 inx
 inx
 inx
 inx
 beq Cleared
 txa
 and #$1f
 bne Partial
ClearGroups:
 clc
Groups:
 lda #$f8
{full_group}
 txa
 adc #$20
 tax
 bne Groups
Cleared:
 rts

ScanEmpty:
 txa
 pha
 ldx #8
Check:
 ; The extra two zero-page bytes only decline the shortcut. A stale ID
 ; can still admit a native firebar, so do not use the live flag here.
 lda Sprites,x
 ora Sprites+8,x
 ora Sprites+16,x
 ora EnemyID-2,x
 bne UseOriginal
 dex
 bne Check
 pla
 jmp EmptyDraw
UseOriginal:
 pla
 tax
 lda #23
 sta LoopCount
 jmp Normalize
MarkEmpty:
 ora #$80
 rts
'''


@lru_cache(maxsize=1)
def resident():
    stores = '\n'.join(f' sta ${0x200+4*slot:04x},x' for slot in range(8))
    text = RESIDENT.format(full_group=stores) + SOURCE.split('.segment "ADVANCE"\n', 1)[1]
    out = Parent.Layout.M.assemble(text, dict(HOOK=(HOOK, len(OLD_HOOK)),
              ALTERNATE=(ALT_HOOK, ALT_POSITIVE-ALT_HOOK),
              LEGACY=(LEGACY_CLEAR, len(LEGACY_BEFORE)), OAM=(OAM_CLEAR, len(OAM_BEFORE))))
    assert out['symbols']['ClearAll'] == OAM_CLEAR
    return out


def compose(raw):
    assert Parent.Epoch.H(raw) == Parent.CORRECTED
    pieces = resident()['images']
    for pc, code in ((0xA030, 'a9f8202ca34cf2a0'), (0xA325, 'a0008cde06a9f8')):
        at = Parent.Layout.off(4, pc)
        expected = bytes.fromhex(code)
        assert raw[at:at+len(expected)] == expected
    alt = OLD_HOOK[:-1] + bytes((ALT_NEGATIVE - ALT_POSITIVE,))
    edits = [(4, at, old, pieces[name].ljust(len(old), b'\xea')) for name, at, old in
             (('HOOK', HOOK, OLD_HOOK), ('ALTERNATE', ALT_HOOK, alt), ('LEGACY', LEGACY_CLEAR, LEGACY_BEFORE),
              ('OAM', OAM_CLEAR, OAM_BEFORE))]
    return Parent.Epoch.apply(raw, edits)
