; Original ring hit on authenticated raw43. The ring fixture has a single
; typed type-$55 slot and fixed vertical scroll, with no host tier export.
.setcpu "6502"
.segment "RING_CONTACT"

DamageStatus:
 jsr DamageScope
 bcc StockStatus
 jmp SourceEligible
StockStatus:
 jmp OriginalStatus

DamageScope:
 lda GameEngineSubroutine
 cmp #8
 bne OutOfScope
 lda HostReady
 beq OutOfScope
 lda WorldNumber
 ora LevelNumber
 bne OutOfScope
 lda AreaAddrsLOffset
 cmp #5
 bne OutOfScope
 rts
OutOfScope:
 clc
 rts

SourceEligible:
 lda HurtFlags
 and #$60
 ora RingBCD
 bne HaveProtection
 lda DropFlags
 ora StarFlags
 and #1
HaveProtection:
 sec
 rts

DamageContact:
 jsr DamageScope
 bcc StockContact
 jsr SourceEligible
 beq StockContact
 lda DropFlags
 ora StarFlags
 and #1
 bne ContactHandled
 lda HurtFlags
 and #$40
 bne ContactHandled
 txa
 pha
 ldx #1
ContactPosition:
 lda SourceX,x
 sta ActorX,x
 lda SourceY,x
 sta ActorY,x
 dex
 bpl ContactPosition
 lda SourceFlags
 sta ActorFlags
 inx
 lda DropRecord
 cmp #$55
 bne ContactSetPool
 dex
ContactSetPool:
 stx PoolSlot
 jsr RingHurt
 lda ActorFlags
 sta SourceFlags
 ldx #2
ContactImpulse:
 lda ActorVX,x
 sta SourceVX,x
 lda ActorVY,x
 sta SourceVY,x
 dex
 bpl ContactImpulse
 pla
 tax
ContactHandled:
 sec
 rts
StockContact:
 jmp OriginalInjury

; SMS $510A, before movement. HostStep restores the old input on a failed
; native terrain transaction; restore the pre-stun flags in the same case.
RingMotor:
 lda HurtFlags
 and #$40
 beq FreeMotor
 lda SourceFlags
 pha
 and #$fa
 sta SourceFlags
 lda #0
 sta SourceInput
 jsr NativeFrame
 pla
 bcs StunMotorReturn
 sta SourceFlags
StunMotorReturn:
 rts
FreeMotor:
 jmp NativeFrame

; Finish the accepted source frame after the ring tile probe. $51BC keeps
; the hurt pose through landing, then releases input on the next epoch.
RingPostCommit:
 txa
 pha
 jsr TickDrop
 pla
 tax
 lda HurtFlags
 and #$40
 beq Project
 lda #$1c
 sta SourceWidth
 lda #$10
 sta SourcePose
 lda SourceVY+2
 bmi Project
 lda SourceFlags
 bpl Project
 lda HurtFlags
 and #$bf
 sta HurtFlags
 lda #0
 sta SourceVX
 sta SourceVX+1
 sta SourceVX+2
Project:
 lda SourceX
 jmp HostProjectContinue

TickDrop:
 lda DropRecord
 cmp #$55
 bne DropWait
 lda DropFlags
 and #1
 bne DropStep
 lda SourceTick
 and #7
 beq DropStep
DropWait:
 rts
DropStep:
 lda DropRecord+24
 ora #$20
 sta DropRecord+24
 lda DropFlags
 ora #1
 sta DropFlags
 lda SourceTick
 and #1
 beq DropHide
 ldx DropRecord+18
 lda DropSprites,x
 sta DropRecord+15
 lda #$7c
 bne DropSpriteHigh
DropHide:
 sta DropRecord+15
DropSpriteHigh:
 sta DropRecord+16
 clc
 lda DropRecord+10
 adc #$20
 sta DropRecord+10
 lda DropRecord+11
 adc #0
 sta DropRecord+11
 lda DropRecord+12
 adc #0
 sta DropRecord+12
 clc
 lda ScrollY+1
 adc #1
 cmp DropRecord+6
 bcc DropDespawn
 bne DropVisible
 lda ScrollY
 cmp DropRecord+5
 bcc DropDespawn
DropVisible:
 dec DropRecord+17
 bne DropIntegrate
 lda #6
 sta DropRecord+17
 ldx DropRecord+18
 inx
 cpx #6
 bcc DropPhase
 ldx #0
DropPhase:
 stx DropRecord+18
 jmp DropIntegrate
DropDespawn:
 lda #$ff
 sta DropRecord
 lda DropFlags
 and #$fe
 sta DropFlags
DropIntegrate:
 ; The private record starts with zero horizontal velocity and only this
 ; type-$55 updater owns it. Integrate Y even on the despawn update.
 clc
 lda DropRecord+4
 adc DropRecord+10
 sta DropRecord+4
 lda DropRecord+5
 adc DropRecord+11
 sta DropRecord+5
 lda DropRecord+6
 adc DropRecord+12
 sta DropRecord+6
 rts
DropSprites:
 .byte $29,$31,$39,$29,$31,$39
