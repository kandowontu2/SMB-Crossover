; Original resident helper relocated without instruction changes.
.pushseg
.segment "ROLL_WORLD"
.proc RlOriginalFullShotBank
  lda #0
  sta MmFireBank
  ldx #3
Find:
  lda MmBulletType,x
  cmp #3
  beq Blue
  cmp #6
  bne Next
    lda #8
    bne Found
Blue:
  lda #0
Found:
  clc
  adc #$70
  sta MmFireBank
Next:
  dex
  bpl Find
.if ::MAPPER_MMC5
  lda #CHR_SPRITES+2
  ldx MmFireBank
  beq BankReady
    txa
    ora #1
BankReady:
  cmp CurrentCHRBank+4
  beq Done
    sta CurrentCHRBank+4
.else
  lda AreaType
  asl
  ldx MmFireBank
  beq Original
    txa                           ; All four area BG CHR images are identical.
    bne BankReady
Original:
  asl
  clc
  adc #2
BankReady:
  cmp AreaChrBank+1
  beq Done
    sta AreaChrBank+1
.endif
  inc ReloadCHRBank
Done:
  rts
.endproc
.popseg
