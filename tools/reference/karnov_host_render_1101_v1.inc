; Original Karnov body/projectiles. Metadata lives in C2 during native farcalls.
.import ObjectMetasprite,SmPosePtr,Player_SprAttrib,VRAM_Buffer1,VRAM_Buffer1_Offset
.import X5SetPhysicalChr,MetaspriteRenderLoop,FarCallCommon,FarcallJmpTarget_SMC,SafecallA_SMC
.import BackgroundColorCtrl
.export KrGraphics,KrDraw,KrColors,KrCopyArt,KrArtImage,KrArtEnd,KrShotTiles
.export KrRebaseShots,KrCameraLo,KrCameraHi
KrCameraLo=$c821
KrCameraHi=$c822
KrCameraDelta=$c823
KrChrIndex=$c824
KrRenderCameraLo=$c825
KrRenderCameraHi=$c826
KrPoseIndex=$c830
KrEmpty=$c831
KrShotCursor=$c832
KrShotPacket=$c834
KrPoseLo=$d000
KrPoseHi=$d040
KrPosePage=$d080
.macro KrFar Target
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(Target)|$80)
 jsr FarCallCommon
.endmacro

KrCopyArt:
 lda ScreenLeft_X_Pos
 sta KrCameraLo
 lda ScreenLeft_PageLoc
 sta KrCameraHi
 lda #0
 sta R0
 lda #$d0
 sta R1
 lda #<KrArtImage
 sta R2
 lda #>KrArtImage
 sta R3
 lda #<(KrArtEnd-KrArtImage)
 sta R4
 lda #>(KrArtEnd-KrArtImage)
 sta R5
 ldy #0
KrCopyArtByte:
 lda (R2),y
 sta (R0),y
 inc R0
 bne :+
 inc R1
:inc R2
 bne :+
 inc R3
:lda R4
 bne :+
 dec R5
:dec R4
 lda R4
 ora R5
 bne KrCopyArtByte
 rts
; The original9 slots use viewport X. Translate existing shots before actor
; spawning and before their original update, keeping new shots at this camera.
KrRebaseShots:
 lda ScreenLeft_X_Pos
 sec
 sbc KrCameraLo
 sta KrCameraDelta
 lda ScreenLeft_PageLoc
 sbc KrCameraHi
 bne KrClearCameraShots
 lda KrCameraDelta
 beq KrCameraDone
 ldx #24
KrCameraShotLoop:
 lda KrState+$6e,x
 bpl KrCameraShotNext
 lda KrState+$6f,x
 sec
 sbc KrCameraDelta
 bcs KrStoreCameraShot
 lda #0
 sta KrState+$6e,x           ; no viewport-wrap respawn on the right edge
 beq KrCameraShotNext
KrStoreCameraShot:
 sta KrState+$6f,x
KrCameraShotNext:
 dex
 dex
 dex
 bpl KrCameraShotLoop
 bmi KrCameraDone
KrClearCameraShots:
 jsr Kr_C2B7                ; genuine original9-slot clear on a scene jump
KrCameraDone:
 lda ScreenLeft_X_Pos
 sta KrCameraLo
 lda ScreenLeft_PageLoc
 sta KrCameraHi
 rts
KrChoosePose:
 lda KrState+$62
 and #31
 sta KrPoseIndex
 sta KrChrIndex              ; source publishes real state's CHR before flash
 lda KrState+$68
 and #$40
 beq KrPoseFacing
 lda KrState+$e8
 and #1
 beq KrPoseFacing
 lda #29                    ; genuine source blank/hurt-flash selector
 sta KrPoseIndex
KrPoseFacing:
 lda KrState+$62
 bpl :+
 lda KrPoseIndex
 ora #32
 sta KrPoseIndex
:rts
KrGraphics:
 KrSave
 jsr KrGraphicsCore
 KrRestore
 sec
 rts
; KrDraw already owns the complete save frame. Reuse the body without a
; second twelve-byte save across the native CHR farcalls.
KrGraphicsCore:
 lda KrReady
 cmp #$a7
 jne KrGraphicsDone
 jsr KrChoosePose
 ldx KrChrIndex
 lda KrPosePage,x
 clc
 adc #<407
 ldx #>407
 ldy #0
 KrFar X5SetPhysicalChr
 lda #<410
 ldx #>410
 ldy #3                     ; even tilesC0..FE are P0/window3, not P1/window6
 KrFar X5SetPhysicalChr
 lda #0
 sta KrEmpty
 sta ObjectMetasprite
 lda #<KrEmpty
 sta SmPosePtr
 lda #>KrEmpty
 sta SmPosePtr+1
KrGraphicsDone:
 rts
KrDraw:
 KrSave
 lda KrReady
 cmp #$a7
 jne KrDrawDone
 jsr KrGraphicsCore
 ldx KrPoseIndex
 lda KrPoseLo,x
 sta R0
 lda KrPoseHi,x
 sta R1
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda Player_PageLoc
 sbc ScreenLeft_PageLoc
 sta R5
 lda R4
 clc
 adc #8                     ; original source center relative to native anchor
 sta R4
 lda R5
 adc #0
 sta R5
 lda Player_Y_Position
 clc
 adc #32
 sta R6
 lda Player_Y_HighPos
 adc #0                     ; native generic renderer expects Ypage1
 sta R7
 lda Player_SprAttrib
 and #$20
 sta R3
 KrFar MetaspriteRenderLoop
 jsr KrDrawShots
KrDrawDone:
 KrRestore
 sec
 rts

KrDrawShots:
 lda ScreenLeft_X_Pos
 sec
 sbc KrCameraLo
 sta KrRenderCameraLo
 lda ScreenLeft_PageLoc
 sbc KrCameraHi
 sta KrRenderCameraHi
 lda KrState+$65
 and #15
 cmp #8
 beq KrDrawBoomerang
 cmp #3
 bcs KrShotsDone
 lda #0
 sta KrShotCursor
KrDrawShotLoop:
 ldx KrShotCursor
 lda KrState+$6e,x
 bpl KrNextShot
 and #$30
 bne KrImpactTile
 lda KrState+$e8
 and #$10
 beq :+
 lda #1
:tax
 lda KrShotTiles,x
 jmp KrShotReady
KrImpactTile:
 lda KrShotTiles+2
KrShotReady:
 jsr KrEmitShot
KrNextShot:
 lda KrShotCursor
 clc
 adc #3
 sta KrShotCursor
 cmp #27
 bcc KrDrawShotLoop
KrShotsDone:rts
KrDrawBoomerang:
 lda KrState+$6e
 bpl KrShotsDone
 lda #0
 sta KrShotCursor
 lda KrState+$e8
 and #12
 lsr
 lsr
 tax
 lda KrShotTiles+3,x
KrEmitShot:
 sta KrShotPacket+1
 lda #4
 sta KrShotPacket
 lda #0
 sta KrShotPacket+2
 sta KrShotPacket+3
 sta KrShotPacket+4
 sta R3
 ldx KrShotCursor
 lda KrState+$6f,x
 sec
 sbc KrRenderCameraLo
 sta R4
 lda #0
 sbc KrRenderCameraHi
 sta R5
 lda KrState+$70,x
 sta R6
 lda #1
 sta R7
 lda #<KrShotPacket
 sta R0
 lda #>KrShotPacket
 sta R1
 KrFar MetaspriteRenderLoop
 rts

KrColors:
 KrSave
 lda KrReady
 cmp #$a7
 bne KrColorsDone
 ldx VRAM_Buffer1_Offset
 cpx #72
 bcs KrColorsDone
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$10                   ; native palette owns the shared background too
 sta VRAM_Buffer1+1,x
 lda #4
 sta VRAM_Buffer1+2,x
 ldy BackgroundColorCtrl
 bne :+
 ldy AreaType
:lda KrNativeBackgroundColors,y
 sta VRAM_Buffer1+3,x
 ldy #0
 lda KrState+$68
 bpl :+
 ldy #3
:lda KrPalette,y
 sta VRAM_Buffer1+4,x
 lda KrPalette+1,y
 sta VRAM_Buffer1+5,x
 lda KrPalette+2,y
 sta VRAM_Buffer1+6,x
 lda #0
 sta VRAM_Buffer1+7,x
 txa
 clc
 adc #7
 sta VRAM_Buffer1_Offset
KrColorsDone:
 KrRestore
 sec
 rts
KrPalette:.byte $28,$16,$0f,$10,$1c,$0f
KrNativeBackgroundColors:.incbin "kr-native-bg.bin"
KrShotTiles:.incbin "kr-shot-tiles.bin"
KrArtImage:.incbin "kr-pose-meta.bin"
KrArtEnd:
