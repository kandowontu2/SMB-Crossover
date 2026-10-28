; Successor: undo only actual horizontal penetration. Pre-existing ceiling
; overlap during native hurt response may not teleport the body sideways.
; RCR horizontal separation before the native feet-first terrain consumer.
; Uses actual native block queries. It never invokes block effects twice.
; The previous Y is captured immediately before RcIntegrate by the private host.
RcTerrainOldY=$5c50
RcWallDirection=$5c51
RcWallCursor=$5c52
.export RcTerrainWallPrepass,RcTerrainOldY
.pushseg
.segment "RIVER_CITY_CORE"
.proc RcTerrainWallPrepass
 lda SelectedCharacter
 cmp #CHARACTER_RIVER_CITY
 jne Done
 lda DisableCollisionDet
 jne Done
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda Player_Y_HighPos
 cmp #1
 jne Done
 lda Player_Y_Position
 cmp #8
 jcc Done
 cmp #207
 jcs Done
 lda MmVX+2
 bmi Left
 ora MmVX+1
 jeq Done
 lda #1
 sta RcWallDirection
 ldy #5
 bne Start
Left:
 lda #2
 sta RcWallDirection
 ldy #3
Start:
 sty RcWallCursor
 lda CrouchingFlag
 bne Lower
 lda Player_Y_Position
 cmp #24                    ; upper side query must stay below the HUD
 bcc Lower
 jsr Sample
 bcs Separate
Lower:
 ldy RcWallCursor
 iny
 jsr Sample
 jcc Done
Separate:
 ; R5 is the native sampled X including the side inset. Compute the same
 ; page carry, then place the side inset one pixel outside that solid cell.
 lda #0
 ldx RcWallDirection
 cpx #1
 bne :+
 lda #13
 bne Inset
:
 lda #2
Inset:
 clc
 adc Player_X_Position
 lda Player_PageLoc
 adc #0
 sta RcTemp2
 lda R5
 and #$f0
 ldx RcWallDirection
 cpx #1
 bne LeftPosition
 sec
 sbc #14
 php                          ; retain candidate page borrow
 tay
 sec
 sbc RcOldX                   ; candidate must be within this horizontal step
 sta RcWallCursor
 lda Player_X_Position
 sec
 sbc RcOldX
 cmp RcWallCursor
 bcc TooDeep
 plp
 tya
 sta Player_X_Position
 lda RcTemp2
 sbc #0
 jmp Page
LeftPosition:
 clc
 adc #14
 php                          ; retain candidate page carry
 tay
 lda RcOldX
 sec
 sbc Player_X_Position
 sta RcWallCursor
 tya
 sec
 sbc Player_X_Position
 cmp RcWallCursor
 bcc AcceptLeft
 beq AcceptLeft
TooDeep:
 plp
 jsr RestoreCursor
 rts                          ; vertical overlap remains native head/side owned
AcceptLeft:
 plp
 tya
 sta Player_X_Position
 lda RcTemp2
 adc #0
Page:
 sta Player_PageLoc
 jsr RestoreCursor
 jsr RcZeroX
 lda #0
 sta MmXFraction+1
 sta Player_X_Speed
 sta Player_XSpeedAbsolute
 lda Player_X_Position
 sec
 sbc RcOldX
 sta Player_X_Scroll
Done:
 rts
RestoreCursor:
 lda #5
 ldx RcWallDirection
 cpx #1
 beq :+
 lda #3
:sta RcWallCursor
 rts
Sample:
 jsr BlockBufferColli_Side
 beq Empty
 cmp #$1c                   ; native horizontal pipe entry stays native
 bcc Other
 cmp #$20
 bcc Empty
Other:
 cmp #$5f                   ; invisible blocks have no solid side
 beq Empty
 cmp #$60
 beq Empty
 cmp #$67                   ; native spring ownership/lifecycle
 beq Empty
 cmp #$68
 beq Empty
 cmp #$6b
 beq Empty
 cmp #$6c
 beq Empty
 cmp #$c2                   ; collectible coins and axe are not walls
 beq Empty
 cmp #$c3
 beq Empty
 cmp #$c5
 beq Empty
 tay
 lda MTileAttribute,y
 and #MTILE_SOLID|MTILE_CLIMB
 cmp #MTILE_SOLID
 bne Empty
 lda Player_Y_Speed
 bmi Rising
 ; A genuine exposed top plane crossed vertically belongs to the native
 ; landing consumer, including its speed-dependent seven-pixel window.
 lda RcTerrainOldY
 cmp R2                     ; previous feet(oldY+32) <= sampled cell top
 bcc TopCrossing
 beq TopCrossing
 sec
 rts
TopCrossing:
 ldy R2
 beq Empty
 tya
 sec
 sbc #16
 tay
 lda (R6),y
 tay
 lda MTileAttribute,y
 and #MTILE_SOLID
 beq Empty
 sec
 rts
Rising:
 ; Likewise preserve a real exposed ceiling crossed by the native head.
 ; R2+44 is the previous player Y at which head(+4) meets the underside.
 lda R2
 clc
 adc #44
 cmp RcTerrainOldY
 bcc BottomCrossing
 beq BottomCrossing
 sec
 rts
BottomCrossing:
 lda R2
 cmp #$c0
 bcs Empty
 clc
 adc #16
 tay
 lda (R6),y
 tay
 lda MTileAttribute,y
 and #MTILE_SOLID
 beq Empty
 sec
 rts
Empty:
 clc
 rts
.endproc
.popseg
