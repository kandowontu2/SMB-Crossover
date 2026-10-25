.pushseg
.segment "Z2_LOGIC"
.proc Z2DrawWorld
 lda #.lobyte(335)
 ldx #.hibyte(335)
 farcall X5SetSpecialChr
 BankPRGC #.bank(Z2ArtBegin)
 lda #5
 sta InvDrawSlot
World:
 ldx InvDrawSlot
 lda Enemy_Flag,x
 jeq WorldNext
 lda Enemy_ID,x
 cmp #PowerUpObject
 jne WorldNext
 lda InvPickupOwner,x
 cmp #CHARACTER_LINK
 jne WorldNext
 lda InvPickup,x
 sec
 sbc #$c0
 cmp #14
 jcs WorldNext
 tay
 lda RewardArt,y
 jsr Pointer
 ldx InvDrawSlot
 sec
 lda Enemy_X_Position,x
 sbc ScreenLeft_X_Pos
 sta R4
 lda Enemy_PageLoc,x
 sbc ScreenLeft_PageLoc
 sta R5
 clc
 lda R4
 adc #8
 sta R4
 lda R5
 adc #0
 sta R5
 lda Enemy_Y_Position,x
 clc
 adc #8
 sta R6
 lda Enemy_Y_HighPos,x
 sta R7
 lda Enemy_SprAttrib,x
 and #$20
 sta R3
 farcall MetaspriteRenderLoop
WorldNext:dec InvDrawSlot
 jpl World
 lda #5
 sta InvDrawSlot
Drops:
 ldx InvDrawSlot
 lda Z2DropKind,x
 jeq DropNext
 cmp #$90
 beq Blue
 cmp #$91
 beq Red
 lda #8
 bne DropPointer
Blue:lda #6
 bne DropPointer
Red:lda #7
DropPointer:jsr Pointer
 ldx InvDrawSlot
 sec
 lda Z2DropX,x
 sbc ScreenLeft_X_Pos
 sta R4
 lda Z2DropPage,x
 sbc ScreenLeft_PageLoc
 sta R5
 lda Z2DropY,x
 sta R6
 jsr Draw
DropNext:dec InvDrawSlot
 jpl Drops
 lda #1
 sta InvDrawSlot
Shots:
 ldx InvDrawSlot
 lda Z2ShotKind,x
 beq ShotNext
 cmp #1
 beq Beam
 lda #4
 bne ShotPointer
Beam:lda #9
ShotPointer:jsr Pointer
 ldx InvDrawSlot
 sec
 lda Z2ShotX,x
 sbc ScreenLeft_X_Pos
 sta R4
 lda Z2ShotPage,x
 sbc ScreenLeft_PageLoc
 sta R5
 lda Z2ShotY,x
 sta R6
 jsr Draw
ShotNext:dec InvDrawSlot
 bpl Shots
 rts
Draw:
 lda #1
 sta R7
 lda #0
 sta R3
 farcall MetaspriteRenderLoop,jmp
Pointer:
 tay
 lda Z2ItemPtrLo,y
 sta R0
 lda Z2ItemPtrHi,y
 sta R1
 rts
RewardArt:.byte 0,1,1,2,0,3,4,0,0,0,5,3,0,6
.endproc
.popseg
