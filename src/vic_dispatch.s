.pushseg
.segment "VIC_WORLD"
.macro VvDispatch Name,Own,Previous
.proc Name
 jsr VvIsActive
 bcc Legacy
 jmp Own
Legacy:farcall Previous,jmp
.endproc
.endmacro
VvDispatch VvMovementDispatch,VvMovement,TnMovementDispatch
VvDispatch VvGraphicsDispatch,VvGraphics,TnGraphicsDispatch
VvDispatch VvPortraitDispatch,VvPortrait,TnPortraitDispatch
VvDispatch VvWeaponsDispatch,VvWeapons,TnWeaponsDispatch
VvDispatch VvDrawDispatch,VvDraw,TnDrawDispatch
VvDispatch VvInjuryDispatch,VvInjury,TnInjuryStartDispatch
VvDispatch VvBodyDispatch,VvBody,TnBodyDispatch
VvDispatch VvDeathDispatch,VvDeathUpdate,TnDeathDispatch
VvDispatch VvDeathStartDispatch,VvDeathStart,CdInventoryDeathDispatch
.proc VvUiDispatch
 jsr VvIsActive
 bcc Legacy
 lda OperMode
 cmp #1
 bne Done
 lda GameEngineSubroutine
 cmp #8
 bne Done
 jmp VvHud
Done:rts
Legacy:farcall Cv3UiGate,jmp
.endproc
.proc VvResetDispatch
 farcall TnResetDispatch
 jmp VvReset
.endproc
.proc VvInjuryStatusDispatch
 jsr VvIsActive
 bcc Legacy
 ldx #1
 txa
 rts
Legacy:farcall TnInjuryStatusDispatch,jmp
.endproc
.proc VvBoxDispatch
 cmp #18
 bne Legacy
 ldy #17
 rts
Legacy:farcall TnBoxDispatch,jmp
.endproc
.proc VvBoundingBoxGate
 php
 pha
 jsr VvIsActive
 bcs Native
 pla
 plp
 farcall TnBoundingBoxGate,jmp
Native:
 pla
 plp
 jsr BoundingBoxCore
 lda VvVariant
 beq GradiusPoint
 lda PnType
 cmp #8
 bne SmallCore
 lda Player_Rel_XPos
 sec
 sbc #5
 sta BoundingBox_UL_XPos
 clc
 adc #26
 sta BoundingBox_LR_Corner
 lda Player_Rel_YPos
 sec
 sbc #5
 sta BoundingBox_UL_YPos
 clc
 adc #26
 sta BoundingBox_LR_Corner+1
 ldx #0
 ldy #0
 rts
SmallCore:
 ; Native Parodius type1 uses a6x6 core at its actor origin. That origin is
 ; Player+(8,8), after translating into SMB's world/HUD coordinates.
 lda Player_Rel_XPos
 clc
 adc #5
 sta BoundingBox_UL_XPos
 clc
 adc #6
 sta BoundingBox_LR_Corner
 lda Player_Rel_YPos
 clc
 adc #5
 sta BoundingBox_UL_YPos
 clc
 adc #6
 sta BoundingBox_LR_Corner+1
 ldx #0
 ldy #0
 rts
GradiusPoint:
 ; Original Gradius $C105/$C10D use a single ship point X+4,Y+8.
 ; Its engine origin is translated(-8,+24) below the32px SMB HUD.
 lda Player_Rel_XPos
 clc
 adc #12
 sta BoundingBox_UL_XPos
 sta BoundingBox_LR_Corner
 lda Player_Rel_YPos
 clc
 adc #16
 sta BoundingBox_UL_YPos
 sta BoundingBox_LR_Corner+1
 ldx #0
 ldy #0
 rts
.endproc
.proc VvAdderDispatch
 cmp #18
 bne Legacy
 ldy #8
 sec
 rts
Legacy:farcall TnAdderDispatch,jmp
.endproc
.proc VvPrepareDispatch
 pha
 jsr VvIsActive
 bcc Legacy
 pla
 lda #$fc
 sta InvPickup,x
 lda #$ff
 sta InvPickupOwner,x
 lda PowerUpType,x
 cmp #2
 bcs Done
 lda #1
 sta PowerUpType,x
Done:rts
Legacy:
 pla
 farcall TnPreparePickupDispatch,jmp
.endproc
.proc VvPickupDispatch
 jsr VvIsActive
 bcc Legacy
 lda PowerUpType,x
 cmp #2
 bcs Legacy
 phx
 jsr VvTake
 plx
 phx
 jsr EraseEnemyObject
 plx
 lda #6
 jsr SetupFloateyNumber
 rts
Legacy:farcall TnPickupDispatch,jmp
.endproc
.proc VvStatusName
 pha
 jsr VvIsActive
 bcs Own
 pla
 farcall CdStatusNameDispatch,jmp
Own:
 pla
 cmp #0
 bne Done
 phx
 phy
 lda VvVariant
 sta VvTemp
 asl
 asl
 asl
 sec
 sbc VvTemp
 clc
 adc #6
 tax
 ldy #6
Loop:
 lda Text,x
 sta VRAM_Buffer1+11,y
 dex
 dey
 bpl Loop
 ply
 plx
 lda #0
Done:rts
Text:.byte "VIC VIP","OCTOPUS","TWINBEE","PENTARO"
.endproc
.popseg
