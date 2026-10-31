; Source-only campaign data loader, stable C65 execution. A=profile0..3.
; Exclusive physical WRAM4,64KiB private header. No code is executed from RAM4.
; The caller owns C mapping, scratch saves and forced-blank transition.
.assert *=$c738,lderror,"Campaign loader must use only verified Proto filler"
J2CacheResidentStart:
.proc J2LoadCache
 cmp #4
 bcc J2Allowed
J2Decline:
 lda #0
 clc
 rts
J2Allowed:
 tax
 lda DisableScreenFlag
 beq J2Decline
 lda Mirror_PPUMASK
 and #$18
 bne J2Decline
 lda NmiDisable
 bpl J2Decline
 lda CurrentBank
 pha
 txa
 pha
 lda #4
 sta CurrentBank
 sta MMC5_PRG_BANK_A
 lda #0
 sta $bfe0
 lda Mirror_PPUCTRL
 and #$fb
 sta PPUCTRL
 lda #1
 sta $5130
 lda J2LoadPage,x
 ldy #0
J2Map:
 sta $5120,y
 clc
 adc #1
 iny
 cpy #8
 bne J2Map
 bit PPUSTATUS
 lda J2LoadHigh,x
 sta PPUADDR
 lda J2LoadLow,x
 sta PPUADDR
 lda PPUDATA
 jsr J2DecodeCache
 lda #0
 adc #0
 tay
 pla
 tax
 tya
 beq J2Failure
 txa
 asl
 asl
 asl
 asl
 tax
 ldy #1
 inx
J2Cookie:
 lda J2CacheCookies,x
 sta $bfe0,y
 cmp $bfe0,y
 bne J2Failure
 inx
 iny
 cpy #16
 bne J2Cookie
 lda #$a7
 sta $bfe0
 cmp $bfe0
 bne J2Failure
 lda #1
 bne J2Restore
J2Failure:
 lda #0
 sta $bfe0
J2Restore:
 tax
 pla
 sta CurrentBank
 sta MMC5_PRG_BANK_A
 txa
 pha
 farcall X5PublishChr
 lda Mirror_PPUCTRL
 sta PPUCTRL
 bit PPUSTATUS
 lda HorizontalScroll
 sta PPUSCROLL
 lda VerticalScroll
 sta PPUSCROLL
 pla
 lsr
 lda #0
 rts
.endproc
.include "smb2j_cache_decoder_1031_v1.inc"
.include "smb2j_cache_tables.inc"
J2CacheResidentEnd:
.assert J2CacheResidentEnd <= $d108,lderror,"Campaign loader exceeds Proto filler"
