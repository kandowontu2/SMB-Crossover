; Contact-only Karnov projectiles. Original actor/weapon motion remains owner.
; Authenticated A3/C2 entry; service4 and34 may alias this once/epoch worker.
; KrCombatReset must run at scene construction and an explicit shot clear.
.import KrState,KrReady,KrHaveEpoch,KrLastEpoch,KrCameraLo,KrCameraHi
.import SelectedCharacter,FrameCounter,OperMode,GamePauseStatus
.import ScreenLeft_X_Pos,ScreenLeft_PageLoc,ObjectOffset,Enemy_Flag,Enemy_State
.import Enemy_ID,Enemy_X_Position,Enemy_PageLoc,Enemy_Y_Position
.import PlayerSize,CrouchingFlag,Player_X_Position,Player_PageLoc
.import Player_Y_Position,Player_Y_HighPos,Player_Y_Speed,MmBlockAttack
.import BoundingBox_UL_Corner,Block_Buffer_1,MmSolidTerrain,MTileAttribute
.import GetBlockBufferAddr,BlockBumpedChk,GuestClaimBlockSlot,NativeRarePlayerHeadCollisionCore
.import RelativeEnemyPosition,GetEnemyOffscreenBits,GetEnemyBoundBox
.import SprObjectCollisionCore,HandleEnemyFBallCol,Square1SoundQueue
.import FarCallCommon,SafecallA_SMC,FarcallJmpTarget_SMC
.import CurrentBank
.importzp R0,R1,R2,R3,R4,R5,R6,R7,GameEngineSubroutine
.import KC_GetBlockBufferAddr_BANK,KC_BlockBumpedChk_BANK
.import KC_GuestClaimBlockSlot_BANK,KC_NativeRarePlayerHeadCollisionCore_BANK
.import KC_RelativeEnemyPosition_BANK,KC_GetEnemyOffscreenBits_BANK
.import KC_GetEnemyBoundBox_BANK,KC_SprObjectCollisionCore_BANK
.import KC_HandleEnemyFBallCol_BANK
.export KrCombat,KrCombatReset,KrCombatRom,KrCombatKernelEnd,KrCombatRomEnd

KC_SAVE=$c840                 ; A/X/Y/P and foreground R0..7, never NMI0..2
KC_OBJECT=$c84c
KC_HAVE=$c84d
KC_EPOCH=$c84e
KC_SLOT=$c84f
KC_WORLD_X=$c850
KC_WORLD_PAGE=$c851
KC_SCREEN_X=$c852
KC_Y=$c853
KC_BOOM_MASK=$c854
KC_TILE=$c855
KC_ROW=$c856
KC_PTR=$c857
KC_ENEMY=KC_TILE              ; block and enemy workers run sequentially
KC_CANON=KC_ROW
KC_ENEMY_BIT=KC_PTR
KC_PLAYER=$c859               ; seven exact player fields for native block proxy
KC_BOX=KC_PLAYER              ; four borrowed native fireball-box bytes
KC_END=$c860                  ;32-byte selected C2 context [C840,C860)

.macro KcFar Target,Bank
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #<Bank
 jsr FarCallCommon
.endmacro
.macro KcFixed Target
 .assert Target >= $8000 .and Target < $a000,lderror,"Native fixed-window import moved"
 jsr Target
.endmacro

.pushseg
.segment "KR_COMBAT_KERNEL"
KrCombatReset:
 lda #0
 sta KC_HAVE
 sta KC_BOOM_MASK
 rts
KrCombat:
 jmp KrCombatRom             ; proposed selected C2 code, explicit fixture load
KrCombatKernelEnd:
.popseg

.pushseg
.segment "KR_COMBAT_ROM"
KrCombatRom:
 sta KC_SAVE
 stx KC_SAVE+1
 sty KC_SAVE+2
 php
 pla
 sta KC_SAVE+3
 ldx #7
KcSaveZp:
 lda R0,x
 sta KC_SAVE+4,x
 dex
 bpl KcSaveZp
 lda ObjectOffset
 sta KC_OBJECT
 lda SelectedCharacter
 cmp #34                    ; actual delivered Karnov ID, never raw7/Rygar
 jne KcDone
 lda KrReady
 cmp #$a7
 jne KcDone
 lda OperMode
 cmp #1
 jne KcDone
 lda GameEngineSubroutine
 cmp #8
 jne KcDone
 lda GamePauseStatus
 and #1
 jne KcDone
 lda KrHaveEpoch
 jeq KcDone
 lda KrLastEpoch
 cmp FrameCounter
 jne KcDone                 ; movement/source weapons must precede contacts
 lda KC_HAVE
 beq KcNewEpoch
 lda KC_EPOCH
 cmp FrameCounter
 jeq KcDone                 ;4+34 cannot apply a second receipt this update
KcNewEpoch:
 lda FrameCounter
 sta KC_EPOCH
 lda #1
 sta KC_HAVE
 lda KrState+$65
 and #15
 cmp #8
 beq KcBoomActive
 cmp #3
 jcs KcDone
 lda #0
 sta KC_BOOM_MASK
 beq KcBegin
KcBoomActive:
 lda KrState+$6e
 bmi KcBegin
 lda #0
 sta KC_BOOM_MASK
KcBegin:
 lda #0
 sta KC_SLOT
KcShot:
 lda KrState+$65
 and #15
 cmp #8
 beq KcColumnReady
 sta R0
 asl
 clc
 adc R0
 sta R0                     ; original gear0/1/2 permits columns0/3/6
 lda KC_SLOT
KcColumnMod:
 cmp #9
 bcc KcColumnCheck
 sbc #9
 bcs KcColumnMod
KcColumnCheck:
 cmp R0
 bcc KcColumnReady
 beq KcColumnReady
 jmp KcNext
KcColumnReady:
 ldx KC_SLOT
 lda KrState+$6e,x
 jpl KcNext
 and #$30
 jne KcNext                 ; genuine original impact animation is not damage
 lda KrState+$6f,x
 clc
 adc KrCameraLo
 sta KC_WORLD_X
 lda KrCameraHi
 adc #0
 sta KC_WORLD_PAGE
 lda KC_WORLD_X
 sec
 sbc ScreenLeft_X_Pos
 sta KC_SCREEN_X
 lda KC_WORLD_PAGE
 sbc ScreenLeft_PageLoc
 bne KcNext                 ; viewport clipping without low-byte wrap contacts
 lda KrState+$70,x
 sta KC_Y
 cmp #$20
 bcc KcNext
 cmp #$f0
 bcs KcNext
 jsr KrCombatBlock
 beq KcEnemies
 jsr KcImpact
 bcs KcNext
KcEnemies:
 lda KC_WORLD_X
 sec
 sbc ScreenLeft_X_Pos
 sta KC_SCREEN_X            ; block proxy used this byte for MmBlockAttack
 lda #5
 sta KC_ENEMY
KcEnemyLoop:
 ldx KC_ENEMY
 lda Enemy_Flag,x
 beq KcEnemyNext
 lda Enemy_State,x
 and #$20
 bne KcEnemyNext
 ; Cheap16-bit world broadphase before the genuine native box producer.
 lda Enemy_X_Position,x
 sec
 sbc KC_WORLD_X
 sta R0
 lda Enemy_PageLoc,x
 sbc KC_WORLD_PAGE
 sta R1
 lda R0
 clc
 adc #32
 sta R0
 lda R1
 adc #0
 bne KcEnemyNext
 lda R0
 cmp #65
 bcs KcEnemyNext
 lda Enemy_Y_Position,x
 sec
 sbc KC_Y
 clc
 adc #48
 cmp #97
 bcs KcEnemyNext
 jsr KrCombatVictim
 beq KcEnemyNext
 jsr KcImpact
 bcs KcNext
KcEnemyNext:
 dec KC_ENEMY
 bpl KcEnemyLoop
KcNext:
 lda KrState+$65
 and #15
 cmp #8
 beq KcDone                 ; boomerang's phase bytes are not extra shot slots
 lda KC_SLOT
 clc
 adc #3
 sta KC_SLOT
 cmp #27
 jcc KcShot
KcDone:
 lda KC_OBJECT
 sta ObjectOffset
 ldx #7
KcRestoreZp:
 lda KC_SAVE+4,x
 sta R0,x
 dex
 bpl KcRestoreZp
 lda KC_SAVE+3
 pha
 lda KC_SAVE
 ldx KC_SAVE+1
 ldy KC_SAVE+2
 plp
 sec
 rts
KcImpact:
 lda KrState+$65
 and #15
 cmp #8
 beq KcKeepBoom
 ldx KC_SLOT
 lda KrState+$6e,x
 and #$c0
 ora #$18                    ; original AFCA/A9EE/CD4B impact conversion
 sta KrState+$6e,x
 sec
 rts
KcKeepBoom:clc
 rts
KrCombatBlock:
 ; A center-point native cell query; all motion and expiry remain source-owned.
 lda KC_Y
 clc
 adc #4
 and #$f0
 sec
 sbc #$20
 sta KC_ROW
 sta R2
 lda KC_WORLD_X
 clc
 adc #4
 sta R0
 lda KC_WORLD_PAGE
 adc #0
 and #1
 asl
 asl
 asl
 asl
 sta R1
 lda R0
 lsr
 lsr
 lsr
 lsr
 ora R1
 KcFixed GetBlockBufferAddr
 lda R6
 sta KC_PTR
 lda R7
 sta KC_PTR+1
 ldy KC_ROW
 lda (R6),y
 sta KC_TILE
 beq KcNoBlock
 cmp #$23
 beq KcNoBlock
 cmp #$26
 beq KcNoBlock
 cmp #$c2
 beq KcNoBlock
 cmp #$c3
 beq KcNoBlock
 cmp #$5f
 beq KcNoBlock
 cmp #$60
 beq KcNoBlock
 KcFixed BlockBumpedChk
 bcs KcActivateBlock
 lda KC_TILE
 cmp #$51
 beq KcActivateBlock
 cmp #$52
 bne KcPlainSolid
 ; Shared underground52 is brick only when parser's terrain flag is clear.
 lda KC_PTR
 clc
 adc #<(MmSolidTerrain-Block_Buffer_1)
 sta R0
 lda KC_PTR+1
 adc #>(MmSolidTerrain-Block_Buffer_1)
 sta R1
 ldy KC_ROW
 lda (R0),y
 beq KcActivateBlock
KcPlainSolid:
 ldy KC_TILE
 lda MTileAttribute,y
 and #$01                   ; actual MTILE_SOLID, asserted by binding producer
 beq KcNoBlock
 lda #2                     ; native Sfx_Bump, asserted by binding producer
 sta Square1SoundQueue
 lda #1
 rts
KcNoBlock:lda #0
 rts
KcActivateBlock:
 KcFar GuestClaimBlockSlot,KC_GuestClaimBlockSlot_BANK
 jcc KcBlocked              ; busy block slots consume contact, never overwrite
 lda Player_X_Position
 sta KC_PLAYER
 lda Player_PageLoc
 sta KC_PLAYER+1
 lda Player_Y_Position
 sta KC_PLAYER+2
 lda Player_Y_HighPos
 sta KC_PLAYER+3
 lda PlayerSize
 sta KC_PLAYER+4
 lda CrouchingFlag
 sta KC_PLAYER+5
 lda Player_Y_Speed
 sta KC_PLAYER+6
 lda MmBlockAttack
 sta KC_SCREEN_X             ; recomputed before the later enemy-box phase
 lda KC_WORLD_X
 clc
 adc #4
 and #$f0
 sta Player_X_Position
 lda KC_WORLD_PAGE
 adc #0
 sta Player_PageLoc
 lda KC_ROW
 clc
 adc #$20
 sta Player_Y_Position
 lda #1
 sta Player_Y_HighPos
 sta MmBlockAttack
 lda #0
 sta PlayerSize
 sta CrouchingFlag
 lda KC_PTR
 sta R6
 lda KC_PTR+1
 sta R7
 lda KC_ROW
 sta R2
 ; The native effect core is the owner; its BillRare ABI capture wrapper is
 ; unnecessary because this caller restores the complete foreground ABI.
 ; We execute C2, so a direct A-window lease needs only its prior shadow.
 ; The outer authenticated service owns complete SMC/AXYP restoration.
 lda CurrentBank
 pha
 lda #<KC_NativeRarePlayerHeadCollisionCore_BANK
 sta CurrentBank
 sta $5115
 lda KC_TILE
 jsr NativeRarePlayerHeadCollisionCore
 pla
 sta CurrentBank
 sta $5115
 lda KC_SCREEN_X
 sta MmBlockAttack
 lda KC_PLAYER
 sta Player_X_Position
 lda KC_PLAYER+1
 sta Player_PageLoc
 lda KC_PLAYER+2
 sta Player_Y_Position
 lda KC_PLAYER+3
 sta Player_Y_HighPos
 lda KC_PLAYER+4
 sta PlayerSize
 lda KC_PLAYER+5
 sta CrouchingFlag
 lda KC_PLAYER+6
 sta Player_Y_Speed
KcBlocked:lda #1
 rts

KrCombatVictim:
 ldx KC_ENEMY
 lda Enemy_ID,x
 cmp #6                     ; Goomba: native stomped-state2 is already defeated
 bne :+
 lda Enemy_State,x
 cmp #2
 jcs KcNoVictim
:lda Enemy_ID,x
 cmp #$24
 bcc KcVictimClass
 cmp #$2b
 jcc KcNoVictim
KcVictimClass:
 stx KC_CANON
 lda Enemy_Flag,x
 bpl KcVictimCanonical
 and #15
 cmp #6
 jcs KcNoVictim
 sta KC_CANON
 tay
 lda Enemy_ID,y
 cmp #$2d                   ; true Bowser duplicate; native damage resolves head
 jne KcNoVictim
KcVictimCanonical:
 ldy KC_CANON
 lda KcEnemyBits,y
 sta KC_ENEMY_BIT
 lda KrState+$65
 and #15
 cmp #8
 bne KcVictimPrepare
 lda KC_BOOM_MASK
 and KC_ENEMY_BIT
 jne KcNoVictim
KcVictimPrepare:
 stx ObjectOffset
 KcFixed RelativeEnemyPosition
 KcFixed GetEnemyOffscreenBits
 KcFar GetEnemyBoundBox,KC_GetEnemyBoundBox_BANK
 ldx KC_ENEMY
 txa
 asl
 asl
 clc
 adc #4
 tax
 ldy #3
KcSaveBox:
 lda BoundingBox_UL_Corner+28,y
 sta KC_BOX,y
 dey
 bpl KcSaveBox
 lda KC_SCREEN_X
 sta BoundingBox_UL_Corner+28
 clc
 adc #7
 sta BoundingBox_UL_Corner+30
 lda KC_Y
 sta BoundingBox_UL_Corner+29
 clc
 adc #7
 sta BoundingBox_UL_Corner+31
 ldy #28
 KcFixed SprObjectCollisionCore
 php
 ldy #3
KcRestoreBox:
 lda KC_BOX,y
 sta BoundingBox_UL_Corner+28,y
 dey
 bpl KcRestoreBox
 plp
 bcc KcNoVictim
 ldx KC_ENEMY
 stx ObjectOffset
 stx R1
 KcFixed HandleEnemyFBallCol
 lda KrState+$65
 and #15
 cmp #8
 bne KcVictimHit
 lda KC_BOOM_MASK
 ora KC_ENEMY_BIT
 sta KC_BOOM_MASK
KcVictimHit:lda #1
 rts
KcNoVictim:lda #0
 rts
KcEnemyBits:.byte 1,2,4,8,16,32
KrCombatRomEnd:
.popseg
