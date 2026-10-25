; Physical block-reward selection/delivery; no ownership change while spawning.
.pushseg
.segment "Z2_LOGIC"
.proc Z2RewardOwned
 tax
 lda RewardKind,x
 cmp #1
 bne Tech
 lda Z2LearnedSpells
 and RewardFlags,x
 rts
Tech:lda Z2Tech
 and RewardFlags,x
 rts
.endproc
.proc Z2ChooseReward
 lda #0
 sta R4
Loop:
 lda R4
 jsr Z2RewardOwned
 bne Next
 lda R4
 clc
 adc #$c0
 sta R5
 ldy #5
Pending:
 lda Enemy_Flag,y
 beq PendingNext
 lda Enemy_ID,y
 cmp #PowerUpObject
 bne PendingNext
 lda InvPickupOwner,y
 cmp #CHARACTER_LINK
 bne PendingNext
 lda InvPickup,y
 cmp R5
 beq Next
PendingNext:dey
 bpl Pending
 lda R5
 rts
Next:inc R4
 lda R4
 cmp #11
 bcc Loop
 lda Z2Containers
 and #7
 sta R4
 lda Z2Containers
 lsr
 lsr
 lsr
 lsr
 and #7
 sta R5
 ldy #5
Containers:
 lda Enemy_Flag,y
 beq ContainerNext
 lda Enemy_ID,y
 cmp #PowerUpObject
 bne ContainerNext
 lda InvPickupOwner,y
 cmp #CHARACTER_LINK
 bne ContainerNext
 lda InvPickup,y
 cmp #$cb
 bne CheckMagic
 inc R4
CheckMagic:cmp #$cc
 bne ContainerNext
 inc R5
ContainerNext:dey
 bpl Containers
 lda R4
 cmp #7
 bcc HpRoom
 lda R5
 cmp #7
 bcc Mp
 lda #$cd
 rts
HpRoom:cmp R5
 beq Hp
 bcc Hp
Mp:lda #$cc
 rts
Hp:lda #$cb
 rts
.endproc
.proc Z2PreparePickupGate
 stx InvObject
 jsr Z2IsActive
 bcs Native
 farcall DwPreparePickup,jmp
Native:
 ldx InvObject
 lda #0
 sta InvRisePhase,x
 sta InvPickupSaveLo,x
 lda #$fc
 sta InvPickup,x
 lda #CHARACTER_LINK
 sta InvPickupOwner,x
 lda PowerUpType,x
 cmp #2
 bcs Done
 cmp #0
 bne :+
 inc InvPickupSaveLo,x ; retain mushroom health benefit independently of art.
:
 jsr Z2ChooseReward
 ldx InvObject
 sta InvPickup,x
 lda #1
 sta PowerUpType,x ; stationary private native actor and48-frame visible rise.
Done:ldx InvObject
 rts
.endproc
.proc Z2CollectPickupGate
 stx InvObject
 jsr Z2IsActive
 bcs Native
 farcall DwCollectPickup,jmp
Native:
 ldx InvObject
 lda InvPickupOwner,x
 cmp #CHARACTER_LINK
 bne Unhandled
 lda InvPickup,x
 cmp #$c0
 bcc Unhandled
 cmp #$ce
 bcs Unhandled
 pha
 lda InvPickupSaveLo,x
 beq NoHeal
 jsr Z2MushroomHeal
NoHeal:pla
 sec
 sbc #$c0
 jsr Z2CollectReward
 lda #1
 sta PlayerStatus ; scene powerup tier only; HP remains the actual damage state.
 sta Z2UiDirty
 lda #60
 sta Z2SfxTimer
 ldx InvObject
 sec
 rts
Unhandled:ldx InvObject
 clc
 rts
.endproc
.proc Z2MushroomHeal
 lda Z2HpPending
 clc
 adc #48
 bcc :+
 lda #255
:sta Z2HpPending
 rts
.endproc
; A=frozen rewardindex0..13. Invalid/duplicate unique rewards never grantmore.
.proc Z2CollectReward
 cmp #14
 jcs No
 cmp #11
 bcs Container
 sta R4
 jsr Z2RewardOwned
 jne No
 ldx R4
 lda RewardKind,x
 cmp #1
 bne Tech
 lda Z2LearnedSpells
 ora RewardFlags,x
 sta Z2LearnedSpells
 lda Z2Selection
 and #8
 ora RewardSpellIndex,x
 sta Z2Selection
 jmp Yes
Tech:
 lda Z2Tech
 ora RewardFlags,x
 sta Z2Tech
 jmp Yes
Container:
 cmp #13
 beq Restore
 cmp #12
 beq Magic
 lda Z2Containers
 and #7
 cmp #7
 bcs No
 inc Z2Containers
 lda #240 ; original HeartContainer queues F0 recoveryticks.
 sta Z2HpPending
 jmp Yes
Magic:
 lda Z2Containers
 and #$70
 cmp #$70
 bcs No
 lda Z2Containers
 clc
 adc #16
 sta Z2Containers
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
 sta Z2MpPending
 jmp Yes
Restore:
 jsr Z2MushroomHeal
 lda #$90
 jsr Z2JarPickup
Yes:lda #1
 sta Z2UiDirty
 sec
 rts
No:clc
 rts
.endproc
.include "zelda2_reward_tables.inc"
.popseg
