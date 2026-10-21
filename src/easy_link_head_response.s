; Bounded old Link normal15 positive ceiling response; native admission retained.
; No persistent state. Unsupported Easy profiles restore native NYSpd exactly.
.pushseg
.segment "LINK_HEAD_COLD"
EasyLinkHeadResponseStart:
.proc EasyLinkHeadResponse
  RP_Save
  lda OperMode
  cmp #1
  jne Native
  lda GameEngineSubroutine
  cmp #8
  jne Native
  lda Player_State
  cmp #1
  jne Native
  lda RgBillBurst
  cmp #17                       ; actual exported jump_1 body15.
  jne Native
  lda RgAttack
  ora RgCrouch
  ora CrouchingFlag
  ora GuestHurtTicks
  ora GuestLegacyHurt
  ora GuestPowerupActive
  ora MmUnderwater
  ora SwimmingFlag
  jne Native
  lda AreaType
  jeq Native                    ; water/cache rules remain independently open.
  lda Player_Y_HighPos
  cmp #1
  jne Native
  lda Player_Y_Position
  cmp #224
  jcs Native
  lda R2
  cmp #$d0
  jcs Native
  lda MmVY+2
  jpl Native
  cmp Player_Y_Speed
  jne Native                    ; actual native/q motion must agree pre-response.
  cmp #$fb
  jcc Native
  bne VelocityReady
  lda MmVY+1
  cmp #$95
  jcc Native
VelocityReady:
  lda Player_PageLoc
  cmp #$ff
  jeq Native
  bne XVelocity
XVelocity:
  lda MmVX+2
  beq XReady
  cmp #$ff
  beq XReady
  cmp #1
  beq XPositive
  cmp #$fe
  jne Native
  lda MmVX+1
  cmp #$8a
  jcc Native
  bne XReady
  lda MmVX
  cmp #$ab
  jcc Native
  bcs XReady
XPositive:
  lda MmVX+1
  cmp #$75
  bcc XReady
  jne Native
  lda MmVX
  cmp #$56
  jcs Native
XReady:
  ldy R3
  lda MTileAttribute,y
  and #MTILE_SOLID|MTILE_CLIMB|MTILE_BUMP
  cmp #MTILE_SOLID|MTILE_BUMP
  jne Native                    ; only authored solid Ground/bump family here.
  cpy #$23
  jeq Native
  cpy #$66
  jeq Native
  cpy #$67
  jeq Native
  cpy #$68
  jeq Native
  cpy #$c2
  jeq Native
  cpy #$c3
  jeq Native
  cpy #$c5
  jeq Native
  lda R2
  clc
  adc #$30
  sta RgTempY                   ; actual queried Ground bottom.
  lda Player_Y_Position
  clc
  adc #17                       ; source body top = foot(PY+32)-15.
  cmp RgTempY
  bcc Previous
  jne Native
  lda MmYFraction
  ora MmYFraction+1
  jne Native                    ; inclusive boundary requires fraction zero.
Previous:
  sec
  lda MmYFraction
  sbc MmVY
  sta R0
  lda MmYFraction+1
  sbc MmVY+1
  sta R1
  lda Player_Y_Position
  sbc MmVY+2
  clc
  adc #17
  cmp RgTempY
  jcc Native                    ; source last top must be below/equal Ground.
  ; The original live Link hRect is15 in every exported live frame except
  ; END34. Current frame17/nohurt and direct below retain that previous body.
  lda RgTempY
  sec
  sbc #17
  sta Player_Y_Position
  lda #0
  sta MmYFraction
  sta MmYFraction+1
  lda LsrHurtFlags
  and #8
  beq KeepVelocity
  lda #$55
  sta MmVY
  lda #$d5
  sta MmVY+1
  lda #0
  sta MmVY+2                    ;100Flash/s /120 =Q16 $00D555.
KeepVelocity:
  lda MmVY+2
  sta Player_Y_Speed             ; existing AirSync must preserve exact qVY.
  lda #Sfx_Bump
  ora Square1SoundQueue
  sta Square1SoundQueue          ; source cue attempt; do not erase queued bits.
  jsr GetPlayerOffscreenBits
  jsr RelativePlayerPosition
  ldx #0
  jsr BoundingBoxCore            ; real later consumers see canonical body.
  jmp Done
Native:
  lda #1
  sta Player_Y_Speed
Done:
  RP_Restore
  rts
.endproc
EasyLinkHeadResponseEnd:
.assert EasyLinkHeadResponseEnd-EasyLinkHeadResponseStart<=529,error,"Link head cold budget529"
.popseg
