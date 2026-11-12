; Surviving thrown actors only. Native contact/destruction admission belongs
; before this leaf; both existing projectile updates still run before orbit.
.setcpu "6502"
.segment "THROW_FLIGHT"

SteveThrowTickPrelude:
    lda #0
    sta SteveThrowFrame
    lda SteveUpgradeState
    beq ThrowReadFacing
    jsr SteveThrowReset
ThrowReadFacing:
    lda PlayerFacingDir
    cmp #2
    rts

SteveThrowOrbit:
    bit SteveThrowSelector
    bpl ThrowOrdinaryOrbit
    lda #$80
    sta SteveThrowFrame
    lda ScreenLeft_X_Pos
    sta SteveThrowCameraX
    lda ScreenLeft_PageLoc
    sta SteveThrowCameraX+1
    ldx #4
ThrowPackCamera:
    asl SteveThrowCameraX
    rol SteveThrowCameraX+1
    dex
    bne ThrowPackCamera
    lda #0
    sta SteveThrowCameraY
    sta SteveThrowCameraY+1
    jsr SteveThrowUpdate
    ; Original $A523 clears the two surviving contact-receipt bits.
    lda SteveBotActor
    and #$3f
    sta SteveBotActor
    rts
ThrowOrdinaryOrbit:
    lda SteveLiftState
    jmp SteveLiftOrbit+3

SteveThrowReset:
    txa
    pha
    lda #0
    ldx #15
ThrowClearState:
    sta SteveThrowSelector,x
    dex
    bpl ThrowClearState
    sta SteveLiftState
    ldx #4
ThrowClearBotPose:
    sta SteveLiftBotAnim,x
    dex
    bpl ThrowClearBotPose
    pla
    tax
    lda #0
    rts

SteveThrowGrant:
    jsr SteveTokenTick
    lda SteveTokenCountdown
    cmp #$30
    bne ThrowGrantDone
    lda SteveTokenPattern
    bne ThrowGrantDone
    jmp SteveThrowReset
ThrowGrantDone:
    rts

.segment "THROW_EMISSION"
; Replace the callers' LDA lift-state/CMP #4 with JSR here and two NOPs.
; The sign-bit frame marker remains set for the zero-pose reattach draw.
SteveThrowEmissionGate:
    lda SteveThrowFrame
    ora SteveLiftState
    cmp #4
    rts
