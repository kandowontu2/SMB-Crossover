; Expanded MMC5 character state. The mapper already contains this RAM; the
; cartridge's 8KB PRG-RAM layout and every existing address stay unchanged.
; Mode2 allows ordinary CPU reads/writes during rendering and blanking.
; No nametable or hardware vertical split uses ExRAM in this game.
X5ProfilesRamStart=$5c00
KirbyProfileState=$5c00             ; 256B, owned by Kirby implementation.
VicProfileState=$5d00               ; 256B, owned by Vic Viper implementation.
Zelda2ProfileState=$5e00            ; 128B, owned by ZeldaII alternate.
DarkwingRecoveryState=$5e80        ; 32B reserved (six currently used).
X5UnallocatedProfileState=$5ea0     ; CV3 reserves64B5EA0..5EDF.
X5NewPersistentState=$5f00          ; seven16B third-row records.
X5MenuVariants=$5fe0                ; seven third-row menu alternatives.
X5ProfilesRamEnd=$6000
.export X5ProfilesRamStart,KirbyProfileState,VicProfileState,Zelda2ProfileState
.export X5NewPersistentState,X5MenuVariants,X5ProfilesRamEnd

.pushseg
.segment "X5_PROFILES"
.proc X5ProfilesNewGame
  lda #0
  tax
Clear:
  sta $5c00,x
  sta $5d00,x
  sta $5e00,x
  sta $5f00,x
  inx
  bne Clear
  rts
.endproc

.proc X5InventoryInit
  ; Selection precedes new-game initialization. Retain only menu variants;
  ; gameplay records and active overlays still reset in the ordinary way.
  ldx #15
SaveVariants:
  lda X5MenuVariants,x
  pha
  dex
  bpl SaveVariants
  farcall InventoryInit
  jsr CdNewGameProfiles
  ldx #0
RestoreVariants:
  pla
  sta X5MenuVariants,x
  inx
  cpx #16
  bcc RestoreVariants
  rts
.endproc
.popseg
