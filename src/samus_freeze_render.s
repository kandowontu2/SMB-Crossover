; Hard Samus freeze: local blue palette lease, source late40ms color epochs.
; Native CHR has three opaque indices: blue11/31/01 is an NES quantization,
; not four-ARGB or waveform/Flash-render parity. Software OAM bit4 is cleared
; before hardware DMA. Fair alternate opportunities preserve live palette1 owners.
.pushseg
.segment "BSS"
SmFreezePalettePacket: .res 7
SmFreezeVisible: .res 1
SmFreezeConflict: .res 1
SmFreezeBlue: .res 1
SmFreezePalettePending: .res 1 ; $EC/$ED belong to imported Metroid literal volume pointers.
.segment "SRAM"
SmFreezeRenderState: .res 1
SmFreezeTurn: .res 1
SmFreezePaletteControl: .res 1
SmFreezeLastBlue: .res 1
.segment "SAMUS_FREEZE_LOW"
; NMI-only: no foreground scratch, new pending byte only; no PRG/SMC writes.
.proc SamusFreezeUpdateScreen
  jsr UpdateScreen
  asl SmFreezePalettePending
  jmp SamusFreezeFlushPalette
.endproc
.segment "SAMUS_FREEZE_NMI"
.proc SamusFreezeFlushPalette
  bcc Done
  lda #<SmFreezePalettePacket
  sta NmiR0
  lda #>SmFreezePalettePacket
  sta NmiR1
  jmp UpdateScreen
Done:
  rts
.endproc
.segment "SAMUS_FREEZE_STORE"
; These stores occupy alignment padding, so BASS DPCM and every old PC stay.
.proc SamusFreezePaletteStoreA
  sta VRAM_Buffer_AddrCtrl
  sta SmFreezePaletteControl
  rts
.endproc
.proc SamusFreezePaletteStoreX
  stx VRAM_Buffer_AddrCtrl
  stx SmFreezePaletteControl
  rts
.endproc
.segment "INVENTORY"
.proc SamusFreezeInit
  inc InvDirty
  php
  pha
  phx
  phy
  lda #0
  sta SmFreezePalettePending
  sta SmFreezeRenderState
  sta SmFreezeTurn
  sta SmFreezePaletteControl
  sta SmFreezeLastBlue
  ldx #9
Clear:
  sta SmFreezePalettePacket,x
  dex
  bpl Clear
  ply
  plx
  pla
  plp
  rts
.endproc
.segment "LEGACY_COLD"
.proc SamusFreezeDebrisPosition
  lda DebrisPart
  and #2
  clc
  adc DebrisSlot
  tax
  lda Block_X_Position,x
  sec
  sbc ScreenLeft_X_Pos
  sta R4
  lda Block_PageLoc,x
  sbc ScreenLeft_PageLoc
  sta R5
  lda Block_Y_Position,x
  sta R6
  lda Block_Y_HighPos,x
  sta R7
  lda DebrisPart
  and #1
  beq PositionReady
  ldx DebrisSlot
  lda Block_Orig_XPos,x
  sec
  sbc ScreenLeft_X_Pos
  sta M0
  lda Block_PageLoc2,x
  sbc ScreenLeft_PageLoc
  sta M1
  asl M0
  rol M1
  sec
  lda M0
  sbc R4
  sta R4
  lda M1
  sbc R5
  sta R5
  clc
  lda R4
  adc #6
  sta R4
  lda R5
  adc #0
  sta R5
PositionReady:
  rts
.endproc
.proc SamusFreezeColorActor
  php
  pha
  phx
  phy
  lda CrossoverBehaviorVersion
  beq Done
  cpy #1
  bcc Done
  cpy #7
  bcs Done
  ; The native duplicate Bowser rear follows only a validated primary owner.
  lda Enemy_ID-1,y
  cmp #Bowser
  bne Owner
  lda Enemy_Flag-1,y
  bpl Owner
  and #$7f
  cmp #6
  bcs Done
  tay
  lda Enemy_ID,y
  cmp #Bowser
  bne Done
  lda Enemy_Flag,y
  beq Done
  bmi Done
  iny
Owner:
  lda AvFrozenHi-1,y
  bne Color
  lda AvFrozen-1,y
  beq Done
  cmp #76
  bcs Color
  tax
  lda LateColor,x
  beq Done
Color:
  lda R3
  ora #$10                    ; unused hardware attribute bit; no forced per-tile palette.
  sta R3
Done:
  ply
  plx
  pla
  plp
  rts
LateColor:
  .byte 1,0,0,0,1,1,0,0,1,1,1,0,0,1,1,1,0,0,1,1,0,0,0,1,1,0,0,0,1,1,0,0,1,1,1,0,0,1,1,1,0,0,1,1,0,0,0,1,1,0,0,0,1,1,0,0,1,1,1,0,0,1,1,1,0,0,1,1,0,0,0,1,1,0,0,0
.endproc
.proc SamusFreezeRenderFinish
  php
  pha
  phx
  phy
  lda #0
  sta SmFreezeVisible
  sta SmFreezeConflict
  sta SmFreezeBlue
  ldx #0
Scan:
  ; Four sequential OAM entries per iteration preserve exact bus-write order.
  .repeat 4, I
    .scope
      lda Sprite_Y_Position+I*4,x
      cmp #240
      bcs Next
      lda Sprite_Attributes+I*4,x
      and #$10
      beq Ordinary
      inc SmFreezeVisible
      bne Next
Ordinary:
      lda Sprite_Attributes+I*4,x
      and #3
      cmp #1
      bne Next
      inc SmFreezeConflict
Next:
    .endscope
  .endrepeat
  txa
  clc
  adc #16
  tax
  jne Scan
  lda SmFreezeVisible
  beq Paint
  lda SmFreezeConflict
  beq Blue
  lda SmFreezeTurn
  eor #1
  sta SmFreezeTurn
  beq Paint
Blue:
  inc SmFreezeBlue
Paint:
  ldx #0
Actor:
  .repeat 4, I
    .scope
      lda Sprite_Attributes+I*4,x
      and #$10
      beq NonFrozen
      lda Sprite_Attributes+I*4,x
      and #$ef
      sta Sprite_Attributes+I*4,x
      lda SmFreezeBlue
      beq Hide
      lda Sprite_Attributes+I*4,x
      and #$fc
      ora #1
      sta Sprite_Attributes+I*4,x
      jmp Advance
NonFrozen:
      lda SmFreezeBlue
      beq Advance
      lda Sprite_Attributes+I*4,x
      and #3
      cmp #1
      bne Advance
Hide:
      lda #$f8
      sta Sprite_Y_Position+I*4,x
Advance:
    .endscope
  .endrepeat
  txa
  clc
  adc #16
  tax
  jeq PaintDone
  jmp Actor
PaintDone:
  lda SmFreezeBlue
  cmp SmFreezeLastBlue
  bne Packet
CheckNativePalette:
  lda SmFreezeBlue
  beq State
  lda VRAM_Buffer_AddrCtrl
  cmp #1
  bcc State
  cmp #5
  bcc Packet
  cmp #8
  bne State
Packet:
  lda #$3f
  sta SmFreezePalettePacket
  lda #$15
  sta SmFreezePalettePacket+1
  lda #3
  sta SmFreezePalettePacket+2
  lda #0
  sta SmFreezePalettePacket+6
  lda SmFreezeBlue
  sta SmFreezeLastBlue
  beq Restore
  ldx #0
  beq Copy
Restore:
  ldx SmFreezePaletteControl
Copy:
  lda Color1,x
  sta SmFreezePalettePacket+3
  lda Color2,x
  sta SmFreezePalettePacket+4
  lda Color3,x
  sta SmFreezePalettePacket+5
  lda #$80                    ; publish only after whole packet and OAM are complete.
  sta SmFreezePalettePending
State:
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  bne Clear
  lda CrossoverBehaviorVersion
  beq Clear
  ldx #5
Frozen:
  lda AvFrozen,x
  ora AvFrozenHi,x
  bne Done
  dex
  bpl Frozen
Clear:
  lda #0
  sta SmFreezeRenderState
Done:
  ply
  plx
  pla
  plp
  rts
; Index0=lease;1..4=literal area palettes;8=actual Axe/Bowser override.
Color1: .byte $11,$10,$1a,$1c,$1c,$1a,$1a,$1a,$1a
Color2: .byte $31,$30,$30,$36,$36,$30,$30,$30,$30
Color3: .byte $01,$27,$27,$17,$17,$27,$27,$27,$27
.endproc
.popseg

; The original clear leaf supplies A=0 and subsequently reloads A=0. Keep its
; entire instruction span/PC fixed; only these two additional actor fields change.
; Enemy.as::die calls removeAllStatusEffects before removal (lines390..397).
.pushseg
.segment "SPECIAL_ROSTER"
.proc SamusFrozenClear
  sta RgShotHitsNow,x
  sta AvFrozen,x
  sta AvFrozenHi,x
  rts
.endproc
.popseg
