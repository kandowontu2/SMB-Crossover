.pushseg
.segment "ROLL_CORE"
.proc RlEnsure
 lda #1
 sta RlOutlineBypass
 lda RlReady
 cmp #$52
 bne NewLife
 lda NumberofLives
 cmp RlLife
 bcc NewLife
 sta RlLife
 lda RlArea
 cmp AreaPointer
 bne Area
 lda RlWorld
 cmp WorldNumber
 beq Done
 bne Area
NewLife:
 lda #0
 sta RlFoodKind
 lda #28
 sta RlHealth
 sta RlEnergy
 lda #$52
 sta RlReady
Area:
 jsr RlClear
Done:rts
.endproc
.proc RlClear
 lda #0
 ldx #$3f
Loop:sta $5c00,x
 dex
 bpl Loop
 ldx #3
Shots:sta MmBulletType,x
 sta InvDropKind,x
 dex
 bpl Shots
 sta MmSliding
 sta RgCrouch
 sta XgDash
 sta XgJumpUsed
 sta SsHeld
 sta SsKick
 sta GuestHurtKind
 sta GuestHurtTicks
 sta PlayerChangeSizeFlag
 lda NumberofLives
 sta RlLife
 lda AreaPointer
 sta RlArea
 lda WorldNumber
 sta RlWorld
 lda #1
 sta RlDirty
 rts
.endproc
.proc RlResetOwn
 ; Check life loss before clearing the volatile state updates RlLife.
 jsr RlEnsure
 jmp RlClear
.endproc
.proc RlMovement
 jsr RlEnsure
::RlFrameReady:
.export RlFrameReady
 inc RlClock
 lda SavedJoypadBits
 eor RlPrevious
 and SavedJoypadBits
 sta RlFresh
 lda SavedJoypadBits
 sta RlPrevious
 sta RlButtons
 lda RlInvul
 beq :+
 dec RlInvul
:lda RlAttack
 beq :+
 dec RlAttack
:lda RlHurt
 beq NotHurt
 dec RlHurt
 lda #0
 sta SavedJoypadBits
 sta MmFrictionYActive
 jmp Move
NotHurt:
 lda SavedJoypadBits
 and #$fb                    ; Mobile Roll has no Down+A slide.
 sta SavedJoypadBits
Move:
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sta Player_Pos_ForScroll        ; SMB camera consumes the pre-motion position.
 lda #0
 sta MmSliding
 sta RgCrouch
 sta XgDash
 sta XgJumpUsed
 sta CrouchingFlag
 sta GuestHurtKind
 sta GuestHurtTicks
 sta SideCollisionTimer          ; Source motion already resolves walls; keep the camera following it.
 lda RlFoodKind
 sta PlayerStatus
 farcall RlSourceMovement
 lda RlButtons
 sta SavedJoypadBits
 lda Player_X_Speed
 beq Idle
 inc RlWalk
 lda RlWalk
 cmp #24
 bcc Done
Idle:lda #0
 sta RlWalk
Done:rts
.endproc
.proc RlAdder
 ldy #3
 lda RlHurt
 bne Done
 lda Player_State
 beq Done
 iny                           ; Match the installed Mega Man airborne probes.
Done:sec
 rts
.endproc
.proc RlBox
 ldy #12
 lda RlHurt
 bne Done
 lda Player_State
 beq Done
 iny
Done:rts
.endproc
.proc RlInjury
 jsr RlEnsure
 lda RlInvul
 bne Protected
 ldx ObjectOffset
 lda Enemy_ID,x
 cmp #Bowser
 bne Ordinary
 lda #8
 bne Damage
Ordinary:lda #4
Damage:sta RlTemp
 lda RlHealth
 sec
 sbc RlTemp
 bcc Dead
 beq Dead
 sta RlHealth
 lda #64
 sta RlInvul
 lda #16
 sta RlHurt
 lda #1
 sta RlDirty
 sta InjuryTimer
 sta Player_State
 lda #0
 sta RlCharge
 sta RlAttack
 sta TimerControl
 sta PlayerChangeSizeFlag
 sta MmVX
 sta MmVY
 lda #$80
 sta MmVX+1
 lda #1
 sta MmVX+2
 lda PlayerFacingDir
 cmp #1
 bne LaunchY
 lda #$fe
 sta MmVX+2
LaunchY:lda #0
 sta MmVY+1
 lda #$fe
 sta MmVY+2
 lda #Sfx_PipeDown_Injury
 sta Square1SoundQueue
Protected:sec
 rts
Dead:lda #0
 sta RlHealth
 sta RlCharge
 jmp KillPlayer
.endproc
.proc RlInjuryStatus
 lda #1
 tax
 rts
.endproc
.proc RlVisible
 lda RlInvul
 beq Show
 lda FrameCounter
 and #2
 bne Hide
Show:sec
 rts
Hide:clc
 rts
.endproc
.proc RlDeathStart
 lda #0
 sta RlHealth
 sta RlCharge
 sta RlAttack
 lda #1
 sta RlDirty
 rts
.endproc
.proc RlPrepare
 stx InvObject
 lda #0
 sta InvRisePhase,x
 lda #9
 sta InvPickupOwner,x
 lda #$fc                    ; Native mushroom/flower art and emergence.
 sta InvPickup,x
 rts
.endproc
.proc RlCollect
 phx
 jsr RlEnsure
 plx
 lda PowerUpType,x
 cmp #2
 bcs No
 lda #28
 sta RlHealth
 sta RlEnergy
 lda #0
 sta RlPalette
 lda #1
 sta RlDirty
 sta PlayerStatus
 sta RlFoodKind
 lda #Sfx_PowerUpGrab
 sta Square2SoundQueue
 sec
 rts
No:clc
 rts
.endproc
.proc RlUi
 lda #0
 sta InvHudActive
 sta InvDirty
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda RlDirty
 jeq Done
 ldx VRAM_Buffer1_Offset
 cpx #53
 jcs Done
 lda #$20
 sta VRAM_Buffer1,x
 lda #4
 sta VRAM_Buffer1+1,x
 lda #12
 sta VRAM_Buffer1+2,x
 lda #$11
 sta VRAM_Buffer1+3,x
 lda #$19
 sta VRAM_Buffer1+4,x
 lda RlHealth
 jsr Decimal
 sta VRAM_Buffer1+6,x
 tya
 sta VRAM_Buffer1+5,x
 lda #$24
 sta VRAM_Buffer1+7,x
 lda #$24
 sta VRAM_Buffer1+8,x
 lda #$0e
 sta VRAM_Buffer1+9,x
 lda #$17
 sta VRAM_Buffer1+10,x
 lda RlEnergy
 jsr Decimal
 sta VRAM_Buffer1+12,x
 tya
 sta VRAM_Buffer1+11,x
 lda #$24
 sta VRAM_Buffer1+13,x
 sta VRAM_Buffer1+14,x
 lda #$20
 sta VRAM_Buffer1+15,x
 lda #$12
 sta VRAM_Buffer1+16,x
 lda #13
 sta VRAM_Buffer1+17,x
 .repeat 13,I
 lda Labels+I
 sta VRAM_Buffer1+18+I,x
 .endrepeat
 txa
 clc
 adc #31
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 sta RlDirty
Done:rts
Decimal:ldy #0
Loop:cmp #10
 bcc End
 sec
 sbc #10
 iny
 bne Loop
End:rts
Labels:.byte "WORLD   TIME "
.endproc
.proc RlStatusName
 cmp #0
 bne Done
 phy
 ldy #7
Loop:lda Text,y
 sta VRAM_Buffer1+11,y
 dey
 bpl Loop
 ply
 lda #0
Done:rts
Text:.byte "ROLL    "
.endproc
.popseg
