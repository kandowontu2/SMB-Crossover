; Authenticated A3 dispatch enters C2 with Y equal to the original caller bank.
; Main projects movement here and the native camera and terrain resolve it later.
.setcpu "6502"
.segment "BRIDGE"

SteveLiveMovement:
    cpy #$e0
    bne SteveMovementFallback
    lda OperMode
    cmp #1
    bne SteveForgetMotion
    lda OperMode_Task
    cmp #3
    bne SteveForgetMotion
    lda GameEngineSubroutine
    cmp #8
    bne SteveForgetMotion
    lda SwimmingFlag
    ora MmDeathFlag
    ora JumpspringAnimCtrl
    bne SteveForgetMotion
    lda Player_State
    cmp #3
    beq SteveForgetMotion
    lda GamePauseStatus
    lsr a
    bcs SteveMovementFallback
    lda NmiDisable
    bpl SteveMovementFallback
    lda FamilyMainCommit
    lsr a
    bcc SteveMovementFallback
    jmp SteveMoveStep
SteveForgetMotion:
    lda #0
    sta SteveHostReady
SteveMovementFallback:
    clc
    rts

SteveMoveStep:
    lda #<JnEnsure
    ldx #>JnEnsure
    jsr SteveMoveMikeCall
    lda #<JnInputs
    ldx #>JnInputs
    jsr SteveMoveMikeCall
    lda #<JnEffectiveTier
    ldx #>JnEffectiveTier
    jsr SteveMoveMikeCall
    ; Exact common prefix of JnMovement after its three initial calls.
    .byte StockPreludeBytes
    lda SteveHostReady
    bne ImportMotion
    lda #0
    sta SteveMoveState
    sta SteveMoveVX
    sta SteveMoveVY
    sta SteveHostXFrac
    sta SteveHostYFrac
    lda PlayerFacingDir
    lsr a
    lda #0
    bcs SetInitialFace
    lda #$80
SetInitialFace:
    sta SteveMoveFacing
    lda #1
    sta SteveHostReady
    lda Player_State
    bne StartFall
    jmp SetMoveInput

ImportMotion:
    lda XgWallContact
    bne ResetHorizontal
    lda Player_X_Position
    cmp SteveHostLastX
    bne ResetHorizontal
    lda Player_PageLoc
    cmp SteveHostLastPage
    beq ReadVertical
ResetHorizontal:
    lda #0
    sta SteveMoveVX
    sta SteveHostXFrac
ReadVertical:
    lda Player_Y_Position
    cmp SteveHostLastY
    bne ResetVerticalFraction
    lda Player_Y_HighPos
    cmp SteveHostLastYPage
    beq ReadNativeState
ResetVerticalFraction:
    lda #0
    sta SteveHostYFrac
ReadNativeState:
    lda SteveMoveState
    cmp #1
    beq ImportAir
    lda Player_State
    beq SetMoveInput
StartFall:
    lda #1
    sta SteveMoveState
    lda #0
    sta SteveMoveVY
    sta SteveHostYFrac
    beq SetMoveInput
ImportAir:
    lda Player_State
    bne CheckCeiling
    lda SteveMoveDY
    beq SetMoveInput
    bmi CheckCeiling
    ; $A319. Keep steering already published before terrain, and import
    ; just the resulting support and recovery before the next projection.
    lda #0
    sta SteveMoveVY
    sta SteveMoveJumpHold
    sta SteveHostYFrac
    lda SteveMovePad
    and #3
    beq RecoverAfterLanding
    lda #0
    beq SaveImportedState
RecoverAfterLanding:
    lda #9
    sta SteveMoveRecovery
    lda #2
SaveImportedState:
    sta SteveMoveState
    bpl SetMoveInput
CheckCeiling:
    lda SteveMoveDY
    bpl SetMoveInput
    lda Player_Y_Speed
    bmi SetMoveInput
    lda #0
    sta SteveMoveVY
    sta SteveHostYFrac
    lda #$ff
    sta SteveMoveJumpHold

SetMoveInput:
    lda #0
    sta XgWallContact
    lda JnPressed
    sta SteveMovePressed
    lda SavedJoypadBits
    sta SteveMovePad
    lda JnAttack
    beq ProjectMotion
    lda SteveMoveState
    cmp #1
    beq ProjectMotion
    ; Existing attack owns the grounded pose. Let residual movement decay.
    lda SteveMovePressed
    and #$7f
    sta SteveMovePressed
    lda SteveMoveState
    cmp #3
    beq KeepAttackCrouch
    lda SteveMovePad
    and #$f8
    jmp SaveAttackPad
KeepAttackCrouch:
    lda SteveMovePad
    and #$fc
SaveAttackPad:
    sta SteveMovePad
ProjectMotion:
    lda SteveMoveState
    pha
    jsr SteveMotionProject
    pla
    bne NoJumpCue
    lda SteveMoveState
    cmp #1
    bne NoJumpCue
    lda #Sfx_BigJump
    sta Square1SoundQueue
NoJumpCue:
    clc
    jsr SteveMotionFinish

    lda SteveMoveDX
    sta Player_X_Speed
    bpl SetAbsSpeed
    eor #$ff
    clc
    adc #1
SetAbsSpeed:
    sta Player_XSpeedAbsolute
    lda SteveMoveDX
    ldx SteveHostXFrac
    jsr SteveIntegrateQ4
    stx SteveHostXFrac
    sta Player_X_Scroll
    tay
    clc
    adc Player_X_Position
    sta Player_X_Position
    sta SteveHostLastX
    tya
    bmi NegativeX
    lda #0
    bpl SaveXPage
NegativeX:
    lda #$ff
SaveXPage:
    adc Player_PageLoc
    sta Player_PageLoc
    sta SteveHostLastPage

    lda SteveMoveDY
    ldx SteveHostYFrac
    jsr SteveIntegrateQ4
    stx SteveHostYFrac
    tay
    clc
    adc Player_Y_Position
    sta Player_Y_Position
    tya
    bmi NegativeY
    lda #0
    bpl SaveYPage
NegativeY:
    lda #$ff
SaveYPage:
    adc Player_Y_HighPos
    sta Player_Y_HighPos
    cmp #1
    bne OutsideFirstPage
    lda Player_Y_Position
    cmp #16
    bcs PublishY
    bcc ClampTop
OutsideFirstPage:
    bcs PublishY
ClampTop:
    lda #1
    sta Player_Y_HighPos
    lda #16
    sta Player_Y_Position
    lda #0
    sta SteveMoveVY
    sta SteveHostYFrac
PublishY:
    lda Player_Y_Position
    sta SteveHostLastY
    lda Player_Y_HighPos
    sta SteveHostLastYPage
    lda SteveMoveVY
    jsr SteveSignedQ4ToPixels
    sta Player_Y_Speed
    sta MmVY+2
    ldx #0
    ldy SteveMoveState
    cpy #3
    bne AirNativeState
    lda #1
    sta CrouchingFlag
AirNativeState:
    cpy #1
    bne PublishState
    inx
    lda SteveMoveVY
    bmi PublishState
    inx
PublishState:
    stx Player_State
    lda SteveMoveFacing
    rol a
    lda #1
    adc #0
    sta PlayerFacingDir
    lda #0
    sta MmVX
    sta MmVX+1
    sta MmVX+2
    sta MmVY
    sta MmVY+1
    sta MmXFraction
    sta MmXFraction+1
    sta MmYFraction
    sta MmYFraction+1
SteveMovementClaim:
    sec
    rts

SteveMoveMikeCall:
    sta $016c
    stx $016d
    lda #$e0
    jmp $015a

; A is signed Q4 displacement, X is a retained nibble. The signed sum
; fits in one byte because horizontal/vertical velocity is limited to ±96.
SteveIntegrateQ4:
    sta SteveMoveDrag
    txa
    clc
    adc SteveMoveDrag
    pha
    and #15
    tax
    pla
SteveSignedQ4ToPixels:
    cmp #$80
    ror a
    cmp #$80
    ror a
    cmp #$80
    ror a
    cmp #$80
    ror a
    rts
