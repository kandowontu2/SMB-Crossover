.pushseg
.segment "FINAL_FANTASY_CORE"
.export FfActionTick,FfWeapons,FfEnemyContact,FfForgetEnemy,FfProjectileEntry
; WarriorOfLight100ms attack frames6..10; BlackMage500ms prepare/300ms cast.
; Fixed60Hz logical-update adapter; pauses/lag do not create extra source ticks.
.proc FfActionTick
 lda FfAction
 beq Input
 inc FfAge
 cmp #1
 beq Melee
 cmp #2
 jeq Prepare
 lda FfAge
 cmp #18
 bcc Done
 bcs End
Melee:
 lda FfAge
 cmp #30
 bcc Done
End:lda #0
 sta FfAction
 sta FfAge
Input:
 lda FfVariant
 cmp #4
 bcs Done
 lda FfFresh
 and #B_Button
 beq Done
 lda SavedJoypadBits
 and #(Up_Dir|Down_Dir)
 cmp #(Up_Dir|Down_Dir)
 beq Done
 sta FfTemp
 ldx FfVariant
 cpx #2
 beq Black
 cpx #1
 beq White
 lda FfTemp
 bne Done                      ; real Fighter/Thief up/down attacks are empty.
Attack:
 lda #1
 sta FfAction
 lda #0
 sta FfAge
 sta FfHits
 lda #Sfx_Fireball
 sta Square1SoundQueue          ; disclosed existing crossover audio cue.
Done:rts
Black:
 ldx #1
 lda FfTemp
 beq Spell
 ldx #2
 cmp #Up_Dir
 beq Spell
 ldx #3
 bne Spell
White:
 lda FfTemp
 beq Attack                    ; authored White attack poses, new staff hit rule.
 cmp #Down_Dir
 beq Light
 lda FfHealCharges
 beq Done
 lda MmDeathFlag
 bne Done
 lda FfPower
 cmp FfEarned
 bcs Done
 ldx #5                        ; finite earned Heal, never dead/cap healing.
 bne Spell
Light:ldx #4                    ; close defensive burst uses authored Ice art.
Spell:
 stx FfSpell
 lda #2
 sta FfAction
 lda #0
 sta FfAge
 rts
Prepare:
 lda FfAge
 cmp #30
 bcc Done
 lda FfSpell
 cmp #5
 bne Allocate
 lda FfHealCharges
 jeq End
 lda MmDeathFlag
 jne End
 lda FfPower
 cmp FfEarned
 jcs End
 dec FfHealCharges
 inc FfPower
 lda FfPower
 sta PlayerStatus
 lda #Sfx_PowerUpGrab
 sta Square2SoundQueue
 jmp Cast
Allocate:
 jsr FfAllocate
 bcc Wait                      ; bounded pool admission never destroys old spell.
Cast:lda #3
 sta FfAction
 lda #0
 sta FfAge
 rts
Wait:lda #30
 sta FfAge
 rts
.endproc
.proc FfAllocate
 ldx #0
Loop:lda FfProjectile,x
 beq Found
 txa
 clc
 adc #12
 tax
 cpx #36
 bcc Loop
 clc
 rts
Found:
 stx FfSlot
 lda #0
 ldy #11
Clear:sta FfProjectile,x
 inx
 dey
 bpl Clear
 ldx FfSlot
 lda FfSpell
 sta FfProjectile,x
 lda FfPower
 sta FfProjectile+10,x
 lda PlayerFacingDir
 sta FfProjectile+8,x
 lda Player_Y_Position
 clc
 adc #18                       ; source foot+32-13.5; retained half below.
 sta FfProjectile+7,x
 lda #$80
 sta FfProjectile+11,x
 lda FfSpell
 cmp #2
 bne :+
 lda #125                      ; source (0+480)/2+10 Flash /2 =125NES.
 sta FfProjectile+7,x
 lda #0
 sta FfProjectile+11,x
: 
 lda #19
 ldy FfSpell
 cpy #1
 beq Offset
 cpy #4
 beq Offset
 lda #50
Offset:sta FfTemp
 lda Player_X_Position
 clc
 adc #8                        ; native body anchor -> source foot center.
 sta FfProjectile+4,x
 lda Player_PageLoc
 adc #0
 sta FfProjectile+5,x
 lda PlayerFacingDir
 cmp #2
 beq Left
 lda FfProjectile+4,x
 clc
 adc FfTemp
 sta FfProjectile+4,x
 lda FfProjectile+5,x
 adc #0
 sta FfProjectile+5,x
 sec
 rts
Left:
 lda FfProjectile+4,x
 sec
 sbc FfTemp
 sta FfProjectile+4,x
 lda FfProjectile+5,x
 sbc #0
 sta FfProjectile+5,x
 sec
 rts
.endproc
; Once after movement per actual active GameLoop. No input/resource ownership.
.proc FfWeapons
 lda SelectedCharacter
 cmp #CHARACTER_FINAL_FANTASY
 jne Done
 lda TimerControl
 ora MmDeathFlag
 jne Done
 lda GamePauseStatus
 and #1
 jne Done
 lda GameEngineSubroutine
 cmp #8
 jne Done
 jsr FfAnimationTick
 ldx #0
Loop:
 lda FfProjectile,x
 jeq Next
 cmp #1
 bne Animation
 lda FfProjectile+8,x
 cmp #2
 beq Left
 clc
 lda FfProjectile+6,x
 adc #$c0                      ; source450/120=3.75px/update.
 sta FfProjectile+6,x
 lda FfProjectile+4,x
 adc #3
 sta FfProjectile+4,x
 lda FfProjectile+5,x
 adc #0
 sta FfProjectile+5,x
 jmp Animation
Left:
 sec
 lda FfProjectile+6,x
 sbc #$c0
 sta FfProjectile+6,x
 lda FfProjectile+4,x
 sbc #3
 sta FfProjectile+4,x
 lda FfProjectile+5,x
 sbc #0
 sta FfProjectile+5,x
Animation:
 lda FfProjectile,x
 cmp #1
 bne Moderate
 lda FfClock
 and #1
 beq Cull
 bne Advance
Moderate:
 lda FfClock
 and #2
 beq Cull
Advance:
 inc FfProjectile+1,x
 lda FfProjectile,x
 tay
 lda FfProjectile+1,x
 cmp Frames-1,y
 bcc Cull
 cpy #1
 bne Clear
 lda #0
 sta FfProjectile+1,x
Cull:
 ; Original whole-object offscreen disposal, using repaired authored widths.
 ; Fire46/2=23,Bolt60/2=30,Ice73/2 roundsout37; strict source edge test.
 ldy FfProjectile,x
 lda Radius-1,y
 sta FfTemp2
 sec
 lda FfProjectile+4,x
 sbc ScreenLeft_X_Pos
 sta FfTemp
 lda FfProjectile+5,x
 sbc ScreenLeft_PageLoc
 beq Next
 cmp #$ff
 bne RightCull
 lda #0
 sec
 sbc FfTemp2
 sta FfTemp2
 lda FfTemp
 cmp FfTemp2
 bcs Next
 bcc Clear
RightCull:
 cmp #1
 bne Clear
 lda FfTemp
 cmp FfTemp2
 bcc Next
 beq Next
Clear:lda #0
 sta FfProjectile,x
Next:txa
 clc
 adc #12
 tax
 cpx #36
 jcc Loop
Done:rts
Frames:.byte 3,6,5,5
Radius:.byte 23,30,37,37
.endproc
; Shared AnimationTimers33ms /75ms clocks. Every source projectile receives
; the SAME event, including newly admitted instances in this update's phase.
; Fixed60Hz event ordering is an explicit host adapter, not Flash VM equality.
.proc FfAnimationTick
 lda #0
 sta FfClock
 clc
 lda FfFireClock
 adc #$e8
 sta FfFireClock
 lda FfFireClock+1
 adc #3
 sta FfFireClock+1
 cmp #7
 bcc Moderate
 bne Fire
 lda FfFireClock
 cmp #$bc
 bcc Moderate
Fire:
 sec
 lda FfFireClock
 sbc #$bc
 sta FfFireClock
 lda FfFireClock+1
 sbc #7
 sta FfFireClock+1
 lda #1
 sta FfClock
Moderate:
 clc
 lda FfModerateClock
 adc #$e8
 sta FfModerateClock
 lda FfModerateClock+1
 adc #3
 sta FfModerateClock+1
 cmp #$11
 bcc Done
 bne Event
 lda FfModerateClock
 cmp #$94
 bcc Done
Event:
 sec
 lda FfModerateClock
 sbc #$94
 sta FfModerateClock
 lda FfModerateClock+1
 sbc #$11
 sta FfModerateClock+1
 lda FfClock
 ora #2
 sta FfClock
Done:rts
.endproc
; X=actual projectile slot0/12/24 => A=authored render entry or Cclear.
.proc FfProjectileEntry
 cpx #0
 beq Valid
 cpx #12
 beq Valid
 cpx #24
 bne No
Valid:lda FfProjectile,x
 jeq No
 cmp #5
 bcs No
 tay
 lda FfProjectile+1,x
 cmp FfWeapons::Frames-1,y
 bcs No
 lda Entry-1,y
 clc
 adc FfProjectile+1,x
 sec
 rts
No:clc
 rts
Entry:.byte 144,152,147,147
.endproc
; X=eligible native enemy identity0..5; caller supplies ACTUAL bounding box.
; A=$FF melee or actual projectile offset0/12/24. Cset/FfDamage are an exact
; accepted hit receipt; caller must apply source HP units, score and effects.
; No stock Samus/MegaMan damage substitution and no world-state writes here.
.proc FfEnemyContact
 cpx #6
 jcs No
 sta FfSlot
 lda Bits,x
 sta FfEnemyBit
 lda FfSlot
 cmp #$ff
 bne Shot
 lda FfVariant
 cmp #4
 jcs No
 cmp #2
 jeq No
 lda FfAction
 cmp #1
 jne No
 lda FfHits
 and FfEnemyBit
 jne No
 lda #16
 sta FfRectW
 lda #25
 sta FfRectH
 lda Player_Y_Position
 clc
 adc #6
 sta FfRectY
 lda Player_X_Position
 clc
 adc #15
 sta FfRectX
 lda Player_PageLoc
 adc #0
 sta FfRectPage
 lda PlayerFacingDir
 cmp #2
 bne MeleeDamage
 lda FfRectX
 sec
 sbc #30
 sta FfRectX
 lda FfRectPage
 sbc #0
 sta FfRectPage
MeleeDamage:
 ldx FfVariant
 lda Damage,x
 sta FfDamage
 lda FfPower
 cmp #2
 bne Test
 lda Flower,x
 sta FfDamage
 jmp Test
Shot:
 tax
 jsr FfProjectileEntry
 jcc No
 lda FfProjectile+9,x
 and FfEnemyBit
 jne No
 ldy FfProjectile,x
 lda Width-1,y
 sta FfRectW
 lda Height-1,y
 sta FfRectH
 lda DamageShot-1,y
 sta FfDamage
 lda FfProjectile+10,x
 cmp #2
 bne ShotRect
 lda FfDamage
 clc
 adc #50
 sta FfDamage
ShotRect:
 lda FfRectW
 lsr
 sta FfTemp
 lda FfProjectile+4,x
 sec
 sbc FfTemp
 sta FfRectX
 lda FfProjectile+5,x
 sbc #0
 sta FfRectPage
 lda FfRectH
 lsr
 sta FfTemp
 lda FfProjectile+7,x
 sec
 sbc FfTemp
 sta FfRectY
 cpy #2
 bne Test
 lda #5                        ; original Bolt HRect27x240 atviewport center125.
 sta FfRectY
Test:
 ; Full page-aware half-open rectangle intersection, target width/height
 ; must be1..64 (actual host eligibility adapter owns and validates them).
 lda FfTargetW
 jeq No
 cmp #65
 jcs No
 lda FfTargetH
 jeq No
 cmp #65
 jcs No
 sec
 lda FfTargetX
 sbc FfRectX
 sta FfTemp
 lda FfTargetPage
 sbc FfRectPage
 sta FfTemp2
 clc
 lda FfTemp
 adc FfTargetW
 sta FfTemp
 lda FfTemp2
 adc #0
 bne No
 lda FfTemp
 beq No
 lda FfRectW
 clc
 adc FfTargetW
 cmp FfTemp
 bcc No
 beq No
 sec
 lda FfTargetY
 sbc FfRectY
 sta FfTemp
 lda #0
 sbc #0
 sta FfTemp2
 clc
 lda FfTemp
 adc FfTargetH
 sta FfTemp
 lda FfTemp2
 adc #0
 sta FfTemp2
 bmi No
 ora FfTemp
 beq No
 lda FfRectH
 clc
 adc FfTargetH
 tay
 lda #0
 adc #0
 cmp FfTemp2
 bcc No
 bne VerticalWide
 tya
 cmp FfTemp
 bcc No
 beq No
VerticalWide:
 lda FfSlot
 cmp #$ff
 bne MarkShot
 lda FfHits
 ora FfEnemyBit
 sta FfHits
 sec
 rts
MarkShot:tax
 lda FfProjectile+9,x
 ora FfEnemyBit
 sta FfProjectile+9,x
 sec
 rts
No:clc
 rts
Bits:.byte 1,2,4,8,16,32
Damage:.byte 75,25,0,10
Flower:.byte 150,50,0,25
Width:.byte 16,28,48,48
Height:.byte 19,240,49,49
DamageShot:.byte 100,150,100,25
.endproc
; Must be called when a genuine enemy object identity is destroyed/reused.
; Source dictionaries key objects, not recycled six-slot native indices.
.proc FfForgetEnemy
 cpx #6
 bcs Done
 lda FfEnemyContact::Bits,x
 eor #$ff
 sta FfTemp
 and FfHits
 sta FfHits
 ldx #0
Loop:lda FfProjectile+9,x
 and FfTemp
 sta FfProjectile+9,x
 txa
 clc
 adc #12
 tax
 cpx #36
 bcc Loop
Done:rts
.endproc
.popseg
