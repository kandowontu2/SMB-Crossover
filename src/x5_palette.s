; Expanded-only palette admission. Old data stays in place for old public PCs.
.pushseg
.segment "X5_PROFILES"
.proc X5GetPlayerColors
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  bne RlLegacyColors
  lda RlVariant
  beq RlLegacyColors
  farcall QueueMegaManFacePalette
  farcall QueueGuestWeaponPalette
  jsr X5QueueAreaBackdrop
  farcall RlForcePalette,jmp
RlLegacyColors:
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  bne :+
  lda ProtoVariant
  beq LegacyMegaMan
  jsr X5LegacyGetPlayerColors
  farcall ProtoFixQueuedPalette,jmp
LegacyMegaMan:
  jmp X5LegacyGetPlayerColors
:
  lda SelectedCharacter
  cmp #15
  bne :+
  farcall QueueMegaManFacePalette
  farcall QueueGuestWeaponPalette
  jsr X5QueueAreaBackdrop
  farcall LmForcePalette,jmp
:
  lda SelectedCharacter
  cmp #CHARACTER_MIKE
  bne :+
  farcall JnGetColors,jmp
:
  cmp #17
  bne :+
  farcall M3GetPlayerColors,jmp
:
  cmp #CHARACTER_SIMON
  bne :+
  lda Cv3Variant
  beq Cv3Ordinary
  cmp #4
  bcs Cv3Ordinary
  farcall QueueMegaManFacePalette
  farcall QueueGuestWeaponPalette
  jsr X5QueueAreaBackdrop
  farcall Cv3ForcePalette,jmp
Cv3Ordinary:
  jmp X5LegacyGetPlayerColors
:
  lda SelectedCharacter
  cmp #CHARACTER_SCROOGE
  bne :+
  lda DarkwingVariant
  beq Original
  farcall QueueMegaManFacePalette
  farcall QueueGuestWeaponPalette
  jsr X5QueueAreaBackdrop
  farcall DwQueuePalette,jmp
:
  cmp #CHARACTER_LINK
  bne :+
  lda Z2Variant
  cmp #1
  bne Original
  farcall QueueMegaManFacePalette
  farcall QueueGuestWeaponPalette
  jsr X5QueueAreaBackdrop
  farcall Z2QueueBodyPalette,jmp
Original:
  jmp X5LegacyGetPlayerColors
:
  lda SelectedCharacter
  cmp #18
  bne :+
  farcall VvGetPlayerColors,jmp
:
  cmp #CHARACTER_TMNT
  bne :+
  farcall QueueMegaManFacePalette
  farcall QueueGuestWeaponPalette
  farcall TnQueuePalette,jmp
: lda SelectedCharacter
  cmp #14
  bne :+
  farcall CdGetPlayerColors,jmp
:
  cmp #CHARACTER_KIRBY
  bne Legacy
  farcall QueueMegaManFacePalette
  farcall QueueGuestWeaponPalette
  jsr X5QueueAreaBackdrop
  farcall KbQueuePalette,jmp
Legacy:
  jmp X5LegacyGetPlayerColors
.endproc
.proc X5QueueAreaBackdrop
  ; $3f10 mirrors the universal backdrop. New player palettes still need the
  ; original area's backdrop on lives-screen/stage transitions.
  ldx VRAM_Buffer1_Offset
  cpx #$70
  bcs Done
  lda #$3f
  sta VRAM_Buffer1,x
  lda #$10
  sta VRAM_Buffer1+1,x
  lda #1
  sta VRAM_Buffer1+2,x
  ldy BackgroundColorCtrl
  bne :+
  ldy AreaType
: lda Colors,y
  sta VRAM_Buffer1+3,x
  txa
  clc
  adc #4
  tax
  stx VRAM_Buffer1_Offset
  lda #0
  sta VRAM_Buffer1,x
Done:rts
Colors:.byte $22,$22,$0f,$0f,$0f,$22,$0f,$0f
.endproc
.proc X5LegacyGetPlayerColors
.if ::ENABLE_CROSSOVER
  farcall QueueMegaManFacePalette
  farcall QueueGuestWeaponPalette
.endif
  ldx VRAM_Buffer1_Offset  ;get current buffer offset
  ldy #$00
  lda CurrentPlayer        ;check which player is on the screen
  beq ChkFiery
  ldy #$04                 ;load offset for luigi
ChkFiery:
  lda PlayerStatus         ;check player status
  cmp #$02
  bne StartClrGet          ;if fiery, load alternate offset for fiery player
  ldy #$08
StartClrGet:
.if ::ENABLE_CROSSOVER
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bcc :+
    bne RosterPaletteIndex
    lda BillVariant
    beq RosterPaletteIndex
    lda PlayerStatus
    asl
    asl
    clc
    adc #152
    tay
    jmp GuestPaletteReady
RosterPaletteIndex:
    lda SelectedCharacter
    sec
    sbc #CHARACTER_BILL
    sta R0
    asl
    clc
    adc R0
    asl
    asl
    sta R0
    farcall RemainingPower
    asl
    asl
    clc
    adc R0
    adc #32
    tay
    jmp GuestPaletteReady
  :
  cmp #CHARACTER_SAMUS
  bne :+
    farcall RemainingPower
    asl
    asl
    clc
    adc #20
    tay
    jmp GuestPaletteReady
  :
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  bne :+
    ldy #$0c
    lda PlayerStatus
    cmp #2
    bne :+
      ldy #$10
  :
GuestPaletteReady:
.endif
  lda #$03                 ;do four colors
  sta R0 
ClrGetLoop:
  lda PlayerColors,y       ;fetch player colors and store them
  sta VRAM_Buffer1+3,x     ;in the buffer
  iny
  inx
  dec R0 
  bpl ClrGetLoop
  ldx VRAM_Buffer1_Offset  ;load original offset from before
  ldy BackgroundColorCtrl  ;if this value is four or greater, it will be set
  bne SetBGColor           ;therefore use it as offset to background color
  ldy AreaType             ;otherwise use area type bits from area offset as offset
SetBGColor:
  lda BackgroundColors,y   ;to background color instead
  sta VRAM_Buffer1+3,x
  lda #$3f                 ;set for sprite palette address
  sta VRAM_Buffer1,x       ;save to buffer
  lda #$10
  sta VRAM_Buffer1+1,x
  lda #$04                 ;write length byte to buffer
  sta VRAM_Buffer1+2,x
  lda #$00                 ;now the null terminator
  sta VRAM_Buffer1+7,x
  txa                      ;move the buffer pointer ahead 7 bytes
  clc                      ;in case we want to write anything else later
  adc #$07
SetVRAMOffset:
  sta VRAM_Buffer1_Offset  ;store as new vram buffer offset
  rts

BGColorCtrl_Addr:
      .byte $00, $09, $0a, $04

BackgroundColors:
      .byte $22, $22, $0f, $0f ;used by area type if bg color ctrl not set
      .byte $0f, $22, $0f, $0f ;used by background color control if set

PlayerColors:
      .byte $22, $16, $27, $18 ;mario's colors
      .byte $22, $30, $27, $19 ;luigi's colors
      .byte $22, $37, $27, $16 ;fiery (used by both)
      .byte $22, $0f, $11, $2c ;Mega Man body
      .byte $22, $0f, $16, $28 ;Fire upgrade
      .byte $22, $16, $1a, $27 ;Samus, short beam
      .byte $22, $16, $1a, $36 ;Long beam
      .byte $22, $15, $2a, $34 ;Wave beam
      .byte $22, $12, $36, $0f, $22, $11, $36, $0f, $22, $16, $36, $0f
      .byte $22, $29, $17, $27, $22, $2c, $17, $27, $22, $16, $17, $27
      .byte $22, $07, $27, $37, $22, $06, $27, $37, $22, $0f, $16, $30
        .byte $22,$07,$26,$30, $22,$07,$27,$30, $22,$07,$36,$30 ; Pit
        .byte $22,$16,$30,$0f, $22,$26,$30,$0f, $22,$28,$30,$0f ; Rygar
        .byte $22,$1a,$27,$17, $22,$1a,$27,$17, $22,$30,$27,$16 ; Luigi
        .byte $22,$0f,$27,$00, $22,$0f,$27,$00, $22,$0f,$27,$00 ; Bass buster suit
        .byte $22,$22,$07,$36, $22,$22,$07,$36, $22,$22,$07,$36 ; Ryu default bitmap palette
        .byte $22,$15,$30,$0f, $22,$15,$30,$0f, $22,$15,$30,$0f ; Sophia default bitmap palette
        .byte $22,$0f,$30,$16, $22,$0f,$30,$16, $22,$0f,$30,$16 ; Scrooge
        .byte $22,$1c,$36,$0f, $22,$1c,$36,$0f, $22,$1c,$36,$0f ; Lance: hair, skin, outline; pants share world red.


;-------------------------------------------------------------------------------------

.endproc
.popseg
