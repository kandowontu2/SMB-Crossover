; Private integration boundary. Existing IDs execute the original routines.
.pushseg
.segment "KIRBY_CORE"
.proc KbMovementDispatch
 lda SelectedCharacter
 cmp #CHARACTER_KIRBY
 jeq Kirby
 farcall ExpandedMovement,jmp
Kirby:jmp KbMovement
.endproc
.proc KbGraphicsDispatch
 lda SelectedCharacter
 cmp #CHARACTER_KIRBY
 jeq Kirby
 farcall ExpandedGraphics,jmp
Kirby:jmp KbGraphics
.endproc
.proc KbPortraitDispatch
 lda SelectedCharacter
 cmp #CHARACTER_KIRBY
 jeq Kirby
 farcall DwExpandedPortrait,jmp
Kirby:
 jsr KbAreaReset
 jmp KbPortrait
.endproc
.proc KbDeathDispatch
 lda SelectedCharacter
 cmp #CHARACTER_KIRBY
 jeq Kirby
 farcall ExpandedDeathUpdate,jmp
Kirby:jmp KbDeathUpdate
.endproc
.proc KbGraphicsBankDispatch
 lda SelectedCharacter
 cmp #CHARACTER_KIRBY
 jne Legacy
 BankPRGC #.bank(KbArtStart)
 rts
Legacy:
 lda SelectedCharacter
 sec
 sbc #CHARACTER_PIT
 tax
 lda Banks,x
 ora #MMC5_PRG_ROM
 BankPRGC a
 rts
Banks:.byte .bank(XgPIT0_STANDRight),.bank(XgRYGAR0_STANDRight),.bank(XgLUIGI0_STANDRight),.bank(XgBASS0_STANDRight),.bank(XgRYU0_STANDRight),.bank(XgSOPHIA0_STANDRight),.bank(XgSCROOGE_STANDRight)
.endproc
.proc KbInjuryStatusDispatch
 lda SelectedCharacter
 cmp #CHARACTER_KIRBY
 jeq Kirby
 farcall Z2InjuryStatusGate,jmp
Kirby:jmp KbInjuryStatus
.endproc
.proc KbInjuryStartDispatch
 lda SelectedCharacter
 cmp #CHARACTER_KIRBY
 jeq Kirby
 farcall Z2InjuryStartGate,jmp
Kirby:jmp KbInjuryStart
.endproc
.proc KbPickupDispatch
 lda SelectedCharacter
 cmp #CHARACTER_KIRBY
 jne Legacy
 lda PowerUpType,x
 jsr KbHealPickup
 jcc Legacy
 phx
 jsr EraseEnemyObject
 plx
 lda #6
 jsr SetupFloateyNumber
 rts
Legacy:
 farcall MarioSourcePowerupCollision,jmp
.endproc
.proc KbResetDispatch
 farcall SpecialRosterClear
 jmp KbAreaReset
.endproc
.proc KbHeadDispatch
 lda SelectedCharacter
 cmp #CHARACTER_KIRBY
 jeq Kirby
 jmp BlockBufferColli_Head
Kirby:
 sty KbTemp2
 lda Player_X_Position
 sta KbTempX
 lda Player_PageLoc
 sta KbTempPage
 jsr BlockBufferColli_Head
 jne Sampled
 lda Player_Y_Speed
 jpl Empty
 ; Side collision resolves after the head probes. At a pipe, this update's
 ; horizontal step can temporarily enter its wall by one pixel. Test the
 ; wider head edges at the pre-step X, so that wall cannot become a ceiling.
 lda KbTempX
 cmp MmOldX
 lda KbTempPage
 ldy Player_X_Scroll
 bmi OldPageLeft
 sbc #0
 jmp OldPageReady
OldPageLeft:
 adc #0
OldPageReady:
 sta KbTemp
 sec
 lda MmOldX
 sbc #7
 sta Player_X_Position
 lda KbTemp
 sbc #0
 sta Player_PageLoc
 ldy KbTemp2
 jsr BlockBufferColli_Head
 jne Sampled
 clc
 lda MmOldX
 adc #6
 sta Player_X_Position
 lda KbTemp
 adc #0
 sta Player_PageLoc
 ldy KbTemp2
 jsr BlockBufferColli_Head
 jmp Sampled
Empty:
 lda #0
Sampled:
 pha
 lda KbTempX
 sta Player_X_Position
 lda KbTempPage
 sta Player_PageLoc
 pla
 pha
 jeq Done
 cmp #$c2
 jeq Done
 cmp #$c3
 jeq Done
 phy
 ldy Player_Y_Speed
 jpl Restore
 ldy R3
 lda MTileAttribute,y
 and #MTILE_SOLID|MTILE_CLIMB
 cmp #MTILE_SOLID
 jne Restore
 ; The compact native15px profile begins at origin+17. Separate the actual
 ; sampled cell before its side probes; retain R2/R6/R7 for block effects.
 lda R2
 clc
 adc #48
 sec
 sbc #17
 sta Player_Y_Position
 and #15
 sta R4
 lda #0
 sta MmYFraction
 sta MmYFraction+1
Restore:
 ply
Done:
 pla
 rts
.endproc
.proc KbFreshGameInit
 farcall DwInventoryInit
 jmp KbGlobalInit::ClearEntry
.endproc
.segment "KIRBY_ABILITIES"
.proc KbWeaponsDispatch
 lda SelectedCharacter
 cmp #CHARACTER_KIRBY
 jeq Kirby
 farcall ExpandedWeapons,jmp
Kirby:jmp KbWeapons
.endproc
.proc KbBodyDispatch
 lda SelectedCharacter
 cmp #CHARACTER_KIRBY
 jeq Kirby
 farcall GuestBodyContact,jmp
Kirby:
 phx
 phy
 lda AreaType
 sta GuestBodyStompAllowed ; Refresh land/water eligibility for this cold family.
 lda CrossoverBehaviorVersion
 sta GuestBodyNoStomp
 jsr KbBodyContact
 jcc Ordinary
 ply
 plx
 sec
 rts
Ordinary:
 ply
 plx
 clc
 rts
.endproc
.popseg




