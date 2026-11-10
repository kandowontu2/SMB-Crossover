.setcpu "6502"

.segment "BINDINGS"
; Fixed operands called by the frozen donor motion relocation.
 jmp WeaponInput
 jmp TerrainEvent

; Bank 6 $81D2: cooldown precedes the donor's weapon selector.
WeaponInput:
 lda WeaponCooldown
 beq SelectWeapon
 dec WeaponCooldown
 rts
SelectWeapon:
 lda WeaponSelection
 bne UnsupportedWeapon
 ; Row 0 of the original fixed $CD36 indirect jump, with its ABI.
 ldx #$4e
 stx DispatchLo
 ldy #2
 lda #$84
 sta DispatchHi
 clc
 ; Bank 6 $844E: the stock gun uses the new B press, never held B.
StockShot:
 jsr OriginalFreshButtons
 and #$40
 beq WeaponReturn
 lda #3
 jsr FreeSlot
 bne WeaponReturn
 lda #$12
 jsr OriginalSoundRequest
 lda #4
 sta WeaponCooldown
 lda #$40
 sta ShotRecords+4,x
 lda #0
 sta ShotRecords+5,x
 lda #0
 sta ShotRecords+8,x
 lda #1
 sta ShotRecords+15,x
 jsr SpawnShot
 jmp ApplyShotStance
WeaponReturn:
 rts
UnsupportedWeapon:
 rts

; Bank 6 $A387. X is always $F0, $E0, or $D0 at the indexed read.
FreeSlot:
 sta ScratchDamage
 ldx #$f0
CheckSlot:
 lda ShotRecords+9,x
 beq SlotReturn
 txa
 sec
 sbc #$10
 tax
 dec ScratchDamage
 bne CheckSlot
 lda #$ff
SlotReturn:
 rts

; Bank 6 $8E39 and $8E7B, including both original signed 4.4 tables.
SpawnShot:
 lda ActorFlags
 ora #1
 and #3
 sta ShotRecords+9,x
 and #2
 beq SpawnY
 lda ShotRecords+4,x
 eor #$ff
 clc
 adc #1
 sta ShotRecords+4,x
SpawnY:
 lda ActorYHi
 sta ShotRecords+2,x
 lda ActorYLo
 sta ShotRecords+3,x
 ldy #0
 lda ActorFlags
 and #2
 beq SpawnX
 ldy #2
SpawnX:
 lda ActorXLo
 clc
 adc SpawnOffsetX,y
 sta ShotRecords+1,x
 lda ActorXHi
 adc SpawnOffsetX+1,y
 sta ShotRecords,x
 rts
SpawnOffsetX:
 .byte $c0,$00,$40,$ff

ApplyShotStance:
 tya
 pha
 ldy #0
 lda ActorFlags
 and #8
 beq SpawnOffsetYApply
 lda ActorFlags
 and #4
 bne SpawnOffsetYApply
 ldy #2
SpawnOffsetYApply:
 lda SpawnOffsetY,y
 clc
 adc ShotRecords+3,x
 sta ShotRecords+3,x
 lda SpawnOffsetY+1,y
 adc ShotRecords+2,x
 sta ShotRecords+2,x
 pla
 tay
 rts
SpawnOffsetY:
 .byte $f0,$ff,$b0,$00

; Fixed bank 7 $EA06. Preserve the primary/saved record split and gates.
TerrainEvent:
 sta ScratchDamage
 lda ActorFlags
 and #1
 beq PrimaryActor
 lda SavedFlags
 and #$10
 bne EventReturn
 lda SavedMode
 and #2
 bne EventReturn
 lda #$20
 sta SavedHurt
 lda SavedFlags
 ora #$10
 sta SavedFlags
 and #2
 bne SavedKnockRight
 lda #$fc
 bne SaveSavedKnock
SavedKnockRight:
 lda #4
SaveSavedKnock:
 sta SavedVX
ApplyDamage:
 lda ActorHP
 sec
 sbc ScratchDamage
 sta ActorHP
 lda #$23
 jsr OriginalSoundRequest
EventReturn:
 rts
PrimaryActor:
 lda ActorFlags
 and #$10
 bne EventReturn
 lda ActorMode
 and #2
 bne EventReturn
 lda #$20
 sta ActorHurt
 lda ActorFlags
 ora #$10
 sta ActorFlags
 and #2
 bne PrimaryKnockRight
 lda #$fc
 bne SavePrimaryKnock
PrimaryKnockRight:
 lda #4
SavePrimaryKnock:
 sta ActorVX
 bne ApplyDamage
