.setcpu "6502"

UniqueBank = $c0fc
UniqueLo = $c13e
UniqueHi = $c180
AudioPtr = $de
AudioBank = $6f39
AudioFamily = $6f37
AudioStatus = $7320
MusicImage = $730c
NativeImage = $7282
NativeDirty = $72aa
GuestNativeStatusSTA = $eceb
ReadByte = $cb03
LegacyCommands = $c956
MaskFrame = $c9f6
Loop = $c989
ClearQueues = $ca57
StopCorruptStream = $cadd

RightOffsets = $ba2b
LeftRecords = $bac0
RightRecords = $bb18

.segment "CODE"
.export ReadSongPointer, GroundCodecDispatch, GroundLoopFrame, EndCode

; The original load clusters leave the selector in X, preserve Y and C/V,
; and return A/N/Z from the loaded pointer's high byte.
ReadSongPointer:
  pha
  txa
  pha
  tsx
  lda $0102,x
  tax
  lda UniqueBank,x
  sta AudioBank
  lda UniqueLo,x
  sta AudioPtr
  lda UniqueHi,x
  sta AudioPtr+1
  pla
  tax
  pla
  lda AudioPtr+1
  rts

GroundCodecDispatch:
  lda AudioFamily
  cmp #7
  bne Legacy
  lda AudioBank
  cmp #$39
  bne ResetFamily
  lda AudioPtr+1
  cmp #$b7
  bcc ResetFamily
  bne Upper
  lda AudioPtr
  cmp #$4c
  bcc ResetFamily
  bcs GroundLoopFrame
Upper:
  cmp #$ba
  bcc GroundLoopFrame
  bne ResetFamily
  lda AudioPtr
  cmp #$2c                     ; The final buffered token may use cursor BA2B.
  bcc GroundLoopFrame
ResetFamily:
  lda AudioFamily
Legacy:
  cmp #13
  bcs UseMask
  jmp LegacyCommands
UseMask:
  jmp MaskFrame

.macro WriteField Record, Register
  lda Record,y
  cmp #$ff                     ; FF is absent from all six actual value sets.
  beq :+
  sta MusicImage+Register
  sta NativeImage+Register
  inc NativeDirty+Register
:
.endmacro

GroundLoopFrame:
  jsr ReadByte
  cmp #$ff
  bne CheckIndex
  jmp Loop
CheckIndex:
  cmp #149
  bcc Decode
  jmp StopCorruptStream
Decode:
  tax
  ldy #0
FindLeft:
  cmp LeftRecords,y
  bcc LeftVoice
  iny
  iny
  iny
  iny
  bne FindLeft
LeftVoice:
  WriteField LeftRecords+1,0
  WriteField LeftRecords+2,2
  WriteField LeftRecords+3,3
  ldy RightOffsets,x
  WriteField RightRecords+0,4
  WriteField RightRecords+1,6
  WriteField RightRecords+2,7
  lda #15
  sta AudioStatus
  jsr GuestNativeStatusSTA
  jmp ClearQueues
EndCode:
