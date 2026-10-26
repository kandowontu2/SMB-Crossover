; Parodius-only queue cache. All old instructions/data retain their addresses.
.pushseg
.segment "PN_HUD_GATE"
.proc PnHudGate
 lda DisableScreenFlag
 bne Done
 lda VvVariant
 asl
 ora #1
 cmp InvHudActive
 bne Slow
 lda VvHudDirty
 bne Slow
 ; Clean valid labels: renew exactly the original physical font lease.
 lda VvVariant
 clc
 adc #.lobyte(395)
 sta InvHudPhysical
 lda X5HudChrUpper
 bmi CleanZero
 lda #.hibyte(396)
 sta X5HudChrUpper
CleanZero:
 lda #0
Done:rts
Slow:
 ; The normal farcall macro owns A. Keep A77 tables mapped and own C
 ; explicitly, using the same shadow-before-hardware NMI-safe convention.
 lda CurrentBankC
 pha
 lda #.bank(PnHudQueue) | MMC5_PRG_ROM
 sta CurrentBankC
 sta MMC5_PRG_BANK_C
 jsr PnHudQueue
 pla
 sta CurrentBankC
 sta MMC5_PRG_BANK_C
 rts
.endproc
.proc PnHudCancelLife
 ; Original callers have A=0. Keep A/XY/C/V and original store's NZ.
 sta InvHudActive
 lda X5HudChrUpper
 and #3
 sta X5HudChrUpper
 lda #0
 rts
.endproc
.proc PnHudNewLife
 lda #0
 jsr PnHudCancelLife
 tax
 rts
.endproc
.assert *-PnHudGate <=106,error,"Use only verified A77 tail"
.popseg
.pushseg
.segment "PN_HUD_INIT"
.proc PnHudInventoryInit
 pha
 lda X5HudChrUpper
 and #3
 sta X5HudChrUpper
 pla
 inc InvDirty
 rts
.endproc
.popseg
.pushseg
.segment "PN_HUD_TEXT"
.proc PnHudTextCancel
 ; WriteGameText overwrites Buffer1, including live warp-zone delivery.
 ; Keep its original saved-A stack item and exact ASL/TAY continuation.
 pha
 pha
 lda X5HudChrUpper
 bpl Restore
 and #3
 sta X5HudChrUpper
 lda #1
 sta VvHudDirty
Restore:
 pla
 asl
 tay
 jmp WriteGameText+3
.endproc
.assert *-PnHudTextCancel=23,error,"Exact verified bank3 tail"
.popseg
; A77 caller remains mapped while C116 owns the rare foreground helper.
; Pending: Upper=$80|(variant<<2)|1, Active=0, Physical=admission offset.
; Both hardware readers require Active!=0 and mask Upper with AND#3.
.pushseg
.segment "PN_HUD_QUEUE"
.proc PnHudQueue
 lda VvVariant
 cmp #1
 jcc Done
 cmp #4
 jcs Done
 asl
 ora #1
 cmp InvHudActive
 jeq Valid
 lda InvHudActive
 bne Invalid
 lda X5HudChrUpper
 bpl Invalid
 and #$0c
 lsr
 lsr
 cmp VvVariant
 jeq Done ; append already pending: preserve any new meter dirty state
Invalid:
 lda InvHudActive
 beq :+
 inc ReloadCHRBank
:
 lda #0
 sta InvHudActive
 lda X5HudChrUpper
 and #3
 sta X5HudChrUpper
 lda #1
 sta VvHudDirty
 lda PnInitialized
 cmp #$50
 jne Done
 lda PnBombPaletteReady
 cmp #1
 jne Done
 ldx VRAM_Buffer1_Offset
 cpx #0
 jne Done
 stx InvHudPhysical
 lda #$20
 sta VRAM_Buffer1,x
 lda #$22
 sta VRAM_Buffer1+1,x
 lda #28
 sta VRAM_Buffer1+2,x
 lda VvVariant
 sec
 sbc #1
 tay
 lda PnHud::GraphicalOffsets,y
 tay
 lda #28
 sta VvTemp2
Cells:
 lda PnHud::PnHudCells,y
 sta VRAM_Buffer1+3,x
 iny
 inx
 dec VvTemp2
 bne Cells
 inx
 inx
 inx
 jsr Attributes
 lda VvVariant
 asl
 asl
 ora #$81
 sta X5HudChrUpper
 rts
Valid:
 lda X5HudChrUpper
 jmi Done
 lda VvVariant
 clc
 adc #.lobyte(395)
 sta InvHudPhysical
 lda #1
 sta X5HudChrUpper
 lda VvHudDirty
 jeq Done
 ldx VRAM_Buffer1_Offset
 cpx #32
 jcs Done
 txa
 pha
 jsr Attributes
 pla
 asl
 asl
 ora #$81
 sta X5HudChrUpper
 rts
Attributes:
 lda #$23
 sta VRAM_Buffer1,x
 lda #$c0
 sta VRAM_Buffer1+1,x
 lda #8
 sta VRAM_Buffer1+2,x
 txa
 clc
 adc #3
 tax
 lda #1
 sta VvTemp
 ldy #8
Loop:
 lda #$aa
 sta VvTemp2
 lda VvTemp
 and VvMeter
 beq RightNormal
 lda #$a6
 sta VvTemp2
RightNormal:
 lda VvTemp
 lsr
 and VvMeter
 beq LeftNormal
 lda VvTemp2
 and #$fc
 ora #1
 sta VvTemp2
LeftNormal:
 lda VvTemp2
 sta VRAM_Buffer1,x
 inx
 asl VvTemp
 dey
 bne Loop
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 sta VvHudDirty
Done:rts
.endproc

; NMI owns C116, no foreground scratch/SMC or mapping changes. The normal
; gateway's ctrl0 selection starts at Buffer1. At this hook UpdateScreen has
; consumed every byte through the live terminator, before CHR/OAM publication.
.proc PnHudCommitAfterVram
 lda X5HudChrUpper
 bmi Pending
 lda OperMode
 jmp PnPaletteScreenUpdate+13
Pending:
 lda InvHudActive
 jne Return ; ctrl6 may retain an attribute command; pre-guard owns it.
 php
 txa
 pha
 tya
 pha
 lda SelectedCharacter
 cmp #18
 jne Cancel
 lda OperMode
 cmp #1
 jne Cancel
 lda GameEngineSubroutine
 cmp #8
 jne Cancel
 lda DisableScreenFlag
 jne Cancel
 lda PnInitialized
 cmp #$50
 jne Cancel
 lda PnBombPaletteReady
 cmp #1
 jne Cancel
 lda VvVariant
 cmp #1
 jcc Cancel
 cmp #4
 jcs Cancel
 asl
 asl
 ora #$81
 cmp X5HudChrUpper
 jne Cancel
 lda VRAM_Buffer_AddrCtrl
 cmp #6
 jeq Deferred
 cmp #0
 jne Cancel
 lda InvHudActive
 jne Cancel
 ldx InvHudPhysical
 cpx #1
 jcs Cancel
 lda VRAM_Buffer1_Offset
 cmp #84
 jcs Cancel
 sec
 sbc InvHudPhysical
 jcc Cancel
 cmp #42
 jne Cancel
 ; Check consumed pointer, including Buffer1's actual AF-page crossing.
 lda VRAM_Buffer1_Offset
 clc
 adc #<VRAM_Buffer1
 tax
 lda #>VRAM_Buffer1
 adc #0
 cmp NmiR1
 jne Cancel
 txa
 cmp NmiR0
 jne Cancel
 ldx InvHudPhysical
 lda VRAM_Buffer1,x
 cmp #$20
 bne Cancel
 lda VRAM_Buffer1+1,x
 cmp #$22
 bne Cancel
 lda VRAM_Buffer1+2,x
 cmp #28
 bne Cancel
 lda VRAM_Buffer1+31,x
 cmp #$23
 bne Cancel
 lda VRAM_Buffer1+32,x
 cmp #$c0
 bne Cancel
 lda VRAM_Buffer1+33,x
 cmp #8
 bne Cancel
 lda VvVariant
 clc
 adc #.lobyte(395)
 sta InvHudPhysical
 lda VvVariant
 asl
 ora #1
 sta InvHudActive
 lda #1
 sta X5HudChrUpper
 inc ReloadCHRBank
 jmp Deferred
Cancel:
 lda X5HudChrUpper
 and #3
 sta X5HudChrUpper
 lda #0
 sta InvHudActive
 lda #1
 sta VvHudDirty
Deferred:
 pla
 tay
 pla
 tax
 plp
Return:
 lda OperMode
 jmp PnPaletteScreenUpdate+13
.endproc
.popseg
; Guard the final assembled packet, after every native foreground producer.
; Full labels are only queued first at offset0. Attribute admissions carry
; offset0..31 in Upper bits2..6 with Active!=0 and the physical font retained.
; All nonpending identities pay only this LDA/branch/JMP before native code.
.pushseg
.segment "PN_HUD_QUEUE"
.proc PnHudPreUpdateScreen
 lda X5HudChrUpper
 bmi Pending
Native:
 jmp PnPaletteScreenUpdate
Pending:
 lda InvHudActive
 jne AttrControl
 ; Common first-full case: ctrl0's initial pointer is owned by the
 ; resident VRAM_AddrTable selection. The post-flush commit still checks
 ; its consumed end pointer and six headers before leasing the font.
 lda VRAM_Buffer_AddrCtrl
 bne FullControl
 lda VRAM_Buffer1_Offset
 cmp #42
 bne FullGeneral
 lda GameEngineSubroutine
 cmp #8
 bne FullGeneral
 lda DisableScreenFlag
 bne FullGeneral
 jmp Native
FullControl:
 cmp #6
 jeq Native
 jmp Cancel
FullGeneral:
 lda NmiR0
 cmp #<VRAM_Buffer1
 jne Cancel
 lda NmiR1
 cmp #>VRAM_Buffer1
 jne Cancel
 lda InvHudPhysical
 jne Cancel
 lda VRAM_Buffer1_Offset
 cmp #42
 jcc Cancel
 jmp DeferFull
AttrControl:
 lda VRAM_Buffer_AddrCtrl
 cmp #6
 beq Native ; Buffer2 flush cannot consume or discard the pending Buffer1.
 cmp #0
 jne Cancel
 lda NmiR0
 cmp #<VRAM_Buffer1
 jne Cancel
 lda NmiR1
 cmp #>VRAM_Buffer1
 jne Cancel
 jmp Attr
 ; A full first-HUD append has no prefix. Never combine it with any later
 ; timer/score/palette/bomb command; those original commands still flush.
DeferFull:
 lda VRAM_Buffer1
 cmp #$20
 jne Cancel
 lda VRAM_Buffer1+1
 cmp #$22
 jne Cancel
 lda VRAM_Buffer1+2
 cmp #28
 jne Cancel
 lda VRAM_Buffer1+31
 cmp #$23
 jne Cancel
 lda VRAM_Buffer1+32
 cmp #$c0
 jne Cancel
 lda VRAM_Buffer1+33
 cmp #8
 jne Cancel
 lda #<(VRAM_Buffer1+42)
 sta NmiR0
 lda #>(VRAM_Buffer1+42)
 sta NmiR1
 clv ; native nonempty Buffer1's final pointer high-ADC always clears V.
 jmp Cancel
Attr:
 lda X5HudChrUpper
 and #$7c
 lsr
 lsr
 tax
 lda VRAM_Buffer1_Offset
 cmp #84
 jcs Cancel
 txa
 clc
 adc #11
 cmp VRAM_Buffer1_Offset
 bcc ExtentChecked
 beq ExtentChecked
 jmp Cancel
ExtentChecked:
 lda VRAM_Buffer1,x
 cmp #$23
 jne Cancel
 lda VRAM_Buffer1+1,x
 cmp #$c0
 jne Cancel
 lda VRAM_Buffer1+2,x
 cmp #8
 jne Cancel
 lda VRAM_Buffer1_Offset
 cmp #32
 bcs DeferAttr
 ; Success does not erase Dirty raised by a later meter/pickup owner.
 lda X5HudChrUpper
 and #3
 sta X5HudChrUpper
 jmp Native
DeferAttr:
 cpx #0
 beq AfterPrefix
 ; Flush the unmodified prefix through native UpdateScreen, ending only
 ; at the temporary attribute header. No foreground can observe this.
 lda #0
 sta VRAM_Buffer1,x
 jsr UpdateScreen
 lda X5HudChrUpper
 and #$7c
 lsr
 lsr
 tax
 lda #$23
 sta VRAM_Buffer1,x
AfterPrefix:
 txa
 clc
 adc #<(VRAM_Buffer1+11)
 sta NmiR0
 lda #>(VRAM_Buffer1+11)
 adc #0
 sta NmiR1
Cancel:
 lda X5HudChrUpper
 and #3
 sta X5HudChrUpper
 lda #1
 sta VvHudDirty
 jmp Native
.endproc
.popseg
