.pushseg
.segment "M3_LOGIC"
.proc M3IsActive
 lda SelectedCharacter
 cmp #17
 beq Yes
 clc
 rts
Yes:sec
 rts
.endproc
.proc M3Ensure
 jsr M3IsActive
 bcc Done
 lda M3Marker
 cmp #$b3
 beq Done
 lda #0
 ldx #15
Clear:sta $5f40,x
 dex
 bpl Clear
 lda #$b3
 sta M3Marker
Done:rts
.endproc
.proc M3Reset
 jsr M3IsActive
 bcc Done
 lda #0
 tax
Clear:sta $5c00,x
 inx
 bne Clear
 lda #$b3
 sta M3Ready
 lda SavedJoypadBits
 sta M3Previous
 lda NumberofLives
 sta M3Life
 lda AreaNumber
 sta M3LastArea
 lda LevelNumber
 sta M3LastLevel
 lda #$80
 ldx #7
Attr:sta M3Native::Tile_AttrTable,x
 dex
 bpl Attr
 lda #$40
 ldx PlayerFacingDir
 cpx #2
 bne :+
 lda #0
:sta M3Native::Player_FlipBits
 ldx M3Form
 lda StandFrames,x
 sta M3Native::Player_Frame
Done:rts
StandFrames:.byte $3e,$0e,$0e,$02,$00,$02,$0e
.endproc
.proc M3Death
 jsr M3IsActive
 bcc Done
 lda #0
 sta M3Form
 jmp M3Reset
Done:rts
.endproc
.proc M3ClearSuitState
 ; Suit loss also cancels a queued statue transformation. Its native queue
 ; is consumed next movement tick, after SMB's enemy collision can hurt us.
 lda #0
 sta M3Native::Player_Statue
 sta M3Native::Player_QueueSuit
 sta M3Native::Player_SuitLost
 sta M3Native::Player_FlashInv
 sta M3Native::Player_TailAttack
 sta M3Native::Player_TailCount
 sta M3Native::Player_FlyTime
 sta M3Native::Player_AllowAirJump
 sta M3Native::Player_WagCount
 sta M3PaletteValid
 rts
.endproc
.popseg
