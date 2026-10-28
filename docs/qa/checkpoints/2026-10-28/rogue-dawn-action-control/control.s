RdHostCommitPosition=$9000
RdHostDoor=$9003
RdHostDoorDirection=$9006
RdHostDrawPlayer=$9009
RdHostElevator=$900c
RdHostEnvironment=$900f
RdHostFindSupport=$9012
RdHostHealthSound=$9015
RdHostLowHealthSound=$9018
RdHostMoveDown=$901b
RdHostMoveLeft=$901e
RdHostMoveRight=$9021
RdHostMoveUp=$9024
RdHostOffsetPosition=$9027
RdHostProbeDown=$902a
RdHostProbeLeft=$902d
RdHostProbeRight=$9030
RdHostProbeUp=$9033
RdHostRelativeX=$9036
RdHostRelativeY=$9039
RdHostSpawnProjectile=$903c
RdHostStagePosition=$903f
SmPosePtr=$6b06
SmChrBank=$6b08
SmTemp=$6b0b
CurrentBankC=$7da1
CurrentCHRBank=$0147
X5ChrMode=$73e0
ReloadCHRBank=$0146
X5WideChrActive=$73ee
ObjectMetasprite=$06e1
R0=$0003
R1=$0004
R3=$0006
R4=$0007
R5=$0008
R6=$0009
R7=$000a
MetaspriteRenderLoop=$a5ba
CurrentOAMOffset=$06de
GuestOamRotationActive=$6c0b
RgOamRotation=$6c08
METASPRITE_SAMUS_BODY=$e9
RD_FIRST_CHR=680
ENABLE_CROSSOVER=1
MMC5_PRG_ROM=$80
MMC5_PRG_BANK_C=$5116
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
.include "rogue_dawn_art.inc"
.include "rogue_dawn.s"
.include "rogue_dawn_weapons.s"
.include "rogue_dawn_render.s"
.include "rogue_dawn_control.s"
