; Character.as defaults canStomp=false; only MarioBase enables it. Guest
; body attacks are resolved separately from the native shell/kick rules.
.pushseg
.segment "FIXED"
.proc GuestBodyContactBridge
.if ::ENABLE_MMC5_EXPANDED
  farcall LmBodyGate

.else
  farcall GuestBodyContact

.endif
  rts
  .include "terrain_catchup.s" ; Reuse the unreachable16-byte resident tail.
.endproc

.if ::ENABLE_MMC5_EXPANDED
.proc GuestInjuryStatus
  farcall RlInjuryStatusDispatch,jmp
  .res 1,$ea
  .assert *-GuestInjuryStatus=19,error,"fixed original span"
.endproc
.else
.proc GuestInjuryStatus
  ; Bill.takeDamage calls die() in every power form. Mushrooms upgrade his
  ; weapon and never grant an additional contact hit. Lance shares this rule.
  ldx PlayerStatus
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bne Done
  lda CrossoverBehaviorVersion
  beq Done                    ;Easy Bill retains the original powered extra hit.
  ldx #0
Done:
  txa
  rts
.endproc
.endif

.segment "OBJECT"
.proc GuestPostEnemyCollision
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne Other
.if ::ENABLE_MMC5_EXPANDED
  farcall Z2DeferredThrustGate
.else
  farcall LinkDeferredThrust
.endif
  jmp Effects
Other:
  cmp #CHARACTER_SAMUS
  beq Effects
Legacy:
  cmp #CHARACTER_SIMON
  beq Effects
  cmp #CHARACTER_RYU
  bne Done
Effects:
  jsr RyuPlatformPostBridge     ; retains the exact old effect gate result.
  beq Done
  farcall LsrEffectsAfterEnemies
Done:
  jmp GetPlayerOffscreenBits
.endproc

.segment "SAMUS"
.proc GuestBodyFrame
  ; Guest body collision runs every physics update. Native MarioBase keeps
  ; the engine's alternating-frame path and never uses these dictionaries.
  lda GuestBodyNow
  sta GuestBodyPrev
  lda #0
  sta GuestBodyNow
  rts
.endproc

.proc GuestBodyContact
  phx
  phy
  lda ObjectOffset
  pha
  jsr GuestSourceStompPolicy
  lda SelectedCharacter
  jeq NativeBody
  cmp #CHARACTER_LUIGI
  jeq NativeBody
  lda #1
  sta GuestBodyNoStomp
  lda SelectedCharacter
  cmp #CHARACTER_SCROOGE
  bne NotScrooge
.if ::ENABLE_MMC5_EXPANDED
  farcall DwScroogeContact
.else
  farcall ScroogePogoContact
.endif
  jcs Protected
  jmp Ordinary
NotScrooge:
  cmp #CHARACTER_LINK
  bne OtherGuest
.if ::ENABLE_MMC5_EXPANDED
  farcall Z2BodyContactGate
.else
  farcall LinkBodyContact
.endif
  jcs Protected
  jmp Ordinary
OtherGuest:
  ; Native enemy-object slots also carry hostile projectiles. A body-safe
  ; attack cannot protect against LavaFireBall, BowserFireBall or FireBar.
  lda Enemy_ID,x
  cmp #Podoboo
  jeq Ordinary
  cmp #$15
  bcc EnemyBody
  cmp #BulletBill_CannonVar
  beq EnemyBody
  cmp #Bowser
  jne Ordinary
EnemyBody:
  ; Bowser's rear is a second native object for the same source enemy.
  lda Enemy_Flag,x
  bpl Canonical
  and #$7f
  cmp #6
  jcs Ordinary
  tax
  lda Enemy_ID,x
  cmp #Bowser
  jne Ordinary
  lda Enemy_Flag,x
  jeq Ordinary
  jmi Ordinary
Canonical:
  lda Enemy_State,x
  and #$20
  jne Ordinary
  lda Enemy_ID,x
  cmp #Goomba
  bne SelectAttack
  lda Enemy_State,x
  cmp #2
  jcs Ordinary
SelectAttack:
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  beq MegaKick
  cmp #CHARACTER_BASS
  beq MegaKick
  cmp #CHARACTER_SAMUS
  beq Screw
  cmp #CHARACTER_RYU
  jne Ordinary
  lda AvSlash
  jeq Ordinary
  jsr NewContact
  jcs Protected
  lda #74                      ; Source Jump Slash:75, pierce0.
  jsr SpinDamage
  jmp Protected
Screw:
  lda Enemy_ID,x
  cmp #Bowser                  ; Samus.hitEnemy explicitly excludes Bowser.
  jeq Ordinary
  lda SmFlip
  jeq Ordinary
  lda Player_State
  jeq Ordinary
  phx
  lda #6
  farcall InventoryHas
  plx
  jcc Ordinary
  jsr NewContact
  jcs Protected
  lda #75                      ; Source Screw Attack: unbounded damage, pierce10.
  jsr SpinDamage
  jmp Protected
MegaKick:
  lda SsKick
  cmp #1                       ; A paid start remains valid after ammo reaches0.
  jne Ordinary
  lda MmSliding
  ora XgDash
  jeq Ordinary
  jsr NewContact
  jcs Protected
  farcall MegaKickBodyDamage
Protected:
  ; KoopaGreen.hitCharacter kicks independently of Character.hitEnemy.
  ; A surviving stationary shell still reaches native kicking, even after
  ; the character's protected attack. A defeated target cannot be kicked.
  lda Enemy_Flag,x
  beq KeepProtection
  lda Enemy_ID,x
  cmp #4
  bcs KeepProtection
  lda Enemy_State,x
  and #$a0
  bne KeepProtection
  lda Enemy_State,x
  and #7
  cmp #2
  bcs Ordinary
KeepProtection:
  pla
  sta ObjectOffset
  ply
  plx
  sec
  rts
NativeBody:
  lda #0
  sta GuestBodyNoStomp
Ordinary:
  pla
  sta ObjectOffset
  ply
  plx
  clc
  rts

NewContact:
  ; Always keep an ongoing contact in the current dictionary, even when
  ; last update's dictionary already excludes a repeat damaging hit.
  lda Bits,x
  and GuestBodyNow
  bne Seen
  lda Bits,x
  ora GuestBodyNow
  sta GuestBodyNow
  lda Bits,x
  and GuestBodyPrev
  bne Seen
  clc
  rts
Seen:
  sec
  rts
Bits: .byte 1,2,4,8,16,32

SpinDamage:
  ; Save the live primary projectile bridge; this body attack owns no slot.
  sta GuestBodyAttack
  phx
  phy
  lda MmEnemySlot
  pha
  lda MmSlot
  pha
  lda RgSlot
  pha
  stx MmEnemySlot
  stx ObjectOffset
  ldy #3
SaveTypes:
  lda MmBulletType,y
  pha
  dey
  bpl SaveTypes
  lda GuestBodyAttack
  sta MmBulletType
  cmp #74
  bne Damage
  lda Enemy_ID,x
  cmp #BuzzyBeetle
  beq Restore
  cmp #BulletBill_FrenzyVar
  beq Restore
  cmp #BulletBill_CannonVar
  beq Restore
Damage:
  lda #0
  sta MmSlot
  farcall MegaManWeapons::DamageEnemy
Restore:
  ldy #0
RestoreTypes:
  pla
  sta MmBulletType,y
  iny
  cpy #4
  bne RestoreTypes
  pla
  sta RgSlot
  pla
  sta MmSlot
  pla
  sta MmEnemySlot
  lda #0
  sta GuestBodyAttack
  ply
  plx
  rts
.endproc
.popseg
