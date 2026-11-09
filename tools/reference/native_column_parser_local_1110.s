.setcpu "6502"
.segment "COLUMN"

ProcessAreaData = $a314
VariantBridge = $bfef
BlockBufferColumnPos = $04a0
GetBlockBufferAddr = $95dc
MetatileBuffer = $04a1
MTileAttribute = $ef36
ResetHealthColumn = $9076
SelectedCharacter = $6002
R0 = $03
BlockPointer = $09

Column:
    jsr ProcessAreaData
    jsr VariantBridge
    lda BlockBufferColumnPos
    jsr GetBlockBufferAddr
    ldx #0
    ldy #0
Row:
    sty R0
    ldy MetatileBuffer,x
    lda MTileAttribute,y
    and #$3f
    beq StoreRow
    tya
StoreRow:
    ldy R0
    sta (BlockPointer),y
    ; GetBlockBufferAddr leaves C clear on either native column page.
    ; On later rows, the taken CPX/BCC path supplies the same clear C.
    tya
    adc #$10
    tay
    inx
    cpx #13
    bcc Row
    ; The raw-zero tail uses CPX. The shadow path sets its own carry.
    ldy SelectedCharacter
    jmp ResetHealthColumn
    .assert *-Column=$30,error,"Preserve ProcessAreaData entry"

.segment "VARIANT_TARGET"
    .byte $12                  ; Existing authored postpass at physical 26:A012.
