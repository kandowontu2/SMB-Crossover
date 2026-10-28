; Exclusive new character20. Addresses reserved by ROOT; no generic-ID arrays.
.ifndef __ICE_CLIMBERS_STATE_INC
__ICE_CLIMBERS_STATE_INC=1
.ifndef CHARACTER_ICE_CLIMBERS
CHARACTER_ICE_CLIMBERS=20
.endif
.ifndef IC_FIRST_CHR
IC_FIRST_CHR=712
.endif
.ifndef IcVariant
IcVariant=$5fec                 ; Select:0Popo /1Nana. Never reset on area entry.
.endif
IcReady=$5f80
IcLife=$5f81
IcArea=$5f82
IcWorld=$5f83
IcPower=$5f84                   ; Crossover0unprotected,1parka,2strong hammer.
IcPaletteAck=$5f85
IcPrevious=$5c00
IcFresh=$5c01
IcAttack=$5c02                  ; Original swing age1..19; hit exactly age9.
IcAttackHits=$5c03
IcRun=$5c04                     ; Original ground buildup0..24.
IcMoveDir=$5c05                 ;0none,1right,2left. Native air direction latch.
IcCoast=$5c06
IcHurt=$5c07
IcHurtMove=$5c08
IcClock=$5c09
IcPose=$5c0a
IcTemp=$5c0b
IcEnemy=$5c0c
IcLastVX=$5c0d
IcJumpAge=$5c0e
IcWasGround=$5c0f
IcJumpHits=$5c10
IcWeaponHits=$5c11
IcOldPower=$5c12
IcJumpActive=$5c13              ; Genuine A launch, distinguished from walking off.
.export IcVariant,IcPower,IcReady,IcAttack,IcHurt,IcPose,IcMoveDir,IcRun
.endif
