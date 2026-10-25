; Three private projectile slots rotate admission. Native enemy windows stay native.
.pushseg
.segment "KIRBY_ABILITIES"
.proc KbDrawShots
  BankPRGC #.bank(KbArtStart)
  lda SmChrBank
  ldx #>KB_FIRST_CHR
  ldy #0
  farcall X5SetPhysicalChr
  lda GameEngineSubroutine
  cmp #8
  jne Done
  lda MmDeathFlag
  jne Done
  inc KbDrawFirst
  lda KbDrawFirst
  cmp #3
  bcc :+
    lda #0
    sta KbDrawFirst
  :
  tax
  lda #3
  sta KbDrawCount
Loop:
  stx KbSavedSlot
  lda KbShotType,x
  jeq Next
  cmp #2
  jeq Air
  cmp #3
  jne Star
  lda KbShotKind,x
  cmp #2
  jeq NativeShell
  cmp #3
  jeq NativeShell
  cmp #5
  jeq NativeHammer
  cmp #11
  jeq NativeNeedle
  cmp #6
  jeq Air
  cmp #7
  jeq Air
  cmp #8
  jeq Air
  cmp #13
  jne Star
  lda KbShotAge,x
  lsr
  and #3
  clc
  adc #6
  jne Effect
NativeShell:
  tay
  dey
  lda KbCopyIconLo,y
  sta R0
  lda KbCopyIconHi,y
  sta R1
  jmp Position
NativeNeedle:
  lda #2
  jne NativePhase
NativeHammer:
  lda #0
NativePhase:
  sta KbTemp
  lda KbShotAge,x
  lsr
  lsr
  and #1
  clc
  adc KbTemp
  tay
  lda KbNativeShotLo,y
  sta R0
  lda KbNativeShotHi,y
  sta R1
  jmp Position
Air:
  lda KbShotAge,x
  lsr
  lsr
  and #1
  clc
  adc #4
  jne Effect
Star:
  lda KbShotAge,x
  lsr
  lsr
  and #3
Effect:
  tay
  lda KbEffectLo,y
  sta R0
  lda KbEffectHi,y
  sta R1
Position:
  lda KbShotX,x
  sec
  sbc ScreenLeft_X_Pos
  sta R4
  lda KbShotPage,x
  sbc ScreenLeft_PageLoc
  sta R5
  lda KbShotY,x
  sta R6
  lda KbShotType,x
  cmp #3
  bne ShotReady
  lda KbShotKind,x
  cmp #2
  beq CenterNative
  cmp #3
  beq CenterNative
  cmp #5
  beq CenterNative
  cmp #11
  bne ShotReady
CenterNative:
  sec
  lda R4
  sbc #8
  sta R4
  lda R5
  sbc #0
  sta R5
  sec
  lda R6
  sbc #8
  sta R6
ShotReady:
  jsr Draw
Next:
  dec KbDrawCount
  jeq Drop
  ldx KbSavedSlot
  inx
  cpx #3
  jcc Loop
  ldx #0
  jeq Loop
Drop:
  lda KbDropKind
  jeq Health
  lda KbClock
  lsr
  lsr
  and #3
  tay
  lda KbEffectLo,y
  sta R0
  lda KbEffectHi,y
  sta R1
  lda KbDropX
  sec
  sbc ScreenLeft_X_Pos
  sta R4
  lda KbDropPage
  sbc ScreenLeft_PageLoc
  sta R5
  lda KbDropY
  sta R6
  jsr Draw
Health:
  lda KbHealth
  sta KbTemp2
  lda #12
  sta $5c90
  ldy #0
HealthLoop:
  sty KbSavedSlot
  lda KbTemp2
  cmp #3
  bcc :+
    lda #2
  :
  tax
  lda KbHealthTiles,x
  sta KbTemp
  tya
  asl
  asl
  tax
  lda KbTemp
  sta $5c91,x
  lda #0
  sta $5c92,x
  sta $5c93,x
  tya
  asl
  asl
  asl
  sta $5c94,x
  lda KbTemp2
  sec
  sbc #2
  bcs :+
    lda #0
  :
  sta KbTemp2
  ldy KbSavedSlot
  iny
  cpy #3
  jcc HealthLoop
  lda #$90
  sta R0
  lda #$5c
  sta R1
  lda #80
  sta R4
  lda #0
  sta R5
  lda #7
  sta R6
  jsr Draw
  lda KbCopy
  jeq Done
  tax
  lda KbCopyIconLo-1,x
  sta R0
  lda KbCopyIconHi-1,x
  sta R1
  ; Keep even32px native enemy portraits in the empty left HUD margin.
  ; The old position covered the coin counter with tall copied enemies.
  lda #4
  sta R4
  lda #0
  sta R5
  lda #0
  sta R6
  jsr Draw
Done:
  rts
Draw:
  lda #1
  sta R7
  lda #0
  sta R3
  farcall MetaspriteRenderLoop
  rts
.endproc
.popseg

; Only this small bridge occupies existing bank4 slack; all art/code is cold.
.pushseg
.segment "X5_DRAW_GATE"
.proc KbDrawDispatch
  lda SelectedCharacter
  cmp #CHARACTER_KIRBY
  bcc CheckSimon
  farcall HotNewCharacterDraw,jmp
CheckSimon:
  cmp #CHARACTER_SIMON
  bne Legacy
  farcall Cv3DrawDispatch,jmp
Legacy:
  jmp Z2DrawGuard
  .assert *-KbDrawDispatch=50,error,"Expanded draw gate fits bank4 tail"
.endproc
.popseg



