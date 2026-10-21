; UNAPPLIED source revision. Pinned2.02 Samus frames31/32 have nominal
; top16.5/height15.5, foot32. Existing body14/terrain5 project top17.
; Optional resident segments occupy only old DMC alignment/vector gaps.
.pushseg
.segment "SAMUS_CROUCH_BODY"

.proc SamusCrouchBodyTail
  ; Entry replaces ORA SmCrouch: Y15, A=Player_State. No stack use.
  ; Loads/branches preserve C/V, matching the old selector ABI.
  lda SmCrouch
  beq Reload
  lda GuestHurtTicks
  bne Reload
  lda SmBall
  bne Reload
  lda Player_State
  bne Reload
  ldy #13                      ; Original following INY selects existing14.
Reload:
  lda Player_State
  ora SmCrouch
  jmp MegaManCollisionBox::Samus+7
.endproc

.proc SamusCrouchTerrainTail
  ; Native PlayerBGCollision makes grounded Player_State=2 dry /1 water
  ; before probes; feet restore0. SmCrouch's movement lifecycle is authoritative.
  lda SmCrouch
  beq Reload
  lda GuestHurtTicks
  bne Reload
  lda SmBall
  bne Reload
  ldy #4                       ; Original following INY selects existing5.
Reload:
  lda Player_State
  ora SmCrouch
  jmp MegaManCollisionAdder::Samus+7
.endproc

.segment "SAMUS_CROUCH_WATER"
.proc SamusCrouchWaterTail
  ; The original water Samus branch is also used by expanded characters.
  ; A separate character gate prevents stale Samus flags changing them.
  lda SmCrouch
  beq NoCrouch
  lda SelectedCharacter
  eor #CHARACTER_SAMUS
  bne Air
  lda Player_State
  bne Air
  lda GuestHurtTicks
  bne Air
  lda #15
  ldy #$80
  jmp CrossoverWaterCheck::Boundary
NoCrouch:
  jmp CrossoverWaterCheck::Samus+14
Air:
  jmp CrossoverWaterCheck::Air25
.endproc
.popseg
