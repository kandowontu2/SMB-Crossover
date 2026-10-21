; Source homing steering: project the growing acceleration onto the normalized
; target vector, then let RemainingWeapons apply source friction and caps.
.pushseg
.segment "XG_SOPHIA_GFX"
.proc SophiaHomingVector
  ldx AvSlot
  ; 3000 source units/s^2, converted to NES Q8.8: round(n*16/9).
  ; Keep growing after two seconds, using the existing per-missile bytes.
  lda SsAngleHi,x
  cmp #$7f
  beq ForceReady
  clc
  lda SsHidden,x
  adc #1
  sta SsHidden,x
  lda SsAngleHi,x
  adc #0
  sta SsAngleHi,x
  clc
  lda SsAngleLo,x
  adc #7
  cmp #9
  bcc Remainder
  sbc #9
  inc SsHidden,x
  bne Remainder
  inc SsAngleHi,x
Remainder:
  sta SsAngleLo,x
ForceReady:
  lda SsHidden,x
  sta AvTmp2
  lda SsAngleHi,x
  sta AvSavedY
::SophiaHomingProject:
  ldx AvSlot
  ldy SsMode,x
  clc
  lda Enemy_X_Position,y
  adc #8
  sta R0
  lda Enemy_PageLoc,y
  adc #0
  sta R1
  sec
  lda R0
  sbc RgShotX,x
  sta R0
  lda R1
  sbc RgShotPage,x
  sta R1
  and #$80
  sta R5
  beq DeltaY
  sec
  lda #0
  sbc R0
  sta R0
  lda #0
  sbc R1
  sta R1
DeltaY:
  clc
  lda Enemy_Y_Position,y
  adc #16
  sta R2
  lda Enemy_Y_HighPos,y
  adc #0
  sta R3
  sec
  lda R2
  sbc RgShotY,x
  sta R2
  lda R3
  sbc RgShotYHigh,x
  sta R3
  and #$80
  sta R6
  beq ChooseMajor
  sec
  lda #0
  sbc R2
  sta R2
  lda #0
  sbc R3
  sta R3
ChooseMajor:
  lda #1
  sta R7
  lda R1
  cmp R3
  bcc Divide
  bne MajorX
  lda R0
  cmp R2
  bcc Divide
MajorX:
  lda #0
  sta R7
  lda R0
  pha
  lda R1
  pha
  lda R2
  sta R0
  lda R3
  sta R1
  pla
  sta R3
  pla
  sta R2
Divide:
  lda #0
  sta R4
  lda R2
  ora R3
  beq Project
  lda R0
  cmp R2
  bne Ratio
  lda R1
  cmp R3
  bne Ratio
  lda #255
  sta R4
  bne Project
Ratio:
  jmp ::SophiaRatioSelect
  .res 39,$ea               ; Retain original42-byte Ratio..Project footprint.
Project:
  ldy R4
  lda Major,y
  sta MmDamage
  lda Minor,y
  sta MmTemp
  lda MmDamage
  bne ScaledMajor
  lda AvTmp2                   ; Axis-aligned cosine is exactly1.
  sta MmMul+1
  lda AvSavedY
  sta MmMul+2
  jmp MajorReady
ScaledMajor:
  jsr Multiply
MajorReady:
  lda MmMul+1
  sta AvTmp
  lda MmMul+2
  sta AvFrictionKind
  lda MmTemp
  jsr Multiply
  lda R7
  beq MajorIsX
  lda MmMul+1
  sta R0
  lda MmMul+2
  sta R1
  lda AvTmp
  sta R2
  lda AvFrictionKind
  sta R3
  jmp Components
MajorIsX:
  lda AvTmp
  sta R0
  lda AvFrictionKind
  sta R1
  lda MmMul+1
  sta R2
  lda MmMul+2
  sta R3
Components:
  ; A projected impulse >=8 pixels/frame always reaches the source speed
  ; clamp, even against the previous capped velocity. Bound it before adding
  ; so a long-lived missile cannot wrap the signed Q8.8 velocity.
  lda R1
  cmp #8
  bcc ClampY
  lda #8
  sta R1
  lda #0
  sta R0
ClampY:
  lda R3
  cmp #8
  bcc ApplyX
  lda #8
  sta R3
  lda #0
  sta R2
ApplyX:
  ldx AvSlot
  lda R5
  bmi Left
  clc
  lda RgShotVXLo,x
  adc R0
  sta RgShotVXLo,x
  lda RgShotVXHi,x
  adc R1
  sta RgShotVXHi,x
  jmp ApplyY
Left:
  sec
  lda RgShotVXLo,x
  sbc R0
  sta RgShotVXLo,x
  lda RgShotVXHi,x
  sbc R1
  sta RgShotVXHi,x
ApplyY:
  lda R6
  bmi Up
  clc
  lda RgShotVYLo,x
  adc R2
  sta RgShotVYLo,x
  lda RgShotVYHi,x
  adc R3
  sta RgShotVYHi,x
  rts
Up:
  sec
  lda RgShotVYLo,x
  sbc R2
  sta RgShotVYLo,x
  lda RgShotVYHi,x
  sbc R3
  sta RgShotVYHi,x
  rts
Multiply:
  sta R0
  lda AvTmp2
  jsr SophiaByteProduct
  lda R3
  sta MmMul+1
  lda #0
  sta MmMul+2
  lda AvSavedY
  beq Multiplied
  jsr SophiaByteProduct
  clc
  lda MmMul+1
  adc R2
  sta MmMul+1
  lda R3
  adc #0
  sta MmMul+2
Multiplied:
  rts
.include "sophia_vectors.inc"
.endproc
.proc SophiaByteProduct
  ; Exact8x8 multiply: floor((a+b)^2/4)-floor((a-b)^2/4).
  ; Both arguments have equal sum/difference parity, so truncations cancel.
  ; A=value, R0=factor, returns R2/R3. No persistent RAM or bank call.
  sta R1
::SophiaByteProductOperands:
  lda R1
  clc
  adc R0
  tax
  bcs LargeSum
  lda QuarterLo,x
  sta R2
  lda QuarterHi,x
  sta R3
  jmp Difference
LargeSum:
  lda QuarterLo+256,x
  sta R2
  lda QuarterHi+256,x
  sta R3
Difference:
  sec
  lda R1
  sbc R0
  bcs Magnitude
  eor #$ff
  adc #1
Magnitude:
  tax
  sec
  lda R2
  sbc QuarterLo,x
  sta R2
  lda R3
  sbc QuarterHi,x
  sta R3
  rts
QuarterLo:
  .repeat 512,I
    .byte .lobyte((I*I)/4)
  .endrepeat
QuarterHi:
  .repeat 512,I
    .byte .hibyte((I*I)/4)
  .endrepeat
.endproc
.proc SophiaFindTarget
  lda #$ff
  sta AvSavedX
  sta R5
  sta R6
  sta R7
  ldx #5
Candidate:
  stx AvSavedY
  lda Enemy_Flag,x
  jeq Next
  jmi Next
  lda Enemy_State,x
  and #$20
  jne Next
  lda EnemyOffscrBitsMasked,x
  jne Next
  lda Enemy_ID,x
  cmp #$15
  jcc State
  cmp #Bowser
  jeq State
  cmp #BulletBill_CannonVar
  jne Next
State:
  cmp #Goomba
  bne :+
    lda Enemy_State,x
    cmp #2
    jcs Next
  :
  clc
  lda Enemy_X_Position,x
  adc #8
  sta R0
  lda Enemy_PageLoc,x
  adc #0
  sta R1
  ldx AvSlot
  sec
  lda R0
  sbc RgShotX,x
  sta R0
  lda R1
  sbc RgShotPage,x
  sta R1
  jsr Square
  lda R2
  sta AvTmp
  lda R3
  sta AvTmp2
  lda R4
  sta AvFrictionNegative
  ldy AvSavedY
  clc
  lda Enemy_Y_Position,y
  adc #16
  sta R0
  lda Enemy_Y_HighPos,y
  adc #0
  sta R1
  sec
  lda R0
  sbc RgShotY,x
  sta R0
  lda R1
  sbc RgShotYHigh,x
  sta R1
  jsr Square
  clc
  lda R2
  adc AvTmp
  sta R2
  lda R3
  adc AvTmp2
  sta R3
  lda R4
  adc AvFrictionNegative
  sta R4
  cmp R7
  bcc Closer
  bne Next
  lda R3
  cmp R6
  bcc Closer
  bne Next
  lda R2
  cmp R5
  bcs Next
Closer:
  lda R2
  sta R5
  lda R3
  sta R6
  lda R4
  sta R7
  lda AvSavedY
  sta AvSavedX
Next:
  ldx AvSavedY
  dex
  jpl Candidate
  lda AvSavedX
  cmp #$ff
  beq Missing
  sec
  rts
Missing:
  clc
  rts
Square:
  lda R1
  bpl Magnitude
  sec
  lda #0
  sbc R0
  sta R0
  lda #0
  sbc R1
  sta R1
Magnitude:
  lda R0
  sta MmMul
  sta MmTemp
  lda R1
  sta MmMul+1
  sta MmDamage
  lda #0
  sta MmMul+2
  sta R2
  sta R3
  sta R4
SquareBit:
  lda MmTemp
  ora MmDamage
  beq Squared
  lsr MmDamage
  ror MmTemp
  bcc NoAdd
  clc
  lda R2
  adc MmMul
  sta R2
  lda R3
  adc MmMul+1
  sta R3
  lda R4
  adc MmMul+2
  sta R4
NoAdd:
  asl MmMul
  rol MmMul+1
  rol MmMul+2
  jmp SquareBit
Squared:
  rts
.endproc

; Exact short-magnitude path for the original eight-bit ratio. Entered by JMP;
; no stack, SRAM, lookup-table, force, target or physics-cadence changes.
.proc SophiaRatioSelect
  lda R4
  bne Wide                   ; Real Divide initializes quotient0.
  lda R1
  ora R3
  bne Wide
  lda R0
  cmp R2
  bcs Wide                   ; Includes zero divisor/equal/non-normal inputs.
  ldy #8
FastBit:
  asl                        ; Ninth bit remains in carry, not memory R1.
  bcs Subtract
  cmp R2
  bcc Below
Subtract:
  sbc R2                     ; Carry1 from ASL branch or successful CMP.
  sec                        ; Quotient bit1 even when low-byte SBC borrows.
  bcs Quotient
Below:
  clc
Quotient:
  rol R4
  dey
  bne FastBit
  sta R0
  lda #0
  sta R1                     ; Normalized remainder is strictly < major256.
  ldy R4
  beq PreserveV              ; No subtraction: original V is unchanged.
  clv                        ; Original high-byte SBC always produces0/V0.
PreserveV:
  lda R4
  lsr
  bcc LastBelow
  lda #0                     ; Original last subtraction leaves A=R1=0.
  beq Finish
LastBelow:
  lda R0                     ; Original last below leaves A=remainder.
Finish:
  ldy #0                     ; Original DEY0 supplies N0/Z1.
  clc                        ; Starting quotient0 means final ROL carry0.
  jmp SophiaHomingVector::Project
Wide:
  ; Original full-width loop, instruction-for-instruction. Changed timing only.
  ldy #8
WideBit:
  asl R0
  rol R1
  lda R1
  cmp R3
  bcc WideBelow
  bne WideSubtract
  lda R0
  cmp R2
  bcc WideBelow
WideSubtract:
  sec
  lda R0
  sbc R2
  sta R0
  lda R1
  sbc R3
  sta R1
  sec
  bcs WideQuotient
WideBelow:
  clc
WideQuotient:
  rol R4
  dey
  bne WideBit
  jmp SophiaHomingVector::Project
.endproc
.popseg
