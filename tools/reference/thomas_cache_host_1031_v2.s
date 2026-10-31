; Cache entry is called only by authenticated stable ROM ThDispatch.
.setcpu "6502"
.macpack longbranch
.import ThomasHostCold,ThomasHostFrame,ThomasHostAfterTerrain,ThomasHostBody
.import ThomasHostWeapons,ThomasHostDamage,ThomasHostPickup,ThomasHostRenderAnchor
.import ThomasHostFeet,ThomasHostHead,ThomasHostSide
.import ThomasState,ThReady,ThBusy,ThOwnerPlayer,ThHaveEpoch,ThPoseCommand,ThHostGround,ThHostArtOrigin
.import CurrentPlayer,NumberofLives,WorldNumber,AreaAddrsLOffset,FrameCounter,GamePauseStatus
.import OperMode,PlayerFacingDir,CrouchingFlag,PlayerSize,CurrentBankC,Player_SprAttrib
.import ObjectMetasprite,SmPosePtr,ScreenLeft_X_Pos,ScreenLeft_PageLoc
.import MetaspriteRenderLoop,X5SetPhysicalChr,KillPlayer,NativePlayerDeath
.import SafecallA_SMC,FarcallJmpTarget_SMC,FarCallCommon
.import ThBodyPage,ThDescriptorLo,ThDescriptorHi,ThPoseWindows,ThColors
.import VRAM_Buffer1,VRAM_Buffer1_Offset
.importzp SavedJoypadBits,GameEngineSubroutine,Player_X_Position,Player_PageLoc,Player_Y_Position,Player_Y_HighPos,Player_State
.importzp R0,R1,R2,R3,R4,R5,R6,R7
.export ThCacheServices,ThEnsure,ThMovement,ThGraphics,ThDraw,ThCacheEnd
.export ThContextPlayer,ThContextLives,ThContextWorld,ThContextArea,ThContextScene,ThContextValid
.export ThPoseIndex,ThDescriptor,ThEmpty
ThContextPlayer=$c840
ThContextLives=$c841
ThContextWorld=$c842
ThContextArea=$c843
ThContextScene=$c844
ThContextValid=$c845
ThPoseIndex=$c846
ThWindow=$c847
ThDescriptor=$c848
ThEmpty=$c84a
.macro Save
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
.macro Restore
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
.macro Far Target,Mode
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
.segment "THOMAS_KERNEL"
ThCacheServices:
 jmp ThMovement
 jmp ThGraphics
 jmp ThDraw
 jmp ThReject                  ;3 genuine ROM-only prepare
 jmp ThomasHostWeapons
 jmp ThInjury
 jmp ThHealth
 jmp ThDeathStart
 jmp ThDeath
 jmp ThVisible
 jmp ThomasHostHead
 jmp ThBody
 jmp ThAdder
 jmp ThBoxProfile
 jmp ThomasHostSide
 jmp ThReject                  ;15 genuine ROM Fresh chain
 jmp ThomasHostBody
 jmp ThReject                  ;17 genuine ROM cold portrait
 jmp ThReject                  ;18 genuine ROM menu name
 jmp ThReject                  ;19 genuine ROM scene chain
 jmp ThReject                  ;20..23 no generic inventory mutation
 jmp ThReject
 jmp ThReject
 jmp ThReject
 jmp ThomasHostPickup
 jmp ThReject                  ;25 no invented source full-power
 jmp ThReject                  ;26 genuine ROM palette/forcedblank load
 jmp ThReject                  ;27 native bounce reconciliation hook later
 jmp ThHeadWithin
 jmp ThReject                  ;29 HUD pending
 jmp ThStatusName              ;30 genuine native name/late lives palette
 jmp ThReject                  ;31 native stomp policy later
 jmp ThReject                  ;32 genuine native world palette fallback proposal
 jmp ThReject                  ;33 generic powerup completion later
 jmp ThomasHostWeapons
 jmp ThReject                  ;35 native vine body fallback proposal
ThReject:clc
 rts
.assert *-ThCacheServices=110,error,"36genuine3bytecachevectors plusreject"
ThEnsure:
 lda ThBusy
 bne EnsureNo
 lda ThReady
 cmp #$a7
 bne Construct
 lda ThContextValid
 cmp #$a7
 bne Construct
 lda CurrentPlayer
 cmp ThContextPlayer
 bne Construct
 lda NumberofLives
 cmp ThContextLives
 bne Construct
 lda ThContextScene
 cmp #$a7
 bne Rebase
 lda WorldNumber
 cmp ThContextWorld
 bne Rebase
 lda AreaAddrsLOffset
 cmp ThContextArea
 bne Rebase
 sec
 rts
Construct:
 lda #0
 ldx CurrentPlayer
 ldy FrameCounter
 jsr ThomasHostCold
 lda ThReady
 cmp #$a7
 bne EnsureNo
 jmp PublishContext
Rebase:
 jsr ThomasHostAfterTerrain
 lda #0
 sta ThHaveEpoch
PublishContext:
 lda CurrentPlayer
 sta ThContextPlayer
 lda NumberofLives
 sta ThContextLives
 lda WorldNumber
 sta ThContextWorld
 lda AreaAddrsLOffset
 sta ThContextArea
 lda #$a7
 sta ThContextValid
 sta ThContextScene             ; source context publication LAST
 sec
 rts
EnsureNo:clc
 rts
ThMovement:
 Save
 lda OperMode
 cmp #1
 bne MoveDone
 lda GameEngineSubroutine
 cmp #8
 bne MoveDone
 lda GamePauseStatus
 and #1
 bne MoveDone
 jsr ThEnsure
 bcc MoveDone
 lda SavedJoypadBits
 ldx #1
 ldy FrameCounter
 jsr ThomasHostFrame
 lda ThomasState+$69
 and #4
 beq GroundState
 lda #1
 bne WriteState
GroundState:lda #2
WriteState:sta Player_State
 lda ThomasState+$69
 and #2
 sta CrouchingFlag
 lda #0
 sta PlayerSize
MoveDone:
 Restore
 rts
ThGraphics:
 Save
 jsr ThEnsure
 jcc GraphicsDone
 lda ThPoseCommand
 sec
 sbc #$25
 cmp #42
 bcc PoseLegal
 lda #0
PoseLegal:sta ThPoseIndex
 tax
 lda ThDescriptorLo,x
 sta ThDescriptor
 lda ThDescriptorHi,x
 sta ThDescriptor+1
 lda #0
 sta ThWindow
PublishWindow:
 lda ThPoseIndex
 asl
 asl
 clc
 adc ThWindow
 tax
 lda ThPoseWindows,x
 clc
 adc #<ThBodyPage
 ldx #>ThBodyPage
 ldy ThWindow
 Far X5SetPhysicalChr,jsr
 inc ThWindow
 lda ThWindow
 cmp #4
 bne PublishWindow
 lda #0
 sta ThEmpty
 sta ObjectMetasprite
 lda #<ThEmpty
 sta SmPosePtr
 lda #>ThEmpty
 sta SmPosePtr+1
GraphicsDone:
 Restore
 rts
ThDraw:
 Save
 jsr ThEnsure
 bcc DrawDone
 jsr ThGraphics
 jsr ThomasHostRenderAnchor
 lda ThDescriptor
 sta R0
 lda ThDescriptor+1
 sta R1
 lda Player_X_Position
 sec
 sbc #16
 sta R4
 lda Player_PageLoc
 sbc #0
 sta R5
 lda R4
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda R5
 sbc ScreenLeft_PageLoc
 sta R5
 lda ThHostArtOrigin
 sec
 sbc #1
 sta R6
 lda ThHostArtOrigin+1
 adc #0                       ; native kernel expects Ypage1, not viewport0
 sta R7
 lda Player_SprAttrib
 and #$20
 sta R3
 Far MetaspriteRenderLoop,jsr
DrawDone:
 Restore
 rts
ThInjury:
 lda #1                       ; original gripper damage scalar A78C..A793
 jmp ThomasHostDamage
ThHealth:
 lda ThomasState+$4a6
 ldx #1
 rts
ThDeathStart:Far KillPlayer,jmp
ThDeath:Far NativePlayerDeath,jmp
ThVisible:clc
 rts
ThBody:clc
 rts
ThAdder:ldy #0
 sec
 rts
ThBoxProfile:ldy #0
 rts
ThHeadWithin:
 lda Player_Y_Position
 cmp #32
 rts
ThStatusName:
 php
 pha
 txa
 pha
 tya
 pha
 tsx
 lda $0103,x
 beq StatusHeader
 cmp #1
 bne StatusDone
 cpy #30
 bne StatusDone
 sty VRAM_Buffer1_Offset
 Far ThColors,jsr             ; actual native A1/Y30 is after bulk lives palette
 jmp StatusDone
StatusHeader:
 ldx #0
StatusCopy:
 lda ThStatusText,x
 sta VRAM_Buffer1+11,x
 inx
 cpx #7
 bne StatusCopy
StatusDone:
 pla
 tay
 pla
 tax
 pla
 plp
 rts
.include "native-charmap.inc"
ThStatusText:.byte "THOMAS "
ThCacheEnd:
