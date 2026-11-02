; Typed immutable helper tail of art441, copied to bank2D000..D3FF.
; Entry execution requires the authenticated bank2 mapping and bank3 actor.
.segment "BB_HELPERS"
.export BbHelperGraphics,BbHelperColors,BbHelperName,BbHelperPortrait,BbHelpersEnd
BbHelperGraphics:
 php
 pha
 lda #<441
 sta CurrentCHRBank+4
 lda #$81
 sta X5ChrMode+4
 lda #0
 sta SsChrActive
 sta ObjectMetasprite
 lda #<ObjectMetasprite
 sta SmPosePtr
 lda #>ObjectMetasprite
 sta SmPosePtr+1
 lda #1
 sta X5WideChrActive
 sta ReloadCHRBank
 pla
 plp
 sec
 rts

BbHelperPortrait:
 jsr BbNativeFresh
 jsr BbHelperGraphics
 jmp BbNativeDraw

BbHelperColors:
 php
 pha
 txa
 pha
 tya
 pha
 ldy #0
 ldx #6
 bne BbHelperQueue
BbHelperName:
 php
 pha
 txa
 pha
 tya
 pha
 lda OperMode
 beq BbHelperMenuName
 ldy #12
 ldx #10
 bne BbHelperQueue
BbHelperMenuName:
 ldy #32
 ldx #19
BbHelperQueue:
 lda R0
 pha
 stx R0
 ldx VRAM_Buffer1_Offset
 cpx #$2d
 bcs BbHelperQueueDone
 lda $c300
 beq BbHelperCopy
 tya
 clc
 adc R0
 tay
BbHelperCopy:
 lda BbHelperPackets,y
 sta VRAM_Buffer1,x
 inx
 iny
 dec R0
 bne BbHelperCopy
 lda #0
 sta VRAM_Buffer1,x
 stx VRAM_Buffer1_Offset
BbHelperQueueDone:
 pla
 sta R0
 pla
 tay
 pla
 tax
 pla
 plp
 sec
 rts
BbHelperPackets:
 ; Write only opaque RGB entries; the native backdrop is retained.
 .byte $3f,$1d,3,$2a,$26,$30,$3f,$11,3,$2c,$23,$30
 .byte $20,$43,7,$0b,$1e,$0b,$24,$24,$24,$24
 .byte $20,$43,7,$0b,$18,$0b,$24,$24,$24,$24
 ; Actual current FmQueueName packet: address2328,width16,space24.
 .byte $23,$28,16,$24,$24,$24,$24,$24,$24,$0b,$1e,$0b,$24,$24,$24,$24,$24,$24,$24
 .byte $23,$28,16,$24,$24,$24,$24,$24,$24,$0b,$18,$0b,$24,$24,$24,$24,$24,$24,$24
BbHelpersEnd:
