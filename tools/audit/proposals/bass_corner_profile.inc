; PRIVATE draft. The two public legacy entries keep their original spans.
; Current air/slide rows match the authenticated MegaMan timeline dimensions;
; the full ceiling sampler must still handle the half-pixel air head position.
.pushseg
.segment "BASS_PROFILE"
.proc BassTerrainAdder
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  bne Legacy
  lda RlVariant
  bne Legacy
  ldy #3
  jsr BassTerrainForm
  sec
  rts
Legacy:
  sec                          ; The original entering CMP #BASS matched.
  jmp KbLegacyExpandedCollisionAdder::Medium
.endproc
.proc BassTerrainBox
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  bne Legacy
  lda RlVariant
  bne Legacy
  ldy #12
  jsr BassTerrainForm
  sec
  rts
Legacy:
  sec
  jmp KbLegacyExpandedCollisionBox::Medium
.endproc
.proc BassTerrainForm
  lda GuestHurtTicks
  bne RestoreA                 ; takeDamage keeps the standing HRect.
  lda RgCrouch
  bne Slide
  lda Player_State
  beq RestoreA
  cmp #2
  bne Aim
  cpy #3
  bne Aim
  lda Player_BoundBoxCtrl
  cmp #12
  beq RestoreA                 ; real pre-BG published standing body.
Aim:
  lda RgShootPose
  beq Air
  lda SavedJoypadBits
  and #Up_Dir|Down_Dir
  bne RestoreA                 ; Air up/diagonal aim uses the24px HRect.
Air:
  iny                          ; Air/jumpShoot: row4/13, nominal28px.
RestoreA:
  lda RgCrouch                 ; Preserve the legacy A/N/Z and incoming V.
  rts
Slide:
  iny
  iny                          ; Authored slide: row5/14, nominal15px.
  lda RgCrouch
  rts
.endproc
.assert *-BassTerrainAdder<=160,error,"Bass profile sparse pool overflow"
.popseg

; Bass only. The existing saved A/P belongs to TnFastHeadGate.
.pushseg
.segment "BASS_HEAD_GATE"
 .proc BassHeadAdmission
 lda RlVariant
 bne Legacy
 lda #0
 sta SmCeilingHit
 lda GameEngineSubroutine
 cmp #8
 bne Legacy
 lda Player_Y_HighPos
 cmp #1
 bne Legacy
 lda Player_Y_Speed
 bpl Legacy
 lda MmVY+2
 bpl Legacy
 lda GuestHurtTicks
 ora RgCrouch
 bne Legacy
 pla
 plp
 farcall BassHeadProbe,jmp
Legacy:
 lda #CHARACTER_BASS
 jmp Z2HeadAdmission
.endproc
.popseg

.pushseg
.segment "BASS_CEILING"
.proc BassHeadProbe
 ; Sole real caller has already checked owner/lifecycle/upward eligibility.
 sty SmTemp
 lda Player_X_Position
 sta SmTempX
 lda Player_PageLoc
 sta SmTempPage
 jsr Probe
 bne Restore
 ; Exact authored head interval starts at X+1.25. Select its integer cell.
 lda #7
 ldx MmXFraction+1
 cpx #$c0
 bcc :+
 lda #6
:sta SmSlot
 sec
 lda SmTempX
 sbc SmSlot
 sta Player_X_Position
 lda SmTempPage
 sbc #0
 sta Player_PageLoc
 jsr Probe
 bne Restore
 ; Right edge is X+14.7499388 (stand) /14.749878 (air).
 lda #6
 ldx MmXFraction+1
 cpx #$40
 bcc Right
 bne Extra
 ldx MmXFraction
 ldy SmTemp
 cpy #37
 bne StandRight
 cpx #8
 bcc Right
 bcs Extra
StandRight:cpx #4
 bcc Right
Extra:lda #7
Right:clc
 adc SmTempX
 sta Player_X_Position
 lda SmTempPage
 adc #0
 sta Player_PageLoc
 jsr Probe
Restore:
 pha
 lda SmTempX
 sta Player_X_Position
 lda SmTempPage
 sta Player_PageLoc
 pla
 beq Done
 bcc Done
 pha
 ldy SmTemp
 sty SmSourceJumped
 ; Cell/effect R2/R3/R5/R6/R7 remains the actual successful sample.
 lda R2
 clc
 adc #48
 ldy SmTemp
 sec
 sbc BlockBuffer_Y_Adder,y
 sta SmTempY
 cpy #37
 bne Integer
 dec SmTempY
 lda #$50
 sta MmYFraction
 lda #$80
 bne Fine
Integer:
 lda #12
 cpy #44
 bne :+
 lda #48
:sta MmYFraction
 lda #0
Fine:sta MmYFraction+1
 lda SmTempY
 sta Player_Y_Position
 lda #2
 sta SmCeilingHit
 lda #4
 sta R4
 ldx #0
 pla
Done:
 pha
 ldy SmTemp
 pla
 rts
Probe:
 ; 27.5px authored head uses origin+4.5, not rounded origin+4.
 lda #0
 sta SmSlot
 ldy SmTemp
 cpy #37
 bne Sample
 lda MmYFraction+1
 bpl Sample
 inc SmSlot
 inc Player_Y_Position
Sample:
 clc
 lda Player_X_Position
 adc #8
 and #$f0
 sta SmHeadX
 lda Player_PageLoc
 adc #0
 sta SmHeadPage
 jsr BlockBufferColli_Head
 pha
 lda SmSlot
 beq :+
 dec Player_Y_Position
:pla
 beq ProbeDone
 ; Coins/climbables preserve native pickup/transition ownership.
 cmp #$26
 beq Keep
 cmp #$c2
 beq Keep
 cmp #$c3
 beq Keep
 tax
 lda MTileAttribute,x
 and #MTILE_CLIMB
 bne Reload
 jsr BassPreviousHead
 bcc Reject
 ; Admit the proved vertical branch only if the previous horizontal HRect
 ; already overlaps this cell. True simultaneous corners retain side work.
 jsr BassPreviousSpan
 bcc Reject
 ldx #0
 lda R3
 sec
 rts
Reload:
Keep:ldx #0
 lda R3
 clc
ProbeDone:rts
Reject:
 lda #0
 ldx #0
 clc
 rts
.endproc

.proc BassPreviousHead
 sec
 lda MmYFraction
 sbc MmVY
 lda MmYFraction+1
 sbc MmVY+1
 pha
 lda Player_Y_Position
 sbc MmVY+2
 sta SmClearance
 bcs Crossed
 pla
 ldy SmTemp
 cpy #37
 bne :+
 cmp #$80
 bcc :+
 inc SmClearance
:lda SmClearance
 clc
 adc BlockBuffer_Y_Adder,y
 bcs Allow
 sta SmClearance
 lda R2
 clc
 adc #48
 bcs No
 cmp SmClearance
 bcc Allow
 beq Allow
No:clc
 rts
Crossed:pla
Allow:sec
 rts
.endproc

.proc BassPreviousSpan
 ; Q16 subtraction keeps the true fraction borrow before world comparison.
 sec
 lda MmXFraction
 sbc MmVX
 sta SmSourceJumped
 lda MmXFraction+1
 sbc MmVX+1
 sta SmClearance
 lda SmTempX
 sbc MmVX+2
 sta SmSlot
 ldx MmVX+2
 bmi Negative
 lda SmTempPage
 sbc #0
 jmp Page
Negative:lda SmTempPage
 sbc #$ff
Page:sta SmTempY
 ; Compute ceil(previous right edge), including the authored tiny epsilon.
 lda SmTemp
 cmp #37
 beq Air
 ldx #$fc
 bne AddFine
Air:ldx #$f8
AddFine:txa
 clc
 adc SmSourceJumped
 tay
 lda SmClearance
 adc #$bf
 tax
 lda #14
 adc SmSlot
 pha
 lda SmTempY
 adc #0
 sta SmSourceJumped
 ; Nonzero fractional result rounds the edge upward for strict comparison.
 txa
 bne Round
 tya
 beq Compare
Round:pla
 clc
 adc #1
 pha
 bcc Compare
 inc SmSourceJumped
Compare:pla
 tax
 lda SmSourceJumped
 cmp SmHeadPage
 bcc No
 bne Left
 cpx SmHeadX
 bcc No
 beq No
Left:
 ; floor(previous left edge) < integer cell right is the exact strict test.
 lda #1
 ldx SmClearance
 cpx #$c0
 bcc :+
 lda #2
:clc
 adc SmSlot
 tax
 lda SmTempY
 adc #0
 sta SmClearance
 lda SmHeadX
 clc
 adc #16
 sta SmSlot
 lda SmHeadPage
 adc #0
 cmp SmClearance
 bcc No
 bne Yes
 cpx SmSlot
 bcs No
Yes:sec
 rts
No:clc
 rts
.endproc

.proc BassAfterBG
 lda SmCeilingHit
 cmp #2
 bne Done
 lda #0
 sta SmCeilingHit
 sta MmVY+2
 sta Player_Y_Speed
 lda #$55
 sta MmVY
 lda #$d5
 sta MmVY+1
 ; Native brick/question effects may have overwritten the scalar velocity
 ; and fractional Y; groundAbove owns final separation and the source Q16.
 lda SmTempY
 sta Player_Y_Position
 ldy SmSourceJumped
 lda #12
 cpy #44
 bne :+
 lda #48
:cpy #37
 bne IntegerFine
 lda #$50
 sta MmYFraction
 lda #$80
 bne Fine
IntegerFine:sta MmYFraction
 lda #0
Fine:sta MmYFraction+1
 lda Square1SoundQueue
 ora #Sfx_Bump
 sta Square1SoundQueue
Done:rts
.endproc
.assert *-BassHeadProbe<=1024,error,"Bass ceiling pool overflow"
.popseg

.pushseg
.segment "BASS_POST"
.proc BassPostBGDispatch
 lda SelectedCharacter
 cmp #CHARACTER_BASS
 bne Legacy
 lda RlVariant
 bne Legacy
 lda SmCeilingHit
 cmp #2
 bne Legacy
 farcall BassAfterBG
 jsr RelativePlayerPosition
 ldx #0
 jmp BoundingBoxCore
Legacy:
 lda SelectedCharacter
 cmp #CHARACTER_SAMUS
 beq Handle
 cmp #CHARACTER_LINK
 bne Done
Handle:jsr Z2AfterBGDispatch
 jsr RelativePlayerPosition
 ldx #0
 jsr BoundingBoxCore
 lda SelectedCharacter
 cmp #CHARACTER_LINK
 bne Done
 lda Z2Variant
 beq Done
 jmp Z2OriginalBodyBox
Done:rts
.endproc
.popseg
