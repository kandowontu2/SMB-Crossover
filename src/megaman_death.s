.pushseg
.segment "FIXED"
.proc MegaManDeathStart
  lda SelectedCharacter
  cmp #CHARACTER_LUIGI
  beq Done
  lda MmDeathFlag
  bne Done
  lda CurrentBank
  pha
.if ::MAPPER_MMC3
  lda #7 | PRG_FIXED_8
  sta BankShadow
  sta BANK_SELECT
  lda #.bank(UnionDeathStartCore)
  sta CurrentBank
  sta BANK_DATA
.else
  lda #.bank(UnionDeathStartCore) | MMC5_PRG_ROM
  sta CurrentBank
  sta MMC5_PRG_BANK_A
.endif
  jsr UnionDeathStartCore
  jsr BillNativeCaptureP
.if ::MAPPER_MMC3
  lda #7 | PRG_FIXED_8
  sta BankShadow
  sta BANK_SELECT
  pla
  sta CurrentBank
  sta BANK_DATA
.else
  pla
  sta CurrentBank
  sta MMC5_PRG_BANK_A
.endif
  jmp BillNativeRestoreP
Done:
  rts
.endproc
.pushseg
.segment "LEVEL"
.proc UnionDeathStartCore
  lda #1
  sta MmDeathFlag
  farcall InventoryDeath
  lda #0
  sta MmDeathAge
  sta MmDeathPit
  sta MmChargeFrames
  sta StarInvincibleTimer
  lda Player_X_Position
  clc
  adc #8
  sta MmDeathX
  lda Player_PageLoc
  adc #0
  sta MmDeathPage
  lda #20
  ldy Player_State
  beq :+
    lda #18
  :
  ldy MmSliding
  beq :+
    lda #24
  :
  clc
  adc Player_Y_Position
  sta MmDeathY
  lda Player_Y_HighPos
  adc #0
  sta MmDeathYHigh
  lda #0
  sta PlayerStatus
  sta MmSliding
  sta Player_X_Speed
  sta SmBall
  sta SmShootPose
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  bne Done
  lda SmSfx
  ora #64
  sta SmSfx
Done:
  rts
.endproc
.popseg

.if ::MAPPER_MMC5
  .repeat 6
    .byte $ea
  .endrepeat
.endif ; Restore all subsequent fixed/audio entry addresses literally.
.if ::MAPPER_MMC3
  ; Three old padding bytes fund the combined resident additions.
.endif
.proc MegaManCheckPit
  php
  pha
  lda SelectedCharacter
  beq Done
  cmp #CHARACTER_LUIGI
  beq Done                      ; Native PlayerHole handles Mario-style falling.
  lda Player_Y_HighPos
  bmi Done                       ; Signed pages above the screen are not a pit.
  cmp #1
  bcc Done
  bne Fall
  lda Player_Y_Position
  cmp #241
  bcc Done
Fall:
  jsr MegaManDeathStart
  lda #1
  sta MmDeathPit
  sta EventMusicQueue
  sta DeathMusicLoaded
  lda #$0b
  sta GameEngineSubroutine
  lda #$ff
  sta TimerControl
Done:
  pla
  plp
  rts
.endproc

.segment "GUEST"
.proc MegaManDeathUpdate
  inc MmDeathAge
  ldy #150                        ; pit: 2500 ms
  lda MmDeathPit
  bne :+
    ldy #168                      ; normal: 300 ms separation + 2500 ms
  :
  tya
  cmp MmDeathAge
  beq EndDeath
  bcs Done
EndDeath:
  lda #6
  sta GameEngineSubroutine
  lda #0
  sta TimerControl
Done:
  rts
.endproc

.segment "METASPRITE"
.proc MegaManDrawDeath
  lda MmDeathPit
  jne Done
  ; Bass shares the source particle burst, whose metasprites live in the
  ; Mega Man bank rather than the current character's graphics bank.
  BankPRGC #.bank(MmMM_PARTICLE_1Right)
  lda CurrentOAMOffset
  pha
  lda #0
.if ::MOUSE_DISPLAY_CURSOR
  lda #2 * 4
.endif
  sta CurrentOAMOffset
  lda #CHR_MM_DEATH
  cmp PlayerChrBank
  beq :+
    sta PlayerChrBank
    inc ReloadCHRBank
  :
  lda MmDeathAge
  lsr
  and #3
  clc
  adc #METASPRITE_MM_PARTICLE_1
  sta MmDeathMetasprite
  ldx #11
Loop:
  stx MmDeathPart
  ldy MmDeathAge
  cpx #4
  bcs Outer
  lda InnerDistance,y
  sta MmDeathDistance
  lda #0
  beq DistanceHigh
Outer:
  lda OuterDistanceLo,y
  sta MmDeathDistance
  lda OuterDistanceHi,y
DistanceHigh:
  sta MmDeathDistance+1
  lda MmDeathX
  sec
  sbc ScreenLeft_X_Pos
  sta R4
  lda MmDeathPage
  sbc ScreenLeft_PageLoc
  sta R5
  lda DirectionX,x
  beq Vertical
  bmi Left
  clc
  lda R4
  adc MmDeathDistance
  sta R4
  lda R5
  adc MmDeathDistance+1
  jmp StoreXHigh
Left:
  sec
  lda R4
  sbc MmDeathDistance
  sta R4
  lda R5
  sbc MmDeathDistance+1
StoreXHigh:
  sta R5
Vertical:
  lda MmDeathY
  sta R6
  lda MmDeathYHigh
  sta R7
  lda DirectionY,x
  beq Draw
  bmi Up
  clc
  lda R6
  adc MmDeathDistance
  sta R6
  lda R7
  adc MmDeathDistance+1
  jmp StoreYHigh
Up:
  sec
  lda R6
  sbc MmDeathDistance
  sta R6
  lda R7
  sbc MmDeathDistance+1
StoreYHigh:
  sta R7
Draw:
  ldy MmDeathMetasprite
  lda MetaspriteTableRightLo,y
  sta R0
  lda MetaspriteTableRightHi,y
  sta R1
  lda #0
  sta R3
  jsr MetaspriteRenderLoop
  ldx MmDeathPart
  dex
  jpl Loop
  pla
  sta CurrentOAMOffset
Done:
  rts
DirectionX:
  .byte 0,0,-1,1, 0,1,1,1,0,-1,-1,-1
DirectionY:
  .byte -1,1,0,0, -1,-1,0,1,1,1,0,-1
InnerDistance:
  .repeat 169,I
    .if I>18
      .byte 5+((I-18)*5)/4
    .else
      .byte 5
    .endif
  .endrepeat
OuterDistanceLo:
  .repeat 169,I
    .if I>18
      .byte <(5+((I-18)*55)/24)
    .else
      .byte 5
    .endif
  .endrepeat
OuterDistanceHi:
  .repeat 169,I
    .if I>18
      .byte >(5+((I-18)*55)/24)
    .else
      .byte 0
    .endif
  .endrepeat
.endproc
.popseg
