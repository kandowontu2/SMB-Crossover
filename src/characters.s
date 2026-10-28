; Crossover character dispatch. All gameplay continues to use SMB's level,
; camera, collision, enemy and transition systems.

.pushseg
.segment "SRAM"
SelectedCharacter: .res 1
CrossoverMenuButtons: .res 1
CrossoverTitleDrawn: .res 1
MegaManShotPose: .res 1
GuestLandingLimit: .res 1
.popseg

.segment "FIXED"

.proc GuestLandingWindow
  ; SMB's five-pixel landing band assumes Mario's capped fall speed. Simon
  ; reaches seven pixels per update, so include the complete crossed band.
  pha
  lda SelectedCharacter
  beq Native
  lda Player_Y_Speed
  cmp #5
  bcc Native
  clc
  adc #1
  sta GuestLandingLimit
  pla
  cpy GuestLandingLimit
  rts
Native:
  pla
  cpy #5
  rts
.endproc

.proc CrossoverHeadProbe
.if ::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5
  jmp MmNativeHeadShortcut
.else
  jmp BillHeadDispatch
.endif
  ; Contextual cold-query tail uses existing unreachable57-EA head padding.
  ; The extra JMP from SAMUS preserves all flags/AXY/SP and adds no bank call.
::SophiaSourceHeadTail:
  farcall SophiaSourceHeadProbe, jmp
::CrossoverSourceFootProbe:
.if ::ENABLE_MMC5_EXPANDED
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  beq FootCold
  cmp #CHARACTER_SOPHIA
  bne FootNative
  cpy #31
  bne FootCold
  bit SmClearance
  bmi FootNative
FootCold:
  farcall Z2SourceFeetDispatch, jmp
FootNative:
  jmp BlockBufferColli_Feet
  .assert *-CrossoverHeadProbe=62,error,"Expanded head/feet dispatch span"
.else
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne FootNative
  cpy #31
  bne FootCold
  bit SmClearance
  bmi FootNative
FootCold:
  farcall SophiaSourceFeet, jmp
FootNative:
  jmp BlockBufferColli_Feet
  .res 2,$ea                 ; Original60-byte head region remains exact size.
  .assert *-CrossoverHeadProbe=60,error,"Old resident head-dispatch span"
.endif
.endproc

.proc CrossoverSourceSideProbe
 .if ::ENABLE_MMC5_EXPANDED
 .if ::MAPPER_MMC5
  jmp MmNativeSideShortcut
::MmNativeHeadShortcut:
  ; Mega Man / Proto Man reach the ordinary query after the other families'
  ; exact-ID gates. Keep its actual native head cell and every later consumer.
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  bcs OrdinaryHeadDispatch
  jmp BlockBufferColli_Head
OrdinaryHeadDispatch:
  jmp BillHeadDispatch
::MmSideDispatchPrefix:
   ; Former solecaller selector span: first ordered half of ordinary farcall.
   ; A/P have been restored before this genuine JMP-only helper entry.
   SMC_StoreValue SafecallA,a
   lda #<TnFastSideGate
   SMC_StoreLowByte FarcallJmpTarget,a
   jmp MmSideDispatchTail
   nop
 .else
  farcall TnFastSideGate,jmp
  .res 10,$ea
 .endif
 .else
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne Native
  farcall SophiaSourceSideProbe, jmp
Native:
  jmp BlockBufferColli_Side
 .endif
  .assert *-CrossoverSourceSideProbe=28,error,"Original side leaf footprint"
.endproc

 .if ::ENABLE_MMC5_EXPANDED
.proc CrossoverHeadWithinTerrain
  farcall Z2HeadWithinTerrain, jmp
  .res 1,$ea ; Reuse two bytes for the expanded feet selector above.
.else
.proc CrossoverHeadWithinTerrain
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  beq Sophia
  jmp PlayerHeadWithinTerrain
Sophia:
  lda MmYFraction+1
  asl
  lda Player_Y_Position
  adc #16
  cmp #32
  rts
.endif
.endproc

.proc GuestFootContactSide
  farcall RosterGuestFootContactSide, jmp
.endproc

.pushseg
.segment "SAMUS"
.proc CrossoverGuestHeadProbe
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  beq Sophia
  cmp #CHARACTER_SAMUS
  beq Samus
  jmp ScroogeHeadProbe
Sophia:
  jmp SophiaSourceHeadTail
Samus:
  jmp SamusHeadProbe
.endproc

.proc CrossoverInit
 .if ::ENABLE_MMC5_EXPANDED
.if ::ENABLE_MMC5_EXPANDED
  farcall NrGlobalInit
.else
  farcall ProtoGlobalInit
.endif
 .else
  farcall InventoryInit
 .endif
.if ::MAPPER_MMC3
  lda #28
  sta GuestHudNextDelay
  sta GuestHudIrqDelay
.endif
  lda #0
  sta SelectedCharacter
  sta BillVariant
  sta MarioVariant
  sta CrossoverMenuIndex
  sta CrossoverMenuButtons
  sta CrossoverTitleDrawn
  sta CrossoverMenuState
  sta CrossoverMenuPressed
  sta CrossoverContinue
  sta CheatInvincible
  sta CheatStartLevel
  sta OutlineSourceHi
  sta OutlineTinyHi
  sta OutlineTinyHi+1
  sta OutlineTinyHi+2
  sta OutlineTinyHi+3
  sta OutlineTinyNext
  sta OutlineTinyLast
  sta CrossoverBehaviorVersion ; 0=1.0 default; only power/reset resets preference.
  sta GuestOamRotationActive
  sta RgOamFirst
  sta RgOamUsed
  sta MarioWaterActive
  sta MegaManShotPose
  lda #1
  sta PlayerOutlinesOff        ; Extra black masks are opt-in to reduce sprite load.
  BankPRGC #.bank(MmMM_HAIR_STANDRight)
  jsr MegaManClearState
  jsr MegaManAudioInit
  jsr SamusClearState
  jsr SamusAudioInit
  lda #0
  sta RgAudioCharacter
  sta RgSfx
  sta XgAudioSong
  lda #$ff
  sta GuestAudioCharacter
  sta XgAudioCharacter
  sta AvAudioChar
  rts
.endproc
.popseg

; Only the existing bank3 status-text producer reads these49 bytes.
.pushseg
.segment "RENDER"
CharacterNamesPrefix:
  .byte "MARIO  ", "MEGAMAN", "SAMUS  ", "BILL   ", "LINK   ", "SIMON  ", "PIT    "
.popseg
CharacterNames:
  .byte "RYGAR  ", "LUIGI  ", "BASS   ", "RYU    ", "SOPHIA "
  .byte "SCROOGE", "LANCE  "

.segment "RENDER"

.proc QueueMegaManFacePalette
  ldx VRAM_Buffer1_Offset
PaletteSelector:
.if ::ENABLE_MMC5_EXPANDED
  farcall NrWorldPaletteIndex
.else
  jsr GuestWorldPaletteIndex
  jmp Guest
.endif
  .res 20-(*-PaletteSelector), $ea
Guest:
  lda #6
  sta R0
Copy:
  lda FacePalette,y
  sta VRAM_Buffer1,x
  inx
  iny
  dec R0
  bne Copy
  stx VRAM_Buffer1_Offset
  lda #0
  sta VRAM_Buffer1,x
  rts
FacePalette:
  ; White is shared with sprite palette 2. Palette 3 retains the Goomba's
  ; black and brown, with the hosted skin tone in its middle entry.
  .byte $3f, $1d, 3, $0f, $37, $17
  .byte $3f, $1d, 3, $0f, $30, $10
  .byte $3f, $1d, 3, $0f, $36, $17
  .byte $3f, $1d, 3, $0c, $3c, $1c
  .byte $3f, $1d, 3, $00, $30, $10
.endproc

.proc QueueGuestWeaponPalette
  ldx VRAM_Buffer1_Offset
  lda #$3f
  sta VRAM_Buffer1,x
  lda #$19
  sta VRAM_Buffer1+1,x
  lda #3
  sta VRAM_Buffer1+2,x
  lda #$16
  sta VRAM_Buffer1+3,x
  lda #$30
  sta VRAM_Buffer1+4,x
  lda #$27
  sta VRAM_Buffer1+5,x
  txa
  clc
  adc #6
  tax
  stx VRAM_Buffer1_Offset
  lda #0
  sta VRAM_Buffer1,x
  rts
; This is also the mushroom / world-object palette. Guest artwork must
; share these colors instead of recoloring every object using palette 2.
.endproc

 .proc CrossoverPatchStatusName
 .if ::ENABLE_MMC5_EXPANDED
.if ::ENABLE_MMC5_EXPANDED
  farcall RlNameDispatch,jmp
.else
  farcall ProtoStatusName,jmp
.endif
  .res 48,$ea
  .assert *-CrossoverPatchStatusName=66,error,"Status wrapper original span"
 .else
  ; Called with WriteGameText's message number in A. Preserve A and X.
  cmp #0
  bne Done
  pha
  txa
  pha
  lda SelectedCharacter
  beq Restore
  cmp #CHARACTER_BILL
  bne NameIndex
  ldx BillVariant
  beq NameIndex
  lda #CHARACTER_COUNT
NameIndex:
  sta R0
  asl
  asl
  asl
  sec
  sbc R0
  sta R0
  ldy #6
Copy:
  tya
  clc
  adc R0
  tax
  cpx #49
  bcc Prefix
  lda CharacterNames-49,x
  clc
  bcc WriteName
Prefix:
  lda CharacterNamesPrefix,x
WriteName:
    sta VRAM_Buffer1+11,y
    dey
    bmi Restore
    jmp Copy
Restore:
  pla
  tax
  pla
Done:
  rts
 .endif
.endproc

.segment "PLAYER"

.proc CrossoverJumpProfile
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  bne OtherCharacter
  lda SwimmingFlag
  bne Done
  lda GameEngineSubroutine
  cmp #8
  bne Done
  lda #$40
  sta VerticalForce
  sta VerticalForceDown
  sta Player_Y_MoveForce
  lda #$fb
SetSpeed:
  sta Player_Y_Speed
Done:
  rts
OtherCharacter:
  cmp #CHARACTER_LUIGI
  bne Done
  jmp LuigiNativeJump
.endproc

.proc MegaManGraphics
.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
  farcall CompactMegaManPaletteState
.else
  farcall MegaManPaletteState
.endif
  lda Player_SprAttrib
  and #$fc
  sta Player_SprAttrib
  lda GuestPowerupActive
  beq :+
    lda GuestPowerupPose
    jmp PoseReady
  :
  lda #10
  ldy GameEngineSubroutine
  cpy #$0b
  bne :+
    lda #0
    sta ObjectMetasprite
    rts
  :
  cpy #$0a
  beq HurtPose
  ldy GuestHurtTicks
  beq MovementPose
HurtPose:
  lda #15                       ; Shared source recoil/native injury pose.
  bne PoseReady
MovementPose:
  ldy MmSliding
  beq :+
    lda #12
    bne PoseReady
  :
  ldy Player_State
  cpy #3
  beq Climbing
  cpy #0
  bne Air
  ldy MegaManShotPose
  bne Shooting
  lda #0
  ldy Player_X_Speed
  beq PoseReady
  lda MmWalkFrame
  clc
  adc #1
  bne PoseReady
Shooting:
  lda #5
  ldy Player_X_Speed
  beq PoseReady
  lda MmWalkFrame
  clc
  adc #6
  bne PoseReady
Air:
  lda #10
  ldy MegaManShotPose
  beq PoseReady
  lda #11
  bne PoseReady
Climbing:
  lda Up_Down_Buttons
  and #$0c
  bne MoveClimbAnimation
  lda GameEngineSubroutine
  cmp #4
  bne ClimbFrame
MoveClimbAnimation:
  inc MmClimbTimer
  lda MmClimbTimer
  cmp #6
  bcc ClimbFrame
  lda #0
  sta MmClimbTimer
  lda MmClimbFrame
  eor #1
  sta MmClimbFrame
ClimbFrame:
  lda MmClimbFrame
  clc
  adc #13
PoseReady:
  sta MmRenderPose
  jsr GuestVisualStatus
  tay
  lda MmRenderPose
  bne NormalPose
  lda GuestPowerupActive
  bne NormalPose
  lda MmStepTimer
  beq NormalPose
  lda GameEngineSubroutine
  cmp #8
  bne NormalPose
  tya
  clc
  adc #64                        ; Appended skin step poses keep 16-pose strides.
  jmp AddBase
NormalPose:
  lda MmRenderPose
  cpy #0
  bne PoweredPose
  ldy GuestPowerupActive
  bne AddBase
  ldy Player_State
  bne Wind
  ldy Player_X_Speed
  beq AddBase
Wind:
  ldy FrameCounter
  tya
  and #1
  beq HairPose
  ; Restore the selected pose after using A to test the wind phase.
  lda MmRenderPose
  clc
  adc #48
  bne AddBase
HairPose:
  lda MmRenderPose
  jmp AddBase
PoweredPose:
  clc
  adc #16
  dey
  beq AddBase
  clc
  adc #16
AddBase:
  clc
  adc #METASPRITE_MM_HAIR_STAND
  sta ObjectMetasprite
 .if ::ENABLE_MMC5_EXPANDED
  farcall ProtoPoseSelector
 .else
  farcall SpecialMegaPose
 .endif
  lda Player_Rel_XPos
  sta Player_Pos_ForScroll
  rts
.endproc
