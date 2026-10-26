; Crossover 2.02 inventory. Item numbers are local to each character;
; bit zero is the mushroom. Persistent state lives outside area scratch RAM.
.pushseg
.segment "SRAM"
InventoryRamStart:
InvOwnedLo: .res 12
InvOwnedHi: .res 12
InvStoredLo: .res 12
InvStoredHi: .res 12
InvViewedLo: .res 12
InvViewedHi: .res 12
InvStoredViewLo: .res 12
InvStoredViewHi: .res 12
InvSelected: .res 12
InvAmmo: .res 192
InvPickup: .res 6
InvRisePhase: .res 6
InvPickupOwner: .res 6
InvPickupSaveLo: .res 6
InvPickupSaveHi: .res 6
InvPickupViewLo: .res 6
InvPickupViewHi: .res 6
InvPrevious: .res 1
InvFresh: .res 1
InvDirty: .res 1
InvItem: .res 1
InvIndex: .res 1
InvObject: .res 1
InvCount: .res 1
InvRandom: .res 1
InvCandidate: .res 1
InvCost: .res 1
InvTmp: .res 1
InvTmpHi: .res 1
InvRefill: .res 1
InvRefillTick: .res 1
InvRefillRemain: .res 1
InvHudAmmo: .res 1
InvHudName: .res 2
InvHudActive: .res 1
InvHudPhysical: .res 1
InvHudSegments: .res 1
InventoryRamEnd:

.segment "INVENTORY"
.proc InventoryInit
  lda #<InventoryRamStart
  sta R0
  lda #>InventoryRamStart
  sta R1
  ldy #0
  tya
Clear:
  sta (R0),y
  inc R0
  bne :+
    inc R1
  :
  ldx R0
  cpx #<InventoryRamEnd
  bne Clear
  ldx R1
  cpx #>InventoryRamEnd
  bne Clear
  ldx #0
Ammo:
  lda InvInitialAmmo,x
  sta InvAmmo,x
  inx
  cpx #192
  bne Ammo
  jmp SamusFreezeInit
  nop
.endproc

; Carry marks characters using the 2.02 inventory, rather than the custom
; Pit/Rygar progression or Mario/Luigi's original flower.
; Easy uses the linked six-character build's native three power tiers.
; Carry=classic guest in Easy, X clobbered, A/Y preserved. Mario has no2.02
; inventory in either mode. Later additions retain their own current systems.
.proc InventoryLegacyClassic
 .if ::ENABLE_MMC5_EXPANDED
  farcall InventoryLegacyItemLeaf,jmp
  .res 2,$ea
  .assert *-InventoryLegacyClassic=20,error,"Original leaf span preserved"
 .else
  ldx CrossoverBehaviorVersion
  bne No
  ldx SelectedCharacter
  cpx #CHARACTER_MEGAMAN
  bcc No
  cpx #CHARACTER_SIMON+1
  bcs No
  sec
  rts
No:
  clc
  rts
 .endif
.endproc

.proc InventorySupported
 .if ::ENABLE_MMC5_EXPANDED
  ; These six profiles own their own items and never use the legacy2.02
  ; inventory. Match the old dispatch chain's A=ID, X=ID, C=0 exactly.
  ; Mac15 retains his supported-item path. All other IDs use the old entry.
  php
  pha
  phx
  ldx SelectedCharacter
  cpx #13
  bcc LegacySupported
  cpx #15
  beq LegacySupported
  cpx #20
  bcs LegacySupported
  ; CPX20 left C clear. None of the checks/pops changes V/D/I, so discard
  ; saved P rather than restoring its old carry. TXA supplies final N/Z.
  pla
  pla
  pla
  txa
  rts
LegacySupported:
  plx
  pla
  plp
  farcall RlSupportedDispatch,jmp
  .assert *-InventorySupported=46,error,"Original leaf span preserved"
 .else
  jsr InventoryLegacyClassic
  bcc ModernRules
  clc                           ; No2.02 ownership, ammo or UI in classic Easy.
  rts
ModernRules:
  ldx SelectedCharacter
  ; Enable each inventory only together with its native weapon migration.
  cpx #CHARACTER_MEGAMAN
  beq Supported
  cpx #CHARACTER_BASS
  beq Supported
  cpx #CHARACTER_SAMUS
  beq Supported
  cpx #CHARACTER_BILL
  beq Supported
  cpx #CHARACTER_LINK
  beq Supported
  cpx #CHARACTER_SIMON
  beq Supported
  cpx #CHARACTER_RYU
  beq Supported
  cpx #CHARACTER_SOPHIA
  beq Supported
  clc
  rts
Supported:
  sec
  rts
 .endif
.endproc

; A=local item, X/Y clobbered. Mushroom is checked through PlayerStatus so
; the native hurt/transform routine remains the authority during transitions.
.proc InventoryHas
  pha
  lda PlayerStatus
  bne :+
    pla
    clc
    rts
  :
  pla
  jmp InventoryHasRaw
.endproc
.proc InventoryHasRaw
  jsr InventoryLegacyClassic
  bcc ModernRules
  clc                           ; No2.02 ownership, ammo or UI in classic Easy.
  rts
ModernRules:
  tay
  ldx SelectedCharacter
  lda InvOwnedLo,x
  and InvBitLo,y
  bne Yes
  lda InvOwnedHi,x
  and InvBitHi,y
  bne Yes
  clc
  rts
Yes:
  sec
  rts
.endproc

.proc InventoryWeaponCost
  jsr InventoryIndex
  lda InvCosts,x
  rts
.endproc
.proc InventoryMaximum
  jsr InventoryIndex
  lda SelectedCharacter
  cmp #CHARACTER_RYU
  bne Normal
  lda InvOwnedLo+CHARACTER_RYU
  and #$80
  beq Normal
  lda #99
  rts
Normal:
  lda InvMaxAmmo,x
  rts
.endproc

.proc InventoryIndex
  sta InvItem
  lda SelectedCharacter
  asl
  asl
  asl
  asl
  clc
  adc InvItem
  tax
  stx InvIndex
  rts
.endproc

; A=local ammo item, Y=cost. Commit only after pool/terrain checks succeed.
.proc InventorySpend
  jsr InventoryLegacyClassic
  bcc ModernRules
  clc                           ; No2.02 ownership, ammo or UI in classic Easy.
  rts
ModernRules:
  sty InvCost
  jsr InventoryIndex
  lda InvAmmoIndex,x
  cmp #$ff
  beq Free
  tax
  lda StarInvincibleTimer
  bne Free                      ; Source starPwr prevents ammunition loss.
  lda InvAmmo,x
  cmp InvCost
  bcc Done
  sec
  sbc InvCost
  sta InvAmmo,x
  inc InvDirty
Free:
  sec
Done:
  rts
.endproc

.proc InventoryPreparePickup
  stx InvObject
  lda #0
  sta InvRisePhase,x
  lda #$fc
  sta InvPickup,x
  jsr InventorySupported
  jcc Done
  ldx InvObject
  lda SelectedCharacter
  sta InvPickupOwner,x
  lda PowerUpType,x
  cmp #2
  jcs Done
  lda PlayerStatus
  beq Mushroom
  ldx SelectedCharacter
  lda InvStoredLo,x
  ora InvStoredHi,x
  beq Roll
  ldy InvObject
  lda InvStoredLo,x
  sta InvPickupSaveLo,y
  lda InvStoredHi,x
  sta InvPickupSaveHi,y
  lda InvStoredViewLo,x
  sta InvPickupViewLo,y
  lda InvStoredViewHi,x
  sta InvPickupViewHi,y
  lda #$ff
  jne Publish
Mushroom:
  lda #0
  jeq Publish
Roll:
  lda #0
  sta InvTmp                    ; At most one new pass over uncollected upgrades.
CountPass:
  lda #0
  sta InvCount
  lda #1
  sta InvCandidate
Count:
  jsr Available
  bcc :+
    inc InvCount
  :
  inc InvCandidate
  ldx SelectedCharacter
  lda InvItemCount,x
  cmp InvCandidate
  bcs Count
  lda InvCount
  bne Random
  lda InvTmp
  bne Fallback
  inc InvTmp
  ; 2.02 starts another tier pass after all choices have been revealed.
  ; Owned upgrades stay excluded; a missed world pickup may appear again.
  ldx SelectedCharacter
  lda #0
  sta InvViewedLo,x
  sta InvViewedHi,x
  jmp CountPass
Random:
  ; Use a rejection-free reduction of the native PRNG into the candidate
  ; count. Candidates are consumed when revealed, as in prepareNextUpgrade.
  lda PseudoRandomBitReg+1
Reduce:
  cmp InvCount
  bcc Reduced
  sbc InvCount
  jmp Reduce
Reduced:
  sta InvRandom
  lda #1
  sta InvCandidate
Choose:
  jsr Available
  bcc Next
  lda InvRandom
  beq Chosen
  dec InvRandom
Next:
  inc InvCandidate
  jmp Choose
Chosen:
  ldy InvCandidate
  ldx SelectedCharacter
  lda InvViewedLo,x
  ora InvBitLo,y
  sta InvViewedLo,x
  lda InvViewedHi,x
  ora InvBitHi,y
  sta InvViewedHi,x
  tya
  bne Publish
Fallback:
  ldx SelectedCharacter
  lda InvFallback,x
Publish:
  ldx InvObject
  sta InvPickup,x
  pha
  farcall RemainingPrepareAmmo
  pla
  cmp #0
  beq NativeMushroom
  lda #1
NativeMushroom:
  sta PowerUpType,x
Done:
  ldx InvObject
  rts
Available:
  lda InvCandidate
  jsr InventoryHasRaw
  bcs No                        ; Ownership, not just viewing, excludes repeats.
  lda InvCandidate
  jsr InventoryIndex
  lda InvAvailability,x
  beq No
  cmp #$ff
  beq CheckViewed
  cmp #$fe
  beq Replacement
  jsr InventoryHasRaw
  bcc No
  jmp CheckViewed
Replacement:
  ldx SelectedCharacter
  lda InvOwnedLo,x
  and InvReplacementLo,x
  bne CheckViewed
  lda InvOwnedHi,x
  and InvReplacementHi,x
  beq No
CheckViewed:
  ldy InvCandidate
  ldx SelectedCharacter
  lda InvViewedLo,x
  and InvBitLo,y
  bne No
  lda InvViewedHi,x
  and InvBitHi,y
  bne No
  sec
  rts
No:
  clc
  rts
.endproc

; Called before native flower handling. Carry=handled, including an empty
; max-tier pickup. Stars and 1-ups continue through the native code.
.proc InventoryCollect
  stx InvObject
  jsr InventorySupported
  jcc Native
  ldx InvObject
  lda InvPickupOwner,x
  cmp SelectedCharacter
  jne Native
  lda InvPickup,x
  cmp #$fc
  jeq Native
  cmp #$ff
  jeq Recover
  cmp #$fe
  jeq Refill
  cmp #$fd
  jeq Empty
  cmp #0
  jeq Mushroom
  jsr InventoryGrant
  jmp Collected
Mushroom:
  ldx SelectedCharacter
  lda InvOwnedLo,x
  ora #1
  ora InvMushroomLo,x
  sta InvOwnedLo,x
  lda InvOwnedHi,x
  ora InvMushroomHi,x
  sta InvOwnedHi,x
  ; The mushroom still uses the character's source power-up animation.
  lda #0
  sta PlayerStatus
  farcall GuestBeginPowerup
  jmp Collected
Recover:
  ldx SelectedCharacter
  ldy InvObject
  lda InvPickupSaveLo,y
  ora InvOwnedLo,x
  sta InvOwnedLo,x
  lda InvPickupSaveHi,y
  ora InvOwnedHi,x
  sta InvOwnedHi,x
  lda InvPickupViewLo,y
  sta InvViewedLo,x
  lda InvPickupViewHi,y
  sta InvViewedHi,x
  lda #0
  sta InvStoredLo,x
  sta InvStoredHi,x
  jmp Collected
Refill:
  lda AvPickupAmmoItem,x
  sta AvRefillItem
  lda Square2SoundQueue
  and #$ff-Sfx_PowerUpGrab
  sta Square2SoundQueue
  jsr InventoryRefillPickup
Collected:
  inc InvDirty
Empty:
  ldx InvObject
  sec
  rts
Native:
  ldx InvObject
  clc
  rts
.endproc

; A=upgrade ID. Availability and exclusivity are separate: a missed upgrade
; stays viewed, and a later exclusive weapon replaces the equipped one.
.proc InventoryGrant
  jsr InventoryIndex
  lda InvSingleLo,x
  eor #$ff
  ldy SelectedCharacter
  and InvOwnedLo,y
  sta InvOwnedLo,y
  lda InvSingleHi,x
  eor #$ff
  and InvOwnedHi,y
  sta InvOwnedHi,y
  ldx InvItem
  lda InvOwnedLo,y
  ora InvBitLo,x
  sta InvOwnedLo,y
  lda InvOwnedHi,y
  ora InvBitHi,x
  sta InvOwnedHi,y
  ldx InvIndex
  lda InvAutoEquip,x
  beq :+
    lda InvItem
    sta InvSelected,y
  :
  inc InvDirty
  farcall RemainingGrant
  rts
.endproc

.proc InventoryHurt
 .if ::ENABLE_MMC5_EXPANDED
  farcall Z2InventoryHurtGate,jmp
  ; Unreachable native tail padding: same-bank HUD helpers, no new RAM.
HudLease:
  ; InventoryIndex is stable throughout this source HUD producer. Valid
  ; legacy robot defaults are indices10/90; native-family aliases bypassUI.
  lda InvIndex
  and #$7f
  cmp #$10
  beq HudKeep
  inc ReloadCHRBank
  lda #0
  sta InvHudActive
HudKeep:
  lda #0
  rts
UniformMeter:
  ; Post-loop X is base+7. First==last iff the monotone7-cell bar is uniform.
  lda #$47
  sta VRAM_Buffer1+5,x
  txa
  sec
  sbc #6
  tax
  rts
  .res 1,$ea
  .assert *-InventoryHurt=50,error,"Original leaf span preserved"
 .else
  jsr InventorySupported
  bcc Done
  ldx SelectedCharacter
  lda InvMushroomLo,x
  ora #1
  eor #$ff
  and InvOwnedLo,x
  sta InvStoredLo,x
  lda InvMushroomHi,x
  eor #$ff
  and InvOwnedHi,x
  sta InvStoredHi,x
  lda InvViewedLo,x
  sta InvStoredViewLo,x
  lda InvViewedHi,x
  sta InvStoredViewHi,x
  jsr InventoryRemove
Done:
  lda #0
  rts
 .endif
.endproc
.proc InventoryRemove
  ldx SelectedCharacter
  lda #0
  sta InvOwnedLo,x
  sta InvOwnedHi,x
  sta InvViewedLo,x
  sta InvViewedHi,x
  sta InvSelected,x
  inc InvDirty
  jsr InventoryClearActive
  ldx SelectedCharacter
  rts
.endproc
.proc InventoryDeath
  jsr InventorySupported
  bcc Done
  jsr InventoryRemove
  lda #0
  sta InvStoredLo,x
  sta InvStoredHi,x
Done:
  rts
.endproc

; Energy balancer: selected non-full weapon first, otherwise least energy
; among owned weapons. One 4-unit increment every 50 ms with world frozen.
.proc InventoryRefillPickup
  lda #40
  jmp InventoryRefillAmount
.endproc
.proc InventoryRefillAmount
  sta InvDropAmount
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  beq Energy
  cmp #CHARACTER_MEGAMAN
  beq Energy
.if ::ENABLE_MMC5_EXPANDED
  farcall DwRefill
.else
  farcall RemainingRefill
.endif
  rts
Energy:
  ldx SelectedCharacter
  lda InvSelected,x
  beq Balance
  jsr InventoryIndex
  lda InvAmmo,x
  cmp #112
  bcc Begin
Balance:
  lda #8
  ldy SelectedCharacter
  cpy #CHARACTER_BASS
  beq :+
    lda #9
  :
  jsr InventoryHas
  bcc Done
  lda #112
  sta InvTmp
  lda #0
  sta InvRefill
  lda #1
  sta InvCandidate
Find:
  lda InvCandidate
  jsr InventoryHas
  bcc Next
  lda InvCandidate
  jsr InventoryIndex
  lda InvMaxAmmo,x
  beq Next
  lda InvAmmo,x
  cmp InvTmp
  bcs Next
  sta InvTmp
  stx InvRefill
Next:
  inc InvCandidate
  lda InvCandidate
  cmp #9
  bcc Find
  ldx InvRefill
  beq Done
Begin:
  stx InvRefill
  lda InvDropAmount
  sta InvRefillRemain
  lda #3
  sta InvRefillTick
  lda #29                       ; Native one-shot refill (track 28).
  ldy InvDropAmount
  cpy #13
  bcc :+
    lda #63                     ; Continuous refill (track 62), stop at full.
  :
  sta SsAudioRequest
Done:
  rts
.endproc

.proc InventoryUiTick
  lda GuestHurtTicks
  beq :+
    lda #0
    sta InvFresh
    lda GuestHurtKind
    cmp #CHARACTER_LINK
    beq HurtPhysicalHistory
    cmp #CHARACTER_SIMON
    beq HurtPhysicalHistory
    cmp #CHARACTER_RYU
    beq HurtPhysicalHistory
    lda #0
    sta InvPrevious
    rts                       ; Source disableInput includes weapon selection.
HurtPhysicalHistory:
    lda SavedJoypad1Bits
    sta InvPrevious            ; Held Select is no synthetic press on recovery.
    rts
  :
  lda SavedJoypad1Bits
  eor InvPrevious
  and SavedJoypad1Bits
  sta InvFresh
  lda SavedJoypad1Bits
  sta InvPrevious
  jsr InventorySupported
  jcc HideHud
  lda OperMode
  cmp #1
  jne HideHud
  lda GameEngineSubroutine
  cmp #8
  jcc HideHud
  jne Done
  lda InvRefill
  beq Input
  lda #2
  sta TimerControl
  dec InvRefillTick
  jne Hud
  lda #3
  sta InvRefillTick
  ldx InvRefill
  lda InvAmmo,x
  clc
  adc #4
  cmp #112
  bcc :+
    lda #112
  :
  sta InvAmmo,x
  inc InvDirty
  lda InvRefillRemain
  sec
  sbc #4
  sta InvRefillRemain
  beq RefillDone
  lda InvAmmo,x
  cmp #112
  bcc Hud
RefillDone:
  lda InvDropAmount
  cmp #13
  bcc :+
    lda #$f2                    ; Native stop-SFX command $f1, encoded +1.
    sta SsAudioRequest
  :
  lda #0
  sta InvRefill
  sta TimerControl
  jmp Hud
Input:
  lda GamePauseStatus
  and #1
  bne Paused
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  beq CycleDirect
  cmp #CHARACTER_BASS
  bne Hud
CycleDirect:
  lda InvFresh
  and #Select_Button
  beq Hud
  jmp Cycle
Paused:
  lda InvFresh
  and #Select_Button
  beq :+
    ldx SelectedCharacter
    lda #0
 .if ::ENABLE_MMC5_EXPANDED
    jsr InventorySelectionCommit
 .else
    sta InvSelected,x
 .endif
    jmp Changed
  :
  lda InvFresh
  and #Left_Dir | Right_Dir
  beq Hud
Cycle:
  jsr InventoryCycle
Changed:
  inc InvDirty
 .if ::ENABLE_MMC5_EXPANDED
  nop                          ; Commit owns cleanup, preserving the old span.
  nop
  nop
 .else
  jsr InventoryClearActive
 .endif
  jmp Hud
Hud:
  jsr InventoryHud
Done:
  rts
HideHud:
  lda InvHudActive
  beq Done
  lda #0
  sta InvHudActive
  inc ReloadCHRBank
  inc InvDirty
  rts
.endproc

.proc InventoryClearActive
  farcall SpecialClear
  ; Source selection clears projectiles and charge before changing palette.
  lda #0
  sta AvSlash
  sta AvSamusMode
  sta AvPending
  sta MmChargeFrames
  sta MmCharging
  sta RgAttack
  sta RgShootPose
  sta MmBulletType
  sta MmBulletType+1
  sta MmBulletType+2
  sta MmBulletType+3
  ldx #9
ClearShots:
  sta RgShotType,x
  dex
  bpl ClearShots
  rts
.endproc

.proc InventoryCycle
  ldx SelectedCharacter
  lda InvSelected,x
  sta InvCandidate
  lda #16
  sta InvCount
Next:
  lda GamePauseStatus
  and #1
  beq Forward
  lda InvFresh
  and #Left_Dir
  beq Forward
  dec InvCandidate
  lda InvCandidate
  bpl Check
  ldx SelectedCharacter
  lda InvItemCount,x
  sta InvCandidate
  jmp Check
Forward:
  inc InvCandidate
  ldx SelectedCharacter
  lda InvItemCount,x
  cmp InvCandidate
  bcs Check
  lda #0
  sta InvCandidate
Check:
  lda InvCandidate
  beq Chosen
  jsr InventoryIndex
  lda InvSelectable,x
  beq Again
  lda InvCandidate
  jsr InventoryHas
  bcs Chosen
Again:
  dec InvCount
  bne Next
  rts
Chosen:
  ldx SelectedCharacter
  lda InvCandidate
 .if ::ENABLE_MMC5_EXPANDED
  jmp InventorySelectionCommit
  nop                          ; Tail call keeps the old span and stack depth.
 .else
  sta InvSelected,x
  rts
 .endif
.endproc

.proc InventoryHud
  lda InvDirty
  jeq Done
  lda DisableScreenFlag
  jne Done
  ldx VRAM_Buffer1_Offset
  cpx #1
  jcs Done                       ; Keep space for native producers later in this update.
  lda #0
  sta InvDirty
 .if ::ENABLE_MMC5_EXPANDED
  nop
  nop
  nop
 .else
  inc ReloadCHRBank
 .endif
  ldy SelectedCharacter
  lda InvSelected,y
  jsr InventoryIndex
  lda InvNameLo,x
  sta R0
  lda InvNameHi,x
  sta R1
  lda InvAmmoIndex,x
  tax
  lda #$ff
  cpx #$ff
  beq NoAmmo
  lda InvAmmo,x
NoAmmo:
  sta InvHudAmmo
  ldx VRAM_Buffer1_Offset
  lda #$20
  sta VRAM_Buffer1,x
  lda #$23
  sta VRAM_Buffer1+1,x
  lda #11
  sta VRAM_Buffer1+2,x
  txa
  clc
  adc #3
  tax
  ldy #0
Name:
  lda (R0),y
Put:
  sta VRAM_Buffer1,x
  inx
  iny
  cpy #7
  bne Name
  lda #$24
  sta VRAM_Buffer1,x
  inx
  lda InvHudAmmo
  cmp #$ff
  bne Digits
  lda #$24
  sta VRAM_Buffer1,x
  sta VRAM_Buffer1+1,x
  sta VRAM_Buffer1+2,x
  jmp End
Digits:
  ldy #0
Hundreds:
  cmp #100
  bcc Tens
  sbc #100
  iny
  bne Hundreds
Tens:
  pha
  tya
  sta VRAM_Buffer1,x
  pla
  ldy #0
Ten:
  cmp #10
  bcc Ones
  sbc #10
  iny
  bne Ten
Ones:
  sta VRAM_Buffer1+2,x
  tya
  sta VRAM_Buffer1+1,x
End:
  txa
  clc
  adc #3
  tax
  ; The assembly character map has already encoded the name strings. HUD
  ; glyphs use the safe HUD rows; the icon fits between WORLD and TIME.
  lda #$20
  sta VRAM_Buffer1,x
  lda #$37
  sta VRAM_Buffer1+1,x
  lda #2
  sta VRAM_Buffer1+2,x
  lda #$24
  sta VRAM_Buffer1+3,x
  sta VRAM_Buffer1+4,x
  lda #$20
  sta VRAM_Buffer1+5,x
  lda #$57
  sta VRAM_Buffer1+6,x
  lda #2
  sta VRAM_Buffer1+7,x
  lda #$24
  sta VRAM_Buffer1+8,x
  sta VRAM_Buffer1+9,x
 .if ::ENABLE_MMC5_EXPANDED
  jsr InventoryHurt::HudLease
  nop
  nop
 .else
  lda #0
  sta InvHudActive
 .endif
  ldy SelectedCharacter
  cpy #CHARACTER_BASS
  beq MegaIcon
  cpy #CHARACTER_MEGAMAN
  bne Meter
MegaIcon:
  lda InvSelected,y
  beq Meter
  tay
  dey
  lda InvHudPhysicalBanks,y
  sta InvHudPhysical
  inc InvHudActive
  inc ReloadCHRBank
  lda #$2a
  sta VRAM_Buffer1+3,x
  lda #$2b
  sta VRAM_Buffer1+4,x
  lda #$2c
  sta VRAM_Buffer1+8,x
  lda #$2d
  sta VRAM_Buffer1+9,x
Meter:
  lda #$20
  sta VRAM_Buffer1+10,x
  lda #$4a
  sta VRAM_Buffer1+11,x
  lda #7
  sta VRAM_Buffer1+12,x
  lda InvHudAmmo
  cmp #$ff
  bne :+
    lda #0
  :
  lsr
  lsr
  lsr
  sta InvHudSegments
  ldy #0
Bar:
 .if !::ENABLE_MMC5_EXPANDED
  lda #$24
 .endif
  lda InvHudSegments
  beq BlankBar
  cmp #1
  beq HalfBar
  dec InvHudSegments
  dec InvHudSegments
  lda #$2f
  bne EmptyBar
HalfBar:
  dec InvHudSegments
  lda #$2e
  bne EmptyBar
BlankBar:
  lda #$24
EmptyBar:
  sta VRAM_Buffer1+13,x
  inx
  iny
  cpy #7
  bne Bar
 .if ::ENABLE_MMC5_EXPANDED
  lda VRAM_Buffer1+6,x
  cmp VRAM_Buffer1+12,x
  bne NotUniform
  jsr InventoryHurt::UniformMeter
NotUniform:
  jmp InventoryHudColdTail
  nop
 .else
  txa
  clc
  adc #13
  tax
  lda #0
  sta VRAM_Buffer1,x
  stx VRAM_Buffer1_Offset
 .endif
Done:
  rts
.endproc
.include "inventory_data.inc"
.popseg

.if ::ENABLE_MMC5_EXPANDED
.pushseg
.segment "INVENTORY_FONT_LEASE"
; Original complete native14B queue tail, relocated into verified bank59 FF.
.proc InventoryHudColdTail
  txa
  clc
  adc #13
  tax
  lda #0
  sta VRAM_Buffer1,x
  stx VRAM_Buffer1_Offset
  rts
.endproc
.popseg
.endif
