; SMB scene adapter around the byte-authenticated original player algorithms.
.pushseg
.segment "Z2_LOGIC"
.proc Z2GlobalInit
 farcall DwGlobalInit
 lda #2
 sta $5104 ; Root shared expanded initializer owns mode2 after integration.
 lda #0
 ldx #7
Loop:sta Z2Variant,x
 dex
 bpl Loop
 ldx #127
Clear:sta Z2TransientBegin,x
 dex
 bpl Clear
 rts
.endproc
.proc Z2MovementGate
 jsr Z2IsActive
 bcs Native
 farcall RosterMovement,jmp
Native:
 farcall Z2MovementCameraExit,jmp
.endproc
.segment "Z2_COLD"
.proc Z2Movement
 farcall Z2EnsureInit
 lda Z2NativeWalkFace
 bne Live
 farcall Z2AreaReset
 lda PlayerFacingDir
 cmp #2
 beq :+
 lda #1
:sta Z2NativeWalkFace
 lda #1
 sta Z2NativeShield
Live:
 lda #0
 sta PlayerSize
 sta MmSliding
 sta MmOnVine
 sta MmUnderwater
 sta Player_X_Scroll
 lda Player_State
 cmp #3
 bne Ordinary
 farcall MegaManClimbing,jmp
Ordinary:
 lda Player_X_Position
 sta MmOldX
 lda Player_State
 bne Air
 lda #4
 bne Contacts
Air:lda #0
Contacts:sta Z2NativeContacts
 lda SavedJoypadBits
 eor Z2PreviousButtons
 and SavedJoypadBits
 sta Z2NativePressed
 lda SavedJoypadBits
 sta Z2PreviousButtons
 lda Z2ActiveSpells
 and #2
 sta Z2NativeJumpFlag
 lda Z2ActiveSpells
 and #8
 jne Fairy
 ; Collision corrections from the completed SMB scene update own these
 ; integer speeds. Preserve native fractional gravity unless speed changed.
 lda Player_State
 beq Ground
 lda Player_Y_Speed
 cmp Z2NativeVY
 beq Timers
 sta Z2NativeVY
 lda #0
 sta Z2NativeGravityFraction
 jmp Timers
Ground:
 lda #0
 sta Z2NativeVY
 sta Z2NativeAir
Timers:
 lda Z2AttackTimer
 beq :+
 dec Z2AttackTimer
:
 lda Z2NativeWalkTimer
 beq :+
 dec Z2NativeWalkTimer
:
 lda Z2HurtTimer
 beq Control
 lda #0
 sta Z2NativePressedAB
 jsr Z2Native::Link_Jumping_routine
 jsr Z2Native::bank0_goto__1610
 lda #10
 sta Z2CachedPose
 jmp MotionReady
Control:
 jsr Z2Native::L959C
 jsr Z2Native::bank0_Side_View4__walking
 jsr Z2Native::Link_Jumping_routine
 jsr Z2Native::bank0_Sword_Slash
 ldy #1
 lda Z2NativeVX
 beq MotionReady
 bpl :+
 iny
:sty Z2NativeWalkFace
MotionReady:
 lda #0
 sta CrouchingFlag
 lda Z2NativeShield
 bne Standing
 lda Z2NativeAir
 bne Standing
 inc CrouchingFlag
Standing:
 lda Z2NativeAir
 beq StateReady
 lda #1
 ldx Z2NativeVY
 bmi StateReady
 lda #2
StateReady:sta Player_State
 jmp Export
Fairy:
 lda #1
 sta CrouchingFlag
 sta Z2NativeAir
 sta Player_State
 lda SavedJoypadBits
 and #$0f
 tay
 lda #0
 sta Z2NativeVX
 sta Z2NativeVY
 cpy #0
 beq Export
 cpy #11
 bcs Export
 lda FairyVX,y
 sta Z2NativeVX
 lda FairyVY,y
 sta Z2NativeVY
 ldx #0
 jsr Z2Native::bank7_XY_Movements_Routine
 ldx #0
 jsr Z2Native::LD20A
Export:
 lda Z2NativeVX
 sta Player_X_Speed
 sta MmLastXSpeed
 bpl :+
 eor #$ff
 clc
 adc #1
:sta Player_XSpeedAbsolute
 lda Z2NativeVY
 sta Player_Y_Speed
 sta MmVY+2
 lda #0
 sta MmVX
 sta MmVY
 sta MmVY+1
 sta MmXFraction
 lda Z2NativeXFraction
 sta MmXFraction+1
 lda Z2NativeVX
 asl
 asl
 asl
 asl
 sta MmVX+1
 lda Z2NativeVX
 lsr
 lsr
 lsr
 lsr
 cmp #8
 bcc :+
 ora #$f0
:sta MmVX+2
 lda Player_X_Position
 sec
 sbc MmOldX
 sta Player_X_Scroll
 rts
FairyVX:.byte $10,$18,$e8,$ff,0,$18,$e8,$ff,0,$18,$e8
FairyVY:.byte 0,0,0,$ff,$18,$18,$18,$ff,$e8,$e8,$e8
.endproc
.proc Z2MovementCameraExit
 ; Source world motion must publish the native relative scroll cache.
 ; This cold tail retains the existing18B gate and all original PCs.
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sta X5CameraBefore
 jsr Z2Movement
 jsr Z2FirstJumpFood
 lda X5CameraBefore
 sta Player_Pos_ForScroll
 rts
.endproc
; SMB delivery adaptation: a first, unowned Jump from a mushroom block
; keeps its full native visible rise, then walks/falls like that mushroom.
; Its owner/stamp and genuine Jump icon stay unchanged; only contact grants it.
.proc Z2FirstJumpFood
 txa
 pha
 lda Z2LearnedSpells
 and #2
 bne Done
 ldx #5
Loop:
 lda Enemy_Flag,x
 beq Next
 lda Enemy_ID,x
 cmp #PowerUpObject
 bne Next
 lda InvPickupOwner,x
 cmp #CHARACTER_LINK
 bne Next
 lda InvPickup,x
 cmp #$c0
 bne Next
 lda InvPickupSaveLo,x
 cmp #1
 bne Next
 lda Enemy_State,x
 bpl Next
 lda #$81
 sta InvPickupSaveLo,x
 lda #0
 sta PowerUpType,x
 lda #$10
 sta Enemy_X_Speed,x
 lda #1
 sta Enemy_MovingDir,x
Next:dex
 bpl Loop
Done:
 pla
 tax
 rts
.endproc
.popseg
