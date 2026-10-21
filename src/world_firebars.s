; Firebar collision remains native. Cache its parts until the final OAM pass,
; after guest sprite clearing, and use CHR independent of the player bank.
.pushseg
.segment "SRAM"
FirebarPartCount: .res 6
FirebarPartX: .res 72
FirebarPartY: .res 72
FirebarSlot: .res 1
FirebarPart: .res 1
FirebarIndex: .res 1
FirebarTemp: .res 1

.segment "OBJECT"
.proc CacheFirebarPart
  phy
  lda FirebarPartCount,x
  cmp #12
  bcs Done
  txa
  asl
  sta FirebarTemp
  asl
  clc
  adc FirebarTemp
  asl
  clc
  adc FirebarPartCount,x
  tay
  lda R6
  sta FirebarPartX,y
  lda R7
  sta FirebarPartY,y
  inc FirebarPartCount,x
Done:
  ply
  rts
.endproc

.segment "BILL_GFX"
FirebarSprite1:
  .byte 4
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_1}, 2,-4,0
FirebarSprite2:
  .byte 4
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_1}, 2,-4,0

.segment "OBJECT_EX"
.proc DrawWorldFirebars
  lda CurrentBankC
  pha
  BankPRGC #.bank(FirebarSprite1)
  lda #5
  sta FirebarSlot
Slot:
  ldx FirebarSlot
  lda Enemy_Flag,x
  jeq NextSlot
  jmi NextSlot                    ; Long-bar duplicate is not another owner.
  lda Enemy_ID,x
  cmp #$1b
  jcc NextSlot
  cmp #$23
  jcs NextSlot
  lda FirebarPartCount,x
  jeq NextSlot
  cmp #13
  jcs NextSlot
  txa
  asl
  sta FirebarTemp
  asl
  clc
  adc FirebarTemp
  asl
  sta FirebarIndex
  lda #0
  sta FirebarPart
Part:
  ldy FirebarIndex
  lda FirebarPartY,y
  cmp #32
  jcc NextPart
  cmp #240
  jcs NextPart
  sta R6
  lda FirebarPartX,y
  sta R4
  lda #0
  sta R5
  lda #1
  sta R7
  lda FrameCounter
  and #8
  beq :+
    lda #$c0
  :
  sta R3
  lda #<FirebarSprite1
  ldx #>FirebarSprite1
  ldy FrameCounter
  tya
  and #4
  beq :+
    lda #<FirebarSprite2
    ldx #>FirebarSprite2
    bne Pointer
  :
  lda #<FirebarSprite1
Pointer:
  sta R0
  stx R1
  farcall MetaspriteRenderLoop
NextPart:
  inc FirebarIndex
  inc FirebarPart
  ldx FirebarSlot
  lda FirebarPart
  cmp FirebarPartCount,x
  jcc Part
NextSlot:
  dec FirebarSlot
  jpl Slot
::WorldFirebarsOamReady:
  pla
  BankPRGC a
  rts
.endproc
.popseg
