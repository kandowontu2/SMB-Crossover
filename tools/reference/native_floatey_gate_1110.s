.setcpu "6502"

ObjectOffset = $000d
FloateyNum_Control = $010d
SafecallA = $016a
EnemiesAndLoopsCore = $a260
FloateyNumbersActive = $8969
GuestPostEnemyCollision = $a1f5
RelativePlayerPosition = $8a8c
SharedAddToScorePacket = $8998
ResumeGameCore = $83df
ResumeFlagpole = $86b8

.segment "ACTOR_LOOP"
  ldx #0
@slot:
  stx ObjectOffset
  jsr EnemiesAndLoopsCore
  ; The actor may award a new popup during its own update.
  lda FloateyNum_Control,x
  beq @advance
  jsr FloateyNumbersActive
@advance:
  inx
  cpx #6
  bne @slot
  jmp AfterActorLoop
  .byte $ea

.segment "FLAGPOLE_PACKET"
  ; The existing score packet ends in a tail jump into FarCallCommon.
  ; This supplies the same single stack return as the original inline call.
  jsr SharedAddToScorePacket
  jmp ResumeFlagpole
AfterActorLoop:
  jsr GuestPostEnemyCollision
  jsr RelativePlayerPosition
  sta SafecallA
  jmp ResumeGameCore
