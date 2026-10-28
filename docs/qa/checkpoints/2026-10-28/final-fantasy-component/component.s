SelectedCharacter=$6002
NumberofLives=$075f
AreaType=$0753
AreaAddrsLOffset=$0754
WorldNumber=$0764
SavedJoypadBits=$00dc
Player_State=$001e
PlayerStatus=$075b
PlayerSize=$0759
CrouchingFlag=$0717
RgCrouch=$6c0f
MmSliding=$68b0
SmBall=$6b00
MmOnVine=$6014
MmUnderwater=$68c1
MmFrictionYActive=$68c0
MmOldX=$68b5
MmVX=$68a5
MmVY=$68a8
MmXFraction=$68ab
MmYFraction=$68ad
InjuryTimer=$079b
Player_X_Position=$0075
Player_PageLoc=$005c
Player_Y_Position=$00bd
Player_Y_HighPos=$00a4
Player_Y_Speed=$008e
PlayerFacingDir=$053e
SwimmingFlag=$0706
Player_X_Scroll=$0701
Player_X_Speed=$0046
Player_XSpeedAbsolute=$0702
Square1SoundQueue=$0105
Square2SoundQueue=$0104
MmDeathFlag=$6007
MmDeathAge=$6009
TimerControl=$074a
GamePauseStatus=$0777
GameEngineSubroutine=$000f
CrossoverBehaviorVersion=$7fe1
KillPlayer=$97d6
BlockBufferColli_Head=$9587
BlockBufferColli_Side=$958b
Player_Rel_XPos=$0571
Player_Pos_ForScroll=$075a
SmPosePtr=$6b06
SmChrBank=$6b08
ObjectMetasprite=$06e1
Player_SprAttrib=$0587
PlayerOutlinesOff=$7eb8
R0=$0003
R1=$0004
R2=$0005
R3=$0006
R4=$0007
R5=$0008
R6=$0009
R7=$000a
CurrentBankC=$7da1
X5SetPhysicalChr=$a275
CurrentCHRBank=$0147
X5ChrMode=$73e0
ReloadCHRBank=$0146
X5WideChrActive=$73ee
MetaspriteRenderLoop=$a5ba
CurrentOAMOffset=$06de
GuestOamRotationActive=$6c0b
RgOamRotation=$6c08
ScreenLeft_X_Pos=$071f
ScreenLeft_PageLoc=$071d
CurrentBank=$0145
IrqScrollSplit=$8000
IrqNewScroll=$0137
IrqPPUCTRL=$0138
NextBank_SMC=$0161
SafecallA_SMC=$0169
SafereturnA_SMC=$0178
FarcallJmpTarget_SMC=$016b
A_Button=$80
B_Button=$40
Up_Dir=$8
Down_Dir=$4
Sfx_BigJump=$1
Sfx_Fireball=$20
Sfx_PowerUpGrab=$20
Sfx_PipeDown_Injury=$10
METASPRITE_SAMUS_BODY=$e9
.macpack longbranch
ENABLE_CROSSOVER=1
MMC5_PRG_ROM=$80
MMC5_PRG_BANK_C=$5116
FF_FIRST_CHR=756
.macro BankPRGC bank
.if ::ENABLE_CROSSOVER
  .if .match(bank, a)
    sta CurrentBankC
  .elseif .match(bank, x)
    stx CurrentBankC
  .elseif .match(bank, y)
    sty CurrentBankC
  .else
    .if (.match (.left (1, {bank}), #))
      lda #.right (.tcount ({bank})-1, {bank}) | MMC5_PRG_ROM
    .else
      lda bank
    .endif
    sta CurrentBankC
  .endif
.endif
  _BANK_INNER bank, MMC5_PRG_BANK_C
.endmacro
.macro _BANK_INNER bank, ADDRESS
.scope
  .if .match(bank, a)
    sta ADDRESS
  .elseif .match(bank, x)
    stx ADDRESS
  .elseif .match(bank, y)
    sty ADDRESS
  .else
    .if (.match (.left (1, {bank}), #))
      lda #.right (.tcount ({bank})-1, {bank}) | MMC5_PRG_ROM ; todo handle ram banking
    .else
      lda bank
    .endif
    sta ADDRESS
  .endif
.endscope
.endmacro
.include "final_fantasy.s"
