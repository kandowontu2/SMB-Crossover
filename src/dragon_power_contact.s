; Original USA0:FBB9..FC4E point construction/acceptance, source coordinates.
; Host supplies actual eligible actor coordinates in six typed target slots.
; This is an acceptance API, not a fake universal enemy-HP damage routine.
DpTargetX=$5c70
DpTargetY=$5c76
.pushseg
.segment "DRAGON_POWER_CORE"
.proc DpBuildAttackPoint
 lda SelectedCharacter
 cmp #CHARACTER_DRAGON_POWER
 beq Owned
 sec
 rts
Owned:jmp DpSourceBuildPoint
.endproc
.proc DpSourceBuildPoint
 lda #0
 sta DpAttackKind
 lda #$ff
 sta DpAttackX
 sta DpAttackY
 lda DpShotState
 and #$0f
 bne Wave
 ldy #0
 lda DpPose
 cmp #5
 beq Melee
 cmp #$15
 beq Melee
 iny
 cmp #6
 beq Melee
 iny
 cmp #$16
 beq Melee
 iny
 cmp #$1a
 beq Melee
 rts
Wave:
 lda DpShotY
 sta DpAttackY
 lda DpShotX
 sta DpAttackX
 lda #$80
 sta DpAttackKind
 rts
Melee:
 tya
 asl
 tay
 lda PointOffsets,y
 sta R0
 lda DpHorizontal
 bmi Left
 lda DpX
 clc
 adc R0
 bcs Done
Point:sta DpAttackX
 lda PointOffsets+1,y
 clc
 adc DpY
 sta DpAttackY
Done:rts
Left:
 lda DpX
 sec
 sbc R0
 bcs Point
 rts
PointOffsets:.byte $18,$18,$14,0,$1c,0,4,$14
.endproc
.proc DpSourceTestPoint
 ; Cclear=accepted, Cset=miss, exactly as0:FC22. Source subtraction/EOR
 ; intentionally has no ADC1 on a negative difference; preserve asymmetry.
 lda DpAttackX
 cmp #$ff
 beq Miss
 sec
 sbc DpTargetX,x
 bcs XPositive
 eor #$ff
XPositive:cmp #8
 bcs Miss
 lda DpAttackY
 sec
 sbc DpTargetY,x
 bcs YPositive
 eor #$ff
YPositive:cmp #12
 bcs Miss
 lda DpAttackKind
 bpl Hit
 lda #0
 sta DpShotState              ; real original first-contact projectile removal.
Hit:clc
 rts
Miss:sec
 rts
.endproc
.proc DpTryContact
 lda SelectedCharacter
 cmp #CHARACTER_DRAGON_POWER
 bne Miss
 cpx #6
 bcs Miss
 jmp DpSourceTestPoint
Miss:sec
 rts
.endproc
.export DpBuildAttackPoint,DpSourceBuildPoint,DpSourceTestPoint,DpTryContact,DpTargetX,DpTargetY
.popseg
