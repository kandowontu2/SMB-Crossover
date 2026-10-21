; Link/Simon/Ryu DEFAULT_PROPS, pinned Crossover2.02.
; Timing is counted in completed60Hz enemy-loop updates, independently of NMI.
; Source citations, palette quantization and isolated fixture scope:
; docs/reference/lsr-enemy-effects-202.md.
.pushseg
.segment "OBJECT"

; The zero case is a strict no-op for both effect passes. Include stale pose
; receipts too: an absent/defeated actor must still reach ordinary cleanup.
; A/Z only; no X/Y, scratch, timer, dictionary or mapper changes.
; SmFreezeVisible is a render-local counter: not read by the NMI packet leaf,
; and initialized before every render pass which publishes it. Foreground paths:
; ProcFireball_Bubble and GuestPostEnemyCollision/RyuPlatformPostBridge, before DrawAll. No ISR reaches it.
SmFreezeAnyX = SmFreezeVisible
.proc LsrEffectsAny
  stx SmFreezeAnyX
  lda #0
  ldx #5
Aggregate:
  ora RgEnemyStun,x
  ora MmEnemyFlash,x
  ora LsrFrozenPose,x
  dex
  bpl Aggregate
  ldx SmFreezeAnyX
  ora #0                       ; exact aggregate A/N/Z; C/V/D/I remain original.
  rts
.endproc
; ProcessCannons bypasses RunEnemyObjectsCore's freeze/TimerControl wrapper.
; Exact original A/P for all non-Hard-Samus-frozen cases. Only Z is consumed by
; the active freeze branch, and GetEnemyOffscreenBits immediately replaces A.
.proc SamusIceCannonTimer
  php
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  bne Native
  lda CrossoverBehaviorVersion
  beq Native
  lda AvFrozen,x
  ora AvFrozenHi,x
  beq Native
  plp
  lda #1
  rts
Native:
  plp
  lda TimerControl
  rts
.endproc

.segment "SPECIAL_ROSTER"

; X is the actual enemy slot. C=1 only for a live LSR STOP target.
; Bowser/Lakitu resist STOP strength0; piercing/damage/FLASH are independent.
.pushseg
.segment "SPECIAL_EXTRA"
.proc LsrEffectsStopped
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  bne Legacy
  lda Enemy_ID,x
  cmp #Bowser
  beq No
  cmp #Lakitu
  beq No
  bne Check
Legacy:
  cmp #CHARACTER_LINK
  beq Check
  cmp #CHARACTER_SIMON
  bne No
Check:
  lda RgEnemyStun,x
  beq No
  sec
  rts
No:
  clc
  rts
.endproc
.popseg

; Successful surviving damage, after the native/source pierce checks.
; Preserve X/Y; C=1 handles LSR, C=0 retains another character's old flash.
.pushseg
.segment "SPECIAL_EXTRA"
.proc LsrEffectsAcceptedHit
  phy
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  bne Modern
  lda CrossoverBehaviorVersion
  bne HardSamus
  lda MmBulletType
  cmp #7
  bcc Other
  cmp #11
  bcs Other
  jsr SamusLegacyEnemyStop
  jmp Handled
HardSamus:
  jsr SamusHardPropertyType
  bcs HardProperties
  jmp Other
  .res 7,$ea                    ; Preserve exactold15B typegate andlaterPCs.
HardProperties:
  jsr SamusHardEnemyEffects
  jmp Handled
Modern:
  cmp #CHARACTER_RYU
  beq Flash
  cmp #CHARACTER_LINK
  beq StopAndFlash
  cmp #CHARACTER_SIMON
  bne Other
  lda #24
  ldy #1
  farcall LsrEffectsApplyStop
  jmp Handled
StopAndFlash:
  lda #24
  ldy #1
  farcall LsrEffectsApplyStop
Flash:
  lda #24                       ; 400ms; phase1 applies immediately.
  sta MmEnemyFlash,x
Handled:
::LsrEffectsAcceptedHitFinish:
  ply
  sec
  rts
Other:
  ply
  clc
  rts
.endproc
.popseg

; LinkBoomerang owns pierce10, zero damage, STOP3000(stopAnim=false).
; It hits native armor5 (Buzzy/Bullet) but not hostile projectile objects.


; A=full duration, Y=stopAnim. Source replaces only a strictly shorter
; remaining Stop. Accepted STOP removes FLASH before later FLASH applies.
.proc LsrEffectsApplyStop
  pha
  lda Enemy_ID,x
  cmp #Bowser
  beq Resisted
  cmp #Lakitu
  beq Resisted
  pla
  cmp RgEnemyStun,x
  bcc Done
  beq Done
  sta RgEnemyStun,x
  lda #0
  sta MmEnemyFlash,x
  sta LsrFrozenPose,x
  tya
  beq SaveTimers
  lda EnemyMetasprite,x
  bne :+
    lda #$ff                    ; First render after spawning captures its pose.
  :
  sta LsrFrozenPose,x
SaveTimers:
  lda EnemyIntervalTimer,x
  sta LsrIntervalTimer,x
  cpx #5                        ; Native EnemyFrameTimer has only five slots.
  bcs Done
  lda EnemyFrameTimer,x
  sta LsrFrameTimer,x
Done:
::LsrEffectsApplyStopFinish:
  rts
Resisted:
  pla
  rts
.endproc

; Called once before any weapon/body hits. The native global timer pass has
; already run: restore the per-object timers which source STOP pauses.
.proc LsrEffectsBeforeEnemies
  phx
  phy
  lda TimerControl
  bne Done
  ldx #5
Loop:
  lda Enemy_Flag,x
  beq Clear
  lda Enemy_State,x
  and #$20
  bne Clear
  lda MmEnemyFlash,x
  beq :+
    dec MmEnemyFlash,x
  :
  lda RgEnemyStun,x
  beq Next
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  bne RestoreTimers
  lda CrossoverBehaviorVersion
  bne RestoreTimers
  lda Enemy_ID,x
  cmp #Bowser
  beq Next                       ; Old overrides resume ordinary timers.
  cmp #Lakitu
  beq Next
RestoreTimers:
  lda LsrIntervalTimer,x
  sta EnemyIntervalTimer,x
  cpx #5
  bcs Next
  lda LsrFrameTimer,x
  sta EnemyFrameTimer,x
  jmp Next
Clear:
  jsr LsrEffectsClear
Next:
  dex
  bpl Loop
Done:
::LsrEffectsBeforeEnemiesFinish:
  ply
  plx
  rts
.endproc

; After body contact and Link's deferred sword rectangle: save legitimate
; collision/shell timer changes, then consume this completed STOP update.
.proc LsrEffectsAfterEnemies
  phx
  phy
  lda TimerControl
  bne Done
  ldx #5
Loop:
  lda Enemy_Flag,x
  beq Clear
  lda Enemy_State,x
  and #$20
  bne Clear
  lda RgEnemyStun,x
  beq Next
  lda EnemyIntervalTimer,x
  sta LsrIntervalTimer,x
  cpx #5
  bcs Advance
  lda EnemyFrameTimer,x
  sta LsrFrameTimer,x
Advance:
  jsr SamusFrozenStopAdvance
  bne Next
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  bne Next
  lda #0
  sta LsrFrozenPose,x             ; Easy stopped-animation receipt expires.
  jmp Next
Clear:
  jsr LsrEffectsClear
Next:
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  bne AdvanceSlot
  lda CrossoverBehaviorVersion
  beq AdvanceSlot
  lda RgShotHitsNow,x             ; Samus-only alias; Expanded is not dispatched.
  beq AdvanceSlot
  dec RgShotHitsNow,x
AdvanceSlot:
  dex
  bpl Loop
Done:
::LsrEffectsAfterEnemiesFinish:
  ply
  plx
  rts
.endproc

.proc LsrEffectsKilled
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  beq LsrEffectsClear
Legacy:
  cmp #CHARACTER_LINK
  beq LsrEffectsClear
  cmp #CHARACTER_SIMON
  beq LsrEffectsClear
  cmp #CHARACTER_RYU
  beq LsrEffectsClear
  rts
.endproc

.proc LsrEffectsClear
  lda #0
  sta RgEnemyStun,x
  sta MmEnemyFlash,x
  sta LsrFrozenPose,x
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  bne Done
  lda #0
  jsr SamusFrozenClear        ; Enemy.die removes all status effects, including Freeze.
Done:
  lda #0
  rts
.endproc
.popseg

.pushseg
.segment "SPECIAL_EXTRA"
; Enemy.hitProj -> enemyStunner -> stunAtk before surviving damage.
; The old independent400ms timer resets on every accepted beam/bomb hit.
; Bowser's override restores movement/animation; Lakitu restores movement only.
.proc SamusLegacyEnemyStop
  lda #24
  sta RgEnemyStun,x
  sta MmEnemyFlash,x
  lda Enemy_ID,x
  cmp #Bowser
  bne SavePose
  lda #0
  sta LsrFrozenPose,x
  rts
SavePose:
  lda LsrFrozenPose,x
  bne PoseReady
  lda EnemyMetasprite,x
  bne :+
    lda #$ff
  :
  sta LsrFrozenPose,x
PoseReady:
  lda Enemy_ID,x
  cmp #Lakitu
  beq Done
  lda EnemyIntervalTimer,x
  sta LsrIntervalTimer,x
  cpx #5
  bcs Done
  lda EnemyFrameTimer,x
  sta LsrFrameTimer,x
Done:
  rts
.endproc
.popseg

.pushseg
.segment "SPECIAL_EXTRA"
; Carry1 skips physics. Original Bill/LSR counter ownership is retained.
.proc SamusLegacyMovementStopped
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  bne Legacy
  lda Enemy_ID,x
  cmp #Bowser
  beq Native
  cmp #Lakitu
  beq Native
  lda RgEnemyStun,x
  beq Native
  bne Stop
Legacy:
  cmp #CHARACTER_BILL
  bcc Native
  lda RgEnemyStun,x
  beq Native
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  beq Stop
  cmp #CHARACTER_SIMON
  beq Stop
  dec RgEnemyStun,x
Stop:
  sec
  rts
Native:
  clc
  rts
.endproc
.popseg

.pushseg
.segment "SPECIAL_EXTRA"
; Samus.DEFAULT_PROPS: STOP/FLASH/INVUL150ms. Bomb removes INVUL from
; its own properties; Enemy.checkAttackProps rejects existing INVUL first.
; RgShotHitsNow is otherwise exclusively Expanded projectile state, which
; never runs for Samus. Area/life clears and enemy health0 prevent stale reuse.
.proc SamusHardEnemyEffects
  lda #9
  ldy #1
  farcall LsrEffectsApplyStop
  lda #9
  sta MmEnemyFlash,x
  lda MmBulletType
  cmp #10
  beq Done
  lda #9
  sta RgShotHitsNow,x
Done:
  rts
.endproc
.proc SamusHardEnemyAdmissionLegacy
  lda CrossoverBehaviorVersion
  beq Allow
  lda MmEnemyHealthLo,x
  ora MmEnemyHealthHi,x
  bne Active
  lda #0
  sta RgShotHitsNow,x             ; New actor before its source health publish.
Active:
  lda RgShotHitsNow,x
  beq Allow
  lda MmBulletType
  cmp #10
  beq Bomb
  ldy MmSlot
  lda #0                         ; confirmedHit(false) still blows up the shot.
  sta MmBulletType,y
  sec
  rts
Bomb:
  lda HitBits,x
  ldy SmSlot
  ora SmBombHits,y                ; Rejected bomb contact is still once/target.
  sta SmBombHits,y
  sec
  rts
Allow:
  clc
  rts
HitBits: .byte 1,2,4,8,16,32
.endproc
.popseg
