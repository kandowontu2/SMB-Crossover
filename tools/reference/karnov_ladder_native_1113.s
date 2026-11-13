; Native transport for the original Karnov Ladder. Measurement source only.
; Requires authenticated relink plus the separate art/state lifetime proofs.
; Original27-byte object lease, native compact transport:
; 624=count/camera column,625=world tile X low8,626=X high4|bottom Y row4,
; 627=next growth tip Y,628=last camera page,629..630=eight saved metatiles.
; Remaining original object bytes stay available only to this object transport.
; Tip627==0 is the inactive marker; live/growing tips are nonzero in the
; native visible plane. Count0 and stale world coordinates never draw/query.
; Caller owns R0/R1; Frame retains R2..R7. No new persistent byte is used.
.setcpu "6502"
.segment "LADDER_MAIN"
KrLadderFrame:
 ldx #5
KrLadderSave:
 lda $05,x
 pha
 dex
 bpl KrLadderSave
 jsr KrLadderStep
 ldx #0
KrLadderRestore:
 pla
 sta $05,x
 inx
 cpx #6
 bne KrLadderRestore
 rts
KrLadderStep:
 lda $c05e
 cmp #1
 beq KrLadderJobEntry
 cmp #2
 beq KrLadderJobEntry
 cmp #11
 beq KrLadderJobEntry
 jsr KrLadderProbes
 jsr KrOptionsControls
 jsr KrSourceFrame
 jsr KrSourceWeapons
 jsr KrOptionsTick
 lda $c624
 and #15
 beq KrLadderDone
 lda ScreenLeft_X_Pos
 and #$f0
 eor $c624
 and #$f0
 bne KrLadderRedraw
 lda ScreenLeft_PageLoc
 cmp $c628
 bne KrLadderRedraw
KrLadderDone:
 rts
KrLadderJobEntry:
 jsr KrLadderQueueFree
 bcc KrLadderDone
 lda $c05e
 cmp #1
 beq KrLadderGrow
 jmp KrLadderRetract
KrLadderRedraw:
 jsr KrLadderQueueFree
 bcc KrLadderDone
 jmp KrLadderFullRedraw

KrLadderGrow:
 lda $c624
 and #15
 tax
 cpx #8
 bcs KrLadderResume
 lda $c627
 cmp #32
 bcc KrLadderResume
 jsr KrLadderCell
 bcc KrLadderResume
 ldy $05
 lda ($09),y
 sta $c629,x
 tay
 lda NativeAttributes,y
 and #3
 bne KrLadderResume
 ldy $05
 lda #0
 sta ($09),y
 inc $c624
 lda $c627
 sec
 sbc #16
 sta $c627
 jsr KrLadderDrawCell
 jsr KrLadderAttribute
 jmp KrLadderCamera
KrLadderResume:
 lda $c71f
 sta $c05e
 rts

KrLadderRetract:
 lda $c624
 and #15
 beq KrLadderEmpty
 tax
 dex
 dec $c624
 lda $c627
 clc
 adc #16
 sta $c627
 jsr KrLadderCell
 bcc KrLadderRetired
 ldy $05
 lda $c629,x
 sta ($09),y
 jsr KrLadderWriteBlank
 lda $c629,x
 tax
 jsr KrLadderNativeQuad
 jsr KrLadderAttribute
KrLadderRetired:
 lda $c624
 and #15
 bne KrLadderDoneRestore
KrLadderEmpty:
 lda $c05e
 cmp #11
 beq KrLadderInit
 lda #0
 sta $c624
 sta $c627
 lda $c08f
 ora #4
 sta $c08f
 lda #2
 sta $c08e
 jmp KrLadderResume
KrLadderDoneRestore:
 rts

KrLadderActivate:
 lda $c062
 and #31
 cmp #7
 bcs KrLadderActivationDone
 lda $c08b
 cmp #8
 beq KrLadderActivationDone
 cmp #9
 beq KrLadderActivationDone
 lda $c089
 cmp #12
 beq KrLadderActivationDone
 lda $c0c4
 bmi KrLadderActivationDone
 lda $c627
 beq KrLadderNew
 lda #11
 sta $c05e
 bne KrLadderActivated
KrLadderNew:
 lda $c05e
 sta $c71f
 jsr KrLadderInit
KrLadderActivated:
 lda #9
 jsr KrSoundCallback
 lda $c08f
 and #$fb
 sta $c08f
 lda #2
 jmp Kr_ED1A
KrLadderActivationDone:
 rts
KrLadderInit:
 ldx #26
 lda #0
KrLadderInitClear:
 sta $c624,x
 dex
 bpl KrLadderInitClear
 lda $c064
 sec
 sbc #8
 sta $c627
 lsr
 lsr
 lsr
 lsr
 sta $c626
 ldx $c063
 jsr KrLadderWorld
 sta $c625
 lda $06
 ora $c626
 sta $c626
 lda #1
 sta $c05e
 rts

; Original EDB7..EEA9 probe positions: center/body-16, facing side/body-16,
; center/foot, facing side/foot-4. Native ordinary support remains its owner.
KrLadderProbes:
 lda $c624
 beq KrLadderProbesDone
 ldx #3
 stx $07
KrLadderProbesLoop:
 ldx $07
 lda $c064
 sec
 sbc KrLadderProbeDY,x
 tay
 lda KrLadderProbeDX,x
 beq KrLadderProbeCenter
 bit $c062
 bpl KrLadderProbeCenter
 lda #$fc
KrLadderProbeCenter:
 clc
 adc $c063
 tax
 jsr KrLadderProbe
 cmp #9
 bne KrLadderProbeNext
 ldx $07
 sta $c089,x
 cpx #0
 bne KrLadderProbeNext
 sta $c08d
KrLadderProbeNext:
 dec $07
 bpl KrLadderProbesLoop
KrLadderProbesDone:
 rts
KrLadderProbeDX:
 .byte $00,$04,$00,$04
KrLadderProbeDY:
 .byte $10,$10,$00,$04

.segment "LADDER_AUX"
; Existing C3D8 callback contract: result A/N/Z, retain X/Y/C/V/D/I.
KrLadderTerrain:
 php
 txa
 pha
 tya
 pha
 ldx #7
KrLadderTerrainSave:
 lda $03,x
 pha
 dex
 bpl KrLadderTerrainSave
 tsx
 lda $0109,x
 tay
 lda $010a,x
 tax
 jsr KrLadderProbe
 sta KrTerrainResult
 ldx #0
KrLadderTerrainRestore:
 pla
 sta $03,x
 inx
 cpx #8
 bne KrLadderTerrainRestore
 pla
 tay
 pla
 tax
 plp
 lda KrTerrainResult
 rts
KrLadderProbe:
 lda $c624
 and #15
 bne KrLadderProbeOwned
 rts
KrLadderProbeOwned:
 sty $05
 jsr KrLadderWorld
 lda $03
 cmp $c625
 bne KrLadderNoProbe
 lda $c626
 and #$f0
 cmp $06
 bne KrLadderNoProbe
 lda $05
 cmp #32
 bcc KrLadderNoProbe
 cmp #208
 bcs KrLadderNoProbe
 lda $03
 and #31
 jsr NativeGetBlockBufferAddr
 lda $05
 and #$f0
 sta $06
 sec
 sbc #32
 tay
 lda ($09),y
 tay
 lda NativeAttributes,y
 and #1
 bne KrLadderProbeDone
 lda $06
 cmp $c627
 bcc KrLadderNoProbe
 beq KrLadderNoProbe
 lda $c626
 and #15
 asl
 asl
 asl
 asl
 cmp $06
 bcc KrLadderNoProbe
 lda #9
KrLadderProbeDone:
 rts
KrLadderNoProbe:
 lda #0
 rts
KrLadderWorld:
 txa
 clc
 adc ScreenLeft_X_Pos
 sta $03
 lda ScreenLeft_PageLoc
 adc #0
 sta $04
 and #$f0
 sta $06
 lda $03
 lsr
 lsr
 lsr
 lsr
 sta $03
 lda $04
 asl
 asl
 asl
 asl
 ora $03
 sta $03
 rts

; X is segment0..7. Return C1 only for a visible native cell and bounded row.
; R2/R6/R7 use native offsets but actual R2 is host address5, R6/R7 are9/10.
KrLadderCell:
 lda $c625
 lsr
 lsr
 lsr
 lsr
 sta $04
 lda $c626
 and #$f0
 ora $04
 sta $04
 lda $c625
 asl
 asl
 asl
 asl
 sec
 sbc ScreenLeft_X_Pos
 sta $03
 lda $04
 sbc ScreenLeft_PageLoc
 beq KrLadderVisible
 cmp #$ff
 bne KrLadderInvisible
 lda $03
 cmp #$f1
 bcc KrLadderInvisible
KrLadderVisible:
 stx $03
 lda $c626
 and #15
 sec
 sbc $03
 cmp #2
 bcc KrLadderInvisible
 cmp #13
 bcs KrLadderInvisible
 asl
 asl
 asl
 asl
 sec
 sbc #32
 sta $05
 lda $c625
 and #31
 jsr NativeGetBlockBufferAddr
 sec
 rts
KrLadderInvisible:
 clc
 rts

KrLadderDrawCell:
 jsr KrLadderWriteBlank
 lda #LadderLeftGlyph
 sta NativeVRAM3,y
 sta NativeVRAM8,y
 lda #LadderRightGlyph
 sta NativeVRAM4,y
 sta NativeVRAM9,y
 rts
KrLadderWriteBlank:
 lda #<NativeWriteBlockMetatile
 sta $016c
 lda #>NativeWriteBlockMetatile
 sta $016d
 lda #0
 sta NativeSafecallA
 lda #$83
 jmp NativeFarCallCommon
KrLadderNativeQuad:
 lda CurrentBankC
 pha
 lda #$83
 sta CurrentBankC
 sta $5116
 lda NativeTopLeft,x
 sta NativeVRAM3,y
 lda NativeTopRight,x
 sta NativeVRAM4,y
 lda NativeBotLeft,x
 sta NativeVRAM8,y
 lda NativeBotRight,x
 sta NativeVRAM9,y
 pla
 sta CurrentBankC
 sta $5116
 rts
KrLadderCamera:
 lda ScreenLeft_X_Pos
 eor $c624
 and #$f0
 eor $c624
 sta $c624
 lda ScreenLeft_PageLoc
 sta $c628
 rts
KrLadderQueueFree:
 lda NmiDisable
 bpl KrLadderQueueBusy
 lda DisableScreenFlag
 ora VRAM_Buffer_AddrCtrl
 ora VRAM_Buffer1_Offset
 ora NativeVRAM0
 bne KrLadderQueueBusy
 sec
 rts
KrLadderQueueBusy:
 clc
 rts
KrLadderSceneClear:
 lda $c627
 beq KrLadderSceneEmpty
 lda $c08f
 ora #4
 sta $c08f
KrLadderSceneEmpty:
 lda #0
 sta $c624
 sta $c627
 sta $c05e
 jmp KrClearSourceShots

; Original F62B..F631 rounds to16px cells at+8. Translate that same grid
; through the actual native camera; keep A/X/Y/P exactly at the patch return.
KrLadderWorldSnap:
 php
 lda $c063
 clc
 adc ScreenLeft_X_Pos
 and #$f0
 ora #8
 sec
 sbc ScreenLeft_X_Pos
 sta $c063
 plp
 lda $c063
 rts

; Additional transport below is measured at an ungranted coordinate only.
.segment "LADDER_EXTRA"
; Two vertical pattern columns, then each distinct attribute group once.
; The exclusive empty84B queue holds at most38+20 bytes and a terminator.
KrLadderFullRedraw:
 lda $c624
 and #15
 tax
 dex
 jsr KrLadderCell
 bcs KrLadderRedrawVisible
 jmp KrLadderCamera
KrLadderRedrawVisible:
 jsr KrLadderWriteBlank
 lda $c624
 and #15
 asl
 sta $03
 asl
 sta $04
 lda $03
 ora #$80
 sta NativeVRAM2
 ldx #0
 lda #LadderLeftGlyph
KrLadderColumnLeft:
 sta NativeVRAM3,x
 inx
 cpx $03
 bcc KrLadderColumnLeft
 lda $08
 sta NativeVRAM3,x
 lda $07
 clc
 adc #1
 sta NativeVRAM4,x
 lda $03
 ora #$80
 sta NativeVRAM5,x
 lda #LadderRightGlyph
KrLadderColumnRight:
 sta NativeVRAM6,x
 inx
 cpx $04
 bcc KrLadderColumnRight
 lda #0
 sta NativeVRAM6,x
 txa
 clc
 adc #6
 sta VRAM_Buffer1_Offset
 lda $c624
 and #15
 pha
 ldx #0
KrLadderAttributeGroups:
 cpx #0
 beq KrLadderAttributeGroup
 txa
 eor $c626
 and #1
 beq KrLadderAttributeNext
KrLadderAttributeGroup:
 txa
 pha
 jsr KrLadderCell
 jsr KrLadderAttribute
 pla
 tax
KrLadderAttributeNext:
 inx
 pla
 sec
 sbc #1
 beq KrLadderAttributesDone
 pha
 jmp KrLadderAttributeGroups
KrLadderAttributesDone:
 jmp KrLadderCamera

; Reconstruct the complete native attribute byte from four current metatiles.
; Active Ladder quadrants use native palette2 (21 blue /0F black), an explicit
; mapping of source palette1 colors22/02. Every other current quadrant and
; every restored target uses its actual saved/current native metatile palette.
; No global palette change, PPU read, stale attribute cache or marker metatile.
KrLadderAttribute:
 ldx VRAM_Buffer1_Offset
 lda $08
 and #$24
 ora #3
 sta NativeVRAM0,x
 lda $05
 clc
 adc #32
 lsr
 lsr
 and #$38
 sta $06
 lda $09
 and #15
 lsr
 ora $06
 ora #$c0
 sta NativeVRAM1,x
 lda #1
 sta NativeVRAM2,x
 lda $09
 and #$fe
 sta $09
 lda $05
 and #$e0
 sta $05
 lda #0
 sta $07
 ldx #0
KrLadderAttributeCells:
 lda KrLadderAttributeOffsets,x
 clc
 adc $05
 tay
 txa
 eor $c625
 and #1
 bne KrLadderNativePalette
 tya
 clc
 adc #32
 and #$f0
 sta $03
 cmp $c627
 bcc KrLadderNativePalette
 beq KrLadderNativePalette
 lda $c626
 and #15
 asl
 asl
 asl
 asl
 cmp $03
 bcc KrLadderNativePalette
 lda #$80
 bne KrLadderPaletteReady
KrLadderNativePalette:
 lda ($09),y
 tay
 lda NativeAttributes,y
 and #$c0
KrLadderPaletteReady:
 sta $06
 lda $07
 lsr
 lsr
 ora $06
 sta $07
 inx
 cpx #4
 bcc KrLadderAttributeCells
 ldx VRAM_Buffer1_Offset
 lda $07
 sta NativeVRAM3,x
 lda #0
 sta NativeVRAM4,x
 txa
 clc
 adc #4
 sta VRAM_Buffer1_Offset
 rts
KrLadderAttributeOffsets:
 .byte $00,$01,$10,$11
