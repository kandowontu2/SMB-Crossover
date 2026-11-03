.export MiniVectors,MiniHostMain,MiniHostFresh,MiniHostDraw,MiniHostGraphics
.export MiniHostHead,MiniHostSide,MiniHostBox,MiniHostColors,MiniHostName
.export MiniHostBounce,MiniHostEnd
MiniReady=$C300
MiniEpoch=$C301
MiniCacheX=$C302
MiniCacheY=$C304
MiniOldX=$C306
MiniOldY=$C308
MiniHostTemp=$C309
MiniHostTempHi=$C30A
MiniVectors:
 jmp MiniHostMain         ;0 movement
 jmp MiniHostGraphics     ;1 graphics
 jmp MiniHostDraw         ;2 draw
 jmp MiniHostGraphics     ;3 chr bank
 jmp MiniHostNo           ;4 native shot fallback
 jmp MiniHostNo           ;5 native injury fallback
 jmp MiniHostStatus       ;6 native power tier authority
 jmp MiniHostNo           ;7 native death start fallback
 jmp MiniHostNo           ;8 native death update fallback
 jmp MiniHostYes          ;9 visible owner
 jmp MiniHostHead         ;10 exact pending source head getter
 jmp MiniHostBody         ;11 ordinary native stomp allowed
 jmp MiniHostAdder        ;12 native small probe group
 jmp MiniHostBoxType      ;13 native small body group
 jmp MiniHostSide         ;14 real native getter
 jmp MiniHostFresh        ;15 fresh life
 jmp MiniHostBox          ;16 exact source body bounds
 jmp MiniHostPortrait     ;17 native menu anchor
 jmp MiniHostName         ;18 menu name
 jmp MiniHostNo           ;19 unimplemented source capability
 jmp MiniHostNo           ;20 unimplemented source capability
 jmp MiniHostNo           ;21 native death query fallback
 jmp MiniHostNo           ;22 native fallback
 jmp MiniHostYes          ;23 mature pickup allowed
 jmp MiniHostNo           ;24 native fallback
 jmp MiniHostNo           ;25 native fallback
 jmp MiniHostColors       ;26 player colors
 jmp MiniHostNo           ;27 ordinary native bounce policy
 jmp MiniHostNo           ;28 native fallback
 jmp MiniHostNo           ;29 native fallback
 jmp MiniHostName         ;30 actual WriteGameText header patch
 jmp MiniHostBounce       ;31 explicit native stomp event
 jmp MiniHostWorldColors  ;32 original world palette selector
 jmp MiniHostNo           ;33 source capability absent
 jmp MiniHostYes          ;34 weapon tail handled (no source projectile)
 jmp MiniHostNo           ;35 reserved
 jmp MiniHostFresh        ;36 actual scene constructor
 jmp MiniHostNo           ;37 ordinary native contact fallback

MiniHostNo: clc
 rts
MiniHostYes: sec
 rts
MiniHostStatus:
 lda PlayerStatus
 sec
 rts
MiniHostBody:
 lda #0
 sta GuestBodyNoStomp
 clc
 rts
MiniHostAdder:
 ldy #2
 sec
 rts
MiniHostBoxType:
 ldy #1
 sec
 rts
MiniHostBounce:
 lda #1
 sta bounce
 lda #12
 sta queued
 sec
 rts

MiniHostFresh:
 jsr MiniInit
 lda #0
 ldx #$23
@clear:
 sta $C300,x
 dex
 bpl @clear
 lda #1
 sta MiniReady
 sta MiniLeft
 sta MiniTop
 lda #6
 sta MiniRight
 lda #7
 sta MiniBottom
 sec
 rts

MiniHostMain:
 lda GameEngineSubroutine
 cmp #8
 bne MiniHostYes
 lda GamePauseStatus
 and #1
 bne MiniHostYes
 lda TimerControl
 bne MiniHostYes
 lda MiniReady
 bne @ready
 jsr MiniHostFresh
@ready:
 cmp #2
 beq @anchored
 lda Player_Y_HighPos
 cmp #1
 bne MiniHostYes
 lda #24                  ; Native small initial Y is 16 above canvas top.
 jsr MiniHostImportY
 jsr MiniHostImportX
 lda #2
 sta MiniReady
 bne @step
@anchored:
 lda FrameCounter
 cmp MiniEpoch
 beq MiniHostYes
 lda Player_X_Position
 cmp MiniCacheX
 bne @correctx
 lda Player_PageLoc
 cmp MiniCacheX+1
 beq @checky
@correctx:
 jsr MiniHostImportX
@checky:
 lda Player_Y_Position
 cmp MiniCacheY
 bne @correcty
 lda Player_Y_HighPos
 cmp MiniCacheY+1
 beq @step
@correcty:
 lda #8
 jsr MiniHostImportY
@step:
 lda FrameCounter
 sta MiniEpoch
 lda Player_X_Position
 sta MiniOldX
 lda Player_PageLoc
 sta MiniOldX+1
 lda Player_Y_Position
 sta MiniOldY
 lda PlayerStatus
 sta MiniTier
 beq @small
 lda MiniCrouched
 bne @small
 lda #$F9
 bne @top
@small:
 lda #1
@top:
 sta MiniTop
 lda ScreenLeft_X_Pos
 sta MiniCoord
 lda ScreenLeft_PageLoc
 sta MiniCoord+1
 jsr MiniHostToSubpixel
 lda MiniCoord
 sta MiniEdgeLeft
 lda MiniCoord+1
 sta MiniEdgeLeft+1
 clc
 adc #15                  ; +240 pixels = +3840 subpixels.
 sta MiniEdgeRight+1
 lda MiniCoord
 sta MiniEdgeRight
 lda SavedJoypadBits
 sta MiniHeld
 jsr MiniStep
 jsr MiniHostWallJump
 jsr MiniAnimate
 jsr MiniHostPixelX
 lda MiniCoord
 sta Player_X_Position
 sta MiniCacheX
 sec
 sbc MiniOldX
 sta Player_X_Scroll
 asl a
 asl a
 asl a
 asl a
 sta Player_X_Speed
 lda MiniCoord+1
 sta Player_PageLoc
 sta MiniCacheX+1
 jsr MiniHostPixelY
 sec
 lda MiniCoord
 sbc #8
 sta Player_Y_Position
 sta MiniCacheY
    lda MiniCoord+1
    sbc #0
    clc
    adc #1
    sta Player_Y_HighPos
    sta MiniCacheY+1
    lda Player_Y_Position
 sec
 sbc MiniOldY
 sta Player_Y_Speed
 lda MiniHeadPending
 beq @headspeed
 lda #$FF
 sta Player_Y_Speed
@headspeed:
 lda MiniFacing
 cmp #3
 bne @right
 lda #2
 bne @face
@right:
 lda #1
@face:
 sta PlayerFacingDir
 lda queued
 cmp #3
 beq @ground
 cmp #4
 beq @ground
 cmp #6
 beq @ground
 cmp #7
 beq @ground
 cmp #9
 beq @ground
 cmp #10
 beq @ground
 lda yvel+1
 bmi @up
 lda #2
 bne @state
@up:
 lda #1
 bne @state
@ground:
 lda #0
@state:
 sta Player_State
 sec
 rts

; Explicit user-authorized native adaptation. Uses original queued jump pulse.
MiniHostWallJump:
 lda MiniContacts
 and #1
 bne @done
 lda yvel+1
 bmi @done
 lda MiniContacts
 and #12
 beq @done
 and #8
 beq @left
 lda MiniHeld
 and #1
 bne @cling
 rts
@left:
 lda MiniHeld
 and #2
 beq @done
@cling:
 lda #0
 sta yvel
 sta yvel+1
 lda MiniFresh
 and #$80
 beq @done
 lda #0
 sta bounce
 lda #12
 sta queued
@done:
 rts

MiniHostImportX:
 lda MiniX
 and #15
 pha
 lda Player_X_Position
 sta MiniCoord
 lda Player_PageLoc
 sta MiniCoord+1
 jsr MiniHostToSubpixel
 pla
 ora MiniCoord
 sta MiniX
 lda MiniCoord+1
 sta MiniX+1
 rts
MiniHostImportY:
 clc
 adc Player_Y_Position
 sta MiniCoord
 lda Player_Y_HighPos
 adc #$FF
 sta MiniCoord+1
 lda MiniY
 and #15
 pha
 jsr MiniHostToSubpixel
 pla
 ora MiniCoord
 sta MiniY
 lda MiniCoord+1
 sta MiniY+1
 rts
MiniHostToSubpixel:
 ldx #4
@shift:
 asl MiniCoord
 rol MiniCoord+1
 dex
 bne @shift
 rts
MiniHostPixelX:
 lda MiniX
 sta MiniCoord
 lda MiniX+1
 sta MiniCoord+1
 jmp MiniToPixel
MiniHostPixelY:
 lda MiniY
 sta MiniCoord
 lda MiniY+1
 sta MiniCoord+1
 jmp MiniToPixel

MiniHostGraphics:
 lda #<968
 sta CurrentCHRBank+4
 lda #$83
 sta X5ChrMode+4
 lda #0
 sta SsChrActive
 sta ObjectMetasprite
 lda #<ObjectMetasprite
 sta SmPosePtr
 lda #>ObjectMetasprite
 sta SmPosePtr+1
 lda #1
 sta X5WideChrActive
 sta ReloadCHRBank
 sec
 rts
MiniHostDraw:
 jsr MiniHostPixelX
 sec
 lda MiniCoord
 sbc ScreenLeft_X_Pos
 sta MiniRenderX
 lda MiniCoord+1
 sbc ScreenLeft_PageLoc
 sta MiniRenderX+1
 jsr MiniHostPixelY
 sec
 lda MiniCoord
 sbc #8
 sta MiniRenderY
 lda MiniCoord+1
 sbc #0
 sta MiniRenderY+1
 jmp MiniNativeDraw
MiniHostPortrait:
 lda #0
 sta MiniPose
 lda R4
 sta MiniRenderX
 lda R5
 sta MiniRenderX+1
 lda R6
 sta MiniRenderY
 lda R7
 sta MiniRenderY+1
 jsr MiniHostGraphics
 jmp MiniNativeDraw

MiniHostBox:
 lda Player_Rel_XPos
 clc
 adc MiniLeft
 sta BoundingBox_UL_Corner
 lda Player_Y_Position
 clc
 adc #8
 clc
 adc MiniTop
 sta BoundingBox_UL_Corner+1
 lda Player_Rel_XPos
 clc
 adc MiniRight
 sta BoundingBox_UL_Corner+2
 lda Player_Y_Position
 clc
 adc #8
 clc
 adc MiniBottom
 sta BoundingBox_UL_Corner+3
 ldx #0
 ldy #0
 sec
 rts
MiniHostSide:
 jmp BlockBufferColli_Side
MiniHostHead:
 lda MiniHeadPending
 beq @native
 lda #0
 sta MiniHeadPending
 lda GameEngineSubroutine
 cmp #8
 bne @native
 tya
 pha
 lda MiniHeadY
 and #$F0
 sec
 sbc #32
 sta R2
 lda MiniHeadAddress
 sec
 sbc R2
 sta R6
 lda MiniHeadAddress+1
 sbc #0
 sta R7
 lda MiniHeadTile
 sta R3
 lda MiniHeadY
 and #15
 sta R4
 lda MiniHeadX
 sta R5
 pla
 tay
 ldx #0
 lda R3
 rts
@native:
 jmp BlockBufferColli_Head

MiniHostWorldColors:
 lda AreaType
 asl a
 sta R0
 asl a
 clc
 adc R0
 adc #6
 tay
 jmp MiniHostColors
MiniHostColors:
 php
 pha
 txa
 pha
 tya
 pha
 ldx VRAM_Buffer1_Offset
 cpx #77
 bcs @done
 lda #$3F
 sta VRAM_Buffer1,x
 lda #$10
 sta VRAM_Buffer1+1,x
 lda #4
 sta VRAM_Buffer1+2,x
 ldy BackgroundColorCtrl
 bne @backdrop
 ldy AreaType
@backdrop:
 lda MiniBackdrop,y
 sta VRAM_Buffer1+3,x
 lda #$27
 sta VRAM_Buffer1+4,x
 ldy PlayerStatus
 cpy #2
 beq @fire
 lda #$16
 sta VRAM_Buffer1+5,x
 lda #$18
 bne @third
@fire:
 lda #$37
 sta VRAM_Buffer1+5,x
 lda #$16
@third:
 sta VRAM_Buffer1+6,x
 txa
 clc
 adc #7
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
@done:
 pla
 tay
 pla
 tax
 pla
 plp
 sec
 rts
MiniBackdrop: .byte $22,$22,$0F,$0F,$0F,$22,$0F,$0F
MiniHostName:
 php
 pha
 txa
 pha
 tya
 pha
 lda OperMode
 beq @menu
 tsx
 lda $0103,x
 bne @done
 ldy #8
@hud:
 lda MiniName,y
 sta VRAM_Buffer1+11,y
 dey
 bpl @hud
 bmi @done
@menu:
 ldx VRAM_Buffer1_Offset
 cpx #65
 bcs @done
 lda #$23
 sta VRAM_Buffer1,x
 lda #$28
 sta VRAM_Buffer1+1,x
 lda #16
 sta VRAM_Buffer1+2,x
 ldy #0
@menucopy:
 lda MiniMenuName,y
 sta VRAM_Buffer1+3,x
 inx
 iny
 cpy #16
 bcc @menucopy
 inx
 inx
 inx
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
@done:
 pla
 tay
 pla
 tax
 pla
 plp
 sec
 rts
MiniName: .byte $16,$12,$17,$12,$16,$0A,$1B,$12,$18
MiniMenuName: .byte $24,$24,$24,$16,$12,$17,$12,$16,$0A,$1B,$12,$18,$24,$24,$24,$24
MiniHostEnd:
