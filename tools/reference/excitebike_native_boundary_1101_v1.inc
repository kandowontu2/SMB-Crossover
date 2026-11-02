; Deliberate SMB side-view adaptations. Right/Left request unsigned original
; throttle in either facing; reversing first coasts to zero. B selects original
; turbo instead. A's fresh edge calls the genuine source ExAirLaunch. Up/Down
; become original backward/forward lean. Native metatiles never become slopes.
; Source speed, fractions, launch, gravity, heat, lean and pose remain original.
ExReady=$c800
ExLastEpoch=$c801
ExHaveEpoch=$c802
ExPrevious=$c803
ExFacing=$c804
ExDesired=$c805
ExDelta=$c806
ExOldY=$c807
ExLastDy=$c808
ExQueryX=$c809
ExQueryY=$c80b
ExQueryTile=$c80d
ExQuerySolid=$c80e
ExMirrorPacket=$c880
ExMetadata=$d000
ExNativeTileAttributes=$d201

.macro ExHostSave
 php
 pha
 txa
 pha
 tya
 pha
 .repeat 8,I
 lda R0+I
 pha
 .endrepeat
.endmacro
.macro ExHostRestore
 .repeat 8,I
 pla
 sta R7-I
 .endrepeat
 pla
 tay
 pla
 tax
 pla
 plp
.endmacro
.macro ExHostFar Target,Bank
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #Bank
 jsr FarCallCommon
.endmacro
.import ExState,ExMotorAll,ExSlopePose,ExFractionalX,ExAirLaunch,ExAirStep,ExTemperature,ExPose
.import ExCrashAll,ExRecoveryAll,ExLaneAll,ExHeatRelease
.export ExHostConstruct,ExHostMovement,ExHostGraphics,ExHostDraw,ExHostColors,ExHostWorldColors,ExHostEnd
.export ExHostScene
.export ExHostHead,ExHostSide,ExHostBody,ExHostAdder,ExHostInjury,ExHostInjuryStatus,ExHostBounce
.export ExHostWeapons
.export ExHostStatus
.segment "EX_HOST"
ExHostScene:
 php
 pha
 jsr ExHostGraphics
 lda ExReady
 cmp #$a7
 beq ExSceneReady
 jsr ExHostConstruct
ExSceneReady:
 pla
 plp
 sec
 rts
ExHostConstruct:
 clc
 ExHostSave
 lda OperMode
 cmp #1
 jne ExConstructReturn
 lda DisableScreenFlag
 jeq ExConstructReturn
 lda Mirror_PPUMASK
 and #$18
 jne ExConstructReturn
 lda NmiDisable
 jpl ExConstructReturn
 lda FamilyMainCommit
 and #1
 jeq ExConstructReturn
 lda #0
 sta ExReady
 sta R0
 lda #$c0
 sta R1
 ldy #0
 ldx #8
ExConstructPage:
 lda #0
ExConstructByte:
 sta (R0),y
 iny
 bne ExConstructByte
 inc R1
 dex
 bne ExConstructPage
 ldx #$7f
 lda #0
ExConstructContext:
 sta $c800,x
 dex
 bpl ExConstructContext
 lda #1
 sta ExState+$04f
 sta ExState+$0a8
 sta ExFacing
 lda #6
 sta ExState+$0ac
 sta ExState+$368
 lda #$20                  ; Source middle lane; lane geometry stays private.
 sta ExState+$0b8
 lda PlayerFacingDir
 cmp #2
 bne ExConstructHeight
 sta ExFacing
ExConstructHeight:
 lda PlayerSize
 beq ExConstructPosition
 lda Player_Y_Position
 sec
 sbc #16                   ; Native32px body preserves the existing foot Y.
 sta Player_Y_Position
 lda Player_Y_HighPos
 sbc #0
 sta Player_Y_HighPos
ExConstructPosition:
 lda #0
 sta PlayerSize
 sta CrouchingFlag
 lda #$a7
 sta ExReady
 tsx
 lda $010c,x
 ora #1
 sta $010c,x
ExConstructReturn:
 ExHostRestore
 rts

ExHostMovement:
 ExHostSave
 lda ExReady
 cmp #$a7
 jne ExMovementReturn
 lda OperMode
 cmp #1
 jne ExMovementReturn
 lda GameEngineSubroutine
 cmp #8
 jne ExMovementReturn
 lda GamePauseStatus
 and #1
 jne ExMovementReturn
 lda ExHaveEpoch
 beq ExMovementAccepted
 lda FrameCounter
 cmp ExLastEpoch
 jeq ExMovementReturn
ExMovementAccepted:
 lda FrameCounter
 sta ExLastEpoch
 lda #1
 sta ExHaveEpoch
 inc ExState+$03f
 lda ExState+$03f
 and #3
 sta ExState+$04c
 ldx #3
ExTickTimers:
 lda ExState+$026,x
 beq :+
 dec ExState+$026,x
:
 lda ExState+$02a,x
 beq :+
 dec ExState+$02a,x
:
 lda ExState+$036,x
 beq :+
 dec ExState+$036,x
:
 dex
 bpl ExTickTimers
 lda ExState+$03c
 beq :+
 dec ExState+$03c
:
 jsr ExHeatRelease
 lda Player_State
 bne ExImportAir
 jsr ExGround
 jmp ExImportY
ExImportAir:
 lda ExState+$0b0
 bne ExCheckHead
 jsr ExFall
ExCheckHead:
 lda ExLastDy
 bpl ExImportY
 lda Player_Y_Speed
 bmi ExImportY
 ; Native head response has already resolved the last upward movement.
 jsr ExFall
ExImportY:
 lda Player_Y_Position
 sta ExState+$08c
 sta ExOldY
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sta ExState+$080
 jsr ExInput
 ldx #0
 lda #0
 sta ExState+$0d4           ; Explicit native flat support, source slope0.
 jsr ExSlopePose
 jsr ExMotorAll
 jsr ExTemperature
 ldx #0
 jsr ExFractionalX
 lda ExState+$060
 ldx ExFacing
 cpx #2
 bne ExDeltaReady
 eor #$ff
 clc
 adc #1
ExDeltaReady:
 sta ExDelta
 sta Player_X_Scroll
 asl
 asl
 asl
 asl
 sta Player_X_Speed
 lda ExDelta
 ldx #0
 cmp #$80
 bcc :+
 dex
:
 clc
 adc Player_X_Position
 sta Player_X_Position
 txa
 adc Player_PageLoc
 sta Player_PageLoc
 lda SavedJoypadBits
 eor ExPrevious
 and SavedJoypadBits
 and #$80
 beq ExAirUpdate
 lda Player_State
 bne ExAirUpdate
 lda ExState+$098
 ora ExState+$3e0
 bne ExAirUpdate
 ldx #0
 jsr ExAirLaunch
 lda #1
 sta Player_State
ExAirUpdate:
 lda SavedJoypadBits
 sta ExPrevious
 ldx #0
 jsr ExAirStep
 jsr ExCrashAll
 jsr ExRecoveryAll
 jsr ExLaneAll
 lda ExState+$08c
 sec
 sbc ExOldY
 sta Player_Y_Speed
 sta ExLastDy
 ldx #0
 cmp #$80
 bcc :+
 dex
:
 clc
 adc Player_Y_Position
 sta Player_Y_Position
 txa
 adc Player_Y_HighPos
 sta Player_Y_HighPos
 jsr ExSupport
 lda ExFacing
 sta PlayerFacingDir
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sta Player_Pos_ForScroll
 lda #0
 sta PlayerSize
 sta CrouchingFlag
ExMovementReturn:
 ExHostRestore
 sec
 rts

ExInput:
 lda #0
 sta ExState+$05c
 lda ExFacing
 sta ExDesired
 lda SavedJoypadBits
 and #3
 cmp #3
 beq ExLean
 cmp #0
 beq ExTurbo
 sta ExDesired
 cmp ExFacing
 beq ExThrottle
 lda ExState+$090
 ora ExState+$094
 bne ExLean                  ; Original coast/braking before reversal.
 lda ExDesired
 sta ExFacing
ExThrottle:
 lda #$80
 sta ExState+$05c
ExTurbo:
 lda SavedJoypadBits
 and #$40
 beq ExLean
 sta ExState+$05c
ExLean:
 lda SavedJoypadBits
 and #8
 beq :+
 lda ExState+$05c
 ora #2
 sta ExState+$05c
:
 lda SavedJoypadBits
 and #4
 beq :+
 lda ExState+$05c
 ora #1
 sta ExState+$05c
:
 rts

ExGround:
 lda #0
 sta ExState+$0b0
 sta ExState+$378
 sta ExState+$37c
 sta ExState+$380
 sta ExState+$384
 sta ExState+$364
 rts
ExFall:
 jsr ExGround
 lda #2
 sta ExState+$0b0
 rts

; Native block buffers and MTileAttribute are the only terrain lookup domain.
; Input ExQueryX=world X16, ExQueryY=SMB Y16 (viewport page1).
ExQuery:
 lda #0
 sta ExQuerySolid
 lda ExQueryY+1
 cmp #1
 bne ExQueryReturn
 lda ExQueryY
 sec
 sbc #32
 bcc ExQueryReturn
 cmp #208
 bcs ExQueryReturn
 and #$f0
 tay
 lda ExQueryX+1
 and #1
 beq ExQueryBuffer1
 lda #<Block_Buffer_2
 bne ExQueryBufferReady
ExQueryBuffer1:
 lda #<Block_Buffer_1
ExQueryBufferReady:
 sta R6
 lda #>Block_Buffer_1
 sta R7
 lda ExQueryX
 lsr
 lsr
 lsr
 lsr
 clc
 adc R6
 sta R6
 lda (R6),y
 sta ExQueryTile
 tax
 lda ExNativeTileAttributes,x
 and #3
 cmp #1
 bne ExQueryReturn
 lda #1
 sta ExQuerySolid
ExQueryReturn:
 lda ExQuerySolid
 rts
ExSupport:
 lda Player_Y_Speed
 bmi ExSupportReturn
 lda Player_Y_Position
 clc
 adc #32
 sta ExQueryY
 lda Player_Y_HighPos
 adc #0
 sta ExQueryY+1
 lda Player_X_Position
 clc
 adc #2
 sta ExQueryX
 lda Player_PageLoc
 adc #0
 sta ExQueryX+1
 jsr ExQuery
 bne ExSupportFound
 lda Player_X_Position
 clc
 adc #13
 sta ExQueryX
 lda Player_PageLoc
 adc #0
 sta ExQueryX+1
 jsr ExQuery
 bne ExSupportFound
 lda Player_State
 bne ExSupportReturn
 lda #2
 sta Player_State
 jsr ExFall
 rts
ExSupportFound:
 lda ExQueryY
 and #15
 cmp #8
 bcs ExSupportReturn
 lda Player_Y_Position
 and #$f0
 sta Player_Y_Position
 lda #0
 sta Player_State
 sta Player_Y_Speed
 sta ExLastDy
 jsr ExGround
ExSupportReturn:
 rts

ExHostGraphics:
 ExHostSave
 ldx #3
ExGraphicsLoop:
 lda ExBodyLow,x
 sta CurrentCHRBank+4,x
 lda #$82
 sta X5ChrMode+4,x
 dex
 bpl ExGraphicsLoop
 lda #0
 sta SsChrActive
 sta ObjectMetasprite
 lda #<ObjectMetasprite
 sta SmPosePtr
 lda #>ObjectMetasprite
 sta SmPosePtr+1              ; Stable zero native header: private draw owns OAM.
 lda #1
 sta X5WideChrActive
 sta ReloadCHRBank
 ExHostRestore
 sec
 rts
ExBodyLow:.byte <736,<737,<738,<739

ExHostDraw:
 ExHostSave
 lda ExReady
 cmp #$a7
 jne ExDrawReturn
 ; Native landing/platform resolution happens before this public draw call.
 lda Player_State
 bne :+
 jsr ExGround
:
 ldx #0
 jsr ExPose
 cmp #23
 jcs ExDrawReturn
 asl
 tay
 lda ExMetadata,y
 sta R0
 lda ExMetadata+1,y
 clc
 adc #>ExMetadata
 sta R1
 lda ExFacing
 cmp #2
 bne ExDrawPacketReady
 ldy #0
 lda (R0),y
 sta ExMirrorPacket
 tay
ExMirrorLoop:
 lda (R0),y
 eor #$ff
 clc
 adc #$f9
 sta ExMirrorPacket,y
 dey
 lda (R0),y
 sta ExMirrorPacket,y
 dey
 lda (R0),y
 eor #$40
 sta ExMirrorPacket,y
 dey
 lda (R0),y
 sta ExMirrorPacket,y
 dey
 bne ExMirrorLoop
 lda #<ExMirrorPacket
 sta R0
 lda #>ExMirrorPacket
 sta R1
ExDrawPacketReady:
 lda Player_X_Position
 clc
 adc #8
 sta R4
 lda Player_PageLoc
 adc #0
 sta R5
 lda R4
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda R5
 sbc ScreenLeft_PageLoc
 sta R5
 lda Player_Y_Position
 sta R6
 lda Player_Y_HighPos
 sta R7
 lda Player_SprAttrib
 and #$20
 sta R3
 ExHostFar MetaspriteRenderLoop,Bank_MetaspriteRenderLoop
ExDrawReturn:
 ExHostRestore
 sec
 rts

ExHostWorldColors:
 ExHostFar HuNativeWorldPalette,Bank_HuNativeWorldPalette
ExHostColors:
 ExHostSave
 ldx VRAM_Buffer1_Offset
 cpx #$4d                    ; Seven-byte packet plus terminator within84B.
 bcs ExColorsReturn
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$10
 sta VRAM_Buffer1+1,x
 lda #4
 sta VRAM_Buffer1+2,x
 ldy BackgroundColorCtrl
 bne :+
 ldy AreaType
:
 lda ExBackgroundColors,y
 sta VRAM_Buffer1+3,x
 lda #$20
 sta VRAM_Buffer1+4,x
 lda #$16
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
ExColorsReturn:
 ExHostRestore
 sec
 rts

; Typed native head/side tile queries return their actual A/Y/status outputs.
; These immutable fixed-bank routines keep native coin/brick/pipe transactions.
ExHostHead:jmp BlockBufferColli_Head
ExHostSide:jmp BlockBufferColli_Side
ExHostBody:
 lda #0
 sta PlayerSize
 sta CrouchingFlag
 sta Player_BoundBoxCtrl
 clc                         ; Continue the native easy/hard body policy.
 rts
ExHostAdder:
 ldy #3                      ; Native32px Mega collision-probe group.
 sec
 rts
ExHostInjuryStatus:
 lda #1                      ; Bike contacts use source crashes, not SMB HP.
 sec
 rts
ExHostInjury:
 php
 pha
 lda ExState+$098
 bne ExInjuryReturn
 lda ExState+$09c
 beq ExInjuryCrash
 cmp #5
 bne ExInjuryReturn
ExInjuryCrash:
 lda #$ff
 sta ExState+$098            ; Same donor crash ingress used by rough landings.
ExInjuryReturn:
 pla
 plp
 sec
 rts
ExHostBounce:
 ExHostSave
 ldx #0
 jsr ExAirLaunch             ; Native stomp -> source-speed launch arithmetic.
 lda #1
 sta Player_State
 ExHostRestore
 sec
 rts
; B belongs to the source motor/turbo. This owner has no separate SMB weapon.
ExHostWeapons:
 sec
 rts
ExHostStatus:
 php
 cmp #0
 bne ExStatusNoCopy
 pha
 tya
 pha
 ldy #6
ExStatusCopy:
 lda ExStatusText,y
 sta VRAM_Buffer1+11,y
 dey
 bpl ExStatusCopy
 pla
 tay
 pla
ExStatusNoCopy:
 plp
 sec
 rts
; Deliberate seven-character native HUD abbreviation.
ExStatusText:.byte 14,33,11,18,20,14,36 ; EXBIKE
ExBackgroundColors:.incbin "host-background.bin"
ExHostEnd:
