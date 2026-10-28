; Independent successor, shared host integration not yet admitted.
RcInkPtr=$5c4c
RcInkChr=$5c4e
RcCopyLeft=$5c4f
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
 stx RcPose
 lda RcVariant
 beq Alex
 lda RcV1BodyPage,x
 sta SmChrBank
 lda RcV1InkPage,x
 sta RcInkChr
 lda PlayerFacingDir
 cmp #2
 beq RyanLeft
 lda RcV1PoseRLo,x
 sta SmPosePtr
 lda RcV1PoseRHi,x
 sta SmPosePtr+1
 lda RcV1InkRLo,x
 sta RcInkPtr
 lda RcV1InkRHi,x
 bne InkHi
RyanLeft:
 lda RcV1PoseLLo,x
 sta SmPosePtr
 lda RcV1PoseLHi,x
 sta SmPosePtr+1
 lda RcV1InkLLo,x
 sta RcInkPtr
 lda RcV1InkLHi,x
 bne InkHi
Alex:
 lda RcV0BodyPage,x
 sta SmChrBank
 lda RcV0InkPage,x
 sta RcInkChr
 lda PlayerFacingDir
 cmp #2
 beq AlexLeft
 lda RcV0PoseRLo,x
 sta SmPosePtr
 lda RcV0PoseRHi,x
 sta SmPosePtr+1
 lda RcV0InkRLo,x
 sta RcInkPtr
 lda RcV0InkRHi,x
 bne InkHi
AlexLeft:
 lda RcV0PoseLLo,x
 sta SmPosePtr
 lda RcV0PoseLHi,x
 sta SmPosePtr+1
 lda RcV0InkLLo,x
 sta RcInkPtr
 lda RcV0InkLHi,x
InkHi:
 sta RcInkPtr+1
 lda PlayerOutlinesOff
 bne Ready
 ; The shared buffer is129B; source maximum is14parts/57B.
 ; Invalidating all cache keys prevents a later legacy owner using stale ink.
 lda #0
 sta OutlineSourceHi
 ldx #3
Invalidate:
 sta OutlineTinyHi,x
 dex
 bpl Invalidate
 lda SmPosePtr
 sta R0
 lda SmPosePtr+1
 sta R1
 ldx #1
 jsr Copy
 lda RcInkPtr
 sta R0
 lda RcInkPtr+1
 sta R1
 jsr Copy
 dex
 stx OutlinePoseBuffer
 lda #<OutlinePoseBuffer
 sta SmPosePtr
 lda #>OutlinePoseBuffer
 sta SmPosePtr+1
Ready:
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 rts
Copy:
 ldy #0
 lda (R0),y
 sta RcCopyLeft
Loop:
 iny
 lda (R0),y
 sta OutlinePoseBuffer,x
 inx
 dec RcCopyLeft
 bne Loop
 rts
.endproc
.proc RcPublish
 ; A single source pose owns two1KB windows; never remap world/effect2/3.
 lda SmChrBank
 ldy #0
 jsr Window
 lda PlayerOutlinesOff
 bne Done
 lda RcInkChr
 ldy #1
 jsr Window
Done:
 lda #1
 sta X5WideChrActive
 rts
Window:
 sta RcPaletteValue
 cmp CurrentCHRBank,y
 bne Changed
 lda X5ChrMode,y
 cmp #$82
 beq Return
Changed:
 lda RcPaletteValue
 sta CurrentCHRBank,y
 lda #$82
 sta X5ChrMode,y
 lda #1
 sta ReloadCHRBank
Return:
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
 ; Pal2 at3F19 remains entirely owned by native enemies/powerups.
 lda StarInvincibleTimer
 ora GuestPowerupActive
 beq Ordinary
 lda #0
 sta RcPalette
 rts
Ordinary:
 lda RcPalette
 bne Done
 ldx VRAM_Buffer1_Offset
 cpx #78                     ;6B command + terminator fits84B queue.
 bcs Done
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$11
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 lda #$30                    ; native source white/skin/blue classes
 sta VRAM_Buffer1+3,x
 lda #$26
 sta VRAM_Buffer1+4,x
 lda #$11
 sta VRAM_Buffer1+5,x
 txa
 clc
 adc #6
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
 lda #$23
 sta VRAM_Buffer1+1,x
 lda #4
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
