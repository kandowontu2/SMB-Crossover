; Independent native pose leaf. Caller has authenticated both Prince banks.
; RenderX is signed screen X; RenderY is native page1 screen Y (pixelY+$100).
; Source frame/facing and exact source packet data supply every body pixel.
.setcpu "6502"
.macpack longbranch
.segment "RENDER"
.export PpHostDraw,PpRenderX,PpRenderY,PpRenderEnd,PpNativePacket
; The native emitter maps ROM into A000, so the packet must remain in C000.
; Exact53B of original OAM is dead in the recovered source instruction graph.
PpNativePacket=$c200
PpHostDraw:
 php
 pha
 txa
 pha
 tya
 pha
 ldx #0
SaveScratch:
 lda R0,x
 pha
 inx
 cpx #8
 bne SaveScratch
 ldx #0
SaveSmc:
 ldy SmcOffsets,x
 lda $0100,y
 pha
 inx
 cpx #5
 bne SaveSmc
 lda #0
 sta Handled
 lda CurrentOAMOffset
 and #3
 jne Done
 lda GuestOamRotationActive
 beq :+
 lda RgOamRotation
 and #3
 jne Done
:
 lda PpState+$617
 jeq Done
 cmp #239
 jcs Done
 asl
 tay
 lda #$c8
 adc #0
 sta OffsetLo+2
 sta OffsetHi+2
OffsetLo:lda $c800,y
 sta Read+1
OffsetHi:lda $c801,y
 cmp #$ff
 jeq Done
 clc
 adc #$c8
 sta Read+2
 ldy #0
 jsr Byte
 pha
 and #15
 asl
 asl
 sta PpNativePacket
 clc
 adc CurrentOAMOffset
 jcs BadHeader
 pla
 lsr
 lsr
 lsr
 lsr
 sta PageCount
 lda #0
 sta Window
Pages:
 jsr Byte
 tax
 tya
 pha
 lda PhysicalLo,x
 sta SafecallA_SMC+1
 lda PhysicalHi,x
 tax
 ldy Window
 lda #<X5SetPhysicalChr
 sta FarcallJmpTarget_SMC+1
 lda #>X5SetPhysicalChr
 sta FarcallJmpTarget_SMC+2
 lda #Bank_X5SetPhysicalChr
 jsr FarCallCommon
 pla
 tay
 inc Window
 dec PageCount
 bne Pages
 ; Publish original projection geometry using source coordinates. Physical
 ; renderY is deliberately independent of the source world's vertical origin.
 jsr Byte
 sta PpState+$70f
 jsr Byte
 pha
 clc
 adc PpState+$611
 sta PpState+$6f1
 pla
 sec
 sbc #3
 sta PpState+$4bc
 jsr Byte
 sta PpState+$4c3
 lda #1
 ldx PpState+$615
 beq :+
 lda #$41
:
 sta Attribute
 lda PpNativePacket
 sec
 sbc #3
 tax
Parts:
 jsr Byte
 sec
 sbc #1
 sta PpNativePacket+2,x
 jsr Byte
 sta PpNativePacket,x
 jsr Byte
 bit Attribute
 bvc :+
 eor #$ff
 clc
 adc #1
:
 sta PpNativePacket+3,x
 lda Attribute
 sta PpNativePacket+1,x
 dex
 dex
 dex
 dex
 bpl Parts
 lda #<PpNativePacket
 sta R0
 lda #>PpNativePacket
 sta R1
 lda #0
 sta R3
 ldx #3
:
 lda PpRenderX,x
 sta R4,x
 dex
 bpl :-
 lda #0
 sta SafecallA_SMC+1
 lda #<MetaspriteRenderLoop
 sta FarcallJmpTarget_SMC+1
 lda #>MetaspriteRenderLoop
 sta FarcallJmpTarget_SMC+2
 lda #Bank_MetaspriteRenderLoop
 jsr FarCallCommon
 inc Handled
 jmp Done
BadHeader:
 pla
Done:
 ldx #4
:
 pla
 ldy SmcOffsets,x
 sta $0100,y
 dex
 bpl :-
 ldx #7
:
 pla
 sta R0,x
 dex
 bpl :-
 lda Handled
 beq Rejected
 pla
 tay
 pla
 tax
 pla
 plp
 sec
 rts
Rejected:
 pla
 tay
 pla
 tax
 pla
 plp
 clc
 rts
Byte:
Read:lda $ffff,y
 iny
 rts
SmcOffsets:
 .byte <(NextBank_SMC+1),<(SafecallA_SMC+1),<(FarcallJmpTarget_SMC+1),<(FarcallJmpTarget_SMC+2),<(SafereturnA_SMC+1)
PpRenderX:.word 0
PpRenderY:.word 0
Handled:.byte 0
PageCount:.byte 0
Window:.byte 0
Attribute:.byte 0
PpRenderEnd:
