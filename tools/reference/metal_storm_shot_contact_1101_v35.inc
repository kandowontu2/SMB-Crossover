; Source shot rectangles E8CE/E92E/E98E/E9EE; native enemy transaction.
; Render scratch is ephemeral here and never persists across an update.
Ms35Enemy=MsPacket
Ms35Object=MsPacket+1
Ms35Left=MsPacket+2
Ms35Right=MsPacket+3
Ms35Top=MsPacket+4
Ms35Bottom=MsPacket+5
Ms35EnemyX=MsPacket+6
.segment "MS11_RENDER"
Ms35Weapons:
 jsr MsRSave
 lda GamePauseStatus
 and #1
 jne Ms35Return
 lda GameEngineSubroutine
 cmp #8
 jne Ms35Return
 lda ObjectOffset
 sta Ms35Object
 lda #2
 sta MsSlot
Ms35Shot:
 ldx MsSlot
 lda MsState+$510,x
 jpl Ms35NextShot
 lda MsState+$528,x
 cmp #$80
 beq Ms35Normal
 cmp #$81
 jne Ms35NextShot
 lda #0
 sta Ms35Left
 sta Ms35Top
 lda #15
 sta Ms35Bottom
 sta Ms35Right
 cpx #2
 beq Ms35Bounds
 lda #7
 sta Ms35Right
 bne Ms35Bounds
Ms35Normal:
 lda #2
 sta Ms35Left
 lda #5
 sta Ms35Right
 lda #6
 sta Ms35Top
 lda #9
 sta Ms35Bottom
Ms35Bounds:
 jsr MsRPosition
 lda R7
 cmp #1
 jne Ms35NextShot
 lda R5
 jne Ms35NextShot
 lda #5
 sta Ms35Enemy
 jsr Ms35Enemies
Ms35NextShot:
 inc MsSlot
 lda MsSlot
 cmp #4
 bcc Ms35Shot
 lda Ms35Object
 sta ObjectOffset
Ms35Return:
 jmp MsRRestore

.segment "MS25_EXTRA"
Ms35Enemies:
 ldx Ms35Enemy
 lda Enemy_Flag,x
 beq Ms35NextEnemy
 bmi Ms35NextEnemy
 lda Enemy_State,x
 and #$20
 bne Ms35NextEnemy
 lda Enemy_ID,x
 cmp #$15
 bcs Ms35NextEnemy          ; platforms/firebars/items are not victims
 cmp #6
 bne :+
 lda Enemy_State,x
 cmp #2
 bcs Ms35NextEnemy
:
 lda Enemy_Y_HighPos,x
 cmp #1
 bne Ms35NextEnemy
 lda Enemy_X_Position,x
 sec
 sbc ScreenLeft_X_Pos
 sta Ms35EnemyX
 lda Enemy_PageLoc,x
 sbc ScreenLeft_PageLoc
 bne Ms35NextEnemy
 ; Inclusive interval overlap, without wrapping a screen-edge rectangle.
 lda R4
 clc
 adc Ms35Right
 bcs :+
 cmp Ms35EnemyX
 bcc Ms35NextEnemy
:
 lda Ms35EnemyX
 clc
 adc #15
 bcs :+
 sec
 sbc R4
 bcc Ms35NextEnemy
 cmp Ms35Left
 bcc Ms35NextEnemy
:
 lda R6
 clc
 adc Ms35Bottom
 bcs :+
 cmp Enemy_Y_Position,x
 bcc Ms35NextEnemy
:
 lda Enemy_Y_Position,x
 clc
 adc #23
 bcs :+
 sec
 sbc R6
 bcc Ms35NextEnemy
 cmp Ms35Top
 bcc Ms35NextEnemy
:
 stx ObjectOffset
 stx R1
 jsr HandleEnemyFBallCol
 ; Original E53C..E543 shot retirement on accepted contact.
 ldx MsSlot
 lda #0
 sta MsState+$510,x
 lda #$80
 sta MsState+$498,x
 rts
Ms35NextEnemy:
 dec Ms35Enemy
 jpl Ms35Enemies
 rts
