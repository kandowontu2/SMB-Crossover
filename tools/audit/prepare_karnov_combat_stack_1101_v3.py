"""Park the authenticated combat entry's 17 inherited stack bytes in C2.

This changes only the proposed combat component. It supplies no carrier,
loader, ROM patch or qualification of a native candidate.
"""
from pathlib import Path

R=Path(__file__).resolve().parents[2]
SOURCE=R/'tools/reference/karnov_combat_1101_v2.inc'


def transform_source(text=None):
    text=SOURCE.read_text()if text is None else text
    old='KC_END=$c860                  ;32-byte selected C2 context [C840,C860)'
    new='''KC_END=$c860                  ;32-byte selected C2 contact context
; Only a genuine authenticated KrDispatch -> FarCallCommon child may enter.
; Its frame owns ten saved dispatcher bytes, five child farcall bytes and
; the two-byte return into the parent's bank helper. Park these opaque bytes
; above the separate pickup context, without changing any return operand.
; Interrupts never execute a combat service; native head callbacks use their
; own pickup context. No frame is freed until every byte is safely parked.
KC_PARK_SP=$c868
KC_PARK=$c869
KC_PARK_BYTES=17
KC_PARK_END=KC_PARK+KC_PARK_BYTES
.assert KC_PARK_END <= $c900,error,"Combat frame overlaps the code carrier"
'''
    assert text.count(old)==1
    text=text.replace(old,new)
    old=''' lda ObjectOffset
 sta KC_OBJECT
 lda SelectedCharacter'''
    new=''' lda ObjectOffset
 sta KC_OBJECT
 tsx
 stx KC_PARK_SP
 ldy #0
KcParkFrame:
 inx
 lda $0100,x
 sta KC_PARK,y
 iny
 cpy #KC_PARK_BYTES
 bne KcParkFrame
 txs                         ; original bytes are now exclusively parked
 lda SelectedCharacter'''
    assert text.count(old)==1
    text=text.replace(old,new)
    old='''KcDone:
 lda KC_OBJECT'''
    new='''KcDone:
 ; Lower SP BEFORE restoring the original frame. An IRQ/NMI at any point
 ; must push strictly below the live/partly restored bytes, never onto them.
 ldx KC_PARK_SP
 txs
 ldy #0
KcUnparkFrame:
 inx
 lda KC_PARK,y
 sta $0100,x
 iny
 cpy #KC_PARK_BYTES
 bne KcUnparkFrame
 lda KC_OBJECT'''
    assert text.count(old)==1
    return text.replace(old,new)
