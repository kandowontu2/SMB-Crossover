; Authenticated SMB3 PRG1 controller. Retargeted RAM; source instruction/order preserved.
; Southbird disassembly credit: https://sonicepoch.com/sm3mix/
.pushseg
.segment "M3_NATIVE"
.scope M3Native
Counter_1=$5c18
Counter_ByPlayerSpd=$5c4c
Counter_Wiggly=$5c3a
Debug_Flag=$5c21
FloatLevel_PlayerWaterStat=$5c4d
Level_JctCtl=$5c24
Level_Objects=$5c58
Level_PipeMove=$5c42
Level_PipeNotExit=$5c22
Level_SlopeEn=$5c3c
Level_Tile_GndL=$5c54
Level_Tile_Head=$5c53
Level_TilesetIdx=$5c3b
Map_ReturnStatus=$5c57
Pad_Holding=$5c19
Pad_Input=$5c1a
Player_AboveTop=$5c2f
Player_AllowAirJump=$5c25
Player_Behind=$5c50
Player_Behind_En=$5c4f
Player_EndLevel=$5c39
Player_FireCount=$5c2c
Player_FlashInv=$5c34
Player_Flip=$5c32
Player_FlipBits=$5c1f
Player_FlipBits_OLD=$5c3f
Player_FlyTime=$5c40
Player_Frame=$5c1e
Player_FrogHopCnt=$5c2c
Player_InAir=$5c1c
Player_InAir_OLD=$5c2b
Player_InWater=$5c45
Player_IsClimbing=$5c3e
Player_IsDucking=$5c41
Player_IsHolding=$5c55
Player_Kick=$5c37
Player_Kuribo=$5c47
Player_KuriboDir=$5c33
Player_LowClearance=$5c4e
Player_MoveLR=$5c43
Player_PMeterCnt=$5c2d
Player_PipeFace=$5c38
Player_Power=$5c23
Player_QueueSuit=$5c48
Player_RunFlag=$5c4b
Player_SandSink=$5c52
Player_Slide=$5c30
Player_SlideRate=$5c3d
Player_Slippery=$5c51
Player_SpriteY=$5c1b
Player_StarInv=$5c35
Player_Statue=$5c4a
Player_Suit=$5f40
Player_SuitLost=$5c36
Player_SwimCnt=$5c46
Player_TailAttack=$5c2e
Player_TailCount=$5c2a
Player_TwisterSpin=$5c5b
Player_UphillFlag=$5c31
Player_UphillSpeedIdx=$5c56
Player_VibeDisable=$5c5a
Player_WagCount=$5c20
Player_WalkAnimTicks=$5c44
Player_WalkFrame=$5c1d
Player_X=$5c00
Player_XHi=$5c02
Player_XVel=$5c04
Player_XVelAdj=$5c26
Player_XVelFrac=$5c06
Player_Y=$5c01
Player_YHi=$5c03
Player_YVel=$5c05
Player_YVelFrac=$5c07
Player_mGoomba=$5c49
Sound_QLevel1=$5c28
Sound_QLevel2=$5c29
Sound_QPlayer=$5c27
Temp_Var1=$5c08
Temp_Var10=$5c11
Temp_Var11=$5c12
Temp_Var12=$5c13
Temp_Var13=$5c14
Temp_Var14=$5c15
Temp_Var15=$5c16
Temp_Var16=$5c17
Temp_Var2=$5c09
Temp_Var3=$5c0a
Temp_Var4=$5c0b
Temp_Var5=$5c0c
Temp_Var6=$5c0d
Temp_Var7=$5c0e
Temp_Var8=$5c0f
Temp_Var9=$5c10
Tile_AttrTable=$5c5c
FALLRATE_MAX=64
OBJ_TOADANDKING=213
PAD_A=128
PAD_B=64
PAD_DOWN=4
PAD_LEFT=2
PAD_RIGHT=1
PAD_SELECT=32
PAD_UP=8
PF_CLIMB_BIG=44
PF_CLIMB_FROG=40
PF_CLIMB_SMALL=74
PF_DUCK_NOTRACCOON=15
PF_DUCK_RACCOON=7
PF_FALLBIG=6
PF_FASTJUMPBIG=56
PF_FASTJUMPFALLSMALL=78
PF_FROGHOP_BASE=21
PF_FROGSWIM_DOWNBASE=36
PF_FROGSWIM_IDLEBASE=31
PF_FROGSWIM_LRBASE=33
PF_FROGSWIM_UPBASE=18
PF_HOLDBIG_BASE=41
PF_HOLDSMALL_BASE=46
PF_INPIPE_BIG=5
PF_INPIPE_BIGKURIBO=24
PF_INPIPE_SMALL=50
PF_INPIPE_SMALLKURIBO=67
PF_JUMPBIG=79
PF_JUMPFALLSMALL=64
PF_JUMPRACCOON=80
PF_KICK_BIG=45
PF_KICK_SMALL=66
PF_KURIBO_BIG=24
PF_KURIBO_SMALL=67
PF_MIDGROW_HALFWAY=39
PF_MIDGROW_SMALL=11
PF_RUNBIG_BASE=57
PF_RUNSMALL_BASE=76
PF_SKID_BIG=48
PF_SKID_SMALL=65
PF_SLIDE_BIG=49
PF_SLIDE_SMALL=51
PF_SOMERSAULT_BASE=26
PF_SPINOTHER_BASE=2
PF_SPINSLIDESUITS_BASE=4
PF_SPINSMALLORFROG_BASE=50
PF_STATUE=30
PF_SWIMACTIVE_BIG=52
PF_SWIMIDLE_BIG=60
PF_SWIMIDLE_SMALL=70
PF_TAILATKGROUND_BASE=3
PF_TAILATKINAIR_BASE=9
PF_TAILWAGFALL=8
PF_TAILWAGFLY_BASE=54
PF_THROWINAIR_BASE=52
PF_THROWONGROUND_BASE=14
PF_WALKBIG_BASE=12
PF_WALKSMALL_BASE=62
PF_WALKSPECIAL_BASE=0
PLAYERSUIT_FROG=4
PLAYERSUIT_LAST=6
PLAYER_FLY_YVEL=-24
PLAYER_FROG_MAXYVEL=-32
PLAYER_JUMP=-56
PLAYER_MAXSPEED=64
PLAYER_SWIMSTART_YVEL=-32
PLAYER_SWIM_YVEL=32
PLAYER_TAILWAG_YVEL=16
PLAYER_TOPPOWERSPEED=56
PLAYER_TOPRUNSPEED=40
PLAYER_TOPWALKSPEED=24
SND_LEVELPOOF=128
SND_LEVELSKID=128
SND_LEVELTAILWAG=176
SND_PLAYERFROG=128
SND_PLAYERJUMP=1
SND_PLAYERPOWER=64
SND_PLAYERSWIM=4
SPR_HFLIP=64
TILE1_SKY=128
TILE1_VINE=133
TILE1_WFALLMID=225
TILE1_WFALLTOP=224
TILEA_DOOR2=67
TILEA_PSWITCH_PRESSED=215
Player_WalkFramesByPUp:
 .byte .lobyte(PF_WALKSMALL_BASE),.lobyte(PF_WALKSMALL_BASE+1),.lobyte(PF_WALKSMALL_BASE),.lobyte(PF_WALKSMALL_BASE+1)
 .byte .lobyte(PF_WALKBIG_BASE),.lobyte(PF_WALKBIG_BASE+1),.lobyte(PF_WALKBIG_BASE+2),.lobyte(PF_WALKBIG_BASE+1)
 .byte .lobyte(PF_WALKBIG_BASE),.lobyte(PF_WALKBIG_BASE+1),.lobyte(PF_WALKBIG_BASE+2),.lobyte(PF_WALKBIG_BASE+1)
 .byte .lobyte(PF_WALKSPECIAL_BASE),.lobyte(PF_WALKSPECIAL_BASE+1),.lobyte(PF_WALKSPECIAL_BASE+2),.lobyte(PF_WALKSPECIAL_BASE+1)
 .byte .lobyte(PF_WALKSPECIAL_BASE),.lobyte(PF_WALKSPECIAL_BASE+1),.lobyte(PF_WALKSPECIAL_BASE+2),.lobyte(PF_WALKSPECIAL_BASE+1)
 .byte .lobyte(PF_WALKSPECIAL_BASE),.lobyte(PF_WALKSPECIAL_BASE+1),.lobyte(PF_WALKSPECIAL_BASE+2),.lobyte(PF_WALKSPECIAL_BASE+1)
 .byte .lobyte(PF_WALKBIG_BASE),.lobyte(PF_WALKBIG_BASE+1),.lobyte(PF_WALKBIG_BASE+2),.lobyte(PF_WALKBIG_BASE+1)
Player_GrowFrames:
 .byte .lobyte(PF_WALKBIG_BASE+2),.lobyte(PF_MIDGROW_HALFWAY),.lobyte(PF_WALKBIG_BASE+2),.lobyte(PF_MIDGROW_HALFWAY),.lobyte(PF_WALKBIG_BASE+2)
 .byte .lobyte(PF_MIDGROW_HALFWAY),.lobyte(PF_MIDGROW_SMALL),.lobyte(PF_MIDGROW_HALFWAY),.lobyte(PF_MIDGROW_SMALL),.lobyte(PF_MIDGROW_HALFWAY)
 .byte .lobyte(PF_MIDGROW_SMALL),.lobyte(PF_MIDGROW_HALFWAY)
PipeMove_Frame:
 .byte .lobyte(PF_INPIPE_SMALL),.lobyte(PF_INPIPE_SMALLKURIBO),.lobyte(PF_INPIPE_BIG),.lobyte(PF_INPIPE_BIGKURIBO)
Player_SkidFrame:
 .byte .lobyte(PF_SKID_SMALL),.lobyte(PF_SKID_BIG)
Player_SwimActiveFrames:
 .byte .lobyte(PF_SWIMACTIVE_BIG),.lobyte(PF_SWIMACTIVE_BIG+1),.lobyte(PF_SWIMACTIVE_BIG+2),.lobyte(PF_SWIMACTIVE_BIG),.lobyte(PF_SWIMACTIVE_BIG+1),.lobyte(PF_SWIMACTIVE_BIG+2)
 .byte .lobyte(PF_SWIMIDLE_SMALL),.lobyte(PF_SWIMIDLE_SMALL+1),.lobyte(PF_SWIMIDLE_SMALL+2),.lobyte(PF_SWIMIDLE_SMALL),.lobyte(PF_SWIMIDLE_SMALL+1),.lobyte(PF_SWIMIDLE_SMALL+2)
Player_SwimIdleFrames:
 .byte .lobyte(PF_SWIMIDLE_BIG),.lobyte(PF_SWIMIDLE_BIG+1),.lobyte(PF_SWIMIDLE_BIG-8),.lobyte(PF_SWIMIDLE_BIG+1)
 .byte .lobyte(PF_SWIMIDLE_SMALL),.lobyte(PF_SWIMIDLE_SMALL),.lobyte(PF_SWIMIDLE_SMALL+3),.lobyte(PF_SWIMIDLE_SMALL+3)
Player_TailAttackFrames:
 .byte .lobyte(PF_TAILATKGROUND_BASE),.lobyte(PF_TAILATKGROUND_BASE+1),.lobyte(PF_TAILATKGROUND_BASE),.lobyte(PF_TAILATKGROUND_BASE+2),.lobyte(PF_TAILATKGROUND_BASE)
 .byte .lobyte(PF_TAILATKINAIR_BASE),.lobyte(PF_TAILATKINAIR_BASE-5),.lobyte(PF_TAILATKINAIR_BASE),.lobyte(PF_TAILATKINAIR_BASE-4),.lobyte(PF_TAILATKINAIR_BASE)
Player_KuriboFrame:
 .byte .lobyte(PF_KURIBO_SMALL),.lobyte(PF_KURIBO_BIG)
Player_DuckFrame:
 .byte .lobyte(PF_DUCK_NOTRACCOON),.lobyte(PF_DUCK_RACCOON)
Player_FireOnGround:
 .byte .lobyte(PF_THROWONGROUND_BASE),.lobyte(PF_THROWONGROUND_BASE+3),.lobyte(PF_THROWONGROUND_BASE+2)
Player_FireInAir:
 .byte .lobyte(PF_THROWINAIR_BASE),.lobyte(PF_THROWINAIR_BASE+1),.lobyte(PF_THROWINAIR_BASE+2)
Player_FrogHopFrames:
 .byte .lobyte(PF_FROGHOP_BASE),.lobyte(PF_FROGHOP_BASE+2),.lobyte(PF_FROGHOP_BASE+1),.lobyte(PF_FROGHOP_BASE)
Player_SpreadEagleFrames:
 .byte .lobyte(PF_RUNBIG_BASE),.lobyte(PF_RUNBIG_BASE+1),.lobyte(PF_RUNBIG_BASE+2),.lobyte(PF_RUNBIG_BASE+1)
 .byte .lobyte(PF_RUNSMALL_BASE),.lobyte(PF_RUNSMALL_BASE+1),.lobyte(PF_RUNSMALL_BASE),.lobyte(PF_RUNSMALL_BASE+1)
Player_TailWagFlyFrames:
 .byte .lobyte(PF_TAILWAGFLY_BASE+2),.lobyte(PF_TAILWAGFLY_BASE+1),.lobyte(PF_TAILWAGFLY_BASE)
 .byte .lobyte(PF_TAILWAGFLY_BASE+1),.lobyte(PF_TAILWAGFLY_BASE+2),.lobyte(PF_TAILWAGFLY_BASE)
 .byte .lobyte(PF_JUMPRACCOON),.lobyte(PF_JUMPRACCOON),.lobyte(PF_JUMPRACCOON)
 .byte .lobyte(PF_TAILWAGFALL+2),.lobyte(PF_TAILWAGFALL+1),.lobyte(PF_TAILWAGFALL)
Player_HoldingFrames:
 .byte .lobyte(PF_HOLDBIG_BASE),.lobyte(PF_HOLDBIG_BASE+1),.lobyte(PF_HOLDBIG_BASE+2),.lobyte(PF_HOLDBIG_BASE+1)
 .byte .lobyte(PF_HOLDSMALL_BASE),.lobyte(PF_HOLDSMALL_BASE+1),.lobyte(PF_HOLDSMALL_BASE),.lobyte(PF_HOLDSMALL_BASE+1)
Player_TwisterSpinFrames:
 .byte .lobyte(PF_SPINSMALLORFROG_BASE+12),.lobyte(PF_SPINSMALLORFROG_BASE),.lobyte(PF_SPINSMALLORFROG_BASE+12),.lobyte(PF_SPINSMALLORFROG_BASE)
 .byte .lobyte(PF_SPINSLIDESUITS_BASE+10),.lobyte(PF_SPINSLIDESUITS_BASE),.lobyte(PF_SPINSLIDESUITS_BASE+10),.lobyte(PF_SPINSLIDESUITS_BASE+1)
 .byte .lobyte(PF_SPINOTHER_BASE),.lobyte(PF_SPINOTHER_BASE+2),.lobyte(PF_SPINOTHER_BASE),.lobyte(PF_SPINOTHER_BASE+3)
Player_ClimbFrame:
 .byte .lobyte(PF_CLIMB_SMALL)
 .byte .lobyte(PF_CLIMB_BIG)
 .byte .lobyte(PF_CLIMB_BIG)
 .byte .lobyte(PF_CLIMB_BIG)
 .byte .lobyte(PF_CLIMB_FROG)
 .byte .lobyte(PF_CLIMB_BIG)
 .byte .lobyte(PF_CLIMB_BIG)
Airship_JumpFrameByPup:
 .byte .lobyte(PF_JUMPFALLSMALL)
 .byte .lobyte(PF_JUMPBIG)
 .byte .lobyte(PF_JUMPBIG)
 .byte .lobyte(PF_JUMPRACCOON)
 .byte .lobyte(PF_WALKSPECIAL_BASE+2)
 .byte .lobyte(PF_JUMPRACCOON)
 .byte .lobyte(PF_JUMPBIG)
Player_VibeDisableFrame:
 .byte .lobyte(PF_WALKSMALL_BASE)
 .byte .lobyte(PF_WALKBIG_BASE+2)
 .byte .lobyte(PF_WALKBIG_BASE+2)
 .byte .lobyte(PF_WALKSPECIAL_BASE+2)
 .byte .lobyte(PF_WALKSPECIAL_BASE)
 .byte .lobyte(PF_WALKSPECIAL_BASE+2)
 .byte .lobyte(PF_WALKBIG_BASE+2)
 .byte .lobyte($FE),.lobyte($02),.lobyte($05),.lobyte($FB),.lobyte($01)
 .byte .lobyte($02),.lobyte($03),.lobyte($00)
Player_PowerUpdate:
 LDY Player_FlyTime
 jeq PRG008_A4E4
 CPY #.lobyte($ff)
 jeq Sound_FullPowerRing
 LDA Counter_1
 AND #.lobyte($01)
 jeq PRG008_A4D5
 DEY
 STY Player_FlyTime
PRG008_A4D5:
 TYA
 jne Sound_FullPowerRing
 STY Player_Power
Sound_FullPowerRing:
 LDA Sound_QPlayer
 ORA #.lobyte(SND_PLAYERPOWER)
 STA Sound_QPlayer
 RTS
PRG008_A4E4:
 LDA Player_Power
 CMP #.lobyte($7f)
 jne PRG008_A4F8
 JSR Sound_FullPowerRing
 LDA Player_RunFlag
 jeq PRG008_A4F8
 LDY #.lobyte($10)
 JMP PRG008_A51A
PRG008_A4F8:
 LDA Player_PMeterCnt
 jne PRG008_A523
 SEC
 ROL Player_Power
 LDA Player_RunFlag
 jne PRG008_A50C
 ROR Player_Power
 LSR Player_Power
PRG008_A50C:
 LDY #.lobyte($18)
 LDA Player_Power
 jeq PRG008_A520
 LDA Player_RunFlag
 jeq PRG008_A51A
 LDY #.lobyte($08)
PRG008_A51A:
 STY Player_PMeterCnt
 JMP PRG008_A523
PRG008_A520:
 STA Player_FlyTime
PRG008_A523:
 LDA #.lobyte($00)
 STA Player_RunFlag
 RTS
Player_XAccelMain:
 .byte .lobyte(-1),.lobyte(0),.lobyte(2),.lobyte(0),.lobyte(-1),.lobyte(0),.lobyte(2),.lobyte(0)
 .byte .lobyte(-1),.lobyte(0),.lobyte(2),.lobyte(0),.lobyte(-1),.lobyte(0),.lobyte(2),.lobyte(0)
 .byte .lobyte(-1),.lobyte(0),.lobyte(2),.lobyte(0),.lobyte(-1),.lobyte(0),.lobyte(2),.lobyte(0)
 .byte .lobyte(-1),.lobyte(0),.lobyte(2),.lobyte(0),.lobyte(-1),.lobyte(0),.lobyte(2),.lobyte(0)
 .byte .lobyte(-1),.lobyte(2),.lobyte(2),.lobyte(0),.lobyte(-1),.lobyte(2),.lobyte(2),.lobyte(0)
 .byte .lobyte(-1),.lobyte(0),.lobyte(2),.lobyte(0),.lobyte(-1),.lobyte(0),.lobyte(2),.lobyte(0)
 .byte .lobyte(-1),.lobyte(0),.lobyte(2),.lobyte(0),.lobyte(-1),.lobyte(0),.lobyte(2),.lobyte(0)
Player_XAccelMain_UW:
 .byte .lobyte(-1),.lobyte(1),.lobyte(1),.lobyte(0),.lobyte(-1),.lobyte(0),.lobyte(0),.lobyte(0)
 .byte .lobyte(-1),.lobyte(0),.lobyte(0),.lobyte(0),.lobyte(-1),.lobyte(0),.lobyte(1),.lobyte(0)
 .byte .lobyte(-1),.lobyte(0),.lobyte(0),.lobyte(0),.lobyte(-1),.lobyte(0),.lobyte(0),.lobyte(0)
Player_XAccelPseudoFrac:
 .byte .lobyte($60),.lobyte($E0),.lobyte($00),.lobyte($00),.lobyte($60),.lobyte($E0),.lobyte($00),.lobyte($00)
 .byte .lobyte($20),.lobyte($E0),.lobyte($00),.lobyte($00),.lobyte($20),.lobyte($E0),.lobyte($00),.lobyte($00)
 .byte .lobyte($20),.lobyte($E0),.lobyte($00),.lobyte($00),.lobyte($20),.lobyte($E0),.lobyte($00),.lobyte($00)
 .byte .lobyte($20),.lobyte($E0),.lobyte($00),.lobyte($00),.lobyte($20),.lobyte($E0),.lobyte($00),.lobyte($00)
 .byte .lobyte($00),.lobyte($00),.lobyte($00),.lobyte($00),.lobyte($00),.lobyte($00),.lobyte($00),.lobyte($00)
 .byte .lobyte($60),.lobyte($E0),.lobyte($00),.lobyte($00),.lobyte($60),.lobyte($E0),.lobyte($00),.lobyte($00)
 .byte .lobyte($60),.lobyte($E0),.lobyte($00),.lobyte($00),.lobyte($60),.lobyte($E0),.lobyte($00),.lobyte($00)
Player_XAccelPseudoFrac_UW:
 .byte .lobyte($30),.lobyte($00),.lobyte($00),.lobyte($00),.lobyte($E0),.lobyte($30),.lobyte($80),.lobyte($00)
 .byte .lobyte($A0),.lobyte($E0),.lobyte($C0),.lobyte($00),.lobyte($A0),.lobyte($E0),.lobyte($20),.lobyte($00)
 .byte .lobyte($D0),.lobyte($E0),.lobyte($60),.lobyte($00),.lobyte($D0),.lobyte($E0),.lobyte($C0),.lobyte($00)
 .byte .lobyte($10),.lobyte($F0)
Player_WalkAnimTickMax:
 .byte .lobyte($07),.lobyte($06),.lobyte($05),.lobyte($04),.lobyte($03),.lobyte($02),.lobyte($01),.lobyte($01),.lobyte($01)
Player_RootJumpVel:
 .byte .lobyte(PLAYER_JUMP)
Player_SpeedJumpInc:
 .byte .lobyte($00),.lobyte($02),.lobyte($04),.lobyte($08)
 .byte .lobyte($00),.lobyte($03),.lobyte($06),.lobyte($08),.lobyte($08),.lobyte($08),.lobyte($08),.lobyte($06),.lobyte($03),.lobyte($00),.lobyte($04),.lobyte($08),.lobyte($12),.lobyte($16),.lobyte($16),.lobyte($12)
 .byte .lobyte($08),.lobyte($04)
Player_SomersaultFlipBits:
 .byte .lobyte($00),.lobyte($00),.lobyte($00),.lobyte($00),.lobyte($C0),.lobyte($C0),.lobyte($C0),.lobyte($C0),.lobyte($80),.lobyte($01)
FloatLevel_StatCheck:
 .byte .lobyte($40),.lobyte($80)
Level_CheckIfTileUnderwater:
 LDY #.lobyte($01)
 STY Temp_Var15
 LDA FloatLevel_PlayerWaterStat
 AND FloatLevel_StatCheck,X
 jne PRG008_A6A8
 LDA Temp_Var1,X
 ASL A
 ROL A
 ROL A
 AND #.lobyte($03)
 TAY
 LDA Temp_Var1,X
 CMP Tile_AttrTable,Y
 jcs PRG008_A6A9
 CMP #.lobyte(TILEA_PSWITCH_PRESSED)
 jne PRG008_A68D
 LDY #.lobyte($00)
 jeq PRG008_A6A6
PRG008_A68D:
 TYA
 ORA Temp_Var3
 TAY
 LDA Level_MinTileUWByQuad,Y
 LDY #.lobyte($00)
 CMP Temp_Var1,X
 jcs PRG008_A6A6
 INY
 LDA Temp_Var1,X
 CMP #.lobyte(TILE1_WFALLTOP)
 jeq PRG008_A6A5
 CMP #.lobyte(TILE1_WFALLMID)
 jne PRG008_A6A6
PRG008_A6A5:
 INY
PRG008_A6A6:
 STY Temp_Var15
PRG008_A6A8:
 CLC
PRG008_A6A9:
 RTS
Player_Control:
 LDA Player_FlipBits
 STA Player_FlipBits_OLD
 LDA Player_InAir
 STA Player_InAir_OLD
 LDA Player_EndLevel
 jne PRG008_A6D2
 LDA Player_VibeDisable
 jeq PRG008_A6DA
 DEC Player_VibeDisable
PRG008_A6D2:
 LDA #.lobyte($00)
 STA Player_XVel
 STA Pad_Holding
 STA Pad_Input
PRG008_A6DA:
 LDA Player_Slide
 jeq PRG008_A6E5
 LDA Pad_Input
 AND #.lobyte(~PAD_B)
 STA Pad_Input
PRG008_A6E5:
 LDA Level_Objects+1
 CMP #.lobyte(OBJ_TOADANDKING)
 jne PRG008_A6F2
 LDA Pad_Holding
 AND #.lobyte(~(PAD_LEFT | PAD_RIGHT | PAD_UP | PAD_DOWN))
 STA Pad_Holding
PRG008_A6F2:
 LDY Player_Suit
 jeq PRG008_A70E
 CPY #.lobyte(PLAYERSUIT_FROG)
 jeq PRG008_A70E
 LDA Player_IsHolding
 ORA Player_Slide
 ORA Player_Kuribo
 jne PRG008_A70E
 LDA Player_InAir
 jeq PRG008_A71C
 LDA Player_InWater
 jeq PRG008_A715
PRG008_A70E:
 LDA #.lobyte($00)
 STA Player_IsDucking
 jeq PRG008_A736
PRG008_A715:
 LDA Player_IsDucking
 jne PRG008_A733
 jeq PRG008_A736
PRG008_A71C:
 LDA #.lobyte($00)
 STA Player_IsDucking
 LDA Level_SlopeEn
 jeq PRG008_A72B
 LDA Player_SlideRate
 jne PRG008_A736
PRG008_A72B:
 LDA Pad_Holding
 AND #.lobyte((PAD_LEFT | PAD_RIGHT | PAD_UP | PAD_DOWN))
 CMP #.lobyte(PAD_DOWN)
 jne PRG008_A736
PRG008_A733:
 STY Player_IsDucking
PRG008_A736:
 LDY #.lobyte(20)
 LDA Player_Suit
 jeq PRG008_A743
 LDA Player_IsDucking
 jne PRG008_A743
 LDY #.lobyte(10)
PRG008_A743:
 STY Temp_Var10
 LDA #.lobyte($08)
 STA Temp_Var11
 JSR Player_GetTileAndSlope
 STA Level_Tile_Head
 STA Temp_Var1
 LDA Level_Tile_GndL
 STA Temp_Var2
 LDA Player_Behind
 STA Player_Behind_En
 jeq PRG008_A77E
 LDA Counter_1
 LSR A
 jcc PRG008_A766
 DEC Player_Behind
PRG008_A766:
 LDY #.lobyte($00)
 LDA Temp_Var1
 CMP #.lobyte($41)
 jeq PRG008_A77B
 CMP #.lobyte(TILE1_SKY)
 jeq PRG008_A77B
 INY
 LDA Player_Behind
 jne PRG008_A77B
 STY Player_Behind
PRG008_A77B:
 STY Player_Behind_En
PRG008_A77E:
 LDA Temp_Var1
 AND #.lobyte($c0)
 ASL A
 ROL A
 ROL A
 TAY
 LDA Temp_Var1
 CMP Tile_AttrTable+4,Y
 jcc PRG008_A7AD
 LDA Player_InAir
 ORA Player_InWater
 ORA Level_PipeMove
 jne PRG008_A7AD
 STA Player_XVel
 STA Pad_Input
 AND #.lobyte(~PAD_A)
 STA Pad_Input
 LDA #.lobyte($01)
 STA Player_LowClearance
 clc
 adc Player_X
 STA Player_X
 jcc PRG008_A7AD
 INC Player_XHi
PRG008_A7AD:
 LDA Level_TilesetIdx
 ASL A
 ASL A
 STA Temp_Var3
 LDX #.lobyte($00)
 JSR Level_CheckIfTileUnderwater
 jcs PRG008_A7BE
 TYA
 jne PRG008_A812
PRG008_A7BE:
 LDA Player_InWater
 jeq PRG008_A827
 LDA Player_InAir
 jne PRG008_A7CB
 jcs PRG008_A827
 jcc PRG008_A80B
PRG008_A7CB:
 jcs PRG008_A7D1
 LDA Player_YVel
 jmi PRG008_A7E2
PRG008_A7D1:
 ROR A
 STA Temp_Var16
 LDX #.lobyte($01)
 JSR Level_CheckIfTileUnderwater
 jcs PRG008_A7DE
 TYA
 jeq PRG008_A80B
PRG008_A7DE:
 LDA Temp_Var16
 jmi PRG008_A812
PRG008_A7E2:
 LDY Player_YVel
 CPY #.lobyte(-$0C)
 jpl PRG008_A7EA
 LDY #.lobyte(-$0C)
PRG008_A7EA:
 LDA Counter_1
 AND #.lobyte($07)
 jne PRG008_A7F1
 INY
PRG008_A7F1:
 STY Player_YVel
 LDA Pad_Input
 AND #.lobyte(~PAD_A)
 STA Pad_Input
 LDA Pad_Holding
 TAY
 AND #.lobyte(~PAD_UP)
 STA Pad_Holding
 TYA
 AND #.lobyte((PAD_UP | PAD_A))
 CMP #.lobyte((PAD_UP | PAD_A))
 jne PRG008_A827
 LDA #.lobyte(-$34)
 STA Player_YVel
PRG008_A80B:
 LDY #.lobyte($00)
 STY Player_SwimCnt
 jeq PRG008_A819
PRG008_A812:
 LDY Temp_Var15
 CPY Player_InWater
 jeq PRG008_A827
PRG008_A819:
 TYA
 ORA Player_InWater
 STY Player_InWater
 CMP #.lobyte($02)
 jeq PRG008_A827
 JSR Player_WaterSplash
PRG008_A827:
 LDA Player_FlipBits
 AND #.lobyte(%01111111)
 STA Player_FlipBits
 LDY Level_TilesetIdx
 LDA #.lobyte(TILEA_DOOR2)
 sec
 sbc Temp_Var1
 jeq PRG008_A83F
 CPY #.lobyte($01)
 jne PRG008_A86C
 CMP #.lobyte($01)
 jne PRG008_A86C
PRG008_A83F:
 LDA Pad_Input
 AND #.lobyte(PAD_UP)
 jeq PRG008_A86C
 LDA Player_InAir
 jne PRG008_A86C
 LDY #.lobyte($01)
 LDA Level_PipeNotExit
 jeq PRG008_A852
 LDY #.lobyte($03)
PRG008_A852:
 STY Level_JctCtl
 LDY #.lobyte(0)
 STY Map_ReturnStatus
 STY Player_XVel
 LDA Player_X
 AND #.lobyte($08)
 jeq PRG008_A864
 LDY #.lobyte(16)
PRG008_A864:
 TYA
 clc
 adc Player_X
 AND #.lobyte($F0)
 STA Player_X
PRG008_A86C:
 LDA Player_InWater
 ORA Player_IsHolding
 ORA Player_Kuribo
 jne PRG008_A890
 LDA Temp_Var1
 CMP #.lobyte(TILE1_VINE)
 jne PRG008_A890
 LDA Player_IsClimbing
 jne PRG008_A898
 LDA Pad_Holding
 AND #.lobyte((PAD_UP | PAD_DOWN))
 jeq PRG008_A890
 LDY Player_InAir
 jne PRG008_A898
 AND #.lobyte(%00001000)
 jne PRG008_A898
PRG008_A890:
 LDA #.lobyte($00)
 STA Player_IsClimbing
 JMP PRG008_A8F9
PRG008_A898:
 LDA #.lobyte($01)
 STA Player_IsClimbing
 LDA #.lobyte($00)
 STA Player_XVel
 STA Player_YVel
 LDY #.lobyte($10)
 LDA Pad_Holding
 AND #.lobyte((PAD_UP | PAD_DOWN))
 jeq PRG008_A8CA
 AND #.lobyte(PAD_UP)
 jeq PRG008_A8C8
 LDY #.lobyte(16)
 LDA Player_Suit
 jeq PRG008_A8B7
 LDY #.lobyte(0)
PRG008_A8B7:
 STY Temp_Var10
 LDA #.lobyte($08)
 STA Temp_Var11
 JSR Player_GetTileAndSlope
 CMP #.lobyte(TILE1_VINE)
 jne PRG008_A8CA
 LDY #.lobyte(-$10)
 STY Player_InAir
PRG008_A8C8:
 STY Player_YVel
PRG008_A8CA:
 LDY #.lobyte($10)
 LDA Pad_Holding
 AND #.lobyte((PAD_LEFT | PAD_RIGHT))
 jeq PRG008_A8DA
 AND #.lobyte(PAD_LEFT)
 jeq PRG008_A8D8
 LDY #.lobyte(-$10)
PRG008_A8D8:
 STY Player_XVel
PRG008_A8DA:
 LDA Player_IsClimbing
 jeq PRG008_A8EC
 LDA Player_InAir
 jne PRG008_A8EC
 LDA Pad_Holding
 AND #.lobyte((PAD_UP | PAD_DOWN))
 jne PRG008_A8EC
 STA Player_IsClimbing
PRG008_A8EC:
 JSR Player_ApplyXVelocity
 JSR Player_ApplyYVelocity
 JSR Player_DoClimbAnim
 JSR Player_Draw29
 RTS
PRG008_A8F9:
 LDA Player_SlideRate
 jeq PRG008_A906
 LDA Player_XVel
 clc
 adc Player_SlideRate
 STA Player_XVel
PRG008_A906:
 JSR Player_ApplyXVelocity
 LDA Player_SlideRate
 jeq PRG008_A916
 LDA Player_XVel
 sec
 sbc Player_SlideRate
 STA Player_XVel
PRG008_A916:
 LDA #.lobyte($00)
 STA Player_SlideRate
 LDY #.lobyte($02)
 LDA Player_XVel
 jpl PRG008_A925
 JSR Negate
 DEY
PRG008_A925:
 jne PRG008_A928
 TAY
PRG008_A928:
 STA Temp_Var3
 STY Player_MoveLR
 LDA Player_InAir
 jeq PRG008_A940
 LDA Player_YHi
 jpl PRG008_A93D
 LDA Player_Y
 jmi PRG008_A93D
 LDA Player_YVel
 jmi PRG008_A940
PRG008_A93D:
 JSR Player_ApplyYVelocity
PRG008_A940:
 JSR Player_CommonGroundAnims
 LDA Player_Kuribo
 jeq PRG008_A94C
 LDA #.lobyte(14)
 jne PRG008_A956
PRG008_A94C:
 LDA Player_Suit
 LDY Player_InWater
 jeq PRG008_A956
 clc
 adc #.lobyte($07)
PRG008_A956:
 ASL A
 TAY
 LDA PowerUpMovement_JumpTable,Y
 STA Temp_Var1
 LDA PowerUpMovement_JumpTable+1,Y
 STA Temp_Var2
 JMP (Temp_Var1)
PowerUpMovement_JumpTable:
 .word GndMov_Small
 .word GndMov_Big
 .word GndMov_FireHammer
 .word GndMov_Leaf
 .word GndMov_Frog
 .word GndMov_Tanooki
 .word GndMov_FireHammer
 .word Swim_SmallBigLeaf
 .word Swim_SmallBigLeaf
 .word Swim_FireHammer
 .word Swim_SmallBigLeaf
 .word Swim_Frog
 .word Swim_Tanooki
 .word Swim_FireHammer
 .word Move_Kuribo
GndMov_Small:
 JSR Player_GroundHControl
 JSR Player_JumpFlyFlutter
 LDA Player_SandSink
 LSR A
 jcs PRG008_A9A3
 LDA Player_AllowAirJump
 jne PRG008_A9A3
 LDA Player_InAir
 jeq PRG008_A9A3
 LDA #.lobyte(PF_JUMPFALLSMALL)
 LDY Player_FlyTime
 jeq PRG008_A9A1
 LDA #.lobyte(PF_FASTJUMPFALLSMALL)
PRG008_A9A1:
 STA Player_Frame
PRG008_A9A3:
 RTS
Swim_SmallBigLeaf:
 JSR Player_UnderwaterHControl
 JSR Player_SwimV
 JSR Player_SwimAnim
 RTS
GndMov_Big:
 JSR Player_GroundHControl
 JSR Player_JumpFlyFlutter
 JSR Player_SoarJumpFallFrame
 RTS
 RTS
GndMov_FireHammer:
 JSR Player_GroundHControl
 JSR Player_JumpFlyFlutter
 JSR Player_SoarJumpFallFrame
 JSR Player_ShootAnim
 RTS
Swim_FireHammer:
 JSR Player_UnderwaterHControl
 JSR Player_SwimV
 JSR Player_SwimAnim
 JSR Player_ShootAnim
 RTS
GndMov_Leaf:
 JSR Player_GroundHControl
 JSR Player_JumpFlyFlutter
 JSR Player_AnimTailWag
 JSR Player_TailAttackAnim
 RTS
 RTS
GndMov_Frog:
 JSR Player_GroundHControl
 JSR Player_JumpFlyFlutter
 LDA Player_IsHolding
 jne PRG008_AA23
 LDA Player_InAir
 jeq PRG008_AA00
 LDA Player_SandSink
 LSR A
 jcs PRG008_AA00
 LDA #.lobyte($00)
 STA Player_FrogHopCnt
 LDY #.lobyte($01)
 JMP PRG008_AA1E
PRG008_AA00:
 LDA Player_FrogHopCnt
 jne PRG008_AA1A
 STA Player_XVel
 LDA Pad_Holding
 AND #.lobyte((PAD_LEFT | PAD_RIGHT))
 jeq PRG008_AA1A
 LDA Sound_QPlayer
 ORA #.lobyte(SND_PLAYERFROG)
 STA Sound_QPlayer
 LDA #.lobyte($1f)
 STA Player_FrogHopCnt
PRG008_AA1A:
 LSR A
 LSR A
 LSR A
 TAY
PRG008_AA1E:
 LDA Player_FrogHopFrames,Y
 STA Player_Frame
PRG008_AA23:
 RTS
Frog_SwimSoundMask:
 .byte .lobyte($03),.lobyte($07)
Frog_BaseFrame:
 .byte .lobyte(PF_FROGSWIM_DOWNBASE),.lobyte(PF_FROGSWIM_UPBASE),.lobyte(PF_FROGSWIM_LRBASE)
Frog_FrameOffset:
 .byte .lobyte($02),.lobyte($02),.lobyte($02),.lobyte($01),.lobyte($00),.lobyte($01),.lobyte($02),.lobyte($02)
Frog_Velocity:
 .byte .lobyte(16),.lobyte(-16)
Swim_Frog:
 LDX #.lobyte($ff)
 LDA Pad_Holding
 AND #.lobyte((PAD_UP | PAD_DOWN))
 jeq PRG008_AA61
 STA Player_InAir
 LSR A
 LSR A
 LSR A
 TAX
 LDA Frog_Velocity,X
 jpl PRG008_AA4D
 LDY Player_AboveTop
 jpl PRG008_AA4D
 LDA #.lobyte($00)
PRG008_AA4D:
 LDY Pad_Holding
 jpl PRG008_AA52
 ASL A
PRG008_AA52:
 CMP #.lobyte((PLAYER_FROG_MAXYVEL+1))
 jcc PRG008_AA5C
 LDY Player_InAir
 jne PRG008_AA5C
 LDA #.lobyte(PLAYER_FROG_MAXYVEL)
PRG008_AA5C:
 STA Player_YVel
 JMP PRG008_AA6E
PRG008_AA61:
 LDY Player_YVel
 jeq PRG008_AA6E
 INY
 LDA Player_YVel
 jmi PRG008_AA6C
 DEY
 DEY
PRG008_AA6C:
 STY Player_YVel
PRG008_AA6E:
 LDA Pad_Holding
 AND #.lobyte((PAD_LEFT | PAD_RIGHT))
 jeq PRG008_AA84
 LSR A
 TAY
 LDA Frog_Velocity,Y
 LDY Pad_Holding
 jpl PRG008_AA7E
 ASL A
PRG008_AA7E:
 STA Player_XVel
 LDX #.lobyte($02)
 jne PRG008_AA9C
PRG008_AA84:
 LDY Player_XVel
 jeq PRG008_AA94
 INY
 LDA Player_XVel
 jmi PRG008_AA8F
 DEY
 DEY
PRG008_AA8F:
 STY Player_XVel
 JMP PRG008_AA9C
PRG008_AA94:
 LDA Player_InAir
 jne PRG008_AA9C
 LDA #.lobyte($15)
 jne PRG008_AAD2
PRG008_AA9C:
 TXA
 jmi PRG008_AAC8
 LDA Counter_1
 LSR A
 LSR A
 LDY #.lobyte($00)
 BIT Pad_Holding
 jmi PRG008_AAAB
 LSR A
 INY
PRG008_AAAB:
 AND #.lobyte($07)
 TAY
 jne PRG008_AABF
 LDA Counter_1
 AND Frog_SwimSoundMask,Y
 jne PRG008_AABF
 LDA Sound_QPlayer
 ORA #.lobyte(SND_PLAYERSWIM)
 STA Sound_QPlayer
PRG008_AABF:
 LDA Frog_BaseFrame,X
 clc
 adc Frog_FrameOffset,Y
 jne PRG008_AAD2
PRG008_AAC8:
 LDY #.lobyte(PF_FROGSWIM_IDLEBASE)
 LDA Counter_1
 AND #.lobyte($08)
 jeq PRG008_AAD1
 INY
PRG008_AAD1:
 TYA
PRG008_AAD2:
 STA Player_Frame
 RTS
GndMov_Tanooki:
 JSR Player_TanookiStatue
 JSR Player_GroundHControl
 JSR Player_JumpFlyFlutter
 JSR Player_AnimTailWag
 JSR Player_TailAttackAnim
 RTS
Swim_Tanooki:
 JSR Player_TanookiStatue
 JSR Player_UnderwaterHControl
 JSR Player_SwimV
 JSR Player_SwimAnim
 RTS
Move_Kuribo:
 JSR Player_GroundHControl
 JSR Player_JumpFlyFlutter
 LDA Player_InAir
 jne PRG008_AAFF
 STA Player_KuriboDir
PRG008_AAFF:
 LDA Player_KuriboDir
 jne PRG008_AB17
 LDA Player_InAir
 jne PRG008_AB25
 LDA Pad_Holding
 AND #.lobyte((PAD_LEFT | PAD_RIGHT))
 STA Player_KuriboDir
 jeq PRG008_AB25
 INC Player_InAir
 LDY #.lobyte(-$20)
 STY Player_YVel
PRG008_AB17:
 LDA Pad_Input
 jpl PRG008_AB25
 LDA #.lobyte($00)
 STA Player_KuriboDir
 LDY Player_RootJumpVel
 STY Player_YVel
PRG008_AB25:
 LDY Player_Suit
 jeq PRG008_AB2B
 LDY #.lobyte($01)
PRG008_AB2B:
 LDA Player_KuriboFrame,Y
 STA Player_Frame
 LDA Counter_1
 AND #.lobyte($08)
 jeq PRG008_AB38
 INC Player_Frame
PRG008_AB38:
 RTS
Player_UphillSpeedVals:
 .byte .lobyte($00),.lobyte($16),.lobyte($15),.lobyte($14),.lobyte($13),.lobyte($12),.lobyte($11),.lobyte($10),.lobyte($0F),.lobyte($0E),.lobyte($0D)
Player_GroundHControl:
 LDA Player_UphillFlag
 jeq PRG008_AB56
 INC Player_WalkAnimTicks
 LDY #.lobyte(10)
 BIT Pad_Holding
 jvc PRG008_AB5B
 LDY #.lobyte(1)
 jne PRG008_AB5B
PRG008_AB56:
 LDY Player_UphillSpeedIdx
 jeq PRG008_AB62
PRG008_AB5B:
 LDA Player_UphillSpeedVals,Y
 TAY
 JMP PRG008_AB83
PRG008_AB62:
 LDY #.lobyte(PLAYER_TOPWALKSPEED)
 BIT Pad_Holding
 jvc PRG008_AB83
 LDA Player_InAir
 ORA Player_Slide
 jne PRG008_AB78
 LDA Temp_Var3
 CMP #.lobyte(PLAYER_TOPRUNSPEED)
 jmi PRG008_AB78
 INC Player_RunFlag
PRG008_AB78:
 LDY #.lobyte(PLAYER_TOPRUNSPEED)
 LDA Player_Power
 CMP #.lobyte($7f)
 jne PRG008_AB83
 LDY #.lobyte(PLAYER_TOPPOWERSPEED)
PRG008_AB83:
 STY Temp_Var14
 LDY Player_Slippery
 jeq PRG008_AB98
 INC Player_WalkAnimTicks
 DEY
 TYA
 ASL A
 ASL A
 ASL A
 clc
 adc #.lobyte($40)
 TAY
 jne PRG008_AB9E
PRG008_AB98:
 LDA Player_Suit
 ASL A
 ASL A
 ASL A
 TAY
PRG008_AB9E:
 BIT Pad_Holding
 jvc PRG008_ABA6
 INY
 INY
 INY
 INY
PRG008_ABA6:
 LDA Pad_Holding
 AND #.lobyte((PAD_LEFT | PAD_RIGHT))
 jne PRG008_ABB8
 LDA Player_InAir
 jne PRG008_AC01
 LDA Player_XVel
 jeq PRG008_AC01
 jmi PRG008_ABD3
 jpl PRG008_ABEB
PRG008_ABB8:
 INY
 INY
 AND Player_MoveLR
 jne PRG008_ABCD
 DEY
 LDA Temp_Var3
 CMP Temp_Var14
 jeq PRG008_AC01
 jmi PRG008_ABCD
 LDA Player_InAir
 jne PRG008_AC01
 DEY
PRG008_ABCD:
 LDA Pad_Holding
 AND #.lobyte(PAD_RIGHT)
 jne PRG008_ABEB
PRG008_ABD3:
 LDA #.lobyte($00)
 sec
 sbc Player_XAccelPseudoFrac,Y
 STA Temp_Var1
 LDA Player_XAccelMain,Y
 EOR #.lobyte($ff)
 STA Temp_Var2
 LDA Temp_Var1
 jne PRG008_ABF5
 INC Temp_Var2
 JMP PRG008_ABF5
PRG008_ABEB:
 LDA Player_XAccelPseudoFrac,Y
 STA Temp_Var1
 LDA Player_XAccelMain,Y
 STA Temp_Var2
PRG008_ABF5:
 LDA Temp_Var1
 clc
 adc Counter_Wiggly
 LDA Player_XVel
 ADC Temp_Var2
 STA Player_XVel
PRG008_AC01:
 RTS
Player_UnderwaterHControl:
 LDY #.lobyte((Player_XAccelMain_UW - Player_XAccelMain))
 LDA #.lobyte(%00001000)
 STA Temp_Var14
 LDA Player_InAir
 jeq PRG008_AC14
 LDA #.lobyte(24)
 STA Temp_Var14
 INY
 INY
 INY
 INY
PRG008_AC14:
 LDA Player_InAir
 PHA
 LDA #.lobyte($00)
 STA Player_InAir
 JSR PRG008_ABA6
 PLA
 STA Player_InAir
 RTS
PRG008_AC22:
 .byte .lobyte($D0),.lobyte($CE),.lobyte($CC),.lobyte($CA),.lobyte($CA),.lobyte($CA)
Player_JumpFlyFlutter:
 LDA Player_AllowAirJump
 jeq PRG008_AC30
 DEC Player_AllowAirJump
PRG008_AC30:
 LDA Pad_Input
 AND #.lobyte(PAD_A)
 STA Temp_Var1
 jeq PRG008_AC9E
 LDA Player_AllowAirJump
 jne PRG008_AC41
 LDA Player_InAir
 jne PRG008_AC9E
PRG008_AC41:
 LDA Sound_QPlayer
 ORA #.lobyte(SND_PLAYERJUMP)
 STA Sound_QPlayer
 LDA Player_StarInv
 jeq PRG008_AC6C
 LDA Player_Power
 CMP #.lobyte($7f)
 jeq PRG008_AC6C
 LDA Player_IsHolding
 jne PRG008_AC6C
 LDA Player_Suit
 jeq PRG008_AC6C
 CMP #.lobyte(PLAYERSUIT_FROG)
 jeq PRG008_AC6C
 STA Player_Flip
 STA Player_InAir
 LDA #.lobyte($00)
 STA Player_AllowAirJump
PRG008_AC6C:
 LDA Player_XVel
 jpl PRG008_AC73
 JSR Negate
PRG008_AC73:
 LSR A
 LSR A
 LSR A
 LSR A
 TAX
 LDA Player_RootJumpVel
 sec
 sbc Player_SpeedJumpInc,X
 STA Player_YVel
 LDA #.lobyte($01)
 STA Player_InAir
 LDA #.lobyte($00)
 STA Player_WagCount
 STA Player_AllowAirJump
 LDA Player_Power
 CMP #.lobyte($7f)
 jne PRG008_AC9E
 LDA Player_FlyTime
 jne PRG008_AC9E
 LDA #.lobyte($80)
 STA Player_FlyTime
PRG008_AC9E:
 LDA Player_InAir
 jne PRG008_ACB3
 LDY Player_Suit
 LDA PowerUp_Ability,Y
 AND #.lobyte($01)
 jne PRG008_AD1A
 LDA #.lobyte($00)
 STA Player_FlyTime
 JMP PRG008_AD1A
PRG008_ACB3:
 LDY #.lobyte($05)
 LDA Player_YVel
 CMP #.lobyte(-$20)
 jpl PRG008_ACC8
 LDA Player_mGoomba
 jne PRG008_ACCD
 LDA Pad_Holding
 jpl PRG008_ACC8
 LDY #.lobyte($01)
 jne PRG008_ACCD
PRG008_ACC8:
 LDA #.lobyte($00)
 STA Player_mGoomba
PRG008_ACCD:
 TYA
 clc
 adc Player_YVel
 STA Player_YVel
 LDA Player_WagCount
 jeq PRG008_ACD9
 DEC Player_WagCount
PRG008_ACD9:
 LDA Player_Kuribo
 jne PRG008_ACEF
 LDX Player_Suit
 LDA PowerUp_Ability,X
 AND #.lobyte($01)
 jeq PRG008_ACEF
 LDY Temp_Var1
 jeq PRG008_ACEF
 LDA #.lobyte($10)
 STA Player_WagCount
PRG008_ACEF:
 LDA Player_WagCount
 jeq PRG008_AD1A
 LDA Player_YVel
 CMP #.lobyte(PLAYER_FLY_YVEL)
 jmi PRG008_AD1A
 LDY #.lobyte(PLAYER_FLY_YVEL)
 LDA Player_FlyTime
 jeq PRG008_AD0E
 CMP #.lobyte($0f)
 jcs PRG008_AD18
 LDY #.lobyte($F0)
 AND #.lobyte($08)
 jne PRG008_AD18
 LDY #.lobyte($00)
 jeq PRG008_AD18
PRG008_AD0E:
 LDA Player_YVel
 jmi PRG008_AD1A
 CMP #.lobyte(PLAYER_TAILWAG_YVEL)
 jcc PRG008_AD1A
 LDY #.lobyte(PLAYER_TAILWAG_YVEL)
PRG008_AD18:
 STY Player_YVel
PRG008_AD1A:
 LDA Player_UphillSpeedIdx
 jeq PRG008_AD2E
 LSR A
 TAY
 LDA Player_YVel
 jpl PRG008_AD2E
 CMP PRG008_AC22,Y
 jmi PRG008_AD2E
 LDA #.lobyte($20)
 STA Player_YVel
PRG008_AD2E:
 RTS
Player_SwimV:
 LDA Pad_Input
 jpl PRG008_AD4C
 LDA Sound_QPlayer
 ORA #.lobyte(SND_PLAYERSWIM)
 STA Sound_QPlayer
 LDY Player_InAir
 jne PRG008_AD45
 LDA #.lobyte(PLAYER_SWIMSTART_YVEL)
 STA Player_InAir
 jne PRG008_AD4A
PRG008_AD45:
 LDA Player_YVel
 sec
 sbc #.lobyte(PLAYER_SWIM_YVEL)
PRG008_AD4A:
 STA Player_YVel
PRG008_AD4C:
 LDA Player_InAir
 jeq PRG008_AD7E
 LDA Player_YVel
 jmi PRG008_AD5A
 LDA Counter_1
 AND #.lobyte($02)
 jne PRG008_AD5C
PRG008_AD5A:
 INC Player_YVel
PRG008_AD5C:
 LDY #.lobyte(PLAYER_SWIM_YVEL)
 LDA Player_YVel
 jpl PRG008_AD75
 LDY Player_AboveTop
 jpl PRG008_AD73
 LDY Player_SpriteY
 CPY #.lobyte(-8)
 jcs PRG008_AD73
 clc
 adc #.lobyte($10)
 STA Player_YVel
PRG008_AD73:
 LDY #.lobyte(PLAYER_SWIMSTART_YVEL)
PRG008_AD75:
 clc
 adc #.lobyte(PLAYER_SWIM_YVEL)
 CMP #.lobyte(PLAYER_MAXSPEED)
 jcc PRG008_AD7E
 STY Player_YVel
PRG008_AD7E:
 RTS
Player_SwimAnim:
 LDA Player_InAir
 jeq PRG008_ADBC
 LDA Pad_Input
 jpl PRG008_AD9A
 LDA Player_SwimCnt
 jne PRG008_AD97
PRG008_AD8C:
 LDA #.lobyte($00)
 STA Player_SwimCnt
 STA Counter_ByPlayerSpd
 STA Player_WalkAnimTicks
PRG008_AD97:
 INC Player_SwimCnt
PRG008_AD9A:
 LDA Player_SwimCnt
 jne PRG008_ADBD
 LDA Player_XVel
 jne PRG008_ADAD
 LDA Counter_1
 AND #.lobyte($30)
 LSR A
 LSR A
 LSR A
 LSR A
 STA Player_WalkFrame
PRG008_ADAD:
 LDY Player_WalkFrame
 LDA Player_Suit
 jne PRG008_ADB7
 INY
 INY
 INY
 INY
PRG008_ADB7:
 LDA Player_SwimIdleFrames,Y
 STA Player_Frame
PRG008_ADBC:
 RTS
PRG008_ADBD:
 LDA Counter_ByPlayerSpd
 CMP #.lobyte($06)
 jcc PRG008_ADCB
 DEC Player_SwimCnt
 jne PRG008_AD8C
 LDA #.lobyte($05)
PRG008_ADCB:
 LDY Player_Suit
 jne PRG008_ADD2
 clc
 adc #.lobyte($06)
PRG008_ADD2:
 TAY
 LDA Player_SwimActiveFrames,Y
 STA Player_Frame
 RTS
Player_CommonGroundAnims:
 LDA Player_XVel
 jpl PRG008_ADE0
 JSR Negate
PRG008_ADE0:
 LSR A
 LSR A
 LSR A
 TAY
 INC Player_WalkAnimTicks
 LDA Player_WalkAnimTicks
 CMP Player_WalkAnimTickMax,Y
 jmi PRG008_AE03
 LDA #.lobyte($00)
 STA Player_WalkAnimTicks
 INC Player_WalkFrame
 INC Counter_ByPlayerSpd
 LDA Player_WalkFrame
 CMP #.lobyte($04)
 jmi PRG008_AE03
 LDA #.lobyte($00)
 STA Player_WalkFrame
PRG008_AE03:
 LDA Pad_Holding
 AND #.lobyte((PAD_LEFT | PAD_RIGHT))
 jne PRG008_AE11
 LDA Player_XVel
 jne PRG008_AE11
 LDA #.lobyte($02)
 STA Player_WalkFrame
PRG008_AE11:
 LDA Player_TailAttack
 jne PRG008_AE26
 LDA Pad_Holding
 AND #.lobyte((PAD_LEFT | PAD_RIGHT))
 jeq PRG008_AE26
 LDY #.lobyte($00)
 AND #.lobyte(%00000010)
 jne PRG008_AE24
 LDY #.lobyte(SPR_HFLIP)
PRG008_AE24:
 STY Player_FlipBits
PRG008_AE26:
 LDA Debug_Flag
 CMP #.lobyte($80)
 jne PRG008_AE58
 LDA Pad_Input
 AND #.lobyte(PAD_SELECT)
 jeq PRG008_AE58
 LDA Pad_Holding
 AND #.lobyte((PAD_A | PAD_B))
 jne PRG008_AE50
 LDA Player_Suit
 clc
 adc #.lobyte($01)
 STA Player_QueueSuit
 CMP #.lobyte((PLAYERSUIT_LAST+1))
 jmi PRG008_AE47
 LDA #.lobyte($00)
PRG008_AE47:
 STA Player_QueueSuit
 INC Player_QueueSuit
 JMP PRG008_AE58
PRG008_AE50:
 LDA Player_Kuribo
 EOR #.lobyte($01)
 STA Player_Kuribo
PRG008_AE58:
 LDA Player_Suit
 ASL A
 ASL A
 ORA Player_WalkFrame
 TAY
 LDA Player_WalkFramesByPUp,Y
 STA Player_Frame
 LDA Player_InWater
 jne PRG008_AE90
 LDA Player_XVel
 clc
 adc #.lobyte($01)
 CMP #.lobyte($03)
 jcc PRG008_AE90
 LDA Player_MoveLR
 AND Pad_Holding
 jeq PRG008_AE90
 LDY Player_Suit
 jeq PRG008_AE7F
 LDY #.lobyte($01)
PRG008_AE7F:
 LDA Player_InAir
 jne PRG008_AE90
 LDA Sound_QLevel2
 ORA #.lobyte(SND_LEVELSKID)
 STA Sound_QLevel2
 LDA Player_SkidFrame,Y
 STA Player_Frame
PRG008_AE90:
 LDA Player_IsDucking
 jeq PRG008_AEA2
 LDY Player_Suit
 LDA PowerUp_Ability,Y
 AND #.lobyte($01)
 TAY
 LDA Player_DuckFrame,Y
 STA Player_Frame
PRG008_AEA2:
 LDA Player_Slide
 jeq PRG008_AEC0
 LDA Player_InAir
 jne PRG008_AEB1
 LDA Pad_Holding
 AND #.lobyte((PAD_LEFT | PAD_RIGHT | PAD_UP))
 jeq PRG008_AEB6
PRG008_AEB1:
 LDA #.lobyte($00)
 STA Player_Slide
PRG008_AEB6:
 LDA #.lobyte(PF_SLIDE_BIG)
 LDY Player_Suit
 jne PRG008_AEBE
 LDA #.lobyte(PF_SLIDE_SMALL)
PRG008_AEBE:
 STA Player_Frame
PRG008_AEC0:
 RTS
TwisterSpin_FlipBits:
 .byte .lobyte($00),.lobyte($40)
Player_SetSpecialFrames:
 LDA Player_XVel
 jpl PRG008_AECA
 JSR Negate
PRG008_AECA:
 CMP #.lobyte($37)
 jcc PRG008_AEF0
 LDA Player_FlyTime
 jne PRG008_AEF0
 LDA Player_IsDucking
 ORA Player_Kuribo
 ORA Player_IsClimbing
 ORA Player_Slide
 jne PRG008_AEF0
 LDY Player_WalkFrame
 LDA Player_Suit
 jne PRG008_AEEB
 INY
 INY
 INY
 INY
PRG008_AEEB:
 LDA Player_SpreadEagleFrames,Y
 STA Player_Frame
PRG008_AEF0:
 LDA Player_Flip
 jeq PRG008_AF0F
 LDA Counter_1
 LSR A
 PHA
 AND #.lobyte($07)
 TAY
 LDA Player_SomersaultFlipBits,Y
 LDY Player_XVel
 jpl PRG008_AF05
 EOR #.lobyte(SPR_HFLIP)
PRG008_AF05:
 STA Player_FlipBits
 PLA
 AND #.lobyte($03)
 clc
 adc #.lobyte(PF_SOMERSAULT_BASE)
 STA Player_Frame
PRG008_AF0F:
 LDA Player_IsHolding
 jeq PRG008_AF2F
 LDY Player_WalkFrame
 LDA Player_InAir_OLD
 jeq PRG008_AF22
 LDY #.lobyte($00)
 LDA Player_Suit
 jne PRG008_AF22
 INY
PRG008_AF22:
 LDA Player_Suit
 jne PRG008_AF2A
 INY
 INY
 INY
 INY
PRG008_AF2A:
 LDA Player_HoldingFrames,Y
 STA Player_Frame
PRG008_AF2F:
 LDA Player_PipeFace
 jne PRG008_AF45
 LDA Player_IsHolding
 jeq PRG008_AF52
 LDA Player_FlipBits
 CMP Player_FlipBits_OLD
 jeq PRG008_AF52
 LDA #.lobyte($07)
 STA Player_PipeFace
PRG008_AF45:
 DEC Player_PipeFace
 LDA #.lobyte(PF_INPIPE_BIG)
 LDY Player_Suit
 jne PRG008_AF50
 LDA #.lobyte(PF_INPIPE_SMALL)
PRG008_AF50:
 STA Player_Frame
PRG008_AF52:
 LDA Player_Kick
 jeq PRG008_AF69
 LDA #.lobyte($00)
 STA Player_TailAttack
 LDY #.lobyte(PF_KICK_SMALL)
 LDA Player_Suit
 jeq PRG008_AF64
 LDY #.lobyte(PF_KICK_BIG)
PRG008_AF64:
 STY Player_Frame
 DEC Player_Kick
PRG008_AF69:
 LDA Player_TwisterSpin
 jeq PRG008_AFA1
 DEC Player_TwisterSpin
 LDY #.lobyte($00)
 LDA Player_Suit
 jeq PRG008_AF87
 CMP #.lobyte($04)
 jeq PRG008_AF85
 LDY #.lobyte($04)
 TAX
 LDA PowerUp_Ability,X
 AND #.lobyte($01)
 jeq PRG008_AF87
PRG008_AF85:
 LDY #.lobyte($08)
PRG008_AF87:
 STY Temp_Var1
 LDA Counter_1
 AND #.lobyte($0c)
 LSR A
 LSR A
 PHA
 LSR A
 TAY
 LDA TwisterSpin_FlipBits,Y
 STA Player_FlipBits
 PLA
 clc
 adc Temp_Var1
 TAY
 LDA Player_TwisterSpinFrames,Y
 STA Player_Frame
PRG008_AFA1:
 LDA Player_VibeDisable
 jeq PRG008_AFAD
 LDY Player_Suit
 LDA Player_VibeDisableFrame,Y
 STA Player_Frame
PRG008_AFAD:
 RTS
Player_TanookiStatue:
 LDA Pad_Holding
 AND #.lobyte(PAD_DOWN)
 TAY
 jeq PRG008_AFE3
 BIT Pad_Input
 jvc PRG008_AFE3
 LDA Player_Statue
 jne PRG008_AFE3
 JSR Sound_StatueSwitch
 LDA #.lobyte($20)
 STA Player_QueueSuit
 LDA #.lobyte($17)
 STA Player_SuitLost
 jne PRG008_B010
PRG008_AFCD:
 LDA #.lobyte(PF_STATUE)
 STA Player_Frame
 LDA #.lobyte($00)
 STA Player_XVel
 LDA Player_InAir
 jeq PRG008_AFE0
 LDA Player_YVel
 clc
 adc #.lobyte($07)
 STA Player_YVel
PRG008_AFE0:
 PLA
 PLA
 RTS
PRG008_AFE3:
 LDA Player_Statue
 jeq PRG008_B010
 CMP #.lobyte($01)
 jeq PRG008_AFFB
 CMP #.lobyte($60)
 jne PRG008_AFF5
 LDA #.lobyte($60)
 STA Player_FlashInv
PRG008_AFF5:
 DEC Player_Statue
 TYA
 jne PRG008_AFCD
PRG008_AFFB:
 LDA #.lobyte($00)
 STA Player_Statue
 STA Player_FlashInv
 JSR Level_SetPlayerPUpPal
 JSR Sound_StatueSwitch
 LDA #.lobyte($17)
 STA Player_SuitLost
 jne PRG008_AFCD
PRG008_B010:
 RTS
Sound_StatueSwitch:
 LDA Sound_QLevel1
 ORA #.lobyte(SND_LEVELPOOF)
 STA Sound_QLevel1
 RTS
Player_DoClimbAnim:
 LDA Player_IsClimbing
 jeq PRG008_B035
 LDY Player_Suit
 LDA Player_ClimbFrame,Y
 STA Player_Frame
 LDA Pad_Holding
 AND #.lobyte((PAD_UP | PAD_DOWN))
 jeq PRG008_B035
 LDA Counter_1
 AND #.lobyte($08)
 ASL A
 ASL A
 ASL A
 STA Player_FlipBits
PRG008_B035:
 RTS
Player_AnimTailWag:
 LDA Player_SandSink
 LSR A
 jcs PRG008_B09F
 LDA Player_AllowAirJump
 jne PRG008_B09F
 LDA Player_InAir
 jeq PRG008_B09F
 LDA Player_IsDucking
 jne PRG008_B082
 LDA Pad_Input
 jpl PRG008_B062
 LDA Sound_QPlayer
 CMP #.lobyte(SND_PLAYERJUMP)
 jeq PRG008_B05D
 LDA Sound_QLevel1
 ORA #.lobyte(SND_LEVELTAILWAG)
 STA Sound_QLevel1
PRG008_B05D:
 LDA #.lobyte(10)
 STA Player_TailCount
PRG008_B062:
 LDA Player_TailCount
 LSR A
 LSR A
 STA Temp_Var1
 LDA #.lobyte($00)
 LDY Player_FlyTime
 jne PRG008_B072
 LDA #.lobyte($06)
PRG008_B072:
 LDY Player_YVel
 jmi PRG008_B079
 clc
 adc #.lobyte($03)
PRG008_B079:
 clc
 adc Temp_Var1
 TAY
 LDA Player_TailWagFlyFrames,Y
 STA Player_Frame
PRG008_B082:
 LDA Player_FlyTime
 ORA Player_WagCount
 jeq PRG008_B09F
 LDY #.lobyte(-1)
 LDA Player_XVel
 jpl PRG008_B095
 LDY #.lobyte(1)
 JSR Negate
PRG008_B095:
 CMP #.lobyte(PLAYER_TOPWALKSPEED)
 jmi PRG008_B09F
 TYA
 clc
 adc Player_XVel
 STA Player_XVel
PRG008_B09F:
 RTS
Player_SoarJumpFallFrame:
 LDA Player_SandSink
 LSR A
 jcs PRG008_B0C5
 LDA Player_AllowAirJump
 jne PRG008_B0C5
 LDA Player_InAir
 jeq PRG008_B0C5
 LDA Player_IsDucking
 jne PRG008_B0C5
 LDA #.lobyte(PF_FASTJUMPBIG)
 LDY Player_FlyTime
 jne PRG008_B0C3
 LDA #.lobyte(PF_JUMPBIG)
 LDY Player_YVel
 jmi PRG008_B0C3
 LDA #.lobyte(PF_FALLBIG)
PRG008_B0C3:
 STA Player_Frame
PRG008_B0C5:
 RTS
Player_TailAttackAnim:
 LDA Pad_Holding
 AND #.lobyte(PAD_DOWN)
 jne PRG008_B109
 BIT Pad_Input
 jvc PRG008_B0E2
 LDA Player_TailAttack
 jne PRG008_B0E2
 LDA #.lobyte($12)
 STA Player_TailAttack
 LDA Sound_QLevel1
 ORA #.lobyte(SND_LEVELTAILWAG)
 STA Sound_QLevel1
PRG008_B0E2:
 LDA Player_TailAttack
 jeq PRG008_B109
 LSR A
 LSR A
 TAY
 LDA Player_InAir
 jeq PRG008_B0F3
 INY
 INY
 INY
 INY
 INY
PRG008_B0F3:
 LDA Player_TailAttackFrames,Y
 STA Player_Frame
 LDA Player_TailAttack
 CMP #.lobyte($0b)
 jeq PRG008_B103
 CMP #.lobyte($03)
 jne PRG008_B109
PRG008_B103:
 LDA Player_FlipBits
 EOR #.lobyte(SPR_HFLIP)
 STA Player_FlipBits
PRG008_B109:
 RTS
Player_ShootAnim:
 LDA Player_FireCount
 jeq PRG008_B11E
 LSR A
 LSR A
 LDY Player_InAir
 jeq PRG008_B118
 clc
 adc #.lobyte((Player_FireInAir - Player_FireOnGround))
PRG008_B118:
 TAY
 LDA Player_FireOnGround,Y
 STA Player_Frame
PRG008_B11E:
 RTS
Player_ApplyXVelocity:
 LDX #.lobyte($00)
 LDY #.lobyte(PLAYER_MAXSPEED)
 LDA Player_XVel
 jpl PRG008_BFAC
 LDY #.lobyte(-PLAYER_MAXSPEED)
 eor #$ff
 clc
 adc #1
PRG008_BFAC:
 STA Temp_Var16
 CMP #.lobyte(PLAYER_MAXSPEED)
 jmi Player_ApplyVelocity
 STY Player_XVel
Player_ApplyVelocity:
 LDA Player_XVel,X
 CPX #.lobyte($00)
 jne PRG008_BFBE
 clc
 adc Player_XVelAdj
PRG008_BFBE:
 PHA
 ASL A
 ASL A
 ASL A
 ASL A
 STA Temp_Var12
 LDY #.lobyte($00)
 PLA
 LSR A
 LSR A
 LSR A
 LSR A
 CMP #.lobyte($08)
 jcc PRG008_BFD3
 DEY
 ORA #.lobyte($F0)
PRG008_BFD3:
 STA Temp_Var11
 STY Temp_Var13
 LDA Player_XVelFrac,X
 clc
 adc Temp_Var12
 STA Player_XVelFrac,X
 LDA Player_X,X
 ADC Temp_Var11
 STA Player_X,X
 LDA Player_XHi,X
 ADC Temp_Var13
 STA Player_XHi,X
 RTS
Player_ApplyYVelocity:
 LDA Player_YVel
 jmi PRG008_BFF9
 CMP #.lobyte(FALLRATE_MAX)
 jmi PRG008_BFF9
 LDA #.lobyte(FALLRATE_MAX)
 STA Player_YVel
PRG008_BFF9:
 LDX #.lobyte((Player_YVel - Player_XVel))
 JSR Player_ApplyVelocity
 RTS
PowerUp_Ability:
 .byte $00,$00,$00,$01,$02,$01,$02
Level_MinTileUWByQuad:
 .byte $ff,$ff,$ff,$da,$ff,$ff,$ff,$da,$ff,$ff,$ff,$c1,$ff,$ff,$ff,$da,$ff,$ff,$ff,$da,$02,$3f,$8a,$c0,$ff,$ff,$ff,$da,$ff,$ff,$8a,$da,$ff,$ff,$ff,$da,$ff,$ff,$ff,$da,$ff,$ff,$ff,$da,$ff,$ff,$ff,$da,$ff,$ff,$ff,$da,$ff,$ff,$ff,$c1,$30,$16,$2a,$2a,$2a,$17,$27,$36
Negate: eor #$ff
 clc
 adc #1
 rts
Level_SetPlayerPUpPal: rts ; Actual queued palette is composed by the port renderer.
Player_Draw29: rts ; Main renderer owns all OAM; no competing native draw pass.
Player_WaterSplash: rts ; The port emits the water sound/effect at its native transition.
Player_GetTileAndSlope: lda #0 ; SMB flat-terrain probe adapter; no source slopes exist here.
 clc
 rts
.endscope
.popseg
