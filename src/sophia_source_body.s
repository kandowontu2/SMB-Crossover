; Sophia symbol113 main HRect: 19 x 15.5 NESpx, centered on source nx,
; bottom at source ny. Flat anchor=(native PX+8+xf,PY+32+yf).
; Ceil lower/floor upper is exact against integral native actor endpoints.
; It does not certify native enemy geometry or arbitrary fractional targets.
.pushseg
.segment "SOPHIA_BODY_COLD"
SophiaSourceBodyStart:
.proc CrossoverSourceBodyDispatch
  cmp #CHARACTER_SOPHIA
  beq Sophia
  jmp RyuSourceBodyBox
Sophia:
  jsr SophiaSourceAfterTerrain
  jmp SophiaSourceBodyBox
.endproc

; A-only eligibility leaf, no scratch/state writes. Flat native pose ownership
; excludes wall/ceiling/vine and death; these require their rotated anchors.
.proc SophiaSourceFlatBodyValid
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne No
  lda OperMode
  cmp #1
  bne No
  lda GameEngineSubroutine
  cmp #8
  bne No
  lda Player_State
  cmp #3
  bcs No
  lda XgWall
  ora XgCeiling
  ora MmDeathFlag
  bne No
  lda Player_Y_HighPos
  cmp #1
  bne No
  lda Player_Y_Position
  cmp #224
  bcs No
  ; Every projected endpoint remains on screen; no wrapped bbox semantics.
  lda Player_X_Position
  sec
  sbc ScreenLeft_X_Pos
  lda Player_PageLoc
  sbc ScreenLeft_PageLoc
  bne No
  lda Player_X_Position
  sec
  sbc ScreenLeft_X_Pos
  cmp #2
  bcc No
  cmp #237
  bcs No
  sec
  rts
No:
  clc
  rts
.endproc

.proc SophiaSourceBodyBox
  php
  pha
  jsr SophiaSourceFlatBodyValid
  bcc Done
  ; leftQ=PX-1.5+xf; ceil is PX-1 through xf==.5, else PX.
  lda Player_X_Position
  sec
  sbc ScreenLeft_X_Pos
  sec
  sbc #1
  sta BoundingBox_UL_Corner
  lda MmXFraction+1
  cmp #$80
  bcc Right
  bne LeftExtra
  lda MmXFraction
  beq Right
LeftExtra:
  inc BoundingBox_UL_Corner
Right:
  ; rightQ=PX+17.5+xf; floor changes at xf==.5 inclusive.
  lda Player_X_Position
  sec
  sbc ScreenLeft_X_Pos
  clc
  adc #17
  sta BoundingBox_LR_Corner
  lda MmXFraction+1
  cmp #$80
  bcc Top
  inc BoundingBox_LR_Corner
Top:
  ; topQ=PY+16.5+yf; ceil changes strictly after yf==.5.
  lda Player_Y_Position
  clc
  adc #17
  sta BoundingBox_UL_Corner+1
  lda MmYFraction+1
  cmp #$80
  bcc Bottom
  bne TopExtra
  lda MmYFraction
  beq Bottom
TopExtra:
  inc BoundingBox_UL_Corner+1
Bottom:
  lda Player_Y_Position
  clc
  adc #32
  sta BoundingBox_LR_Corner+1
Done:
  pla
  plp
  rts
.endproc

.proc CrossoverSourceFirebarDisjoint
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  beq Link
  jmp SophiaSourceFirebarDisjoint
Link:
  jmp EasyLinkFirebarDisjoint
.endproc

; Before native direction/injury mutation, reject only proven vertical
; disjointness from the complete 8x16 native container (including spare edge).
; A real overlap retains native response pending full Flash bitmap port.
.proc SophiaSourceFirebarDisjoint
  jsr SophiaSourceFlatBodyValid
  bcc Native
  ; Require a current projected rectangle, never a stale/other-form box.
  lda Player_Y_Position
  clc
  adc #32
  cmp BoundingBox_LR_Corner+1
  bne Native
  lda MmYFraction+1
  cmp #$80
  bcc SameTop
  bne ExtraTop
  lda MmYFraction
  beq SameTop
ExtraTop:
  lda Player_Y_Position
  clc
  adc #18
  jmp CompareTop
SameTop:
  lda Player_Y_Position
  clc
  adc #17
CompareTop:
  cmp BoundingBox_UL_Corner+1
  bne Native
  lda R7
  cmp #3
  bcc Native
  cmp #243
  bcs Native
  clc
  adc #13
  cmp BoundingBox_UL_Corner+1
  bcc Disjoint
  lda R7
  sec
  sbc #3
  cmp BoundingBox_LR_Corner+1
  bcc Native
  beq Native
Disjoint:
  sec
  rts
Native:
  clc
  rts
.endproc
SophiaSourceBodyEnd:
.popseg
