; Two native vertical platform actors for Jay's 52.5-pixel source jump.
.setcpu "6502"
.segment "HELPERS"
StepHelpers:
 php
 pha
 lda HelperSeen
 cmp #3
 beq QuickReturn
 lda AreaType
 cmp #1
 bne QuickReturn
 lda WorldNumber
 ora LevelNumber
 ora TimerControl
 bne QuickReturn
 lda ScreenLeftPage
 cmp #1
 bcc QuickReturn
 cmp #3
 bcc SaveContext
QuickReturn:
 pla
 plp
 rts
SaveContext:
 txa
 pha
 tya
 pha
 lda ObjectOffset
 pha
 lda $03
 pha
 lda $04
 pha
 lda $05
 pha
 lda $06
 pha
 lda $07
 pha
 lda $08
 pha
 lda $09
 pha
 lda $0a
 pha
 ldy #1
NextPlacement:
 sty HelperIndex
 lda PlacementMask,y
 and HelperSeen
 bne SkipPlacement
 lda PlacementXLo,y
 sec
 sbc ScreenLeftX
 sta HelperDelta
 lda PlacementPage,y
 sbc ScreenLeftPage
 cmp #1
 bne SkipPlacement
 lda HelperDelta
 cmp #32
 bcs SkipPlacement
 ldx #5
FindFreeActor:
 lda EnemyFlag,x
 beq SpawnPlatform
 dex
 bpl FindFreeActor
 jmp SkipPlacement
SpawnPlatform:
 stx ObjectOffset
 lda PlacementXLo,y
 sta EnemyX,x
 lda PlacementPage,y
 sta EnemyPage,x
 lda #192
 sta EnemyY,x
 lda #1
 sta EnemyYHigh,x
 sta EnemyFlag,x
 lda #$25
 sta EnemyID,x
 lda #$4f
 sta $016c
 lda #$a7
 sta $016d
 lda #$82
 jsr $015a
 ldy HelperIndex
 lda PlacementCenterY,y
 sta PlatformCenterY,x
 lda #5
 sta EnemyBox,x
 lda PlacementMask,y
 ora HelperSeen
 sta HelperSeen
SkipPlacement:
 ldy HelperIndex
 dey
 bmi ReturnHelpers
 jmp NextPlacement
ReturnHelpers:
 pla
 sta $0a
 pla
 sta $09
 pla
 sta $08
 pla
 sta $07
 pla
 sta $06
 pla
 sta $05
 pla
 sta $04
 pla
 sta $03
 pla
 sta ObjectOffset
 pla
 tay
 pla
 tax
 pla
 plp
 rts
ResetHelpers:
 lda #0
 sta HelperSeen
 sta DropStage
 rts
PlacementXLo:
 .byte $b0,$70
PlacementPage:
 .byte 2,3
PlacementCenterY:
 .byte 169,161
PlacementMask:
 .byte 1,2
