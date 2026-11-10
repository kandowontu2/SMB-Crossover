.setcpu "6502"

.macro FarJump Target, Tag
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #Tag
 jmp FarCallCommon
.endmacro
.macro FarJumpNoA Target, Tag
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #Tag
 jmp FarCallCommon
.endmacro

; Same original85-byte public set-pose envelope and original mapper owner.
.segment "POSE"
.export PrototypeSetPose
PrototypeSetPose:
 lda #$e1
 sta CurrentBankC
 sta $5116
 stx JnPose
 jsr PrototypeBodyBank
 sta SmChrBank
 sta PlayerChrBank
 lda PlayerFacingDir
 cmp #2
 bne PoseIndex
 txa
 clc
 adc #7
 tax
PoseIndex:
 lda CompactBodyLo,x
 sta SmPosePtr
 lda CompactBodyHi,x
 sta SmPosePtr+1
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 tya
 tax
 lda SmChrBank
 ldy #0
 FarJump X5SetPhysicalChr,$be
 .assert *-PrototypeSetPose<=85,error,"Mike set-pose envelope"
 .res 85-(*-PrototypeSetPose),$ea

; Sentinel rows retain R0, Y and the original full-buffer failure contract.
.segment "PAL"
.export PrototypePalette
PrototypePalette:
 ldx VRAM_Buffer1_Offset
 cpx #78
 bcs PaletteDone
 tya
 pha
 lda #$e1
 sta CurrentBankC
 sta $5116
 lda FmGroups
 and #$60
 lsr
 lsr
 lsr
 lsr
 tay
 lda PrototypePaletteOffsets,y
 tay
PaletteLoop:
 lda PrototypePaletteCommands,y
 beq PaletteEnd
 sta VRAM_Buffer1,x
 inx
 iny
 bne PaletteLoop
PaletteEnd:
 stx VRAM_Buffer1_Offset
 sta VRAM_Buffer1,x
 pla
 tay
 lda #0
PaletteDone:
 rts
 .assert *-PrototypePalette<=54,error,"Mike palette envelope"
 .res 54-(*-PrototypePalette),$ea

; Mac's legal0/1/2 lookup and the former six SMB3 NOPs fund the Mike far gate.
.segment "MENU_GATE"
.export PrototypeMenuGate
PrototypeMenuGate:
 cmp #15
 bne NotMac
 ldx MacVariant
 lda MacNameRows,x
 jmp $b7f9
MacNameRows:.byte 30,41,42
NotMac:
 cmp #16
 bne NotMike
 FarJumpNoA PrototypeMenuName,$e1
NotMike:
 cmp #17
 bne MenuNext
 jmp $b05b
MenuNext:
 .assert *-PrototypeMenuGate=42,error,"Mac Mike SMB3 name source envelope"

; The installed DK fallback always compares X again, preserving foreign flags.
.segment "TOGGLE_ENTRY"
.export PrototypeToggleEntry
PrototypeToggleEntry:
 cpx #15
 .byte $f0,$e8                 ; BF7B -> BF65, independently linked sections.
 jmp $bf11
 nop
 .assert *-PrototypeToggleEntry=8,error,"Retired preview rows31..32"

; CPX#15 supplies carry1, so ADC#1F advances preciselyone20-bit field.
.segment "TOGGLE_HEAD"
.export PrototypeToggleHead
PrototypeToggleHead:
 lda FmGroups
 tax
 and #$60
 adc #$1f
 cmp #$60
 .byte $d0,$8c                 ; BF6F -> BEFD.
 lda #0
 .byte $f0,$88                 ; BF73 -> BEFD.
 .assert *-PrototypeToggleHead=16,error,"Retired preview rows26..29"
.segment "TOGGLE_TAIL"
.export PrototypeToggleTail
PrototypeToggleTail:
 .assert PrototypeToggleHead=$bf65,lderror,"Head relative branch binding"
 .assert PrototypeToggleTail=$befd,lderror,"Tail relative branch binding"
 .assert PrototypeToggleEntry=$bf79,lderror,"Entry relative branch binding"
 sta R0
 txa
 and #$9f
 ora R0
 sta FmGroups
 sec
 rts
 .assert *-PrototypeToggleTail=12,error,"Retired preview rows0..2"

.segment "HUD_HOOK"
 FarJump PrototypeStatusName,$e1

; This section executes in A97. It never borrows the C window for names.
.segment "ALT_A"
.export PrototypeMenuName,PrototypeSonicName,PrototypeNamesEnd
PrototypeMenuName:
 lda FmGroups
 and #$60
 beq OriginalMikeName
 ldy #0
 cmp #$20
 beq NameCopy
 ldy #16
NameCopy:
 ldx VRAM_Buffer1_Offset
 lda #$23
 sta VRAM_Buffer1,x
 lda #$28
 sta VRAM_Buffer1+1,x
 lda #16
 sta VRAM_Buffer1+2,x
 sta R0
NameLoop:
 lda PrototypeTitles,y
 sta VRAM_Buffer1+3,x
 inx
 iny
 dec R0
 bne NameLoop
 txa
 clc
 adc #3
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 rts
OriginalMikeName:
 lda #31
 FarJump $b7f9,$d1
PrototypeSonicName:
 ldy #32
 bne NameCopy
PrototypeTitles:
 .byte JAY_TITLE
 .byte STEVE_TITLE
 .byte SONIC_TITLE
PrototypeNamesEnd:

; These routines execute in C97 while Mike's existing A96 owner is mapped.
.segment "ALT_C"
.export PrototypeBodyBank,PrototypeStatusName,PrototypeAltEnd
PrototypeBodyBank:
 lda FmGroups
 and #$60
 beq MikeBank
 cmp #$60
 beq MikeBank
 pha
 cpx #3
 bcc BodyPoseReady
 lda Player_State
 beq BodyStanding
 ldx #4
 bne BodyPoseReady
BodyStanding:
 ldx #0
BodyPoseReady:
 pla
 lsr
 lsr
 lsr
 clc
 adc #$d4
 ldy #0
 rts
MikeBank:
 lda #$c4
 ldy #2
 rts

PrototypeStatusName:
 cmp #0
 bne StatusDone
 pha
 txa
 pha
 ldx #6
StatusLoop:
 lda FmGroups
 and #$60
 beq MikeChar
 cmp #$20
 beq JayChar
 lda PrototypeSteveTitleC,x
 bne StatusWrite
JayChar:
 lda PrototypeJayHud,x
 bne StatusWrite
MikeChar:
 lda $a91a,x
StatusWrite:
 sta VRAM_Buffer1+11,x
 dex
 bpl StatusLoop
 pla
 tax
 pla
StatusDone:
 rts
PrototypeJayHud:.byte JAY_HUD
PrototypePaletteOffsets:.byte 0,0,7,0,14,0,0
PrototypePaletteCommands:
 .byte $3f,$11,3,$07,$36,$21,0
 .byte $3f,$11,3,JAY_PALETTE,0
 .byte $3f,$11,3,STEVE_PALETTE,0
PrototypeAltEnd:
