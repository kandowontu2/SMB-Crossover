; Dedicated, non-gameplay front end. The title never runs GameCoreRoutine.
.pushseg
.segment "SRAM"
CrossoverMenuState: .res 1       ; 0 title, 1 build select, 2 select, 3 build options, 4 options
CrossoverMenuPressed: .res 1
CrossoverMenuIndex: .res 1
MarioVariant: .res 1
CrossoverContinue: .res 1
.segment "CHAR_SELECT"

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
  jsr DrawOptionsPage
  lda #4
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
  sta CrossoverOptionsFocus
  sta ScreenLeft_PageLoc
  sta ScreenLeft_X_Pos
  sta HorizontalScroll
  sta VerticalScroll
  lda #1
  sta PlayerSize
  lda #2
  sta BackgroundColorCtrl
  lda CrossoverMenuState
  cmp #4
  beq OptionsReady
  jsr QueueSelection
  jmp ScreenReady
OptionsReady:
  farcall MoveAllSpritesOffscreen
  jsr QueueOptions
ScreenReady:
  lda #0
  sta DisableScreenFlag
  rts
OptionsInput:
  lda CrossoverMenuPressed
  and #B_Button
  bne ReturnTitle
  lda CrossoverMenuPressed
  and #Up_Dir | Down_Dir
  beq OptionsToggle
  lda CrossoverOptionsFocus
  eor #1
  sta CrossoverOptionsFocus
  jmp OptionsChanged
OptionsToggle:
  lda CrossoverMenuPressed
  and #A_Button | Start_Button | Select_Button | Left_Dir | Right_Dir
  beq MenuIdle
  lda CrossoverOptionsFocus
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
  jsr QueueOptions
MenuIdle:
  lda #0
  rts
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
  lda CrossoverContinue
  bne :+
    farcall InventoryInit
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
Changed:
  sta CrossoverMenuIndex
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
  ldx CrossoverMenuIndex
  lda MenuCharacters,x
  bne Done
  ldx MarioVariant
  beq Done
  lda #CHARACTER_LUIGI
Done:
  sta SelectedCharacter
  rts
MenuCharacters: .byte 0,1,2,3,4,5,6,7,12,9,10,11
.endproc

.proc QueueSelection
  farcall GetPlayerColors
  jsr QueueSelectName
  jsr QueueVariantHint
  lda #$3f
  jsr QueueCursor
  jmp DrawSelectionPreview
.endproc

.proc DrawSelectionPreview
  farcall MoveAllSpritesOffscreen
  farcall DrawPlayer_Intermediate
  ldx CrossoverMenuIndex
  lda PreviewX,x
  sta Player_X_Position
  lda #152
  sta Player_Y_Position
  lda #0
  sta ObjectVerticalFlip
  sta RgOamRotation
  sta GuestOamRotationActive
  sta CurrentOAMOffset
  tay
  ldx ObjectMetasprite
  farcall DrawMetasprite
  rts
PreviewX: .byte 120,121,118,116,120,120
  .byte 120,120,120,121,120,120
.endproc

.proc QueueVariantHint
  ldx VRAM_Buffer1_Offset
  lda #$23
  sta VRAM_Buffer1,x
  lda #$26
  sta VRAM_Buffer1+1,x
  lda #20
  sta VRAM_Buffer1+2,x
  ldy #0
Copy:
  lda SelectedCharacter
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
  bne Copy
  txa
  clc
  adc #3
  tax
  lda #0
  sta VRAM_Buffer1,x
  stx VRAM_Buffer1_Offset
  rts
Hint: .byte "SELECT - BILL/LANCE "
MarioHint: .byte "SELECT - MARIO/LUIGI"
.endproc

.proc QueueSelectName
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bne NameIndex
  ldx BillVariant
  beq NameIndex
  lda #CHARACTER_COUNT
NameIndex:
  asl
  asl
  asl
  asl
  tay
  ldx VRAM_Buffer1_Offset
  lda #$23
  sta VRAM_Buffer1,x
  lda #$08
  sta VRAM_Buffer1+1,x
  lda #16
  sta VRAM_Buffer1+2,x
  sta R0
Copy:
  lda Names,y
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
.endproc

.proc QueueCursor
  pha
  ldy CrossoverMenuIndex
  lda CursorLow,y
  ldx VRAM_Buffer1_Offset
  sta VRAM_Buffer1+1,x
  lda CursorHigh,y
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
  .byte $22,$ca,8,"B - BACK"
  .byte 0
.endproc

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
  cpy #2
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
CursorHi:.byte $21,$22
CursorLo:.byte $63,$03
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
  .byte $0f,$00,$10,$30, $0f,$11,$21,$30
  .byte $0f,$28,$28,$28, $0f,$00,$10,$30 ; Bright gold option glyphs use palette2.
SelectNameTable:
  .incbin "chr/raw/character-select.bin"
.popseg
