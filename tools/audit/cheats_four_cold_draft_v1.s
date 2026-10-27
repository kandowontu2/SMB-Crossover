; Expanded MMC5 only. Decimal63/$3F cold page, not decimal99/$63 UI.
; Persistent flags reuse CheatInvincible: bit0 injury,1 air jump,2 wrap,
; 3 countdown hold,4 full power. No new WRAM/ExRAM allocation.
.pushseg
.segment "CHEATS_FOUR"
CheatAir=$02
CheatWrap=$04
CheatTimer=$08
CheatPower=$10
.proc CheatsSixInput
 lda CrossoverMenuPressed
 and #B_Button
 beq Navigate
 lda #2
 sta CrossoverOptionsFocus
 lda #3
 sta CrossoverMenuState
 lda #1
 sta DisableScreenFlag
 rts
Navigate:
 lda CrossoverMenuPressed
 and #Up_Dir|Down_Dir
 beq Change
 and #Up_Dir
 beq Down
 dec CrossoverOptionsFocus
 bpl Changed
 lda #5
 bne Focus
Down:inc CrossoverOptionsFocus
 lda CrossoverOptionsFocus
 cmp #6
 bcc Changed
 lda #0
Focus:sta CrossoverOptionsFocus
 jmp Changed
Change:
 lda CrossoverMenuPressed
 and #A_Button|Start_Button|Select_Button|Left_Dir|Right_Dir
 beq Done
 ldx CrossoverOptionsFocus
 cpx #1
 beq Level
 lda CheatInvincible
 eor Bits,x
 sta CheatInvincible
 jmp Changed
Level:
 lda CrossoverMenuPressed
 and #Left_Dir
 beq Forward
 dec CheatStartLevel
 jmp Wrap
Forward:inc CheatStartLevel
Wrap:lda CheatStartLevel
 and #31
 ora #$20
 sta CheatStartLevel
Changed:
 lda #Sfx_CoinGrab
 sta Square2SoundQueue
 jsr CheatsSixQueue
Done:rts
Bits:.byte $01,$00,$02,$04,$08,$10
.endproc
.proc CheatsSixQueue
 ; Six3-cell values36B +4B vertical RLE cursor erase +4B cursor =44B.
 ldy #0
Row:
 tya
 pha
 ldx VRAM_Buffer1_Offset
 lda AddrHi,y
 sta VRAM_Buffer1,x
 lda AddrLo,y
 clc
 adc #17
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 cpy #1
 beq Level
 lda CheatInvincible
 and CheatsSixInput::Bits,y
 beq Off
 lda #$24
 sta VRAM_Buffer1+5,x
 lda #'O'
 sta VRAM_Buffer1+3,x
 lda #'N'
 bne Middle
Off:lda #'F'
 sta VRAM_Buffer1+5,x
 sta VRAM_Buffer1+4,x
 lda #'O'
 sta VRAM_Buffer1+3,x
 jmp Next
Level:
 lda CheatStartLevel
 and #31
 lsr
 lsr
 clc
 adc #1
 sta VRAM_Buffer1+3,x
 lda CheatStartLevel
 and #3
 clc
 adc #1
 sta VRAM_Buffer1+5,x
 lda #'-'
Middle:sta VRAM_Buffer1+4,x
Next:txa
 clc
 adc #6
 sta VRAM_Buffer1_Offset
 pla
 tay
 iny
 cpy #6
 bcc Row
 ldx VRAM_Buffer1_Offset
 lda #$21
 sta VRAM_Buffer1,x
 lda #$23
 sta VRAM_Buffer1+1,x
 lda #$cb
 sta VRAM_Buffer1+2,x
 lda #$24
 sta VRAM_Buffer1+3,x
 lda #0
 sta VRAM_Buffer1+4,x
 inx
 inx
 inx
 inx
 ldy CrossoverOptionsFocus
 lda AddrHi,y
 sta VRAM_Buffer1,x
 lda AddrLo,y
 sec
 sbc #2
 sta VRAM_Buffer1+1,x
 lda #1
 sta VRAM_Buffer1+2,x
 lda #$3f
 sta VRAM_Buffer1+3,x
 lda #0
 sta VRAM_Buffer1+4,x
 txa
 clc
 adc #4
 sta VRAM_Buffer1_Offset
 rts
AddrHi:.byte $21,$21,$21,$21,$22,$22
AddrLo:.byte $25,$65,$a5,$e5,$25,$65
.endproc
.proc CheatsSixPage
 php
 sei ; serialize direct PPU address/data pairs against visible-split IRQ
 ; BuildOptions owns forced blank. Clearrows8..26, including parent
 ; AUDIO TEST row22/footer; paint this page's own B-back atrow23.
 bit PPUSTATUS
 lda #$20
 sta PPUADDR
 lda #$cb
 sta PPUADDR
 ldx #0
Header:lda Title,x
 sta PPUDATA
 inx
 cpx #7
 bne Header
 lda #$21
 sta PPUADDR
 lda #0
 sta PPUADDR
 lda #$24
 ldx #0
 ldy #2
BlankPage:sta PPUDATA
 inx
 bne BlankPage
 dey
 bne BlankPage
 ldx #96
BlankTail:sta PPUDATA
 dex
 bne BlankTail
 ldy #0
 ldx #0
Row:lda CheatsSixQueue::AddrHi,y
 sta PPUADDR
 lda CheatsSixQueue::AddrLo,y
 sta PPUADDR
 lda #22
 sta R0
Copy:lda Text,x
 sta PPUDATA
 inx
 dec R0
 bne Copy
 iny
 cpy #6
 bcc Row
 lda #$22
 sta PPUADDR
 lda #$ea
 sta PPUADDR
 ldx #0
BackCopy:lda Back,x
 sta PPUDATA
 inx
 cpx #8
 bcc BackCopy
 plp
 rts
Back:.byte "B - BACK"
Title:.byte "CHEATS "
Text:
 .byte "INVINCIBLE            "
 .byte "START LEVEL           "
 .byte "MID-AIR JUMPS         "
 .byte "SCREEN WRAP           "
 .byte "FREEZE TIMER          "
 .byte "FULL POWER            "
 .assert *-Text=132,error,"six22-cell cheat labels"
.endproc

.proc CheatsGameRoutinesGate
 ; Only the cheat-enabled or source-injury path enters. All-off retains the
 ; original farcall path, with one ORA admission instruction added resident.
 php
 pha
 phx
 phy
 ldx #7
Save:lda R0,x
 pha
 dex
 bpl Save
 jsr CheatsActive
 bcc Restore
 lda CheatInvincible
 and #CheatTimer
 beq :+
 lda #2
 sta GameTimerCtrlTimer
:
 lda GuestPowerupActive
 ora GuestHurtKind
 ora GuestHurtTicks
 bne Restore
 lda CheatInvincible
 and #CheatWrap
 beq :+
 jsr CheatsWrapPlayer
:
 lda CheatInvincible
 and #CheatAir
 beq :+
 jsr CheatsAirJump
:
 lda CheatInvincible
 and #CheatPower
 beq Restore
 jsr CheatsFullPower
Restore:
 ldx #0
Pop:pla
 sta R0,x
 inx
 cpx #8
 bcc Pop
 ply
 plx
 pla
 plp
 lda GuestHurtKind
 beq Native
 farcall GuestInjuryGameRoutines,jmp
Native:farcall GameRoutines,jmp
.endproc
.proc CheatsActive
 lda OperMode
 cmp #MODE_GAMEPLAY
 bne No
 lda OperMode_Task
 cmp #3
 bne No
 lda GameEngineSubroutine
 cmp #8
 bne No
 lda GamePauseStatus
 and #1

 bne No
 sec
 rts
No:clc
 rts
.endproc
.proc CheatsAirJump
 lda JumpspringAnimCtrl
 bne Done
 lda SelectedCharacter
 cmp #18
 beq Done
 lda SwimmingFlag
 bne Done
 lda Player_State
 beq Done
 cmp #3
 bcs Done
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 beq Turtle
 lda SavedJoypadBits
 and #A_Button
 beq Done
 lda PreviousA_B_Buttons
 and #A_Button
 bne Done
Rearm:
 ; Ground admission only; real hero wrappers compute jump impulse, native
 ; fractional motion, animation and jump SFX. Do not synthesize a velocity.
 lda #0
 sta Player_State
 lda SelectedCharacter
 cmp #CHARACTER_SIMON
 bne Done
 lda Cv3Variant
 beq Done
 lda #0
 sta Cv3JumpActive
 sta Cv3JumpPhase
Done:rts
Turtle:
 ; The real two-update TMNT producer queues a fresh A on the skipped tick.
 ; Re-arm only at its consuming tick, otherwise BG collision erases the
 ; fabricated grounded admission before the genuine initializer executes.
 lda TnClock
 and #1
 beq Done
 lda PreviousA_B_Buttons
 eor #$ff
 and SavedJoypadBits
 ora TnPendingFresh
 and #A_Button
 beq Done
 jmp Rearm
.endproc

.proc CheatsWrapPlayer
 lda JumpspringAnimCtrl
 jne Done
 lda Player_State
 cmp #3
 jcs Done
 lda SelectedCharacter
 cmp #18
 beq Ship
 ; Largest retained dry step is TMNT native cap9 pixels. Check
 ; before native motion:232 catches a falling body before guest pit241.
 lda Player_Y_HighPos
 cmp #1
 bcc Top
 bne Bottom
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 bne CommonTop
 lda Player_State
 beq CommonTop
 lda Player_Y_Position
 cmp #41
 bcc Top
CommonTop:lda Player_Y_Position
 cmp #32
 bcc Top
 cmp #232
 jcc Done
Bottom:lda #32
 ldx #16
 bne Search
Top:lda #192
 ldx #$f0
Search:sta R2
 stx R3
 lda #11
 sta R4
Candidate:
 jsr CheatsWrapClear
 bcs Move
 lda R2
 clc
 adc R3
 sta R2
 dec R4
 bne Candidate
 rts ; No free32x32 landing volume: retain native body, no hidden terrain edit.
Move:lda R2
 sta Player_Y_Position
 lda #1
 sta Player_Y_HighPos
 ; Canonical world position is the native input for every platform adapter;
 ; fractional velocity remains unchanged. Actual enemy/background runs next.
 rts
Ship:
 ; Native Gradius/Parodius clamp before crossing the screen. Admit held
 ; direction at their real clamp, update both real owner images before tick.
 lda SavedJoypadBits
 and #Down_Dir
 beq ShipUp
 lda VvObjY
 cmp #192
 bcc Done
 lda #8
 bne ShipMove
ShipUp:lda SavedJoypadBits
 and #Up_Dir
 beq Done
 lda VvObjY
 cmp #17
 bcs Done
 lda #168
ShipMove:clc
 adc #24
 sta R2
 lda #16
 ldx R2
 cpx #100
 bcc ShipSearch
 lda #$f0
ShipSearch:sta R3
 lda #11
 sta R4
ShipCandidate:jsr CheatsWrapClear
 bcs ShipClear
 lda R2
 clc
 adc R3
 sta R2
 dec R4
 bne ShipCandidate
 rts
ShipClear:lda R2
 sec
 sbc #24
 sta VvObjY
 sta PnY
 lda #0
 sta VvObjYF
 sta PnYF
 lda VvObjY
 clc
 adc #24
 sta Player_Y_Position
 lda #1
 sta Player_Y_HighPos
Done:rts
.endproc
.proc CheatsWrapClear
 ; Six actual tile queries cover a conservative32x32 volume at sameworldX.
 ; The real buffer pointer and current native MTileAttribute own solidity.
 lda #0
 sta R5
Column:
 ldx R5
 lda Player_X_Position
 clc
 adc Deltas,x
 sta R0
 lda Player_PageLoc
 adc #0
 and #1
 asl
 asl
 asl
 asl
 sta R1
 lda R0
 lsr
 lsr
 lsr
 lsr
 ora R1
 jsr GetBlockBufferAddr
 lda R2
 sec
 sbc #32
 sta R0
 tay
 lda (R6),y
 tay
 lda MTileAttribute,y
 and #MTILE_SOLID
 bne Blocked
 lda R0
 clc
 adc #16
 tay
 lda (R6),y
 tay
 lda MTileAttribute,y
 and #MTILE_SOLID
 bne Blocked
 inc R5
 lda R5
 cmp #3
 bcc Column
 sec
 rts
Blocked:clc
 rts
Deltas:.byte 0,16,31
.endproc

.proc CheatsFullPower
 ; Native private owners first; never index12-entry legacy arrays by13..19.
 ldx SelectedCharacter
 cpx #CHARACTER_LINK
 bne Cv3
 lda Z2Variant
 jeq Legacy
 farcall Z2EnsureInit
 lda #$ff
 sta Z2LevelsLo
 sta Z2LearnedSpells
 lda #$81
 sta Z2LevelsHi
 lda #$77
 sta Z2Containers
 lda #3
 sta Z2Tech
 lda #255
 sta Z2Hp
 sta Z2Mp
 rts
Cv3:cpx #CHARACTER_SIMON
 bne Roll
 lda Cv3Variant
 jeq Legacy
 tay
 dey
 lda #64
 sta Cv3Health,y
 lda #99
 sta Cv3Hearts,y
 lda #2
 sta Cv3Power,y
 lda Cv3Variant
 cmp #3
 bcs Cv3Equipped
 lda Cv3Subweapon,y
 bne Cv3Equipped
 lda #1 ; legal first carried dagger/flame; preserve any current choice.
 sta Cv3Subweapon,y
Cv3Equipped:lda #1
 sta PlayerStatus
 rts
Roll:cpx #CHARACTER_BASS
 bne Duck
 lda RlVariant
 jeq Legacy
 lda RlHealth
 cmp #28
 bne RollFill
 lda RlEnergy
 cmp #28
 jeq Done
RollFill:lda #28
 sta RlHealth
 sta RlEnergy
 lda #1
 sta RlDirty
 rts
Duck:cpx #CHARACTER_SCROOGE
 bne Kirby
 lda DarkwingVariant
 jeq Tier
 lda DwAdaptor
 bne DuckStocked
 lda #$26 ; source first-upgrade Arrow; exactly one current adaptor.
 farcall DwGiveItem
DuckStocked:lda #4
 sta DwHealth
 lda #99
 sta DwGas
 rts
Kirby:cpx #CHARACTER_KIRBY
 bne Chip
 lda #6
 sta KbHealth
 rts
Chip:cpx #14
 bne Mac
 lda #3
 sta CdHealth
 rts
Mac:cpx #15
 bne Mike
 lda LmHealth
 cmp #96
 bne MacFill
 lda LmHearts
 cmp #20
 bne MacFill
 lda LmStars
 cmp #3
 jeq Done
MacFill:lda #96
 sta LmHealth
 lda #20
 sta LmHearts
 lda #3
 sta LmStars
 lda #1
 sta LmDirty
 rts
Mike:cpx #CHARACTER_MIKE
 bne M3
 lda #0
 sta R0
 lda JnMaxHearts
 cmp #22
 beq :+
 inc R0
:lda JnHealth
 cmp #44
 beq :+
 inc R0
:lda JnOwnedTier
 cmp #3
 beq :+
 inc R0
:lda #22
 sta JnMaxHearts
 lda #44
 sta JnHealth
 lda #3
 sta JnOwnedTier
 ldx #9
MikeAmmo:lda MikeAmmoMax,x
 cmp JnAmmo,x
 beq :+
 sta JnAmmo,x
 inc R0
:
 dex
 bpl MikeAmmo
 lda R0
 beq :+
 lda #1
 sta JnUiDirty
:rts
M3:cpx #17
 bne Viper
 lda M3Form
 cmp #2
 jcs Done
 farcall M3ClearSuitState
 lda #2
 sta M3Form
 lda #0
 sta M3PaletteValid
 rts
Viper:cpx #18
 jeq Ship
 cpx #CHARACTER_TMNT
 bne Legacy
 ldx #3
Turtles:lda #128
 sta TnHealth,x
 lda TnEquipment,x
 bne :+
 lda #4
 sta TnEquipment,x
:
 lda #99
 sta TnAmmo,x
 dex
 bpl Turtles
 rts
Legacy:
 ldx SelectedCharacter
 beq Mario
 cpx #CHARACTER_LUIGI
 beq Tier
 cpx #CHARACTER_PIT
 beq Tier
 cpx #CHARACTER_RYGAR
 beq Tier
 lda CrossoverBehaviorVersion
 bne Modern
 cpx #CHARACTER_SIMON+1
 bcc Tier
Modern:jsr CheatsInventoryMax
 lda PlayerStatus
 bne Done
 farcall GuestBeginPowerup
 rts
Mario:lda PlayerStatus
 cmp #2
 bcs Done
 sta GuestPowerupOld
 sta GuestPowerupDisplay
 lda #2
 sta GuestPowerupTarget
 lda #0
 sta GuestLegacyHurt
 farcall MarioSourceBeginFreeze,jmp
Tier:lda PlayerStatus
 cmp #2
 bcs Done
 farcall GuestBeginPowerup
Done:rts
Ship:jmp CheatsShipPower
MikeAmmoMax:.byte 10,10,10,5,5,10,3,10,99,20
.endproc
.proc CheatsInventoryMax
 ldx SelectedCharacter
 lda RequiredLo,x
 sta R0
 lda RequiredHi,x
 sta R1
 lda Exclusive,x
 and InvOwnedLo,x
 bne HaveGun
 lda DefaultGun,x
HaveGun:ora R0
 sta R0
 lda #0
 sta R2
 ; API owns exclusivity, equip and RemainingGrant side effects. Only call
 ; for actual missing requireditems; retain every alreadylegalexclusivegun.
Grant:
 ldy R2
 lda R0
 and BitsLo,y
 bne Need
 lda R1
 and BitsHi,y
 beq Next
Need:
 ldx SelectedCharacter
 lda InvOwnedLo,x
 and BitsLo,y
 bne Next
 lda InvOwnedHi,x
 and BitsHi,y
 bne Next
 tya
 farcall InventoryGrant
Next:inc R2
 ldx SelectedCharacter
 lda Counts,x
 cmp R2
 bcs Grant
 ; Refill only this12-owner record. Actual maxima are copied byte-exact
 ; from source-generated InvMaxAmmo, including shared Simon/Ryu heartslots.
 txa
 asl
 asl
 asl
 asl
 tax
 lda #16
 sta R2
Ammo:cpx #160
 bne NativeMaximum
 lda #99 ; source SCROLL owns Ryu shared pool; never refill50 then99.
 bne HaveMaximum
NativeMaximum:lda AmmoMax,x
HaveMaximum:beq Skip
 cmp InvAmmo,x
 beq Skip
 sta InvAmmo,x
 inc InvDirty
Skip:inx
 dec R2
 bne Ammo
 rts
RequiredLo:.byte 0,$ff,$e7,$43,$7f,$83,0,0,0,$ff,$c1,$ff
RequiredHi:.byte 0,$07,0,0,0,$03,0,0,0,$01,0,0
Exclusive:.byte 0,0,$18,$3c,0,$7c,0,0,0,0,$3e,0
DefaultGun:.byte 0,0,$10,$10,0,$04,0,0,0,0,$02,0
Counts:.byte 0,10,7,6,6,9,0,0,0,8,7,7
BitsLo:.byte 1,2,4,8,16,32,64,128,0,0,0
BitsHi:.byte 0,0,0,0,0,0,0,0,1,2,4
AmmoMax:
  .byte 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
  .byte 0,112,112,112,112,112,112,112,112,0,0,0,0,0,0,0
  .byte 0,0,20,0,0,0,0,0,0,0,0,0,0,0,0,0
  .byte 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
  .byte 0,20,20,0,0,0,0,0,0,0,0,0,0,0,0,0
  .byte 99,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
  .byte 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
  .byte 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
  .byte 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
  .byte 0,112,112,112,112,112,112,112,0,0,0,0,0,0,0,0
  .byte 50,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
  .byte 0,60,20,8,0,0,0,0,0,0,0,0,0,0,0,0
.endproc
.proc CheatsShipPower
 ; Let the real owners initialize first; fullpower must not be overwritten
 ; by the first native movement tick. At most20 genuine purchases fit all
 ; native caps, with no unbounded retry if a source purchase refuses.
 farcall VvEnsure
 lda VvVariant
 beq Ready
 farcall PnEnsure
Ready:jsr Full
 bcs Done
 lda #20
Buy:pha
 jsr CheatsShipMax
 pla
 tax
 dex
 txa
 bne Buy
Done:rts
Full:lda VvVariant
 bne Pn
 lda VvSpeed
 cmp #14
 bcc No
 lda VvMissile
 beq No
 lda VvGun
 beq No
 lda VvOptions
 cmp #2
 bcc No
 lda VvShield
 cmp #5
 rts
Pn:lda VvSpeed
 cmp #4
 bcc No
 lda VvGun
 and #8
 beq No
 lda VvGun
 and #$c0
 beq No
 lda VvGun
 and #7
 ldx VvVariant
 cpx #2
 bcc Four
 cmp #3
 rts
Four:cmp #4
 rts
No:clc
 rts
.endproc
.proc CheatsShipMax
 lda VvVariant
 jne Parodius
 lda VvSpeed
 cmp #14 ; native motion cap: (speed+2)/2, capped at8pixels.
 bcs Missile
 lda #1
 jsr Buy
 rts
Missile:lda VvMissile
 bne Gun
 lda #2
 jsr Buy
 rts
Gun:lda VvGun
 bne Options
 lda #4 ; native laser default; preserve a currentlyselectedDOUBLE.
 jsr Buy
 rts
Options:lda VvOptions
 cmp #2
 bcs Shield
 lda #5
 jsr Buy
 rts
Shield:lda VvShield
 cmp #5
 bcs Done
 ; The real purchase refuses a nonzero shield. A partlyused shield remains
 ; sourcelegal and is refilled to its sourcemaximum by the cheat directly.
 lda VvShield
 beq NewShield
 lda #5
 sta VvShield
 lda #1
 sta VvHudDirty
 rts
NewShield:lda #6
 jsr Buy
Done:rts
Buy:
 pha
 lda VvHeld
 pha
 lda VvMeter
 pha
 tsx
 lda $0103,x
 sta VvMeter
 lda VvHeld
 ora #B_Button
 sta VvHeld
 farcall VvBuyUpgrade
 pla
 sta VvMeter
 pla
 sta VvHeld
 pla
 rts
Parodius:
 ; Original bar bits1speed/2missile/4double/8laser/16options. Bit32 is
 ; RESET, never a grant. Bellpowers are temporary choices, not stacked.
 lda VvSpeed
 cmp #4
 bcs PnMissile
 lda #1
 jsr PnBuy
 rts
PnMissile:lda VvGun
 and #8
 bne PnBeam
 lda #2
 jsr PnBuy
 rts
PnBeam:lda VvGun
 and #$c0
 bne PnOptions
 lda #8
 jsr PnBuy
 rts
PnOptions:lda VvGun
 and #7
 ldx VvVariant
 cpx #2
 bcc Four
 cmp #3
 bcs Done
 lda #16
 jsr PnBuy
 rts
Four:cmp #4
 bcs Done
 lda #16
 jsr PnBuy
 rts
PnBuy:
 pha
 lda VvMeter
 pha
 lda VvFresh
 pha
 lda PnAutoMode
 pha
 lda CurrentBankC
 pha
 BankPRGC #.bank(PnAnimationTable)
 lda #0
 sta PnAutoMode
 lda #$80
 sta VvFresh
 tsx
 lda $0105,x
 sta VvMeter
 farcall PnNativeGear
 pla
 BankPRGC a
 pla
 sta PnAutoMode
 pla
 sta VvFresh
 pla
 sta VvMeter
 pla
 lda #1
 sta VvHudDirty
 rts
.endproc
.assert * <= $b800,error,"Cheats cold module exceeds declared6KiB extent"
.popseg
