; Dedicated, non-gameplay front end. The title never runs GameCoreRoutine.
.pushseg
.segment "SRAM"
CrossoverMenuState: .res 1       ; 0 title, 1/2 select, 3/4 options, 5/6 cheats
CrossoverMenuPressed: .res 1
CrossoverMenuIndex: .res 1
MarioVariant: .res 1
CrossoverContinue: .res 1
.if ::ENABLE_MMC5_EXPANDED
.segment "PROTO_MENU"
.else
.segment "CHAR_SELECT"
.endif

.proc CrossoverMenuInput
  lda #0
  sta NumberOfPlayers
  sta Sprite0HitDetectFlag
  lda #$18
  sta DemoTimer                 ; never enter the native attract demo
  lda SavedJoypad1Bits
  ora SavedJoypad2Bits
  tax
  stx CrossoverMenuPressed
  eor CrossoverMenuButtons
  and CrossoverMenuPressed
  sta CrossoverMenuPressed
  stx CrossoverMenuButtons
  lda CrossoverMenuState
  cmp #1
  jeq BuildScreen
  cmp #2
  jeq SelectInput
  cmp #3
  jeq BuildOptions
  cmp #4
  jeq OptionsInput
  cmp #5
  jeq BuildOptions
  cmp #6
  jeq CheatsInput
.if ::ENABLE_MMC5_EXPANDED
  cmp #7
  jeq BuildOptions
  cmp #8
  jeq SoundInput
.endif
  lda CrossoverTitleDrawn
  bne TitleInput
  inc CrossoverTitleDrawn
  lda #0
  sta CrossoverOptionsFocus
  farcall MoveAllSpritesOffscreen
  jsr QueueStaticTitleGuide
TitleInput:
  lda CrossoverMenuPressed
  and #Up_Dir | Down_Dir | Select_Button
  beq TitleConfirm
  lda CrossoverOptionsFocus
  eor #1
  sta CrossoverOptionsFocus
  jsr QueueTitleCursor
TitleConfirm:
  lda CrossoverMenuPressed
  and #Start_Button | A_Button
  beq NotReady
  lda CrossoverOptionsFocus
  beq StartSelected
  lda #3
  bne OpenPage
StartSelected:
  lda CrossoverMenuButtons
  and #Start_Button
  beq FreshGame
  lda CrossoverMenuButtons
  and #A_Button
FreshGame:
  sta CrossoverContinue
  lda #1
OpenPage:
.if ::ENABLE_MMC5_EXPANDED
  ldx #0
  stx CrossoverOptionsFocus
.endif
  sta CrossoverMenuState
  sta DisableScreenFlag
NotReady:
  lda #0
  rts
BuildScreen:
  lda Mirror_PPUMASK
  and #$18
  bne NotReady
  ; Rendering is off; the lag-NMI path leaves the PPU address alone.
  farcall InitializeNameTables
  lda PPUSTATUS
  lda #$20
  sta PPUADDR
  lda #0
  sta PPUADDR
  lda #<SelectNameTable
  sta R0
  lda #>SelectNameTable
  sta R1
  ldx #4
  ldy #0
CopyPage:
  lda (R0),y
  sta PPUDATA
  iny
  bne CopyPage
  inc R1
  dex
  bne CopyPage
  lda #2
  sta CrossoverMenuState
  jmp ScreenPalette
BuildOptions:
  lda Mirror_PPUMASK
  and #$18
  jne NotReady
  farcall InitializeNameTables
.if ::ENABLE_MMC5_EXPANDED
  farcall DrawOptionsPage
.else
  jsr DrawOptionsPage
.endif
.if ::ENABLE_MMC5_EXPANDED
  lda CrossoverMenuState
  cmp #7
  bne :+
  farcall SoundTestBuildPage
  lda #8
  jmp OptionsBuilt
:
.endif
  lda CrossoverMenuState
  cmp #5
  bne NormalOptions
  farcall CheatsPatchPage
  lda #6
  bne OptionsBuilt
NormalOptions:
  lda #4
OptionsBuilt:
  sta CrossoverMenuState
ScreenPalette:
  lda #$3f
  sta PPUADDR
  lda #0
  sta PPUADDR
  ldx #0
CopyPalette:
  lda SelectPalette,x
  sta PPUDATA
  inx
  cpx #16
  bne CopyPalette
  lda #$3c
  sta AreaChrBank
.if ::MAPPER_MMC5
  lda #$3d
  sta AreaChrBank+1
  lda #$3e
  sta AreaChrBank+2
  lda #$3f
  sta AreaChrBank+3
.else
  lda #$3e
  sta AreaChrBank+1
.endif
  inc ReloadCHRBank
  jsr MenuResolveCharacter
  lda #0
  sta PlayerStatus
  sta RgOamRotation
  sta GuestOamRotationActive
.if !::ENABLE_MMC5_EXPANDED
  sta CrossoverOptionsFocus
.endif
  sta ScreenLeft_PageLoc
  sta ScreenLeft_X_Pos
  sta HorizontalScroll
  sta VerticalScroll
  lda #1
  sta PlayerSize
  lda #2
  sta BackgroundColorCtrl
  lda CrossoverMenuState
  cmp #2
  bne OptionsReady
  jsr QueueSelection
  jmp ScreenReady
OptionsReady:
  farcall MoveAllSpritesOffscreen
  lda CrossoverMenuState
  cmp #6
  beq CheatsReady
.if ::ENABLE_MMC5_EXPANDED
  cmp #8
  bne :+
  farcall SoundTestQueue
  jmp ScreenReady
:
.endif
  farcall QueueOptions
  jmp ScreenReady
CheatsReady:
  farcall QueueCheats
ScreenReady:
  lda #0
  sta DisableScreenFlag
  rts
OptionsInput:
  lda CrossoverMenuPressed
  and #B_Button
  jne ReturnTitle
  lda CrossoverMenuPressed
  and #Up_Dir | Down_Dir
  beq OptionsToggle
  lda CrossoverOptionsFocus
  ldx CrossoverMenuPressed
  cpx #Up_Dir
  beq OptionsUp
  clc
  adc #1
.if ::ENABLE_MMC5_EXPANDED
  cmp #4
.else
  cmp #3
.endif
  bcc OptionsFocusReady
  lda #0
  beq OptionsFocusReady
OptionsUp:
  sec
  sbc #1
  bpl OptionsFocusReady
.if ::ENABLE_MMC5_EXPANDED
  lda #3
.else
  lda #2
.endif
OptionsFocusReady:
  sta CrossoverOptionsFocus
  jmp OptionsChanged
OptionsToggle:
  lda CrossoverMenuPressed
  and #A_Button | Start_Button | Select_Button | Left_Dir | Right_Dir
  beq MenuIdle
  lda CrossoverOptionsFocus
.if ::ENABLE_MMC5_EXPANDED
  cmp #3
  beq OpenSoundTest
.endif
  cmp #2
  beq OpenCheats
  cmp #0
  bne ToggleBehavior
  lda PlayerOutlinesOff
  eor #1
  sta PlayerOutlinesOff
  jmp OptionsChanged
ToggleBehavior:
  lda CrossoverBehaviorVersion
  eor #1
  sta CrossoverBehaviorVersion
OptionsChanged:
  lda #Sfx_CoinGrab
  sta Square2SoundQueue
  farcall QueueOptions
MenuIdle:
  lda #0
  rts
.if ::ENABLE_MMC5_EXPANDED
OpenSoundTest:
  farcall SoundTestEnter
  jmp MenuIdle
SoundInput:
  farcall SoundTestInput
  jmp MenuIdle
.endif
OpenCheats:
.if ::ENABLE_MMC5_EXPANDED
  lda #0
  sta CrossoverOptionsFocus
.endif
  lda #5
  sta CrossoverMenuState
  lda #1
  sta DisableScreenFlag
  jmp MenuIdle
CheatsInput:
  farcall CheatsMenuInput
  jmp MenuIdle
SelectInput:
  lda CrossoverMenuPressed
  and #B_Button
  beq CheckConfirm
ReturnTitle:
  ; Rebuild the static title using the native initialization path.
  lda #0
  sta CrossoverMenuState
  sta CrossoverTitleDrawn
  sta BackgroundColorCtrl
  sta OperMode_Task
  sta CrossoverOptionsFocus
  lda #1
  sta DisableScreenFlag
  farcall MoveAllSpritesOffscreen
  lda #0
  rts
CheckConfirm:
  lda CrossoverMenuPressed
  and #Start_Button | A_Button
  beq CheckDirection
  farcall CheatsApplyStartingLevel
  lda CrossoverContinue
  bne :+
 .if ::ENABLE_MMC5_EXPANDED
.if ::ENABLE_MMC5_EXPANDED
    farcall NrFreshGameInit
.else
    farcall X5InventoryInit
.endif
 .else
    farcall InventoryInit
 .endif
  :
  lda #0
  sta CrossoverMenuState
  sta BackgroundColorCtrl
  lda #1
  sta DisableScreenFlag
  farcall MoveAllSpritesOffscreen
  lda #Sfx_CoinGrab
  sta Square2SoundQueue
  lda CrossoverContinue
  ora #Start_Button
  rts
CheckDirection:
.if ::ENABLE_MMC5_EXPANDED
  farcall NrMenuToggle
  bcc NrNoToggle
  lda CrossoverMenuIndex
  jmp Changed
NrNoToggle:
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  bne RlNoToggle
  lda CrossoverMenuPressed
  and #Select_Button
  beq RlNoToggle
  lda RlVariant
  eor #1
  sta RlVariant
  lda #0
  sta RlPalette
  lda CrossoverMenuIndex
  jmp Changed
RlNoToggle:
  lda SelectedCharacter
  cmp #18
  bne PnNoToggle
  lda CrossoverMenuPressed
  and #Select_Button
  beq PnNoToggle
  inc VvVariant
  lda VvVariant
  and #3
  sta VvVariant
  lda CrossoverMenuIndex
  jmp Changed
PnNoToggle:
  lda SelectedCharacter
  cmp #CHARACTER_KIRBY
  bne KbNoToggle
  lda CrossoverMenuPressed
  and #Select_Button
  beq KbNoToggle
  lda KbVariant
  eor #1
  sta KbVariant
  lda CrossoverMenuIndex
  jmp Changed
KbNoToggle:
  lda SelectedCharacter
  cmp #CHARACTER_TMNT
  bne TnNoToggle
  lda CrossoverMenuPressed
  and #Select_Button
  beq TnNoToggle
  inc TnVariant
  lda TnVariant
  and #3
  sta TnVariant
  lda CrossoverMenuIndex
  jmp Changed
TnNoToggle:
.endif
  lda CrossoverMenuIndex
  bne :+
    lda CrossoverMenuPressed
    and #Select_Button
    beq :+
    lda MarioVariant
    eor #1
    sta MarioVariant
    lda #0
    jmp Changed
  :
 .if ::ENABLE_MMC5_EXPANDED
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  bne ProtoNoToggle
  lda CrossoverMenuPressed
  and #Select_Button
  beq ProtoNoToggle
  lda ProtoVariant
  eor #1
  sta ProtoVariant
  lda #0
  sta ProtoAudioState
  sta MmLastPalette
  sta SsLastPalette
  lda CrossoverMenuIndex
  jmp Changed
ProtoNoToggle:
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne Z2NoToggle
  lda CrossoverMenuPressed
  and #Select_Button
  beq Z2NoToggle
  lda Z2Variant
  eor #1
  sta Z2Variant
  lda CrossoverMenuIndex
  jmp Changed
Z2NoToggle:
  lda SelectedCharacter
  cmp #CHARACTER_SIMON
  bne Cv3NoToggle
  lda CrossoverMenuPressed
  and #Select_Button
  beq Cv3NoToggle
  lda Cv3Variant
  clc
  adc #1
  and #3
  sta Cv3Variant
  lda CrossoverMenuIndex
  jmp Changed
Cv3NoToggle:
  lda SelectedCharacter
  cmp #CHARACTER_SCROOGE
  bne DwNoToggle
  lda CrossoverMenuPressed
  and #Select_Button
  beq DwNoToggle
  lda DarkwingVariant
  eor #1
  sta DarkwingVariant
  lda #0
  sta DwAnim
  sta DwPhase
  sta DwAnimTick
  lda CrossoverMenuIndex
  jmp Changed
DwNoToggle:
  lda SelectedCharacter
  cmp #14
  bne CdNoToggle
  lda CrossoverMenuPressed
  and #Select_Button
  beq CdNoToggle
  lda CdVariant
  eor #1
  sta CdVariant
  lda CrossoverMenuIndex
  jmp Changed
CdNoToggle:
  lda SelectedCharacter
  cmp #17
  bne M3NoToggle
  lda CrossoverMenuPressed
  and #Select_Button
  beq M3NoToggle
  lda M3Variant
  eor #1
  sta M3Variant
  lda CrossoverMenuIndex
  jmp Changed
M3NoToggle:
 .endif
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bne Navigation
  lda CrossoverMenuPressed
  and #Select_Button
  beq Navigation
  lda BillVariant
  eor #1
  sta BillVariant
  lda CrossoverMenuIndex
  jmp Changed
Navigation:
.if ::ENABLE_MMC5_EXPANDED
  farcall NrMenuNavigate
  cmp #$ff
  jeq NotReady
  jmp Changed
.else
  lda CrossoverMenuPressed
  and #Select_Button | Left_Dir | Right_Dir | Up_Dir | Down_Dir
  jeq NotReady
  and #Up_Dir | Down_Dir
  bne Vertical
  lda CrossoverMenuPressed
  and #Left_Dir
  bne Previous
  lda #$24
  jsr QueueCursor
  lda CrossoverMenuIndex
  clc
  adc #1
  cmp #MENU_CHARACTER_COUNT
  bcc Changed
  lda #0
  beq Changed
Vertical:
OtherRow:
  lda #$24
  jsr QueueCursor
  lda CrossoverMenuIndex
  clc
  adc #6
  cmp #MENU_CHARACTER_COUNT
  bcc Changed
  sbc #MENU_CHARACTER_COUNT
  jmp Changed
Previous:
  lda #$24
  jsr QueueCursor
  lda CrossoverMenuIndex
  bne :+
    lda #MENU_CHARACTER_COUNT
  :
  sec
  sbc #1
.endif
Changed:
  sta CrossoverMenuIndex
.if ::ENABLE_MMC5_EXPANDED
  lda #0
  sta RlOutlineBypass
.endif
  jsr MenuResolveCharacter
  lda #1
  sta PlayerSize                  ; returning to Mario preserves small form
  lda #Sfx_CoinGrab
  sta Square2SoundQueue
  jsr QueueSelection
  lda #0
  rts
.endproc

.proc MenuResolveCharacter
.if ::ENABLE_MMC5_EXPANDED
  farcall CmHostResolveCharacter,jmp
  .res 16,$ea
.else
  ldx CrossoverMenuIndex
.if ::ENABLE_MMC5_EXPANDED
  farcall NrMenuCharacter
.else
  lda MenuCharacters,x
.endif
  bne Done
  ldx MarioVariant
  beq Done
  lda #CHARACTER_LUIGI
Done:
  sta SelectedCharacter
  rts
.if !::ENABLE_MMC5_EXPANDED
MenuCharacters: .byte 0,1,2,3,4,5,6,7,12,9,10,11
.endif
.endif
.endproc

.proc QueueSelection
 .if ::ENABLE_MMC5_EXPANDED
  farcall Z2MenuPrepare
 .endif
  farcall GetPlayerColors
  jsr QueueSelectName
  jsr QueueVariantHint
.if ::ENABLE_MMC5_EXPANDED
  lda #$fd
.else
  lda #$3f
.endif
  jsr QueueCursor
.if ::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5
  jmp MenuPreviewBudget
.else
  jmp DrawSelectionPreview
.endif
.endproc

.proc DrawSelectionPreview
  farcall MoveAllSpritesOffscreen
  farcall DrawPlayer_Intermediate
  ldx CrossoverMenuIndex
  lda PreviewX,x
  sta Player_X_Position
  lda #152
.if ::ENABLE_MMC5_EXPANDED
  lda #160
  ldx SelectedCharacter
  cpx #15
  bne :+
  lda #160
:
.endif
  sta Player_Y_Position
  lda #0
  sta ObjectVerticalFlip
  sta RgOamRotation
  sta GuestOamRotationActive
  sta CurrentOAMOffset
  tay
  ldx ObjectMetasprite
.if ::ENABLE_MMC5_EXPANDED
  farcall X5PortraitRender
.else
  farcall DrawMetasprite
.endif
  rts
PreviewX: .byte 120,121,118,116,120,120
  .byte 120,120,120,121,120,120
.if ::ENABLE_MMC5_EXPANDED
  .byte 120,120,120,120,120,120,120
  .repeat 9
  .byte 120
  .endrepeat
.endif
.endproc

.proc QueueVariantHint
.if ::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5
  jmp PnMenuVariantHintGate
.else
  ldx VRAM_Buffer1_Offset
.endif
  lda #$23
  sta VRAM_Buffer1,x
.if ::ENABLE_MMC5_EXPANDED
  lda #$46
.else
  lda #$26
.endif
  sta VRAM_Buffer1+1,x
  lda #20
  sta VRAM_Buffer1+2,x
  ldy #0
Copy:
  lda SelectedCharacter
 .if ::ENABLE_MMC5_EXPANDED
  cmp #CHARACTER_ICE_CLIMBERS
  beq NrAlternateHint
  cmp #15
  beq NrAlternateHint
  cmp #CHARACTER_RIVER_CITY
  bne NrOtherHint
NrAlternateHint:
  lda ProtoHint,y
  jmp Put
NrOtherHint:
  cmp #CHARACTER_BASS
  bne RlNoHint
  lda ProtoHint,y
  jmp Put
RlNoHint:
  cmp #18
  bne PnNoHint
  lda ProtoHint,y
  jmp Put
PnNoHint:
  cmp #CHARACTER_KIRBY
  bne KbNoHint
  lda ProtoHint,y
  jmp Put
KbNoHint:
  cmp #CHARACTER_TMNT
  bne TnNoHint
  lda TnHint,y
  jmp Put
TnNoHint:
  cmp #17
  bne M3NoHint
  lda M3Hint,y
  jmp Put
M3NoHint:
  cmp #14
  bne CdNoHint
  lda CdHint,y
  jmp Put
CdNoHint:
  cmp #CHARACTER_MEGAMAN
  bne ProtoNoHint
  lda ProtoHint,y
  jmp Put
ProtoNoHint:
  cmp #CHARACTER_LINK
  bne Z2NoHint
  lda Z2Hint,y
  jmp Put
Z2NoHint:
  cmp #CHARACTER_SIMON
  bne Cv3NoHint
  lda Cv3Hint,y
  jmp Put
Cv3NoHint:
  cmp #CHARACTER_SCROOGE
  bne DwNoHint
  lda DwHint,y
  jmp Put
DwNoHint:
 .endif
  cmp #CHARACTER_BILL
  beq BillHint
  lda CrossoverMenuIndex
  bne Blank
  lda MarioHint,y
  jmp Put
BillHint:
  lda Hint,y
  jmp Put
Blank:
  lda #$24
Put:
  sta VRAM_Buffer1+3,x
  inx
  iny
  cpy #20
  jne Copy
  txa
  clc
  adc #3
  tax
  lda #0
  sta VRAM_Buffer1,x
  stx VRAM_Buffer1_Offset
  rts
 .if ::ENABLE_MMC5_EXPANDED
Hint: .byte "SELECT  CHANGE HERO "
MarioHint: .byte "SELECT  CHANGE HERO "
 .else
Hint: .byte "SELECT - BILL/LANCE "
MarioHint: .byte "SELECT - MARIO/LUIGI"
 .endif
 .if ::ENABLE_MMC5_EXPANDED
DwHint: .byte "SELECT  CHANGE HERO "
Z2Hint: .byte "SELECT  CHANGE HERO "
TnHint: .byte "SELECT  CHANGE HERO "
CdHint: .byte "SELECT  CHANGE HERO "
Cv3Hint: .byte "SELECT  CHANGE HERO "
M3Hint: .byte "SELECT  CHANGE HERO "
ProtoHint: .byte "SELECT  CHANGE HERO "
 .assert *-ProtoHint=20,error,"Proto hint width"
 .endif
.endproc

.proc QueueSelectName
.if ::ENABLE_MMC5_EXPANDED
  farcall NrQueueSelectName,jmp
.else
  lda SelectedCharacter
.if ::ENABLE_MMC5_EXPANDED
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
  jmp NameIndex
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
  .byte "   DOC LOUIS    ","   MIKE TYSON   "
 .endif
.endif
.endproc

.proc QueueCursor
.if ::ENABLE_MMC5_EXPANDED
  farcall NrQueueCursor,jmp
.endif
  pha
  ldy CrossoverMenuIndex
.if ::ENABLE_MMC5_EXPANDED
  lda X5MenuCursorLo,y
.else
  lda CursorLow,y
.endif
  ldx VRAM_Buffer1_Offset
  sta VRAM_Buffer1+1,x
.if ::ENABLE_MMC5_EXPANDED
  lda X5MenuCursorHi,y
.else
  lda CursorHigh,y
.endif
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
CursorLow: .byte $62,$67,$6c,$71,$76,$7b,$22,$27,$2c,$31,$36,$3b
CursorHigh:.byte $21,$21,$21,$21,$21,$21,$22,$22,$22,$22,$22,$22
.endproc

 ; Options are a dedicated title page; the character grid has no option row.
.if ::ENABLE_MMC5_EXPANDED
.pushseg
.segment "X5_MENU_UI"
.endif
.proc DrawOptionsPage
  lda PPUSTATUS
  lda #$20
  sta PPUADDR
  lda #0
  sta PPUADDR
  lda #$24
  ldx #4
  ldy #0
Blank:
  sta PPUDATA
  iny
  bne Blank
  dex
  bne Blank
  lda #$23
  sta PPUADDR
  lda #$c0
  sta PPUADDR
  lda #$aa                     ; Bright palette2 for text and both option rows.
  ldx #64
Attributes:
  sta PPUDATA
  dex
  bne Attributes
  ldy #0
Next:
  lda Text,y
  beq Done
  sta PPUADDR
  iny
  lda Text,y
  sta PPUADDR
  iny
  lda Text,y
  tax
  iny
Copy:
  lda Text,y
  sta PPUDATA
  iny
  dex
  bne Copy
  beq Next
Done:
  rts
Text:
  .byte $20,$cb,7,"OPTIONS"
  .byte $22,$65,22,"CHEATS                "
.if ::ENABLE_MMC5_EXPANDED
  .byte $22,$c5,22,"AUDIO TEST            "
  .byte $23,$4a,8,"B - BACK"
.else
  .byte $22,$ca,8,"B - BACK"
.endif
  .byte 0
.endproc
.if ::ENABLE_MMC5_EXPANDED
.popseg
.endif

.pushseg
.segment "CHEATS_MENU_COLD"
.proc QueueOptions
  lda #$21
  sta R1
  lda #$65
  sta R0
  ldy #0
  lda PlayerOutlinesOff
  beq Shadows
  ldy #22
Shadows:
  jsr QueueOptionLine
  lda #$22
  sta R1
  lda #$05
  sta R0
  ldy #44
  lda CrossoverBehaviorVersion
  beq Behavior
  ldy #66
Behavior:
  jsr QueueOptionLine
.if ::ENABLE_MMC5_EXPANDED
  lda #4
.else
  lda #3
.endif
  sta R4
  jmp QueueOptionCursor
.endproc
.proc QueueOptionCursor
  lda #$24
  jsr CursorBoth
  ldy CrossoverOptionsFocus
  ldx VRAM_Buffer1_Offset
  lda CursorLo,y
  sta VRAM_Buffer1+1,x
  lda CursorHi,y
  sta VRAM_Buffer1,x
  lda #1
  sta VRAM_Buffer1+2,x
  lda #$3f
  sta VRAM_Buffer1+3,x
  jmp AdvanceCursor
CursorBoth:
  pha
  ldx VRAM_Buffer1_Offset
  ldy #0
NextCursor:
  lda CursorHi,y
  sta VRAM_Buffer1,x
  lda CursorLo,y
  sta VRAM_Buffer1+1,x
  lda #1
  sta VRAM_Buffer1+2,x
  pla
  pha
  sta VRAM_Buffer1+3,x
  inx
  inx
  inx
  inx
  iny
  cpy R4
  bne NextCursor
  pla
  stx VRAM_Buffer1_Offset
  rts
AdvanceCursor:
  inx
  inx
  inx
  inx
  stx VRAM_Buffer1_Offset
  lda #0
  sta VRAM_Buffer1,x
  rts
CursorHi:.byte $21,$22,$22
.if ::ENABLE_MMC5_EXPANDED
  .byte $22
.endif
CursorLo:.byte $63,$03,$63
.if ::ENABLE_MMC5_EXPANDED
  .byte $c3
.endif
.endproc

.proc QueueOptionLine
  ldx VRAM_Buffer1_Offset
  lda R1
  sta VRAM_Buffer1,x
  lda R0
  sta VRAM_Buffer1+1,x
  lda #22
  sta VRAM_Buffer1+2,x
  sta R2
Copy:
  lda Text,y
  sta VRAM_Buffer1+3,x
  iny
  inx
  dec R2
  bne Copy
  inx
  inx
  inx
  stx VRAM_Buffer1_Offset
  lda #0
  sta VRAM_Buffer1,x
  rts
Text:
  .byte "PLAYER OUTLINES  ON   "
  .byte "PLAYER OUTLINES  OFF  "
  .byte "MODE             EASY "
  .byte "MODE             HARD "
.endproc
.popseg

.proc QueueTitleCursor
  ldx VRAM_Buffer1_Offset
  ldy #0
Next:
  lda #$22
  sta VRAM_Buffer1,x
  lda Low,y
  sta VRAM_Buffer1+1,x
  lda #1
  sta VRAM_Buffer1+2,x
  lda #$24
  cpy CrossoverOptionsFocus
  bne Put
  lda #$2a
Put:
  sta VRAM_Buffer1+3,x
  inx
  inx
  inx
  inx
  iny
  cpy #2
  bne Next
  stx VRAM_Buffer1_Offset
  lda #0
  sta VRAM_Buffer1,x
  rts
Low:.byte $4a,$8a
.endproc

.proc QueueStaticTitleGuide
  ldx VRAM_Buffer1_Offset
  ldy #0
Copy:
  lda Guide,y
  sta VRAM_Buffer1,x
  inx
  iny
  cpy #End-Guide
  bne Copy
  stx VRAM_Buffer1_Offset
  lda #0
  sta VRAM_Buffer1,x
  jmp QueueTitleCursor
Guide:
  .byte $22,$46,18,"      START       "
  .byte $22,$86,18,"      OPTIONS     "
  .byte $22,$c6,18,"                  "
End:
.endproc

SelectPalette:
.if ::ENABLE_MMC5_EXPANDED
  .byte $0f,$00,$10,$30, $0f,$30,$30,$30
.else
  .byte $0f,$00,$10,$30, $0f,$11,$21,$30
.endif
 .if ::ENABLE_MMC5_EXPANDED
  .byte $0f,$28,$28,$28, $0f,$21,$11,$21
 .else
  .byte $0f,$28,$28,$28, $0f,$00,$10,$30 ; Bright gold option glyphs use palette2.
 .endif
SelectNameTable:
.if ::ENABLE_MMC5_EXPANDED
  .incbin "chr/raw/roster-expansion-menu.bin"
.else
  .incbin "chr/raw/character-select.bin"
.endif
.popseg

.if ::ENABLE_MMC5_EXPANDED
.pushseg
.segment "CHAR_SELECT"
.res $b22,$ff ; Keep following Rush reset leaf at its original public PC.
.popseg
.endif

.if ::ENABLE_MMC5_EXPANDED
.pushseg
.segment "NEW_ROSTER_GATE"
.include "roster_expansion_menu.inc"
.popseg
.endif


.if ::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5
; Only an already-live ship Select-only toggle can reuse the published hint.
; Initial/rebuilt pages keep DisableScreenFlag set through QueueSelection;
; navigation with any direction retains the original complete hint writer.
; All four ship variants have the identical native ProtoHint20 cells.
.pushseg
.segment "PN_MENU_HINT"
.proc PnMenuVariantHintGate
 jmp PnMenuInitialHintDispatch
 jmp MenuHintQueuePolicy
 .res 21,$ea
Original:
 ldx VRAM_Buffer1_Offset
 jmp QueueVariantHint+3
.endproc
.popseg
.endif


.if ::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5
.pushseg
.segment "PN_MENU_HINT"
; BuildScreen owns direct PPUDATA while display is off and GameLoop's
; NmiDisable is negative. Lag NMI skips PPU work with DisableScreenFlag!=0.
; Mask IRQ only around the paired address/data transaction; retain NMI/audio.
.proc PnMenuInitialHintDispatch
 .res 7,$ea ; Existing entry/copy/native addresses remain genuine.
 lda CrossoverMenuState
 cmp #2
 bne Native
 lda DisableScreenFlag
 beq Native
 lda Mirror_PPUMASK
 and #$18
 bne Native
 lda NmiDisable
 bpl Native
 php
 sei
 lda Mirror_PPUCTRL
 and #$fb
 sta PPUCTRL
 bit PPUSTATUS
 lda #$23
 sta PPUADDR
 lda #$46
 sta PPUADDR
 ldy #0
Copy:
 lda MenuStaticLegend,y
 sta PPUDATA
 iny
 cpy #20
 bne Copy
 lda Mirror_PPUCTRL
 sta PPUCTRL
 plp
 nop
Native:
 lda CrossoverMenuPressed
 jmp PnMenuVariantHintGate+3
.endproc
.popseg
.endif

.include "menu_vram_budget.s"
