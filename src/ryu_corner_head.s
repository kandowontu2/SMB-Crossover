.pushseg
.segment "RYU_COLD"
RyuCornerHeadStart:
.proc RyuCornerHeadGate
  ; Outer RyuSourceHeadGate owns RP_Save/RP_Restore and blank query return.
  cpy #51                     ; actual normal native side rows8/24.
  bne EarlyExit
  lda GameEngineSubroutine
  cmp #8
  bne EarlyExit
  lda RyuSourceBodyProfile
  cmp #25
  bne EarlyExit
  lda RyWallOldHeight
  cmp #25
  bne EarlyExit
  lda RyWallSupported
  beq EarlyExit
  lda RyWallWasGround
  cmp #1
  bne EarlyExit
  lda Player_State
  cmp #1
  bne EarlyExit
  lda RgAttack
  ora RgCrouch
  ora CrouchingFlag
  ora GuestHurtTicks
  ora MmUnderwater
  ora SwimmingFlag
  ora XgWall
  ora XgWallLock
  ora RyPlatformSlot
  ora AvSlash
  bne EarlyExit
  lda AreaType
  beq EarlyExit
  lda Player_Y_HighPos
  cmp #1
  bne EarlyExit
  lda Player_PageLoc
  cmp #$ff
  beq EarlyExit
  lda MmVY+2
  bmi Coherent
EarlyExit:
  jmp Done
Coherent:
  ; Compute each multi-byte sum before comparing: CMP must not corrupt ADC C.
  clc
  lda RyWallOldYFine
  adc MmVY
  sta R0
  lda RyWallOldYFrac
  adc MmVY+1
  sta R1
  lda RyWallOldY
  adc MmVY+2
  cmp Player_Y_Position
  bne EarlyExit
  lda R0
  cmp MmYFraction
  bne EarlyExit
  lda R1
  cmp MmYFraction+1
  bne EarlyExit
  lda RyWallOldPage
  cmp Player_PageLoc
  bne EarlyExit                 ; world page seams remain native fallback.
  clc
  lda RyWallOldXFine
  adc MmVX
  sta R0
  lda RyWallOldXFrac
  adc MmVX+1
  sta R1
  lda RyWallOldX
  adc MmVX+2
  cmp Player_X_Position
  bne EarlyExit
  lda R0
  cmp MmXFraction
  bne EarlyExit
  lda R1
  cmp MmXFraction+1
  bne EarlyExit
  ; Direct underside crossing within bounded, nonwrapped map rows.
  lda Player_Y_Position
  cmp #32
  bcc MiddleExit
  cmp #176
  bcs MiddleExit
  lda MmYFraction
  ora MmYFraction+1
  cmp #1
  lda Player_Y_Position
  adc #6                       ; floor(source top-epsilon), inclusive touch.
  and #$f0
  sta RgTempY
  clc
  adc #16
  sta R2                       ; candidate bottom.
  lda RyWallOldY
  clc
  adc #7
  cmp R2
  bcc MiddleExit
  jmp Width
MiddleExit:
  jmp Done
Width:
  ; A body-width edge can touch a different cell than center PX+8.
  lda Player_X_Position
  clc
  adc #8
  and #$f0
  sta R3
  lda MmXFraction
  cmp #1
  lda MmXFraction+1
  sbc #$c0                    ; C iff fraction>.75; inclusive left cell.
  lda Player_X_Position
  adc #1
  sta RgTempX
  lda Player_PageLoc
  adc #0
  sta RgTempPage
LeftCell:
  lda RgTempX
  and #$f0
  cmp R3
  bne Candidate
  clc                          ; same column as actual native right probe.
  lda Player_X_Position
  adc #14
  sta RgTempX
  lda Player_PageLoc
  adc #0
  sta RgTempPage
  lda RgTempX
  and #$f0
  cmp R3
  beq MiddleExit
Candidate:
  sta RgTempX
  jsr ReadCell
  cmp #$16
  bcc MiddleExit
  cmp #$19
  bcs MiddleExit                     ; proven plain immutable Pipe/Ground only.
  ; Previous source X must overlap this same cell, not a calcAxis diagonal.
  lda RgTempX
  sec
  sbc RyWallOldX
  sta R5
  lda RgTempPage
  sbc RyWallOldPage
  beq OldRight
  cmp #$ff
  bne Done
  lda R5
  cmp #$f3                     ; conservative previous left strictly inside cell.
  bcc Done
  bcs Lower
OldRight:
  lda R5
  cmp #15
  bcs Done
Lower:
  ; Every lower same-side cell through the new source foot must be empty.
  ; Conservative nonzero rejection retains all other/special collisions.
  lda R2
  clc
  adc #25
  sta R6
  lda R2
  sta RgTempY
Loop:
  jsr ReadCell
  bne Done
  lda RgTempY
  clc
  adc #16
  sta RgTempY
  cmp R6
  bcc Loop
  beq Loop
  lda R2
  sec
  sbc #7
  sta Player_Y_Position
  lda #0
  sta MmYFraction
  sta MmYFraction+1
  lda XgJumpUsed
  beq KeepVY
  lda #0
  sta MmVY+2
  sta Player_Y_Speed
  lda #$55
  sta MmVY
  lda #$d5
  sta MmVY+1
KeepVY:
::RyuCornerHeadResolved:
  lda #Sfx_Bump
  ora Square1SoundQueue
  sta Square1SoundQueue
  farcall RyuPlatformBox
Done:
  rts
; RgTempX/Page/Y bounded world cell -> raw block buffer, no row wrapping.
ReadCell:
  lda RgTempY
  sec
  sbc #32
  sta R0
  lda RgTempX
  lsr
  lsr
  lsr
  lsr
  clc
  adc R0
  sta R0
  lda RgTempPage
  and #1
  beq First
  lda R0
  clc
  adc #208
  sta R0
  lda #>Block_Buffer_1
  adc #0
  jmp Ptr
First:
  lda #>Block_Buffer_1
Ptr:
  sta R1
.assert <Block_Buffer_1=0,error,"Raw cell pointer requires page-aligned buffer"
  ldy #0
  lda (R0),y
  rts
.endproc
RyuCornerHeadEnd:
.assert RyuCornerHeadEnd-RyuCornerHeadStart<=512,error,"Ryu cold budget512"
.popseg
