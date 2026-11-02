; Original91A9 death pose and200-update hold; SMB engine6 owns life loss.
.segment "DEATH"
.export ShDeathStart,ShDeathTick
.macro DeathSave
 .repeat 4,I
 lda R0+I
 pha
 .endrepeat
.endmacro
ShDeathStart:
 DeathSave
 ldx #0
 lda #7
 sta $c300
 jsr ShAnimatorInit
 lda #200
 sta $c408
 lda $c460
 and #$fe
 sta $c460
 lda FrameCounter
 sta $c802
 lda #0
 sta $c810
 lda #11
 sta GameEngineSubroutine
 jmp DeathReturn
ShDeathTick:
 DeathSave
 lda GamePauseStatus
 and #1
 bne DeathReturn
 lda FrameCounter
 cmp $c802
 beq DeathReturn
 sta $c802
 lda $c408
 beq DeathReturn
 dec $c408
 beq DeathFinished
 ldx #0
 jsr ShAnimatorTick
 jmp DeathReturn
DeathFinished:
 lda #6
 sta GameEngineSubroutine
 lda #0
 sta $c800
DeathReturn:
 .repeat 4,I
 pla
 sta R0+3-I
 .endrepeat
 sec
 rts
