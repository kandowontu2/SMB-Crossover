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

 ; Dispatch and tiny near helpers live in PROTO_MENU bank66. This body is
; reached through the genuine FarCallCommon transport from that bank.
.proc J2GameMenu
 lda CrossoverMenuState
 cmp #9
 beq J2BuildMenu
 jmp J2InputMenu
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
 beq J2Blank
 lda #0
 rts
J2Blank:
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
J2Palette:
 lda J2MenuPalette,x
 sta PPUDATA
 inx
 cpx #16
 bne J2Palette
 ldx #0
J2Command:
 lda J2TextData,x
 beq J2TextDone
 bit PPUSTATUS
 sta PPUADDR
 inx
 lda J2TextData,x
 sta PPUADDR
 inx
 lda J2TextData,x
 tay
 inx
J2Copy:
 lda J2TextData,x
 sta PPUDATA
 inx
 dey
 bne J2Copy
 jmp J2Command
J2TextDone:
 plp
 lda #10
 sta CrossoverMenuState
 jsr J2QueueCursor
 lda #0
 sta DisableScreenFlag
 rts
J2TextData:
 J2Text $20a8,"CHOOSE YOUR GAME "
 J2Text $2166,"SUPER MARIO BROS."
 J2Text $21c6,"SUPER MARIO BROS 2J"
 J2Text $22e6,"A OR START  PLAY"
 J2Text $2326,"B  CHARACTERS"
 .byte 0
.assert *-J2TextData<256,error,"Campaign static command X must not wrap"
.endproc

.proc J2QueueCursor
 ldx VRAM_Buffer1_Offset
 cpx #76
 bcs J2Done
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
 lda J2Marks,y
 sta VRAM_Buffer1+3,x
 lda J2Marks+1,y
 sta VRAM_Buffer1+7,x
 txa
 clc
 adc #8
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
J2Done:
 rts
J2Marks:.byte $fd,$24,$fd
.endproc

.proc J2InputMenu
 lda CrossoverMenuPressed
 and #B_Button
 beq J2Toggle
 lda CrossoverContinue
 ora #2
 sta CrossoverContinue
 lda #1
 sta CrossoverMenuState
 sta DisableScreenFlag
 lda #0
 rts
J2Toggle:
 lda CrossoverMenuPressed
 and #Up_Dir | Down_Dir | Left_Dir | Right_Dir | Select_Button
 beq J2Confirm
 lda CrossoverContinue
 eor #1
 sta CrossoverContinue
 jsr J2QueueCursor
 lda #Sfx_Bump
 sta Square1SoundQueue
 lda #0
 rts
J2Confirm:
 lda CrossoverMenuPressed
 and #A_Button | Start_Button
 beq J2Wait
 jsr J2CampaignReady
 bcc J2Wait
 farcall FmStartFlags
 farcall CrossoverMenuInput::FmStartReady+18,jmp
J2Wait:
 lda #0
 rts
.endproc

; Deliberate source-component guard. Until the complete engine is linked,
; choosing2J must NOT silently launch SMB1 under an incorrect game label.
.proc J2CampaignReady
 lda CrossoverContinue
 and #1
 bne J2Pending
 sec
 rts
J2Pending:
 clc
 rts
.endproc
J2MenuPalette:
 .byte $0f,$00,$10,$30,$0f,$30,$30,$30
 .byte $0f,$28,$28,$28,$0f,$21,$11,$21
J2MenuEnd:
.assert J2MenuEnd <= $bef0,lderror,"Campaign frontend exceeds root filler grant"
