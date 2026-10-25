; NES HUD/pause layout is an SMB adaptation; numeric rules remain nativeZ2.
.pushseg
.segment "Z2_LOGIC"
.proc Z2UiTickGate
 jsr Z2IsActive
 bcs Active
 farcall InventoryUiTick,jmp
Active:
 lda OperMode
 cmp #1
 jne Done
 lda GameEngineSubroutine
 cmp #8
 jne Done
 jsr Z2EnsureInit
 jsr Z2PanelSync
 lda Z2PanelPending
 cmp #2
 jeq Done
 lda SavedJoypad1Bits
 eor Z2UiPrevious
 and SavedJoypad1Bits
 sta R4
 sta Z2PanelFresh
 lda SavedJoypad1Bits
 sta Z2UiPrevious
 inc Z2MeterCursor
 lda Z2MeterCursor
 jsr Z2RefillA
 jsr Z2ExpTick
 lda Z2PanelFresh
 sta R4
 lda GamePauseStatus
 and #1
 jne Paused
 lda Z2UiState
 beq Live
 lda #0
 sta Z2UiState
 lda Z2Selection
 and #$0f ; original pause-close releases lastcast cache.
 sta Z2Selection
Live:
 lda Z2HurtTimer
 beq :+
 dec Z2HurtTimer
:
 lda Z2SpecialFlash
 beq :+
 dec Z2SpecialFlash
:
 lda Z2SfxTimer
 beq :+
 dec Z2SfxTimer
:
 lda R4
 and #Select_Button
 beq ExpMenu
 lda Z2Selection
 and #7
 jsr Z2TryCast
 bcc ExpMenu
 lda #Sfx_PowerUpGrab
 sta Square2SoundQueue
ExpMenu:
 ldx #2
Check:
 stx R4
 lda BitMasks,x
 and Z2DeferredMask
 bne NextCategory
 txa
 jsr Z2Threshold
 sta R0
 sty R1
 lda Z2ExpLo
 sec
 sbc R0
 lda Z2ExpHi
 sbc R1
 bcs OpenStats
 ldx R4
NextCategory:
 dex
 bpl Check
Done:rts
OpenStats:
 lda #$81
 sta Z2UiState
 lda R4
 sta Z2UiCursor
 lda GamePauseStatus
 ora #1
 sta GamePauseStatus
 jmp Z2Hud
Paused:
 lda Z2UiState
 bmi MenuReady
 lda #$81
 sta Z2UiState
MenuReady:
 lda Z2PanelFresh
 and #B_Button
 jne Defer
 lda R4
 and #Left_Dir|Right_Dir
 beq Navigation
 lda Z2UiState
 eor #1
 sta Z2UiState
Navigation:
 lda Z2UiState
 and #1
 bne Stats
 lda R4
 and #Up_Dir|Down_Dir
 beq SpellConfirm
 lda Z2Selection
 and #7
 pha
 lda Z2PanelFresh
 and #Up_Dir
 tay
 pla
 cpy #Up_Dir
 bne SpellDown
 sec
 sbc #1
 jmp SpellReady
SpellDown:clc
 adc #1
SpellReady:and #7
 sta R0
 tax
 lda BitMasks,x
 and Z2LearnedSpells
 bne Learned
 ; Bounded scan in the requested direction; never select a missing spell.
 ldx #8
FindSpell:
 dec R0
 lda Z2PanelFresh
 and #Up_Dir
 bne CheckSpell
 inc R0
 inc R0
CheckSpell:
 lda R0
 and #7
 sta R0
 tay
 lda BitMasks,y
 and Z2LearnedSpells
 bne Learned
 dex
 bne FindSpell
 jmp Hud
Learned:
 lda Z2Selection
 and #$f8
 ora R0
 sta Z2Selection
 jmp Hud
SpellConfirm:
 lda Z2PanelFresh
 and #A_Button
 jeq Hud
 jmp Close
Stats:
 lda R4
 and #Up_Dir|Down_Dir
 beq Purchase
 lda Z2UiCursor
 pha
 lda Z2PanelFresh
 and #Up_Dir
 tay
 pla
 cpy #Up_Dir
 bne StatDown
 sec
 sbc #1
 jmp StatReady
StatDown:clc
 adc #1
StatReady:and #3
 sta Z2UiCursor
Purchase:
 lda R4
 and #A_Button
 beq Hud
 lda Z2UiCursor
 cmp #3
 beq Defer
 jsr Z2LevelUp
 bcc Hud
 lda #0
 sta Z2DeferredMask
 lda Z2Selection
 and #7
 sta Z2Selection
 jmp Close
Defer:
 jsr Z2Defer
 jcc Hud
Close:
 lda GamePauseStatus
 and #$fe
 sta GamePauseStatus
 lda #0
 sta Z2UiState
Hud:jmp Z2Hud
.endproc

.proc Z2Hud
 lda GamePauseStatus
 and #1
 jeq OrdinaryHud
 jmp Z2PanelTick
OrdinaryHud:
 jsr Z2PanelSync
 lda Z2PanelPending
 cmp #2
 bne HudReady
 rts
HudReady:
 lda OperMode
 cmp #1
 jne Done
 lda DisableScreenFlag
 jne Done
 ; Native terrain and numeric packets have priority. Do not append a
 ; duplicate live pane while the area renderer owns the other queue.
 lda Z2HudCacheValid
 beq Changed
 lda Z2Hp
 cmp Z2HudCacheHp
 bne Changed
 lda Z2Mp
 cmp Z2HudCacheMp
 bne Changed
 lda Z2ExpLo
 cmp Z2HudCacheExpLo
 bne Changed
 lda Z2ExpHi
 cmp Z2HudCacheExpHi
 bne Changed
 lda Z2Selection
 and #7
 cmp Z2HudCacheSpell
 jeq Done
Changed:
 ldx VRAM_Buffer1_Offset
 jne Done
 lda Z2Hp
 sta Z2HudCacheHp
 lda Z2Mp
 sta Z2HudCacheMp
 lda Z2ExpLo
 sta Z2HudCacheExpLo
 lda Z2ExpHi
 sta Z2HudCacheExpHi
 lda Z2Selection
 and #7
 sta Z2HudCacheSpell
 lda #1
 sta Z2HudCacheValid
 lda #$20
 sta VRAM_Buffer1,x
 lda #$42
 sta VRAM_Buffer1+1,x
 lda #14
 sta VRAM_Buffer1+2,x
 inx
 inx
 inx
 lda TextHP
 jsr Put
 lda TextHP+1
 jsr Put
 lda Z2Hp
 jsr Decimal3
 lda #$24
 jsr Put
 lda TextMP
 jsr Put
 lda TextMP+1
 jsr Put
 lda Z2Mp
 jsr Decimal3
 lda #$24
 jsr Put
 jsr Put
 jsr Put
 jmp Row2
Row2:
 lda #$20
 sta VRAM_Buffer1,x
 lda #$62
 sta VRAM_Buffer1+1,x
 lda #14
 sta VRAM_Buffer1+2,x
 inx
 inx
 inx
 jsr SpellName
 lda TextExp
 jsr Put
 jsr Exp5
 lda #$24
 jsr Put
 jmp Finish
Finish:
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
Done:rts
Put:sta VRAM_Buffer1,x
 inx
 rts
Decimal3:
 ldy #0
Hundreds:cmp #100
 bcc Tens
 sbc #100
 iny
 bne Hundreds
Tens:pha
 tya
 jsr Put
 pla
 ldy #0
Ten:cmp #10
 bcc Ones
 sbc #10
 iny
 bne Ten
Ones:pha
 tya
 jsr Put
 pla
 jmp Put
SpellName:
 lda Z2Selection
 and #7
 sta R0
 asl
 asl
 asl
 sec
 sbc R0
 tay
 lda #7
 sta R2
NameLoop:lda SpellNames,y
 jsr Put
 iny
 dec R2
 bne NameLoop
 rts
Exp5:
 lda Z2ExpLo
 sta R0
 lda Z2ExpHi
 sta R1
Number5:
 ldy #0
Digit:
 lda #0
 sta R2
Subtract:
 lda R0
 sec
 sbc PowersLo,y
 sta R3
 lda R1
 sbc PowersHi,y
 bcc DigitReady
 sta R1
 lda R3
 sta R0
 inc R2
 jmp Subtract
DigitReady:lda R2
 jsr Put
 iny
 cpy #5
 bcc Digit
 rts
TextHP:.byte "HP"
TextMP:.byte "MP"
TextAML:.byte "AML"
TextExp:.byte "E"
TextNeed:.byte "N"
TextCost:.byte "COST"
StatNames:.byte "AMLC"
SpellNames:.byte "SHIELD ","JUMP   ","LIFE   ","FAIRY  ","FIRE   ","REFLECT","SPELL  ","THUNDER"
PowersLo:.byte <10000,<1000,<100,<10,<1
PowersHi:.byte >10000,>1000,>100,>10,>1
.endproc
.popseg
