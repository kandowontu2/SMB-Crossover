.export RcGraphics,RcPortrait,RcGraphicsBank,RcDraw,RcUi,RcStatusName,RcColors
.export RcSetPose,RcPublish,RcQueuePalette
.pushseg
.segment "RIVER_CITY_CORE"
.proc RcGraphics
 jsr RcEnsure
 lda Player_Rel_XPos
 sta Player_Pos_ForScroll
 lda Player_SprAttrib
 and #$fc
 sta Player_SprAttrib
 ldx #0
 lda MmDeathFlag
 beq Live
 lda MmDeathPit
 jne Hide
 lda MmDeathAge
 cmp #90
 jcs Hide
 ldx #6
 bne Set
Live:
 lda RcHurtMove
 beq Carry
 ldx #6
 bne Set
Carry:
 lda RcCarrySlot
 cmp #$ff
 beq Attack
 ldx #15
 bne Set
Attack:
 lda RcAttack
 beq Duck
 ldy RcAttackKind
 cpy #4
 bne AirAttack
 ldx #16
 bne Set
AirAttack:
 cpy #3
 bne GroundAttack
 ldx #17
 lda RcRun
 beq Set
 ldx #14
 bne Set
GroundAttack:
 ldx #8
 cpy #2
 bne Phase
 ldx #11
Phase:
 cmp #10
 bcs Set
 inx
 cmp #6
 bcs Set
 inx
 bne Set
Duck:
 lda RgCrouch
 beq Air
 ldx #5
 bne Set
Air:
 lda Player_State
 beq Walk
 ldx #4
 bne Set
Walk:
 lda Player_X_Speed
 beq Set
 lda RcClock
 lsr
 lsr
 lsr
 and #3
 tay
 lda WalkPoses,y
 tax
 lda RcRun
 beq Set
 lda RcClock
 and #4
 beq Stand
 ldx #3
 bne Set
Stand:ldx #0
Set:
 stx RcPose
 jmp RcSetPose
Hide:
 lda #0
 sta ObjectMetasprite
 rts
WalkPoses:.byte 0,1,0,2
.endproc
.proc RcPortrait
 jsr RcEnsure
 ldx #0
 jsr RcSetPose
 jsr RcPublish
 jmp RcColors
.endproc
.proc RcGraphicsBank
 BankPRGC #.bank(RcArtStart)
 rts
.endproc
.proc RcSetPose
 BankPRGC #.bank(RcArtStart)
 cpx #18
 bcc Valid
 ldx #0
Valid:
 lda RcVariant
 beq Alex
 lda PlayerFacingDir
 cmp #2
 beq RyanLeft
 lda RcV1PoseRLo,x
 sta SmPosePtr
 lda RcV1PoseRHi,x
 jmp RyanHi
RyanLeft:
 lda RcV1PoseLLo,x
 sta SmPosePtr
 lda RcV1PoseLHi,x
RyanHi:
 sta SmPosePtr+1
 lda #<(RC_FIRST_CHR+4)
 bne Chr
Alex:
 lda PlayerFacingDir
 cmp #2
 beq AlexLeft
 lda RcV0PoseRLo,x
 sta SmPosePtr
 lda RcV0PoseRHi,x
 jmp AlexHi
AlexLeft:
 lda RcV0PoseLLo,x
 sta SmPosePtr
 lda RcV0PoseLHi,x
AlexHi:
 sta SmPosePtr+1
 lda #<RC_FIRST_CHR
Chr:
 sta SmChrBank
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 rts
.endproc
.proc RcPublish
 ; Four body windows, same source epoch as SmPosePtr. No reload when unchanged.
 lda RcVariant
 asl
 asl
 clc
 adc #<RC_FIRST_CHR
 sta RcPaletteValue
 ldy #0
Loop:
 lda CurrentCHRBank,y
 cmp RcPaletteValue
 bne Changed
 lda X5ChrMode,y
 cmp #($80|>RC_FIRST_CHR)
 beq Next
Changed:
 lda RcPaletteValue
 sta CurrentCHRBank,y
 lda #($80|>RC_FIRST_CHR)
 sta X5ChrMode,y
 lda #1
 sta ReloadCHRBank
Next:
 inc RcPaletteValue
 iny
 cpy #4
 bne Loop
 lda #1
 sta X5WideChrActive
 rts
.endproc
.proc RcDraw
 jmp RcPublish
.endproc
.proc RcColors
 lda #0
 sta RcPalette
 jmp RcQueuePalette
.endproc
.proc RcQueuePalette
 lda RcPalette
 bne Done
 ldx VRAM_Buffer1_Offset
 cpx #72                      ; two6B runs plus terminator fit84B native queue
 bcs Done
 lda #$3f
 sta VRAM_Buffer1,x
 sta VRAM_Buffer1+6,x
 lda #$11
 sta VRAM_Buffer1+1,x
 lda #$19
 sta VRAM_Buffer1+7,x
 lda #3
 sta VRAM_Buffer1+2,x
 sta VRAM_Buffer1+8,x
 lda #$0f
 sta VRAM_Buffer1+3,x
 sta VRAM_Buffer1+9,x
 lda #$26
 sta VRAM_Buffer1+4,x
 lda #$11                     ; authenticated native blue: E9FD palette1[2]
 sta VRAM_Buffer1+10,x
 lda #$30
 sta VRAM_Buffer1+5,x
 sta VRAM_Buffer1+11,x
 txa
 clc
 adc #12
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 inc RcPalette
Done:rts
.endproc
.proc RcUi
 jsr RcQueuePalette
 lda GameEngineSubroutine
 cmp #8
 bne Done
 lda RcHudDirty
 beq Done
 ldx VRAM_Buffer1_Offset
 cpx #76                      ;7B packet + terminator, no unbounded appends
 bcs Done
 lda #$20
 sta VRAM_Buffer1,x
 lda #4
 sta VRAM_Buffer1+1,x
 sta VRAM_Buffer1+2,x
 lda #$11                     ; existing native font H/P, no new font or lease
 sta VRAM_Buffer1+3,x
 lda #$19
 sta VRAM_Buffer1+4,x
 ldy RcVariant
 lda RcHealth,y
 ldy #0
Tens:
 cmp #10
 bcc Digits
 sec
 sbc #10
 iny
 bne Tens
Digits:
 sta VRAM_Buffer1+6,x
 tya
 sta VRAM_Buffer1+5,x
 txa
 clc
 adc #7
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 sta RcHudDirty
Done:rts
.endproc
.proc RcStatusName
 phy
 ldy #6                       ; native status packet reserves seven cells
 lda RcVariant
 beq Alex
Ryan:
 lda RyanText,y
 sta VRAM_Buffer1+11,y
 dey
 bpl Ryan
 jmp Done
Alex:
 lda AlexText,y
 sta VRAM_Buffer1+11,y
 dey
 bpl Alex
Done:
 ply
 lda #0
 rts
AlexText:.byte "ALEX    "
RyanText:.byte "RYAN    "
.endproc
.popseg
