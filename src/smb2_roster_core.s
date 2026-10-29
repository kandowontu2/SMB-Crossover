.pushseg
.segment "PARODIUS_BELLS"
.export S2ColdInit,S2NewLife,S2Ensure,S2Movement,S2EndFrame,S2NmiClock,S2GiveItem,S2Pickup
.export S2InjuryStatus,S2InjuryStart,S2DeathStart,S2DeathUpdate,S2HeadContact
.export S2StompPolicy,S2Box,S2Adder,S2Head,S2Side,S2FullPower
.export S2CollisionBounds
.include "smb2_roster_stats.inc"
.proc S2SceneKey
 lda AreaType
 .repeat 5
 asl
 .endrepeat
 ora AreaAddrsLOffset
 rts
.endproc
.proc S2ColdInit
 ; Real selection/newgame calls this BEFORE any Ready read or clock tick.
 lda SelectedCharacter
 cmp #CHARACTER_SMB2_ROSTER
 bne No
 lda #0
 sta S2Clock                 ; cold ownership switch only; source phase starts.
 jmp S2InitializeRecord
No:clc
 rts
.endproc
.proc S2NewLife
 lda SelectedCharacter
 cmp #CHARACTER_SMB2_ROSTER
 bne No
 ; Native byte10 survives loss of a life. Never save/restore this NMI owner.
 jmp S2InitializeRecord
No:clc
 rts
.endproc
.proc S2InitializeRecord
 lda #0
 sta S2Ready
 sta S2MaxHealth
 sta S2Vegetables
 lda #$1f                      ; original two-heart initial health.
 sta S2Health
 jsr S2ResetTransient
 jsr S2ExportPosition         ; native initial two-heart/large form, before draw.
 lda #$b2                      ; publish initialized owner state LAST.
 sta S2Ready
 sec
 rts
.endproc
.proc S2ResetTransient
 lda #0
 ; Keep NMI-owned Clock live across a scene reset. No save/restore window
 ; can lose an NMI increment while foreground initialization is running.
 ldx #80
ClearUpper:sta $5c2f,x
 dex
 bpl ClearUpper
 ldx #45
ClearLower:sta $5c00,x
 dex
 bpl ClearLower
 lda S2Variant
 cmp #4
 bcc Valid
 lda #0
Valid:tax
 lda VariantNative,x
 sta S2NativeCharacter
 lda StatOffset,x
 tay
 ldx #0
Stats:lda S2OriginalStats,y
 sta S2Stats,x
 iny
 inx
 cpx #23
 bcc Stats
 lda #1
 sta S2Horizontal
 sta S2Face
 lda S2Health
 cmp #$10
 lda #0
 bcs Size
 lda #1
Size:sta S2Size
 lda NumberofLives
 sta S2Life
 jsr S2SceneKey
 sta S2Area
 lda WorldNumber
 sta S2World
 lda #$ff
 sta S2PaletteAck
 sta S2ObjectHost0
 sta S2ObjectHost1
 sta S2ObjectHost2
 jsr S2ImportPosition
 rts
VariantNative:.byte 0,3,2,1
StatOffset:.byte 0,23,46,69
.endproc
.proc S2Ensure
 lda SelectedCharacter
 cmp #CHARACTER_SMB2_ROSTER
 bne No
 lda S2Ready
 cmp #$b2
 bne Cold
 lda NumberofLives
 sec
 sbc S2Life                    ; ordinary INC gains/wrap are not a death.
 bmi NewLife
 lda NumberofLives
 sta S2Life
 jsr S2SceneKey
 cmp S2Area
 bne Scene
 lda WorldNumber
 cmp S2World
 bne Scene
 ldx S2Variant
 cpx #4
 bcc :+
 ldx #0
:lda S2ResetTransient::VariantNative,x
 cmp S2NativeCharacter
 beq Yes
 jmp S2ColdInit               ; real menu selection must call ColdInit first.
Scene:
 jsr S2ResetScene              ; native carried vegetables survive room entry.
Yes:sec
 rts
Cold:jmp S2ColdInit
NewLife:jmp S2NewLife
No:clc
 rts
.endproc
.proc S2ResetScene
 lda S2Previous
 pha                          ; keep real input edge history across a room.
 lda S2Holding
 beq None
 ldx S2HeldIndex
 lda S2ObjectHost0,x
 cmp #$ff
 bne None                     ; real SMB actor transfer requires root authority.
 lda S2ObjectType,x
 cmp #$32
 bcc None
 cmp #$34
 bcc Save
None:lda #$ff
Save:pha
 jsr S2ResetTransient
 pla
 cmp #$ff
 beq Done
 sta S2ObjectType
 lda #1
 sta S2Holding
 sta S2ObjectState
 sta S2ObjectLift              ; source area carry-over resumes at final hold.
 lda #2
 sta S2ObjectHitbox
 ldx #0
 stx S2Source12
 jsr S2O960F                  ; actual current-room source carry coordinates.
Done:pla
 sta S2Previous
 rts
.endproc
.proc S2NmiClock
 ; NMI-safe leaf ONLY: no shared farcallSMC, RAM borrow, bank or Ready read.
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_SMB2_ROSTER
 bne Done
 inc S2Clock                   ; original counter advances even lag/pause.
Done:pla
 plp
 rts
.endproc
.proc S2ImportPosition
 lda Player_X_Position
 sta S2X
 lda Player_PageLoc
 sta S2Page
 lda Player_Y_Position
 sta S2Y
 lda Player_Y_HighPos
 sec
 sbc #1
 sta S2YPage                   ; source screen page0 = host page1.
 lda Player_Rel_XPos
 sta S2ScreenX
 rts
.endproc
.proc S2Movement
 jsr S2Ensure
 bcc No
 lda OperMode
 cmp #1
 bne No
 lda GameEngineSubroutine
 cmp #8
 bne No
 lda TimerControl
 bne No
 lda GamePauseStatus
 and #1
 bne No
 ; Root terrain/camera handoffs can move native XY. Import real position,
 ; keeping the source's independent signed velocities and fractions.
 jsr S2ImportPosition
 lda SavedJoypadBits
 ; Both real engines already use A80/B40/Down04/Left02/Right01.
 sta S2Held
 eor S2Previous
 and S2Held
 sta S2Fresh
 lda S2Held
 sta S2Previous
 lda StarInvincibleTimer
 sta S2Star
 jsr S2LimitThrowPool
 jsr S2HandlePlayerState
 jsr S2ObjectsTick
 jsr S2ExportPosition
 sec
 rts
No:clc
 rts
.endproc
.proc S2HandlePlayerState
 ; Actual8A02 prefix; only the native jump-table dispatcher is made explicit.
 lda S2State
 cmp #2
 bcs Dispatch
 lda #0
 ldy #$10
 cpy S2Health
 rol
 eor S2Size
 beq Dispatch
 ldy S2Size
 lda GrowShrink,y
 sta S2Sfx2
 lda #30
 sta S2Timer
 lda #8
 sta S2State
Dispatch:
 lda S2State
 beq Normal
 cmp #2
 beq Lift
 cmp #8
 beq Changing
 rts                           ; real climb/pipe/door handoff is root-owned.
Normal:
 lda AreaType
 beq Water
 jmp S2N8A41                   ; Gravity/input/collision/boundary/Y/X order.
Water:jmp S2SwimFrame          ; disclosed SMB1 water adaptation only.
Lift:jmp S2N8A87
Changing:jmp S2N8BF1
GrowShrink:.byte 8,32
.endproc
.proc S2EndFrame
 lda SelectedCharacter
 cmp #CHARACTER_SMB2_ROSTER
 bne Done
 lda OperMode
 cmp #1
 bne Done
 lda GamePauseStatus
 and #1
 bne Done
 lda GameEngineSubroutine
 cmp #8
 beq Timers
 cmp #11
 bne Done
Timers:
 ; Call ONCE after player/object/render actions of each completed activeMain.
 ; Native82/84/85 timers, source order AFTER render; clock is NMI-owned.
 lda S2Hurt
 beq Walk
 dec S2Hurt
Walk:lda S2WalkTimer
 beq State
 dec S2WalkTimer
State:lda AreaType
 bne StateTimer
 lda S2Charge
 beq StateTimer
 dec S2Charge                 ; authored water stroke gate is completed-Main.
StateTimer:lda S2Timer
 beq Done
 dec S2Timer
Done:rts
.endproc
.proc S2ExportPosition
 lda S2X
 sec
 sbc Player_X_Position
 sta Player_X_Scroll
 lda S2X
 sta Player_X_Position
 lda S2Page
 sta Player_PageLoc
 lda S2Y
 sta Player_Y_Position
 lda S2YPage
 clc
 adc #1
 sta Player_Y_HighPos
 lda S2VX
 sta Player_X_Speed
 bpl Abs
 eor #$ff
 clc
 adc #1
Abs:sta Player_XSpeedAbsolute
 lda S2VY
 sta Player_Y_Speed
 lda S2Air
 beq Ground
 lda #1
Ground:sta Player_State
 lda S2Face
 eor #1
 clc
 adc #1
 sta PlayerFacingDir
 lda S2Duck
 sta CrouchingFlag
 lda S2Size
 sta PlayerSize
 lda S2Health
 cmp #$10
 lda #0
 bcc Status
 lda #1
Status:sta PlayerStatus
 rts
.endproc
.proc S2GiveItem
 pha
 jsr S2Ensure
 pla
 bcc No
 cmp #0
 beq Mushroom
 cmp #1
 bne No
 lda S2Vegetables
 clc
 adc #3
 cmp #10
 bcc Reserve
 lda #9
Reserve:sta S2Vegetables
 sec
 rts
Mushroom:
 ldx S2MaxHealth
 cpx #2
 bcs Full
 inx
 stx S2MaxHealth
Full:lda FullHealth,x
 sta S2Health
 sec
 rts
No:clc
 rts
FullHealth:.byte $1f,$2f,$3f
.endproc
.proc S2Pickup
 ; Actual physical collector supplies X/PowerUpType; root erases only on C1.
 lda SelectedCharacter
 cmp #CHARACTER_SMB2_ROSTER
 bne No
 txa
 pha
 lda PowerUpType,x
 jsr S2GiveItem
 pla
 tax                          ; actual collector owner survives the item call.
 rts
No:clc
 rts
.endproc
.proc S2FullPower
 jsr S2Ensure
 bcc Done
 lda #2
 sta S2MaxHealth
 lda #$3f
 sta S2Health
 lda #9
 sta S2Vegetables
Done:rts
.endproc
.proc S2InjuryStatus
 lda SelectedCharacter
 cmp #CHARACTER_SMB2_ROSTER
 bne No
 lda S2Hurt
 ora StarInvincibleTimer
 beq No
 sec
 rts
No:clc
 rts
.endproc
.proc S2InjuryStart
 ; A=actual touching enemy's relativeX, no synthetic HP/outcome input.
 pha
 jsr S2Ensure
 pla
 bcc No
 sta S2SourceScreenX
 lda S2Hurt
 ora StarInvincibleTimer
 bne No
 ; Exact native nonfatal damage/knockback body3:B9FA..BA31.
 lda S2Health
 sec
 sbc #$10
 bcc Dead
 sta S2Health
 ldy #$7f
 sty S2Hurt
 ldy #0
 sty S2VY
 sty S2VX
 cmp #$10
 bcc Request
 lda S2ScreenX
 sec
 sbc S2SourceScreenX
 asl
 asl
 sta S2VX
 lda #$c0
 ldy S2VY
 bpl Velocity
 lda #0
Velocity:sta S2VY
Request:lda #4
 sta S2DpcmRequest
 sec
 rts
Dead:jsr S2DeathStart
 sec
 rts
No:clc
 rts
.endproc
.proc S2TerrainHurt
 lda S2ScreenX
 jmp S2InjuryStart
.endproc
.proc S2DeathStart
 lda SelectedCharacter
 cmp #CHARACTER_SMB2_ROSTER
 bne Done
 jsr S2DropHeld
 lda #0
 sta S2Health
 sta S2Charge
 sta S2Star
 lda #7
 sta S2State
 sta S2Animation
 lda #$c0
 sta S2VY
 lda #32
 sta S2Timer
 lda #$80
 sta S2DpcmRequest
 lda #11
 sta GameEngineSubroutine
 lda #1
 sta MmDeathFlag
Done:rts
.endproc
.proc S2DeathUpdate
 lda SelectedCharacter
 cmp #CHARACTER_SMB2_ROSTER
 bne Done
 lda S2Timer
 bne Done
 lda S2YPage
 beq Move
 bmi Move
 lda #6
 sta GameEngineSubroutine
 rts
Move:jsr S2N8EA4
 lda S2VY
 bmi Accelerate
 cmp #$39
 bcs Export
Accelerate:inc S2VY
 inc S2VY
Export:jmp S2ExportPosition
Done:rts
.endproc
.proc S2StompPolicy
 lda SelectedCharacter
 cmp #CHARACTER_SMB2_ROSTER
 bne No
 lda CrossoverBehaviorVersion
 beq Yes                      ; Easy normal stomps; Hard stand/lift contract.
No:clc
 rts
Yes:sec
 rts
.endproc
.proc S2Box
 ldy #0
 lda SelectedCharacter
 cmp #CHARACTER_SMB2_ROSTER
 bne Done
 lda S2Duck
 beq Done
 ldy #2
Done:rts
.endproc
.proc S2CollisionBounds
 ; Original fixedF099/F0AD/F0C1/F0D5 fields0/1. R0/R1=left/top,
 ; R2/R3=exclusive right/bottom; width11,height22 standing/17 ducked.
 ; Native size does not alter this original game's enemy hitbox.
 lda SelectedCharacter
 cmp #CHARACTER_SMB2_ROSTER
 bne Done
 lda #2
 sta R0
 lda #11
 ldy S2Duck
 beq :+
 lda #16
:sta R1
 lda #13
 sta R2
 lda #33
 sta R3
Done:rts
.endproc
.proc S2Adder
 clc
 rts
.endproc
.proc S2Head
 jmp BlockBufferColli_Head
.endproc
.proc S2Side
 jmp BlockBufferColli_Side
.endproc
.proc S2HeadContact
 lda SelectedCharacter
 cmp #CHARACTER_SMB2_ROSTER
 bne No
 lda S2Collision
 and #8
 beq No
 lda S2HeadX
 sta R4
 lda S2HeadPage
 sta R5
 lda S2HeadY
 sta R6
 sec
 rts                           ; genuine foreground block consumer owns reward.
No:clc
 rts
.endproc
.popseg
