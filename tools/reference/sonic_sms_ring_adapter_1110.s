; Portable SMS ring acquisition and damage onset.
; Caller supplies RingContext and code placement. No mapper or host RAM ABI.
; A and carry on AcquireRingTile are the replacement tile and collected bit.
; AwardRings accepts the donor's packed $01/$10. RingHurt returns
; A=0 blocked, A=1 stunned, A=2 source death. PoolSlot=$ff means full.
; The caller supplies the first free pool record and consumes the cues.

.setcpu "6502"
.segment "RINGS"

RingBCD    = RingContext
RingLives  = RingContext+1
ActorX     = RingContext+2
ActorY     = RingContext+4
ScrollY    = RingContext+6
SparkX     = RingContext+8
SparkY     = RingContext+10
SparkTimer = RingContext+12
RingSfx    = RingContext+13
RingMusic  = RingContext+14
HurtFlags  = RingContext+15
StarFlags  = RingContext+16
DropFlags  = RingContext+17
DeathFlags = RingContext+18
ActorFlags = RingContext+19
ActorVX    = RingContext+20
ActorVY    = RingContext+23
ActorInput = RingContext+26
DeathTimer = RingContext+27
PoolSlot   = RingContext+28
RingMask   = RingContext+29
DropRecord = RingContext+30
ContextEnd = RingContext+56

; SMS 4C28 and 4DEF use the tile queried at (X+12,Y+8). The caller
; owns the tile map and applies the returned replacement on success.
AcquireRingTile:
 tay
 and #$7f
 cmp #$79
 bcc RingMiss
 sec
 lda ActorY
 sbc ScrollY
 tax
 lda ActorY+1
 sbc ScrollY+1
 bcc RingMiss
 bne RingSide
 cpx #16
 bcc RingMiss
RingSide:
 clc
 lda ActorX
 adc #12
 and #$10
 beq RingLeft
 tya
 and #2
 beq RingMiss
 bne RingBit
RingLeft:
 tya
 and #1
 beq RingMiss
RingBit:
 sta RingMask
 clc
 lda ActorX
 adc #12
 and #$f0
 sta SparkX
 lda ActorX+1
 adc #0
 sta SparkX+1
 clc
 lda ActorY
 adc #8
 and #$e0
 ora #8
 sta SparkY
 lda ActorY+1
 adc #0
 sta SparkY+1
 lda #6
 sta SparkTimer
 lda #1
 jsr AwardRings
 tya
 eor RingMask
 sec
 rts
RingMiss:
 tya
 clc
 rts

; SMS 39AC DAA for the two actual packed award operands. RP2A03
; arithmetic is binary, so correct the ones digit explicitly.
AwardRings:
 clc
 adc RingBCD
 pha
 and #$0f
 cmp #10
 pla
 bcc AwardCheck100
 adc #5
AwardCheck100:
 cmp #$a0
 bcc AwardNormal
 sbc #$a0
 sta RingBCD
 inc RingLives
 lda #9
 bne AwardCue
AwardNormal:
 sta RingBCD
 lda #2
AwardCue:
 sta RingSfx
 rts

; SMS 35FD through 36BD. Damage, shield, drop immunity and star
; immunity are independent of the SMB status and timer variables.
RingHurt:
 lda DropFlags
 ora StarFlags
 and #1
 bne HurtBlocked
 lda HurtFlags
 and #$40
 beq HurtCheckShield
HurtBlocked:
 lda #0
 rts
HurtCheckShield:
 lda HurtFlags
 and #$20
 bne HurtStun
 lda RingBCD
 bne HurtRings
 jmp HurtDeath
HurtRings:
 lda #0
 sta RingBCD
 lda PoolSlot
 cmp #$ff
 beq HurtStun
 lda #$55
 sta DropRecord
 lda ActorX
 sta DropRecord+2
 lda ActorX+1
 sta DropRecord+3
 lda ActorY
 sta DropRecord+5
 lda ActorY+1
 sta DropRecord+6
 lda #0
 sta DropRecord+10
 sta DropRecord+18
 lda #$fc
 sta DropRecord+11
 lda #$ff
 sta DropRecord+12
 lda #6
 sta DropRecord+17
HurtStun:
 lda #0
 sta ActorVY
 sta ActorVX
 lda ActorFlags
 and #$10
 beq HurtDry
 lda #$fe
 bne HurtVertical
HurtDry:
 lda #$fc
HurtVertical:
 sta ActorVY+1
 lda #$ff
 sta ActorVY+2
 lda ActorFlags
 and #2
 beq HurtFacingRight
 lda ActorFlags
 ora #$12
 sta ActorFlags
 lda #0
 ldx #2
 bne HurtHorizontal
HurtFacingRight:
 lda #$ff
 ldx #$fe
HurtHorizontal:
 stx ActorVX+1
 sta ActorVX+2
 lda HurtFlags
 and #$df
 ora #$40
 sta HurtFlags
 lda #$ff
 sta ActorInput
 lda #$11
 sta RingSfx
 lda #1
 rts
HurtDeath:
 lda DeathFlags
 ora #1
 sta DeathFlags
 lda ActorFlags
 ora #$80
 sta ActorFlags
 lda #0
 sta ActorVY
 lda #$fa
 sta ActorVY+1
 lda #$ff
 sta ActorVY+2
 lda #96
 sta DeathTimer
 lda HurtFlags
 and #$9f
 sta HurtFlags
 lda StarFlags
 and #$fe
 sta StarFlags
 lda #10
 sta RingMusic
 lda #2
 rts
