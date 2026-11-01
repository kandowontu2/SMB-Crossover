; Selected-owner source adapter, NOT a native admission/loader.
; Caller must authenticate BOTH full C2/C3 headers before any A3 opcode.
; Source actor: A3:A000, MsState=C2:C000, MsPointer=foregroundR0=$03.
; Never use native NMI scratch00..02 or convert motion into Mm velocities.
.import SelectedCharacter,SavedJoypadBits,FrameCounter,GamePauseStatus
.import OperMode,GameEngineSubroutine
.export MsHostSelected,MsHostInput,MsHostSetBounds,MsHostReadY
.export MsHostSavePoint,MsHostReadDelta,MsHostStep,MsHostContractEnd
MsHostReady=$c800
MsHostEpoch=$c801
MsHostHaveEpoch=$c802
MsHostDeltaX=$c803
MsHostDeltaY=$c805
MsHostBeforeX=$c807
MsHostBeforeY=$c809
MsHostPad=$c80b
MsHostMulLo=$c80c
MsHostMulHi=$c80d
MsHostLinearLo=$c80e
MsHostLinearHi=$c80f

; Typed selected owner. Raw11 remains Sophia; raw35 is a proposed new owner.
; A/N/Z/C volatile; X/Y retained. A resident ROM equivalent is required cold.
MsHostSelected:
 lda SelectedCharacter
 cmp #35
 beq :+
 clc
 rts
:sec
 rts

; A=original right-bound low, X=high. Exact original732/733 contract;
; caller supplies the HOST AREA extent, never just donor low byteE4.
; Stores preserve all AXYP.
MsHostSetBounds:
 sta MsState+$732
 stx MsState+$733
 rts

; Actual NES input bit order -> original Metal Storm31. AXYP preserved.
; Original polling follows the actor: call AFTER the accepted source step.
; Source735 remains the sole jump/gravity edge latch; do not synthesize it.
MsHostInput:
 php
 pha
 txa
 pha
 lda #0
 sta MsHostPad
 lda SavedJoypadBits
 ldx #8
:lsr a
 rol MsHostPad
 dex
 bne :-
 lda MsHostPad
 sta MsState+$31
 pla
 tax
 pla
 plp
 rts

; SourceY uses signed240-pixel pages, not SMB's256-pixel high byte.
; A=linear source topY low, X=high; Y retained, flags volatile.
MsHostReadY:
 lda MsState+$4c8
 sta MsHostMulLo
 lda #0
 bit MsHostMulLo
 bpl :+
 lda #$ff
:sta MsHostMulHi
 .repeat 4
 asl MsHostMulLo
 rol MsHostMulHi
 .endrepeat
 lda MsState+$4b0
 sec
 sbc MsHostMulLo
 sta MsHostLinearLo
 lda MsState+$4c8
 sbc MsHostMulHi
 sta MsHostLinearHi
 tax
 lda MsHostLinearLo
 rts

MsHostSavePoint:
 php
 pha
 txa
 pha
 lda MsState+$480
 sta MsHostBeforeX
 lda MsState+$498
 sta MsHostBeforeX+1
 jsr MsHostReadY
 sta MsHostBeforeY
 stx MsHostBeforeY+1
 pla
 tax
 pla
 plp
 rts

; Exact signed world displacement. Native bridge applies it ONCE, then lets
; typed terrain/camera callbacks reconcile source positions at their boundary.
; No private fractions, source velocities or jump clocks are round-tripped.
MsHostReadDelta:
 php
 pha
 txa
 pha
 lda MsState+$480
 sec
 sbc MsHostBeforeX
 sta MsHostDeltaX
 lda MsState+$498
 sbc MsHostBeforeX+1
 sta MsHostDeltaX+1
 jsr MsHostReadY
 sec
 sbc MsHostBeforeY
 sta MsHostDeltaY
 txa
 sbc MsHostBeforeY+1
 sta MsHostDeltaY+1
 pla
 tax
 pla
 plp
 rts

; AXYP preserved exceptC1accepted/C0rejected. Epoch/pause repeats produce
; zero deltas and do not advance source input, clocks or object callbacks.
; The real FF27 callback owns original DCAE:INC53; never add a second tick.
MsHostStep:
 php
 pha
 txa
 pha
 tya
 pha
 jsr MsHostSelected
 bcc Rejected
 lda MsHostReady
 cmp #$a7
 bne Rejected
 lda OperMode
 cmp #1
 bne Rejected
 lda GameEngineSubroutine
 cmp #8
 bne Rejected
 lda #0
 sta MsHostDeltaX
 sta MsHostDeltaX+1
 sta MsHostDeltaY
 sta MsHostDeltaY+1
 lda GamePauseStatus
 and #1
 bne Accepted
 lda MsHostHaveEpoch
 beq Update
 lda FrameCounter
 cmp MsHostEpoch
 beq Accepted
Update:
 jsr MsHostSavePoint
 ; Restore the original source entry AXYP before its real frame routine.
 ; Temporary P/A copies are popped before entering the source call chain.
 tsx
 lda $0104,x
 pha
 lda $0101,x
 tay
 lda $0103,x
 pha
 lda $0102,x
 tax
 pla
 plp
 jsr MsFrame
 jsr MsHostReadDelta
 jsr MsHostInput                 ; original one-update controller pipeline
 lda FrameCounter
 sta MsHostEpoch
 lda #1
 sta MsHostHaveEpoch
Accepted:
 tsx
 lda $0104,x
 ora #1
 bne Status
Rejected:
 tsx
 lda $0104,x
 and #$fe
Status:
 sta $0104,x
 pla
 tay
 pla
 tax
 pla
 plp
 rts
MsHostContractEnd:
