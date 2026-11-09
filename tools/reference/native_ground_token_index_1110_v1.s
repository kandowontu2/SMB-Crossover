.setcpu "6502"

AudioStatus = $7320
MusicImage = $730c
NativeImage = $7282
NativeDirty = $72aa
GuestNativeStatusSTA = $eceb
ReadByte = $cb03
Loop = $c989
ClearQueues = $ca57
StopCorruptStream = $cadd
RightOffsets = $ba2b
LeftRecords = $bac0
RightRecords = $bb18

.macro StoreField Register
  sta MusicImage+Register
  sta NativeImage+Register
  inc NativeDirty+Register
.endmacro

.macro WriteField Record, Register
  lda Record,y
  cmp #$ff
  beq :+
  StoreField Register
:
.endmacro

.segment "DECODER"
.export GroundLoopFrame, DecodeToken, VolumeForToken, TimedBucket, EndDecoder
GroundLoopFrame:
  jsr ReadByte
  cmp #$ff
  bne CheckIndex
  jmp Loop
CheckIndex:
  cmp #149
  bcc DecodeToken
  jmp StopCorruptStream
DecodeToken:
  tax
  cmp #8
  bcc RightVoice               ; The first group has no left writes.
  cmp #53
  bcs TimedLeft
  lda VolumeForToken-8,x       ; Exactly one left volume write in this range.
  StoreField 0
  jmp RightVoice
TimedLeft:
  lsr a
  lsr a
  tay
  lda TimedBucket-13,y         ; The first timed token is 53 (bucket 13).
  tay
  txa
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
  lda LeftRecords+2,y           ; Both timer writes are present for timed rows.
  StoreField 2
  lda LeftRecords+3,y
  StoreField 3
RightVoice:
  ldy RightOffsets,x
  WriteField RightRecords+0,4
  lda RightRecords+2,y
  cmp #$ff
  beq Finish                   ; Missing high implies missing low for all rows.
  WriteField RightRecords+1,6   ; Two records legitimately write only high.
  lda RightRecords+2,y
  StoreField 7
  clc                          ; Match the old final CMP with a present high byte.
Finish:
  lda #15
  sta AudioStatus
  jsr GuestNativeStatusSTA
  jmp ClearQueues

VolumeForToken:
  .repeat 12
    .byte $38
  .endrepeat
  .repeat 7
    .byte $39
  .endrepeat
  .repeat 6
    .byte $37
  .endrepeat
  .repeat 9
    .byte $34
  .endrepeat
  .repeat 6
    .byte $35
  .endrepeat
  .repeat 5
    .byte $33
  .endrepeat
EndDecoder:
  .assert EndDecoder-GroundLoopFrame <= $dd,error,"Existing decoder footprint"
  .res $dd-(EndDecoder-GroundLoopFrame),$ea

.segment "TIMED_OFFSETS"
TimedBucket:
  .byte $18,$1c,$1c,$1c,$20,$20,$24,$24,$28,$28,$28,$28,$28
  .byte $2c,$2c,$2c,$30,$30,$30,$34,$3c,$40,$48,$4c,$54
  .res 28-(*-TimedBucket),$ff
