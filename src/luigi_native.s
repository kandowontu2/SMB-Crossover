; User-selected Luigi profile: Mario's actual movement engine, with a modest
; dry jump increase and slightly lower ground braking traction. The former
; Crossover floating-point Luigi movement is no longer dispatched.
LUIGI_EXTRA_JUMP_FRACTION = $33 ; 51/256 px/update: about8..10% higher apex.
LUIGI_BRAKING_SHIFT = 3        ; Native braking minus1/8; acceleration is native.
.pushseg
.segment "FIXED"
.proc LuigiNativePrepare
  lda #0
  ldx PlayerStatus
  bne :+
    lda #1
  :
  sta PlayerSize
  rts
.endproc
.segment "PLAYER"
.proc LuigiNativeJump
  lda SwimmingFlag
  bne Done
  lda GameEngineSubroutine
  cmp #8
  bne Done
  ; Preserve native gravity, speed-dependent jump class and release cutoff.
  ; Subtract from the signed initial velocity, including its fractional byte.
  lda Player_Y_MoveForce
  sec
  sbc #LUIGI_EXTRA_JUMP_FRACTION
  sta Player_Y_MoveForce
  lda Player_Y_Speed
  sbc #0
  sta Player_Y_Speed
Done:
  rts
.endproc
.proc LuigiNativeTraction
.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
  ; Foreign callers execute the exact original prefix and original Done RTS.
  lda SelectedCharacter
  cmp #CHARACTER_LUIGI
  bne Done
  farcall LuigiSourceNativeTractionBody,jmp
::LuigiSourceMovementBridge:
  ; Genuine local entry, only called by Luigi's actual movement selector.
  farcall LuigiSourceMovementDispatch,jmp
  .res 83-(*-::LuigiNativeTraction),$ea
Done:
  rts
  .assert *-LuigiNativeTraction=84,error,"Retained native traction public span"
.else
  lda SelectedCharacter
  cmp #CHARACTER_LUIGI
  bne Done
  lda SwimmingFlag
  bne Done
  lda GameEngineSubroutine
  cmp #8
  bne Done
  lda Player_State
  bne Done
  lda Player_X_Speed
  beq Done
  bmi Leftward
  lda Left_Right_Buttons
  and #Right_Dir
  bne Done                       ; Keep native acceleration/run speed.
  beq Brake
Leftward:
  lda Left_Right_Buttons
  and #Left_Dir
  bne Done
Brake:
  lda FrictionAdderLow
  sta R0
  lda FrictionAdderHigh
  sta R1
  .repeat ::LUIGI_BRAKING_SHIFT
    lsr R1
    ror R0
  .endrepeat
  lda FrictionAdderLow
  sec
  sbc R0
  sta FrictionAdderLow
  lda FrictionAdderHigh
  sbc R1
  sta FrictionAdderHigh
Done:
  rts
.endif
.endproc
.segment "EXPANDED"
.proc LuigiNativeVisuals
  lda CrouchingFlag
  sta RgCrouch
  lda #0
  sta XgLuigiSkid
  lda Player_State
  bne Done
  lda Player_XSpeedAbsolute
  cmp #$0b
  bcc Done
  lda PlayerFacingDir
  cmp Player_MovingDir
  beq Done
  inc XgLuigiSkid
Done:
  rts
.endproc
.popseg
