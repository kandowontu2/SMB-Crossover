; Exact ID21 exclusive state. Root-owned allocation, 2026-10-28.
.ifndef CHARACTER_RIVER_CITY
CHARACTER_RIVER_CITY=21
.endif
RC_FIRST_CHR=716
RcVariant=$5fed                 ; menu-only:0 Alex,1 Ryan
RcHealth=$5fa0                  ; two independent 0..64 stamina values
RcTier=$5fa2                    ; two explicit crossover book/food tiers,0..2
RcMarker=$5fa4
RcLife=$5fa5
RcArea=$5fa6
RcWorld=$5fa7
RcSavedVariant=$5fa8
RcPrevious=$5c00
RcFresh=$5c01
RcHeld=$5c02
RcClock=$5c03
RcAttack=$5c04                 ; remaining native-style animation ticks
RcAttackKind=$5c05             ;1 punch,2 kick,3 flying kick,4 throw
RcAttackHits=$5c06
RcAttackFace=$5c07
RcRun=$5c08
RcTapDir=$5c09
RcTapWindow=$5c0a
RcHurt=$5c0b
RcHurtMove=$5c0c
RcWalk=$5c0d
RcPose=$5c0e
RcPalette=$5c0f
RcHudDirty=$5c10
RcCarrySlot=$5c11              ; FF means none; never an arbitrary actor state
RcCarryType=$5c12
RcThrowSlot=$5c13
RcThrowAge=$5c14
RcLastVx=$5c15
RcOldX=$5c16
RcSlot=$5c17
RcTemp=$5c18
RcTemp2=$5c19
RcRectX=$5c1a
RcRectPage=$5c1b
RcRectY=$5c1c
RcRectW=$5c1d
RcRectH=$5c1e
RcDamage=$5c1f
RcEnemyHP=$5c20                ;6 typed SMB adaptation records
RcEnemyType=$5c26
RcEnemyStun=$5c2c              ;6 private stun timers; NEVER Enemy_State enums
RcEnemyStamp=$5c32             ;native flag identity when typed ownership starts
RcEnemyX=$5c38                 ;last observed page/X protects actor-slot reuse
RcEnemyPage=$5c3e
RcInputStamp=$5c44
RcPaletteValue=$5c45
RcSavedObject=$5c46
RcHudValue=$5c47
RcGrabAge=$5c48
RcActionAge=$5c49
RcCarryVX=$5c4a
RcCarryVY=$5c4b
.export RcVariant,RcHealth,RcTier,RcMarker,RcLife,RcArea,RcWorld
.export RcPrevious,RcFresh,RcAttack,RcAttackKind,RcAttackHits,RcRun,RcHurt
.export RcCarrySlot,RcThrowSlot,RcEnemyHP,RcEnemyType,RcEnemyStun,RcPose
