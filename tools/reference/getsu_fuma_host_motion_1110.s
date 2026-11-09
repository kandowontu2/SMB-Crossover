.setcpu "6502"
.macpack longbranch
.export GfHostMove, GfHostReset
.import GfHorizontalSpeed, GfJumpStart, GfVerticalSpeed, GfIntegrateY
.import GfSwordStart, GfSwordAdvance
.import GfAction, GfFacing, GfVXLo, GfVXHi, GfVYLo, GfVYHi
.import GfYLo, GfYHi, GfJumpHold, GfSupport, GfClock
.import GfStateStart, GfStateSize, GfInitialized, GfPreviousPad, GfFresh
.import GfCrouchTime, GfXFrac, GfIssuedXSpeed, GfIssuedYSpeed
.import SelectedCharacter, OperMode, GameEngineSubroutine, SwimmingFlag, JumpspringAnimCtrl
.import SavedJoypadBits, Player_State, PlayerFacingDir, PlayerSize, CrouchingFlag
.import Player_X_Position, Player_PageLoc, Player_X_Speed, Player_XSpeedAbsolute, Player_X_Scroll
.import Player_Pos_ForScroll, ScreenLeft_X_Pos
.import Player_Y_Position, Player_Y_HighPos, Player_Y_Speed, Player_Y_MoveForce

.segment "GETSU_HOST_MOTION"

; The host still runs ScrollHandler, native background probes and contact
; after this worker returns. The scene owner clears this state at each spawn.
.proc GfHostReset
    lda #0
    sta GfInitialized
    rts
.endproc

.proc GfHostMove
    lda SelectedCharacter
    cmp #42
    jne Reject
    lda OperMode
    cmp #1
    jne Reject
    lda GameEngineSubroutine
    cmp #8
    jne Reject
    lda SwimmingFlag
    ora JumpspringAnimCtrl
    jne Reject
    lda Player_State
    cmp #3
    jeq Reject

    lda GfInitialized
    bne Ready
    lda #0
    ldx #GfStateSize-1
ClearState:
    sta GfStateStart,x
    dex
    bpl ClearState
    lda PlayerFacingDir
    cmp #2
    bne InitRight
    inc GfFacing
InitRight:
    inc GfInitialized
Ready:
    lda SavedJoypadBits
    eor GfPreviousPad
    and SavedJoypadBits
    sta GfFresh
    lda SavedJoypadBits
    sta GfPreviousPad

    ; If native side contact cleared the projected speed, discard the
    ; blocked donor velocity and fraction. Camera carries keep both.
    lda Player_X_Speed
    bne Crouch
    lda GfIssuedXSpeed
    beq Crouch
    lda #0
    sta GfVXLo
    sta GfVXHi
    sta GfXFrac
Crouch:
    jsr CrouchInput
    lda Player_State
    bne HorizontalPad
    lda SavedJoypadBits
    and #4
    beq HorizontalPad
    lda #0
    beq Horizontal
HorizontalPad:
    lda SavedJoypadBits
Horizontal:
    jsr GfHorizontalSpeed
    jsr ApplyX
    jsr MoveY

    ; The donor admits fresh A and B after movement. It does not apply a
    ; newly armed jump's velocity until the following update.
    jsr GfSwordAdvance
    lda GfAction
    and #$0b
    bne CheckSword
    lda GfFresh
    and #$80
    beq CheckSword
    jsr GfJumpStart
    lda GfVYHi
    sta GfIssuedYSpeed
    sta Player_Y_Speed
    lda #1
    sta Player_State
CheckSword:
    lda GfAction
    and #$0c
    bne Publish
    lda GfFresh
    and #$40
    beq Publish
    jsr GfSwordStart
Publish:
    lda GfFacing
    clc
    adc #1
    sta PlayerFacingDir
    lda #0
    sta PlayerSize
    lda GfAction
    and #1
    asl a
    asl a
    sta CrouchingFlag
    inc GfClock
    sec
    rts
Reject:
    clc
    rts
.endproc

; Grounded Down starts the donor's 16-update crouch latch. The first
; timer decrement happens on the entry update, as at donor E4EC.
.proc CrouchInput
    lda Player_State
    bne Return
    lda GfAction
    and #$f5
    sta GfAction
    ldy #16
    lda GfCrouchTime
    bne CountDown
    dey
    bne CheckPad
CountDown:
    dec GfCrouchTime
    bne Return
CheckPad:
    lda SavedJoypadBits
    and #4
    beq Release
    lda GfAction
    ora #1
    sta GfAction
    sty GfCrouchTime
    rts
Release:
    lda GfAction
    and #$fe
    sta GfAction
Return:
    rts
.endproc

.proc ApplyX
    lda Player_X_Position
    sec
    sbc ScreenLeft_X_Pos
    sta Player_Pos_ForScroll
    lda GfXFrac
    clc
    adc GfVXLo
    sta GfXFrac
    lda Player_X_Position
    tax
    adc GfVXHi
    sta Player_X_Position
    ldy GfVXHi
    bmi Negative
    lda Player_PageLoc
    adc #0
    jmp Page
Negative:
    lda Player_PageLoc
    adc #$ff
Page:
    sta Player_PageLoc
    txa
    eor #$ff
    sec
    adc Player_X_Position
    sta Player_X_Scroll

    lda GfVXHi
    asl a
    asl a
    asl a
    asl a
    sta GfIssuedXSpeed
    lda GfVXLo
    lsr a
    lsr a
    lsr a
    lsr a
    ora GfIssuedXSpeed
    sta GfIssuedXSpeed
    sta Player_X_Speed
    bpl Absolute
    eor #$ff
    clc
    adc #1
Absolute:
    sta Player_XSpeedAbsolute
    rts
.endproc

.proc MoveY
    lda Player_State
    bne Air
    lda #0
    sta GfVYHi
    sta GfVYLo
    sta GfYLo
    sta GfIssuedYSpeed
    sta Player_Y_Speed
    rts
Air:
    lda Player_Y_Speed
    cmp GfIssuedYSpeed
    beq KeepVelocity
    sta GfVYHi
    lda #0
    sta GfVYLo
    sta GfYLo
KeepVelocity:
    lda GfAction
    and #2
    beq NoHold
    lda SavedJoypadBits
NoHold:
    jsr GfVerticalSpeed
    lda Player_Y_Position
    sta GfYHi
    jsr GfIntegrateY
    ldx GfVYHi
    bmi UpPage
    lda Player_Y_HighPos
    adc #0
    jmp Page
UpPage:
    lda Player_Y_HighPos
    adc #$ff
Page:
    sta Player_Y_HighPos
    lda GfYHi
    sta Player_Y_Position
    lda GfYLo
    sta Player_Y_MoveForce
    stx GfIssuedYSpeed
    stx Player_Y_Speed
    rts
.endproc
