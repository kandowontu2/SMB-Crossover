.setcpu "6502"
.segment "AMMODROP"

; Private Jay projectile-defeat hook. X remains the native object slot.
; The caller supplies the donor roll inputs from the killed actor and scene.
RecordAmmoDefeat:
 php
 pha
 jsr RollAmmoDrop
 pla
 plp
 jmp NativeDefeat

; Donor 6:881D and 7:CB4E. Keep carry from the first addition for the
; second, and advance the source PRNG even when the private record is busy.
RollAmmoDrop:
 lda DropSourceRoom
 cmp #$0c
 bcs NoDrop
 lda DropSourceMode
 bne NoDrop
 inc DropRandom
 lda DropSourceXLo
 and #$10
 bne ReadSeed
 rol DropRandom
ReadSeed:
 lda DropRandom
 bmi InvertSeed
 eor DropSourceClock
AddPosition:
 clc
 adc DropScreenX
 adc DropCameraXLo
 sta DropRandom
 and #$3f
 beq NoDrop
 and #$07
 bne NoDrop
 lda DropStage
 bne NoDrop
 lda #$23
 sta DropStage
 lda #24
 sta DropTimer
NoDrop:
 rts
InvertSeed:
 eor #$ff
 bpl AddPosition

; 6:8C79 and 7:C4C8 together give 24 actor ticks after the death tick.
; Step exactly once per eligible, onscreen actor update.
AdvanceAmmoDrop:
 lda DropStage
 beq DropDone
 ; Bit 0 identifies the pending explosion. DEC preserves carry, so the
 ; same countdown can retire active ammo or turn a pending actor into ammo.
 lsr a
 bcs CountDrop
 lda DropSourceClock
 lsr a
 bcs DropDone
CountDrop:
 dec DropTimer
 bne DropDone
 bcc ExpireDrop
 lda #$22
 sta DropStage
 lda #$c0
 sta DropVelocityY
 asl a
 sta DropTimer
 rts
ExpireDrop:
 lda #0
 sta DropStage
DropDone:
 rts

; 7:E20E, before terrain collision. The caller commits the resulting
; signed Q4 velocity through its stage collision projection.
AmmoGravity:
 lda DropVelocityY
 cmp #$3c
 beq GravityDone
 clc
 adc #4
 sta DropVelocityY
GravityDone:
 rts

; A and X are the non-wrapping horizontal and vertical magnitudes from
; visible actor/player centers. Donor 6:993D, 7:E7F5 and 7:E82C.
TouchAmmoDrop:
 cmp #$12
 bcs NoTouch
 lda DropStage
 cmp #$22
 bne NoTouch
 cpx #$12
 bcs NoTouch
 lda DropPlayerFlags
 and #$08
 beq ClaimAmmo
 cpx #$0c
 bcs NoTouch
ClaimAmmo:
 lda #$18
 jsr OriginalSoundRequest
 lda #0
 sta DropStage
 lda WeaponAmmo
 clc
 adc #$10
 cmp #$3f
 bcc SaveAmmo
 lda #$3f
SaveAmmo:
 sta WeaponAmmo
 sec
 rts
NoTouch:
 clc
 rts
