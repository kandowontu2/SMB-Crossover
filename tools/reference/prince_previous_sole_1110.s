; Private authenticated Prince code, after shared pose packets and before
; the unchanged D622 camera. Source physics, C086, climb and DY stay exact.
.setcpu "6502"
.segment "LANDING"
PpCapturePreviousSole:
 lda $c084
 sta PreviousSole+1
 lda $c085
 sta PreviousHigh+1
 jmp $b36e

; PpNativeContact has saved AXYP and admitted nonzero HP. Classify before
; its original defender callback can debit HP. Native collision owns X and
; ObjectOffset plus the actual bounding box. Preserve source no-bounce policy.
PpLandingContact:
 php
 lda CrossoverBehaviorVersion
 bne Original
 lda AreaType
 beq Original
 lda $c0aa
 beq Original
 lda FrameCounter
 cmp $c0a9
 bne Original
 lda Enemy_ID,x
 cmp #7
 bcs Original
 lda Enemy_Y_HighPos,x
 cmp #1
 bne Original
 lda $c085
 bne Original
PreviousHigh:
 lda #$00
 bne Original
 txa
 asl a
 asl a
 tay
 lda $065d,y
PreviousSole:
 cmp #$00
 bcc Original
 cmp $c084
 bcs Original
 plp
 ldy #4
 jmp $da1b
Original:
 plp
 lda $c6cf
 ldy #0
 jmp $dadd
LandingLo:
 .byte $96,$f8,$71,$3a,<EnemyStomped
LandingHi:
 .byte $a2,$9a,$af,$af,>EnemyStomped
LandingBank:
 .byte $ce,$fe,$83,$88,$fe
