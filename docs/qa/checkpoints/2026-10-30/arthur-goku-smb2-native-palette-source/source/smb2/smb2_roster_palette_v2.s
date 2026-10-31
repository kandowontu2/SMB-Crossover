; Additive to frozen v1. Consume this endpoint through a normal farcall:
; pointers remain in the intentional C80 art lease after A is restored.
.pushseg
.segment "PARODIUS_BELLS"
.export S2NativePaletteHeader,S2PaletteCCodeStart,S2PaletteCCodeEnd
S2PaletteCCodeStart:
.proc S2NativePaletteHeader
OwnStart:
 ; OWN unused45B private pointer gate retired after exact object closure.
 ; Genuine native SetBGColor chooses BackgroundColorCtrl, or AreaType when0.
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$10
 sta VRAM_Buffer1+1,x
 lda #4
 sta VRAM_Buffer1+2,x
 ldy BackgroundColorCtrl
 bne S2NativeBGSelect
 ldy AreaType
S2NativeBGSelect:lda S2NativeBGBytes,y
 sta VRAM_Buffer1+3,x
 inx
 ldy #1
 rts
S2NativeBGBytes:.byte $22,$22,$0f,$0f,$0f,$22,$0f,$0f
 .assert *-OwnStart<=45,error,"Retired own45B gate"
 .res 45-(*-OwnStart),$ea
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
