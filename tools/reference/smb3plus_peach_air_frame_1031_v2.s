; Source: Super Mario Bros. 3+ SHA be750155... donor32:B140..B16F.
; The original float-ready path reverses the ordinary jump/fall choice.
; Microgoomba forces the falling pose. The host owns only Peach's float
; state; foreign identities retain the existing SMB3 controller ABI.
.proc MbPeachAirFrame
 php
 lda M3Variant
 cmp #3
 bne Original
 lda MbFloatReady
 cmp #2
 bne Original
 lda MbFloatExpired
 bne Original
 plp
 ldy M3Native::Player_YVel
 bmi Fall
 lda M3Native::Player_UphillSpeedIdx ; source alias of06B6
 bne Fall
 lda #$4f
 rts
Fall:
 lda #6
 rts
Original:
 plp
 lda #$4f
 ldy M3Native::Player_YVel
 bmi Done
 lda #6
Done:
 rts
.endproc
