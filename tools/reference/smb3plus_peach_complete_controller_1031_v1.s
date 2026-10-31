; These helpers are source transcriptions, not new hover rules.
; 32:A003 runs after a fresh A input, BEFORE the native air-jump permission.
.proc MbPeachJumpRoot
 php
 lda M3Variant
 cmp #3
 bne Root
 lda M3Form
 cmp #4
 bpl Root
 lda MbFloatReady
 cmp #2
 beq Store
 inc MbFloatReady
Store:
 lda M3Native::Player_Y
 sta MbFloatAnchor
Root:
 plp
 lda M3Native::Player_AllowAirJump
 rts
.endproc

; 30:BAC0..BB5E after native gravity/flutter. BB50 consults Anchor in
; forms4..6, so those forms do not invent a ready2 producer at Anchor0.
.proc MbPeachAfterJump
 jsr M3Native::Player_JumpFlyFlutter
 php
 pha
 lda M3Variant
 cmp #3
 bne Done
 lda MbFloatReady
 cmp #2
 beq Maintain
 lda M3Native::Pad_Holding
 bpl Override
 lda M3Native::Player_YVel
 bmi Override
 lda M3Form
 cmp #4
 bmi CheckExpired
 lda MbFloatAnchor
 beq Override
CheckExpired:
 lda MbFloatExpired
 bne Override
Maintain:
 lda M3Native::Player_SandSink
 bne Sink
 lda #2
 sta MbFloatReady
Override:
 jmp MbPeachAfterOverride
Sink:
 jsr MbPeachFloatSink
 jmp Override
Done:
 jmp MbPeachFloatReturn
.endproc

.proc MbPeachAfterOverride
 lda M3Form
 cmp #4
 bpl Done
 lda MbFloatReady
 cmp #2
 bne Done
 lda MbFloatExpired
 bne Done
 lda #$ff
 sta M3Native::Player_YVel
Done:
 jmp MbPeachFloatReturn
.endproc

; Original stock frame table is read with A92 still mapped. Only the
; pure selected-Peach override changes A81; FarCallCommon restores A92.
.proc MbPeachLeafFrame
 lda M3Native::Player_TailWagFlyFrames,y
 farcall MbPeachLeafOverride,jmp
.endproc

; Donor32:AF80..AFA4, using the original P1 float bytes. Preserve the
; incoming native-table frame for all foreign/expired/fast-frame paths.
.proc MbPeachLeafOverride
 php
 pha
 lda M3Variant
 cmp #3
 bne Original
 lda MbFloatExpired
 bne Original
 lda MbFloatReady
 cmp #2
 bne Original
 lda M3Native::Player_Frame
 cmp #$38
 beq Original
 pla
 lda M3Native::Player_Power
 cmp #$7f
 beq Fast
 lda #10
 bne Return
Fast:
 lda #$38
Return:
 plp
 rts
Original:
 pla
 plp
 rts
.endproc
