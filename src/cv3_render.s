.pushseg
.segment "CV3_CORE"
.proc Cv3GraphicsGate
 Cv3Gate Z2GraphicsGate
 jsr Cv3Ensure
 lda MmDeathFlag
 jeq Live
 ldx #10
 jmp Pose
Live:
 ldx #1
 lda Cv3HurtAge
 jeq Bat
 ldx #11
 jmp Pose
Bat:
 lda Cv3Variant
 cmp #3
 jne Climb
 lda Cv3Bat
 jeq Climb
 cmp #2
 jeq Flying
 lda Cv3BatTransform
 lsr
 lsr
 lsr
 cmp #6
 bcc :+
 lda #5
: tay
 ldx Transform,y
 jmp Pose
Flying:
 lda Cv3VxHi
 ora Cv3VxLo
 ora Cv3VyHi
 ora Cv3VyLo
 jeq RestBat
 lda FrameCounter
 lsr
 lsr
 and #1
 clc
 adc #21
 tax
 jmp Pose
RestBat:
 lda FrameCounter
 lsr
 lsr
 and #1
 clc
 adc #18
 tax
 jmp Pose
Climb:
 lda Cv3Climb
 jeq Attack
 lda Cv3AttackAge
 jeq ClimbIdle
 ldx #12
 lda Cv3AttackProfile
 cmp #3
 jeq CeilingAttack
 cmp #2
 jeq DownWallAttack
 lda Cv3AttackAge
 cmp #15
 jcs Pose
 cmp #2
 jcc Pose
 ldx #14
 jmp Pose
DownWallAttack:
 ldx #27
 lda Cv3AttackAge
 cmp #15
 jcs Pose
 cmp #2
 jcc Pose
 ldx #29
 jmp Pose
CeilingAttack:
 ldx #15
 lda Cv3AttackAge
 cmp #15
 jcs Pose
 cmp #2
 jcc Pose
 ldx #17
 jmp Pose
ClimbIdle:
 lda Cv3Climb
 cmp #3
 jeq Ceiling
 lda SavedJoypadBits
 and #Up_Dir|Down_Dir
 jeq WallStill
 lda FrameCounter
 lsr
 lsr
 and #1
 clc
 adc #12
 tax
 jmp Pose
WallStill:ldx #12
 jmp Pose
Ceiling:
 lda FrameCounter
 lsr
 lsr
 and #1
 clc
 adc #14
 tax
 jmp Pose
Attack:
 lda Cv3AttackAge
 jeq Ordinary
 lda Cv3AttackKind
 cmp #2
 jeq Spell
 lda Cv3Variant
 cmp #3
 jeq AlucardAttack
 lda Cv3AttackAge
 cmp #15
 jcs IdleAttack
 cmp #10
 jcs Windup
 ldx #13
 lda Cv3Variant
 cmp #1
 jne AttackCrouch
 ldx #34
 lda Cv3AttackAge
 cmp #3
 jcs AttackCrouch
 ldx #20
 jmp AttackCrouch
Spell:
 ldx #18
 lda Cv3Variant
 cmp #2
 jeq SyphaSpell
 lda Cv3AttackAge
 cmp #14
 jcs Pose
 ldx #19
 jmp Pose
SyphaSpell:
 ldx #26
 lda Cv3AttackAge
 cmp #18
 jcs Pose
 ldx #22
 jmp Pose
AlucardAttack:
 ldx #12
 lda Cv3AttackAge
 cmp #17
 jcs AttackCrouch
 inx
 cmp #9
 jcs AttackCrouch
 inx
 jmp AttackCrouch
IdleAttack:
 ldx #1
 lda Cv3AttackCrouch
 jeq Pose
 ldx #7
 jmp Pose
Windup:
 ldx #12
 lda Cv3Variant
 cmp #1
 jne AttackCrouch
 ldx #20
 lda Cv3AttackAge
 cmp #12
 jcs AttackCrouch
 ldx #34
AttackCrouch:
 lda Cv3AttackCrouch
 jeq Pose
 lda Cv3Variant
 cmp #3
 jeq AlucardCrouch
 cmp #2
 jeq SyphaCrouch
 cpx #34
 jeq GrantExtend
 ldx #35
 jmp Pose
GrantExtend:ldx #37
 jmp Pose
SyphaCrouch:
 inx
 inx
 jmp Pose
AlucardCrouch:
 txa
 clc
 adc #3
 tax
 jmp Pose
Ordinary:
 lda RgCrouch
 jeq Air
 ldx #7
 jmp Pose
Air:
 lda Player_State
 jeq Walk
 ldx #5
 jmp Pose
Walk:
 lda Cv3VxLo
 ora Cv3VxHi
 jeq Pose
 inc Cv3WalkTick
 lda Cv3WalkTick
 lsr
 lsr
 lsr
 and #3
 tay
 ldx WalkFrames,y
Pose:
 stx Cv3Pose
 jmp Cv3SetPose
WalkFrames:.byte 2,3,4,1
Transform:.byte 24,25,26,27,18,18
.endproc
.proc Cv3PortraitGate
 Cv3Gate Z2PortraitGate
 jsr Cv3Ensure
 lda #0
 sta Cv3LastPalette
 ldx #1
 jsr Cv3SetPose
 jmp Cv3PublishBody
.endproc
.proc Cv3SetPose
 lda Player_SprAttrib
 and #$fc
 sta Player_SprAttrib
 lda Cv3Variant
 cmp #3
 jeq Alucard
 BankPRGC #83
 lda Cv3Variant
 cmp #2
 jeq Sypha
 lda PlayerFacingDir
 cmp #2
 jeq GrantLeft
 lda Cv3V1PoseRLo-1,x
 sta SmPosePtr
 lda Cv3V1PoseRHi-1,x
 sta SmPosePtr+1
 lda Cv3V1ChrRLo-1,x
 sta SmChrBank
 lda Cv3V1ChrRUpper-1,x
 jmp Upper
GrantLeft:
 lda Cv3V1PoseLLo-1,x
 sta SmPosePtr
 lda Cv3V1PoseLHi-1,x
 sta SmPosePtr+1
 lda Cv3V1ChrLLo-1,x
 sta SmChrBank
 lda Cv3V1ChrLUpper-1,x
 jmp Upper
Sypha:
 lda PlayerFacingDir
 cmp #2
 jeq SyphaLeft
 lda Cv3V2PoseRLo-1,x
 sta SmPosePtr
 lda Cv3V2PoseRHi-1,x
 sta SmPosePtr+1
 lda Cv3V2ChrRLo-1,x
 sta SmChrBank
 lda Cv3V2ChrRUpper-1,x
 jmp Upper
SyphaLeft:
 lda Cv3V2PoseLLo-1,x
 sta SmPosePtr
 lda Cv3V2PoseLHi-1,x
 sta SmPosePtr+1
 lda Cv3V2ChrLLo-1,x
 sta SmChrBank
 lda Cv3V2ChrLUpper-1,x
 jmp Upper
Alucard:
 BankPRGC #85
 lda PlayerFacingDir
 cmp #2
 jeq AlucardLeft
 lda Cv3V3PoseRLo-1,x
 sta SmPosePtr
 lda Cv3V3PoseRHi-1,x
 sta SmPosePtr+1
 lda Cv3V3ChrRLo-1,x
 sta SmChrBank
 lda Cv3V3ChrRUpper-1,x
 jmp Upper
AlucardLeft:
 lda Cv3V3PoseLLo-1,x
 sta SmPosePtr
 lda Cv3V3PoseLHi-1,x
 sta SmPosePtr+1
 lda Cv3V3ChrLLo-1,x
 sta SmChrBank
 lda Cv3V3ChrLUpper-1,x
Upper:
 sta Cv3BodyChrUpper
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 jsr Cv3QueuePalette
 rts
.endproc
.proc Cv3PublishBody
 lda SmChrBank
 ldx Cv3BodyChrUpper
 ldy #0
 farcall X5SetPhysicalChr,jmp
.endproc
.proc Cv3QueuePalette
 lda Cv3LastPalette
 cmp Cv3Variant
 jeq Done
 ldx VRAM_Buffer1_Offset
 cpx #78 ; 6-byte palette command plus terminator must fit the 84-byte buffer.
 jcs Done
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$11
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 lda Cv3Variant
 sec
 sbc #1
 sta Cv3Temp
 asl
 clc
 adc Cv3Temp
 tay
 lda Palette,y
 sta VRAM_Buffer1+3,x
 lda Palette+1,y
 sta VRAM_Buffer1+4,x
 lda Palette+2,y
 sta VRAM_Buffer1+5,x
 txa
 clc
 adc #6
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 lda Cv3Variant
 sta Cv3LastPalette
Done:rts
Palette:.byte $08,$15,$38,$21,$11,$20,$0f,$15,$36
.endproc
.popseg

.pushseg
.segment "CV3_CORE"
.proc Cv3ForcePalette
 lda #0
 sta Cv3LastPalette
 jmp Cv3QueuePalette
.endproc
.popseg

