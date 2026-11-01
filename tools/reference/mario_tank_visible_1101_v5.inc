; Selected Tank0/7 only, reached exclusively after the complete ROM gate.
; Code aliases C2DCA0/A2BCA0. Native OAM/geometry/clipping owners are retained.
; C880..888 is dead terrain-query storage after physics, reused for at most
; two native 8x16 shoe records. C889..88B retain terrain state.
.segment "MT_VISIBLE"
MtArtPostV5:
 lda #<502
 ldx #>502
 ldy #5
 MtHostFar X5SetPhysicalChr
 ; The native four-cell flower descriptor alone uses78/7A in the fixed
 ; native atlas. Keep its coordinates, mirroring and two-frame palettes.
 lda Enemy_Flag+5
 beq MtArtBodyV5
 lda PowerUpType+5
 cmp #1
 bne MtArtBodyV5
 ldx #1
MtPickupCellV5:
 lda Sprite_Data,x
 cmp #$78
 beq MtPickupTopV5
 cmp #$7a
 bne MtPickupNextV5
 lda #$69
 bne MtPickupStoreV5
MtPickupTopV5:
 lda #$67
MtPickupStoreV5:
 sta Sprite_Data,x
MtPickupNextV5:
 inx
 inx
 inx
 inx
 cpx #1
 bne MtPickupCellV5
MtArtBodyV5:
 lda PlayerStatus
 cmp #2
 jne MtArtDoneV5
 lda ObjectMetasprite
 jeq MtArtDoneV5
 cmp #29
 jcs MtArtDoneV5
 bit ObjectVerticalFlip
 jmi MtArtDoneV5             ; native inverted death art has no worn shoe overlay
 ; The reservation hook has already left8 bytes before world OAM. Move
 ; the unchanged native four-cell body backwards, then draw masks first.
 ldx #15
MtMoveBodyV5:
 lda Sprite_Data,x
 sta Sprite_Data+8,x
 dex
 bpl MtMoveBodyV5
 lda #$f8
 sta Sprite_Data
 sta Sprite_Data+4
 lda CurrentBankC
 pha
 lda #2
 sta CurrentBankC
 sta $5116
 lda ObjectMetasprite
 sec
 sbc #1
 ldx PlayerFacingDir
 cpx #1
 beq MtPoseSideV5
 clc
 adc #28
MtPoseSideV5:
 tax
 lda MtShoeLookupV5,x
 tax
 ldy #1
MtDecodeShoeV5:
 lda MtShoeRecordsV5,x
 sta R2
 and #$1f
 asl
 ora #$41
 sta $c880,y
 iny
 lda R2
 and #$60
 asl
 sta $c880,y
 iny
 lda MtShoeRecordsV5+2,x
 sta $c880,y
 iny
 lda MtShoeRecordsV5+1,x
 sta $c880,y
 iny
 inx
 inx
 inx
 lda R2
 bpl MtDecodeShoeV5
 dey
 sty $c880
 lda #<$c880
 sta R0
 lda #>$c880
 sta R1
 lda FrameCounter
 lsr
 and #3
 sta R3
 lda Player_SprAttrib
 and #$20
 ora R3
 sta R3
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda Player_PageLoc
 sbc ScreenLeft_PageLoc
 sta R5
 lda Player_Y_HighPos
 sta R7
 lda ObjectVerticalFlip
 and #$3f
 cmp #$20
 bcc MtPositiveYOffsetV5
 ora #$c0
 clc
 adc Player_Y_Position
 bcs MtShoeYReadyV5
 dec R7
 bcc MtShoeYReadyV5
MtPositiveYOffsetV5:
 adc Player_Y_Position
 bcc MtShoeYReadyV5
 inc R7
MtShoeYReadyV5:
 sta R6
 lda #0
 sta CurrentOAMOffset
 MtHostFar MetaspriteRenderLoop
 pla
 sta CurrentBankC
 sta $5116
 lda #24
 sta CurrentOAMOffset
MtArtDoneV5:
 rts
MtArtPostEndV5:
