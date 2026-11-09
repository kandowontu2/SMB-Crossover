; This entry is reached through the fixed far call, so $016A already
; holds the incoming accumulator. The loader-cookie probe is a leaf.
.setcpu "6502"
.segment "SIDE"
SelectedCharacter = $6002
FarCallCommon = $015a
SavedA = $016a
TargetLo = $016c
TargetHi = $016d
LegacySide = $bee2

 php
 lda SelectedCharacter
 cmp #41
 beq Mini

 lda #$b0
 sta TargetLo
 lda #$bf
 sta TargetHi
 lda #$9c
 jsr FarCallCommon
 bcc Legacy

 lda #$55
 sta TargetLo
 lda #$b7
 sta TargetHi
 plp
 lda #$02
 jmp FarCallCommon

Mini:
 ; Reuse the current exact Mini/native collision branch in bank 124.
 lda #$9b
 sta TargetLo
 lda #$ad
 sta TargetHi
 plp
 lda #$fc
 jmp FarCallCommon

Legacy:
 lda SavedA
 plp
 jmp LegacySide
