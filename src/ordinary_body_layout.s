; Exact original poses remain the fallback at screen/page edges. These three
; internal-window alternatives reduce blank 8x16 rows without changing pixels.
.include "ordinary_body_layout_art.inc"
.pushseg
.segment "SAMUS"
.proc OrdinaryLowPressurePose
  phx
  phy
  lda Player_Y_HighPos
  cmp #1
  jne Original
  lda Player_Y_Position
  cmp #16
  jcc Original
  cmp #208
  jcs Original
  lda Player_X_Position
  sec
  sbc ScreenLeft_X_Pos
  sta R0
  lda Player_PageLoc
  sbc ScreenLeft_PageLoc
  jne Original
  lda R0
  cmp #16
  jcc Original
  cmp #225
  jcs Original
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  beq Bass
  ; Caller limits this to normal Bill WALK2; the fire outfit is a different
  ; source image/bank, and Lance retains his own original art.
  lda BillVariant
  jne Original
  cpx #96
  jcs Original
  lda #$1d
  sta SmChrBank
  lda PlayerFacingDir
  cmp #1
  bne BillLeft
  lda #<OrdBillWalk2Right
  sta SmPosePtr
  lda #>OrdBillWalk2Right
  jmp Selected
BillLeft:
  lda #<OrdBillWalk2Left
  sta SmPosePtr
  lda #>OrdBillWalk2Left
  jmp Selected
Bass:
  lda RgPose
  cmp #XG_POSE_WALK3
  beq BassThird
  lda #$83
  sta SmChrBank
  lda PlayerFacingDir
  cmp #1
  bne BassFirstLeft
  lda #<OrdBassWalk1Right
  sta SmPosePtr
  lda #>OrdBassWalk1Right
  jmp Selected
BassFirstLeft:
  lda #<OrdBassWalk1Left
  sta SmPosePtr
  lda #>OrdBassWalk1Left
  jmp Selected
BassThird:
  lda #$e1
  sta SmChrBank
  lda PlayerFacingDir
  cmp #1
  bne BassThirdLeft
  lda #<OrdBassWalk3Right
  sta SmPosePtr
  lda #>OrdBassWalk3Right
  jmp Selected
BassThirdLeft:
  lda #<OrdBassWalk3Left
  sta SmPosePtr
  lda #>OrdBassWalk3Left
Selected:
  sta SmPosePtr+1
  ply
  plx
  lda SmPosePtr+1              ; 6502 PLY/PLX macros return their value through A.
  sec
::OrdinaryPoseSelected:
  rts
Original:
  ply
  plx
  clc
::OrdinaryPoseOriginal:
  rts
.endproc
.popseg
