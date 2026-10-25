.pushseg
.segment "CD_LOGIC"
.proc CdIsActive
 lda SelectedCharacter
 cmp #14
 beq Yes
 clc
 rts
Yes:sec
 rts
.endproc
.proc CdEnsureInit
 jsr CdIsActive
 bcc Done
 lda CdMagic
 cmp #$a5
 beq Done
 lda #0
 ldx #15
Clear:sta CdPersistent,x
 dex
 bpl Clear
 lda #3
 sta CdHealth
 lda #$a5
 sta CdMagic
Done:rts
.endproc
.proc CdResetTransient
 jsr CdIsActive
 bcc Done
 lda #0
 tax
Clear:sta $5c00,x
 inx
 bne Clear
 lda #$43
 sta CdReady
 lda #$55 ; original bank7:C6FC gravity.
 sta CdGravity
 lda SavedJoypadBits
 sta CdPrevious
 lda #1
 sta CdAnim
 lda #1
 sta CdAnimFrame
 lda #6
 sta CdAnimTimer
 lda #1
 sta CdEntrancePending
Done:rts
.endproc
.proc CdResetArea
 jsr CdIsActive
 bcs Active
 rts
Active:
 farcall MegaManResetArea
 jmp CdResetTransient
.endproc
.proc CdDeath
 jsr CdIsActive
 bcc Done
 jsr CdResetTransient
 lda #3
 sta CdHealth
Done:rts
.endproc
.proc CdSpawnEntrance
 jsr CdIsActive
 bcc Done
 lda CdEntrancePending
 beq Done
 lda #0
 sta CdEntrancePending
 lda #1
 sta CdBoxKind
 lda #0
 sta CdBoxMode
 lda Player_X_Position
 clc
 adc #32
 sta CdBoxX
 lda Player_PageLoc
 adc #0
 sta CdBoxPage
 lda Player_Y_Position
 clc
 adc #16
 sta CdBoxY
Done:rts
.endproc
.popseg
