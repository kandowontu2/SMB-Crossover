; Original earned options and timers, with a deliberately limited SMB control
; adapter. No host grant, SMC, NMI0..2, generic Mario tier, or code lease.
; Caller already maps authenticated C2. SourceCall wrappers are sequential
; with KrSourceFrame/Weapons, never nested inside their saved-pointer frame.
; KrState,KrPointer,KrSaved0/1 and source callbacks are owning-link imports.
.export KrOptionsNative,KrOptionsNativeTimers,KrOptionsControls,KrOptionsTick
.export KrOptionsCycle,KrOptionsEnd
KrOptionPressed=$c865

; Complete original EAA7..EDB6 and ADA8..AE32, recovered with all inline
; dispatch words and their exact original helper/data islands.
.include "karnov-options-portable-v7.inc"

.macro KrOptionSourceCall Target
 lda KrPointer
 sta KrSaved0
 lda KrPointer+1
 sta KrSaved1
 jsr Target
 php
 pha
 lda KrSaved0
 sta KrPointer
 lda KrSaved1
 sta KrPointer+1
 pla
 plp
 rts
.endmacro
KrOptionsNative:KrOptionSourceCall Kr_EAA7
KrOptionsNativeTimers:KrOptionSourceCall Kr_ADA8

; Explicit host clock adaptation: one accepted source update advances E8.
; Native0F is the NMI clock; using accepted E8 keeps expiry paused with the
; host's paused/lagged source update. The original64-tick divider is intact.
; Invoke AFTER original actor/weapons and BEFORE the existing INC E8.
KrOptionsTick:
 lda KrState+$e8
 sta KrState+$0f
 jmp KrOptionsNativeTimers

; Invoke after the FULL newly pressed source21 bits are built, before actor.
; Select cycles owned supported equipment, then NONE. Down+freshB activates.
; Ordinary A/B, directions, Start, and all other source edge bits stay live.
; AXY/P are consumed; C marks recognized cycle/activation, not item success.
; Original effects already active continue when the selection becomes NONE.
KrOptionsControls:
 lda KrState+$21
 and #$fb
 sta KrOptionPressed
 lda KrState+$21
 and #4
 beq KrOptionsNotSelect
 jsr KrOptionsCycle
 lda KrOptionPressed
 sta KrState+$21
 sec
 rts
KrOptionsNotSelect:
 lda KrState+$1b
 and #$20
 beq KrOptionsUnhandled
 lda KrState+$21
 and #2
 beq KrOptionsUnhandled
 lda KrState+$62
 and #$1f
 cmp #$19
 bcs KrOptionsUnhandled
 lda KrState+$8e
 cmp #0
 beq KrOptionsSupported
 cmp #3
 beq KrOptionsSupported
 cmp #7
 bne KrOptionsUnhandled
KrOptionsSupported:
 jsr Kr_C28C
 beq KrOptionsUnhandled
 lda KrOptionPressed
 and #$fd
 sta KrOptionPressed
 ora #4
 sta KrState+$21
 jsr KrOptionsNative
 lda KrOptionPressed
 sta KrState+$21
 sec
 rts
KrOptionsUnhandled:
 lda KrOptionPressed
 sta KrState+$21
 clc
 rts

; A cursor change consumes no stock and grants no ownership. Only the exact
; native activation leaves consume BCD stocks or set source ability states.
KrOptionsCycle:
 ldx #0
 lda KrState+$8e
KrOptionsFind:
 cmp KrOptionIds,x
 beq KrOptionsNext
 inx
 cpx #4
 bne KrOptionsFind
 ldx #3
KrOptionsNext:
 inx
 txa
 and #3
 tax
 lda KrOptionIds,x
 bmi KrOptionsChoose
 lda KrState+$8f
 and KrOptionMasks,x
 beq KrOptionsNext
 lda KrOptionIds,x
KrOptionsChoose:
 sta KrState+$8e
 rts
KrOptionIds:.byte 0,3,7,$ff
KrOptionMasks:.byte 1,8,$80,0
KrOptionsEnd:
