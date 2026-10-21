; Isolated proposal, never included by this preparation. Normal25px static
; Ground correction only. Potential native-platform overlap keeps the previous
; behavior; whole sourceGROUND_STG_DCT/platform parity remains explicitly open.
.pushseg
.segment "SPECIAL_ROSTER"
.proc RyuWallAdjustGrab
  ; Arrive by same-size JMP after CanAttach SEC. No extra trampoline return.
  ; Source lowerpoint = nativeY+19.5. Early-out adds no new stack residue.
  lda MmYFraction+1
  clc
  adc #$80
  tax
  lda Player_Y_Position
  adc #19
  cmp R3                         ; CanAttach leaves contacted tile bottom inR3.
  bcc Return
  bne Save
  cpx #0
  bne Save
  lda MmYFraction
  bne Save
Return:
  lda RyWallResolved
  sec                            ; Original CanAttach SEC survives LDA.
  jmp RyuWallGrabContinue
Save:
  ; Preserve every scratch byte this helper/map query changes. Actual native
  ; component records all10240RAM and ordered writes, including dead stack.
  lda RgTempX
  pha
  lda RgTempPage
  pha
  lda RgTempY
  pha
  ldx #7
PushScratch:
  lda R0,x
  pha
  dex
  bpl PushScratch
  lda R3
  sta R4
  clc
  lda Player_Y_Position
  adc #7
  sta R7                         ; Conservative platform vertical envelope.
  clc
  lda Player_Y_Position
  adc #32
  sta R5
  ldx #5
Platform:
  lda Enemy_Flag,x
  beq NextPlatform
  lda Enemy_ID,x
  cmp #$24
  bcc NextPlatform
  cmp #$2d
  bcs NextPlatform
  lda Enemy_Y_HighPos,x
  cmp #1
  bne NextPlatform
  lda Enemy_Y_Position,x
  jsr PotentialPlatform
  jcs Restore
  lda Enemy_ID,x
  cmp #$2b
  bcc NextPlatform
  lda Enemy_Y_Position,x
  eor #$80                       ; Native smalllift has a second128px copy.
  jsr PotentialPlatform
  jcs Restore
NextPlatform:
  dex
  bpl Platform
  ; Inclusive source hTop/hBot rows. An exact top boundary also intersects
  ; the preceding row; no buffer row wraps or offscreen extrapolation.
  clc
  lda Player_Y_Position
  adc #7
  sta R2
  and #15
  bne RoundTop
  lda MmYFraction
  ora MmYFraction+1
  bne RoundTop
  lda R2
  sec
  sbc #16
  sta R2
RoundTop:
  lda R2
  and #$f0
  cmp #32
  jcc Restore
  sta R2
  lda R5
  and #$f0
  cmp #208
  bcs Restore
  sta R5
  sec
  lda RyWallEdge
  sbc #16
  sta RgTempX
  lda RyWallPage
  sbc #0
  sta RgTempPage
  lda #0
  sta R6                         ; Both mirror cases touch columns edge-16/edge.
Column:
  lda R2
  sta R7
Row:
  lda R7
  cmp RyWallScanY
  bne Other
  clc
  lda R6
  adc RyWallResolved
  cmp #2                         ; right targetcol1 / left targetcol0.
  beq NextRow
Other:
  lda R7
  sta RgTempY
  jsr RyuWallMap
  bcs Restore                    ; Source otherGround intersects current body.
NextRow:
  lda R7
  cmp R5
  bcs NextColumn
  clc
  adc #16
  sta R7
  jmp Row
NextColumn:
  lda R6
  bne Raise
  inc R6
  clc
  lda RgTempX
  adc #16
  sta RgTempX
  bcc Column
  inc RgTempPage
  jmp Column
Raise:
  ; Exact source loop: subtract2Flashpx=1NESpx, retain original Q16 fraction.
  ; CanAttach bounds excess to<=5px, so this requires at most5 decrements.
  lda MmYFraction+1
  clc
  adc #$80
  tax
  lda Player_Y_Position
  adc #19
  cmp R4
  bcc Restore
  bne Lower
  cpx #0
  bne Lower
  lda MmYFraction
  beq Restore
Lower:
  dec Player_Y_Position
  jmp Raise
Restore:
  ldx #0
PopScratch:
  pla
  sta R0,x
  inx
  cpx #8
  bne PopScratch
  pla
  sta RgTempY
  pla
  sta RgTempPage
  pla
  sta RgTempX
  jmp Return
PotentialPlatform:
  ; This is a conservative UNCHANGED-PATH bailout, not an invented source
  ; platform HRect. Native platform bodies fit inside top..top+32; if that
  ; vertical envelope could overlap, leave the old behavior untouched.
  cmp R5
  bcc PlatformBottom
  beq PlatformBottom
  clc
  rts
PlatformBottom:
  clc
  adc #32
  bcs Potential
  cmp R7
  bcc NotPotential
Potential:
  sec
  rts
NotPotential:
  clc
  rts
.endproc
.assert *-RyuWallAdjustGrab <= 456, error, "Ryu static grapple helper exceeds min free bank61 budget"
.popseg
