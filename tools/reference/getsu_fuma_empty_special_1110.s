.setcpu "6502"

SelectedCharacter = $6002
SafecallA = $016a
ShRestoreScroll = $aa4b
GfEmptyReturn = $a7eb
CoNativePrimitive = $a817

.segment "TAIL"
.export GfEmptySpecial
    jmp ShRestoreScroll         ; Identical incumbent CTRL/status/scroll tail.

GfEmptySpecial:
    lda SelectedCharacter
    eor #42
    bne Foreign
    jmp GfEmptyReturn
Foreign:
    lda SafecallA
    jmp CoNativePrimitive

    .res 2,$ea
PrCopyLiveDone:
    rts                          ; Existing non-Prince branch still targets AFAF.
