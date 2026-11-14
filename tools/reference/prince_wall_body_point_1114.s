; Proposal only: WorldMaterial current-row wall AND floor point reads.
; No allocation or mount. The source ActorX is authoritative before export;
; current HostExport defines native left = ActorX - 8. Sprite pose width is
; deliberately absent from this existing 16px physical-body contract.
; Caller consumes C only, then reloads A. Keep A/X/Y and architectural flags except the
; deliberate C1 -> C0 rejection of a solid cell outside that body.
.setcpu "6502"
.segment "WALL_BODY"
WallBodyPoint:
 ; Keep the delivered Hand filter, including its native flag tile25 policy.
 jsr $a49a
 bcs Body
 rts
FloorBodyPoint:
 jsr $b310
 bcc Done
Body:
 php
 pha
 txa
 pha
 lda $c07c
 cmp $c083
 bne Keep
 ; CellStart - (ActorX-8). CellStart+8 cannot overflow its low byte.
 lda $b369
 and #$f0
 clc
 adc #8
 sec
 sbc $c60f
 tax
 lda $b36a
 sbc $c610
 beq Positive
 cmp #$ff
 bne Reject
 cpx #$f1
 bcs Keep
 bcc Reject
Positive:
 cpx #$10
 bcc Keep
Reject:
 pla
 tax
 pla
 plp
 clc
 rts
Keep:
 pla
 tax
 pla
 plp
Done:
 rts
