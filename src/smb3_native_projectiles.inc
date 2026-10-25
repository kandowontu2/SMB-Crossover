; Authenticated original SMB3 fireball/hammer initialization and movement.
.pushseg
.segment "M3_NATIVE"
.scope M3ShotNative
PlayerProj_ID=M3ShotKind
PlayerProj_X=M3ShotX
PlayerProj_Y=M3ShotY
PlayerProj_YHi=M3ShotYHi
PlayerProj_XVel=M3ShotVX
PlayerProj_YVel=M3ShotVY
PlayerProj_XVelFrac=M3ShotFrac
PlayerProj_Cnt=M3ShotAge
Player_X=M3Native::Player_X
Player_Y=M3Native::Player_Y
Player_YHi=M3Native::Player_YHi
Player_XVel=M3Native::Player_XVel
Player_FlipBits=M3Native::Player_FlipBits
Player_Suit=M3Form
Player_FireCount=M3Native::Player_FireCount
Sound_QPlayer=M3Native::Sound_QPlayer
Temp_Var1=M3Native::Temp_Var1
Player_HaltGame=$5cb0
Level_AScrlConfig=$5cae
Level_ScrollDiffV=$5caf
Negate=M3Native::Negate
SND_PLAYERFIRE=32
PLAYERSUIT_HAMMER=6
PlayerProj_ThrowWeapon:
LDX #.lobyte($01)
PRG007_A2B1:
LDA PlayerProj_ID,X
jeq PRG007_A2BA
DEX
jpl PRG007_A2B1
RTS
PRG007_A2BA:
LDA Sound_QPlayer
ORA #.lobyte(SND_PLAYERFIRE)
STA Sound_QPlayer
LDA #.lobyte($0b)
STA Player_FireCount
LDA Player_X
 clc
ADC #.lobyte($04)
STA PlayerProj_X,X
LDA Player_Y
STA PlayerProj_Y,X
LDA Player_YHi
STA PlayerProj_YHi,X
LDA #.lobyte($01)
LDY Player_Suit
CPY #.lobyte(PLAYERSUIT_HAMMER)
SEC
jne PRG007_A2E3
ASL A
PRG007_A2E3:
STA PlayerProj_ID,X
LDA #.lobyte($03)
jcs PRG007_A2EC
LDA #.lobyte(-$03)
PRG007_A2EC:
STA PlayerProj_YVel,X
LDA #.lobyte($00)
STA Temp_Var1
LDA #.lobyte($03)
jcs PRG007_A304
LDA Player_FlipBits
ASL A
EOR Player_XVel
jpl PRG007_A302
LDA Player_XVel
STA Temp_Var1
PRG007_A302:
LDA #.lobyte($10)
PRG007_A304:
LDY Player_FlipBits
jne PRG007_A30B
JSR Negate
PRG007_A30B:
 clc
ADC Temp_Var1
STA PlayerProj_XVel,X
LDA #.lobyte($00)
STA PlayerProj_Cnt,X
RTS
PRG007_A361:
LDY Player_HaltGame
jne PRG007_A3DB
LDA PlayerProj_YVel,X
LDY Level_AScrlConfig
jeq PRG007_A371
 clc
ADC Level_ScrollDiffV
PRG007_A371:
PHA
LDY #.lobyte($00)
PLA
jpl PRG007_A378
DEY
PRG007_A378:
 clc
ADC PlayerProj_Y,X
STA PlayerProj_Y,X
TYA
ADC PlayerProj_YHi,X
STA PlayerProj_YHi,X
INC PlayerProj_Cnt,X
LDA PlayerProj_ID,X
CMP #.lobyte($02)
jne PRG007_A3C0
LDA PlayerProj_XVel,X
ASL A
ASL A
ASL A
ASL A
 clc
ADC PlayerProj_XVelFrac,X
STA PlayerProj_XVelFrac,X
PHP
LDA PlayerProj_XVel,X
LSR A
LSR A
LSR A
LSR A
CMP #.lobyte(%00001000)
jcc PRG007_A3AC
ORA #.lobyte(%11110000)
PRG007_A3AC:
PLP
ADC PlayerProj_X,X
STA PlayerProj_X,X
LDA PlayerProj_Cnt,X
AND #.lobyte($07)
jne PRG007_A3BD
INC PlayerProj_YVel,X
PRG007_A3BD:
JMP PRG007_A3DB
PRG007_A3C0:
LDA PlayerProj_X,X
 clc
ADC PlayerProj_XVel,X
STA PlayerProj_X,X
LDA PlayerProj_YVel,X
CMP #.lobyte($04)
jeq PRG007_A3DB
LDA PlayerProj_Cnt,X
AND #.lobyte($03)
jne PRG007_A3DB
INC PlayerProj_YVel,X
PRG007_A3DB:
RTS
.endscope
.popseg
