; Measured proposal only. Current Ready85 Doki sources are reproduced first.
.setcpu "6502"
.segment "S2_PRIORITY_GRAPHICS"
 jsr S2Ensure
 bcc G_Foreign
 lda S2Hurt
 beq G_Pose
 lda S2Clock
 and #8
 bne G_No
G_Pose:
 jsr S2GraphicsBank
 lda S2Variant
 and #4
 beq G_USA
 lda S2Animation
 cmp #11
 bcs G_No
 jsr DdqBuildPose
 bcc G_Meta                   ; actual builder exits ADC#32, C0 for variants0..7.
G_USA:
 lda S2NativeCharacter
 cmp #3
 bne G_Class
 lda #0
G_Class:
 asl
 ora S2Size
 asl
 asl
 asl
 asl
 asl
 sta R2
 lda S2Animation
 cmp #11
 bcs G_No
 tax
 lda G_AnimationIndex,x
 bmi G_No
 asl
 asl
 ora R2
 sta R2
 lda S2Holding
 asl
 ora R2
 ora S2Face
 tax
 lda S2BodyRecord,x
G_SetBody:
 jsr S2SetRecord
 lda S2NativeCharacter
 asl
 ora S2Size
 clc
 adc #<S2_FIRST_CHR
 sta SmChrBank
G_Meta:
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 jsr S2PriorityValue
 sta Player_SprAttrib
 lda Player_Rel_XPos
 sta Player_Pos_ForScroll
 sec
 rts
G_No:
 lda #0
 sta ObjectMetasprite
G_Foreign:
 clc
 rts
G_AnimationIndex:
 .byte $00,$ff,$01,$ff,$02,$ff,$03,$04,$05,$06,$07

.segment "S2_PRIORITY_PALETTE"
 lda SelectedCharacter
 cmp #25
 bne P_No
 ldx S2Variant
 txa
 and #4
 beq P_USA
 txa
 and #3
 asl
 asl
 tax
 adc #<DdqPalettes            ; both ASLs leave C0; actual lowE9+12 staysF5.
 sta R0
 lda #>DdqPalettes
 bne P_High                  ; actual highD5 is nonzero, no low carry/V.
P_USA:
 lda S2NativeCharacter
 asl
 asl
 tax
 adc #<S2Palettes             ; native class0..3, low2E+12 stays3A.
 sta R0
 lda #>S2Palettes
P_High:
 sta R1
 lda #<S2Role1
 sta R2
 lda #>S2Role1
 sta R3
 sec
 rts
P_No:
 clc
 rts
S2PriorityValue:
 lda Player_SprAttrib
 and #$20
 sta R3
 rts

.segment "S2_PRIORITY_BODY"
 sty R5                      ; real PublishBody->X5SetPhysicalChr preservesY0.
 nop
 nop
 nop
 nop                         ; R3 is already initialized by Graphics helper.
