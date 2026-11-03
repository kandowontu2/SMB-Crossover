; Private source-only frontend successor. No menu/ROM admission by inclusion.
; Actual full native resolver precedes ExMenuBody. Its complete legal menu
; domain has X==29 iff CrossoverMenuIndex==29. Mario can return Variant0..7;
; DK can return X=$ff. No arbitrary direct-entry X contract is asserted.
.macro PrinceFrontendResolver
 php
 cpx #29
 .byte $d0,<(ExMenuDone-(*+1))
 lda FmAlts
 and #16
 cmp #16                      ; C0 for Ex, C1 for original Prince alternate.
 lda #37
 adc #0
 sta SelectedCharacter
 .byte $d0,<(ExMenuDone-(*+1)) ; Both37/38 are nonzero through STA.
.endmacro

.macro PrinceFrontendStartMasks
 php
 txa
 pha
 tya
 pha
 jsr FmCfRestoreP1
 tsx
 lda $0102,x
 ldy #8
Find:
 cmp Slots,y
 beq Found
 dey
 bpl Find
 ldy #9                      ; Fallback has two zero masks, not Prince row4.
Found:
 lda Alts,y
 and FmAlts
 sta FmAlts
 lda Groups,y
 and FmGroups
 sta FmGroups
 pla
 tay
 pla
 tax
 plp
 lda #0
 rts
Slots:.byte 10,31,9,26,29,23,30,28,25
Alts:.byte $44,$80,$20,$08,$10
; Alts5..9 overlaps Groups0..4, all zero. Groups9 is the explicit fallback.
; This uses the two final bytes of the same source-declared74B procedure.
Groups:.byte 0,0,0,0,0,$20,$18,7,$80,0
.endmacro

PrinceFrontendReadinessLimit=26 ; Existing8B helper CMP immediate only.
PrinceFrontendNameMarker=36    ; Existing FmNames index25/tile1 only.
