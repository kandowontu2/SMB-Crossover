.setcpu "6502"

EnemyID = $17
EnemyState = $1f
EnemyBoxControl = $0646
RelX = $0572
RelY = $057d
ULX = $0658
ULY = $0659
DRX = $065a
DRY = $065b
SavedA = $016a
TargetLo = $016c
TargetHi = $016d
FarCallCommon = $015a
ClipBox = $9f90
LegacyBox = $b05a

.segment "NATIVE_PLATFORM"
.export NativeMotionPacket, TaggedPlatformBox
NativeMotionPacket:
  lda EnemyID,x
  sec
  sbc #$24
  tay
  ; The original JumpEngine at AE70 stacked AE72 and dispatched the seven
  ; fixed local packet entries. Keep its exact observable scratch image.
  lda #$72
  sta $07
  lda #$ae
  sta $08
  sta $0a
  sta SavedA
  lda OriginalEntryLow,y
  sta $09
  lda MotionLow,y
  sta TargetLo
  lda MotionHigh,y
  sta TargetHi
  tya
  asl
  tay
  iny
  iny
  lda #$80
  jmp FarCallCommon
OriginalEntryLow:
  .byte $81,$93,$a5,$a5,$b7,$c9,$db
MotionLow:
  .byte $9f,$42,$be,$be,$76,$a0,$ac
MotionHigh:
  .byte $b4,$b6,$b6,$b6,$b6,$b6,$b6

; Admission at B057 already executed GetXOffscreenBits and its full native
; offscreen rejection. Control 5/6 is [0,0,32/48,13]. The tagged original
; replaces bottom with top+8 before it invokes the same native clipper.
TaggedPlatformBox:
  lda EnemyState,x
  and #$20
  bne FullBox
  lda EnemyBoxControl,x
  sec
  sbc #5
  cmp #2
  bcs FullBox
  .repeat 4
    asl
  .endrepeat
  ora #$20
  sta $04                       ; R1 becomes the screen-center page in ClipBox.
  inx
  stx $03
  txa
  asl
  asl
  tay
  lda RelX
  sta ULX,y
  clc
  adc $04
  sta DRX,y
  lda RelY
  sta ULY,y
  clc
  adc #8
  sta DRY,y
  jmp ClipBox
FullBox:
  jmp LegacyBox

  .res $82 - (* - NativeMotionPacket), $ea

.segment "BOX_GATE"
  jmp TaggedPlatformBox
  inx                           ; Exact index consumed by legacy BoundingBoxCore.
  nop
