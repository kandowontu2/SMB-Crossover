.pushseg
.segment "M3_LOGIC"
.proc M3DrawWorld
 lda #.lobyte(544)
 ldx #.hibyte(544)
 farcall X5SetSpecialChr
 BankPRGC #.bank(M3ArtBegin)
 lda #5
 sta InvDrawSlot
World:ldx InvDrawSlot
 lda Enemy_Flag,x
 jeq Next
 jsr M3PrivatePickup
 jcc Next
 lda Enemy_State,x
 bmi Visible
 cmp #2
 jcc Next
Visible:lda InvPickup,x
 and #15
 jsr M3WorldPointer
 ldx InvDrawSlot
 lda Enemy_X_Position,x
 clc
 adc #8
 sta R4
 lda Enemy_PageLoc,x
 adc #0
 sta R5
 lda R4
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda R5
 sbc ScreenLeft_PageLoc
 sta R5
 lda Enemy_Y_Position,x
 clc
 adc #8
 sta R6
 lda Enemy_Y_HighPos,x
 adc #0
 sta R7
 lda Enemy_SprAttrib,x
 and #$20
 sta R3
 farcall MetaspriteRenderLoop
Next:dec InvDrawSlot
 jpl World
 lda #1
 sta InvDrawSlot
Shots:ldx InvDrawSlot
 lda M3ShotKind,x
 beq NextShot
 cmp #2
 beq Hammer
 lda M3ShotAge,x
 lsr
 lsr
 and #3
 clc
 adc #7
 bne Pointer
Hammer:lda M3ShotAge,x
 lsr
 lsr
 and #3
 clc
 adc #11
Pointer:jsr M3WorldPointer
 ldx InvDrawSlot
 lda M3ShotX,x
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda M3ShotPage,x
 sbc ScreenLeft_PageLoc
 sta R5
 lda M3ShotY,x
 sta R6
 lda M3ShotYHi,x
 sta R7
 lda #0
 sta R3
 lda M3ShotKind,x
 cmp #2
 bne Render
 lda M3ShotVX,x
 bpl Render
 lda #$40
 sta R3
Render:farcall MetaspriteRenderLoop
NextShot:dec InvDrawSlot
 bpl Shots
 lda M3Poof
 beq Body
 dec M3Poof
 lda M3Poof
 and #$0c
 lsr
 lsr
 clc
 adc #15
 jsr M3WorldPointer
 lda Player_Rel_XPos
 sta R4
 lda #0
 sta R5
 sta R3
 lda Player_Y_Position
 clc
 adc #8
 sta R6
 lda Player_Y_HighPos
 sta R7
 farcall MetaspriteRenderLoop
Body:jsr M3WeaponPalette
 jsr M3Hud
 jmp M3PublishBody
.endproc
.proc M3Hud
 ; Original six chevrons and two-tile [P], in the empty row above the
 ; coin counter. The separate font preserves every other HUD label/digit.
 lda DisableScreenFlag
 jne Done
.if ::MAPPER_MMC5
 lda #<545
 sta InvHudPhysical
 lda #>545
 sta X5HudChrUpper
 lda InvHudActive
 bne :+
 inc ReloadCHRBank
:lda #1
 sta InvHudActive
.endif
 lda M3Native::Player_Power
 and #$7f
 sta M3HudBits
 cmp #$7f
 bne Key
 lda FrameCounter
 and #8
 beq FullDark
 lda #$ff
 bne Key
FullDark:lda #$7f
Key:sta M3Scratch2
 cmp M3HudPower
 bne Queue
 lda M3HudValid
 bne Done
Queue:ldx VRAM_Buffer1_Offset
 cpx #73 ; Eleven command bytes plus terminator fit the84-byte queue.
 bcs Done
 lda M3Scratch2
 sta M3HudPower
 lda #1
 sta M3HudValid
 lda #$20
 sta VRAM_Buffer1,x
 lda #$2b
 sta VRAM_Buffer1+1,x
 lda #8
 sta VRAM_Buffer1+2,x
 txa
 clc
 adc #3
 tax
 ldy #6
Chevron:
 lda #$31
 lsr M3HudBits
 bcc :+
 lda #$30
:sta VRAM_Buffer1,x
 inx
 dey
 bne Chevron
 lda #$34
 bit M3Scratch2
 bpl :+
 lda #$32
:sta VRAM_Buffer1,x
 inx
 clc
 adc #1
 sta VRAM_Buffer1,x
 inx
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
Done:rts
.endproc
.proc M3WorldPointer
 tay
 lda M3WorldPtrLo,y
 sta R0
 lda M3WorldPtrHi,y
 sta R1
 rts
.endproc
.proc M3WeaponPalette
 ; Layered item/effect records share the host's world palettes. Recoloring
 ; palette1 here changes every Koopa. Retain this existing two-byte entry
 ; span and its cold call target while retiring the private palette producer.
 rts
 nop
 ldx #5
Find:
 ldy Enemy_Flag,x
 beq Next
 ldy InvPickupOwner,x
 cpy #17
 bne Next
 ldy InvPickup,x
 cpy #$d1
 bcc Next
 cpy #$d7
 bcs Next
 lda ItemColors-$d1,y
 jmp Chosen
Next:dex
 bpl Find
Chosen:cmp M3ItemColor
 bne Queue
 ldy M3ItemColorValid
 bne Done
Queue:sta M3Scratch
 ldx VRAM_Buffer1_Offset
 cpx #$70 ; Unreachable legacy body retained to preserve cold addresses.
 bcs Done
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$15
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 lda #$30
 sta VRAM_Buffer1+3,x
 lda M3Scratch
 sta VRAM_Buffer1+4,x
 lda #$0f
 sta VRAM_Buffer1+5,x
 lda M3Scratch
 sta M3ItemColor
 lda #1
 sta M3ItemColorValid
 txa
 clc
 adc #6
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
Done:rts
ItemColors:.byte $16,$2a,$2a,$2a,$17,$27
.endproc
.popseg
