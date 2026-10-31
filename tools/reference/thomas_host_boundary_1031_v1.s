; Isolated source-owned Thomas host boundaries. No shared row/hook admission.
.setcpu "6502"
.macpack longbranch
.import ThomasC2ColdInit,ThomasC2AcceptedFrame,ThomasC2Borrow,ThomasC2Return
.import ThomasState,ThReady,ThBusy,ThOwnerPlayer,ThLastEpoch,ThHaveEpoch
.import ThomasBodyBox,ThomasOverlap,ThomasNativeDamage
.import ThAttackEnabled,ThAttackRect,ThPoseCommand
.importzp R0,R1,R2,R3,R4,R5,R6,R7
.importzp Player_X_Position,Player_PageLoc,Player_Y_Position,Player_Y_HighPos
.importzp Player_X_Speed,Player_Y_Speed,Player_State,PowerUpType
.import Player_Rel_XPos,Player_Rel_YPos,PlayerFacingDir,CurrentPlayer,InjuryTimer
.import ScreenLeft_X_Pos,ScreenLeft_PageLoc,BoundingBox_UL_Corner,BoundingBox_LR_Corner
.import Enemy_Flag,Enemy_ID,EnemyOffscrBitsMasked
.importzp Enemy_State,Enemy_Y_HighPos
.import BlockBufferColli_Feet,BlockBufferColli_Head,BlockBufferColli_Side
.import HandleEnemyFBallCol,MarioSourcePowerupCollision,KillPlayer
.import Bank_BlockBufferColli_Feet,Bank_BlockBufferColli_Head,Bank_BlockBufferColli_Side
.import Bank_HandleEnemyFBallCol,Bank_MarioSourcePowerupCollision,Bank_KillPlayer
.import SafecallA_SMC,FarcallJmpTarget_SMC,FarCallCommon
.export ThomasHostCold,ThomasHostFrame,ThomasHostAfterTerrain,ThomasHostBody
.export ThomasHostFeet,ThomasHostHead,ThomasHostSide,ThomasHostQueries
.export ThomasHostWeapons,ThomasHostDamage,ThomasHostPickup,ThomasHostRenderAnchor
.export ThHostGround,ThHostBodyRect,ThHostQueries,ThHostAttackRect,ThHostArtOrigin
.export ThomasHostBoundaryEnd
ThHostGround=$C820             ; Native top-coordinate plane, 16-bit.
ThHostOldXY=$C822              ; xlo/xhi/ylo/yhi before accepted original update.
ThHostBodyRect=$C826           ; Original body in actual host viewport coordinates.
ThHostQueries=$C82A            ; Native feet L/R/head/side returned metatiles.
ThHostAttackRect=$C82E         ; Native viewport original inclusive melee rectangle.
ThHostHitEpoch=$C832
ThHostHaveHit=$C833
ThHostArtOrigin=$C834          ; 16-bit original-canvas origin in host viewport.
ThHostTemp=$C836
.macro ThSave
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
.macro ThRestore
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
.macro ThFar Target,Mode,TargetBank
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(TargetBank)
 .if .xmatch({Mode},{jmp})
 jmp FarCallCommon
 .else
 jsr FarCallCommon
 .endif
.endmacro
.segment "CODE"
; Requires authenticated selected C2/RAM3 ownership before entry. Public caller
; A=floor/X=player/Y=epoch as original wrapper; caller AXYP/SP retained.
ThomasHostCold:
 jsr ThomasC2ColdInit
 ThSave
 lda ThReady
 cmp #$a7
 bne ColdDone
 lda Player_Y_Position
 sta ThHostGround
 lda Player_Y_HighPos
 sta ThHostGround+1
 lda #0
 sta ThHostHaveHit
 jsr ThomasHostImportX
ColdDone:
 ThRestore
 rts
ThomasHostImportX:
 lda Player_X_Position
 clc
 adc #8                       ; Native anchor -> original center, once.
 sta ThomasState+$D4
 lda Player_PageLoc
 adc #0
 sta ThomasState+$E5
 lda Player_Rel_XPos
 clc
 adc #8
 sta ThomasState+$94
 rts
; Original accepted actor update exactly once. Host collision still belongs to
; the caller's genuine native progression phase, followed by AfterTerrain.
ThomasHostFrame:
 php
 pha
 txa
 pha
 tya
 pha
 cpx #1
 jne FrameDone
 lda ThReady
 cmp #$a7
 jne FrameDone
 lda ThBusy
 jne FrameDone
 lda ThHaveEpoch
 beq FrameNew
 cpy ThLastEpoch
 jeq FrameDone
FrameNew:
 lda Player_X_Position
 sta ThHostOldXY
 lda Player_PageLoc
 sta ThHostOldXY+1
 lda Player_Y_Position
 sta ThHostOldXY+2
 lda Player_Y_HighPos
 sta ThHostOldXY+3
 jsr ThomasHostImportX
 tsx
 lda $0103,x
 ldx #1
 jsr ThomasC2AcceptedFrame
 lda ThomasState+$D4
 sec
 sbc #8
 sta Player_X_Position
 lda ThomasState+$E5
 sbc #0
 sta Player_PageLoc
 ; Source B6 contains the actual jump displacement. It is never added twice.
 lda ThomasState+$B6
 sec
 sbc #$87
 sta ThHostTemp
 ldx #0
 bit ThHostTemp
 bpl :+
 dex
:lda ThHostGround
 clc
 adc ThHostTemp
 sta Player_Y_Position
 txa
 adc ThHostGround+1
 sta Player_Y_HighPos
 lda Player_X_Position
 sec
 sbc ThHostOldXY
 sta Player_X_Speed
 lda Player_Y_Position
 sec
 sbc ThHostOldXY+2
 sta Player_Y_Speed
 lda ThomasState+$69
 and #1
 eor #1
 clc
 adc #1
 sta PlayerFacingDir
FrameDone:
 pla
 tay
 pla
 tax
 pla
 plp
 rts
; Rebase the source plane after native support/ceiling/platform correction.
; A genuine host collision/terrain phase must run before this entry. It does
; not integrate velocity or manufacture support. Source grounded state is not
; inferred from a sampled metatile alone.
ThomasHostAfterTerrain:
 ThSave
 jsr ThomasHostImportX
 lda ThomasState+$B6
 sec
 sbc #$87
 sta ThHostTemp
 ldx #0
 bit ThHostTemp
 bpl :+
 dex
:lda Player_Y_Position
 sec
 sbc ThHostTemp
 sta ThHostGround
 txa
 sta ThHostTemp
 lda Player_Y_HighPos
 sbc ThHostTemp
 sta ThHostGround+1
 ThRestore
 rts
; Original inclusive body rectangle C0B6, with source Y189 -> host footY+32.
ThomasHostBody:
 ThSave
 jsr ThomasHostImportX
 jsr ThomasC2Borrow
 ldx #0
 jsr ThomasBodyBox
 .repeat 4,I
 lda R0+I
 sta ThHostBodyRect+I
 .endrepeat
 jsr ThomasC2Return
 lda ThHostBodyRect
 sta BoundingBox_UL_Corner
 lda ThHostBodyRect+2
 sta BoundingBox_LR_Corner
 lda ThHostGround
 sec
 sbc #157                     ; groundY+32-189
 sta ThHostTemp
 lda ThHostBodyRect+1
 clc
 adc ThHostTemp
 sta ThHostBodyRect+1
 sta BoundingBox_UL_Corner+1
 lda ThHostBodyRect+3
 clc
 adc ThHostTemp
 sta ThHostBodyRect+3
 sta BoundingBox_LR_Corner+1
 ThRestore
 rts
; Actual host query ABI is retained: Y profile input, native AXYP/result scratch
; outputs are live. These leaves are the future typed terrain ingress targets.
ThomasHostFeet: ThFar BlockBufferColli_Feet,jmp,Bank_BlockBufferColli_Feet
ThomasHostHead: ThFar BlockBufferColli_Head,jmp,Bank_BlockBufferColli_Head
ThomasHostSide: ThFar BlockBufferColli_Side,jmp,Bank_BlockBufferColli_Side
ThomasHostQueries:
 ThSave
 ldy #0
 jsr ThomasHostFeet
 sta ThHostQueries
 jsr ThomasHostFeet
 sta ThHostQueries+1
 ldy #0
 jsr ThomasHostHead
 sta ThHostQueries+2
 ldy #3
 jsr ThomasHostSide
 sta ThHostQueries+3
 ThRestore
 rts
; The art scripts already encode jump phase. Canvas origin removes sourceB6
; displacement once, while retaining every original baked pose pixel.
; Original canvasY104/foot184 -> native ground foot+32: origin=groundY-48.
ThomasHostRenderAnchor:
 ThSave
 lda ThHostGround
 sec
 sbc #48
 sta ThHostArtOrigin
 lda ThHostGround+1
 sbc #1                       ; native Yhigh1 is viewport high0
 sta ThHostArtOrigin+1
 ThRestore
 rts
; Consume one original attack-window publication per accepted epoch. Bounds
; are exactly original C65B inclusive AABB; host target defeat/immunity/score
; remains the genuine HandleEnemyFBallCol implementation.
ThomasHostWeapons:
 ThSave
 lda ThAttackEnabled
 jeq WeaponsDone
 lda ThHostHaveHit
 beq AttackNew
 lda ThHostHitEpoch
 cmp ThLastEpoch
 jeq WeaponsDone
AttackNew:
 lda ThLastEpoch
 sta ThHostHitEpoch
 lda #1
 sta ThHostHaveHit
 lda ThHostGround
 sec
 sbc #157
 sta ThHostTemp
 .repeat 4,I
 lda ThAttackRect+I
 .if I=1 .or I=3
 clc
 adc ThHostTemp
 .endif
 sta ThHostAttackRect+I
 .endrepeat
 ldx #5
HitScan:
 lda Enemy_Flag,x
 jeq HitNext
 lda Enemy_State,x
 and #$20
 jne HitNext
 lda EnemyOffscrBitsMasked,x
 jne HitNext
 lda Enemy_Y_HighPos,x
 cmp #1
 jne HitNext
 stx ThHostTemp+1
 txa
 clc
 adc #1
 asl
 asl
 tay
 .repeat 4,I
 lda ThHostAttackRect+I
 sta R0+I
 lda BoundingBox_UL_Corner+I,y
 sta R4+I
 .endrepeat
 jsr ThomasOverlap
 pha
 ldx ThHostTemp+1
 pla
 beq HitNext
 stx R1
 ThFar HandleEnemyFBallCol,jsr,Bank_HandleEnemyFBallCol
 jmp WeaponsDone             ; one original melee event, one native target
HitNext:
 dex
 jpl HitScan
WeaponsDone:
 ThRestore
 rts
; A=actual source damage scalar, X always forced to original player slot6.
; Full donor HP/reaction math retained. Native life loss is only underflow.
ThomasHostDamage:
 ThSave
 jsr ThomasC2Borrow
 tsx
 lda $010B,x                 ; eight scope pushes + savedY/X/A/P
 sta ThomasState+$037A
 ldx #6
 jsr ThomasNativeDamage
 jsr ThomasC2Return
 lda ThomasState+$04A6
 bpl DamageDone
 ThFar KillPlayer,jsr,Bank_KillPlayer
DamageDone:
 ThRestore
 rts
; Genuine host mushroom/flower/star/1UP progression, no synthetic Thomas heal.
ThomasHostPickup: ThFar MarioSourcePowerupCollision,jmp,Bank_MarioSourcePowerupCollision
ThomasHostBoundaryEnd:
