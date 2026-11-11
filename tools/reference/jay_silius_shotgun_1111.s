.setcpu "6502"

.segment "SHOT"
; PRG6 $81D2/$84C0. Preserve the released input path for other rows.
AlternateInput:
 php
 pha
 lda WeaponCooldown
 bne ReleasedInput
 lda WeaponSelection
 cmp #2
 bne ReleasedInput
 pla
 plp
 ldx #$c0
 stx DispatchLo
 ldy #6
 lda #$84
 sta DispatchHi
 clc
 lda WeaponAmmo
 bne CanFire
 sta WeaponSelection
 rts
ReleasedInput:
 pla
 plp
 jmp StockWeaponInput
CanFire:
 jsr OriginalFreshButtons
 and #$40
 beq ShotReturn
 lda ShotRecords+$f9
 ora ShotRecords+$e9
 ora ShotRecords+$d9
 bne ShotReturn
 lda #2
 jsr SpendAmmo
 lda #4
 sta WeaponCooldown
 lda #2
 sta ShotOrdinal
SpawnEach:
 ldx ShotOrdinal
 lda ShotSlots,x
 tax
 lda #0
 sta ShotRecords+8,x
 lda ShotOrdinal
 asl a
 tay
 lda SpreadVelocity,y
 sta ShotRecords+4,x
 lda SpreadVelocity+1,y
 sta ShotRecords+5,x
 lda #1
 sta ShotRecords+15,x
 jsr SpawnShot
 jsr ApplyShotStance
 dec ShotOrdinal
 bpl SpawnEach
 lda #$12
 jsr OriginalSoundRequest
ShotReturn:
 rts
SpreadVelocity:
 .byte $48,$1a,$48,$e6,$50,0
ShotSlots:
 .byte $f0,$e0,$d0

; PRG6 $8E20. The source clears selection on exact or insufficient ammo.
; A zero-input abort discards the spend return before returning to input.
SpendAmmo:
 sta ScratchDamage
 lda WeaponAmmo
 beq AbortSpend
 lda WeaponAmmo
 sec
 sbc ScratchDamage
 beq EmptyAmmo
 bcs SaveAmmo
EmptyAmmo:
 lda #0
 sta WeaponSelection
SaveAmmo:
 sta WeaponAmmo
 rts
AbortSpend:
 pla
 pla
 rts

; Stock row $8865 still drives all three projectiles. Preserve its exact
; existing zero-VY path. PRG7 $E1E0/$CE63 uses tentative Y for both
; probes and resolves horizontal movement before vertical movement.
ShotgunFlight:
 lda ShotRecords+5,x
 bne SpreadFlight
 jmp StockFlight
SpreadFlight:
 clc
 adc ShotRecords+3,x
 sta NextYLo
 lda ShotRecords+5,x
 bmi NegativeY
 lda #0
 beq AddYHigh
NegativeY:
 lda #$ff
AddYHigh:
 adc ShotRecords+2,x
 sta NextYHi
 lda #0
 sta SideBlocked
 lda ShotRecords+4,x
 beq VerticalProbe
 bmi ProbeLeft
 ldy #6
 bne SideProbe
ProbeLeft:
 ldy #4
SideProbe:
 jsr ShotgunPoint
 beq MoveX
 lda #0
 sta ShotRecords+4,x
 inc SideBlocked
 bne VerticalProbe
MoveX:
 lda ShotRecords+4,x
 clc
 adc ShotRecords+1,x
 sta ShotRecords+1,x
 lda ShotRecords+4,x
 bmi NegativeX
 lda #0
 beq AddXHigh
NegativeX:
 lda #$ff
AddXHigh:
 adc ShotRecords,x
 sta ShotRecords,x
VerticalProbe:
 ldy #2
 lda ShotRecords+5,x
 bpl ReadVertical
 ldy #0
ReadVertical:
 jsr ShotgunPoint
 bne VerticalBlocked
 lda ShotRecords+9,x
 ora #4
 sta ShotRecords+9,x
 lda NextYHi
 sta ShotRecords+2,x
 lda NextYLo
 sta ShotRecords+3,x
 lda SideBlocked
 bne Retire
 jmp StockProject
VerticalBlocked:
 lda ShotRecords+5,x
 pha
 lda #0
 sta ShotRecords+5,x
 pla
 bmi Retire
 lda ShotRecords+9,x
 and #4
 beq Retire
 lda NextYHi
 sta ShotRecords+2,x
 lda NextYLo
 and #$80
 sta ShotRecords+3,x
Retire:
 lda #0
 sta ShotRecords+9,x
 rts

; X=2 in the original CF07 resolver selects D097 in every direction.
; Here X is the preserved stock slot index, while Y holds its direction.
ShotgunPoint:
 sty QueryDirection
 lda NextYHi
 sta QueryY
 and #$0f
 cmp #$0f
 bne CameraRow
 lda ShotRecords+5,x
 bmi RaiseQuery
 dec QueryY
 bne CameraRow
RaiseQuery:
 inc QueryY
CameraRow:
 lda QueryY
 eor CameraYHi
 and #$f0
 beq QueryWorldX
 inc QueryY
QueryWorldX:
 lda ShotRecords,x
 sta QueryX
 jmp JayHostTile

.segment "SUPPORT"
; PRG1 $9644. A host pause UI must supply its established lock and
; input sample. This leaf does not claim ownership of the SMB pause UI.
PausedSelect:
 lda SelectLock
 bne SelectReturn
 lda PadNow
 and #$20
 beq SelectReturn
 ldx #1
 stx ScratchDamage
 lda WeaponSelection
NextSelection:
 clc
 adc ScratchDamage
 jsr EligibleSelection
 bcs NextSelection
 cmp WeaponSelection
 beq SelectReturn
 ldx WeaponSelection
 stx PreviousSelection
 sta WeaponSelection
 lda #$ff
 sta SelectionDirty
 lda ScratchDamage
 cmp #$ff
 beq SaveDirection
 lda #0
SaveDirection:
 sta SelectionDirection
SelectReturn:
 rts
EligibleSelection:
 cmp #6
 beq WrapForward
 cmp #$ff
 bne CheckBit
 lda #5
 bne CheckBit
WrapForward:
 lda #0
CheckBit:
 tax
 beq OwnedSelection
 pha
 lda WeaponUnlocks
RotateMask:
 ror a
 dex
 bne RotateMask
 pla
 bcc LockedSelection
OwnedSelection:
 clc
 rts
LockedSelection:
 sec
 rts

; Fixed PRG7 $E82C. The consumed record is the pickup, not Jay's actor.
AmmoPickup:
 lda #$18
 jsr OriginalSoundRequest
 lda #0
 sta AmmoDropFlags
 lda WeaponAmmo
 clc
 adc #$10
 cmp #$3f
 bcs FullAmmo
 sta WeaponAmmo
 rts
FullAmmo:
 lda #$3f
 sta WeaponAmmo
 rts
