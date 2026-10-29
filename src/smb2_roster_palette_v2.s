; Additive to frozen v1. Consume this endpoint through a normal farcall:
; pointers remain in the intentional C80 art lease after A is restored.
.pushseg
.segment "PARODIUS_BELLS"
.export S2PalettePointerC,S2PaletteCCodeStart,S2PaletteCCodeEnd
S2PaletteCCodeStart:
.proc S2PalettePointerC
 lda SelectedCharacter
 cmp #25
 bne No
 lda S2NativeCharacter
 cmp #4
 bcs No
 jsr S2GraphicsBank
 lda S2NativeCharacter
 asl
 asl
 clc
 adc #<S2CharacterPalettesC
 sta R0
 lda #>S2CharacterPalettesC
 adc #0
 sta R1
 lda #<S2EyeObjectRoleC
 sta R2
 lda #>S2EyeObjectRoleC
 sta R3
 sec
 rts
No:clc
 rts
.endproc
S2PaletteCCodeEnd:
.segment "CD_GFX"
.export S2CharacterPalettesC,S2EyeObjectRoleC,S2PaletteCDataEnd
S2CharacterPalettesC:
 .byte $0f,$01,$16,$27,$0f,$06,$25,$36
 .byte $0f,$01,$30,$27,$0f,$01,$2a,$36
S2EyeObjectRoleC:
 .byte $0f,$30,$16,$0f          ; original world1 eye/object role, not all areas.
S2PaletteCDataEnd:
.popseg
