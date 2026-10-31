; BT's own selected RAM3 host adapter. No cold/menu admission claim.
.setcpu "6502"
.macpack longbranch
.include "native-constants.inc"
.import BtInit,BtPhysicsStep,BtSrc_Object_RamSlotID_tmp
.import BtSrc_Objects_Xpos_L,BtSrc_Objects_Xpos_H,BtSrc_Objects_Ypos_L,BtSrc_Objects_Ypos_H
.import BtSrc_Objects_X_sub,BtSrc_Objects_Z_sub,BtSrc_Objects_Zpos_L,BtSrc_Objects_Zpos_H
.import BtSrc_Objects_X_speed,BtSrc_Objects_Z_speed,BtSrc_Objects_Z_spd_sub,BtSrc_Objects_Z_floor
.import BtSrc_Objects_Flags,BtSrc_Objects_dir,BtSrc_Objects_Life,BtSrc_Objects_death_timer
.import BtSrc_player1_obj_wanted_frame,BtSrc_update_ui_flag
.import BtSrc_Obj_anims_timer,BtSrc_tmp_var_15
.import BtPoseIds,BtPosePages,BtPoseLo,BtPoseHi,BtOriginalPalettes
.import SelectedCharacter,CurrentPlayer,NumberofLives,FmGroups,OperMode,GamePauseStatus,TimerControl
.importzp GameEngineSubroutine
.importzp Player_X_Position,Player_PageLoc,Player_Y_Position,Player_Y_HighPos,Player_X_Speed,Player_Y_Speed
.import PlayerFacingDir,PlayerSize,CrouchingFlag,InjuryTimer
.importzp Player_State,SavedJoypadBits
.import Player_Rel_XPos,Player_Rel_YPos,ScreenLeft_X_Pos,ScreenLeft_PageLoc
.import CurrentBankC,SmPosePtr,ObjectMetasprite,Player_SprAttrib,GuestBodyStompAllowed,GuestBodyNoStomp,QwEmpty34
.importzp Enemy_State
.import BoundingBox_UL_Corner,BoundingBox_LR_Corner,Square2SoundQueue
.importzp PowerUpType
.import BlockBufferColli_Head,BlockBufferColli_Side,MetaspriteRenderLoop,X5SetPhysicalChr
.import EraseEnemyObject,SetupFloateyNumber,MarioSourcePowerupCollision,KillPlayer,NativePlayerDeath
.import VRAM_Buffer1,VRAM_Buffer1_Offset,FarCallCommon,FarcallJmpTarget_SMC,SafecallA_SMC
.importzp R0,R1,R2,R3,R4,R5,R6,R7
.exportzp BtScriptPtr
BtScriptPtr=R0
.export BtState,BtHostCamera,BtHostTerrain,BtHostHit,BtSoundDeath
.export BtCacheServices,BtConstruct,BtCoreStep,BtHostReady,BtHostState,BtCacheInvalid
.export BtMovement,BtImportNative,BtExportNative,BtGraphics,BtDraw,BtWeapons,BtInjury,BtInjuryStatus
.export BtFoodHeal,BtApplyDamage18,BtFullBox,BtNativeHead,BtNativeSide,BtColors,BtPickup
.macro BtFar Target,Mode
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(Target)|$80)
 .if .xmatch({Mode},{jmp})
 jmp FarCallCommon
 .else
 jsr FarCallCommon
 .endif
.endmacro
.macro BtSave
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
.macro BtRestore
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
.segment "BT_CACHE_API"
BtCacheServices:
 jmp BtMovement       ;0 single genuine donor integrator
 jmp BtGraphics       ;1 actual physical CHR publication
 jmp BtDraw           ;2 native kernel/source descriptors
 jmp BtDraw           ;3 warm actor only, ROM cold bridge still pending
 jmp BtWeapons        ;4 consume genuine E2 event once
 jmp BtInjury         ;5 source-health/native contact bridge
 jmp BtInjuryStatus   ;6
 jmp BtDeathStart     ;7
 jmp BtNativeDeath    ;8
 jmp BtUnavailable    ;9 native visible bridge still pending
 jmp BtNativeHead     ;10
 jmp BtBody           ;11
 jmp BtNativeAdder    ;12
 jmp BtNativeBox      ;13
 jmp BtNativeSide     ;14
 jmp BtConstruct      ;15 ROM Fresh chain still pending
 jmp BtFullBox        ;16 native contact rectangle
 jmp BtDraw           ;17 warm only, cold ROM preview pending
 jmp BtUnavailable    ;18 ROM name bridge pending
 jmp BtUnavailable    ;19 ROM scene bridge pending
 jmp BtUnavailable    ;20 inventory preparation intentionally excluded
 jmp BtUnavailable    ;21
 jmp BtUnavailable    ;22
 jmp BtUnavailable    ;23
 jmp BtPickup         ;24 native food/star/1up bridge
 jmp BtFullPower      ;25 existing cheat endpoint
 jmp BtColors         ;26 exact two source role rows, retirement pending
 jmp BtUnavailable    ;27 native bounce imported next Movement
 jmp BtHeadWithin     ;28
 jmp BtUnavailable    ;29 HUD not yet implemented
 jmp BtUnavailable    ;30 status-name bridge pending
 jmp BtUnavailable    ;31
 jmp BtUnavailable    ;32 ROM world-palette bridge pending
 jmp BtUnavailable    ;33
 jmp BtWeapons        ;34 consumes flag, never ticks source twice
 jmp BtUnavailable    ;35 native vine draw bridge pending
.segment "BT_CACHE_HOST"
BtConstruct:
 jsr BtInit
 lda #0
 ldx #63
ClearHost:sta BtHostState,x
 dex
 bpl ClearHost
 lda FmGroups
 and #$20
 sta BtVariant
 lda CurrentPlayer
 and #1
 tax
 sta BtPlayer
 lda NumberofLives
 sta BtLife,x
 jsr BtGroundAtNative
 lda #1
 sta BtHostReady
 rts
BtActive:
 lda BtHostReady
 cmp #1
 bne No
 lda SelectedCharacter
 cmp #33
 bne No
 lda OperMode
 cmp #1
 bne No
 lda GameEngineSubroutine
 cmp #8
 bne No
 lda GamePauseStatus
 and #1
 ora TimerControl
 bne No
 sec
 rts
No:clc
 rts
BtMovement:
 BtSave
 jsr BtActive
 bcc MovementDone
 lda CurrentPlayer
 and #1
 tax
 stx BtPlayer
 lda NumberofLives
 cmp BtLife,x
 beq SameLife
 sta BtLife,x
 lda #$2f
 sta BtSrc_Objects_Life,x
 lda #0
 sta BtSrc_Objects_death_timer,x
SameLife:
 jsr BtImportNative
 lda SavedJoypadBits
 jsr BtCoreStep
 jsr BtExportNative
MovementDone:
 BtRestore
 rts
BtCoreStep:
 stx BtSrc_Object_RamSlotID_tmp
 jmp BtPhysicsStep
; Source actor coordinates are centerX/ground-planeY, with Z positive up.
; Native SMB's viewport high byte1 is removed at import, restored at export.
; Native clipping from the preceding real BG pass is imported BEFORE the
; next donor tick, retaining source fractional motion on unclipped axes.
BtImportNative:
 lda Player_X_Position
 clc
 adc #8
 sta BtSrc_Objects_Xpos_L,x
 lda Player_PageLoc
 adc #0
 sta BtSrc_Objects_Xpos_H,x
 lda Player_X_Speed
 bne KeepX
 lda BtLastXSpeed
 beq KeepX
 lda #0
 sta BtSrc_Objects_X_speed,x
 sta BtSrc_Objects_X_sub,x
KeepX:
 lda Player_State
 beq BtGroundAtNative
 lda Player_Y_Speed
 cmp BtLastYSpeed
 beq KeepZ
 eor #$ff
 clc
 adc #1
 sta BtSrc_Objects_Z_speed,x
 lda #0
 sta BtSrc_Objects_Z_spd_sub,x
KeepZ:
 lda Player_Y_Position
 clc
 adc #32
 sta BtTmp
 lda Player_Y_HighPos
 adc #$ff
 sta BtTmp+1
 lda BtTmp
 clc
 adc BtSrc_Objects_Zpos_L,x
 sta BtSrc_Objects_Ypos_L,x
 lda BtTmp+1
 adc BtSrc_Objects_Zpos_H,x
 sta BtSrc_Objects_Ypos_H,x
 lda #1
 sta BtSrc_Objects_Z_floor,x
 rts
BtGroundAtNative:
 lda Player_X_Position
 clc
 adc #8
 sta BtSrc_Objects_Xpos_L,x
 lda Player_PageLoc
 adc #0
 sta BtSrc_Objects_Xpos_H,x
 lda Player_Y_Position
 clc
 adc #32
 sta BtSrc_Objects_Ypos_L,x
 lda Player_Y_HighPos
 adc #$ff
 sta BtSrc_Objects_Ypos_H,x
 lda #0
 sta BtSrc_Objects_Zpos_L,x
 sta BtSrc_Objects_Zpos_H,x
 sta BtSrc_Objects_Z_sub,x
 sta BtSrc_Objects_Z_speed,x
 sta BtSrc_Objects_Z_spd_sub,x
 sta BtSrc_Objects_Z_floor,x
 rts
BtHostTerrain:
 ; A falling sideview actor may pass below its last ground plane. Rebase
 ; plane/Z together without moving the visible body or changing velocity.
 ; Native SMB terrain/hole progression remains the sole collision owner.
 lda BtSrc_Objects_Zpos_H,x
 bpl NoRebase
 lda BtSrc_Objects_Ypos_L,x
 sec
 sbc BtSrc_Objects_Zpos_L,x
 sta BtSrc_Objects_Ypos_L,x
 lda BtSrc_Objects_Ypos_H,x
 sbc BtSrc_Objects_Zpos_H,x
 sta BtSrc_Objects_Ypos_H,x
 lda #0
 sta BtSrc_Objects_Zpos_L,x
 sta BtSrc_Objects_Zpos_H,x
 lda #1
 sta BtSrc_Objects_Z_floor,x
NoRebase:
 lda BtSrc_Objects_Zpos_L,x
 ora BtSrc_Objects_Zpos_H,x
 beq TerrainDone
 lda #1
 sta BtSrc_Objects_Z_floor,x
TerrainDone:rts
BtExportNative:
 lda BtSrc_Objects_Xpos_L,x
 sec
 sbc #8
 sta Player_X_Position
 lda BtSrc_Objects_Xpos_H,x
 sbc #0
 sta Player_PageLoc
 lda BtSrc_Objects_Ypos_L,x
 sec
 sbc BtSrc_Objects_Zpos_L,x
 sta BtTmp
 lda BtSrc_Objects_Ypos_H,x
 sbc BtSrc_Objects_Zpos_H,x
 sta BtTmp+1
 lda BtTmp
 sec
 sbc #32
 sta Player_Y_Position
 lda BtTmp+1
 sbc #$ff
 sta Player_Y_HighPos
 lda BtSrc_Objects_X_speed,x
 lsr
 sta BtTmp
 lda BtSrc_Objects_dir,x
 bpl RightSpeed
 lda BtTmp
 eor #$ff
 clc
 adc #1
 sta BtTmp
RightSpeed:lda BtTmp
 sta Player_X_Speed
 sta BtLastXSpeed
 lda BtSrc_Objects_Z_speed,x
 eor #$ff
 clc
 adc #1
 sta Player_Y_Speed
 sta BtLastYSpeed
 lda BtSrc_Objects_Flags,x
 and #$40
 beq FaceRight
 lda #2
 bne FaceSet
FaceRight:lda #1
FaceSet:sta PlayerFacingDir
 lda #0
 sta PlayerSize
 sta CrouchingFlag
 lda BtSrc_Objects_Z_floor,x
 beq StateSet
 lda #2
StateSet:sta Player_State
 rts
BtGraphics:
 BtSave
 lda CurrentPlayer
 and #1
 tax
 lda BtSrc_player1_obj_wanted_frame,x
 ldy #11
FindPose:cmp BtPoseIds,y
 beq PoseFound
 dey
 bpl FindPose
 ldy #0
PoseFound:sty BtPoseIndex
 lda BtPoseLo,y
 sta R0
 lda BtPoseHi,y
 sta R1
 ldy #0
 lda (R0),y
 sta BtRenderBuffer
 tay
CopyRender:
 lda (R0),y
 sta BtRenderBuffer,y
 dey
 bne CopyRender
 ldx BtPlayer
 lda BtSrc_Objects_Flags,x
 and #$40
 beq RenderCopied
 ldy #4
FlipRender:
 lda BtRenderBuffer-2,y
 eor #$40
 sta BtRenderBuffer-2,y
 lda BtRenderBuffer,y
 eor #$ff
 sec
 sbc #6
 sta BtRenderBuffer,y
 iny
 iny
 iny
 iny
 tya
 cmp BtRenderBuffer
 bcc FlipRender
 beq FlipRender
RenderCopied:
 ldy BtPoseIndex
 lda BtPosePages,y
 clc
 adc #<915
 ldx #>915
 ldy #0
 BtFar X5SetPhysicalChr,jsr
 lda #0
 sta ObjectMetasprite
 lda #<QwEmpty34
 sta SmPosePtr
 lda #>QwEmpty34
 sta SmPosePtr+1
 BtRestore
 rts
BtDraw:
 BtSave
 lda CurrentBankC
 pha
 lda #3
 sta CurrentBankC
 sta $5116
 lda #<(BtRenderBuffer+$2000)
 sta R0
 lda #>(BtRenderBuffer+$2000)
 sta R1
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
 clc
 adc #20
 sta R6
 lda Player_Y_HighPos
 adc #0
 sta R7
 lda Player_SprAttrib
 and #$20
 sta R3
 BtFar MetaspriteRenderLoop,jsr
 pla
 sta CurrentBankC
 sta $5116
 BtRestore
 rts
BtEmpty:.byte 0
BtHostCamera:rts
BtHostHit:
 inc BtPunchEvents
 lda #1
 sta BtPunchPending
 rts
BtSoundDeath:rts
BtWeapons:
 ; Source E2 is retained as a single event. Native target/defeat join comes
 ; next; never invent a repeated generic attack-active frame window.
 lda BtPunchPending
 beq WeaponsDone
 lda #0
 sta BtPunchPending
 inc BtPendingHitsConsumed
WeaponsDone:rts
BtNativeHead:BtFar BlockBufferColli_Head,jmp
BtNativeSide:BtFar BlockBufferColli_Side,jmp
; Real HotCollisionAdder caller consumes a profile index in Y, not tabledata.
BtNativeAdder:ldy #0
 sec
 rts
BtNativeBox:ldy #0
 rts
BtFullBox:
 lda Player_Rel_XPos
 clc
 adc #2
 sta BoundingBox_UL_Corner
 lda Player_Rel_XPos
 clc
 adc #14
 sta BoundingBox_LR_Corner
 lda Player_Rel_YPos
 clc
 adc #8
 sta BoundingBox_UL_Corner+1
 lda Player_Rel_YPos
 clc
 adc #32
 sta BoundingBox_LR_Corner+1
 ldx #0
 ldy #0
 rts
BtBody:
 lda #1
 sta GuestBodyStompAllowed
 lda #0
 sta GuestBodyNoStomp
 clc
 rts
BtHeadWithin:
 lda Player_Y_Position
 cmp #32
 rts
BtNativeDeath:BtFar NativePlayerDeath,jmp
BtDeathStart:BtFar KillPlayer,jmp
BtInjuryStatus:
 ldx CurrentPlayer
 lda BtSrc_Objects_Life,x
 ldx #1
 rts
BtInjury:
 BtSave
 lda InjuryTimer
 bne InjuryDone
 ldx CurrentPlayer
 jsr BtApplyDamage18
 lda BtSrc_Objects_death_timer,x
 bmi InjuryFatal
 lda #$1c
 sta InjuryTimer
 lda #Sfx_PipeDown_Injury
 sta Square2SoundQueue
 jmp InjuryDone
InjuryFatal:BtFar KillPlayer,jsr
InjuryDone:BtRestore
 sec
 rts
; Exact source gen_damage_effects E056 health portion, ordinary player-target
; punch profile18 (damage4, anim1C). ZeroHP alone is not the underflow death.
BtApplyDamage18:
 lda #0
 sta BtSrc_Objects_Z_speed,x
 sta BtSrc_Objects_Z_spd_sub,x
 lda BtSrc_Objects_Life,x
 sec
 sbc #4
 sta BtSrc_tmp_var_15
 bcc DamageUnderflow
 eor BtSrc_Objects_Life,x
 and #$f0
 beq DamageUI
 lda BtSrc_tmp_var_15
 ora #$0f
 sta BtSrc_tmp_var_15
 bne DamageUI
DamageUnderflow:
 lda #$c0
 sta BtSrc_Objects_death_timer,x
 lda #0
 sta BtSrc_tmp_var_15
 beq DamageZero
DamageUI:
 lda BtSrc_tmp_var_15
 eor BtSrc_Objects_Life,x
 and #$38
 beq DamageWrite
DamageZero:inc BtSrc_update_ui_flag
DamageWrite:
 lda BtSrc_tmp_var_15
 sta BtSrc_Objects_Life,x
 lda BtSrc_Objects_death_timer,x
 beq DamageAlive
 lda #3
 sta BtSrc_Objects_Z_speed,x
 lda #$d4
 bne DamageTimer
DamageAlive:lda #$1c
DamageTimer:sta BtSrc_Obj_anims_timer,x
 rts
BtFoodHeal:
 lda BtSrc_Objects_Life,x
 clc
 adc #8
 cmp #$2f
 bcc HealSet
 lda #$2f
HealSet:sta BtSrc_Objects_Life,x
 inc BtSrc_update_ui_flag
 rts
BtFullPower:
 ldx CurrentPlayer
 lda #$2f
 sta BtSrc_Objects_Life,x
 rts
BtPickup:
 lda PowerUpType,x
 cmp #2
 bcc Food
 BtFar MarioSourcePowerupCollision,jmp
Food:
 lda Enemy_State,x
 bpl FoodDone
 txa
 pha
 ldx CurrentPlayer
 jsr BtFoodHeal
 pla
 tax
 BtFar EraseEnemyObject,jsr
 lda #6
 BtFar SetupFloateyNumber,jsr
 lda #Sfx_PowerUpGrab
 sta Square2SoundQueue
FoodDone:rts
BtColors:
 ; Only completed own body roles are queued. Universal background entries
 ; 3F10/14 are not written. Menu P1 retirement is still an explicit blocker.
 BtSave
 lda FmGroups
 and #$20
 ldy #0
 beq PaletteVariant
 ldy #4
PaletteVariant:sty BtTmp
 ldx VRAM_Buffer1_Offset
 cpx #72
 bcs PaletteDone
 lda #$3f
 sta VRAM_Buffer1,x
 sta VRAM_Buffer1+6,x
 lda #$11
 sta VRAM_Buffer1+1,x
 lda #$15
 sta VRAM_Buffer1+7,x
 lda #3
 sta VRAM_Buffer1+2,x
 sta VRAM_Buffer1+8,x
 ldy #0
ColorCopy:
 tya
 clc
 adc BtTmp
 tay
 lda BtOriginalPalettes+1,y
 sta VRAM_Buffer1+3,x
 ldy BtColorLoop
 lda BtOriginalPalettes+9,y
 sta VRAM_Buffer1+9,x
 inx
 ldy BtColorLoop
 iny
 sty BtColorLoop
 cpy #3
 bcc ColorCopy
 lda #0
 sta BtColorLoop
 txa
 clc
 adc #9
 tax
 sta VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
PaletteDone:
 BtRestore
 rts
BtUnavailable:clc
 rts
.segment "BT_CACHE_STATE"
BtState:.res 117,0
.segment "BT_CACHE_HOST_STATE"
BtHostState:
BtHostReady:.res 1,0
BtVariant:.res 1,0
BtPlayer:.res 1,0
BtLife:.res 2,0
BtLastXSpeed:.res 1,0
BtLastYSpeed:.res 1,0
BtTmp:.res 2,0
BtPoseIndex:.res 1,0
BtPunchPending:.res 1,0
BtPunchEvents:.res 1,0
BtPendingHitsConsumed:.res 1,0
BtColorLoop:.res 1,0
BtRenderBuffer:.res 49,0
.res 64-(*-BtHostState),0
.segment "BT_CACHE_INVALID_COOKIE"
BtCacheInvalid:.res 16,0
