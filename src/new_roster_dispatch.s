; Dedicated admission for the October roster expansion. Never index the
; old twelve-owner inventory or graphics tables with a new character ID.
; Each adapter restores incoming A/P before entering its actual owner.
.pushseg
.segment "NEW_ROSTER_GATE"
.macro NrCeleste Target
 php
 pha
 lda SelectedCharacter
 bne :+
 lda MarioVariant
 cmp #4
 bne :+
 pla
 plp
 farcall Target,jmp
:pla
 plp
.endmacro
.macro NrGate Name,Ice,City,Sunny,Legacy
.proc Name
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_ICE_CLIMBERS
 beq ToIce
 cmp #CHARACTER_RIVER_CITY
 beq ToCity
 cmp #CHARACTER_SUNNY
 beq ToSunny
 pla
 plp
 farcall Legacy,jmp
ToIce:
 pla
 plp
 farcall Ice,jmp
ToCity:
 pla
 plp
 farcall City,jmp
ToSunny:
 pla
 plp
 farcall Sunny,jmp
.endproc
.endmacro
NrGate NrMovement,IcMovement,RcMovement,SunnyNativeMovement,JnMovementDispatch
NrGate NrGraphics,IcGraphics,RcGraphics,SunnyGraphicsIntegrated,RlGraphicsDispatch
NrGate NrDraw,IcDraw,RcDraw,SunnyDraw,RlDrawDispatch
NrGate NrPortrait,IcPortrait,RcPortrait,SunnyPortrait,JnPortraitDispatch
NrGate NrWeapons,IcWeapons,RcWeapons,SunnyWeapons,JnWeaponsDispatch
NrGate NrInjury,IcInjuryStart,RcInjuryStart,SunnyInjuryIntegrated,JnInjuryStartDispatch
.proc NrInjuryStatus
 NrCeleste CmHostInjuryStatus
 jmp NrLegacyInjuryStatus
.endproc
NrGate NrLegacyInjuryStatus,IcInjuryStatus,RcInjuryStatus,SunnyInjuryStatus,JnInjuryStatusDispatch
NrGate NrDeathStart,IcDeathStart,RcDeathStart,SunnyDeathStart,JnInventoryDeathDispatch
NrGate NrDeath,IcDeathUpdate,RcDeath,SunnyNativeDeath,JnDeathDispatch
NrGate NrVisible,IcVisible,RcVisible,SunnyVisible,JnVisibleDispatch
NrGate NrHead,IcHead,RcHeadProbe,SunnyHead,JnHeadDispatch

.proc NrReset
 php
 pha
 lda SelectedCharacter
 bne :+
 lda MarioVariant
 cmp #4
 beq Own
:
 lda SelectedCharacter
 cmp #CHARACTER_ICE_CLIMBERS
 beq Own
 cmp #CHARACTER_RIVER_CITY
 beq Own
 cmp #CHARACTER_SUNNY
 beq Own
 pla
 plp
 farcall JnResetDispatch,jmp
Own:
 pla
 plp
 lda #0
 farcall SpecialRosterClear    ; clear shared legacy weapon/CHR overrides too
 lda SelectedCharacter
 bne :+
 farcall CmHostEnsure,jmp
:
 lda SelectedCharacter
 cmp #CHARACTER_SUNNY
 beq Sunny
 cmp #CHARACTER_ICE_CLIMBERS
 bne City
 farcall IcAreaReset,jmp
City:farcall RcReset,jmp
Sunny:farcall SunnyReset,jmp
.endproc

.proc NrBody
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_SUNNY
 beq Sunny
 cmp #CHARACTER_RIVER_CITY
 beq City
 cmp #CHARACTER_ICE_CLIMBERS
 beq Ice
 pla
 plp
 farcall JnBodyDispatch,jmp
City:
 pla
 plp
 farcall RcBodyContact,jmp
Ice:
 lda AreaType
 sta GuestBodyStompAllowed
 lda CrossoverBehaviorVersion
 sta GuestBodyNoStomp
 pla
 plp
 clc
 rts
Sunny:
 pla
 plp
 farcall SunnyBody,jmp
.endproc

; Terrain admission also validates the explicit ID argument supplied by SMB.
.proc NrAdder
 php
 pha
 cmp SelectedCharacter
 bne Legacy
 cmp #CHARACTER_ICE_CLIMBERS
 beq Ice
 cmp #CHARACTER_RIVER_CITY
 beq City
 cmp #CHARACTER_SUNNY
 beq Sunny
Legacy:pla
 plp
 farcall RlAdderDispatch,jmp
Ice:pla
 plp
 farcall IcAdder,jmp
City:pla
 plp
 farcall RcCollisionAdder,jmp
Sunny:pla
 plp
 farcall SunnyAdder,jmp
.endproc
.proc NrBox
 php
 pha
 cmp SelectedCharacter
 bne Legacy
 cmp #CHARACTER_ICE_CLIMBERS
 beq Ice
 cmp #CHARACTER_RIVER_CITY
 beq City
 cmp #CHARACTER_SUNNY
 beq Sunny
Legacy:pla
 plp
 farcall RlBoxDispatch,jmp
Ice:pla
 plp
 farcall IcBox,jmp
City:pla
 plp
 farcall RcCollisionBox,jmp
Sunny:pla
 plp
 farcall SunnyBox,jmp
.endproc

.proc NrPrepare
 php
 pha
 lda SelectedCharacter
 bne :+
 lda MarioVariant
 cmp #4
 beq Own
:
 lda SelectedCharacter
 cmp #CHARACTER_ICE_CLIMBERS
 beq Own
 cmp #CHARACTER_RIVER_CITY
 beq Own
 cmp #CHARACTER_SUNNY
 beq Own
 pla
 plp
 farcall JnPrepareDispatch,jmp
Own:
 lda SelectedCharacter
 sta InvPickupOwner,x
 lda #$fc
 sta InvPickup,x
 lda #0
 sta InvRisePhase,x
 sta InvPickupSaveLo,x
 sta InvPickupSaveHi,x
 pla
 plp
 rts
.endproc
.proc NrRise
 php
 pha
 lda SelectedCharacter
 bne :+
 lda MarioVariant
 cmp #4
 beq Native
:
 lda SelectedCharacter
 cmp #CHARACTER_ICE_CLIMBERS
 beq Native
 cmp #CHARACTER_RIVER_CITY
 beq Native
 cmp #CHARACTER_SUNNY
 beq Native
 pla
 plp
 farcall JnRiseDispatch,jmp
Native:
 pla
 plp
 clc                         ; let SMB's visible emergence move the actor
 rts
.endproc
.proc NrPrivate
 php
 pha
 lda SelectedCharacter
 bne :+
 lda MarioVariant
 cmp #4
 beq Native
:
 lda SelectedCharacter
 cmp #CHARACTER_ICE_CLIMBERS
 beq Native
 cmp #CHARACTER_RIVER_CITY
 beq Native
 cmp #CHARACTER_SUNNY
 beq Native
 pla
 plp
 farcall JnPrivateDispatch,jmp
Native:
 pla
 plp
 clc                         ; ordinary Mushroom/Flower art
 rts
.endproc
.proc NrPickupCollision
 php
 pha
 lda SelectedCharacter
 bne :+
 lda MarioVariant
 cmp #4
 beq Own
:
 lda SelectedCharacter
 cmp #CHARACTER_ICE_CLIMBERS
 beq Own
 cmp #CHARACTER_RIVER_CITY
 beq Own
 cmp #CHARACTER_SUNNY
 beq Own
 pla
 plp
 farcall JnCollisionDispatch,jmp
Own:
 pla
 plp
 lda PowerUpType,x
 cmp #2
 bcs Allowed
 lda Enemy_State,x
 bmi Allowed                 ; no pickup while still inside its block
 clc
 rts
Allowed:sec
 rts
.endproc
.proc NrPickup
 NrCeleste CmHostPickup
 lda SelectedCharacter
 cmp #CHARACTER_SUNNY
 beq Sunny
 cmp #CHARACTER_ICE_CLIMBERS
 beq Ice
 cmp #CHARACTER_RIVER_CITY
 beq City
 farcall JnPickupDispatch,jmp
Ice:
 phx
 lda PowerUpType,x
 farcall IcPickup
 plx
 bcc Native
 phx
 jsr EraseEnemyObject
 plx
 lda #6
 jmp SetupFloateyNumber
City:
 farcall RcPickup
 bcs Done
Native:
 farcall MarioSourcePowerupCollision,jmp ; native Star and extra-life handling
Done:rts
Sunny:
 farcall SunnyCollectIntegrated,jmp
.endproc
.proc NrUi
 NrCeleste CmHostUi
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_SUNNY
 beq Sunny
 cmp #CHARACTER_ICE_CLIMBERS
 beq Ice
 cmp #CHARACTER_RIVER_CITY
 beq City
 pla
 plp
 farcall VvUiDispatch,jmp
Ice:
 pla
 plp
 farcall X5NativeInventoryUiLeaf,jmp
City:
 pla
 plp
 farcall X5NativeInventoryUiLeaf
 farcall RcUi,jmp
Sunny:
 pla
 plp
 farcall SunnyUi,jmp
.endproc
.proc NrStatusName
 NrCeleste CmHostStatusName
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_SUNNY
 beq Sunny
 cmp #CHARACTER_ICE_CLIMBERS
 beq Ice
 cmp #CHARACTER_RIVER_CITY
 beq City
 pla
 plp
 farcall JnStatusName,jmp
City:
 pla
 plp
 cmp #0
 bne Done
 farcall RcStatusName,jmp
Ice:
 pla
 plp
 cmp #0
 bne Done
 phy
 ldy #6
 lda IcVariant
 beq Popo
Nana:
 lda NanaName,y
 sta VRAM_Buffer1+11,y
 dey
 bpl Nana
 jmp NameDone
Popo:
 lda PopoName,y
 sta VRAM_Buffer1+11,y
 dey
 bpl Popo
NameDone:
 ply
 lda #0
Done:rts
PopoName:.byte "POPO   "
NanaName:.byte "NANA   "
Sunny:
 pla
 plp
 farcall SunnyStatusName,jmp
.endproc
.proc NrGlobalInit
 farcall KbGlobalInit
 lda #0
 sta RcVariant
 sta MacVariant
 sta RcMarker                 ; initialize lazily, preserve selected owner's RAM
 sta CmMarker
 sta CmActive
 farcall IcGlobalInit
 farcall SunnyGlobalInit,jmp
.endproc
.proc NrFreshGameInit
 farcall KbFreshGameInit
 lda IcVariant               ; chosen alternate survives pressing Start
 pha
 farcall IcGlobalInit
 pla
 sta IcVariant
 lda #0
 sta RcMarker
 farcall SunnyGlobalInit
 farcall CmHostFresh,jmp
.endproc
.proc NrFullPower
 lda SelectedCharacter
 cmp #CHARACTER_SUNNY
 beq Sunny
 cmp #CHARACTER_ICE_CLIMBERS
 beq Ice
 cmp #CHARACTER_RIVER_CITY
 beq City
 farcall CheatsFullPower,jmp
Ice:farcall IcFullPower,jmp
City:
 farcall RcEnsure
 ldx RcVariant
 lda #64
 sta RcHealth,x
 lda #2
 sta RcTier,x
 sta PlayerStatus
 lda #1
 sta RcHudDirty
 rts
Sunny:
 farcall SunnyFullPower,jmp
.endproc
.proc NrSide
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_ICE_CLIMBERS
 beq Native
 cmp #CHARACTER_RIVER_CITY
 beq Native
 cmp #CHARACTER_SUNNY
 beq Native
 pla
 plp
 farcall Z2SideAdmission,jmp
Native:
 pla
 plp
 jmp BlockBufferColli_Side
.endproc
.proc NrColors
 NrCeleste CmHostColors
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_ICE_CLIMBERS
 beq Own
 cmp #CHARACTER_RIVER_CITY
 beq Own
 cmp #CHARACTER_SUNNY
 beq Own
 pla
 plp
 farcall X5GetPlayerColors,jmp
Own:
 pla
 plp
 farcall QueueMegaManFacePalette
 farcall QueueGuestWeaponPalette
 farcall X5QueueAreaBackdrop
 lda SelectedCharacter
 cmp #CHARACTER_SUNNY
 beq Sunny
 cmp #CHARACTER_ICE_CLIMBERS
 bne City
 farcall IcForcePalette,jmp
City:farcall RcColors,jmp
Sunny:farcall SunnyColorsIntegrated,jmp
.endproc
.proc NrMenuToggle
 lda CrossoverMenuIndex
 bne NrOtherToggle
 lda CrossoverMenuPressed
 and #Select_Button
 beq NrOtherToggle
 lda MarioVariant
 beq NrToLuigi
 cmp #1
 beq NrToCeleste
 lda #0
 beq NrMarioPublish
NrToLuigi:lda #1
 bne NrMarioPublish
NrToCeleste:lda #4
NrMarioPublish:sta MarioVariant
 sec
 rts
NrOtherToggle:
 lda CrossoverMenuPressed
 and #Select_Button
 beq No
 lda SelectedCharacter
 cmp #CHARACTER_ICE_CLIMBERS
 beq Ice
 cmp #15
 beq Mac
 cmp #CHARACTER_RIVER_CITY
 bne No
 lda RcVariant
 eor #1
 sta RcVariant
 lda #0
 sta RcPalette
 sec
 rts
Mac:
 inc MacVariant
 lda MacVariant
 cmp #MAC_ROSTER_VARIANTS
 bcc MacReady
 lda #0
 sta MacVariant
MacReady:
 lda #0
 sta LmPalette
 sec
 rts
Ice:
 lda IcVariant
 eor #1
 sta IcVariant
 lda #$ff
 sta IcPaletteAck
 sec
 rts
No:clc
 rts
.endproc
.proc NrMenuCharacter
 lda X5MenuCharacters,x
 rts
.endproc
.proc NrWorldPaletteIndex
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_ICE_CLIMBERS
 beq Native
 cmp #CHARACTER_RIVER_CITY
 beq Native
 cmp #CHARACTER_SUNNY
 beq Native
 pla
 plp
 farcall KbWorldPaletteIndex,jmp
Native:
 pla
 plp
 lda AreaType
 asl
 sta R0
 asl
 clc
 adc R0
 adc #6
 tay
 rts
.endproc
.proc NrMenuNavigate
 lda CrossoverMenuPressed
 and #Left_Dir|Right_Dir|Up_Dir|Down_Dir
 beq No
 lda #$24
 jsr NrQueueCursor
 ldx CrossoverMenuIndex
 lda CrossoverMenuPressed
 and #Up_Dir
 beq Down
 lda X5MenuUp,x
 rts
Down:
 lda CrossoverMenuPressed
 and #Down_Dir
 beq Left
 lda X5MenuDown,x
 rts
Left:
 lda CrossoverMenuPressed
 and #Left_Dir
 beq Right
 lda X5MenuLeft,x
 rts
Right:
 lda X5MenuRight,x
 rts
No:lda #$ff
 rts
.endproc
.proc NrQueueCursor
 pha
 ldy CrossoverMenuIndex
 lda X5MenuCursorLo,y
 ldx VRAM_Buffer1_Offset
 sta VRAM_Buffer1+1,x
 lda X5MenuCursorHi,y
 sta VRAM_Buffer1,x
 lda #1
 sta VRAM_Buffer1+2,x
 pla
 sta VRAM_Buffer1+3,x
 txa
 clc
 adc #4
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 rts
.endproc
.proc NrEnemyMovement
 lda SelectedCharacter
 cmp #CHARACTER_RIVER_CITY
 bne LegacyStop
 phx
 farcall RcEnemyControl
 plx
 bcs Done
 farcall NrNativeEnemyMovement,jmp
LegacyStop:
 farcall SamusLegacyMovementStopped
 bcc Native
Done:rts
Native:
 farcall NrNativeEnemyMovement,jmp
.endproc
.proc NrNativePowerupDispatch
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_SUNNY
 beq Sunny
 pla
 plp
 farcall GuestPowerupUpdate,jmp
Sunny:pla
 plp
 farcall SunnyPowerupUpdate,jmp
.endproc
.proc NrObjectWeaponTail
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_SUNNY
 beq Sunny
 pla
 plp
 farcall RlWeaponsDispatch
 farcall ProcFireball_Bubble::ProcAirBubbles,jmp
Sunny:pla
 plp
 farcall SunnyNativeWeaponTail,jmp
.endproc
.segment "NEW_ROSTER_NAMES"
.proc NrQueueSelectName
  lda SelectedCharacter
  bne CmOtherName
  lda MarioVariant
  cmp #4
  bne CmMarioName
  lda #44
  jmp NameIndex
CmMarioName:lda #0
CmOtherName:
.if ::ENABLE_MMC5_EXPANDED
  cmp #CHARACTER_SUNNY
  bne SunnyOtherName
  lda #43
  jmp NameIndex
SunnyOtherName:
  cmp #CHARACTER_ICE_CLIMBERS
  bne NrNotIceName
  lda IcVariant
  clc
  adc #37
  jmp NameIndex
NrNotIceName:
  cmp #CHARACTER_RIVER_CITY
  bne NrNotCityName
  lda RcVariant
  clc
  adc #39
  jmp NameIndex
NrNotCityName:
  cmp #CHARACTER_BASS
  bne RlOtherName
  lda RlVariant
  beq RlOriginalName
  lda #36
  jmp NameIndex
RlOriginalName:lda #CHARACTER_BASS
RlOtherName:
  cmp #15
  bne LmOtherName
  lda MacVariant
  beq LmDefaultName
  clc
  adc #40
  jmp NameIndex
LmDefaultName:
  lda #30
  jmp NameIndex
LmOtherName:
  cmp #CHARACTER_MIKE
  bne JnOtherName
  lda #31
  jmp NameIndex
JnOtherName:
  cmp #17
  bne M3OtherName
  lda #28
  clc
  adc M3Variant
  jmp NameIndex
M3OtherName:
  cmp #18
  bne :+
  lda VvVariant
  beq PnDefaultName
  clc
  adc #32
  jmp NameIndex
PnDefaultName:
  lda #24
  jmp NameIndex
:
  cmp #CHARACTER_TMNT
  bne :+
  lda TnVariant
  clc
  adc #20
  jmp NameIndex
:
  cmp #14
  bne CdOtherName
  lda #18
  clc
  adc CdVariant
  jmp NameIndex
CdOtherName:
  cmp #CHARACTER_KIRBY
  bne :+
  lda KbVariant
  beq KirbyName
  lda #32
  jmp NameIndex
KirbyName:
  lda #17
  jmp NameIndex
:
.endif
 .if ::ENABLE_MMC5_EXPANDED
  cmp #CHARACTER_MEGAMAN
  bne ProtoOriginalName
  ldx ProtoVariant
  beq NameIndex
  lda #14
  bne NameIndex
ProtoOriginalName:
  cmp #CHARACTER_LINK
  bne Z2OriginalName
  ldx Z2Variant
  beq NameIndex
  lda #16
  bne NameIndex
Z2OriginalName:
  cmp #CHARACTER_SIMON
  bne Cv3OriginalName
  ldx Cv3Variant
  beq NameIndex
  cpx #4
  bcs Cv3OriginalName
  txa
  clc
  adc #24
  bne NameIndex
Cv3OriginalName:
  lda SelectedCharacter
  cmp #CHARACTER_SCROOGE
  bne DwOriginalName
  ldx DarkwingVariant
  beq NameIndex
  lda #15
  bne NameIndex
DwOriginalName:
 .endif
  cmp #CHARACTER_BILL
  bne NameIndex
  ldx BillVariant
  beq NameIndex
  lda #CHARACTER_COUNT
NameIndex:
.if ::ENABLE_MMC5_EXPANDED
  ; Names beyond15 require the high byte of index*16. R2/R3 are not the
  ; VRAM byte counterR0; old indices retain their exact source bytes.
  pha
  lda #<Names
  sta R2
  lda #>Names
  sta R3
  pla
NamePage:
  cmp #16
  bcc :+
  inc R3
  sec
  sbc #16
  bcs NamePage
:
.endif
  asl
  asl
  asl
  asl
  tay
  ldx VRAM_Buffer1_Offset
  lda #$23
  sta VRAM_Buffer1,x
.if ::ENABLE_MMC5_EXPANDED
  lda #<X5MenuNameAddress
.else
  lda #$08
.endif
  sta VRAM_Buffer1+1,x
  lda #16
  sta VRAM_Buffer1+2,x
  sta R0
Copy:
.if ::ENABLE_MMC5_EXPANDED
  lda (R2),y
.else
  lda Names,y
.endif
  sta VRAM_Buffer1+3,x
  inx
  iny
  dec R0
  bne Copy
  txa
  clc
  adc #3
  tax
  stx VRAM_Buffer1_Offset
  lda #0
  sta VRAM_Buffer1,x
  rts
Names:
  .byte "     MARIO      ", "    MEGA MAN    ", "   SAMUS ARAN   "
  .byte "   BILL RIZER   ", "      LINK      ", " SIMON BELMONT  "
  .byte "      PIT       ", "     RYGAR      ", "     LUIGI      "
  .byte "      BASS      ", " RYU HAYABUSA   ", "   SOPHIA III   "
  .byte "SCROOGE MCDUCK  ", "   LANCE BEAN   "
 .if ::ENABLE_MMC5_EXPANDED
  .byte "   PROTO MAN    ", " DARKWING DUCK  ", " ZELDA II LINK  ", "     KIRBY      ","     CHIP       ","     DALE       ","   LEONARDO     ","   RAPHAEL      "," MICHELANGELO   ","   DONATELLO    ","   VIC VIPER    ","     GRANT      ","     SYPHA      ","    ALUCARD     ","   SMB3 MARIO   ","   SMB3 LUIGI   ","   LITTLE MAC   ","   MIKE JONES   "
  .byte "  META KNIGHT   "
  .byte "    OCTOPUS     ","    TWINBEE     ","    PENTAROU    "
  .byte "     ROLL       "
  .byte "      POPO      ","      NANA      "
  .byte "      ALEX      ","      RYAN      "
  .byte "   DOC LOUIS    ","   MIKE TYSON   ","     SUNNY      "," CELESTE MARIO  "
 .endif
.endproc
.segment "NEW_ROSTER_GATE"
.assert * <= $ae00,lderror,"Roster dispatcher overlaps Rogue auxiliary reservation"
.popseg
