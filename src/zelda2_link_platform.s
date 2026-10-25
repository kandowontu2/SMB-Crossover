; Original body rectangle E975 is distinct from the terrain probes.
.pushseg
.segment "LM_CORE"
.proc LmBoundingBoxGate
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_LINK
 bne Legacy
 lda Z2Variant
 beq Legacy
 pla
 plp
 farcall Z2OriginalBodyBox
 farcall X5EasyFootBox,jmp
Legacy:pla
 plp
 jmp Z2LegacyBoundingBoxGate
.endproc

.segment "SOPHIA_BODY_COLD"
.macro Z2PlatformBodyGate Name,Own,Legacy
.proc Name
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_LINK
 bne Original
 lda Z2Variant
 beq Original
 pla
 plp
 farcall Own,jmp
Original:pla
 plp
 jmp Legacy
.endproc
.endmacro
Z2PlatformBodyGate RyuSourceBodyPlatformPrepare,Z2PlatformBodyPrepare,Z2LegacyPlatformPrepare
Z2PlatformBodyGate RyuSourceBodyPlatformFinish,Z2PlatformBodyFinish,Z2LegacyPlatformFinish

.segment "Z2_COLD"
; Native static floor quantization is retained except for an actual preceding
; SMB platform attachment. SaveX/Y and nativeC before checking object slots;
; the following original jump impulse depends on that carry bit.
.proc Z2PlatformGroundY
 php
 lda Player_Y_Position
 and #15
 beq NativeAligned
 phx
 phy
 jsr Z2HasPlatformSupport
 bcs Supported
 ply
 plx
NativeAligned:
 plp
 lda Player_Y_Position
 and #$f0
 sta Player_Y_Position
 rts
Supported:
 ply
 plx
 plp
 lda Player_Y_Position
 rts
.endproc
.proc Z2HasPlatformSupport
 lda GameEngineSubroutine
 cmp #8
 jne No
 lda Player_State
 jne No
 lda Player_Y_HighPos
 cmp #1
 jne No
 lda Player_Y_Position
 clc
 adc #32
 jcs No
 sta Z2BodyScratch+8
 ldx #5
Slot:
 lda Enemy_Flag,x
 jeq Next
 lda Enemy_Y_HighPos,x
 cmp #1
 jne Next
 lda Enemy_ID,x
 cmp #$24
 jcc Next
 cmp #$2d
 jcs Next
 cmp #$24
 beq Balance
 cmp #$2b
 bcs Small
 txa
 cmp PlatformCollisionFlag,x
 jne Next
 lda Enemy_Y_Position,x
 jmp CompareY
Balance:
 ; A native balance pair stores the contacted sibling slot on its parent.
 ; The sibling itself has state$ff and owns no collision pass. Resolve the
 ; exact referenced active platform; never infer support from matchingY.
 lda Enemy_State,x
 cmp #6
 jcs Next
 lda PlatformCollisionFlag,x
 cmp #6
 jcs Next
 tay
 txa
 cmp PlatformCollisionFlag,x
 beq BalanceTarget
 lda Enemy_State,x
 cmp PlatformCollisionFlag,x
 jne Next
BalanceTarget:
 lda Enemy_Flag,y
 jeq Next
 lda Enemy_ID,y
 cmp #$24
 jne Next
 lda Enemy_Y_HighPos,y
 cmp #1
 jne Next
 lda Enemy_Y_Position,y
 jmp CompareY
Small:
 lda PlatformCollisionFlag,x
 cmp #2
 beq First
 cmp #1
 jne Next
 lda AreaPointer
 cmp #$62
 bne VanillaSecond
 lda WorldNumber
 cmp #1
 beq SourceSecond
 cmp #4
 bne VanillaSecond
SourceSecond:lda Enemy_State,x
 jmp CompareY
VanillaSecond:lda Enemy_Y_Position,x
 clc
 adc #128
 jmp CompareY
First:lda Enemy_Y_Position,x
CompareY:cmp Z2BodyScratch+8
 beq Yes
Next:dex
 jpl Slot
No:clc
 rts
Yes:sec
 rts
.endproc
.proc Z2PlatformBodyPrepare
 RP_Save
 lda SelectedCharacter
 cmp #CHARACTER_LINK
 bne Done
 lda Z2Variant
 beq Done
 jsr RelativePlayerPosition
 ldx #0
 jsr BoundingBoxCore
 lda Z2ActiveSpells
 and #8
 beq Normal
 lda Player_Rel_XPos
 cmp #240
 bcs FairyY
 clc
 adc #3
 sta BoundingBox_UL_XPos
 lda Player_Rel_XPos
 clc
 adc #13
 sta BoundingBox_LR_Corner
FairyY:
 lda Player_Rel_YPos
 clc
 adc #8
 sta BoundingBox_UL_YPos
 lda Player_Rel_YPos
 clc
 adc #26
 bne Bottom
Normal:
 lda Player_Rel_YPos
 sta BoundingBox_UL_YPos
 clc
 adc #32
Bottom:sta BoundingBox_LR_Corner+1
Done:RP_Restore
 rts
.endproc
.proc Z2PlatformBodyFinish
 RP_Save
 lda SelectedCharacter
 cmp #CHARACTER_LINK
 bne Done
 lda Z2Variant
 beq Done
 jsr RelativePlayerPosition
 jsr Z2OriginalBodyBox
 farcall X5EasyFootBox
Done:RP_Restore
 rts
.endproc
.proc Z2SmallPlatformCollision
 jsr Z2PlatformBodyPrepare
 jsr Z2NativeSmallPlatformCollision
 jsr Z2PlatformBodyFinish
 rts
.endproc
.proc Z2OriginalBodyBox
 ldx #0
 jsr BoundingBoxCore
 ; Preserve native horizontal clipping at the viewport edges. The source
 ; original itself bounds Link to a smaller viewport; SMB permits edge wrap.
 lda Player_Rel_XPos
 cmp #240
 bcs Vertical
 clc
 adc #14
 sta BoundingBox_LR_Corner
Vertical:
 lda Player_Rel_YPos
 ldx Z2NativeShield
 bne Top
 clc
 adc #4
Top:sta BoundingBox_UL_YPos
 lda Player_Rel_YPos
 clc
 adc #29
 sta BoundingBox_LR_Corner+1
 ldx #0
 ldy #0
 rts
.endproc

.proc Z2PostBGBodyBridge
 lda SelectedCharacter
 cmp #CHARACTER_SAMUS
 beq Handle
 cmp #CHARACTER_LINK
 bne Done
Handle:jsr Z2AfterBGDispatch
 jsr RelativePlayerPosition
 ldx #0
 jsr BoundingBoxCore
 lda SelectedCharacter
 cmp #CHARACTER_LINK
 bne Done
 lda Z2Variant
 beq Done
 jmp Z2OriginalBodyBox
Done:rts
.endproc

; A is the native platform ordinate. Small lifts arrive after their original
; first/second-platform offset and BIT skip; all large platforms load it here.
.proc Z2PositionOnPlatform
 ldy GameEngineSubroutine
 cpy #$0b
 beq Done
 ldy Enemy_Y_HighPos,x
 cpy #1
 bne Done
 pha
 lda SelectedCharacter
 cmp #CHARACTER_LINK
 bne Native
 lda Z2Variant
 beq Native
 lda Z2ActiveSpells
 and #8
 beq Native
 pla
 sec
 sbc #26
 jmp Store
Native:pla
 sec
 sbc #32
Store:sta Player_Y_Position
 tya
 sbc #0
 sta Player_Y_HighPos
 lda #0
 sta Player_Y_Speed
 sta Player_Y_MoveForce
 jsr Z2RefreshPlatformBody
Done:rts
.endproc
.proc Z2RefreshPlatformBody
 RP_Save
 lda SelectedCharacter
 cmp #CHARACTER_LINK
 bne Done
 lda Z2Variant
 beq Done
 jsr RelativePlayerPosition
 jsr Z2OriginalBodyBox
Done:RP_Restore
 rts
.endproc
.popseg
.include "zelda2_small_platform_native.inc"
