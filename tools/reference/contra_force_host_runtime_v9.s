; PRIVATE unresolved host worker object. No fixed PRG/RAM/CHR or admission.
; Entry requires raw31 AND full verified CF payload cookie with C2 mapped.
; Hardware native/typed importer, loader and renderer are NOT installed here.
.setcpu "6502"
.macpack longbranch
.import CfState,CfNativeClear,CfHostCallInput,CfHostCallBody
.importzp CfPointers
.import SelectedCharacter,FmGroups,TimerControl,GameEngineSubroutine,CurrentPlayer,NumberofLives
.import OperMode,FamilyMainCommit,Mirror_PPUMASK,DisableScreenFlag,NmiDisable,GamePauseStatus
.import FarCallCommon,SafecallA_SMC,FarcallJmpTarget_SMC,JnResetDispatch,CfNativeResetBank
.import Player_X_Position,Player_PageLoc,Player_Y_Position,Player_Y_HighPos
.import Player_X_Speed,Player_Y_Speed,Player_XSpeedAbsolute,Player_X_Scroll
.import Player_State,PlayerStatus,PlayerSize,PlayerFacingDir,CrouchingFlag
.import ScreenLeft_X_Pos,ScreenLeft_PageLoc,Player_Pos_ForScroll,SavedJoypadBits
.import BlockBufferAddr,Block_Buffer_1
.import BoundingBox_UL_Corner,BoundingBox_LR_Corner
.import GuestBodyStompAllowed,GuestBodyNoStomp
.import KillPlayer,InjuryTimer,StarInvincibleTimer
.importzp R2,R3,R4,R5,R6,R7
.export CfHostConstruct,CfHostSceneEnsure,CfHostEnsure,CfHostAreaReset,CfHostLastLife,CfHostMovement,CfHostAfterBG,CfHostFresh
.export CfHostHeadWithin,CfHostHead,CfHostFeet,CfHostSide,CfHostAdder,CfHostBoxProfile,CfHostBox,CfHostBody
.export CfHostFullPower,CfHostInjury,CfHostReset,CfHostImport,CfHostExport
.export CfHostRuntimeStart,CfHostRuntimeEnd
; Whole original pages00/02/03/06/07 compact to00/01/02/03/04.
CFX=CfState+$034e
CFY=CfState+$0368
CFXF=CfState+$03c8
CFYF=CfState+$03de
CFActor=CfState+$0382
CFType=CfState+$0482
CFInput=CfState+$04aa
CFJumpAge=CfState+$04b4
CFHurt=CfState+$04c8
CFContact=CfState+$04d2
CFDXL=CfState+$04e6
CFDXH=CfState+$04e8
CFDYL=CfState+$04ea
CFDYH=CfState+$04ec
CFVariant=CfState+$02e0
CFReady=CfState+$02e1
CFPaletteDirty=CfState+$02e2
CFPrevX=CfState+$02e3
CFPrevY=CfState+$02e4
CFLastVY=CfState+$02e5
CFNativeX=CfState+$02e6
CFNativePage=CfState+$02e7
CFNativeY=CfState+$02e8
CFDTemp=CfState+$02e9
CFProbeIndex=CfState+$02ea
CFProbeMode=CfState+$02eb
.segment "CF_HOST_LIFECYCLE_STATE"
CfHostLastLife:.res 1
.segment "CF_HOST_RUNTIME"
CfHostRuntimeStart:
; Outer cookie guard must run before this worker, including constructor.
CfHostConstruct:
 lda #0
 tax
:
 sta CfState,x
 sta CfState+$100,x
 sta CfState+$200,x
 sta CfState+$300,x
 sta CfState+$400,x
 inx
 bne :-
 lda FmGroups
 lsr
 lsr
 lsr
 and #3
 sta CFVariant
 sta CfState+$00b1
 tax
 lda PlayerStatus
 cmp #3
 bcc :+
 lda #2
:
 ora #$10
 sta CfState+$007f,x
 lda #$2e
 sta CFType
 lda #$0a
 sta CFActor
 lda #2
 sta CfState+$0036
 lda #1
 sta CFPaletteDirty
 sta CFContact
 lda CurrentPlayer
 and #1
 clc
 adc #1
 sta CFReady
 lda NumberofLives
 sta CfHostLastLife
 jsr CfHostImport
 sec
 rts

CfHostFresh:
 lda #0
 sta CFReady
 rts
; Scene Ensure never repeats native CmFresh. Native status is the complete
; persistent gear/one-native-life authority for this declared WIP. A player
; switch or a DECREASED life count reconstructs from the genuine swapped/reset
; native status; a1up INCREASE updates only the marker and retains source HP.
; Public15 is ONLY the genuine source scene constructor/ensure boundary.
; General active movement uses CfHostEnsure below, never this cold-context gate.
CfHostSceneEnsure:
 php
 pha
 txa
 pha
 tya
 pha
 lda SelectedCharacter
 cmp #31
 bne CfSceneNo
 lda OperMode
 cmp #1
 bne CfSceneNo
 lda FamilyMainCommit
 and #1
 beq CfSceneNo
 lda Mirror_PPUMASK
 and #$18
 bne CfSceneNo
 lda DisableScreenFlag
 beq CfSceneNo
 lda NmiDisable
 bpl CfSceneNo
 lda GamePauseStatus
 and #1
 bne CfSceneNo
 jsr CfHostEnsure
 tsx
 lda $0104,x
 ora #1
 bne CfSceneFlags
CfSceneNo:
 tsx
 lda $0104,x
 and #$fe
CfSceneFlags:
 sta $0104,x
 pla
 tay
 pla
 tax
 pla
 plp
 rts

CfHostEnsure:
 lda CurrentPlayer
 and #1
 clc
 adc #1
 cmp CFReady
 bne CfEnsureConstruct
 lda NumberofLives
 cmp CfHostLastLife
 bcc CfEnsureConstruct
 sta CfHostLastLife
 sec
 rts
CfEnsureConstruct:jmp CfHostConstruct

; Actual typed19 callback invokes native JnReset ONCE, never RosterClearState
; (which would recurse through NrReset). The original native result AXYP is
; restored after own motion/scene state cleanup.
CfHostReset:
 sta SafecallA_SMC+1
 lda #<JnResetDispatch
 sta FarcallJmpTarget_SMC+1
 lda #>JnResetDispatch
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(CfNativeResetBank)
 jsr FarCallCommon
 php
 pha
 txa
 pha
 tya
 pha
 jsr CfHostEnsure
 jsr CfHostAreaReset
 pla
 tay
 pla
 tax
 pla
 plp
 rts

; Preserve all original per-class gear/HP bytes7F..82 and selected class.
; Clear original current actor/projectile motion/action pages only. Same-player
; pipes/scene transitions do not rerun constructor and do not erase earned gear.
CfHostAreaReset:
 lda #0
 tax
:
 sta CfState+$300,x
 sta CfState+$400,x
 inx
 bne :-
 sta CfState+$0040
 sta CfState+$0042
 sta CFLastVY
 sta CFNativeX
 sta CFNativePage
 sta CFNativeY
 sta CfState+$02ff
 lda #$2e
 sta CFType
 lda #$0a
 sta CFActor
 lda #1
 sta CFContact
 sta CFPaletteDirty
 lda CfState+$0023
 sec
 sbc #1
 sta CfState+$02de
 jsr CfHostImport
 sec
 rts

CfHostImport:
 lda Player_X_Position
 cmp CFNativeX
 bne CfResetXFraction
 lda Player_PageLoc
 cmp CFNativePage
 beq :+
CfResetXFraction:
 lda #0
 sta CFXF
:
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 clc
 adc #8
 sta CFX
 sta CFPrevX
 lda Player_Y_Position
 cmp CFNativeY
 beq :+
 lda #0
 sta CFYF
:
 lda Player_Y_Position
 clc
 adc #16
 sta CFY
 sta CFPrevY
 rts

CfHostMovement:
 jsr CfHostEnsure
 jsr CfHostImport
 inc CfState+$0023
 lda SavedJoypadBits
 and #$cf                    ; Pause/Select stay native owned.
 pha
 eor #$ff
 ora CfState+$0042
 eor #$ff
 sta CfState+$0040          ; pad & ~previous, original source edge byte.
 pla
 sta CfState+$0042
 ldx #0
 jsr CfNativeClear
 ldx #0
 jsr CfHostCallInput
 ldx #0
 jsr CfHostCallBody
 lda CFHurt
 bmi CfHostFell
 jmp CfHostExport
CfHostFell:jmp KillPlayer

CfHostExport:
 lda CFXF
 clc
 adc CFDXL
 sta CFXF
 lda CFX
 adc CFDXH
 sta CFX
 sec
 sbc CFPrevX
 sta Player_X_Scroll
 clc
 adc Player_X_Position
 sta Player_X_Position
 sta CFNativeX
 lda #0
 ldx Player_X_Scroll
 bpl :+
 lda #$ff
:
 adc Player_PageLoc
 sta Player_PageLoc
 sta CFNativePage
 lda CFYF
 clc
 adc CFDYL
 sta CFYF
 lda CFY
 adc CFDYH
 sta CFY
 sec
 sbc CFPrevY
 sta CFDTemp
 clc
 adc Player_Y_Position
 sta Player_Y_Position
 sta CFNativeY
 lda #0
 ldx CFDTemp
 bpl :+
 lda #$ff
:
 adc Player_Y_HighPos
 sta Player_Y_HighPos
 lda CFDXL
 lsr
 lsr
 lsr
 lsr
 sta CFDTemp
 lda CFDXH
 asl
 asl
 asl
 asl
 ora CFDTemp
 sta Player_X_Speed
 bpl :+
 eor #$ff
 clc
 adc #1
:
 sta Player_XSpeedAbsolute
 lda CFDYH
 sta Player_Y_Speed
 sta CFLastVY
 lda #0
 ldx CFInput
 txa
 and #$40
 beq CfGroundState
 lda #1
 ldx CFDYH
 bmi CfGroundState
 lda #2
CfGroundState:
 sta Player_State
 lda #1
 ldx CFInput
 txa
 and #$10
 beq :+
 lda #2
 bne CfFacing
:
 lda #1
CfFacing:sta PlayerFacingDir
 lda #0
 sta PlayerSize
 sta CrouchingFlag
 lda CFInput
 and #$4f
 cmp #5
 bne :+
 inc CrouchingFlag
:
 rts

CfHostAfterBG:
 jsr CfHostImport
 lda Player_State
 bne CfAir
 lda CFInput
 and #$bf
 sta CFInput
 lda #0
 sta CFJumpAge
 sta CFYF
 lda #1
 sta CFContact
 rts
CfAir:
 lda #0
 sta CFContact
 lda CFInput
 and #$40
 bne :+
 lda CFInput
 ora #$40
 sta CFInput
 lda #$80
 sta CFJumpAge
:
 lda CFLastVY
 bpl CfAfterX
 lda Player_Y_Speed
 bmi CfAfterX
 lda #$80                   ; Accepted native ceiling stops source ascent.
 sta CFJumpAge
 lda #0
 sta CFYF
CfAfterX:
 lda Player_X_Speed
 bne :+
 lda #0
 sta CFXF
 sta CFDXL
 sta CFDXH
:
 rts

CfHostBody:
 lda #0
 sta GuestBodyStompAllowed
 lda #1
 sta GuestBodyNoStomp
 clc
 rts
CfHostAdder:ldy #0
 sec
 rts
CfHostBoxProfile:ldy #12
 rts
CfHostBox:
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 clc
 adc #1
 sta BoundingBox_UL_Corner
 clc
 adc #14
 sta BoundingBox_LR_Corner
 lda #1
 ldx CrouchingFlag
 beq :+
 lda #17
:
 clc
 adc Player_Y_Position
 sta BoundingBox_UL_Corner+1
 lda Player_Y_Position
 clc
 adc #32
 sta BoundingBox_LR_Corner+1
 rts

; Native typed query tuple follows the genuine admitted QhProbe ABI.
CfHostHeadWithin:
 lda CrouchingFlag
 beq :+
 lda Player_Y_Position
 clc
 adc #17
 cmp #32
 rts
:
 lda Player_Y_Position
 clc
 adc #1
 cmp #32
 rts
CfHostHead:ldy #0
 lda #0
 jmp CfProbe
CfHostFeet:iny
 lda #0
 jmp CfProbe
CfHostSide:lda #1
CfProbe:
 sta CFProbeMode
 sty CFProbeIndex
 lda Player_X_Position
 clc
 adc CfXAdd,y
 sta R5
 lda Player_PageLoc
 adc #0
 and #1
 tay
 lda #>Block_Buffer_1
 sta R7
 lda R5
 lsr
 lsr
 lsr
 lsr
 clc
 adc BlockBufferAddr,y
 sta R6
 ldy CFProbeIndex
 lda CfYAdd,y
 cpy #0
 bne :+
 ldx CrouchingFlag
 beq :+
 lda #17
:
 clc
 adc Player_Y_Position
 and #$f0
 sec
 sbc #32
 sta R2
 tay
 lda (R6),y
 sta R3
 ldy CFProbeIndex
 lda CFProbeMode
 bne CfHorizontalFraction
 lda Player_Y_Position
 jmp CfQueryFraction
CfHorizontalFraction:
 lda Player_X_Position
CfQueryFraction:
 and #15
 sta R4
 ldx #0
 lda R3
 sec
 rts
CfXAdd:.byte 8,1,15,1,1,15,15
CfYAdd:.byte 1,32,32,8,31,8,31

CfHostFullPower:
 lda PlayerStatus
 cmp #2
 bcs :+
 inc PlayerStatus
:
 ldx CFVariant
 lda PlayerStatus
 ora #$10
 sta CfState+$007f,x
 lda #1
 sta CFPaletteDirty
 rts
CfHostInjury:
 lda InjuryTimer
 ora StarInvincibleTimer
 bne :+
 jmp KillPlayer
:
 rts
CfHostRuntimeEnd:

