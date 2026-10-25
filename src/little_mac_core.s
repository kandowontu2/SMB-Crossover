; Punch-Out runner and native boxing timing; SMB platform motion is adapted.
.pushseg
.segment "LM_CORE"
.macro TnHotGate Target
.local Legacy
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 bne Legacy
 pla
 plp
 farcall Target,jmp
Legacy:pla
 plp
.endmacro
.proc LmIsActive
 lda SelectedCharacter
 cmp #15
 beq Yes
 clc
 rts
Yes:sec
 rts
.endproc
.macro LmGate Legacy
.local Active
 php
 pha
 jsr LmIsActive
 jcs Active
 pla
 plp
 farcall Legacy,jmp
Active:pla
 plp
.endmacro
.proc LmEnsure
 lda LmReady
 cmp #$4d
 jne NewLife
 lda LmLife
 cmp NumberofLives
 jne NewLife
 lda AreaPointer
 cmp LmArea
 jne Area
 lda WorldNumber
 cmp LmWorld
 jeq Done
 jne Area
NewLife:
 lda #96
 sta LmHealth
 lda #20
 sta LmHearts
 lda #0
 sta LmStars
 lda #$4d
 sta LmReady
Area:jsr LmClear
Done:rts
.endproc
.proc LmClear
 lda #0
 tax
Loop:sta $5c00,x
 inx
 bne Loop
 sta MarioSourceActive
 sta MmSliding
 sta SmBall
 sta GuestHurtKind
 sta GuestHurtTicks
 sta DisableCollisionDet
 lda NumberofLives
 sta LmLife
 lda AreaPointer
 sta LmArea
 lda WorldNumber
 sta LmWorld
 lda #1
 sta LmDirty
 rts
.endproc
.proc LmResetGate
 farcall JnResetDispatch
 jsr LmIsActive
 bcc Done
 ; Check the old life marker before LmClear stamps the newly loaded life.
 ; Otherwise a death leaves zero HP with a marker that looks current.
 jsr LmEnsure
 jmp LmClear
Done:rts
.endproc
.proc LmMovementGate
 TnHotGate TnMovement
 LmGate JnMovementDispatch
 jsr LmEnsure
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda SavedJoypadBits
 eor LmPrevious
 and SavedJoypadBits
 sta LmFresh
 lda SavedJoypadBits
 sta LmPrevious
 lda #0
 sta PlayerSize
 sta MmSliding
 sta SmBall
 sta DisableCollisionDet
 sta GuestHurtKind
 sta GuestHurtTicks
 lda #1
 sta GuestHurtVisible
 lda LmInvul
 beq :+
 dec LmInvul
:lda LmHurt
 beq :+
 dec LmHurt
:lda LmAttack
 beq :+
 dec LmAttack
:lda SwimmingFlag
 beq Land
 farcall MarioWaterMovement
 jmp Crouch
Land:
 lda SavedJoypadBits
 sta LmHeld
 lda RgCrouch
 beq Free
 lda SavedJoypadBits
 and #Down_Dir
 bne Free
 jsr LmStandBlocked
 beq Free
 lda SavedJoypadBits
 ora #Down_Dir
 sta SavedJoypadBits
Free:
 farcall MarioSourceGravity
 sta XgGravity
 sty XgGravity+1
 lda #0
 sta RgFallCap
 sta RgFallCap+1
 lda #5
 sta RgFallCap+2
 farcall MarioSourceMovement
 lda LmHeld
 sta SavedJoypadBits
Crouch:
 lda CrouchingFlag
 sta RgCrouch
 lda Player_X_Speed
 beq Rest
 inc LmWalk
 lda LmWalk
 cmp #40
 bcc Rest
 lda #0
 sta LmWalk
Rest:
 lda LmHearts
 bne Done
 lda RgCrouch
 beq Done
 inc LmRest
 lda LmRest
 cmp #30
 bcc Done
 lda #0
 sta LmRest
 lda #20
 sta LmHearts
 lda #1
 sta LmDirty
Done:rts
.endproc
.proc LmInjuryGate
 LmGate JnInjuryStartDispatch
 lda LmInvul
 jne Protected
 lda #8
 ldx ObjectOffset
 ldy Enemy_ID,x
 cpy #HammerBro
 bne :+
 lda #16
:cpy #Bowser
 bne :+
 lda #32
:sta LmTemp
 lda LmHealth
 sec
 sbc LmTemp
 jcc Dead
 jeq Dead
 sta LmHealth
 lda LmHearts
 sec
 sbc #3
 bcs :+
 lda #0
:sta LmHearts
 lda LmStars
 beq :+
 dec LmStars
:lda #0
 sta LmAttack
 sta TimerControl
 sta PlayerChangeSizeFlag
 lda #64
 sta LmInvul
 lda #16
 sta LmHurt
 lda #1
 sta LmDirty
 lda #Sfx_PipeDown_Injury
 sta Square1SoundQueue
Protected:sec
 rts
Dead:lda #0
 sta LmHealth
 jmp KillPlayer
.endproc
.proc LmInjuryStatusGate
 LmGate JnInjuryStatusDispatch
 lda #1
 tax
 rts
.endproc
.proc LmBodyGate
 php
 pha
 lda X5FootDescending
 beq NoFootContact
 pla
 plp
 farcall X5EasyBodyContact
 jmp FootContactReady
NoFootContact:
 pla
 plp
FootContactReady:
 TnHotGate TnBodyDispatch
 LmGate JnBodyDispatch
 pha
 lda AreaType
 sta GuestBodyStompAllowed
 lda CrossoverBehaviorVersion
 sta GuestBodyNoStomp
 pla
 clc
 rts
.endproc
.proc LmDeathStartGate
 LmGate JnInventoryDeathDispatch
 lda #0
 sta LmStars
 sta LmAttack
 sta LmHealth
 lda #1
 sta LmDirty
 rts
.endproc
.proc LmDeathGate
 LmGate JnDeathDispatch
 farcall MegaManDeathUpdate,jmp
.endproc
.proc LmAdderGate
 TnHotGate TnAdderDispatch
 cmp #15
 beq Own
 farcall JnAdderDispatch,jmp
Own:ldy #0
 sec
 rts
.endproc
.proc LmBoxGate
 TnHotGate TnBoxDispatch
 cmp #15
 beq Own
 farcall JnBoxDispatch,jmp
Own:ldy #0
 rts
.endproc
.proc LmVisibleGate
 TnHotGate TnVisibleDispatch
 LmGate JnVisibleDispatch
 lda LmInvul
 beq Show
 lda FrameCounter
 lsr
 bcs Hide
Show:sec
 rts
Hide:clc
 rts
.endproc
.proc LmStatusNameGate
 LmGate JnStatusName
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
Text:.byte "L MAC   "
.endproc
.popseg
