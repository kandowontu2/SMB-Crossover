; Expanded MMC5 ABI: 15 bytes in the existing SRAM alignment gap.
; Integrators must reserve this range alongside all optional profile/helper state.
X5ChrMode=$73e0
X5SpecialChrUpper=$73ec
X5HudChrUpper=$73ed
X5WideChrActive=$73ee
.assert X5WideChrActive<$7400,error,"Existing aligned XgLzHistory stays fixed"
.export X5ChrMode,X5SpecialChrUpper,X5HudChrUpper,X5WideChrActive,X5PublishChr,X5ColdInit
.export X5SetPhysicalChr,X5SetSpecialChr,X5ClearChrModes
.pushseg
.segment "X5_PUBLISH"
X5ColdInit:
  lda #0
  sta RlOutlineBypass
  sta $5130
  sta $5200                       ; manual native scroll IRQ, no vertical-split region
  lda #2
  sta $5104                       ; CPU R/W ExRAM; all nametables still use CIRAM ($44).
  lda #0
  ldx #15
X5ClearMenuVariants:
  sta X5MenuVariants,x
  dex
  bpl X5ClearMenuVariants
  sta X5SpecialChrUpper
  sta X5HudChrUpper
  sta X5WideChrActive
  ldx #0
X5InitLoop:
  lda #0
  sta X5ChrMode,x
  lda CHRBankInitValues,x
  sta CurrentCHRBank,x
  tay
  lda ChrPhysicalMap,y
  sta $5120,x
  inx
  cpx #12
  bcc X5InitLoop
  rts
X5PublishChr:
  lda X5WideChrActive
  jne X5WidePublication
  lda #0
  sta $5130
 .scope X5LegacyPublication
  .repeat 12, I
    lda CurrentCHRBank + I
.if ::ENABLE_CROSSOVER
    tay
    lda ChrPhysicalMap,y
.if I = 8
    ldy InvHudActive
    beq HudChrDone
      lda InvHudPhysical
HudChrDone:
.endif
.if I = 4
    ldy SsChrActive
    beq SpecialChrDone
      lda SsChrPhysical
SpecialChrDone:
.endif
.endif
    sta MMC5_CHR_BANK_BASE + I
  .endrepeat
  rts
 .endscope
X5WidePublication:
  lda X5ChrMode+0
  bmi X5Direct0
  lda #0
  sta $5130
  lda CurrentCHRBank+0
  tay
  lda ChrPhysicalMap,y
  jmp X5Write0
X5Direct0:
  and #3
  sta $5130
  lda CurrentCHRBank+0
X5Write0:
  sta $5120
  lda X5ChrMode+1
  bmi X5Direct1
  lda #0
  sta $5130
  lda CurrentCHRBank+1
  tay
  lda ChrPhysicalMap,y
  jmp X5Write1
X5Direct1:
  and #3
  sta $5130
  lda CurrentCHRBank+1
X5Write1:
  sta $5121
  lda X5ChrMode+2
  bmi X5Direct2
  lda #0
  sta $5130
  lda CurrentCHRBank+2
  tay
  lda ChrPhysicalMap,y
  jmp X5Write2
X5Direct2:
  and #3
  sta $5130
  lda CurrentCHRBank+2
X5Write2:
  sta $5122
  lda X5ChrMode+3
  bmi X5Direct3
  lda #0
  sta $5130
  lda CurrentCHRBank+3
  tay
  lda ChrPhysicalMap,y
  jmp X5Write3
X5Direct3:
  and #3
  sta $5130
  lda CurrentCHRBank+3
X5Write3:
  sta $5123
  ldy SsChrActive
  beq X5Default4
  lda X5SpecialChrUpper
  and #3
  sta $5130
  lda SsChrPhysical
  jmp X5Write4
X5Default4:
  lda X5ChrMode+4
  bmi X5Direct4
  lda #0
  sta $5130
  lda CurrentCHRBank+4
  tay
  lda ChrPhysicalMap,y
  jmp X5Write4
X5Direct4:
  and #3
  sta $5130
  lda CurrentCHRBank+4
X5Write4:
  sta $5124
  lda X5ChrMode+5
  bmi X5Direct5
  lda #0
  sta $5130
  lda CurrentCHRBank+5
  tay
  lda ChrPhysicalMap,y
  jmp X5Write5
X5Direct5:
  and #3
  sta $5130
  lda CurrentCHRBank+5
X5Write5:
  sta $5125
  lda X5ChrMode+6
  bmi X5Direct6
  lda #0
  sta $5130
  lda CurrentCHRBank+6
  tay
  lda ChrPhysicalMap,y
  jmp X5Write6
X5Direct6:
  and #3
  sta $5130
  lda CurrentCHRBank+6
X5Write6:
  sta $5126
  lda X5ChrMode+7
  bmi X5Direct7
  lda #0
  sta $5130
  lda CurrentCHRBank+7
  tay
  lda ChrPhysicalMap,y
  jmp X5Write7
X5Direct7:
  and #3
  sta $5130
  lda CurrentCHRBank+7
X5Write7:
  sta $5127
  ldy InvHudActive
  beq X5Default8
  lda X5HudChrUpper
  and #3
  sta $5130
  lda InvHudPhysical
  jmp X5Write8
X5Default8:
  lda X5ChrMode+8
  bmi X5Direct8
  lda #0
  sta $5130
  lda CurrentCHRBank+8
  tay
  lda ChrPhysicalMap,y
  jmp X5Write8
X5Direct8:
  and #3
  sta $5130
  lda CurrentCHRBank+8
X5Write8:
  sta $5128
  lda X5ChrMode+9
  bmi X5Direct9
  lda #0
  sta $5130
  lda CurrentCHRBank+9
  tay
  lda ChrPhysicalMap,y
  jmp X5Write9
X5Direct9:
  and #3
  sta $5130
  lda CurrentCHRBank+9
X5Write9:
  sta $5129
  lda X5ChrMode+10
  bmi X5Direct10
  lda #0
  sta $5130
  lda CurrentCHRBank+10
  tay
  lda ChrPhysicalMap,y
  jmp X5Write10
X5Direct10:
  and #3
  sta $5130
  lda CurrentCHRBank+10
X5Write10:
  sta $512a
  lda X5ChrMode+11
  bmi X5Direct11
  lda #0
  sta $5130
  lda CurrentCHRBank+11
  tay
  lda ChrPhysicalMap,y
  jmp X5Write11
X5Direct11:
  and #3
  sta $5130
  lda CurrentCHRBank+11
X5Write11:
  sta $512b
  pha
  lda #0
  sta $5130
  pla
  rts
; Called only while the new profile owns a private GameLoop frame.
; A=physical low8, X=upper2, Y=hardware window0..11. No persistent scratch.
X5SetPhysicalChr:
  sta CurrentCHRBank,y
  txa
  and #3
  ora #$80
  sta X5ChrMode,y
  lda #1
  sta X5WideChrActive
  sta ReloadCHRBank
  rts
; Selected weapon art uses the existing direct override at sprite window4.
; A=physical low8 (the actual1KB window, not a2KB pair), X=upper2.
X5SetSpecialChr:
  sta SsChrPhysical
  txa
  and #3
  sta X5SpecialChrUpper
  lda #1
  sta SsChrActive
  sta X5WideChrActive
  sta ReloadCHRBank
  rts
; Select a legacy profile, then rebuild its ordinary body/window bytes in the
; same private frame before it is released to NMI. A/X/P volatile, Y preserved.
X5ClearChrModes:
  lda #0
  ldx #11
X5ClearLoop:
  sta X5ChrMode,x
  dex
  bpl X5ClearLoop
  sta X5SpecialChrUpper
  sta X5HudChrUpper
  sta X5WideChrActive
  lda #1
  sta ReloadCHRBank
  rts
.popseg
