; The resident owner entry supplies R5/R6 pointing at one of the six
; immutable headers. The linker binds the mirrored comparison bytes to the
; actual parent ROM. A cache hit is limited to Mini's gameplay service calls.
.setcpu "6502"
.segment "AUTH"
.export FrameAuth
.import CookieLows, CookieTableLo, CookieTableHi
CurrentBankC = $7da1
FrameCounter = $0e
MiniCacheEpoch = $c3f0
Header = $dfe0
R5 = $08
R6 = $09

FrameAuth:
 ldx #5
FindCookie:
 lda CookieLows,x
 cmp R5
 beq Found
 dex
 bpl FindCookie
 clc
 rts
Found:
 lda CurrentBankC
 pha
 lda R5
 pha
 lda R6
 pha
 lda CookieTableLo,x
 sta R5
 lda CookieTableHi,x
 sta R6
 ; The original CoCheckCode -> CoCheckHeaders return is AEF9. The 6502
 ; stacks AEF8. At this point it is eleven bytes above SP after the two
 ; saved target bytes, the farcall's stack frame and our three saved bytes.
 ; Cold and retirement invoke the full comparison even in the same frame.
 cpx #4
 bne Full
 tsx
 lda $010b,x
 cmp #$f8
 bne Full
 ldx #2
 jsr MapC
 lda FrameCounter
 beq MiniMiss
 cmp MiniCacheEpoch
 bne MiniMiss
 jsr MiniHeaderLive
 bcc MiniMiss
 ldx #3
 jsr MapC
 jsr MiniHeaderLive
 bcs Restore
MiniMiss:
 jsr VerifyBoth
 bcc Restore
 ; VerifyBoth ends in bank 2. The cold worker zeroes this Mini state
 ; before installing a new owner. CoInvalidate clears both live headers.
 lda FrameCounter
 sta MiniCacheEpoch
 bcs Restore
Full:
 jsr VerifyBoth
Restore:
 pla
 sta R6
 pla
 sta R5
 pla
 sta CurrentBankC
 sta $5116
 rts

MiniHeaderLive:
 lda Header
 cmp #$a7
 bne Invalid
 lda Header+1
 cmp #41
 beq HeaderReturn
Invalid:
 clc
HeaderReturn:
 rts

VerifyBoth:
 ldx #3
VerifyBank:
 jsr MapC
 ldy #15
VerifyByte:
 lda Header,y
 cmp (R5),y
 bne Invalid
 dey
 bpl VerifyByte
 dex
 cpx #1
 bne VerifyBank
 rts
MapC:
 stx CurrentBankC
 stx $5116
 rts

.segment "BRIDGE"
.export CheckHeaders
CheckHeaders:
 ; All existing callers have a five-byte SMC save frame. Only the active
 ; target is consumed before the outer frame restores the other SMC bytes.
 lda $016c
 pha
 lda $016d
 pha
 lda #<FrameAuth
 sta $016c
 lda #>FrameAuth
 sta $016d
 lda #$94
 jsr $015a
 pla
 sta $016d
 pla
 sta $016c
 rts
