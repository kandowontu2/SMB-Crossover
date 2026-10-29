; Native 8x16 records. Parent ac126 uses 8x16 too: one source part is ONE OAM
; entry. No tile splitting, recoloring artwork or extra outline layer.
.pushseg
.segment "GIMMICK_COLD"
.proc GmGraphics
 php
 pha
 txa
 pha
 tya
 pha
 lda SelectedCharacter
 cmp #CHARACTER_GIMMICK
 jne Done
 GmSaveScratch
 lda #($80|73)
 sta CurrentBankC
 sta $5116
 ; Actual original30:83F5..8429, once late Main, not every Draw.
 lda #0
 sta GmVisible
 lda GmRam0300
 cmp #$15
 beq Hurt
 lda GmRam036E
 bmi Hurt
 lda #8
 sta GmRam0300
 lda #$3b
 sta GmRam0382
Hurt:lda GmRam038C
 beq Visible
 dec GmRam038C
 sec
 sbc #$66
 bcs HurtPose
 and #2
 bne Restore
 beq Visible
HurtPose:tay
 lda GmHurtFrame,y
 sta GmRam0300
Visible:
 lda #1
 sta GmVisible
 ldx GmRam0300
 cpx #22
 bcs Restore
 lda GmHeroPage,x
 clc
 adc #<GM_FIRST_CHR
 ldx #>GM_FIRST_CHR
 ldy #0
 GmFar X5SetPhysicalChr,62
 lda #<(GM_FIRST_CHR+2)
 ldx #>(GM_FIRST_CHR+2)
 ldy #1
 GmFar X5SetPhysicalChr,62
Restore:GmRestoreScratch
Done:pla
 tay
 pla
 tax
 pla
 plp
 rts
.endproc
.proc GmColors
 ; Real GetPlayerColors/scene/star-end owner must call this endpoint. It
 ; appends only P0 visible colors, never the universal backdrop or world P2.
 ; P2 already has16/30/27: approved source07 -> native16 quantization.
 lda SelectedCharacter
 cmp #CHARACTER_GIMMICK
 bne No
 lda VRAM_Buffer_AddrCtrl
 bne No
 ldx VRAM_Buffer1_Offset
 cpx #58                     ; 6B command+terminator fit native64B buffer.
 bcs No
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$11
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 lda #$0b
 sta VRAM_Buffer1+3,x
 lda #$2a
 sta VRAM_Buffer1+4,x
 lda #$30
 sta VRAM_Buffer1+5,x
 lda #0
 sta VRAM_Buffer1+6,x
 txa
 clc
 adc #6
 sta VRAM_Buffer1_Offset
 sec
 rts
No:clc
 rts
.endproc
.proc GmPortrait
 ; Cold menu/lives draw. A=original facing0/1,R4/5 screenX,R6 screenY.
 ; No Ready/health/clock reads, no hidden gameplay tick. R0..3/A/X/Y volatile
 ; like original renderer; C mapping and all5 live farcall operands restored.
 pha
 lda SelectedCharacter
 cmp #CHARACTER_GIMMICK
 beq Owned
 pla
 rts
Owned:pla
 and #1
 sta GmTemp2
 lda NextBank_SMC+1
 pha
 lda SafecallA_SMC+1
 pha
 lda FarcallJmpTarget_SMC+1
 pha
 lda FarcallJmpTarget_SMC+2
 pha
 lda SafereturnA_SMC+1
 pha
 lda CurrentBankC
 pha
 lda #($80|73)
 sta CurrentBankC
 sta $5116
 lda #<GM_FIRST_CHR
 ldx #>GM_FIRST_CHR
 ldy #0
 GmFar X5SetPhysicalChr,62
 lda #<(GM_FIRST_CHR+2)
 ldx #>(GM_FIRST_CHR+2)
 ldy #1
 GmFar X5SetPhysicalChr,62
 lda GmHeroTable
 sta R0
 lda GmHeroTable+1
 sta R1
 lda GmTemp2
 beq Attr
 lda #$40
Attr:sta R3
 GmFar GmEmitRecord,24
 pla
 sta CurrentBankC
 sta $5116
 pla
 sta SafereturnA_SMC+1
 pla
 sta FarcallJmpTarget_SMC+2
 pla
 sta FarcallJmpTarget_SMC+1
 pla
 sta SafecallA_SMC+1
 pla
 sta NextBank_SMC+1
 rts
.endproc
.segment "GIMMICK_CORE"
.proc GmScreenPoint
 ; SlotX source16.4 -> host screen pixels. Y modulo256 is literal source;
 ; host extends original191-row viewport clip to239, an explicit adaptation.
 lda GmRam00AE,x
 sta R4
 lda GmRam00B8,x
 sta R5
 lda GmRam009A,x
 sta R6
 lda GmRam00A4,x
 sta R7
 .repeat 4
 lsr R5
 ror R4
 lsr R7
 ror R6
 .endrepeat
 jmp GmCameraPoint
.endproc
.proc GmCameraPoint
 lda R4
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda R5
 sbc ScreenLeft_PageLoc
 sta R5
 rts
.endproc
.proc GmEmitRecord
 ; InputR0/1 original terminated record; R4/5 screenX,R6 screenY,R3 XOR.
 ; GmTemp2 facing0/1. Ordered source parts; exact parent OAM rotation contract.
 ldy #0
Next:lda (R0),y
 jeq Done
 clc
 adc R6
 cmp #240
 bcs Skip
 sta GmTemp
 lda CurrentOAMOffset
 clc
 adc #4
 bcs Done
 ldx CurrentOAMOffset
 lda GuestOamRotationActive
 beq At
 txa
 clc
 adc RgOamRotation
 tax
At:lda GmTemp
 sta Sprite_Y_Position,x
 iny
 lda (R0),y
 sta Sprite_Tilenumber,x
 iny
 lda (R0),y
 eor R3
 ; Preserve source flips/priority. Source palette1 uses compatible nativeP2.
 sta GmTemp
 and #3
 cmp #1
 bne Attr
 lda GmTemp
 eor #3
 bne WriteAttr
Attr:lda GmTemp
WriteAttr:sta Sprite_Attributes,x
 iny
 lda GmTemp2
 beq Normal
 lda #$fa
 sec
 sbc (R0),y
 jmp Offset
Normal:lda (R0),y
Offset:sta GmTemp
 lda #0
 bit GmTemp
 bpl Sign
 lda #$ff
Sign:sta R2
 lda GmTemp
 clc
 adc R4
 sta Sprite_X_Position,x
 lda R5
 adc R2
 bne Advance
 lda CurrentOAMOffset
 clc
 adc #4
 sta CurrentOAMOffset
Advance:iny
 jmp Next
Skip:tya
 clc
 adc #4
 tay
 jne Next
Done:rts
.endproc
.proc GmStarRecord
 ; A=source frame. Only validated66 frames can address source table.
 cmp #66
 bcs No
 asl
 tay
 lda GmStarTable,y
 sta R0
 lda GmStarTable+1,y
 sta R1
 jmp GmEmitRecord
No:rts
.endproc
.proc GmDraw
 php
 pha
 txa
 pha
 tya
 pha
 lda SelectedCharacter
 cmp #CHARACTER_GIMMICK
 jne Done
 GmSaveScratch
 lda #($80|73)
 sta CurrentBankC
 sta $5116
 ; Original star trails draw oldest(age4),middle(age2),current(age0).
 lda GmRam030B
 sta GmTemp2
 beq StarAttr
 lda #$40
StarAttr:ora GmRam03C9
 sta R3
 ldx #0
Trail:
 stx GmPart
 lda GmHistory+4,x
 bpl TrailNext
 and #$7f
 cmp #$15                     ; Original84BB literal15 HEX (21 decimal).
 bcs TrailNext
 pha
 lda GmHistory,x
 sta R4
 lda GmHistory+1,x
 sta R5
 lda GmHistory+2,x
 sta R6
 jsr GmCameraPoint
 pla
 jsr GmStarRecord
TrailNext:ldx GmPart
 txa
 clc
 adc #10
 tax
 cpx #20
 bcc Trail
 lda GmRam0091
 beq History
 ldx #1
 jsr GmScreenPoint
 lda GmRam0301
 jsr GmStarRecord
History:
 ; Move four packed source history entries, keeping all fractional renderer
 ; bits that matter: positions are exact floor(source/16) without fractions.
 ldx #0
Shift:lda GmHistory+5,x
 sta GmHistory,x
 inx
 cpx #15
 bne Shift
 ldx #1
 jsr GmScreenPoint
 ; Undo screen subtraction: history is source world pixels, not screen-relative.
 lda R4
 clc
 adc ScreenLeft_X_Pos
 sta GmHistory+15
 lda R5
 adc ScreenLeft_PageLoc
 sta GmHistory+16
 lda R6
 sta GmHistory+17
 lda R7
 sta GmHistory+18
 lda GmRam0301
 and #$7f
 ldx GmRam0091
 beq SaveHistory
 ora #$80
SaveHistory:sta GmHistory+19
 GmFar GmRetireStar,122
 ; Noninteractive native B4 particles retain actual four-pose age animation.
 ldx #0
 lda #0
 sta GmTemp2
Effect:stx GmPart
 lda GmEffects+3,x
 and #$f0
 beq NextEffect
 lsr
 lsr
 lsr
 lsr
 lsr
 lsr
 asl
 tay
 lda GmEffectTable,y
 sta R0
 lda GmEffectTable+1,y
 sta R1
 lda GmEffects,x
 sta R4
 lda GmEffects+1,x
 sta R5
 lda GmEffects+2,x
 sta R6
 lda GmEffects+3,x
 and #15
 sta R7
 .repeat 4
 lsr R5
 ror R4
 lsr R7
 ror R6
 .endrepeat
 jsr GmCameraPoint
 lda GmClock
 and #1
 sta R3
 jsr GmEmitRecord
NextEffect:ldx GmPart
 txa
 clc
 adc #4
 tax
 cpx #28
 bcc Effect
 lda GmVisible
 beq Restore
 ldx #0
 jsr GmScreenPoint
 lda GmRam030A
 sta GmTemp2
 beq BodyAttr
 lda #$40
BodyAttr:ora GmRam03C8
 sta R3
 lda GmRam0300
 cmp #22
 bcs Restore
 asl
 tay
 lda GmHeroTable,y
 sta R0
 lda GmHeroTable+1,y
 sta R1
 jsr GmEmitRecord
Restore:GmRestoreScratch
Done:pla
 tay
 pla
 tax
 pla
 plp
 rts
.endproc
.export GmGraphics,GmDraw,GmColors,GmPortrait,GmEmitRecord,GmScreenPoint,GmStarRecord
.popseg
