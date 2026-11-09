.setcpu "6502"
.export GfSwordStart, GfSwordAdvance
.import GfAction, GfFacing, GfVXLo, GfVXHi, GfClock, GfBodyPose, GfBodyFacing
.import GfSwordActive, GfSwordPhase, GfSwordPose, GfSwordFacing, GfSwordCue

.segment "GETSU_SWORD"

; PRG15:$E36E..$E376. Call with fresh B when the basic sword is equipped
; and the donor action mask permits a new attack.
.proc GfSwordStart
    lda GfSwordPhase
    bne Return
    lda #$01
    sta GfSwordActive
Return:
    rts
.endproc

; PRG15:$E62A..$E6A6 and $E8CE..$E8E8, with the basic sword equipped.
; A cue is published for the host audio bridge on source phase 3.
; Rock-breaker and other equipped weapon effects have separate owners.
.proc GfSwordAdvance
    lda #$00
    sta GfSwordCue
    lda GfSwordActive
    beq Return
    lda GfVXHi
    ora GfVXLo
    bne CheckClock
    lda GfAction
    lsr a
    bcs CheckClock
    lda GfFacing
    sta GfBodyFacing
    lda #$0c
    sta GfBodyPose
CheckClock:
    lda GfClock
    and #$03
    bne Return
    inc GfSwordPhase
    lda GfSwordPhase
    cmp #$06
    bcs Clear
    cmp #$03
    bne SetPose
    lda #$25
    sta GfSwordCue
    bne SetPose
Clear:
    lda #$00
    sta GfSwordPhase
    lda GfAction
    and #$fb
    sta GfAction
    lda #$00
    sta GfSwordActive
SetPose:
    lda GfFacing
    sta GfSwordFacing
    ldy GfSwordPhase
    lda Poses,y
    sta GfSwordPose
Return:
    rts
Poses:
    .byte $01,$07,$08,$09,$0a,$0b
.endproc
