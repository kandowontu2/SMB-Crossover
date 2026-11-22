; Newly written controls for this NES mod. No donor instructions or assets.
; Positions/velocities use the established signed 16.8 actor interface.
; PrevPad and Charge are inside the existing accepted-frame rollback block.
.setcpu "6502"

PrevPad = $c097
Charge = $c098
Pad = $c0a8
Hurt = $c34f
Flags = $c030
Pose = $c031
Vx = $c020
Height = $c042
WorkY = $c043
HorizontalBody = $a22d

.segment "ROLL"
OriginalRoll:
 lda Hurt
 and #$40
 beq RollHealthy
 lda #0
 sta Charge
 jmp RollTravel
RollHealthy:
 lda Flags
 bpl RollAir
 lda Pad
 and #4
 beq RollRelease
 lda Charge
 bne RollChargeInput
 ; Running Down+A remains a rolling jump. Charge starts at rest.
 lda Vx
 ora Vx+1
 ora Vx+2
 bne RollTravel
RollChargeInput:
 lda Pad
 and #$80
 beq RollChargeReady
 lda PrevPad
 bmi RollChargeReady
 lda Charge
 cmp #6
 bcs RollChargeReady
 inc Charge
RollChargeReady:
 lda Charge
 beq RollTravel
 lda #0
 sta Vx
 sta Vx+1
 sta Vx+2
 jmp RollCompact
RollRelease:
 lda Charge
 beq RollTravel
 bmi RollTravel
 ; Six charge levels launch at 4,4.5,...6.5 px/update.
 clc
 adc #7
 lsr
 sta Vx+1
 lda #0
 ror
 sta Vx
 lda #0
 sta Vx+2
 lda Flags
 and #2
 beq RollLaunchReady
 sec
 lda #0
 sbc Vx
 sta Vx
 lda #0
 sbc Vx+1
 sta Vx+1
 lda #$ff
 sta Vx+2
RollLaunchReady:
 lda #$80
 sta Charge
 jmp RollCompact
RollAir:
 lda #0
 sta Charge
RollTravel:
 lda Vx
 ora Vx+1
 ora Vx+2
 bne RollFriction
 lda Flags
 bpl RollCompact
 lda Pad
 and #4
 bne RollCompact
 lda Flags
 and #$fe
 sta Flags
 jmp HorizontalBody
RollFriction:
 ; Airborne rolling conserves horizontal momentum.
 lda Flags
 bpl RollCompact
 lda #6
 sta $c014
 lda Vx+2
 bmi RollLeft
 lda Pad
 and #2
 beq RollRightDrag
 lda #48
 sta $c014
RollRightDrag:
 sec
 lda Vx
 sbc $c014
 sta Vx
 lda Vx+1
 sbc #0
 sta Vx+1
 lda Vx+2
 sbc #0
 sta Vx+2
 bpl RollCompact
 jmp RollStop
RollLeft:
 lda Pad
 and #1
 beq RollLeftDrag
 lda #48
 sta $c014
RollLeftDrag:
 clc
 lda Vx
 adc $c014
 sta Vx
 lda Vx+1
 adc #0
 sta Vx+1
 lda Vx+2
 adc #0
 sta Vx+2
 bmi RollCompact
RollStop:
 lda #0
 sta Vx
 sta Vx+1
 sta Vx+2
RollCompact:
 lda #9
 sta Pose
 lda Height
 cmp #24
 beq RollDone
 ; Preserve the foot when changing standing32 to rolling24.
 clc
 lda WorkY
 adc #8
 sta WorkY
 lda WorkY+1
 adc #0
 sta WorkY+1
 lda #24
 sta Height
RollDone:
 rts

; Replaces a constructor STA $C047 with JSR here. Entry A=0.
OriginalMotionReset:
 sta $c047
 sta PrevPad
 sta Charge
 rts

.segment "JUMP"
OriginalJump:
 lda Pad
 eor PrevPad
 and #$80
 sta $c099
 lda Pad
 sta PrevPad
 lda Hurt
 and #$40
 beq JumpHealthy
 lda #0
 sta Charge
 sta $c058
 jmp JumpGravity
JumpHealthy:
 lda Charge
 beq JumpButtons
 bpl JumpGravity
 lda #0
 sta Charge
 jmp JumpGravity
JumpButtons:
 lda Pad
 bmi JumpHeld
 lda $c058
 beq JumpGravity
 lda #0
 sta $c058
 lda $c052
 bpl JumpGravity
 lda $c051
 cmp #$fc
 bcc JumpCut
 bne JumpGravity
 lda $c050
 cmp #$80
 bcs JumpGravity
JumpCut:
 jmp JumpCutTail
JumpHeld:
 lda $c099
 beq JumpGravity
 lda $c056
 bpl JumpGravity
 ; One impulse per fresh grounded A; held A never reapplies it.
 lda #$80
 sta $c050
 lda #$f9
 sta $c051
 lda #$ff
 sta $c052
 lda $c056
 and #$7f
 ora #5
 sta $c056
 lda #1
 sta $c058
 sta $c05e
 jmp JumpGravity

.segment "ROLLJUMP"
OriginalRollingJump:
 jmp OriginalJump
JumpGravity:
 lda $c056
 bmi JumpGroundGravity
 ; Keep the existing fall-speed selection; new jump gravity is 1/4px.
 lda $c052
 bmi JumpAccelerate
 lda $c051
 cmp $c05d
 bcc JumpAccelerate
 lda $c05d
 sta $c051
 lda #0
 sta $c050
 sta $c052
 rts
JumpAccelerate:
 lda #64
 sta $c054
 lda #0
 sta $c053
 sta $c055
 rts
JumpCutTail:
 lda #$80
 sta $c050
 lda #$fc
 sta $c051
 jmp JumpGravity
JumpGroundGravity:
 ; Preserve the incumbent standing/walking fractional floor behavior.
 lda $c05b
 sta $c054
 lda $c05c
 sta $c055
 lda #0
 sta $c053
 rts
