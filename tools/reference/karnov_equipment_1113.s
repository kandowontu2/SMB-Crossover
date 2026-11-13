; Unallocated native-table reader prototype for the Ladder adapter.
; Caller executes in authenticated RAM3, with its source C2 state banked at C.
; The original native metatile tables are PRG3 at A, so alias that same ROM
; bank at C only while reading. No source-state access is legal in the loan.
; X is the existing native VRAM1 command offset; Y is the saved metatile ID.
; A/P are consumed, X/Y and the mapped C owner are retained. Native foreground
; caller owns its VRAM reservation and R0..R7 preservation. This does not grant
; a placement, alter current code, or qualify live IRQ/cold behavior.
.setcpu "6502"
.segment "NATIVE_QUAD"
KrLadderNativeQuad:
 lda CurrentBankC
 pha
 lda #$83
 sta CurrentBankC
 sta $5116
 lda NativeTopLeft,y
 sta NativeVRAM+3,x
 lda NativeTopRight,y
 sta NativeVRAM+4,x
 lda NativeBotLeft,y
 sta NativeVRAM+8,x
 lda NativeBotRight,y
 sta NativeVRAM+9,x
 pla
 sta CurrentBankC
 sta $5116
 rts
