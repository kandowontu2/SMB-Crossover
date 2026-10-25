.pushseg
.segment "TMNT_CORE"
.proc TnGraphics
 jsr TnEnsure
 lda Player_Rel_XPos
 sta Player_Pos_ForScroll
 lda Player_SprAttrib
 and #$fc
 sta Player_SprAttrib
 lda GameEngineSubroutine
 cmp #11
 bne Live
 lda #$19
 sta TnPose
Live:
 lda TnPose
 bne Valid
 lda #9
Valid:tax
 jmp TnSetPose
.endproc
.proc TnPortrait
 jsr TnEnsure
 BankPRGC #.bank(TnArtStart)
 ldx TnVariant
 lda TnPortraitBodyID,x
 tax
 jsr TnSetPose
 jsr TnPublishPortrait
 ldx TnVariant
 lda PlayerFacingDir
 cmp #2
 beq Left
 lda TnPortraitRLo,x
 sta SmPosePtr
 lda TnPortraitRHi,x
 sta SmPosePtr+1
 rts
Left:
 lda TnPortraitLLo,x
 sta SmPosePtr
 lda TnPortraitLHi,x
 sta SmPosePtr+1
 rts
.endproc
.proc TnSetPose
 BankPRGC #.bank(TnArtStart)
 lda TnBodyChr,x
 sta SmChrBank
 lda PlayerFacingDir
 cmp #2
 beq Left
 lda TnBodyRLo,x
 sta SmPosePtr
 lda TnBodyRHi,x
 jmp Pointer
Left:
 lda TnBodyLLo,x
 sta SmPosePtr
 lda TnBodyLHi,x
Pointer:sta SmPosePtr+1
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 ; TnDraw publishes gameplay pages only when matching sprites are drawn.
 rts
  .byte $ea,$ea ; constant body colors initialize through GetPlayerColors/Portrait.
.endproc
.proc TnPublishPortrait
 lda SmChrBank
 ldx #>TN_FIRST_CHR
 ldy #0
 farcall X5SetPhysicalChr,jmp
.endproc
.proc TnQueuePalette
 ldx VRAM_Buffer1_Offset
 cpx #77 ;7-byte palette append plus terminator must fit84-byte queue
 bcs Done
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$10
 sta VRAM_Buffer1+1,x
 lda #4
 sta VRAM_Buffer1+2,x
 ldy BackgroundColorCtrl
 bne :+
 ldy AreaType
:lda NativeBackgroundColors,y
 sta VRAM_Buffer1+3,x
 lda #$09
 sta VRAM_Buffer1+4,x
 lda #$12
 sta VRAM_Buffer1+5,x
 lda #$2a
 sta VRAM_Buffer1+6,x
 txa
 clc
 adc #7
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
Done:rts
NativeBackgroundColors:.byte $22,$22,$0f,$0f,$0f,$22,$0f,$0f
.endproc
.segment "TMNT_COMBAT"
.proc TnDraw
 BankPRGC #.bank(TnArtStart)
 lda SmChrBank
 ldx #>TN_FIRST_CHR
 ldy #0
 farcall X5SetPhysicalChr
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda MmDeathFlag
 jne Done
 jsr TnWeaponPosition
 lda TnAttack
 beq Health
 ldx TnPose+1
 beq Health
 lda PlayerFacingDir
 cmp #2
 beq Left
 lda TnWeaponRLo,x
 sta R0
 lda TnWeaponRHi,x
 jmp WeaponPtr
Left:
 lda TnWeaponLLo,x
 sta R0
 lda TnWeaponLHi,x
WeaponPtr:sta R1
 lda TnWeaponX
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda TnWeaponPage
 sbc ScreenLeft_PageLoc
 sta R5
 lda TnWeaponY
 sta R6
::TnPrimaryDrawCall:
 jsr TnPrimaryRender
Health:
 ldx TnVariant
 lda TnHealth,x
 cmp TnHudHealth
 bne RebuildHealth
 ldy TnHudValid
 cpy #$c9
 beq RenderHealth
RebuildHealth:
 sta TnHudHealth
 ldy #$c9
 sty TnHudValid
 sta TnTemp2
 lda #16
 sta $5ca0
 ldy #0
Cell:
 sty TnSavedY
 ldx #0
 lda TnTemp2
 cmp #16
 bcc Tile
 inx
 cmp #32
 bcc Tile
 inx
Tile:lda TnHealthTiles,x
 sta TnTemp
 tya
 asl
 asl
 tax
 lda TnTemp
 sta $5ca1,x
 lda #0
 sta $5ca2,x
 sta $5ca3,x
 tya
 asl
 asl
 asl
 sta $5ca4,x
 lda TnTemp2
 sec
 sbc #32
 bcs :+
 lda #0
:sta TnTemp2
 ldy TnSavedY
 iny
 cpy #4
 bcc Cell
RenderHealth:
 lda #$a0
 sta R0
 lda #$5c
 sta R1
 lda #80
 sta R4
 lda #0
 sta R5
 lda #7
 sta R6
::TnHealthDrawCall:
 jsr TnHealthRender
Done:
 farcall TnDrawEquipment
 rts
Draw:
 lda #1
 sta R7
 lda #0
 sta R3
 farcall MetaspriteRenderLoop
 rts
.endproc
.popseg
