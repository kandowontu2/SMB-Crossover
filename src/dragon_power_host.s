; Host-coordinate/terrain boundary for the genuine side-view kernel.
; No native scene tilemap/NPC RAM is emulated. Bank126/127 resident helpers only.
.pushseg
.segment "DRAGON_POWER_CORE"
DpHungerPeriod=DpBorrow+6         ; explicit source scene period1/3;0pending.
.proc DpSceneKey
 lda AreaType
 .repeat 5
 asl
 .endrepeat
 ora AreaAddrsLOffset
 rts
.endproc
.proc DpSourceFrame
 ; Complete original3:9867 caller body, with genuine translated targets.
 jsr DpNE82E
 jmp DpNEC4D
.endproc
.proc DpEnsure
 lda SelectedCharacter
 cmp #CHARACTER_DRAGON_POWER
 bne Foreign
 lda DpReady
 cmp #$44
 bne NewLife
 lda NumberofLives
 sec
 sbc DpLife
 bmi NewLife
 lda NumberofLives
 sta DpLife                     ; INC gains/wrap retain earned equipment.
 jsr DpSceneKey
 cmp DpArea
 bne Area
 lda WorldNumber
 cmp DpWorld
 beq Ready
 bne Area
NewLife:
 lda #100                      ; authentic original initial health.
 sta DpHP
 lda #0
 sta DpPole
 sta DpWaves
 sta DpFlags
 sta DpPower
 sta DpHunger
 lda #$44
 sta DpReady
Area:
 lda #0
 ldx #$7f
Clear:sta $5c00,x
 dex
 bpl Clear
 lda #1
 sta DpAction                  ; caller's real spawn replaces original room table.
 lda #2
 sta DpPose
 lda NumberofLives
 sta DpLife
 jsr DpSceneKey
 sta DpArea
 lda WorldNumber
 sta DpWorld
 lda SavedJoypadBits
 sta DpPrevious
 lda #$ff
 sta DpPaletteAck
Ready:sec
 rts
Foreign:clc
 rts
.endproc
.proc DpSpawnHook
 ; Original ECBA is a room-specific XY table. Actual host spawn owns XY.
 ; Kernel state0 is diagnostic only; ordinary DpEnsure starts at state1.
 rts
.endproc
.proc DpSceneExitRequest
 lda DpBorrow+7                ; projected originalD7; distinct host output.
 ora #$80
 sta DpBorrow+7
 rts
.endproc
.proc DpAudioRequest
 ; Explicit source event output, not a substituted shared waveform or live hook.
 ; Mimic genuine98A8 request-pointer arithmetic and finalAXYP; store cue first,
 ; count last. Consumer may run ONLY after complete DpMovement, not in NMI yet.
 sta DpBorrow+2                ; source14
 sta DpBorrow+4                ; source16
 txa
 pha
 tya
 pha
 lda #0
 asl DpBorrow+2
 rol a
 asl DpBorrow+2
 rol a
 sta DpBorrow+3
 lda #$40
 clc
 adc DpBorrow+2
 sta DpBorrow+2
 lda #$80
 adc DpBorrow+3
 sta DpBorrow+3
 php
 ldx DpCueCount
 cpx #4
 bcs Overflow
 lda DpBorrow+4
 sta DpCues,x
 inx
 stx DpCueCount
 jmp Finished
Overflow:lda #1
 sta DpCueOverflow             ; fail-closed integration diagnostic, never silent.
Finished:plp
 pla
 tay
 pla
 tax
 rts
.endproc
.proc DpHostTileQuery
 ; Original ED2C interface A=screenY,Y=screenX. Return source class and
 ; original02/03/Y tile-index state. Preserve original carry at normal load.
 cmp #$f0
 bcc Query
 lda #1
 rts
Query:
 sty DpMath+2
 sta DpMath+3
 and #$f0
 sta R1
 tya
 lsr
 lsr
 lsr
 lsr
 ora R1
 sta DpTileIndex
 php
 txa
 pha
 lda R0
 sta DpSavedR0
 lda R1
 sta DpSavedR1
 lda DpMath+3
 cmp #32
 bcc Empty
 and #$f0
 sec
 sbc #32
 sta DpProbeY
 lda ScreenLeft_X_Pos
 clc
 adc DpMath+2
 sta DpProbeX
 lda ScreenLeft_PageLoc
 adc #0
 sta DpProbePage
 and #1
 asl
 asl
 asl
 asl
 sta R0
 lda DpProbeX
 lsr
 lsr
 lsr
 lsr
 ora R0
 jsr GetBlockBufferAddr         ; actual native block-buffer addressing.
 ldy DpProbeY
 lda (R6),y
 beq Empty
 cmp #$23
 beq Empty
 cmp #$26
 beq Empty
 cmp #$c2
 beq Empty
 cmp #$c3
 beq Empty
 cmp #$5f
 beq Empty
 cmp #$60
 beq Empty
 cmp #$51
 beq Brick
 cmp #$52
 bne Attribute
 ; Native source differentiates foundation from the identical brick art.
 clc
 lda R6
 adc #<(MmSolidTerrain-Block_Buffer_1)
 sta R6
 lda R7
 adc #>(MmSolidTerrain-Block_Buffer_1)
 sta R7
 lda (R6),y
 beq Brick
 bne Solid
Attribute:tay
 lda MTileAttribute,y
 and #MTILE_SOLID
 beq Empty
Solid:lda #$75                  ; source solid native tile property.
 bne Result
Brick:lda #$95                  ; source breakable class; genuine block outputs.
 bne Result
Empty:lda #0
Result:sta DpTileResult
 lda DpSavedR0
 sta R0
 lda DpSavedR1
 sta R1
 pla
 tax
 plp
 ldy DpTileIndex
 lda DpTileResult
 rts
.endproc
.proc DpMovement
 jsr DpEnsure
 jcc Done
 lda GamePauseStatus
 and #1
 jne Done
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda TimerControl
 jne Done
 lda #0
 sta DpCueCount
 sta DpCueOverflow
 ; Original block commands remain pending until the genuine host block/VRAM
 ; consumer acknowledges them. Never discard a command at the next tick.
 lda DpPole
 and #1
 sta R0
 lda DpActionFlags
 and #$fe
 ora R0
 sta DpActionFlags
 lda SavedJoypadBits
 tax
 lda DpInputReverse,x
 sta DpHeld
 lda SavedJoypadBits
 eor DpPrevious
 and SavedJoypadBits
 tax
 lda DpInputReverse,x
 sta DpFresh
 lda SavedJoypadBits
 sta DpPrevious
 lda Player_Rel_XPos
 sta DpX
 sta DpOldX
 lda Player_Y_Position
 clc
 adc #16
 sta DpY
 sta DpOldY
 lda DpShotState
 pha
 jsr DpSourceFrame             ; action AND projectile, original caller order.
 pla
 and #$0f
 bne ShotActive
 lda DpShotState
 and #$0f
 beq ShotActive
 lda ScreenLeft_X_Pos
 sta DpShotCamera
 lda ScreenLeft_PageLoc
 sta DpShotCamera+1
ShotActive:
 lda DpX
 sec
 sbc DpOldX
 sta DpDeltaX
 sta Player_X_Scroll
 clc
 adc Player_X_Position
 sta Player_X_Position
 lda #0
 ldx DpDeltaX
 bpl :+
 lda #$ff
:adc Player_PageLoc
 sta Player_PageLoc
 lda DpY
 sec
 sbc DpOldY
 sta DpDeltaY
 clc
 adc Player_Y_Position
 sta Player_Y_Position
 lda #0
 ldx DpDeltaY
 bpl :+
 lda #$ff
:adc Player_Y_HighPos
 sta Player_Y_HighPos
 lda DpDeltaY
 sta Player_Y_Speed
 lda DpDeltaX
 asl
 asl
 asl
 asl
 sta Player_X_Speed
 bpl :+
 eor #$ff
 clc
 adc #1
:sta Player_XSpeedAbsolute
 lda #1
 ldx DpHorizontal
 bpl :+
 lda #2
:sta PlayerFacingDir
 lda #1
 ldx DpAction
 cpx #1
 bne :+
 lda #0
:sta Player_State
 lda #0
 sta PlayerSize
 sta CrouchingFlag
 lda DpAction
 cmp #12
 bne :+
 inc CrouchingFlag
:lda DpPower
 sta PlayerStatus
 inc DpClock
 inc DpSecondPhase
 lda DpSecondPhase
 cmp #60
 bcc Health
 lda #0
 sta DpSecondPhase
Health:jsr DpHealthTick
Done:rts
.endproc
.proc DpHealthTick
 ; Source0:9A33/9A80: actual queued damage drains1HP every8updates.
 lda DpProtection
 beq Hunger
 lda DpClock
 and #7
 bne Hunger
 dec DpProtection
 jsr Debit
Hunger:
 lda DpHungerPeriod
 beq Done
 lda DpSecondPhase
 bne Done
 inc DpHunger
 lda DpHunger
 cmp DpHungerPeriod
 bcc Done
 lda #0
 sta DpHunger
Debit:
 lda DpFlags
 and #$20
 bne Done
 lda DpHP
 beq Done
 dec DpHP
 lda DpHP
 cmp #30
 bne Done
 lda #$64
 jsr DpAudioRequest
 lda #$65
 jsr DpAudioRequest
Done:rts
.endproc
.proc DpPickup
 pha
 jsr DpEnsure
 bcc Foreign
 pla
 cmp #2
 bcs No
 cmp #1
 beq Flower
 lda #1                       ; approved NEW crossover mapping, native pole bit.
 sta DpPole
 lda DpPower
 bne KeepTier
 lda #1
 sta DpPower
KeepTier:
 lda DpHP
 clc
 adc #20
 bcs Cap
 cmp #150
 bcc Health
Cap:lda #150
Health:sta DpHP
 lda #0                       ; authentic food helper also restarts hunger age.
 sta DpHunger
 sec
 rts
Flower:
 lda DpWaves
 and #$3f
 beq Add
 lda DpWaves
 and #$c0
 bne Accepted                  ; native priority refuses plain downgrade/refill.
Add:lda DpWaves
 and #$3f
 clc
 adc #3
 cmp #61
 bcc Stock
 lda #60
Stock:sta DpWaves
 lda #2
 sta DpPower
Accepted:sec
 rts
Foreign:pla
No:clc
 rts
.endproc
.proc DpInjuryStart
 pha
 jsr DpEnsure
 bcc Foreign
 pla
 sta DpBorrow
 lda DpProtection
 bne Protected
 lda DpBorrow                  ; actual original damage budget, not immediateHP.
 sta DpProtection
 sec
 rts
Foreign:pla
Protected:clc
Done:rts
.endproc
.proc DpCollisionBounds
 lda SelectedCharacter
 cmp #CHARACTER_DRAGON_POWER
 bne Done
 lda #0
 sta R0
 sta R1
 lda #16
 sta R2
 lda #32
 sta R3
Done:
 rts
.endproc
.proc DpStompPolicy
 lda SelectedCharacter
 cmp #CHARACTER_DRAGON_POWER
 bne Hard
 lda CrossoverBehaviorVersion
 beq Easy
Hard:
 clc
 rts
Easy:sec
 rts
.endproc
.export DpEnsure,DpMovement,DpPickup,DpInjuryStart,DpCollisionBounds,DpStompPolicy
.export DpHealthTick,DpHungerPeriod
.export DpSourceFrame
.export DpHostTileQuery,DpAudioRequest,DpSpawnHook,DpSceneExitRequest
DpInputReverse:
.repeat 256,I
 .byte ((I&1)<<7)|((I&2)<<5)|((I&4)<<3)|((I&8)<<1)|((I&16)>>1)|((I&32)>>3)|((I&64)>>5)|((I&128)>>7)
.endrepeat
DpHostEnd:
.popseg
