.pushseg
.segment "FINAL_FANTASY_CORE"
.export FfGraphics,FfGraphicsBank,FfRenderChunk,FfPublishChunk,FfDraw,FfPortrait
.export FfPalettePointer,FfVisible
.export FfSetPose,FfEffectPalettePointer
; Rendering is an explicit chunk iterator; no complete source part is dropped.
; Body normal/default uses chunk0. When shadows enabled iterate remaining ink
; chunks too. Effects require every chunk. Caller adds signed FfRenderYOffset
; to genuine object Y with carry/high propagation before the real host draw.
; Render scratch: R0/R1 source->output pointer,R2 chunkcount,R3 format,R4 cursor,
; R5 source count,R6 output byte count,R7 packed part; all transient outputs.
; FfSlot = requested1right/2left; FfTemp2 = physical sprite window0..3.
.proc FfGraphicsBank
 BankPRGC #<.bank(FfArtStart)
 rts
.endproc
.proc FfGraphics
 jsr FfEnsure
 lda #0
 sta Player_SprAttrib          ; own records carry facing/palette, front priority.
 lda Player_Rel_XPos
 sta Player_Pos_ForScroll
 lda FfHurt
 and #4
 jne Hide
 lda #18
 ldx MmDeathFlag
 bne Pose
 lda #16
 ldx FfHurt
 bne Pose
 lda FfAction
 cmp #1
 bne Magic
 lda FfAge
 ldx #6
Divide:cmp #6
 bcc Attack
 sec
 sbc #6
 inx
 bne Divide
Attack:txa
 bne Pose
Magic:
 ldx #11
 cmp #2
 beq Action
 ldx #14
 cmp #3
 beq Action
 lda Player_State
 beq Ground
 lda FfJump
 beq Fall
 lda #13
 bne Pose
Fall:lda #15
 bne Pose
Ground:
 lda #17
 ldx RgCrouch
 bne Pose
 lda #1
 ldx Player_X_Speed
 beq Pose
 lda FfWalk
 bne Pose
 lda #2
 bne Pose
Action:txa
Pose:
::FfSetPose:
 cmp #1
 bcc Hide
 cmp #19
 bcs Hide
 sta FfPose
 sec
 sbc #1
 sta FfTemp
 lda FfVariant
 cmp #4
 bcs Hide
 tax
 lda Offset,x
Tier:
 ldx FfPower
 cpx #2
 bcc Base
 clc
 adc #18
Base:clc
 adc FfTemp
 pha
 lda PlayerFacingDir
 sta FfSlot
 pla
 ldx #0
 ldy #0
 jsr FfRenderChunk
 bcc Hide
 lda #<FfRenderBuffer
 sta SmPosePtr
 lda #>FfRenderBuffer
 sta SmPosePtr+1
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 rts
Hide:lda #0
 sta ObjectMetasprite
 rts
Offset:.byte 0,36,72,108
.endproc
.proc FfVisible
 lda FfHurt
 and #4
 bne No
 sec
 rts
No:clc
 rts
.endproc
; A=entry0..157, X=chunk0..,Y=CHRwindow0..3. Cclear rejects unsupported
; input. Cset includes empty optional-ink chunks when shadows are disabled.
.proc FfRenderChunk
 cmp #158
 jcs Empty
 cpy #4
 jcs Empty
 pha
 lda FfSlot
 cmp #3
 pla
 jcs Empty
 sty FfTemp2
 stx FfTemp
 pha
 jsr FfGraphicsBank
 pla
 tax
 lda FfEntryRecord,x
 tax
 lda FfRecordLo,x
 sta R0
 lda FfRecordHi,x
 sta R1
 ldy #0
 lda (R0),y
 sta R3                        ; bit7 compressed body; low5relativeCHRpage.
 and #31
 sta FfRenderPage
 clc
 adc #<FF_FIRST_CHR
 sta SmChrBank
 iny
 lda (R0),y
 sta R2
 cmp FfTemp
 jcc Empty
 jeq Empty
 iny
Find:
 lda FfTemp
 beq Found
 lda (R0),y
 sta R5
 iny
 bit R3
 bmi BodySkip
 iny
 iny
 lda R5
 clc
 adc R5
 adc R5
 bne Skip
BodySkip:lda R5
 asl
Skip:clc
 sty R4
 adc R4
 tay
 dec FfTemp
 bne Find
Found:
 lda (R0),y
 sta R5
 iny
 lda #0
 sta FfRenderYOffset
 sta FfRenderYOffset+1
 sta R6
 bit R3
 bmi Part
 lda (R0),y
 sec
 sbc #1                        ; actual NES OAM Y is one less than display Y.
 sta FfRenderYOffset
 iny
 lda (R0),y
 sbc #0
 sta FfRenderYOffset+1
 iny
Part:
 lda (R0),y
 sta R7
 iny
 bit R3
 bmi BodyXY
 lda (R0),y
 sta FfRectX
 iny
 lda (R0),y
 sta FfRectY
 iny
 jmp Admit
BodyXY:
 lda (R0),y
 pha
 and #7
 asl
 asl
 asl
 sec
 sbc #16                       ; sourcefootX+8 relative native PlayerX.
 sta FfRectX
 pla
 and #$38
 asl
 sec
 sbc #13                       ; sourcefootY+32, minus actual OAM's+1.
 sta FfRectY
 iny
Admit:
 lda R7
 and #32
 beq Emit
 lda PlayerOutlinesOff
 bne Next                      ; exact original black pixels, defaultOFF.
Emit:
 ldx R6
 lda R7
 and #31
 asl
 sta FfRenderBuffer+1,x
 lda FfTemp2
 .repeat 6
 asl
 .endrepeat
 ora FfRenderBuffer+1,x
 sta FfRenderBuffer+1,x
 lda R7
 asl
 rol
 rol
 and #3
 sta FfRenderBuffer+2,x
 lda R7
 and #32
 beq Face
 lda #3                        ; real foreground black, no hardware-priority20.
 sta FfRenderBuffer+2,x
Face:
 lda FfSlot
 cmp #2
 bne Coordinates
 lda FfRenderBuffer+2,x
 ora #$40
 sta FfRenderBuffer+2,x
 bit R3
 bmi BodyLeft
 lda #$f8
 bne Mirror
BodyLeft:lda #8
Mirror:sec
 sbc FfRectX
 sta FfRectX
Coordinates:
 lda FfRectY
 sta FfRenderBuffer+3,x
 lda FfRectX
 sta FfRenderBuffer+4,x
 txa
 clc
 adc #4
 sta R6
Next:dec R5
 jne Part
 lda R6
 sta FfRenderBuffer
 lda #<FfRenderBuffer
 sta R0
 lda #>FfRenderBuffer
 sta R1
 sec
 rts
Empty:
 lda #0
 sta FfRenderBuffer
 clc
 rts
.endproc
; Actual complete physical page arithmetic crosses756..787 at768 correctly.
; Must publish the same chunk immediately with its real OAM epoch.
.proc FfPublishChunk
 lda FfRenderPage
 clc
 adc #<FF_FIRST_CHR
 ldx #>FF_FIRST_CHR
 bcc :+
 inx
:ldy FfTemp2
 jmp X5SetPhysicalChr           ; same A-bank62, genuine same-bank call.
.endproc
.proc FfDraw
 jmp FfPublishChunk
.endproc
.proc FfPortrait
 jsr FfEnsure
 lda #0
 sta Player_SprAttrib
 lda #1
 jmp FfSetPose
.endproc
; Actual legal action timing prevents Ice/Bolt coexistence (30prepare >27
; maximum non-Fire life). A contradictory external state is rejected.
; R0/R1 points four P2 colors; Cclear means no override or invalid coexistence.
.proc FfEffectPalettePointer
 jsr FfGraphicsBank
 lda #0
 sta FfTemp
 ldx #0
Loop:
 lda FfProjectile,x
 cmp #2
 bcc Next
 cmp #5
 bcs No
 cmp #4
 bne :+
 lda #3
:ldy FfTemp
 beq Found
 cmp FfTemp
 bne No
Found:sta FfTemp
Next:txa
 clc
 adc #12
 tax
 cpx #36
 bcc Loop
 lda FfTemp
 beq No
 cmp #2
 beq Bolt
 lda #<FfPaletteIce
 sta R0
 lda #>FfPaletteIce
 sta R1
 sec
 rts
Bolt:
 lda #<FfPaletteBolt
 sta R0
 lda #>FfPaletteBolt
 sta R1
 sec
 rts
No:clc
 rts
.endproc
; R0/R1 = actual16-byte role block in C93. Root compositor must preserve
; world actor palette ownership/Star/transform and acknowledge queue success.
; Bodypal0; Firepal1; sword OR non-Fire spellpal2; exactoptionalblackpal3.
.proc FfPalettePointer
 jsr FfGraphicsBank
 lda #<FfPaletteRed
 ldx FfVariant
 cpx #2
 bcc Selected
 lda #<FfPaletteBlue
Selected:sta R0
 lda #>FfPaletteRed
 cpx #2
 bcc :+
 lda #>FfPaletteBlue
:sta R1
 rts
.endproc
.popseg
.pushseg
.segment "FINAL_FANTASY_ART"
FfPaletteRed: .byte $0f,$16,$30,$36,$0f,$16,$26,$30,$0f,$0c,$1c,$2c,$0f,$0f,$0f,$0f
FfPaletteBlue:.byte $0f,$28,$18,$21,$0f,$16,$26,$30,$0f,$0c,$1c,$2c,$0f,$0f,$0f,$0f
FfPaletteIce: .byte $0f,$12,$21,$30
FfPaletteBolt:.byte $0f,$18,$28,$30
.popseg
