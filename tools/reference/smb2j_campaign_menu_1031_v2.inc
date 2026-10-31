; Private frontend component. No SMB2J engine admission is implied.
; Root owns only the former CHAR_SELECT filler B640..<BEF0.
.assert * <= $b640,lderror,"Campaign menu overlaps existing helper"
.res $b640-$b49b-(*-FmCfHelperStart),$ff
J2MenuStart:
.macro J2Text address,text
 .local Begin,End
 .byte >address,<address,End-Begin
Begin:.byte text
End:
.endmacro

.proc J2MenuDispatch
 cmp #1
 jeq CrossoverMenuInput::BuildScreen
 cmp #2
 jeq CrossoverMenuInput::SelectInput
 cmp #3
 jeq CrossoverMenuInput::BuildOptions
 cmp #4
 jeq CrossoverMenuInput::OptionsInput
 cmp #5
 jeq CrossoverMenuInput::BuildOptions
 cmp #6
 jeq CrossoverMenuInput::CheatsInput
 cmp #7
 jeq CrossoverMenuInput::BuildOptions
 cmp #8
 jeq CrossoverMenuInput::SoundInput
 cmp #9
 jeq J2BuildMenu
 cmp #10
 jeq J2InputMenu
 jmp CrossoverMenuInput::J2LegacyTitleCheck
.endproc

; Continue is exactly the old A-button bit. Bit0 now retains campaign choice;
; bit1 is a one-shot return-to-roster marker. No new global/ZP allocation.
.proc J2ContinueValue
 lda CrossoverContinue
 and #A_Button
 rts
.endproc

.proc J2SelectionReset
 lda CrossoverContinue
 and #2
 beq Fresh
 lda CrossoverContinue
 and #$fd
 sta CrossoverContinue
 rts
Fresh:
 lda #0
 sta FmAlts
 sta FmGroups
 rts
.endproc

.proc J2OpenCampaign
 lda CrossoverContinue
 and #A_Button
 sta CrossoverContinue
 lda #9
 sta CrossoverMenuState
 lda #1
 sta DisableScreenFlag
 lda #0
 rts
.endproc

.proc J2BuildMenu
 lda Mirror_PPUMASK
 and #$18
 beq Blank
 lda #0
 rts
Blank:
 php
 sei
 farcall InitializeNameTables
 farcall MoveAllSpritesOffscreen
 farcall FmNativePrepare
 lda #$3c
 sta AreaChrBank
 lda #$3d
 sta AreaChrBank+1
 lda #$3e
 sta AreaChrBank+2
 lda #$3f
 sta AreaChrBank+3
 inc ReloadCHRBank
 lda PPUSTATUS
 lda #$3f
 sta PPUADDR
 lda #0
 sta PPUADDR
 ldx #0
Palette:
 lda SelectPalette,x
 sta PPUDATA
 inx
 cpx #16
 bne Palette
 ldx #0
Command:
 lda Text,x
 beq TextDone
 bit PPUSTATUS
 sta PPUADDR
 inx
 lda Text,x
 sta PPUADDR
 inx
 lda Text,x
 tay
 inx
Copy:
 lda Text,x
 sta PPUDATA
 inx
 dey
 bne Copy
 jmp Command
TextDone:
 plp
 lda #10
 sta CrossoverMenuState
 jsr J2QueueCursor
 lda #0
 sta DisableScreenFlag
 rts
Text:
 J2Text $20a8,"CHOOSE YOUR GAME "
 J2Text $2166,"SUPER MARIO BROS."
 J2Text $21c6,"SUPER MARIO BROS 2J"
 J2Text $22e6,"A OR START  PLAY"
 J2Text $2326,"B  CHARACTERS"
 .byte 0
.assert *-Text<256,error,"Campaign static command X must not wrap"
.endproc

.proc J2QueueCursor
 ldx VRAM_Buffer1_Offset
 cpx #76
 bcs Done
 lda #$21
 sta VRAM_Buffer1,x
 sta VRAM_Buffer1+4,x
 lda #$64
 sta VRAM_Buffer1+1,x
 lda #$c4
 sta VRAM_Buffer1+5,x
 lda #1
 sta VRAM_Buffer1+2,x
 sta VRAM_Buffer1+6,x
 lda CrossoverContinue
 and #1
 tay
 lda Marks,y
 sta VRAM_Buffer1+3,x
 lda Marks+1,y
 sta VRAM_Buffer1+7,x
 txa
 clc
 adc #8
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
Done:
 rts
Marks:.byte $fd,$24,$fd
.endproc

.proc J2InputMenu
 lda CrossoverMenuPressed
 and #B_Button
 beq Toggle
 lda CrossoverContinue
 ora #2
 sta CrossoverContinue
 lda #1
 sta CrossoverMenuState
 sta DisableScreenFlag
 lda #0
 rts
Toggle:
 lda CrossoverMenuPressed
 and #Up_Dir | Down_Dir | Left_Dir | Right_Dir | Select_Button
 beq Confirm
 lda CrossoverContinue
 eor #1
 sta CrossoverContinue
 jsr J2QueueCursor
 lda #Sfx_Bump
 sta Square1SoundQueue
 lda #0
 rts
Confirm:
 lda CrossoverMenuPressed
 and #A_Button | Start_Button
 beq Wait
 jsr J2CampaignReady
 bcc Wait
 farcall FmStartFlags
 jmp CrossoverMenuInput::FmStartReady+18
Wait:
 lda #0
 rts
.endproc

; Deliberate source-component guard. Until the complete engine is linked,
; choosing2J must NOT silently launch SMB1 under an incorrect game label.
.proc J2CampaignReady
 lda CrossoverContinue
 and #1
 bne Pending
 sec
 rts
Pending:
 clc
 rts
.endproc
J2MenuEnd:
.assert J2MenuEnd <= $bef0,lderror,"Campaign frontend exceeds root filler grant"
