.setcpu "6502"
.import SelectedCharacter, MarioVariant, OperMode, GameEngineSubroutine
.import VRAM_Buffer1_Offset, Player_X_Position, Player_PageLoc
.import Player_Y_Position, Player_Y_HighPos, PlayerSize, CrouchingFlag
.import Player_Y_Speed, MmBlockAttack, FarCallCommon, PlayerHeadCollision
.importzp R2, R3, R4, R5, R6, R7
.export GiantCrushCell

.segment "GIANT_CRUSH"

; Called only after the source sweep has classified a crushable contact.
; A=metatile, X/Y=world page/low X, native R2/R6/R7 own the cell.
; C set means the real native block owner accepted and queued the effect.
; R0..R7, M0/M1, A/X/Y and non-carry flags are caller scratch.
GiantCrushCell:
    sta R3
    stx R4
    sty R5
    lda SelectedCharacter
    bne Rejected
    lda MarioVariant
    cmp #9
    bne Rejected
    lda OperMode
    cmp #1
    bne Rejected
    lda GameEngineSubroutine
    cmp #8
    bne Rejected
    ; The largest reached native effect appends 24 bytes. Keep space for
    ; another 20-byte native producer and the 84-byte buffer's terminator.
    lda VRAM_Buffer1_Offset
    cmp #40
    bcs Rejected
    lda R7
    cmp #3
    bne Rejected
    lda R6
    and #$f0
    beq ColumnReady
    cmp #$d0
    bne Rejected
ColumnReady:
    ldy R2
    cpy #$d0
    bcs Rejected
    tya
    and #$0f
    bne Rejected
    lda (R6),y
    beq Rejected
    cmp #$23
    beq Rejected
    cmp R3
    bne Rejected
    jmp Claim
Rejected:
    clc
    rts

Claim:
    ; Exact MMC5 safe call to physical PRG8:$BDC4, GuestClaimBlockSlot.
    lda #$c4
    sta $016c
    lda #$bd
    sta $016d
    lda #$88
    jsr FarCallCommon
    bcc Rejected

    lda Player_X_Position
    pha
    lda Player_PageLoc
    pha
    lda Player_Y_Position
    pha
    lda Player_Y_HighPos
    pha
    lda PlayerSize
    pha
    lda CrouchingFlag
    pha
    lda Player_Y_Speed
    pha
    lda MmBlockAttack
    pha

    lda R5
    and #$f0
    sta Player_X_Position
    lda R4
    sta Player_PageLoc
    lda R2
    clc
    adc #$20
    sta Player_Y_Position
    lda #1
    sta Player_Y_HighPos
    sta MmBlockAttack
    lda #0
    sta PlayerSize
    sta CrouchingFlag
    lda R3
    jsr PlayerHeadCollision

    pla
    sta MmBlockAttack
    pla
    sta Player_Y_Speed
    pla
    sta CrouchingFlag
    pla
    sta PlayerSize
    pla
    sta Player_Y_HighPos
    pla
    sta Player_Y_Position
    pla
    sta Player_PageLoc
    pla
    sta Player_X_Position
    sec
    rts
