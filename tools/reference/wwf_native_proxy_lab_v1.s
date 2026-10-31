; Isolated selected-cache native SMB interface. No shared hooks/allocation.
; Every native alias is generated from the hash-pinned current a126 DBG.
.setcpu "6502"
.macpack longbranch
.import WfState,BlockBufferAddr,MTileAttribute,BoundBoxCtrlData
.import ShellOrBlockDefeat,ImposeGravitySprObj,VerticalForce
.import Player_X_Position,Player_PageLoc,Player_Y_Position,Player_Y_HighPos
.import Player_State,Player_Y_Speed,Player_X_Scroll,Player_X_Speed
.import Player_XSpeedAbsolute,PlayerFacingDir,PlayerSize,CrouchingFlag
.import Enemy_BoundBoxCtrl,Enemy_MovingDir
.importzp Enemy_Flag,Enemy_ID,Enemy_State,Enemy_X_Position,Enemy_PageLoc
.importzp Enemy_Y_Position,Enemy_Y_HighPos,ObjectOffset
.importzp R0,R1,R2,R3,R4,R5,R6,R7,MTILE_SOLID,MTILE_CLIMB

.segment "WF_PROXY_CONTEXT"
.export WfProxyContext,WfProxyResult,WfPointX,WfPointPage,WfPointY,WfPointYHi
.export WfProxyValid,WfProxySlot,WfProxyHealthBefore,WfProxyHealthAfter
.export WfProxyActionBefore,WfProxyActionAfter,WfProxySelfBefore,WfProxySelfAfter
.export WfProxyHitKind,WfProxyEpochs,WfProxyNativeReturn
WfProxyContext:
WfProxyResult:.res 1
WfPointX:.res 1
WfPointPage:.res 1
WfPointY:.res 1
WfPointYHi:.res 1
WpOldX:.res 1
WpOldPage:.res 1
WpOldY:.res 1
WpOldYHi:.res 1
WpOldSourceX:.res 1
WpOldJump:.res 1
WpDX:.res 1
WpDY:.res 1
WpClampX:.res 1
WpClampY:.res 1
WfProxyValid:.res 1
WfProxySlot:.res 1
WpArg:.res 1
WpFlag:.res 1
WpID:.res 1
WpState:.res 1
WpPage:.res 1
WpX:.res 1
WpYHi:.res 1
WpY:.res 1
WpBox:.res 1
WpEpoch:.res 1
WfProxyHealthBefore:.res 1
WfProxyHealthAfter:.res 1
WfProxyActionBefore:.res 1
WfProxyActionAfter:.res 1
WfProxySelfBefore:.res 1
WfProxySelfAfter:.res 1
WfProxyHitKind:.res 1
WpTemp:.res 1
WpTemp2:.res 1
WpSign:.res 1
WpDir:.res 1
WfProxyEpochs:.res 6
WfProxyNativeReturn:.res 4
WpEchoX:.res 1
WpEchoPage:.res 1
WpEchoY:.res 1
WpEchoYHi:.res 1
.res 64-(*-WfProxyContext)

.macro SaveNative
 .local loop
 php
 pha
 txa
 pha
 tya
 pha
 ldx #7
loop:
 lda R0,x
 pha
 dex
 bpl loop
.endmacro
.macro ReturnC
 .local loop
 ; Original caller P is exactly12 bytes above the current liveSP.
 ; Change C only, then restore every borrowed byte and actual AXYP.
 tsx
 lda $010c,x
 and #$fe
 ora WfProxyResult
 sta $010c,x
 ldx #0
loop:
 pla
 sta R0,x
 inx
 cpx #8
 bcc loop
 pla
 tay
 pla
 tax
 pla
 plp
 rts
.endmacro

.segment "WF_NATIVE_PROXY"
.export WfProxyReset,WfProxyResetCore,WfHostPoint,WfProxyNoteReuse
.export WfProxySnapshot,WfProxyCollect
WfProxyReset:
 SaveNative
 jsr WfProxyResetCore
 ReturnC
WfProxyResetCore:
 lda #0
 ldx #63
:
 sta WfProxyContext,x
 dex
 bpl :-
 rts

; Physical world point. Y-high must be1; top32 and bottom240 are outside
; the native13-row block buffer. Return preserves AXYP except resultC.
WfHostPoint:
 SaveNative
 jsr WfHostPointCore
 ReturnC
WfHostPointCore:
 lda #0
 sta WfProxyResult
 lda WfPointYHi
 cmp #1
 bne WpPointDone
 lda WfPointY
 cmp #32
 bcc WpPointDone
 cmp #240
 bcs WpPointDone
 and #$f0
 sec
 sbc #32
 pha
 lda WfPointPage
 and #1
 tay
 lda BlockBufferAddr+2,y
 sta R7
 lda WfPointX
 lsr
 lsr
 lsr
 lsr
 clc
 adc BlockBufferAddr,y
 sta R6
 pla
 tay
 lda (R6),y
 tay
 lda MTileAttribute,y
 and #MTILE_SOLID|MTILE_CLIMB
 cmp #MTILE_SOLID
 bne WpPointDone
 inc WfProxyResult
WpPointDone:rts

; Future genuine CheckpointEnemyID/EraseEnemyObject call sites MUST notify
; this entry. It is not hooked in a shared cartridge by this source lab.
WfProxyNoteReuse:
 stx WpArg
 SaveNative
 lda #0
 sta WfProxyResult
 ldx WpArg
 cpx #6
 bcs WpReuseDone
 inc WfProxyEpochs,x
 cpx WfProxySlot
 bne :+
 lda #0
 sta WfProxyValid
:
 inc WfProxyResult
WpReuseDone:
 ReturnC

; X=native enemy slot. No source-ready/health byte is synthesized.
; Actor1 receives only current geometry/direction; original health/actions
; remain source-owned and the raw before/after packet stays inspectable.
WfProxySnapshot:
 stx WpArg
 SaveNative
 lda #0
 sta WfProxyResult
 sta WfProxyValid
 sta WfProxyHitKind
 ldx WpArg
 cpx #6
 jcs WpSnapshotDone
 lda Enemy_Flag,x
 jeq WpSnapshotDone
 jmi WpSnapshotDone
 sta WpFlag
 lda Enemy_ID,x
 cmp #$15
 jcs WpSnapshotDone
 cmp #8                        ; native frenzy bullet is not an ordinary body
 jeq WpSnapshotDone
 cmp #12                       ; Podoboo cannot be a grounded wrestler proxy
 jeq WpSnapshotDone
 sta WpID
 lda Enemy_State,x
 and #$20
 jne WpSnapshotDone
 lda Enemy_State,x
 sta WpState
 lda Enemy_Y_HighPos,x
 cmp #1
 jne WpSnapshotDone
 sta WpYHi
 lda Enemy_BoundBoxCtrl,x
 cmp #21
 jcs WpSnapshotDone
 sta WpBox
 asl
 asl
 tay
 lda Enemy_X_Position,x
 clc
 adc BoundBoxCtrlData,y
 sta WpTemp
 lda Enemy_PageLoc,x
 adc #0
 sta WpTemp2
 lda WpTemp
 sec
 sbc Player_X_Position
 sta WpTemp
 lda WpTemp2
 sbc Player_PageLoc
 beq WpPositiveDistance
 cmp #$ff
 jne WpSnapshotDone
 lda WpTemp
 cmp #$a0                     ; reject distance below-96
 jcc WpSnapshotDone
 bcs WpDistanceOK
WpPositiveDistance:
 lda WpTemp
 cmp #96
 jcs WpSnapshotDone
WpDistanceOK:
 lda WpTemp
 clc
 adc #128
 sta WfState+$2d
 lda BoundBoxCtrlData+2,y
 sec
 sbc BoundBoxCtrlData,y
 clc
 adc #1
 sta WfState+$87
 lda Enemy_X_Position,x
 sta WpX
 lda Enemy_PageLoc,x
 sta WpPage
 lda Enemy_Y_Position,x
 sta WpY
 lda Enemy_MovingDir,x
 sta WpDir
 and #2
 lsr
 sta WfState+$3b             ; native1right/2left -> source0right/1left
 lda WfProxyEpochs,x
 sta WpEpoch
 stx WfProxySlot
 ; Ring depth is NOT platformer Y. Only overlap eligibility is projected.
 lda WfState+$2e
 clc
 adc #8
 sta WfState+$2f
 lda Player_Y_HighPos
 cmp #1
 bne WpSnapshotAccepted
 lda WpY
 clc
 adc BoundBoxCtrlData+3,y
 bcs WpSnapshotAccepted
 cmp Player_Y_Position
 bcc WpSnapshotAccepted
 lda Player_Y_Position
 clc
 adc #31                     ; explicit native16x32 WIP player profile
 bcs WpSnapshotAccepted
 sta WpTemp
 lda WpY
 clc
 adc BoundBoxCtrlData+1,y
 bcs WpSnapshotAccepted
 cmp WpTemp
 bcc WpSameDepth
 bne WpSnapshotAccepted
WpSameDepth:
 lda WfState+$2e
 sta WfState+$2f
WpSnapshotAccepted:
 lda WfState+$7a
 sta WfProxyHealthBefore
 lda WfState+$3d
 sta WfProxyActionBefore
 lda WfState+$79
 sta WfProxySelfBefore
 lda #1
 sta WfProxyValid
 sta WfProxyResult
WpSnapshotDone:
 ReturnC

WfProxyCollect:
 SaveNative
 lda #0
 sta WfProxyResult
 sta WfProxyHitKind
 lda WfState+$7a
 sta WfProxyHealthAfter
 lda WfState+$3d
 sta WfProxyActionAfter
 lda WfState+$79
 sta WfProxySelfAfter
 lda WfProxyValid
 beq WpCollectDone
 lda WfProxyHealthAfter
 cmp WfProxyHealthBefore
 bcc WpCollectHit
 cmp #$e6                    ; native original underflow/knockdown sentinel
 bcc WpCollectDone
 lda WfProxyHealthBefore
 cmp #$e6
 bcs WpCollectDone
WpCollectHit:
 inc WfProxyHitKind
 inc WfProxyResult
WpCollectDone:
 ReturnC
.export WfNativeProxyCoreEnd
WfNativeProxyCoreEnd:
.assert *<=$d400,lderror,"Isolated proxy core budget"

.segment "WF_NATIVE_PROXY_TAIL"
.export WfHostImport,WfHostExport,WfProxyCommit
; Must execute AFTER the preceding nativeBG clamps and BEFORE the next
; source update. Rebase sourceX only; never replace original ring-depth.
WfHostImport:
 SaveNative
 lda Player_X_Position
 sta WpOldX
 cmp WpEchoX
 bne WpXChanged
 lda Player_PageLoc
 cmp WpEchoPage
 beq WpXSame
WpXChanged:lda #1
 bne WpXFlag
WpXSame:lda #0
WpXFlag:sta WpClampX
 lda Player_PageLoc
 sta WpOldPage
 lda Player_Y_Position
 sta WpOldY
 cmp WpEchoY
 bne WpYChanged
 lda Player_Y_HighPos
 cmp WpEchoYHi
 beq WpYSame
WpYChanged:lda #1
 bne WpYFlag
WpYSame:lda #0
WpYFlag:sta WpClampY
 lda Player_Y_HighPos
 sta WpOldYHi
 lda #128
 sta WfState+$2c
 sta WpOldSourceX
 lda WfState+$30
 sta WpOldJump
 lda #1
 sta WfProxyResult
 ReturnC

WfHostExport:
 SaveNative
 lda WfState+$2c
 sec
 sbc WpOldSourceX
 sta WpDX
 sta Player_X_Scroll
 clc
 adc Player_X_Position
 sta Player_X_Position
 lda #0
 ldx WpDX
 bpl :+
 lda #$ff
:
 adc Player_PageLoc
 sta Player_PageLoc
 lda WfState+$30
 sec
 sbc WpOldJump
 sta WpDY
 clc
 adc Player_Y_Position
 sta Player_Y_Position
 lda #0
 ldx WpDY
 bpl :+
 lda #$ff
:
 adc Player_Y_HighPos
 sta Player_Y_HighPos
 lda WpDY
 beq WpMaybeNativeFall
 sta Player_Y_Speed
 lda #1
 ldx WpDY
 bmi :+
 lda #2
:
 sta Player_State
 lda WfState+$30
 bne WpExportFacing
 ; Source jump packet ended: subsequent unsupported fall starts natively.
 lda #0
 sta Player_Y_Speed
 beq WpExportFacing
WpMaybeNativeFall:
 lda WfState+$30
 bne WpExportFacing
 lda Player_State
 beq WpExportFacing
 lda VerticalForce
 sta R0
 ldx #0
 lda #4
 jsr ImposeGravitySprObj      ; actual fixed native fall/fraction arithmetic
 lda #2
 sta Player_State
WpExportFacing:
 lda #1
 ldx WfState+$3a
 beq :+
 lda #2
:
 sta PlayerFacingDir
 lda #0
 sta PlayerSize
 sta CrouchingFlag
 lda Player_X_Position
 sta WpEchoX
 lda Player_PageLoc
 sta WpEchoPage
 lda Player_Y_Position
 sta WpEchoY
 lda Player_Y_HighPos
 sta WpEchoYHi
 lda #1
 sta WfProxyResult
 ReturnC

; No defeat without an original target-health transition and unchanged
; native actor tuple+epoch. Raw source hurt/health remain in the context.
WfProxyCommit:
 SaveNative
 lda #0
 sta WfProxyResult
 lda WfProxyValid
 jeq WpCommitDone
 lda WfProxyHitKind
 jeq WpCommitDone
 ldx WfProxySlot
 cpx #6
 jcs WpCommitDone
 lda WfProxyEpochs,x
 cmp WpEpoch
 jne WpCommitDone
.macro Recheck native,snapshot
 lda native,x
 cmp snapshot
 jne WpCommitDone
.endmacro
 Recheck Enemy_Flag,WpFlag
 Recheck Enemy_ID,WpID
 Recheck Enemy_State,WpState
 Recheck Enemy_PageLoc,WpPage
 Recheck Enemy_X_Position,WpX
 Recheck Enemy_Y_HighPos,WpYHi
 Recheck Enemy_Y_Position,WpY
 Recheck Enemy_BoundBoxCtrl,WpBox
 Recheck Enemy_MovingDir,WpDir
 lda ObjectOffset
 pha
 stx ObjectOffset
 stx R1
 jsr ShellOrBlockDefeat       ; true current native callback, no canned kill
 sta WfProxyNativeReturn
 stx WfProxyNativeReturn+1
 sty WfProxyNativeReturn+2
 php
 pla
 sta WfProxyNativeReturn+3
 pla
 sta ObjectOffset
 lda #0
 sta WfProxyValid
 lda #1
 sta WfProxyResult
WpCommitDone:
 ReturnC
.export WfNativeProxyTailEnd
WfNativeProxyTailEnd:
.assert *<=$dfd0,lderror,"Isolated proxy tail budget"
