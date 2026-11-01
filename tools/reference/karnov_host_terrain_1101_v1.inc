; Native SMB boundary for original Karnov land movement. Code executes A3/C2.
; The original actor supplies every displacement; SMB owns solid tile effects,
; support, head bumps, pipe/flag scripts and camera progression.
.import CurrentPlayer,NumberofLives,WorldNumber,AreaAddrsLOffset,FrameCounter
.import OperMode,GamePauseStatus,PlayerFacingDir,PlayerSize,CrouchingFlag
.import Player_X_Scroll,Player_XSpeedAbsolute,Player_Pos_ForScroll
.import ScreenLeft_X_Pos,ScreenLeft_PageLoc,Player_Rel_XPos,Player_Rel_YPos
.import BoundingBox_UL_Corner,BoundingBox_LR_Corner,Block_Buffer_1,Block_Buffer_2
.import AreaType,CrossoverBehaviorVersion,GuestBodyStompAllowed,GuestBodyNoStomp
.import DisableScreenFlag,Mirror_PPUMASK,NmiDisable,FamilyMainCommit
.importzp R1,R2,R3,R4,R5,R6,R7,SavedJoypadBits,GameEngineSubroutine
.importzp Player_X_Position,Player_PageLoc,Player_Y_Position,Player_Y_HighPos
.importzp Player_X_Speed,Player_Y_Speed,Player_State
.export KrConstruct,KrMovement,KrPostTerrain,KrHead,KrFeet,KrSide,KrAdder,KrBox
.export KrReady,KrHaveEpoch,KrLastEpoch,KrDeltaX,KrDeltaY,KrQueryY,KrHeadWithin
.export KrBodyPolicy,KrBoxProfile
KrReady=$c810
KrHaveEpoch=$c811
KrLastEpoch=$c812
KrPlayer=$c813
KrLives=$c814
KrWorld=$c815
KrArea=$c816
KrOldX=$c818
KrOldY=$c819
KrDeltaX=$c81a
KrDeltaY=$c81b
KrPrevious=$c81c
KrTemp=$c81d
KrQueryY=$c81e
KrQueryAxis=$c81f
KrQueryProbe=$c820
.macro KrSave
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

; Movement's source calls own R0/R1 and restore their inline-dispatch pointer.
; R2..R7 are never used here; future native callback leaves must preserve them.
; Keep the caller pair explicitly without saving unused R2..R7.
.macro KrActorSave
 php
 pha
 txa
 pha
 tya
 pha
 lda R0
 pha
 lda R1
 pha
.endmacro
.macro KrActorRestore
 pla
 sta R1
 pla
 sta R0
 pla
 tay
 pla
 tax
 pla
 plp
.endmacro
.macro KrRestore
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

; Called at cold scene setup, never opportunistically during a game frame.
KrConstruct:
 KrSave
 lda DisableScreenFlag
 jeq KrConstructNo
 lda Mirror_PPUMASK
 and #$18
 jne KrConstructNo
 lda NmiDisable
 jpl KrConstructNo
 lda FamilyMainCommit
 and #1
 jeq KrConstructNo
 lda #0
 sta KrReady
 sta R0
 lda #$c0
 sta R1
 ldy #0
 ldx #8
KrClearState:
 lda #0
 sta (R0),y
 iny
 bne KrClearState
 inc R1
 dex
 bne KrClearState
 lda #0
 sta KrHaveEpoch
 sta KrPrevious
 sta KrTerrainResult
 sta KrSoundEvent
 sta KrSceneEvent
 lda CurrentPlayer
 sta KrPlayer
 lda NumberofLives
 sta KrLives
 lda WorldNumber
 sta KrWorld
 lda AreaAddrsLOffset
 sta KrArea
 lda PlayerFacingDir
 cmp #2
 bne :+
 lda #$80
 sta KrState+$62
:
 lda #$a7
 sta KrReady                 ; context publication last
 KrRestore
 sec
 rts
KrConstructNo:
 KrRestore
 clc
 rts

KrMovement:
 KrActorSave
 lda OperMode
 cmp #1
 jne KrMoveNo
 lda GameEngineSubroutine
 cmp #8
 jne KrMoveNo
 lda GamePauseStatus
 and #1
 jne KrMoveNo
 lda KrReady
 cmp #$a7
 jne KrMoveNo
 lda CurrentPlayer
 cmp KrPlayer
 jne KrMoveNo
 lda NumberofLives
 cmp KrLives
 jne KrMoveNo
 lda KrHaveEpoch
 beq :+
 lda FrameCounter
 cmp KrLastEpoch
 jeq KrMoveYes
:
 lda FrameCounter
 sta KrLastEpoch
 lda #1
 sta KrHaveEpoch
 ; Sample the camera from the actual pre-step world coordinate, never from
 ; last frame's graphic anchor. Export the signed committed pixel step below.
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sta Player_Pos_ForScroll
 clc
 adc #8
 sta KrState+$63
 sta KrOldX
 lda Player_Y_Position
 clc
 adc #32
 sta KrState+$64
 sta KrOldY
 ; Native coordinate bank/vertical scroll and stage-control fields have no
 ; donor counterpart. No original tile ID is fabricated from a metatile.
 lda #0
 sta KrState+$89
 sta KrState+$8a
 sta KrState+$8b
 sta KrState+$8c
 sta KrState+$8d
 sta KrState+$c4
 lda Player_State
 bne :+
 lda #2                      ; native support observed on previous BG phase
 sta KrState+$8b
:
 lda SavedJoypadBits
 and #15
 tax
 lda KrReverseNibble,x
 asl
 asl
 asl
 asl
 sta KrTemp
 lda SavedJoypadBits
 lsr
 lsr
 lsr
 lsr
 tax
 lda KrReverseNibble,x
 ora KrTemp
 sta KrState+$1b
 eor KrPrevious
 and KrState+$1b
 and #3
 sta KrState+$21
 lda KrState+$1b
 sta KrPrevious
 jsr KrSourceFrame
 inc KrState+$e8             ; one source clock tick per accepted game update
 lda KrState+$63
 sec
 sbc KrOldX
 sta KrDeltaX
 sta Player_X_Scroll
 clc
 adc Player_X_Position
 sta Player_X_Position
 lda #0
 ldx KrDeltaX
 bpl :+
 lda #$ff
:adc Player_PageLoc
 sta Player_PageLoc
 lda KrState+$64
 sec
 sbc KrOldY
 sta KrDeltaY
 sta Player_Y_Speed
 clc
 adc Player_Y_Position
 sta Player_Y_Position
 lda #0
 ldx KrDeltaY
 bpl :+
 lda #$ff
:adc Player_Y_HighPos
 sta Player_Y_HighPos
 lda KrDeltaX
 asl
 asl
 asl
 asl
 sta Player_X_Speed
 bpl :+
 eor #$ff
 clc
 adc #1
:sta Player_XSpeedAbsolute
 lda #1
 ldx KrState+$62
 bpl :+
 lda #2
:sta PlayerFacingDir
 lda KrState+$62
 and #31
 tax
 lda #0
 sta PlayerSize
 sta CrouchingFlag
 cpx #6
 beq KrCrouch
 cpx #7
 bne KrNotCrouch
KrCrouch:inc CrouchingFlag
KrNotCrouch:
 lda #0
 cpx #8
 beq KrAir
 cpx #9
 beq KrAir
 cpx #23
 bcc KrWriteState
 lda #2
 bne KrWriteState
KrAir:
 lda KrState+$62
 and #$40
 bne KrFall
 lda KrDeltaY
 bne :+
 lda #$ff                    ; zero-step rising phase must not land on floor
 sta Player_Y_Speed
:lda #1
 bne KrWriteState
KrFall:lda #2
KrWriteState:
 sta Player_State
KrMoveYes:
 KrActorRestore
 sec
 rts
KrMoveNo:
 KrActorRestore
 clc
 rts

; Runs after the genuine SMB PlayerBGCollision. It reconciles the source
; state to real landing/ceiling results; it never integrates a second step.
KrPostTerrain:
 php
 pha                        ; this leaf touches only A/P, no foreground ZP
 lda KrReady
 cmp #$a7
 jne KrPostDone
 lda GameEngineSubroutine
 cmp #8
 bne KrPostDone
 lda GamePauseStatus
 and #1
 bne KrPostDone
 lda Player_State
 beq KrGrounded
 lda KrDeltaY
 bmi KrCheckCeiling
 beq KrCheckCeiling
 bpl KrCheckUnsupported
KrCheckCeiling:
 lda KrState+$62
 and #$40
 bne KrCheckUnsupported      ; zero-pixel fall phase is not a new head impact
 lda Player_Y_Speed
 bmi KrPostDone
 lda KrState+$62
 and #31
 cmp #8
 beq KrCeiling
 cmp #9
 bne KrCheckUnsupported
KrCeiling:
 lda KrState+$62
 ora #$40
 sta KrState+$62
 lda #0
 sta KrState+$66
 sta KrState+$6a
 sta KrState+$6b
 jmp KrPostDone
KrCheckUnsupported:
 lda KrState+$62
 and #31
 cmp #8
 bcs KrPostDone
 lda KrState+$62
 and #$80
 ora #23                     ; original unsupported-ledge fall selector
 sta KrState+$62
 bne KrPostDone
KrGrounded:
 lda KrState+$62
 and #31
 cmp #8
 beq KrLand
 cmp #9
 beq KrLand
 cmp #23
 beq KrLand
 cmp #24
 bne KrPostDone
KrLand:
 lda KrState+$62
 and #$80
 sta KrState+$62
 lda #0
 sta KrState+$66
 sta KrState+$6a
 sta KrState+$6b
KrPostDone:
 pla
 plp
 sec
 rts

KrAdder:
 ldy #3                      ; reuse native Mega group: feet at (2,32)/(13,32)
 sec
 rts
KrBodyPolicy:
 lda AreaType
 sta GuestBodyStompAllowed
 lda CrossoverBehaviorVersion
 sta GuestBodyNoStomp
 clc
 rts
KrBoxProfile:
 ldy #0
 rts
KrHeadWithin:
 lda CrouchingFlag
 beq KrHeadStanding
 lda Player_Y_Position
 clc
 adc #16
 cmp #32
 rts
KrHeadStanding:
 lda Player_Y_Position
 clc
 adc #8
 cmp #32
 rts
KrHead:
 lda #0
 beq KrQuery
KrFeet:
 iny
 lda #0
 beq KrQuery
KrSide:
 lda #1
KrQuery:
 sta KrQueryAxis
 sty KrQueryY
 tya
 sec
 sbc #30                     ; native Mega group starts at global offset30
 tay
 sty KrQueryProbe
 cpy #7
 bcs KrQueryInvalid
 lda KrProbeX,y
 clc
 adc Player_X_Position
 sta R5
 lda Player_PageLoc
 adc #0
 and #1
 beq :+
 lda #<Block_Buffer_2
 jmp KrQueryBase
:lda #<Block_Buffer_1
KrQueryBase:
 sta R6
 lda #>Block_Buffer_1
 sta R7
 lda R5
 lsr
 lsr
 lsr
 lsr
 clc
 adc R6
 sta R6
 ; Source C969 uses a24px standing body and16px crouching body, both ending
 ; at the source foot. Keep the native32px anchor plane and move only probes.
 lda CrouchingFlag
 beq :+
 lda KrProbeCrouchY,y
 bne KrProbeYReady
:lda KrProbeY,y
KrProbeYReady:
 clc
 adc Player_Y_Position
 cmp #32
 bcc KrQueryInvalid
 cmp #240
 bcs KrQueryInvalid
 and #$f0
 sec
 sbc #32
 sta R2
 tay
 lda (R6),y
 sta R3
 ldy KrQueryY
 lda KrQueryAxis
 bne :+
 lda Player_Y_Position
 jmp KrQueryFraction
:lda Player_X_Position
KrQueryFraction:
 and #15
 sta R4
 ldx #0
 lda R3
 rts
KrQueryInvalid:
 ldy KrQueryY
 lda #0
 sta R3
 ldx #0
 rts
KrBox:
 php
 pha
 txa
 pha                        ; this leaf touches only A/X/P
 lda Player_Rel_XPos
 sta BoundingBox_UL_Corner
 clc
 adc #15
 sta BoundingBox_LR_Corner
 lda #8
 ldx CrouchingFlag
 beq :+
 lda #16
:clc
 adc Player_Rel_YPos
 sta BoundingBox_UL_Corner+1
 lda Player_Rel_YPos
 clc
 adc #31
 sta BoundingBox_LR_Corner+1
 pla
 tax
 pla
 plp
 sec
 rts
KrReverseNibble:.byte 0,8,4,12,2,10,6,14,1,9,5,13,3,11,7,15
KrProbeX:.byte 8,2,13,1,1,14,14
KrProbeY:.byte 8,32,32,12,24,12,24
KrProbeCrouchY:.byte 16,32,32,20,28,20,28
