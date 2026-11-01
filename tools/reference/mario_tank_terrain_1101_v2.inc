; Original Tank terrain semantics, adapted to returning native host callbacks.
; No donor TXS, actor coordinate proxy, head-item dispatch or borrowed NMI ZP.
; The conditional RAM2 A-window fixture aliases are NOT a RAM/ROM lease.
.import MtHostSelected,MtHostBooted
.import SelectedCharacter,MarioVariant,PlayerStatus,GameEngineSubroutine
.import Player_X_Position,Player_PageLoc,Player_Y_Speed
.import Block_State,Block_Metatile,Block_RepFlag,BlockMetasprite
.import Block_X_Position,Block_PageLoc,Block_PageLoc2,Block_Y_Position
.import Block_Y_HighPos,Block_Orig_YPos,Block_BBuf_Low,Block_OffscreenBits
.import SprDataOffset_Ctrl,NoiseSoundQueue,Square1SoundQueue
.import AreaType,BlockBounceTimer,CheckTopOfBlock
.import DigitModifier,PlayerScoreLastIndex,VRAM_Buffer_AddrCtrl
.import BlockBufferColli_Head,BlockBufferColli_Side
.import MmSideDispatchPrefix,SpawnBrickChunks
.import R0,R1,R2,R3,R4,R5,R6,R7
.import MtTerrainSave,MtTerrainY,MtTerrainA,MtRemovedTile,MtTerrainHeadMode
.export MtTerrainStart,MtTerrainHeadProbe,MtTerrainSideProbe
.export MtTerrainDestroyCell,MtTerrainTileChecks,MtTerrainEnd
.segment "MT_TERRAIN"

MtTerrainStart:
; The actual MtHostMovement hook resets the cell budget before native BG.
; RdNativeBGGate's MaaAfterBG call is Maaa-only and is deliberately untouched.

; Replace BillBGHeadConsumer's existing farcall MaaHead,jmp target. The native
; head query remains the geometry owner. A0 makes its existing caller proceed
; to feet, so source boots neither bounce nor enter item/question dispatch.
MtTerrainHeadProbe:
 php
 pha
 jsr MtHostBooted
 bcc MtTerrainHeadLegacy
 pla
 plp
 jsr BlockBufferColli_Head
 beq MtTerrainHeadDone
 cmp #$c2                    ; coins retain the actual native pickup owner
 beq MtTerrainHeadDone
 cmp #$c3
 beq MtTerrainHeadDone
 ldx Player_Y_Speed
 bpl MtTerrainHeadDone
 jsr MtTerrainTileChecks
 bcc MtTerrainHeadDestroy
 cmp #$26                    ; original protected head response
 beq MtTerrainHeadStop
 lda #2
 sta Square1SoundQueue
MtTerrainHeadStop:
 lda #1
 sta Player_Y_Speed
 lda #0
 rts
MtTerrainHeadDestroy:
 lda #1
 sta MtTerrainHeadMode
 lda R3
 jsr MtTerrainDestroyCell
 bcs MtTerrainHeadDone
 ; A busy host VRAM queue/two bouncing slots must never turn this into an
; ordinary item release. Defer destruction and hold the upward body here.
 lda #1
 sta Player_Y_Speed
 lda #0
MtTerrainHeadDone:
 rts
MtTerrainHeadLegacy:
 pla
 plp
 MtHostFar MaaHead
 rts

; Replace only the27B MmNativeSideShortcut body with an18B farcall plus9B
; padding, retaining MmSideDispatchTail and all subsequent public addresses.
; Other identities reproduce the actual shortcut's A/P and tail ownership.
MtTerrainSideProbe:
 php
 pha
 jsr MtHostSelected
 bcc MtTerrainOtherSide
 pla
 plp
 jsr BlockBufferColli_Side
 beq MtTerrainSideDone
 pha
 lda #0
 sta MtTerrainHeadMode
 pla
 jsr MtTerrainDestroyCell
MtTerrainSideDone:
 rts
MtTerrainOtherSide:
 pla
 plp
 php
 pha
 lda SelectedCharacter
 cmp #4
 beq MtTerrainGuestSide
 cmp #14
 beq MtTerrainGuestSide
 cmp #11
 bcs MtTerrainGuestSide
 pla
 plp
 jmp BlockBufferColli_Side
MtTerrainGuestSide:
 pla
 plp
 jmp MmSideDispatchPrefix

; A=the actual native nonzero head/side cell, R2/R5/R6/R7=that query's cell.
; C1,A0 means destroyed or this update's one-cell source budget already used.
; C0,A=original means native/inactive/protected/busy. Never call for feet.
; Restores all R0..R7 and query Y around actual score/VRAM/debris owners.
; No player coordinate, size, velocity or collision box is ever proxied.
MtTerrainDestroyCell:
 pha
 jsr MtTerrainTileChecks
 jcs MtTerrainCellNative
 lda GameEngineSubroutine
 cmp #8
 jne MtTerrainCellNative
 lda PlayerStatus
 cmp #2
 jne MtTerrainCellNative
 lda MtRemovedTile
 jne MtTerrainCellSpent
 lda VRAM_Buffer_AddrCtrl
 jne MtTerrainCellNative
 pla
 sta MtTerrainA
 sty MtTerrainY
 ldx #7
MtTerrainSaveProbe:
 lda R0,x
 sta MtTerrainSave,x
 dex
 bpl MtTerrainSaveProbe
 MtHostFar GuestClaimBlockSlot
 jcc MtTerrainCellBusy
 inc MtRemovedTile
 ldx SprDataOffset_Ctrl
 lda #$12
 sta Block_State,x
 lda #0
 sta Block_Metatile,x
 sta Block_RepFlag,x
 sta BlockMetasprite,x
 sta Block_OffscreenBits,x
 ldy MtTerrainSave+2
 sta (R6),y
 tya
 sta Block_Orig_YPos,x
 clc
 adc #$20
 sta Block_Y_Position,x
 lda MtTerrainSave+6
 sta Block_BBuf_Low,x
 lda MtTerrainSave+5
 and #$f0
 sta Block_X_Position,x
 lda MtTerrainSave+5
 cmp Player_X_Position
 lda Player_PageLoc
 bcs MtTerrainPageReady
 clc
 adc #1
MtTerrainPageReady:
 sta Block_PageLoc,x
 sta Block_PageLoc2,x
 lda #1
 sta Block_Y_HighPos,x
 ; Authentic source DoBlockRemove uses these owners directly. Calling the
; ordinary head core/BrickShatter would additionally release an item, bump
; the player, and possibly collect the coin above a side-destroyed block.
 lda MtTerrainHeadMode
 beq MtTerrainEraseSide
 lda #1
 sta Block_RepFlag,x
 lda #$10
 sta BlockBounceTimer
 lda AreaType
 beq MtTerrainHeadCoinAbove
 MtHostFar DestroyBlockMetatile
MtTerrainHeadCoinAbove:
 jsr CheckTopOfBlock
 jmp MtTerrainEmitChunks
MtTerrainEraseSide:
 MtHostFar RemoveCoin_Axe
MtTerrainEmitChunks:
 ldx SprDataOffset_Ctrl
 jsr SpawnBrickChunks
 lda #1
 sta NoiseSoundQueue
 lda #5
 sta DigitModifier+PlayerScoreLastIndex
 MtHostFar AddToScore
 lda SprDataOffset_Ctrl
 eor #1
 sta SprDataOffset_Ctrl
 jsr MtTerrainRestoreProbe
 lda #0
 sec
 rts
MtTerrainCellBusy:
 jsr MtTerrainRestoreProbe
 lda MtTerrainA
 clc
 rts
MtTerrainCellSpent:
 pla
 lda #0
 sec
 rts
MtTerrainCellNative:
 pla
 clc
 rts
MtTerrainRestoreProbe:
 ldx #7
MtTerrainRestoreLoop:
 lda MtTerrainSave,x
 sta R0,x
 dex
 bpl MtTerrainRestoreLoop
 ldy MtTerrainY
 ldx #0
 rts

; Original49B TileChecks/ForceSolidBlocks with its original climb predicate.
; Host MTileAttribute is deliberately not substituted for donor thresholds.
MtTerrainTileChecks:
 jsr MtTerrainCheckClimb
 bcs MtTerrainProtected
 cmp #$c2
 beq MtTerrainProtected
 cmp #$c3
 beq MtTerrainProtected
 cmp #$6d
 beq MtTerrainProtected
 cmp #$67
 beq MtTerrainProtected
 cmp #$68
 beq MtTerrainProtected
 cmp #$c5
 beq MtTerrainProtected
 cmp #$1c
 beq MtTerrainProtected
 cmp #$1f
 beq MtTerrainProtected
 cmp #$6b
 beq MtTerrainProtected
 cmp #$6c
 beq MtTerrainProtected
 clc
 rts
MtTerrainProtected:
 sec
 rts
MtTerrainCheckClimb:
 pha
 and #$c0
 asl
 rol
 rol
 tax
 pla
 cmp MtTerrainClimbUpper,x
 rts
MtTerrainClimbUpper:
 .byte $24,$6e,$8a,$c6       ; BRIDGE_METATILE=$89 in authenticated source
MtTerrainEnd:
