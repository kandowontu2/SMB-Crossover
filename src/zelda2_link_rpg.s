; Original USA byte-authenticated numeric rules; SMB delivery is separate.
.pushseg
.segment "Z2_LOGIC"
.proc Z2RecordInit
 lda #0
 ldx #15
Loop: sta InvAmmo,x
 dex
 bpl Loop
 lda #$80
 sta Z2LevelsHi
 lda #$33 ; original fourHP/fourMPcontainers
 sta Z2Containers
 lda #127
 sta Z2Hp
 sta Z2Mp
 rts
.endproc
.proc Z2EnsureInit
 bit Z2LevelsHi
 bmi Done
 jsr Z2RecordInit
Done:rts
.endproc
; A=category0Attack/1Magic/2Life -> A=index0..7 (displaylevel1..8).
.proc Z2GetLevel
 cmp #1
 beq Magic
 bcs Life
 lda Z2LevelsLo
 and #7
 rts
Magic:lda Z2LevelsLo
 lsr
 lsr
 lsr
 and #7
 rts
Life:lda Z2LevelsHi
 and #1
 asl
 asl
 sta R6
 lda Z2LevelsLo
 rol
 rol
 rol
 and #3
 ora R6
 rts
.endproc
; X=category,A=index; preserve all other level/initialized bits.
.proc Z2SetLevel
 and #7
 sta R6
 cpx #1
 beq Magic
 bcs Life
 lda Z2LevelsLo
 and #$f8
 ora R6
 sta Z2LevelsLo
 rts
Magic:lda R6
 asl
 asl
 asl
 sta R6
 lda Z2LevelsLo
 and #$c7
 ora R6
 sta Z2LevelsLo
 rts
Life:lda R6
 and #4
 lsr
 lsr
 sta R7
 lda Z2LevelsHi
 and #$fe
 ora R7
 sta Z2LevelsHi
 lda R6
 and #3
 ror
 ror
 ror
 and #$c0
 sta R7
 lda Z2LevelsLo
 and #$3f
 ora R7
 sta Z2LevelsLo
 rts
.endproc
.proc Z2MaxHp
 lda Z2Containers
 and #7
 jmp Z2ContainerCap
.endproc
.proc Z2MaxMp
 lda Z2Containers
 lsr
 lsr
 lsr
 lsr
 and #7
.endproc
.proc Z2ContainerCap
 clc
 adc #1
 asl
 asl
 asl
 asl
 asl
 sec
 sbc #1
 rts
.endproc
; A=category -> A=thresholdLo,Y=thresholdHi.
.proc Z2Threshold
 sta R5
 jsr Z2GetLevel
 ldx R5
 clc
 adc CategoryOffsets,x
 tax
 lda ThresholdHi,x
 tay
 lda ThresholdLo,x
 rts
.endproc
; A=spellindex0..7 -> actual native MPcost.
.proc Z2SpellCost
 and #7
 asl
 asl
 asl
 sta R5
 lda #1
 jsr Z2GetLevel
 clc
 adc R5
 tax
 lda SpellCosts,x
 rts
.endproc
; A=spell index, C=cast. Matches native one-unit-short exception and lastcast.
.proc Z2TryCast
 cmp #8
 bcs No
 sta R4
 tax
 lda BitMasks,x
 and Z2LearnedSpells
 beq No
 lda Z2Selection
 lsr
 lsr
 lsr
 lsr
 sec
 sbc #1
 cmp R4
 beq No
 lda R4
 jsr Z2SpellCost
 sta R0
 lda Z2Mp
 sec
 sbc R0
 bcs Pay
 cmp #$ff
 bne No
 lda #0
Pay:sta Z2Mp
 ldx R4
 lda BitMasks,x
 ora Z2ActiveSpells
 sta Z2ActiveSpells
 txa
 clc
 adc #1
 asl
 asl
 asl
 asl
 sta R0
 lda Z2Selection
 and #$0f
 ora R0
 sta Z2Selection
 cpx #2
 bne Yes
 lda Z2ActiveSpells
 and #$fb
 sta Z2ActiveSpells
 lda Z2HpPending
 clc
 adc #$30
 bcc :+
 lda #$ff
:sta Z2HpPending
Yes:sec
 rts
No:clc
 rts
.endproc
; Source alternatesMP/HP by frame parity, adds2 and caps inclusively.
.proc Z2RefillTick
 lda FrameCounter
::Z2RefillA:
 and #1
 beq Magic
 lda Z2HpPending
 beq Done
 dec Z2HpPending
 jsr Z2MaxHp
 sta R0
 lda Z2Hp
 clc
 adc #2
 bcs HpCap
 cmp R0
 bcc HpStore
HpCap:lda #0
 sta Z2HpPending
 lda R0
HpStore:sta Z2Hp
 rts
Magic:lda Z2MpPending
 beq Done
 dec Z2MpPending
 jsr Z2MaxMp
 sta R0
 lda Z2Mp
 clc
 adc #2
 bcs MpCap
 cmp R0
 bcc MpStore
MpCap:lda #0
 sta Z2MpPending
 lda R0
MpStore:sta Z2Mp
Done:rts
.endproc
; A=damage class0..7. C=fatalunderflow; HPzero byitself isnotfatal.
.proc Z2Damage
 and #7
 asl
 asl
 asl
 sta R5
 lda #2
 jsr Z2GetLevel
 clc
 adc R5
 tax
 lda DamageTable,x
 ; Shield activebit0 halves source damage, floor exactly.
 pha
 lda Z2ActiveSpells
 and #1
 beq NoShield
 pla
 lsr
 jmp Apply
NoShield:pla
Apply:sta R0
 lda Z2Hp
 sec
 sbc R0
 bcs Alive
 lda #0
 sta Z2Hp
 sec
 rts
Alive:sta Z2Hp
 clc
 rts
.endproc
; A=group1weak/2strong,X=per-enemy randomizer. A=originalitemcode or0.
.proc Z2DropRoll
 stx R4
 cmp #1
 beq Weak
 cmp #2
 bne None
 lda Z2DropCounters
 and #$38
 clc
 adc #8
 cmp #48
 beq StrongDrop
 sta R0
 lda Z2DropCounters
 and #$c7
 ora R0
 sta Z2DropCounters
 bne None
StrongDrop:lda Z2DropCounters
 and #$c7
 sta Z2DropCounters
 lda R4
 and #7
 ora #8
 tax
 lda DropTable,x
 rts
Weak:lda Z2DropCounters
 and #7
 clc
 adc #1
 cmp #6
 beq WeakDrop
 sta R0
 lda Z2DropCounters
 and #$f8
 ora R0
 sta Z2DropCounters
None:lda #0
 rts
WeakDrop:lda Z2DropCounters
 and #$f8
 sta Z2DropCounters
 lda R4
 and #7
 tax
 lda DropTable,x
 rts
.endproc
; A=original90Blue/91Red; original byte-add queue wraps, unlike Life's cap.
.proc Z2JarPickup
 cmp #$90
 beq Blue
 cmp #$91
 bne Done
 lda Z2Containers
 lsr
 lsr
 lsr
 lsr
 and #7
 clc
 adc #1
 asl
 asl
 asl
 asl
 bne Queue
Blue:lda #16
Queue:clc
 adc Z2MpPending
 sta Z2MpPending
Done:rts
.endproc
; A=amountLo,Y=amountHi -> capped16-bit animated queue, no EXPwrap.
.proc Z2QueueExp
 clc
 adc Z2ExpPendingLo
 sta Z2ExpPendingLo
 tya
 adc Z2ExpPendingHi
 sta Z2ExpPendingHi
 bcc Done
 lda #255
 sta Z2ExpPendingLo
 sta Z2ExpPendingHi
Done:rts
.endproc
.proc Z2ExpTick
 lda Z2ExpPendingLo
 ora Z2ExpPendingHi
 beq Done
 ldx #10
 lda Z2ExpPendingHi
 bne Amount
 lda Z2ExpPendingLo
 cmp #10
 bcs Amount
 ldx #1
Amount:stx R0
 lda Z2ExpPendingLo
 sec
 sbc R0
 sta Z2ExpPendingLo
 lda Z2ExpPendingHi
 sbc #0
 sta Z2ExpPendingHi
 lda Z2ExpLo
 clc
 adc R0
 sta Z2ExpLo
 lda Z2ExpHi
 adc #0
 sta Z2ExpHi
Done:rts
.endproc
; A=category; C=purchased. Native deducts cost, retains excess, max8 giveslife.
.proc Z2LevelUp
 cmp #3
 bcs No
 sta R4
 jsr Z2Threshold
 sta R0
 sty R1
 lda Z2ExpLo
 sec
 sbc R0
 sta R2
 lda Z2ExpHi
 sbc R1
 bcc No
 sta Z2ExpHi
 lda R2
 sta Z2ExpLo
 lda R4
 jsr Z2GetLevel
 cmp #7
 bcc Raise
 inc NumberofLives
 bpl :+
 dec NumberofLives
: 
 sec
 rts
Raise:clc
 adc #1
 ldx R4
 jsr Z2SetLevel
 lda R4
 beq Yes
 cmp #1
 beq Magic
 jsr Z2MaxHp
 sta Z2Hp
 jmp Yes
Magic:jsr Z2MaxMp
 sta Z2Mp
Yes:sec
 rts
No:clc
 rts
.endproc
.proc Z2AreaReset
 lda #0
 sta Z2ActiveSpells
 sta Z2AttackStage
 sta Z2AttackTimer
 lda Z2Selection
 and #7
 sta Z2Selection
 rts
.endproc
.proc Z2NewLife
 jsr Z2AreaReset
 jsr Z2MaxHp
 sta Z2Hp
 jsr Z2MaxMp
 sta Z2Mp
 lda #0
 sta Z2HpPending
 sta Z2MpPending
 rts
.endproc
.proc Z2GameOver
 jsr Z2NewLife
 lda #0
 sta Z2ExpLo
 sta Z2ExpHi
 sta Z2ExpPendingLo
 sta Z2ExpPendingHi
 rts
.endproc
CategoryOffsets:.byte 0,8,16
BitMasks:.byte 1,2,4,8,16,32,64,128
.include "zelda2_native_tables.inc"
.popseg
