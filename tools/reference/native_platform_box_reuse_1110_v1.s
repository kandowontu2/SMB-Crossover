.setcpu "6502"

GetXOffscreenBits = $8b1a
MoveBoundBoxOffscreen = $9f3b
BoundingBoxCore = $9f4e
TaggedPlatformBox = $aeae
TaggedHeightTail = $aedf
EnemyOffscreenBits = $05a1
EnemyState = $1f
ULX = $0658
ULY = $0659
DRX = $065a

.segment "BOX"
.export GenericBox, PreparedBox, VisibleBox, LegacyBox
GenericBox:
  inx
  jsr GetXOffscreenBits
  dex
  cmp #$fe
  bcc VisibleBox
  jmp MoveBoundBoxOffscreen

PreparedBox:
  ; RunLargePlatform has just published X's high nibble in the low four
  ; bits of EnemyOffscreenBits. Both rejection codes FE/FF have bit0
  ; set after packing. An ambiguous bit always takes the original test.
  lda EnemyOffscreenBits
  lsr
  bcs GenericBox
VisibleBox:
  jmp TaggedPlatformBox

LegacyBox:
  inx
  nop
  ldy #1
  jsr BoundingBoxCore
  lda EnemyState-1,x
  and #$20
  beq Height
  lda ULX,y
  clc
  adc #16
  sta DRX,y
Height:
  lda ULY,y
  jmp TaggedHeightTail
.assert *-GenericBox=49,error,"Preserve HpPrepareNativePointers"

.segment "INGRESS"
  .byte <PreparedBox

.segment "LEGACY_TARGET"
  .word LegacyBox
