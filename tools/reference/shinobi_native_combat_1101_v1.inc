; Native enemy contact for actual source shuriken slots, not a second mover.
; Authenticated A3/C2 only. Original phase, pose bbox and slot expiry remain
; owners; this adapter calls native SMB box/defeat services for actual enemies.
; Source private OAM200..20F is retired by the8x16 renderer replacement.
ShContactSlot=ShState+$0200
ShContactEnemy=ShState+$0201
ShContactObject=ShState+$0202
ShContactBox=ShState+$0203
ShContactResult=ShState+$0207
ShContactWorld=ShState+$0208

.macro ShNativeFar Target,Bank
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #Bank
 jsr FarCallCommon
.endmacro
.segment "SHINOBI_KERNEL"
ShSourceBounds:
 ldy ShState+$0300,x
 lda ShNativePoseOrdinal,y
 cmp #$ff
 beq ShBoundsUnsupported
 tay
 lda ShOriginalBoxId,y
 cmp #$ff
 beq ShBoundsUnsupported
 tay
 lda ShOriginalBoxOffsets,y
 clc
 adc #<ShOriginalBoxData
 sta ShScratch
 sta ShState+$0010
 lda #>ShOriginalBoxData
 adc #0
 sta ShScratch+1
 sta ShState+$0011
 jsr Sh_D98A                 ; genuine signed/clamped six-offset bbox math
 sec
 rts
ShBoundsUnsupported:
 clc
 rts

ShNativeShotContact:
 stx ShContactSlot
 lda #0
 sta ShContactResult
 txa
 eor ShState+$0553
 and #1
 jne ShShotReturn            ; exact original D3AD alternating source phase
 jsr ShSourceBounds
 jcc ShShotReturn            ; undefined original bbox is not invented
 lda ObjectOffset
 sta ShContactObject
 lda ShState+$0379,x
 clc
 adc ScreenLeft_X_Pos
 sta ShContactWorld
 lda ShState+$0384,x
 adc ScreenLeft_PageLoc
 sta ShContactWorld+1
 lda #5
 sta ShContactEnemy
ShShotEnemy:
 ldx ShContactEnemy
 lda Enemy_Flag,x
 jeq ShShotNext
 jmi ShShotNext              ; duplicate-owner classification remains pending
 lda Enemy_State,x
 and #$20
 jne ShShotNext
 lda Enemy_ID,x
 cmp #6
 bne :+
 lda Enemy_State,x
 cmp #2
 jcs ShShotNext
:
 lda Enemy_ID,x
 cmp #$24
 bcc ShShotRange
 cmp #$2b
 jcc ShShotNext              ; native platforms/firebars are not victims
 cmp #$2e
 jcs ShShotNext              ; items/flagpole/script objects are not victims
ShShotRange:
 lda Enemy_X_Position,x
 sec
 sbc ShContactWorld
 sta R0
 lda Enemy_PageLoc,x
 sbc ShContactWorld+1
 sta R1
 lda R0
 clc
 adc #64
 sta R0
 lda R1
 adc #0
 jne ShShotNext
 lda R0
 cmp #129
 jcs ShShotNext
 lda Enemy_Y_Position,x
 sec
 ldx ShContactSlot
 sbc ShState+$038f,x
 clc
 adc #48
 cmp #97
 jcs ShShotNext
 ldx ShContactEnemy
 stx ObjectOffset
 jsr RelativeEnemyPosition
 jsr GetEnemyOffscreenBits
 ShNativeFar GetEnemyBoundBox,Bank_GetEnemyBoundBox
 ldx ShContactEnemy
 txa
 asl
 asl
 clc
 adc #4
 tax
 ldy #3
ShSaveContactBox:
 lda BoundingBox_UL_Corner+28,y
 sta ShContactBox,y
 dey
 bpl ShSaveContactBox
 lda ShState+$0008
 sta BoundingBox_UL_Corner+28
 lda ShState+$000c
 sta BoundingBox_UL_Corner+29
 lda ShState+$000a
 sta BoundingBox_UL_Corner+30
 lda ShState+$000e
 sta BoundingBox_UL_Corner+31
 ldy #28
 jsr SprObjectCollisionCore
 php
 ldy #3
ShRestoreContactBox:
 lda ShContactBox,y
 sta BoundingBox_UL_Corner+28,y
 dey
 bpl ShRestoreContactBox
 plp
 bcc ShShotNext
 ldx ShContactEnemy
 stx ObjectOffset
 stx R1
 jsr HandleEnemyFBallCol      ; native defeat/score/SFX/drop transaction
 lda #1
 sta ShContactResult
 jmp ShShotDone
ShShotNext:
 dec ShContactEnemy
 jpl ShShotEnemy
ShShotDone:
 lda ShContactObject
 sta ObjectOffset
ShShotReturn:
 ldx ShContactSlot
 lda ShContactResult
 rts
ShNativeCombatEnd:
