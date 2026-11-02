; Private authenticated-caller leaves. The resident owner must validate both
; headers before entering RAM2/3, and retire them before any overlay replacement.
; Only original source movement runs; these leaves supply native lifecycle.
.setcpu "6502"
.segment "SERVICES"
.export PpNativeInit,PpNativeRetire,PpNativeTick,PpNativePitDeath
PpEpoch=$c0a9
PpEpochValid=$c0aa
PpReady=$c0ab
PpDead=$c0ac
PpNativeInit:
 jsr PpHostInit
 lda #0
 sta PpEpochValid
 sta PpDead
 lda #$a7
 sta PpReady
 sec
 rts
PpNativeRetire:
 lda #0
 sta PpReady
 sta PpEpochValid
 sec
 rts
PpNativeTick:
 lda SelectedCharacter
 cmp #38
 bne Rejected
 lda PpReady
 cmp #$a7
 bne Rejected
 lda PpDead
 bne Rejected
 lda OperMode
 cmp #1
 bne Rejected
 lda GameEngineSubroutine
 cmp #8
 bne Rejected
 lda GamePauseStatus
 and #1
 bne Rejected
 lda PpEpochValid
 beq NewEpoch
 lda FrameCounter
 cmp PpEpoch
 beq Rejected
NewEpoch:
 lda FrameCounter
 sta PpEpoch
 lda #1
 sta PpEpochValid
 jsr PpHostUpdate
 jsr PpNativePitDeath
 sec
 rts
Rejected:
 clc
 rts
PpNativePitDeath:
 lda PpDead
 bne Rejected
 lda Player_Y_HighPos
 cmp #1
 bne CheckHigh
 lda Player_Y_Position
 cmp #240
 bcc Rejected
 bcs Kill
CheckHigh:
 cmp #2
 bcc Rejected
Kill:
 lda #1
 sta PpDead
 ; FarCallCommon owns five foreground SMC bytes and R0..R7. Preserve the
 ; caller's complete values around the genuine native KillPlayer service.
 ldx #0
SaveZp:
 lda R0,x
 pha
 inx
 cpx #8
 bne SaveZp
 ldx #0
SaveSmc:
 ldy SmcOffsets,x
 lda $0100,y
 pha
 inx
 cpx #5
 bne SaveSmc
 lda #<KillPlayer
 sta FarcallJmpTarget_SMC+1
 lda #>KillPlayer
 sta FarcallJmpTarget_SMC+2
 ldx #0
 lda #Bank_KillPlayer
 jsr FarCallCommon
 ldx #4
RestoreSmc:
 pla
 ldy SmcOffsets,x
 sta $0100,y
 dex
 bpl RestoreSmc
 ldx #7
RestoreZp:
 pla
 sta R0,x
 dex
 bpl RestoreZp
 sec
 rts
SmcOffsets:
 .byte <(SafecallA_SMC+1),<(FarcallJmpTarget_SMC+1),<(FarcallJmpTarget_SMC+2),<(NextBank_SMC+1),<(SafereturnA_SMC+1)
.export PpNativeServicesEnd
PpNativeServicesEnd:
