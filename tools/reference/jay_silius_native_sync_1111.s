; Import host horizontal separation and actual native25 carrying before the
; next original movement update. Native foot-seam flags do not prove support.
.setcpu "6502"
.segment "HANDOFF"

ImportNativePosition:
 lda XHi
 ldx XLo
 jsr Q4ToPixels
 cmp PlayerPage
 bne ImportNativeX
 cpx PlayerX
 beq CheckNativeY
ImportNativeX:
 lda XLo
 and #15
 sta Temp
 lda PlayerPage
 sta XHi
 lda PlayerX
 ldx #4
NativeXToQ4:
 asl A
 rol XHi
 dex
 bne NativeXToQ4
 ora Temp
 sta XLo
CheckNativeY:
 lda PlayerState
 bne NativeImportDone
 lda PlayerYSpeed
 bne NativeImportDone
 lda PlayerYPage
 cmp #1
 bne NativeImportDone
 ldx #5
FindNativeSupport:
 lda EnemyFlag,x
 cmp #1
 bne NextNativeSupport
 lda EnemyID,x
 cmp #$25
 bne NextNativeSupport
 txa
 cmp PlatformContact,x
 bne NextNativeSupport
 lda EnemyYPage,x
 cmp #1
 bne NextNativeSupport
 lda PlayerY
 clc
 adc #32
 bcs NextNativeSupport
 cmp EnemyY,x
 beq ImportNativeY
NextNativeSupport:
 dex
 bpl FindNativeSupport
 rts
ImportNativeY:
 lda PlayerY
 clc
 adc #16
 sta Temp
 lda PlayerYPage
 sbc #0
 sta YHi
 lda Temp
 ldx #4
NativeYToQ4:
 asl A
 rol YHi
 dex
 bne NativeYToQ4
 sta YLo
 lda DonorFlags
 and #$fb
 sta DonorFlags
 lda #0
 sta DonorVY
NativeImportDone:
 rts
