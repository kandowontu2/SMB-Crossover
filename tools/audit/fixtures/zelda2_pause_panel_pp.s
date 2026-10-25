; Original Zelda II font/borders and level-up panel, with a separate spell page.
; Only active Zelda II Link borrows these otherwise inactive profile bytes.
Z2PanelActive=$5d84
Z2PanelChr=$5d85
Z2PanelMode=$5d86
Z2PanelScreen=$5d87
Z2PanelOrigin=$5d88
Z2PanelRow=$5d89
Z2PanelCol=$5d8a
Z2PanelIndex=$5d8b
Z2PanelLo=$5d8c
Z2PanelHi=$5d8d
Z2PanelPage=$5d8e
Z2PanelCursor=$5d8f
Z2PanelOldRow=$5d90
Z2PanelWork=$5d91
Z2PanelDigit=$5d92
Z2PanelFresh=$5d93
Z2ThresholdCategory=$5d94
Z2PanelPending=$5d95
Z2PanelPalette=$5dc0
Z2PanelOam=$5c00
Z2PanelTiles=$5c40             ;196bytes; only64OAM Y bytes need backup
Z2PanelAttrs=$5d04             ;128bytes, both native nametables
Z2DeferredMask=$5e1b           ; formerly unused reward-toast byte
.assert Z2PanelOam+64=Z2PanelTiles,error,"OAM Y-only backup extent"
.assert Z2PanelTiles+196=Z2PanelAttrs,error,"Panel tile extent"
.assert Z2PanelAttrs+128=Z2PanelActive,error,"Panel attribute extent"
.assert Z2PanelPalette+16<$5e00,error,"Keep all cached world data out of other character records"
.pushseg
.segment "Z2_LOGIC"
.proc Z2PanelSync
 lda Z2PanelPending
 cmp #2
 beq Close
 lda Z2PanelActive
 bne Active
 lda Z2PanelPending
 jeq Done
 lda GamePauseStatus
 and #1
 jne Done
 ; Start can cancel an opening pane before its blank transaction begins.
 jmp Z2PanelUnblank
Active:
 lda GamePauseStatus
 and #1
 jne Done
Close:
 lda GamePauseStatus
 ora #1
 sta GamePauseStatus
 lda Z2PanelPending
 beq RequestClose
 lda #2
 sta Z2PanelPending
RequestClose:
 lda #2
 jsr Z2PanelReady
 jcc Done
 ldx #0
 ldy #0
Oam:
 lda Z2PanelOam,x
 sta $200,y
 inx
 iny
 iny
 iny
 iny
 bne Oam
 lda #0
 sta OAMADDR
 lda #2
 sta $4014
 jsr Z2PanelAttributesRestore
 lda #0
 sta Z2PanelIndex
 sta Z2PanelRow
Rows:
 lda #0
 sta Z2PanelCol
Cells:
 jsr Z2PanelAddress
 jsr Z2PanelSetAddress
 ldx Z2PanelIndex
 lda Z2PanelTiles,x
 sta PPUDATA
 inc Z2PanelIndex
 inc Z2PanelCol
 lda Z2PanelCol
 cmp #14
 bcc Cells
 inc Z2PanelRow
 lda Z2PanelRow
 cmp #14
 bcc Rows
 lda #$3f
 sta PPUADDR
 lda #0
 sta PPUADDR
 ldx #0
Palette:
 lda Z2PanelPalette,x
 sta PPUDATA
 inx
 cpx #16
 bcc Palette
 lda Z2PanelChr
 sta CurrentCHRBank+11
 lda Z2PanelMode
 sta X5ChrMode+11
 inc ReloadCHRBank
 lda #0
 sta Z2PanelActive
 lda GamePauseStatus
 and #$fe
 sta GamePauseStatus
 jsr Z2PanelUnblank
Done:rts
.endproc
.proc Z2PanelTick
 lda Z2PanelPending
 cmp #2
 jeq Done
 lda GamePauseStatus
 and #1
 beq Done
 lda Z2PanelActive
 beq Open
 lda Z2PanelPending
 cmp #3
 jeq Redraw
 lda Z2UiState
 and #1
 cmp Z2PanelPage
 jne Redraw
 jsr Z2PanelCursorValue
 cmp Z2PanelCursor
 beq Done
 ; Cursor navigation is queued within the native NMI budget: no screen blank.
 ldx VRAM_Buffer1_Offset
 cpx #76
 bcs Done
 lda Z2PanelCursor
 jsr Z2PanelCursorRow
 lda Z2PanelRow
 sta Z2PanelOldRow
 lda #$f4
 jsr Z2PanelQueueCursor
 jsr Z2PanelCursorValue
 sta Z2PanelCursor
 jsr Z2PanelCursorRow
 lda #$fb
 jsr Z2PanelQueueCursor
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
Done:rts
Open:
 lda VRAM_Buffer1_Offset
 ora VRAM_Buffer_AddrCtrl
 bne Done                    ; let the existing queue drain before backup
 lda #1
 jsr Z2PanelReady
 jcc Done
 lda #1
 sta Z2PanelActive
 lda CurrentCHRBank+11
 sta Z2PanelChr
 lda X5ChrMode+11
 sta Z2PanelMode
 lda ScreenLeft_X_Pos
 lsr
 lsr
 lsr
 sta Z2PanelOrigin
 lda ScreenLeft_PageLoc
 and #1
 asl
 asl
 asl
 asl
 asl
 ora Z2PanelOrigin
 clc
 adc #9
 and #63
 sta Z2PanelOrigin
 ldx #0
 ldy #0
Oam:
 lda $200,y
 sta Z2PanelOam,x
 lda #$f8
 sta $200,y
 inx
 iny
 iny
 iny
 iny
 bne Oam
 lda #0
 sta OAMADDR
 lda #2
 sta $4014
 lda #0
 sta Z2PanelIndex
 sta Z2PanelRow
Rows:
 lda #0
 sta Z2PanelCol
Cells:
 jsr Z2PanelAddress
 jsr Z2PanelSetAddress
 lda PPUDATA
 lda PPUDATA
 ldx Z2PanelIndex
 sta Z2PanelTiles,x
 inc Z2PanelIndex
 inc Z2PanelCol
 lda Z2PanelCol
 cmp #14
 bcc Cells
 inc Z2PanelRow
 lda Z2PanelRow
 cmp #14
 bcc Rows
 ldx #0
Attr:
 jsr Z2PanelAttributeAddress
 lda PPUDATA
 lda PPUDATA
 sta Z2PanelAttrs,x
 inx
 bpl Attr
 lda #$3f
 sta PPUADDR
 lda #0
 sta PPUADDR
 ldx #0
Palette:
 lda PPUDATA
 sta Z2PanelPalette,x
 inx
 cpx #16
 bcc Palette
 lda #$3f
 sta PPUADDR
 lda #5
 sta PPUADDR
 lda #$30
 sta PPUDATA
 lda #$3f
 sta PPUADDR
 lda #7
 sta PPUADDR
 lda #$0f
 sta PPUDATA
 jmp Draw
Redraw:
 lda VRAM_Buffer1_Offset
 ora VRAM_Buffer_AddrCtrl
 jne Done
 lda #3
 jsr Z2PanelReady
 jcc Done
Draw:
 lda #.lobyte(395)
 sta CurrentCHRBank+11
 lda #$81
 sta X5ChrMode+11
 inc ReloadCHRBank
 lda Z2UiState
 and #1
 sta Z2PanelPage
 jsr Z2PanelCursorValue
 sta Z2PanelCursor
 lda #0
 sta Z2PanelIndex
 sta Z2PanelRow
DrawRows:
 lda #0
 sta Z2PanelCol
DrawCells:
 jsr Z2PanelAddress
 jsr Z2PanelSetAddress
 jsr Z2PanelTile
 sta PPUDATA
 ; The original pane is opaque. Clear only its touched palette quadrants.
 lda Z2PanelRow
 and #1
 bne Next
 lda Z2PanelCol
 beq ClearAttr
 clc
 adc Z2PanelOrigin
 and #1
 bne Next
ClearAttr:
 jsr Z2PanelClearAttribute
Next:
 inc Z2PanelIndex
 inc Z2PanelCol
 lda Z2PanelCol
 cmp #14
 bcc DrawCells
 inc Z2PanelRow
 lda Z2PanelRow
 cmp #14
 bcc DrawRows
 jmp Z2PanelUnblank
.endproc
.proc Z2PanelBlank
 lda #0
 sta $5204
 bit $5204
 sta PPUMASK
 lda Mirror_PPUCTRL
 and #$fb                    ; PPU increment1 throughout this transaction
 sta PPUCTRL
 bit PPUSTATUS
 rts
.endproc
.proc Z2PanelUnblank
 bit PPUSTATUS
 lda #0
 sta PPUSCROLL
 sta PPUSCROLL
 lda Mirror_PPUCTRL
 sta PPUCTRL
 lda Z2PanelScreen
 sta DisableScreenFlag
 lda #0
 sta Z2PanelPending
 ; Native NMI restores rendering/CHR/scroll after this completed publication.
 rts
.endproc
.proc Z2PanelReady
 pha
 lda Z2PanelPending
 bne Wait
 lda DisableScreenFlag
 sta Z2PanelScreen
 lda #1
 sta DisableScreenFlag
 pla
 sta Z2PanelPending
 clc
 rts
Wait:
 pla
 lda Mirror_PPUMASK
 and #$18
 bne NotYet
 ; Native NMI has admitted an entirely blank frame. Disabling its IRQ
 ; and reading/writing PPU memory can no longer disturb a visible HUD split.
 jsr Z2PanelBlank
 sec
 rts
NotYet:clc
 rts
.endproc
.proc Z2PanelAddress
 lda Z2PanelCol
 clc
 adc Z2PanelOrigin
 and #63
 sta Z2PanelWork
 and #31
 sta Z2PanelLo
 lda Z2PanelRow
 clc
 adc #8
 lsr
 lsr
 lsr
 ora #$20
 sta Z2PanelHi
 lda Z2PanelWork
 and #32
 lsr
 lsr
 lsr
 ora Z2PanelHi
 sta Z2PanelHi
 lda Z2PanelRow
 clc
 adc #8
 asl
 asl
 asl
 asl
 asl
 ora Z2PanelLo
 sta Z2PanelLo
 rts
.endproc
.proc Z2PanelSetAddress
 bit PPUSTATUS
 lda Z2PanelHi
 sta PPUADDR
 lda Z2PanelLo
 sta PPUADDR
 rts
.endproc
.proc Z2PanelAttributeAddress
 bit PPUSTATUS
 txa
 and #64
 lsr
 lsr
 lsr
 lsr
 ora #$23
 sta PPUADDR
 txa
 and #63
 ora #$c0
 sta PPUADDR
 rts
.endproc
.proc Z2PanelAttributesRestore
 ldx #0
Loop:
 jsr Z2PanelAttributeAddress
 lda Z2PanelAttrs,x
 sta PPUDATA
 inx
 bpl Loop
 rts
.endproc
.proc Z2PanelClearAttribute
 lda Z2PanelWork
 and #32
 asl
 sta R0
 lda Z2PanelWork
 and #31
 lsr
 lsr
 ora R0
 sta R0
 lda Z2PanelRow
 clc
 adc #8
 and #$fc
 asl
 ora R0
 tax
 jsr Z2PanelAttributeAddress
 lda PPUDATA
 lda PPUDATA
 sta R0
 lda Z2PanelRow
 and #2
 ora #0
 asl
 sta R1
 lda Z2PanelWork
 and #2
 ora R1
 lsr
 tay
 lda R0
 and Masks,y
 ora Values,y
 sta R0
 jsr Z2PanelAttributeAddress
 lda R0
 sta PPUDATA
 rts
Masks:.byte $fc,$f3,$cf,$3f
Values:.byte 1,4,16,64
.endproc
.proc Z2PanelCursorValue
 lda Z2UiState
 and #1
 beq Spell
 lda Z2UiCursor
 rts
Spell:lda Z2Selection
 and #7
 rts
.endproc
.proc Z2PanelCursorRow
 ldy Z2PanelPage
 beq Spell
 cmp #3
 beq Cancel
 asl
 clc
 adc #4
 bne Store
Cancel:lda #11
 bne Store
Spell:clc
 adc #2
Store:sta Z2PanelRow
 lda #1
 ldy Z2PanelPage
 beq Col
 lda #6
Col:sta Z2PanelCol
 rts
.endproc
.proc Z2PanelQueueCursor
 pha
 phx
 jsr Z2PanelAddress
 plx
 lda Z2PanelHi
 sta VRAM_Buffer1,x
 lda Z2PanelLo
 sta VRAM_Buffer1+1,x
 lda #1
 sta VRAM_Buffer1+2,x
 pla
 sta VRAM_Buffer1+3,x
 inx
 inx
 inx
 inx
 rts
.endproc
.proc Z2PanelTile
 ldy Z2PanelIndex
 lda Z2PanelPage
 beq Spell
 lda Z2PanelRow
 cmp #2
 bne Stat
 lda Z2PanelCol
 sec
 sbc #7
 cmp #5
 bcs Static
 sta Z2PanelDigit
 jsr Z2NextThreshold
 jmp Number
Stat:
 lda Z2PanelRow
 sec
 sbc #4
 cmp #6
 bcs Static
 pha
 lsr
 pha
 lda Z2PanelCol
 cmp #11
 bne Cost
 tsx
 lda $102,x                  ; row offset saved below the category
 and #1
 beq Cost
 pla
 jsr Z2GetLevel
 clc
 adc #$d1
 sta Z2PanelWork
 pla
 and #1
 beq Static
 lda Z2PanelWork
 rts
Cost:
 pla
 tax
 pla
 and #1
 bne Static
 lda Z2PanelCol
 sec
 sbc #1
 cmp #4
 bcs Static
 clc
 adc #1
 sta Z2PanelDigit
 txa
 jsr Z2Threshold
 sta R0
 sty R1
 jmp Number
Static:
 ldy Z2PanelIndex
 lda Z2PanelStats,y
 jmp Cursor
Spell:
 lda Z2PanelRow
 sec
 sbc #2
 cmp #8
 bcs StaticSpell
 tax
 lda BitMasks,x
 and Z2LearnedSpells
 beq Locked
 lda Z2PanelCol
 sec
 sbc #10
 cmp #3
 bcs StaticSpell
 clc
 adc #2
 sta Z2PanelDigit
 txa
 jsr Z2SpellCost
 sta R0
 lda #0
 sta R1
 jmp Number
Locked:
 lda Z2PanelCol
 beq StaticSpell
 cmp #13
 beq StaticSpell
 lda #$f4
 rts
StaticSpell:
 ldy Z2PanelIndex
 lda Z2PanelSpells,y
Cursor:
 pha
 lda Z2PanelRow
 sta Z2PanelOldRow
 lda Z2PanelCol
 pha
 lda Z2PanelCursor
 jsr Z2PanelCursorRow
 pla
 cmp Z2PanelCol
 bne Restore
 lda Z2PanelRow
 cmp Z2PanelOldRow
 bne Restore
 pla
 lda #$fb
 jmp Row
Restore:pla
Row:pha
 lda Z2PanelOldRow
 sta Z2PanelRow
 ldy Z2PanelIndex
 ; Restore column from the loop's immutable cell index, rather than the
 ; temporary cursor column. The caller advances that real column next.
 tya
Col:
 cmp #14
 bcc ColReady
 sbc #14
 bcs Col
ColReady:sta Z2PanelCol
 pla
 rts
Number:
 ldy #0
Digit:
 lda #$d0
 sta R2
Subtract:
 lda R0
 sec
 sbc Z2Hud::PowersLo,y
 sta R3
 lda R1
 sbc Z2Hud::PowersHi,y
 bcc Ready
 sta R1
 lda R3
 sta R0
 inc R2
 jmp Subtract
Ready:
 cpy Z2PanelDigit
 beq Return
 iny
 bne Digit
Return:lda R2
 rts
.endproc
.proc Z2NextThreshold
 lda #$ff
 sta R0
 sta R1
 ldx #0
Loop:
 stx Z2ThresholdCategory
 lda BitMasks,x
 and Z2DeferredMask
 bne Next
 txa
 jsr Z2Threshold
 sta R2
 sty R3
 sec
 sbc R0
 tya
 sbc R1
 bcs Next
 lda R2
 sta R0
 lda R3
 sta R1
Next:ldx Z2ThresholdCategory
 inx
 cpx #3
 bcc Loop
 rts
.endproc
.proc Z2Defer
 jsr Z2NextThreshold
 lda Z2ExpLo
 sec
 sbc R0
 lda Z2ExpHi
 sbc R1
 bcc Close                   ; voluntary menu below next threshold
 lda Z2DeferredMask
 sta R4
 ldx #0
Loop:
 stx Z2ThresholdCategory
 txa
 jsr Z2Threshold
 cmp R0
 bne Next
 cpy R1
 bne Next
 ldx Z2ThresholdCategory
 lda BitMasks,x
 ora R4
 sta R4
Next:ldx Z2ThresholdCategory
 inx
 cpx #3
 bcc Loop
 lda R4
 cmp #7
 beq No                      ; native pane cannot cancel its last option
 sta Z2DeferredMask
Close:sec
 rts
No:clc
 rts
.endproc
.include "zelda2_pause_tables.inc"
.popseg
.pushseg
.segment "Z2_UI_CHR"
.incbin "chr/characters/zelda2-pause-font.chr"
.popseg
