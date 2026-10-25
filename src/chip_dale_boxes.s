.pushseg
.segment "CD_LOGIC"
.proc CdWeapons
 jsr CdIsActive
 jcc Done
 lda MmDeathFlag
 ora TimerControl
 jne Done
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda CdThrowAge
 beq Input
 dec CdThrowAge
 lda CdThrowAge
 cmp #4
 bne Update
 jsr CdRelease
 jmp Update
Input:
 lda CdPressed
 and #B_Button
 beq Update
 lda CdHeld
 beq Pickup
 lda SavedJoypadBits
 and #Up_Dir
 beq Horizontal
 lda #1
 sta CdThrowUp
 jsr CdRelease
 jmp Update
Horizontal:
 lda #0
 sta CdThrowUp
 lda #8 ; original horizontal throw animation2frames×4ticks.
 sta CdThrowAge
 jmp Update
Pickup:
 jsr CdPickResting
 bcs Update
 jsr CdLiftBrick
Update:
 lda #5
 sta CdSlot
Loop:
 ldx CdSlot
 lda CdBoxKind,x
 jeq Next
 lda CdBoxMode,x
 cmp #1
 beq Carried
 cmp #2
 beq Thrown
 jmp Next
Carried:
 lda Player_X_Position
 sta CdBoxX,x
 lda Player_PageLoc
 sta CdBoxPage,x
 lda Player_Y_Position
 sec
 sbc #8
 ldy CdHide
 beq CarryY
 clc
 adc #24
CarryY:sta CdBoxY,x
 jmp Next
Thrown:
 jsr CdBoxPhysics
 jsr CdBoxEnemies
Next:dec CdSlot
 jpl Loop
Done:rts
.endproc
.proc CdPickResting
 ldx #5
Loop:
 lda CdBoxKind,x
 beq Next
 lda CdBoxMode,x
 bne Next
 lda CdBoxX,x
 sec
 sbc Player_X_Position
 sta R0
 lda CdBoxPage,x
 sbc Player_PageLoc
 sta R1
 lda R0
 clc
 adc #20
 sta R0
 lda R1
 adc #0
 bne Next
 lda R0
 cmp #41
 bcs Next
 lda CdBoxY,x
 sec
 sbc Player_Y_Position
 clc
 adc #8
 cmp #41
 bcs Next
 txa
 clc
 adc #1
 sta CdHeld
 lda #1
 sta CdBoxMode,x
 lda #Sfx_Bump
 sta Square1SoundQueue
 sec
 rts
Next:dex
 bpl Loop
 clc
 rts
.endproc
.proc CdRelease
 ldx CdHeld
 beq Done
 dex
 lda #2
 sta CdBoxMode,x
 lda #0
 sta CdHeld
 sta CdBoxFrac,x
 sta CdBoxVYLo,x
 sta CdBoxVYHi,x
 sta CdBoxAge,x
 sta CdBoxVX,x
 lda CdThrowUp
 beq Horizontal
 lda #4 ; originalCD95 virtual-index writes native upwardVY4.
 sta CdBoxVYHi,x
 bne Sound
Horizontal:
 lda #4 ; originalCDF5 native horizontal integer speed4.
 ldy PlayerFacingDir
 cpy #1
 beq :+
 lda #$fc
:sta CdBoxVX,x
Sound:
 lda #Sfx_Fireball
 sta Square1SoundQueue
Done:rts
.endproc
.proc CdLiftBrick
 ldx #5
Find:lda CdBoxKind,x
 beq Free
 dex
 bpl Find
 rts
Free:stx CdSlot
 lda #20
 ldy PlayerFacingDir
 cpy #1
 beq :+
 lda #$fc
:sta R0
 lda #0
 ldy R0
 bpl :+
 lda #$ff
:sta R1
 lda Player_X_Position
 clc
 adc R0
 sta CdQueryX
 lda Player_PageLoc
 adc R1
 sta CdQueryPage
 lda Player_Y_Position
 clc
 adc #20
 jsr CdReadCell
 cmp #$51
 beq Check
 cmp #$52
 bne Reject
Check:
 lda VRAM_Buffer1_Offset
 cmp #80
 bcs Reject
 lda R6
 clc
 adc #<(MmSolidTerrain-Block_Buffer_1)
 sta M0
 lda R7
 adc #>(MmSolidTerrain-Block_Buffer_1)
 sta M1
 ldy R2
 lda (M0),y
 bne Reject
 ldx CdSlot
 lda CdQueryX
 and #$f0
 sta CdBoxX,x
 lda CdQueryPage
 sta CdBoxPage,x
 lda Player_Y_Position
 clc
 adc #20
 and #$f0
 sta CdBoxY,x
 lda #0
 sta (R6),y
 ldx #0
 farcall DestroyBlockMetatile
 ldx CdSlot
 lda #1
 sta CdBoxKind,x
 sta CdBoxMode,x
 txa
 clc
 adc #1
 sta CdHeld
 lda #Sfx_Bump
 sta Square1SoundQueue
 sec
 rts
Reject:clc
 rts
.endproc
; CdQueryX/Page and A=Y -> A=metatile; R6/R7columnbase,R2row.
.proc CdReadCell
 cmp #32
 bcc Empty
 cmp #240
 bcs Empty
 and #$f0
 sec
 sbc #32
 sta R2
 lda CdQueryPage
 and #1
 asl
 asl
 asl
 asl
 sta R0
 lda CdQueryX
 lsr
 lsr
 lsr
 lsr
 ora R0
 jsr GetBlockBufferAddr
 ldy R2
 lda (R6),y
 rts
Empty:lda #0
 rts
.endproc
.proc CdBoxPhysics
 inc CdBoxAge,x
 lda CdBoxAge,x
 cmp #120
 jcs Kill
 lda #0
 ldy CdBoxVX,x
 bpl :+
 lda #$ff
:sta R0
 lda CdBoxX,x
 clc
 adc CdBoxVX,x
 sta CdBoxX,x
 sta CdQueryX
 lda CdBoxPage,x
 adc R0
 sta CdBoxPage,x
 sta CdQueryPage
 lda CdBoxFrac,x
 sec
 sbc CdBoxVYLo,x
 sta CdBoxFrac,x
 lda CdBoxY,x
 sbc CdBoxVYHi,x
 sta CdBoxY,x
 cmp #240
 jcs Kill
 lda CdBoxVYLo,x
 sec
 sbc #$55
 sta CdBoxVYLo,x
 lda CdBoxVYHi,x
 sbc #0
 sta CdBoxVYHi,x
 clc
 lda CdBoxY,x
 adc #8
 jsr CdReadCell
 beq Done
 cmp #$23
 beq Done
 cmp #$26
 beq Done
 cmp #$c2
 beq Done
 cmp #$c3
 beq Done
Kill:
 ldx CdSlot
 lda #0
 sta CdBoxKind,x
 lda #Sfx_BrickShatter
 sta NoiseSoundQueue
Done:rts
.endproc
.proc CdBoxEnemies
 ldx CdSlot
 lda CdBoxKind,x
 beq Done
 lda CdBoxX,x
 sta CdRectX
 lda CdBoxPage,x
 sta CdRectPage
 lda CdBoxY,x
 sta CdRectY
 ldx #5
Loop:
 lda Enemy_Flag,x
 beq Next
 bmi Next
 lda Enemy_State,x
 and #$20
 bne Next
 lda Enemy_ID,x
 cmp #$15
 bcs Next
 cmp #Podoboo
 beq Next
 lda Enemy_X_Position,x
 sec
 sbc CdRectX
 sta R0
 lda Enemy_PageLoc,x
 sbc CdRectPage
 sta R1
 lda R0
 clc
 adc #16
 sta R0
 lda R1
 adc #0
 bne Next
 lda R0
 cmp #32
 bcs Next
 lda Enemy_Y_Position,x
 clc
 adc #8
 sec
 sbc CdRectY
 clc
 adc #16
 cmp #32
 bcs Next
 stx ObjectOffset
 jsr CdDefeatEnemy
 ldx CdSlot
 lda #0
 sta CdBoxKind,x
 rts
Next:dex
 bpl Loop
Done:rts
.endproc
.proc CdDefeatEnemy
 ; Use native SMB defeat/scoring below the old inventory hook. No12-family
 ; drop/inventory code may derive an index from new rawID14.
 lda Enemy_ID,x
 cmp #PiranhaPlant
 bne Stun
 lda Enemy_Y_Position,x
 clc
 adc #24
 sta Enemy_Y_Position,x
Stun:jmp StnE
.endproc
.popseg
