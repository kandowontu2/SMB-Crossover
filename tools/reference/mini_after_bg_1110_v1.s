; The installed bank-66 router retains its entry and both owned services.
.setcpu "6502"
.export PostBgDispatch, MiniPostBgReturn

SelectedCharacter = $6002
FmAlts = $5fe5
CrossoverBehaviorVersion = $7fe1
NextBank = $0162
SafeCallA = $016a
FarTarget = $016c
SafeReturnA = $0179
FarCall = $015a
FarCallAfterNextBank = $015d

.segment "DISPATCH"
PostBgDispatch:
    php
    sta SafeCallA
    lda SelectedCharacter
    cmp #34
    beq @karnov
    cmp #10
    bne @legacy
    lda FmAlts
    and #$44
    cmp #$40
    bne @legacy
    plp
    lda #$51
    sta FarTarget
    lda #$b4
    sta FarTarget+1
    lda #$d5
    jmp FarCall
@legacy:
    lda #$9e
    sta FarTarget
    lda #$bb
    sta FarTarget+1
    lda #$cf
    sta NextBank
    lda SelectedCharacter
    cmp #41
    beq MiniPostBgReturn
    plp
    jmp FarCallAfterNextBank
@karnov:
    plp
    lda #$6c
    sta FarTarget
    lda #$b4
    sta FarTarget+1
    lda #$9d
    jmp FarCall

.assert *-PostBgDispatch = 82, error, "Keep the following fireball entry fixed"

; Link the branch across the existing fireball leaf. The installer discards
; these link-only bytes and verifies the native leaf's exact preimage.
    .res 13,0
MiniPostBgReturn:
    ; Exact raw-41 result of HuLegacyPostBG. Its following legacy owner
    ; filter restores these flags and does not alter Mini game state.
    plp
    lda CrossoverBehaviorVersion
    beq @publish
    sec
    lda #41
@publish:
    sta SafeReturnA
    rts

.assert *-MiniPostBgReturn = 13, error, "Use only the declared graphics tail"
