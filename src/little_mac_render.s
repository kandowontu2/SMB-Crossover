.pushseg
.segment "LM_CORE"
.proc LmGraphicsGate
 TnHotGate TnGraphics
 LmGate JnGraphicsDispatch
 jsr LmEnsure
 lda OperMode
 bne Live
 lda CrossoverMenuState
 cmp #2
 bne Live
 lda #160
 sta Player_Y_Position
Live:ldx #0
 lda MmDeathFlag
 beq Hurt
 lda MmDeathPit
 bne Hide
 lda MmDeathAge
 cmp #90
 bcs Hide
 ldx #7
 jmp Pose
Hurt:lda LmHurt
 beq Attack
 ldx #7
 jmp Pose
Attack:lda LmAttack
 beq Duck
 ldx #4
 lda LmSuper
 beq CrouchAttack
 ldx #5
CrouchAttack:
 lda RgCrouch
 beq Pose
 txa
 clc
 adc #4
 tax
 jmp Pose
Duck:lda RgCrouch
 beq Air
 ldx #3
 jmp Pose
Air:lda Player_State
 beq Walk
 ldx #6
 jmp Pose
Walk:lda Player_X_Speed
 beq Pose
 ldx #1
 lda LmWalk
 cmp #24
 bcc Pose
 ldx #2
Pose:stx LmPose
 jmp LmSetPose
Hide:lda #0
 sta ObjectMetasprite
 rts
.endproc
.proc LmPortraitGate
 LmGate NrPortrait
 jsr LmEnsure
 farcall MacRosterPortrait,jmp
.endproc
.proc LmSetPose
 farcall MacRosterSetPose,jmp
.endproc
.proc LmPublish
 lda SmChrBank
 ldx #2
 ldy #0
 farcall X5SetPhysicalChr
 lda #<704
 ldx #>704
 farcall X5SetSpecialChr,jmp
.endproc
.proc LmDrawGate
 TnHotGate TnDraw
 LmGate JnDrawDispatch
 BankPRGC #94
 jsr LmPublish
 lda #5
 sta LmSlot
Loop:ldx LmSlot
 jsr LmIsStar
 bcc Next
 lda #0
 sta EnemyMetasprite,x
 lda #<LmStar
 sta R0
 lda #>LmStar
 sta R1
 lda Enemy_X_Position,x
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda Enemy_PageLoc,x
 sbc ScreenLeft_PageLoc
 sta R5
 lda Enemy_Y_Position,x
 clc
 adc #8
 sta R6
 lda #1
 sta R7
 lda #0
 sta R3
 farcall MetaspriteRenderLoop
Next:dec LmSlot
 bpl Loop
 rts
.endproc
 .proc LmForcePalette
 farcall MacRosterForcePalette,jmp
.endproc
.proc LmQueuePalette
 farcall MacRosterQueuePalette,jmp
.endproc
.proc LmUiGate
 LmGate NrUi
 lda #0
 sta InvHudActive
 sta InvDirty
 lda GameEngineSubroutine
 cmp #8
 bne Done
 lda LmDirty
 beq Done
 ldx VRAM_Buffer1_Offset
 cpx #70 ; Fourteen command bytes plus terminator fit.
 bcs Done
 lda #$20
 sta VRAM_Buffer1,x
 lda #4
 sta VRAM_Buffer1+1,x
 lda #11
 sta VRAM_Buffer1+2,x
 lda #$11
 sta VRAM_Buffer1+3,x
 lda #$19
 sta VRAM_Buffer1+4,x
 lda LmHealth
 jsr Decimal
 sta VRAM_Buffer1+6,x
 tya
 sta VRAM_Buffer1+5,x
 lda #$24
 sta VRAM_Buffer1+7,x
 lda #$11
 sta VRAM_Buffer1+8,x
 lda LmHearts
 jsr Decimal
 sta VRAM_Buffer1+10,x
 tya
 sta VRAM_Buffer1+9,x
 lda #$24
 sta VRAM_Buffer1+11,x
 lda #$1c
 sta VRAM_Buffer1+12,x
 lda LmStars
 sta VRAM_Buffer1+13,x
 txa
 clc
 adc #14
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 sta LmDirty
Done:rts
Decimal:ldy #0
Loop:cmp #10
 bcc Finish
 sec
 sbc #10
 iny
 bne Loop
Finish:rts
.endproc
.popseg
