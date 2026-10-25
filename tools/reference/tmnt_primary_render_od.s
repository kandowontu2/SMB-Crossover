; Private primary-weapon call: X is the native weapon pose, Ptr was just
; loaded from its facing table, and R4/R5/R6 hold its screen origin.
; Immutable descriptors are baked into ordered stores by the generator.
.pushseg
.segment "TMNT_COMBAT"
.proc TnPrimaryRender
 lda #1
 sta R7
 lda #0
 sta R3
.if ::MAPPER_MMC3
 farcall MetaspriteRenderLoop,jmp
.else
 cpx #31
 jcs Legacy
 lda CurrentBankC
 cmp #$d8
 jne Legacy
 lda R5
 jne Legacy
 lda R4
 cmp #20
 jcc Legacy
 cmp #244
 jcs Legacy
 lda R6
 cmp #24
 jcc Legacy
 cmp #248
 jcs Legacy
 lda PlayerFacingDir
 cmp #2
 bne Index
 txa
 ora #32
 tax
Index:
 lda TnPrimaryPtrLo,x
 cmp R0
 jne Legacy
 lda TnPrimaryPtrHi,x
 cmp R1
 jne Legacy
 ldy #0
 lda (R0),y
 beq Empty
 clc
 adc CurrentOAMOffset
 jcs Legacy
 ; RTS consumes this synthetic target immediately; the caller's real
 ; return address stays below it. No foreground scratch pointer is borrowed.
 lda TnPrimaryCodeHi,x
 pha
 lda TnPrimaryCodeLo,x
 pha
 ldx CurrentOAMOffset
 ldy GuestOamRotationActive
 beq Dispatch
 txa
 clc
 adc RgOamRotation
 tax
Dispatch:rts
Empty:
 ldx CurrentOAMOffset
 ldy #0
 lda #0
 clc
 rts
Legacy:
 farcall MetaspriteRenderLoop,jmp
.endif
.endproc
.export TnPrimaryRender
.include "tmnt_primary_records.inc"
.popseg
