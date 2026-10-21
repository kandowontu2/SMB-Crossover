; Enemy.checkAttackProps: INVUL, existing-freeze removal, newFREEZE,
; then piercing/defaultproperties and damage. No new persistent state.
.pushseg
.segment "INVENTORY"
.proc SamusHardEnemyAdmission
  lda CrossoverBehaviorVersion
  jeq Allow
  lda MmEnemyHealthLo,x
  ora MmEnemyHealthHi,x
  bne Active
  lda #0
  sta RgShotHitsNow,x
Active:
  lda RgShotHitsNow,x
  beq FreezeOrder
  lda MmBulletType
  cmp #10
  beq Bomb
  jsr SamusShotConfirmed       ; confirmedHit(false) follows rejected properties.
  ldy MmSlot
  lda #0
  sta MmBulletType,y
  sec
  rts
Bomb:
  lda HitBits,x
  ldy SmSlot
  ora SmBombHits,y
  sta SmBombHits,y
  sec
  rts
FreezeOrder:
  lda AvFrozen,x
  ora AvFrozenHi,x
  beq NewFreeze
  lda #0
  sta AvFrozen,x
  sta AvFrozenHi,x
  sta RgEnemyStun,x             ; Freeze.destroy removes its source STOP.
  sta LsrFrozenPose,x
  beq Allow
NewFreeze:
  lda MmBulletType
  cmp #73                      ; ActualIce46 +27.
  bne Allow
  lda Enemy_ID,x
  cmp #Podoboo                 ; Hostileprojectile, not a sourceEnemy receipt.
  beq Allow
  cmp #Lakitu                  ; SourceFREEZE_PAS10 resists Ice strength0.
  beq Allow
  cmp #Bowser
  beq Allow
  cmp #$15
  bcc Freeze
  cmp #BulletBill_CannonVar
  bne Allow
Freeze:
  lda #104                     ;6000ms at60completedupdates/s =360.
  sta AvFrozen,x
  lda #1
  sta AvFrozenHi,x
  lda #255                     ; Hold the source6000ms STOP with AvFrozen's16-bit owner.
  ldy #1
  farcall LsrEffectsApplyStop   ; Capture current animation and per-object timers.
  lda #1
  sta SmFreezeRenderState
  jsr SamusShotConfirmed
  phy                          ; common.inc TYA/PHA clobbers A.
  lda #0                       ; Freeze's STOP removes preexisting FLASH.
  sta MmEnemyFlash,x
  ldy MmSlot
  sta MmBulletType,y            ; confirmedHit(false) still enters nativeEnd.
  ply
  lda #0                       ; Restore admission A/N/Z after PLY's PLA/TAY.
  sec                          ; Skip health/damage/defaultproperties thishit.
  rts
Allow:
  lda #0                       ; Literalold non-INVUL Allow A/N/Z/C result.
  clc
  rts
HitBits: .byte 1,2,4,8,16,32
.endproc
.segment "SPECIAL_EXTRA"
.proc SamusHardPropertyType
  lda MmBulletType
  cmp #7
  bcc No
  cmp #11
  bcc Yes
  cmp #68
  beq Yes
  cmp #73
  beq Yes
No:
  clc
  rts
Yes:
  sec
  rts
.endproc
.popseg

.pushseg
.segment "INVENTORY"
; Called only after this Hard Samus contact's properties/piercing decision.
; X=enemy slot; preserve Y. Bomb/Screw are not SamusShot and retain their owners.
.proc SamusShotConfirmed
  phy
  lda MmBulletType
  cmp #73
  beq Ice
  cmp #7
  bcc Done
  cmp #10
  bcs Done
  ldy SmSlot
  lda #0
  sta SmShotType,y
  sta SmShotImpact,y
  jmp ArmorCue
Ice:
  ldy AvSlot
  lda #0
  sta RgShotType,y
  sta RgShotImpact,y
ArmorCue:
  lda Enemy_ID,x
  cmp #BuzzyBeetle
  beq Proof
  cmp #BulletBill_FrenzyVar
  beq Proof
  cmp #BulletBill_CannonVar
  bne Done
Proof:
  lda SmSfx
  ora #32                      ; Dedicated BulletProof; world Bump is separately mixed.
  sta SmSfx
Done:
  ply
  rts
.endproc
.segment "GUEST"
.proc SamusShotEnemyConsume
  php                          ; Preserve original Consume CMP10's live C/V/D/I.
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  bne Native
  lda CrossoverBehaviorVersion
  beq Native
  lda MmBulletType,x
  cmp #73
  beq Confirm
  cmp #7
  bcc Native
  cmp #10
  bcs Native
Confirm:
  phx
  ldx MmEnemySlot
  farcall SamusShotConfirmed
  plx
Native:
  plp
  jmp MegaManWeapons::Kill
.endproc
.segment "SPECIAL_ROSTER"
.proc SamusFrozenStopAdvance
  lda AvFrozen,x
  ora AvFrozenHi,x
  bne Hold
  dec RgEnemyStun,x
  rts
Hold:
  lda #1                       ; Internal caller consumes only Z; active STOP stays nonzero.
  rts
.endproc
.segment "SPECIAL_EXTRA"
.proc SamusFrozenDecrement
  dec AvFrozen,x
  lda AvFrozen,x
  ora AvFrozenHi,x
  bne Done
  lda #0
  sta RgEnemyStun,x
  sta LsrFrozenPose,x
Done:
  rts
.endproc
.popseg
