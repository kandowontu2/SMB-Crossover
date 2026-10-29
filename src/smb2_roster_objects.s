.include "smb2_roster_objects_native.inc"
.pushseg
.segment "PARODIUS_BELLS"
.export S2ActorEpochChanged,S2TryLiftEnemy,S2EnemyControl,S2ObjectHit,S2StandOnActor
.proc S2CarrySelect
 php
 pha
 sty R2
 ldy S2NativeCharacter
 lda Offsets,y
 clc
 adc R2
 tay
 pla
 plp
 rts
Offsets:.byte 0,29,58,87
.endproc
.proc S2CarryAddLo
 jsr S2CarrySelect
 adc S2CarryOffsets,y
 php
 ldy R2
 plp
 rts
.endproc
.proc S2CarryAddHi
 jsr S2CarrySelect
 adc S2CarryOffsets+14,y
 php
 ldy R2
 plp
 rts
.endproc
.proc S2FreeObject
 ldx #0
Loop:lda S2ObjectState,x
 beq Found
 inx
 cpx #3
 bcc Loop
 clc
 rts
Found:sec
 rts
.endproc
.proc S2BeginLift
 ; X=successfully allocated private record. Caller supplies real type/owner.
 stx S2HeldIndex
 lda #1
 sta S2ObjectState,x
 sta S2Holding
 lda #0
 sta S2ObjectProjectile,x
 sta S2VX+1,x
 sta S2VY+1,x
 sta S2XF+1,x
 sta S2YF+1,x
 sta S2AX+1,x
 sta S2AY+1,x
 lda #7
 sta S2ObjectLift,x
 lda #2
 sta S2State
 lda #6
 sta S2Timer
 lda #8
 sta S2Animation
 rts
.endproc
.proc S2LimitThrowPool
 lda S2Holding
 beq Done
 ldx #2
 ldy #0
Loop:lda S2ObjectProjectile,x
 beq Next
 iny
Next:dex
 bpl Loop
 cpy #2
 bcc Done
 lda S2Fresh
 and #$bf
 sta S2Fresh                 ; preserve held record/reserve on full refusal.
Done:rts
.endproc
.proc S2ObjectsTick
 ldx #0
Loop:stx S2Source12
 lda S2ObjectState,x
 beq Next
 jsr S2AdvanceProjectileAge
 lda S2ObjectLift,x
 beq Physics
 jsr S2O960F                 ; complete original carried position, source fractions.
 jmp Next
Physics:jsr S2O9E50
 jsr S2O9E4B
 lda S2VY+1,x
 bmi Accelerate
 cmp #$3e
 bcs Cull
Accelerate:inc S2VY+1,x
 inc S2VY+1,x
Cull:
 ; Authored host-world ownership boundary: below the screen is gone. No
 ; active visible projectile time limit, bounce or velocity substitution.
 lda S2YPage+1,x
 bmi Next
 beq Next
 jsr S2ClearObject
Next:ldx S2Source12
 inx
 cpx #3
 bcc Loop
 rts
.endproc
.proc S2AdvanceProjectileAge
 ; Exact alive-object prefix: a throw ages1..32, then saturates. Zero stays
 ; zero. This is grace/ownership state, never a projectile lifetime cutoff.
 ldy S2ObjectProjectile,x
 dey
 cpy #$1f
 bcs Done
 inc S2ObjectProjectile,x
Done:rts
.endproc
.proc S2ClearObject
 lda S2Holding
 beq Clear
 cpx S2HeldIndex
 bne Clear
 lda #0
 sta S2Holding
 sta S2State
Clear:lda #0
 sta S2ObjectState,x
 sta S2ObjectProjectile,x
 sta S2ObjectLift,x
 lda #$ff
 sta S2ObjectHost0,x
 rts
.endproc
.proc S2DropHeld
 ; Native death releases the held actor; other throws keep their state.
 lda S2Holding
 beq Done
 ldx S2HeldIndex
 lda #0
 sta S2Holding
 sta S2ObjectLift,x
 sta S2VX+1,x
 sta S2VY+1,x
Done:
 rts
.endproc
.proc S2ActorEpochChanged
 ; ROOT calls at the ACTUAL spawn/erase/reset authority before slot reuse.
 ; X=real SMB enemy slot0..5. It never infers an epoch from a live flag.
 txa
 pha
 lda SelectedCharacter
 cmp #CHARACTER_SMB2_ROSTER
 bne Done
 cpx #6
 bcs Done
 txa
 ldx #2
Loop:cmp S2ObjectHost0,x
 bne Next
 pha
 jsr S2ClearObject
 pla
Next:dex
 bpl Loop
Done:pla
 tax
 rts
.endproc
.proc S2TryLiftEnemy
 ; Genuine Hard standing-on-actor callback: X=contact owner. Root must
 ; only call for actual top contact; no arbitrary-distance enemy grant.
 txa
 pha
 lda SelectedCharacter
 cmp #CHARACTER_SMB2_ROSTER
 bne No
 cpx #6
 bcs No
 lda CrossoverBehaviorVersion
 beq No
 lda S2State
 ora S2Holding
 ora S2Duck
 bne No
 lda S2Fresh
 and #$40
 beq No
 lda Enemy_Flag,x
 beq No
 bmi No
 lda Enemy_State,x
 bne No
 lda Enemy_ID,x
 cmp #6
 beq Valid
 cmp #2
 bcs No
Valid:jsr S2FreeObject
 bcc No
 pla
 sta S2ObjectHost0,x
 lda #1                       ; source ShyguyRed carry/throw class; SMB art stays.
 sta S2ObjectType,x
 lda #0                       ; native basic walking-enemy carry classification.
 sta S2ObjectHitbox,x
 jsr S2BeginLift
 txa
 tay                          ; Y=private record, X=original actor owner.
 lda S2ObjectHost0,x
 tax
 sec
 rts
No:pla
 tax
 clc
 rts
.endproc
.proc S2StandOnActor
 ; Root calls ONLY after genuine Hard top-contact resolution has corrected
 ; host XY using S2CollisionBounds. This does not manufacture an overlap.
 ; Exact eligible walking Goomba/Koopa retains native enemy art and AI.
 lda SelectedCharacter
 cmp #CHARACTER_SMB2_ROSTER
 bne No
 lda CrossoverBehaviorVersion
 beq No
 cpx #6
 bcs No
 lda Enemy_Flag,x
 beq No
 bmi No
 lda Enemy_State,x
 bne No
 lda Enemy_ID,x
 cmp #6
 beq Valid
 cmp #2
 bcs No
Valid:
 txa
 pha
 jsr S2ImportPosition
 lda #0
 sta S2Air
 sta S2VY
 sta S2YF
 sta S2AY
 sta Player_State
 pla
 tax
 jsr S2TryLiftEnemy            ; source freshB + no held item/no duck.
 sec                          ; actual top contact handled even without lift.
 rts
No:clc
 rts
.endproc
.proc S2EnemyControl
 ; X=actual enemy slot; C1 means caller must use private geometry/skip
 ; native actor AI. Host render still uses original SMB enemy art/attributes.
 lda SelectedCharacter
 cmp #CHARACTER_SMB2_ROSTER
 bne No
 cpx #6
 bcs No
 txa
 ldy #2
Loop:cmp S2ObjectHost0,y
 bne Next
 pha
 lda S2ObjectState,y
 beq Empty
 lda S2X+1,y
 sta Enemy_X_Position,x
 lda S2Page+1,y
 sta Enemy_PageLoc,x
 lda S2Y+1,y
 sta Enemy_Y_Position,x
 lda S2YPage+1,y
 clc
 adc #1
 sta Enemy_Y_HighPos,x
 pla
 sec
 rts
Empty:pla
Next:dey
 bpl Loop
No:clc
 rts
.endproc
.proc S2ObjectHit
 ; X=private projectile whose REAL host collision was accepted. C1 authorizes
 ; root's native enemy-damage/score consumer; this leaf never writes an outcome.
 lda SelectedCharacter
 cmp #CHARACTER_SMB2_ROSTER
 bne No
 cpx #3
 bcs No
 lda S2ObjectState,x
 beq No
 lda S2ObjectProjectile,x
 beq No
 lda S2ObjectHost0,x
 pha
 jsr S2ClearObject
 pla                          ; actual owner or FF vegetable to root consumer.
 sec
 rts
No:clc
 rts
.endproc
.popseg
