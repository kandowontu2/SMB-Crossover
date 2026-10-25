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
