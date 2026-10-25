; Menu preferences survive a life/area reset, and reset only on power/reset.
; Invincibility gates enemy/hazard injury, not pits or the stage timer.
.pushseg
.segment "SRAM"
CheatInvincible: .res 1
CheatStartLevel: .res 1             ; Low5: world*4+stage. Bit5: user changed it.

.segment "CHEATS_MENU_COLD"
.proc CheatsMenuInput
  lda CrossoverMenuPressed
  and #B_Button
  beq Navigate
  lda #3                          ; Rebuild the parent Options page.
  sta CrossoverMenuState
  lda #1
  sta DisableScreenFlag
  rts
Navigate:
  lda CrossoverMenuPressed
  and #Up_Dir | Down_Dir
  beq Change
  lda CrossoverOptionsFocus
  eor #1
  sta CrossoverOptionsFocus
  jmp Changed
Change:
  lda CrossoverMenuPressed
  and #A_Button | Start_Button | Select_Button | Left_Dir | Right_Dir
  beq Done
  lda CrossoverOptionsFocus
  bne Level
  lda CheatInvincible
  eor #1
  sta CheatInvincible
  jmp Changed
Level:
  lda CrossoverMenuPressed
  and #Left_Dir
  beq Forward
  dec CheatStartLevel
  jmp Wrap
Forward:
  inc CheatStartLevel
Wrap:
  lda CheatStartLevel
  and #31
  ora #$20
  sta CheatStartLevel
Changed:
  lda #Sfx_CoinGrab
  sta Square2SoundQueue
  jsr QueueCheats
Done:
  rts
.endproc

.proc QueueCheats
  lda #$21
  sta R1
  lda #$65
  sta R0
  ldy #0
  lda CheatInvincible
  beq :+
    ldy #22
  :
  jsr Line
  lda #$22
  sta R1
  lda #$05
  sta R0
  ldy #44
  jsr Line
  lda CheatStartLevel
  and #31
  lsr
  lsr
  clc
  adc #1
  sta VRAM_Buffer1-5,x
  lda CheatStartLevel
  and #3
  clc
  adc #1
  sta VRAM_Buffer1-3,x
  lda #2
  sta R4
  jmp QueueOptionCursor
Line:
  ldx VRAM_Buffer1_Offset
  lda R1
  sta VRAM_Buffer1,x
  lda R0
  sta VRAM_Buffer1+1,x
  lda #22
  sta VRAM_Buffer1+2,x
  sta R2
Copy:
  lda Text,y
  sta VRAM_Buffer1+3,x
  iny
  inx
  dec R2
  bne Copy
  inx
  inx
  inx
  stx VRAM_Buffer1_Offset
  lda #0
  sta VRAM_Buffer1,x
  rts
Text:
  .byte "INVINCIBLE       OFF  "
  .byte "INVINCIBLE       ON   "
  .byte "START LEVEL      1-1  "
.endproc

.proc CheatsPatchPage
  lda PPUSTATUS
  lda #$20
  sta PPUADDR
  lda #$cb
  sta PPUADDR
  ldx #0
Header:
  lda Title,x
  sta PPUDATA
  inx
  cpx #7
  bne Header
  lda #$22
  sta PPUADDR
  lda #$63
  sta PPUADDR
  lda #$24
  ldx #24                         ; Remove the parent's static Cheats row.
Blank:
  sta PPUDATA
  dex
  bne Blank
  rts
Title: .byte "CHEATS "
.endproc

.proc CheatsApplyStartingLevel
  lda CheatStartLevel
  and #$20
  beq Done                        ; Unused level cheat retains native start/continue.
  lda CheatStartLevel
  and #31
  tax
  lsr
  lsr
  sta WorldNumber
  sta OffScr_WorldNumber
  txa
  and #3
  sta LevelNumber
  sta OffScr_LevelNumber
  lda Areas,x
  sta AreaNumber
  sta OffScr_AreaNumber
  lda #0
  sta HalfwayPage
  sta OffScr_HalfwayPage
  sta AltEntranceControl
  sta CrossoverContinue
Done:
  rts
Areas:
  .byte 0,1,3,4, 0,1,3,4, 0,1,2,3, 0,1,3,4
  .byte 0,1,2,3, 0,1,2,3, 0,1,3,4, 0,1,2,3
.endproc

; Relocated rare native cleanup. R0 was saved by its original resident entry.
.proc CheatsNativeKillEnemies
  lda #0
  ldx #4
Loop:
  ldy Enemy_ID,x
  cpy R0
  bne :+
    sta EnemyMetasprite,x
    sta EnemyVerticalFlip,x
    sta Enemy_Flag,x
  :
  dex
  bpl Loop
  jsr BillNativeCaptureP
.if ::MAPPER_MMC3
  txa
  pha
  tsx
  lda $0107,x
  sta BillNativeReturnSelector
  pla
  tax
  lda BillNativeReturnSelector
.else
  lda #0
  sta BillNativeReturnSelector
.endif
  rts
.endproc
.assert * <= $c000,error,"Cheats menu exceeds its reserved bank14 A tail"
.popseg
