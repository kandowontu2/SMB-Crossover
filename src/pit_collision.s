; Pit can crouch in the air. Do not expand his body into a low ceiling when
; Down is released: the native side probes cannot separate that overlap.
.pushseg
.segment "SAMUS"
.proc PitCrouchUpdate
  lda SavedJoypadBits
  and #Down_Dir
  bne Crouch
  lda XgPitCrouchHeld
  beq Done
  jsr PitStandClearance
  beq Done
Crouch:
  lda #1
  sta RgCrouch
  lda #4
  sta CrouchingFlag
Done:
  lda RgCrouch
  sta XgPitCrouchHeld
  rts
.endproc

.proc PitStandClearance
  lda #0
  sta SmClearance
  lda Player_Y_HighPos
  cmp #1
  jne Return
  lda Player_X_Position
  sta SmTempX
  lda Player_PageLoc
  sta SmTempPage
  lda Player_Y_Position
  sta SmTempY
  ldx #3
Loop:
  stx SmTemp
  ; The native head probe adds (8,4). Sample the two horizontal edges of
  ; Pit's standing box at Y+8 and Y+16, inside the newly exposed head band.
  txa
  and #2
  asl
  clc
  adc #8
  adc SmTempY
  bcs Next
  cmp #32
  bcc Next
  cmp #240
  bcs Next
  sec
  sbc #4
  sta Player_Y_Position
  lda SmTemp
  and #1
  tay
  lda XOffsets,y
  clc
  adc SmTempX
  sta Player_X_Position
  lda SmTempPage
  cpy #0
  bne PositivePage
  ; CPY changes carry; recover the carry from the signed low-byte sum.
  lda SmTempX
  cmp #7
  lda SmTempPage
  sbc #0
  jmp Page
PositivePage:
  lda SmTempX
  cmp #250
  lda SmTempPage
  adc #0
Page:
  sta Player_PageLoc
  ldy #0
  jsr BlockBufferColli_Head
  beq Next
  jsr ChkForNonSolids
  beq Next
  cmp #$23
  beq Next
  inc SmClearance
  bne Restore
Next:
  ldx SmTemp
  dex
  bpl Loop
Restore:
  lda SmTempX
  sta Player_X_Position
  lda SmTempPage
  sta Player_PageLoc
  lda SmTempY
  sta Player_Y_Position
Return:
  lda SmClearance
  rts
XOffsets: .byte $f9,6
.endproc
.popseg
