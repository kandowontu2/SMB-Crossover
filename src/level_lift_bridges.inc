.proc CrossoverLiftMoveBridge
  farcall CrossoverLiftMove
  rts
.endproc

.proc CrossoverLiftSecondY
  pha
  lda AreaPointer
  cmp #$62
  bne Native
  lda WorldNumber
  cmp #World2
  beq Source
  cmp #World5
  bne Native
Source:
  pla
  ldx ObjectOffset            ; DrawSmallPlatform's incoming X is an old Y value.
  sec
  sbc Enemy_Y_Position,x
  clc
  adc Enemy_State,x
  rts
Native:
  pla
  clc
  adc #$80
  rts
.endproc

.proc CrossoverLiftPlayerY
  cpy #1
  beq Second
  clc
  adc #0
  rts
Second:
  jmp CrossoverLiftSecondY
.endproc
