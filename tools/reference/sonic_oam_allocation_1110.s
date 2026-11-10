.setcpu "6502"

PosePointer = $6b06
PlayerStart = $6c07
Rotation = $6c08
FirstSprite = $6c09
OamOffset = $06de
PoseZp = $03
DrawGuest = $bfcc
DrawObjects = $a155

.segment "GUEST_BRANCH"
    bne RosterShots

.segment "GUEST_RESERVATION"
RosterShots:
    jsr DrawGuest
    lda OamOffset
    sta PlayerStart
ReservePose:
    lda PosePointer
    sta PoseZp
    lda PosePointer+1
    sta PoseZp+1
    ; A guest that drew its complete body can leave the native pose null.
    beq Done
    ldy #0
    lda (PoseZp),y
    clc
    adc OamOffset
    sta OamOffset
Done:
    jmp DrawObjects

.segment "GUEST_ROTATION"
    lda #0
    sec
    sbc FirstSprite
    and #$fc
    sta Rotation
    rts
