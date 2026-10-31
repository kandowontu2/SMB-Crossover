; Same-bank dispatcher and short helpers. No unbanked near call crosses
; PROTO_MENU66 / CHAR_SELECT29. Exact existing116B PROTO tail only.
.assert * <= $b0c0,lderror,"Campaign dispatch overlaps roster RLE"
.res $c18-(*-CrossoverMenuInput),$ff
J2ProtoStart:
.proc J2MenuDispatch
 cmp #9
 bcc J2OldRoutes
 farcall J2GameMenu,jmp
J2OldRoutes:
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
 jmp CrossoverMenuInput::J2LegacyTitleCheck
.endproc
.proc J2ContinueValue
 lda CrossoverContinue
 and #A_Button
 rts
.endproc
.proc J2SelectionReset
 lda CrossoverContinue
 and #2
 beq J2Fresh
 lda CrossoverContinue
 and #$fd
 sta CrossoverContinue
 rts
J2Fresh:
 lda #0
 sta FmAlts
 sta FmGroups
 rts
.endproc
J2ProtoEnd:
.assert J2ProtoEnd <= $b134,lderror,"Campaign near helpers exceed116B tail"
