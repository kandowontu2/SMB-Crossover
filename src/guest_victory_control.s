; Rare castle WATCH controller. Ordinary gameplay has no new instructions.
.pushseg
.segment "PLAYER"
.proc GuestVictoryControl
  lda SelectedCharacter
  beq Native
  cmp #CHARACTER_LUIGI
  beq Native
  farcall GuestVictoryGuestControl, jmp
Native:
  jmp PlayerCtrlRoutine
.endproc

.segment "RYU_COLD"
.proc GuestVictoryGuestControl
  ; PlayerVictoryWalk supplies only zero or Right. Preserve its saved latch,
  ; parse it explicitly, and reuse the entire original post-movement suffix.
  ; Source WATCH keeps the EasyLink global clock and clip live.
  lda SelectedCharacter
  eor #CHARACTER_LINK
  ora CrossoverBehaviorVersion
  bne ClockReady
  farcall EasyLinkFrameCycle
ClockReady:
  jsr FinishAnimation
  lda SavedJoypadBits
  and #3
  sta Left_Right_Buttons
  lda #0
  sta A_B_Buttons
  sta Up_Down_Buttons
  farcall CrossoverVanillaMovement
  ; Complete the original full BG/collision suffix before current-state
  ; animation. Foreign/Hard returnedA/NZ andC/V remain exact: EOR/ORA do
  ; not changeC/V, and FarCallCommon already returnsNZ derived fromA.
  farcall GuestVictoryAfterMovement
  pha
  lda SelectedCharacter
  eor #CHARACTER_LINK
  ora CrossoverBehaviorVersion
  bne ReturnControl
  pla
  farcall EasyLinkAnimate, jmp
ReturnControl:
  pla
  rts

FinishAnimation:
  ; WATCH continues these existing finite lifetimes; it cannot start attacks.
  lda RgCooldown
  beq :+
    dec RgCooldown
  :
  lda RgShootPose
  beq :+
    dec RgShootPose
  :
  lda SmShootPose
  beq :+
    dec SmShootPose
  :
  lda RgAttack
  beq Done
  dec RgAttack
  inc RgAttackAge
  lda SelectedCharacter
  cmp #CHARACTER_SIMON
  bne Link
  lda RgAttackKind
  beq Done
  lda RgAttackAge
  cmp #14
  bne Done
  ; Both source versions spawn a pending throw at throwEnd in WATCH.
  farcall AvSimonRelease
  rts
Link:
  cmp #CHARACTER_LINK
  bne Done
  lda RgAttackKind
  bne Done
  lda RgAttackAge
  cmp #9
  bne Done
  farcall RemainingPower
  cmp #2
  bne Done
  ; Complete an already-started beam event; no melee/enemy collision pass.
  farcall RosterWeapons::SpawnBeam
Done:
  rts
.endproc
.popseg
