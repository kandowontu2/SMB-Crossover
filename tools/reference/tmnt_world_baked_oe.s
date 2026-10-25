; Immutable source world records, proved inside the visible coordinate page.
; The original renderer owns all unsupported records and clipped draws.
.pushseg
.segment "TMNT_CORE"
.proc TnWorldBakedRender
 lda R5
 jne Legacy
 lda R7
 cmp #1
 jne Legacy
 lda R4
 cmp #8
 jcc Legacy
 lda R6
 cmp #24
 jcc Legacy
 lda R3
 and #3
 jne Legacy
 lda CurrentBankC
 cmp #$d8
 jne Legacy
 lda R1
 cmp #$d1
 jcc Legacy
 cmp #$d4
 jcs Legacy
 asl
 asl
 eor R0
 tax
 ; Hash = low XOR (high*4). It is collision-free for the26 source pointers.
 ; Matching high plus hash also proves low. Invalid entries have high0.
 lda TnWorldExpectedHigh,x
 cmp R1
 jne Legacy
 ldy #0
 lda (R0),y
 clc
 adc CurrentOAMOffset
 jcs Legacy
 lda TnWorldCodeHi,x
 pha
 lda TnWorldCodeLo,x
 pha
 ldx CurrentOAMOffset
 ldy GuestOamRotationActive
 beq Dispatch
 txa
 clc
 adc RgOamRotation
 tax
Dispatch:rts
Legacy:
 jmp TnFastWorldRender
.endproc
.export TnWorldBakedRender
.include "tmnt_world_baked_records.inc"
.popseg
