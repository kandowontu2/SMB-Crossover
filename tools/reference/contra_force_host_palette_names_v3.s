; PRIVATE selected31 authenticated A3/C2 body colors and real UI identity.
; No P1 policy: yellow loan-requiring shots remain whole-object hidden.
.setcpu "6502"
.macpack longbranch
.import CfP1Heartbeat
.import CfState,VRAM_Buffer1,VRAM_Buffer1_Offset,BackgroundColorCtrl,AreaType
.importzp R0
.export CfHostForcePalette,CfHostPaletteTick,CfHostMenuName,CfHostStatusName,CfHostWorldPalette
.export CfHostQueueBody,CfHostQueueBodyColor,CfHostPaletteNamesEnd
CFPaletteDirty=CfState+$02e2
CFVariant=CfState+$02e0
.macro UI_SAVE
 php
 pha
 txa
 pha
 tya
 pha
.endmacro
.macro UI_RESTORE
 pla
 tay
 pla
 tax
 pla
 plp
.endmacro
.segment "CF_HOST_PALETTE_NAMES"
CfHostForcePalette:
 lda #1
 sta CFPaletteDirty
 jmp CfHostQueueBody
CfHostPaletteTick:
 jsr CfHostBodyPaletteTick
 jmp CfP1Heartbeat
CfHostBodyPaletteTick:
 lda CFPaletteDirty
 bne CfHostQueueBody
 sec
 rts
; Exact native GetPlayerColors transparent/background entry contract, not
; source universal0F (which would turn overworld sky black via3F10alias).
CfHostQueueBody:
 ldy BackgroundColorCtrl
 bne :+
 ldy AreaType
:cpy #8
 bcc :+
 ldy #2
:lda CfBackgroundColors,y
CfHostQueueBodyColor:
 pha
 ldx VRAM_Buffer1_Offset
 cpx #77
 bcs CfBodyNoSpace
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$10
 sta VRAM_Buffer1+1,x
 lda #4
 sta VRAM_Buffer1+2,x
 pla
 sta VRAM_Buffer1+3,x
 lda #$37
 sta VRAM_Buffer1+4,x
 lda #$12
 sta VRAM_Buffer1+5,x
 lda #$0f
 sta VRAM_Buffer1+6,x
 txa
 clc
 adc #7
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 sta CFPaletteDirty             ; complete packet before dirty ACK
 sec
 rts
CfBodyNoSpace:
 pla
 clc
 rts
CfBackgroundColors:.byte $22,$22,$0f,$0f,$0f,$22,$0f,$0f
; Exact genuine native HuNativeWorldPalette instruction policy. Intentional
; native R0/Y outputs select original areaP3, never guest recoloringP2/P3.
CfHostWorldPalette:
 lda AreaType
 asl
 sta R0
 asl
 clc
 adc R0
 adc #6
 tay
 rts

; Own authenticated ready menu API. The genuine pre-load menu must continue
; calling ROM FmQueueName/FmDrawCfPreview; it cannot execute this A3 yet.
CfHostMenuName:
 UI_SAVE
 ldx VRAM_Buffer1_Offset
 cpx #65
 jcs CfMenuNoSpace
 lda #$23
 sta VRAM_Buffer1,x
 lda #$28
 sta VRAM_Buffer1+1,x
 lda #16
 sta VRAM_Buffer1+2,x
 lda CFVariant
 and #3
 asl
 asl
 asl
 asl
 tay
CfMenuCopy:
 lda CfMenuNames,y
 sta VRAM_Buffer1+3,x
 inx
 iny
 tya
 and #15
 bne CfMenuCopy
 txa
 clc
 adc #3
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 UI_RESTORE
 sec
 rts
CfMenuNoSpace:
 UI_RESTORE
 clc
 rts

; Actual WriteGameText supplies originalA0 for top HUD, orA1/Y30 only AFTER
; native world/lives text has overwritten the whole earlier queue. Preserve
; true callerX/Y and returnedA; append exact black/lives P0 after those30B.
CfHostStatusName:
 cmp #0
 beq CfHudName
 cmp #1
 bne CfStatusDone
 cpy #30
 bne CfStatusDone
 UI_SAVE
 sty VRAM_Buffer1_Offset
 lda #1
 sta CFPaletteDirty
 lda #$0f
 jsr CfHostQueueBodyColor
 UI_RESTORE
 rts
CfHudName:
 UI_SAVE
 lda CFVariant
 and #3
 asl
 asl
 asl
 tax
 ldy #0
CfHudCopy:
 lda CfHudNames,x
 sta VRAM_Buffer1+11,y
 inx
 iny
 cpy #7
 bcc CfHudCopy
 UI_RESTORE
CfStatusDone:
 rts
; Exact native ASCII->SMB character mapping, checked againstinc/charmap.inc.
.charmap $20,$24
.repeat 26,I
 .charmap $41+I,$0a+I
.endrepeat
CfMenuNames:
 .byte "     BURNS      ","     SMITH      ","      IRON      ","     BEANS      "
CfHudNames:
 .byte "BURNS   ","SMITH   ","IRON    ","BEANS   "
CfHostPaletteNamesEnd:
