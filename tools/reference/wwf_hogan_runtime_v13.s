; First-Hogan source-driven resident phases. Shared hooks are separate.
.setcpu "6502"
.macpack longbranch
.import NextBank_SMC,SafereturnA_SMC
.macro SaveRuntime
 php
 pha
 txa
 pha
 tya
 pha
 ldx #0
:lda R0,x
 pha
 inx
 cpx #8
 bcc :-
 lda NextBank_SMC+1
 pha
 lda SafecallA_SMC+1
 pha
 lda FarcallJmpTarget_SMC+1
 pha
 lda FarcallJmpTarget_SMC+2
 pha
 lda SafereturnA_SMC+1
 pha
 lda CurrentBankC
 pha
 lda ReloadCHRBank
 pha
.endmacro
.import WfAuthC2,WfHostReady,WfState,WfHostFrame
.import WfRawHostImport,WfRawHostExport,WfRawProxySnapshot,WfRawProxyCollect,WfRawProxyCommit
.import WfProxyValid,WfProxyHealthBefore,WfHoganMetadata,WfRenderBuffer
.import WfPreviousInput,WfPosePage,WfPoseIndex,WfPoseWidth,WfCellCount,WfRenderFace,WfCellOffset
.import SelectedCharacter,FmGroups,CurrentBank,CurrentBankC,ReloadCHRBank
.import __SMCCODE_RUN__,__SMCCODE_SIZE__,FarCallCommon,FarcallJmpTarget_SMC,SafecallA_SMC
.import OperMode,OperMode_Task,GamePauseStatus,TimerControl,InjuryTimer
.import SmPosePtr,ObjectMetasprite,BlankPalette,Player_SprAttrib,CurrentCHRBank,X5ChrMode,X5WideChrActive
.import PlayerFacingDir,ScreenLeft_X_Pos,ScreenLeft_PageLoc
.import VRAM_Buffer1,VRAM_Buffer1_Offset,MetaspriteRenderLoop,X5SetPhysicalChr,X5QueueAreaBackdrop
.import BwScene,CfRetire,WfRetire,WfLoad,WfCheck,WfConstructCold
.import BwBtResolve,CmHostFresh,JnResetDispatch,FmQueueName,HuNativeWorldPalette,MaaBox
.import BlockBufferColli_Head,BlockBufferColli_Side,PlayerHeadWithinTerrain
.import WfIdleRecord,WfIdlePage,WfP1Early,WfP1Retire,WfP1Temp
.import Sprite_Data,GuestOamRotationActive,RgOamRotation
.import FfMuxNativeTail,SamusFreezeRenderFinish
.importzp Player_X_Position,Player_PageLoc,Player_Y_Position,Player_Y_HighPos
.importzp SavedJoypadBits,Player_X_Speed,GameEngineSubroutine,R0,R1,R2,R3,R4,R5,R6,R7
.import CurrentOAMOffset
.import Player_XSpeedAbsolute,Player_X_Scroll,PlayerPhysicsSub,Player_Y_Speed,VerticalForce,VerticalForceDown
.import A_B_Buttons
.export WfMovement,WfGraphics,WfDrawBody,WfColdPortrait,WfColors,WfStatusName
.export WfResolve,WfResolveTargets,WfFresh,WfNoop,WfVisible

.macro WfFar Target
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(Target)|$80)
 jsr FarCallCommon
.endmacro
.segment "WF_RUNTIME_A"
WfReady:
 jsr WfAuthC2
 bcc NotReady
 lda WfHostReady
 cmp #$a7
 bne NotReady
 sec
 rts
NotReady:clc
 rts
WfActive:
 jsr WfReady
 bcc NotReady
 lda GameEngineSubroutine
 cmp #8
 bne NotReady
 lda GamePauseStatus
 and #1
 ora TimerControl
 bne NotReady
 sec
 rts

WfMovement:
 SaveRuntime
 jsr WfActive
 jcc WfRuntimeReturnC
 jsr WfDetachRuntime
 WfFar PlayerPhysicsSub       ; actual native A-edge jump setup, no native X displacement
 jsr WfRawHostImport
 lda #0
 sta WfProxyValid
 ldx #0
FindEnemy:
 jsr WfRawProxySnapshot
 bcs EnemyFound
 inx
 cpx #6
 bcc FindEnemy
 ; No native actor can become an eligible old ring-opponent by accident.
 lda WfState+$2e
 clc
 adc #8
 sta WfState+$2f
 lda #0
 sta WfState+$2d
 beq TickActor
EnemyFound:
 ; Explicit native one-HP proxy constructor. It is not a button hit:
 ; only the real source damage opcode can change200 into a defeat result.
 lda #200
 sta WfState+$7a
 sta WfProxyHealthBefore
 lda #0
 sta WfState+$3d
 sta WfState+$3f
 sta WfState+$41
 sta WfState+$8c
 sta WfState+$31
TickActor:
 ; Platformer translation: native A stays with PlayerPhysicsSub only.
 ; B becomes original A punch; Down+B consumesDown and becomes originalB.
 ; Left/right and Up+B keep their original directional attack meanings.
 lda SavedJoypadBits
 and #$0f
 sta R2
 lda SavedJoypadBits
 and #$40
 beq DonorInputReady
 lda SavedJoypadBits
 and #4
 beq DonorPunch
 lda R2
 and #$fb
 ora #$40
 bne DonorInputStore
DonorPunch:
 lda R2
 ora #$80
DonorInputStore:sta R2
DonorInputReady:
 lda R2
 eor WfPreviousInput
 and R2
 tax
 lda R2
 sta WfPreviousInput
 sta SafecallA_SMC+1
 lda #<WfHostFrame
 sta FarcallJmpTarget_SMC+1
 lda #>WfHostFrame
 sta FarcallJmpTarget_SMC+2
 ldy #0
 lda #3
 jsr FarCallCommon
 jsr WfRawProxyCollect
 jsr WfRawProxyCommit
 ; No snapshot survives this serial Main phase. Native world/AI updates
 ; happen later; external Snapshot/Commit API still needs epoch Notify.
 lda #0
 sta WfProxyValid
 ; Native jump release/falling switches to its genuine fall-force packet.
 ; The source30 packet remains an independent additive hurt displacement.
 lda Player_Y_Speed
 bpl NativeFallForce
 lda A_B_Buttons
 and #$80
 bne NativeVerticalReady
NativeFallForce:
 lda VerticalForceDown
 sta VerticalForce
NativeVerticalReady:
 jsr WfRawHostExport
 lda Player_X_Scroll
 asl
 asl
 asl
 asl
 sta Player_X_Speed
 bpl PositiveSpeed
 eor #$ff
 clc
 adc #1
PositiveSpeed:sta Player_XSpeedAbsolute
 sec
 jmp WfDetachedReturnC

WfGraphics:
 SaveRuntime
 jsr WfReady
 jcc WfRuntimeReturnC
 jsr WfDetachRuntime
 jsr WfBuildPose
 lda #0
 sta ObjectMetasprite
 lda #<(BlankPalette+7)
 sta SmPosePtr
 lda #>(BlankPalette+7)
 sta SmPosePtr+1
 sec
 jmp WfDetachedReturnPending

WfBuildPose:
 lda WfState+$32
 cmp #17
 bcc :+
 lda #0
:
 asl
 tay
 lda WfHoganMetadata+2,y
 sta WfPoseIndex
 lda WfState+$34
 cmp WfHoganMetadata+3,y
 bcc :+
 lda #0
:
 clc
 adc WfPoseIndex
 sta WfPoseIndex
 asl
 clc
 adc WfPoseIndex
 clc
 adc #36                     ; 2+17*2 group header
 tay
 lda WfHoganMetadata+2,y
 sta WfPosePage
 lda WfHoganMetadata,y
 clc
 adc #<WfHoganMetadata
 sta R0
 lda WfHoganMetadata+1,y
 adc #>WfHoganMetadata
 sta R1
 ldy #0
 lda (R0),y
 sta WfPoseWidth
 iny
 lda (R0),y
 sta WfCellCount
 asl
 asl
 sta WfRenderBuffer
 lda WfState+$3a
 and #1
 sta WfRenderFace
 lda #2
 sta WfCellOffset
 ldx #1
Cell:
 ldy WfCellOffset
 lda (R0),y
 sta WfRenderBuffer,x
 iny
 lda (R0),y
 ldy WfRenderFace
 beq :+
 ora #$40
:
 sta WfRenderBuffer+1,x
 ldy WfCellOffset
 iny
 iny
 lda (R0),y
 ldy WfRenderFace
 beq :+
 sta R2
 lda WfPoseWidth
 sec
 sbc R2                      ; native A6C7: mirrorWidth-sourceX
:
 sta WfRenderBuffer+3,x
 ldy WfCellOffset
 iny
 iny
 iny
 lda (R0),y
 sta WfRenderBuffer+2,x
 lda WfCellOffset
 clc
 adc #4
 sta WfCellOffset
 txa
 clc
 adc #4
 tax
 dec WfCellCount
 bne Cell
 lda WfPosePage
 clc
 adc #<546
 ldx #>546
 ldy #0
 WfFar X5SetPhysicalChr
 rts

WfDrawBody:
 SaveRuntime
 jsr WfReady
 jcc WfRuntimeReturnC
 jsr WfDetachRuntime
 jsr WfBuildPose
 lda #<WfRenderBuffer
 sta R0
 lda #>WfRenderBuffer
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
 adc WfState+$36
 sta R4
 lda #0
 ldx WfState+$36
 bpl :+
 lda #$ff
:
 adc R5
 sta R5
 ; Native floor anchor is PlayerY+32. Original body anchor42 and pose38
 ; remain live; Hogan's original foot geometry sets source plane +39.
 lda Player_Y_Position
 clc
 adc #36
 sta R6
 lda Player_Y_HighPos
 adc #0
 sta R7
 lda R6
 sec
 sbc WfState+$42
 sta R6
 lda R7
 sbc #0
 sta R7
 lda R6
 clc
 adc WfState+$38
 sta R6
 lda #0
 ldx WfState+$38
 bpl :+
 lda #$ff
:
 adc R7
 sta R7
 lda Player_SprAttrib
 and #$20
 sta R3
 lda CurrentOAMOffset
 sta WfP1Temp
 WfFar MetaspriteRenderLoop
 ; The genuine kernel stripssoftware bit3. Mark the emitted source span
 ; AFTER return, with the same actual logical-to-physical OAM rotation.
 ldy WfP1Temp
WfTagBody:
 cpy CurrentOAMOffset
 beq WfTagDone
 tya
 ldx GuestOamRotationActive
 beq :+
 clc
 adc RgOamRotation
:tax
 lda Sprite_Data+2,x
 ora #8
 sta Sprite_Data+2,x
 iny
 iny
 iny
 iny
 bne WfTagBody
WfTagDone:
 jsr WfP1Early
 sec
 jmp WfDetachedReturnPending

WfReturnPending:
 ; SaveRuntime's top saved byte is the incoming reload request. Preserve it
 ; and OR any newly requested publication from the real page producer.
 tsx
 lda $0101,x
 ora ReloadCHRBank
 sta $0101,x
 sec
 jmp WfRuntimeReturnC

WfColdIdentity:
 lda SelectedCharacter
 cmp #29
 bne ColdNo
 lda FmGroups
 and #7
 bne ColdNo
 sec
 rts
ColdNo:clc
 rts
WfColdPortrait:
 SaveRuntime
 jsr WfColdIdentity
 jcc WfRuntimeReturnC
 lda #<WfIdlePage
 ldx #>WfIdlePage
 ldy #0
 WfFar X5SetPhysicalChr
 lda #.lobyte(.bank(WfIdleRecord)|$80)
 sta CurrentBankC
 sta $5116
 lda #<(WfIdleRecord+$2000)
 sta R0
 lda #>(WfIdleRecord+$2000)
 sta R1
 lda Player_X_Position
 sta R4
 lda #0
 sta R5
 sta R3
 lda Player_Y_Position
 clc
 adc #24
 sta R6
 lda #1
 adc #0
 sta R7
 WfFar MetaspriteRenderLoop
 sec
 jmp WfReturnPending

WfColors:
 SaveRuntime
 jsr WfColdIdentity
 jcc WfRuntimeReturnC
 ldx VRAM_Buffer1_Offset
 cpx #68
 bcs ColorsDone
 WfFar X5QueueAreaBackdrop
 jsr WfQueueRoles
ColorsDone:sec
 jmp WfRuntimeReturnC
WfQueueRoles:
 ldx VRAM_Buffer1_Offset
 cpx #71
 bcs RolesDone
 ldy #0
RoleCopy:
 lda WfRolePacket,y
 sta VRAM_Buffer1,x
 beq RolesOffset
 inx
 iny
 bne RoleCopy
RolesOffset:stx VRAM_Buffer1_Offset
RolesDone:rts
WfRolePacket:.byte $3f,$11,3,$28,$27,$17,$3f,$15,3,$16,$05,$0f,0

WfFresh:
 WfFar CmHostFresh
 SaveRuntime
 jsr WfAuthC2
 bcc FreshDone
 lda #0
 sta WfHostReady
FreshDone:jmp WfRuntimeReturnOriginal
WfStatusName:
 cmp #0
 beq StatusHeader
 cmp #1
 bne StatusDone
 cpy #30
 bne StatusDone
 SaveRuntime
 sty VRAM_Buffer1_Offset
 jsr WfQueueRoles             ; black lives universal remains native
 jmp WfRuntimeReturnOriginal
StatusHeader:
 php
 tya
 pha
 ldy #6
:
 lda WfHudName,y
 sta VRAM_Buffer1+11,y
 dey
 bpl :-
 pla
 tay
 plp
 lda #0
StatusDone:rts
.include "inc/charmap.inc"
WfHudName:.byte " HOGAN "
; Explicit basic-WIP policy: one native life; authentic WWF endurance
; integration remains unqualified. Never return selectedID as status.
WfOneLifeStatus:lda #0
 rts
WfNoop:clc
 rts
WfVisible:sec
 rts

; Genuine B020 resolver ABI: A=3*service, original nativeAXYP is saved
; by the outer row. Targets are ROM-owned phase workers, not cache entries.
WfResolve:
 pha
 lda SelectedCharacter
 cmp #29
 beq OwnResolve
 pla
 WfFar BwBtResolve
 rts
OwnResolve:
 lda FmGroups
 and #7
 bne ResolveBadPop
 pla
 cmp #108
 bcs ResolveBad
 tay
 lda WfResolveTargets,y
 sta FarcallJmpTarget_SMC+1
 lda WfResolveTargets+1,y
 sta FarcallJmpTarget_SMC+2
 lda WfResolveTargets+2,y
 sec
 rts
ResolveBadPop:pla
ResolveBad:clc
 rts
.macro Target Name
 .byte <Name,>Name,.lobyte(.bank(Name)|$80)
.endmacro
WfResolveTargets:
 Target WfMovement
 Target WfGraphics
 Target WfDrawBody
 Target WfNoop
 Target WfNoop
 Target WfNoop
 Target WfOneLifeStatus
 Target WfNoop
 Target WfNoop
 Target WfVisible
 Target BlockBufferColli_Head
 Target WfNoop
 Target WfNoop
 Target WfNoop
 Target BlockBufferColli_Side
 Target WfFresh
 Target MaaBox
 Target WfColdPortrait
 Target FmQueueName
 Target JnResetDispatch
 Target WfNoop
 Target WfNoop
 Target WfNoop
 Target WfNoop
 Target WfNoop
 Target WfNoop
 Target WfColors
 Target WfNoop
 Target PlayerHeadWithinTerrain
 Target WfNoop
 Target WfStatusName
 Target WfNoop
 Target HuNativeWorldPalette
 Target WfNoop
 Target WfNoop
 Target WfNoop
; Proposed same-size shared call targets; no shared hook installed here.
.export WfMenuRetire,WfScene
WfMenuRetire:
 SaveRuntime
 jsr WfP1Retire
 jsr WfRetire
 WfFar CfRetire
 jmp WfRuntimeReturnOriginal
WfScene:
 SaveRuntime
 lda SelectedCharacter
 cmp #29
 beq :+
 jsr WfP1Retire
 jsr WfRetire                 ; BEFORE inner Bw/S2/Qw/Ar/Fw writes
 jmp WfSceneForeignReturn
:
 WfFar BwScene                ; native Move and every existing owner once
 jsr WfColdIdentity
 bcc SceneDone
 jsr WfCheck
 bcs SceneConstruct
 jsr WfLoad
 bcc SceneDone
SceneConstruct:
 jsr WfAuthC2
 bcc SceneDone
 lda WfHostReady
 cmp #$a7
 bne SceneInitialize
 lda #0
 sta WfState+$30
 sta WfState+$3c
 sta WfState+$3e
 sta WfState+$40
 sta WfPreviousInput
SceneInitialize:
 jsr WfConstructCold
SceneDone:
 jmp WfRuntimeReturnOriginal
.export WfLegacyFreeze
WfLegacyFreeze:
 ; Extra own-ROM transport only on native nonzero-freeze path.
 ; Both genuine callbacks see the same incomingstateA/carry and order.
 WfFar FfMuxNativeTail
 WfFar SamusFreezeRenderFinish
 rts
WfRuntimeReturnC:
 tsx
 lda $0113,x
 and #$fe
 bcc :+
 ora #1
:sta $0113,x
WfRuntimeReturnOriginal:
 pla
 sta ReloadCHRBank
 pla
 sta CurrentBankC
 sta $5116
 pla
 sta SafereturnA_SMC+1
 pla
 sta FarcallJmpTarget_SMC+2
 pla
 sta FarcallJmpTarget_SMC+1
 pla
 sta SafecallA_SMC+1
 pla
 sta NextBank_SMC+1
 ldx #7
:pla
 sta R0,x
 dex
 bpl :-
 pla
 tay
 pla
 tax
 pla
 plp
 rts
; SFC-WORKER-ONLY forwarding ABI. Actual InitScreen's genuine farcall
; is the sole importing caller. Restore all19 own bytes, discard exactly
; its current JSR-worker return, retain original SFC saved-oldA and caller
; return, then reuse NextBank_SMC. No additional foreign ctor/save frame.
; The fullflags/return-origin fixture pins that genuine live frame.
WfSceneForeignReturn:
 pla
 sta ReloadCHRBank
 pla
 sta CurrentBankC
 sta $5116
 pla
 sta SafereturnA_SMC+1
 pla
 sta FarcallJmpTarget_SMC+2
 pla
 sta FarcallJmpTarget_SMC+1
 pla
 sta SafecallA_SMC+1
 pla
 sta NextBank_SMC+1
 ldx #7
:pla
 sta R0,x
 dex
 bpl :-
 pla
 tay
 pla
 tax
 pla
 plp
  sta SafecallA_SMC+1
 pla
 pla
 lda #<BwScene
 sta FarcallJmpTarget_SMC+1
 lda #>BwScene
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(BwScene)|$80)
 sta NextBank_SMC+1
 jmp NextBank_SMC

; PRIVATE unpublished WfReset wrapper retired: zero actual import/call
; consumers after19 targets genuineJn and authenticatedScene owns reset.
; This funds serial active-frame detachment inside the same resident lease.
; Original19 saved bytes plus the real JSR-detach return occupy exactly21
; selected-C2 data bytes. Full ROM cookie authentication precedes every
; call. Only movement/graphics/draw use it; none recursively calls another
; detached entry. Native IRQ/NMI never calls a selected29 foreground API.
; Scoped native R0..7 remain unchanged and no CF workspace is borrowed.
.segment "WF_DETACHED_STATE"
.export WfDetachedFrame,WfDetachedFrameEnd
WfDetachedFrame:.res 21
WfDetachedFrameEnd:
.segment "WF_RUNTIME_A"
WfDetachRuntime:
 tsx
 ldy #0
:lda $0101,x
 sta WfDetachedFrame,y
 inx
 iny
 cpy #21
 bcc :-
 dex
 dex
 txs
 lda WfDetachedFrame
 sta $0101,x
 lda WfDetachedFrame+1
 sta $0102,x
 rts
WfDetachedReturnPending:
 lda WfDetachedFrame+2
 ora ReloadCHRBank
 sta WfDetachedFrame+2
 sec
WfDetachedReturnC:
 ldx #18
:lda WfDetachedFrame+2,x
 pha
 dex
 bpl :-
 jmp WfRuntimeReturnC

.export WfRuntimeReturnC,WfRuntimeReturnOriginal
.export WfRuntimeEnd
WfRuntimeEnd:
