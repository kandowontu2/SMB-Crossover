.setcpu "6502"

EnemyID = $17
EnemyState = $1f
PlatformCollisionFlag = $0566
HpActorOwner = $73ae
YMovingPlatform = $b642
LargePlatformBoundBox = $9f25
FarCallCommon = $015a
SavedA = $016a
TargetLo = $016c
TargetHi = $016d

.segment "MOTION"
.export NativePlatformMotion, DirectVertical
NativePlatformMotion:
  ; The only caller has A=0 from its TimerControl test.
  ldy EnemyID,x
  cpy #$25
  bne LegacyMotion
  ldy HpActorOwner,x
  bne LegacyMotion
  ldy PlatformCollisionFlag,x
  bpl LegacyMotion
DirectVertical:
  jmp YMovingPlatform
LegacyMotion:
  jmp MotionPacket
.assert *-NativePlatformMotion=22,error,"Preserve the platform motion footprint"

.segment "BOX"
.export NativePlatformBBoxGate, MotionPacket
NativePlatformBBoxGate:
  lda EnemyID,x
  cmp #$25
  beq Tagged
  cmp #$28
  bne NativeBox
Tagged:
  lda EnemyState,x
  and #$40
  beq NativeBox
  sta SavedA
  lda #$4b
  ldy #$b0
  bne Bank26
MotionPacket:
  sta SavedA
  lda #$40
  ldy #$ae
Bank26:
  sta TargetLo
  sty TargetHi
  lda #$9a
  jmp FarCallCommon
NativeBox:
  jmp LargePlatformBoundBox
.assert *-NativePlatformBBoxGate<=47,error,"Preserve the original DrawSmallPlatform tail"
.res 47-(*-NativePlatformBBoxGate),$ea
