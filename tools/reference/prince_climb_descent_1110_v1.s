; Prince action7 exports the pose sole before the donor terrain phase.
; A downward frame can cross the whole native pipe top metatile. Present
; the earliest exposed pipe top to native collision for that export, while
; leaving the original source pose, sole history and landing in charge.
.setcpu "6502"
.segment "CLIMB_DESCENT"
.export PpClimbDescentExport

PpClimbDescentExport:
.scope
ActorX = $c60f
ActorAction = $c616
ActorMode = $c618
Foot = $c084
OldFoot = $c086
QueryX = $b369
QueryY = $b36b
ReadPoint = $b310
NativeY = $00bd
VerticalSubtract = $bd45

 lda ActorAction
 cmp #7
 bne Original
 lda ActorMode
 cmp #3
 beq Falling
 cmp #4
 bne Original
Falling:
 lda Foot+1
 ora OldFoot+1
 bne Original
 lda Foot
 cmp #240
 bcs Original
 lda OldFoot
 cmp #32
 bcc Original
 cmp Foot
 bcs Original
 adc #15
 and #$f0
 sta QueryY
 cmp Foot
 bcs Original
 lda #0
 sta QueryY+1
 lda ActorX
 sta QueryX
 lda ActorX+1
 sta QueryX+1
Probe:
 jsr ReadPoint
 bcc NextRow
 cmp #$10
 bcc Original
 cmp #$14
 bcs Original
 dec QueryY
 jsr ReadPoint
 inc QueryY
 bcs Original
 lda QueryY
 sec
 sbc #32
 sta NativeY
 bcs Original
NextRow:
 lda QueryY
 clc
 adc #16
 sta QueryY
 cmp Foot
 bcc Probe
Original:
 ; PpNativeMotionExport always entered the original leaf with SEC.
 sec
 lda Foot
 jmp VerticalSubtract
.endscope
