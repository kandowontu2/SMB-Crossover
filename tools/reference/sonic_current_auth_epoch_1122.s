; Original owner-limited authorization reuse. First ordinary Main call still
; performs both complete cookies. Every hit checks both live header prefixes.
.setcpu "6502"
CurrentBankC=$7da1
SelectedCharacter=$6002
FrameCounter=$0e
SharedEpoch=$c3f0

.segment "GATE"
CheckEpoch:
 lda CurrentBankC
 pha
 lda #2
 jsr MapC
 ldx SelectedCharacter
 jsr LiveHeader
 bcc Miss
 jsr ReadEpoch
 ora #0
 beq Miss
 bcc MiniGood
 jmp ReadSonicEpoch
MiniGood:
 jmp CheckCodeHeader
Miss:
 clc
 jmp RestoreC
.segment "UTIL"
LiveHeader:
 lda $dfe0
 cmp #$a7
 bne Invalid
 cpx $dfe1
 beq HeaderReturn
Invalid:
 clc
HeaderReturn:
 rts
RestoreC:
 pla
MapC:
 sta CurrentBankC
 sta $5116
 rts
CheckCodeHeader:
 lda #3
 jsr MapC
 jsr LiveHeader
 jmp RestoreC
.segment "HEADER"
ReadEpoch:
 lda SharedEpoch
 beq BadEpoch
 cmp FrameCounter
 bne BadEpoch
 cpx #43
 rts
BadEpoch:
 ; Equal nonzero epochs return A unchanged and C=(owner43). A miss must
 ; return zero, independent of the CMP carry, before any private jump.
 lda #0
 rts

.segment "SONIC_EPOCH"
; Genuine unpaused ordinary Main scope, not an independent authorization.
; C3F0 belongs to the current exclusive C2 owner; Sonic cold zeroes it.
ReadSonicEpoch:
 lda $5fff
 and #1
 beq NoSonicEpoch
 lda $01fa
 cmp #$83
 bne NoSonicEpoch
 lda $01f9
 cmp #$52
 bne NoSonicEpoch
 lda $c119
 cmp #1
 bne NoSonicEpoch
 lda $c11a
 cmp #1
 bne NoSonicEpoch
 lda GameEngineSubroutine
 cmp #8
 bne NoSonicEpoch
 lda GamePauseStatus
 and #1
 ora TimerControl
 bne NoSonicEpoch
 lda $c11b
 cmp FrameCounter
 bne NoSonicEpoch
 jmp CheckCodeHeader
NoSonicEpoch:
 clc
 jmp RestoreC
StampSonicEpoch:
 sta $c11b
 sta SharedEpoch
 rts
