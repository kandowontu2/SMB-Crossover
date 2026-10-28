; Authentic USA Dragon Power source projection. Raw24 exclusively owns this.
.ifndef __DRAGON_POWER_STATE_INC
__DRAGON_POWER_STATE_INC=1
CHARACTER_DRAGON_POWER=24
.ifndef DP_FIRST_CHR
DP_FIRST_CHR=788
.endif
DpHP=$5fd0
DpPole=$5fd1
DpWaves=$5fd2
DpFlags=$5fd3
DpReady=$5fd4
DpLife=$5fd5
DpArea=$5fd6
DpWorld=$5fd7
DpPower=$5fd8
DpPrevious=$5fd9
DpPaletteAck=$5fda
DpHunger=$5fdb
DpAction=$5c00
DpProtection=$5c02
DpPose=$5c03
DpAttribute=$5c04
DpActionFlags=$5c05
DpTimer=$5c06
DpVertical=$5c07
DpHorizontal=$5c08
DpSeconds=$5c09
DpSpecial=$5c0a
DpJumping=$5c0b
DpGroundY=$5c0c
DpShotState=$5c0d
DpShotY=$5c0f
DpShotYPage=$5c10
DpShotX=$5c11
DpShotXPage=$5c12
DpClock=$5c13
DpSecondPhase=$5c14
DpHeld=$5c15
DpFresh=$5c16
DpSourcePrevious=$5c17
DpX=$5c18
DpY=$5c19
DpExit=$5c1a
DpSpawnSide=$5c1b
DpSpawnFlag=$5c1c
DpKickAge=$5c1d
DpOldX=$5c1e
DpOldY=$5c1f
DpShotCamera=$5c20               ;16bit world camera at genuine source allocation.
DpTileIndex=$5c22
DpTileResult=$5c23
DpProbeY=$5c24
DpProbeX=$5c25
DpProbePage=$5c26
DpSavedR0=$5c27
DpSavedR1=$5c28
DpMath=$5c30                    ; original02..0F ->5C32..3F;00/01 borrowR0/R1.
DpContacts=$5c40                ; source0400..040C including2 block effect records.
DpPlatform=$5c4d                ; source0446..044A,5bytes.
DpCueCount=$5c52
DpCues=$5c53                    ;4 committed requests per logical tick; overflowflag.
DpCueOverflow=$5c57
DpDeltaX=$5c58
DpDeltaY=$5c59
DpAttackX=$5c5a
DpAttackY=$5c5b
DpAttackKind=$5c5c
DpAttackEpoch=$5c5d
DpHitMask=$5c5e
DpHitType=$5c60                 ;6 actual host enemy lifetime/type receipts.
DpRenderIndex=$5c66
DpRenderFace=$5c67
DpBorrow=$5c68                  ; request14..16 math,+6 hungerperiod,+7 sceneD7.
DpRenderBuffer=$5c70            ;small transient wrapper scratch only, notfullsprite.
.export DpHP,DpPole,DpWaves,DpReady,DpPower,DpAction,DpPose,DpHorizontal,DpVertical
.export DpX,DpY,DpHeld,DpFresh,DpShotState,DpShotX,DpShotY,DpShotCamera
.export DpCueCount,DpCues,DpCueOverflow,DpContacts,DpPlatform,DpDeltaX,DpDeltaY
.export DpAttackX,DpAttackY,DpAttackKind,DpAttackEpoch,DpHitMask,DpHitType
.endif
