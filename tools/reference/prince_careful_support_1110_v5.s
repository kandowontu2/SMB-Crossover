; Derivative of the exact128B D297 native exposed-cap support adapter.
; The only new accepted original action is careful-step42. Running1 and all
; existing mode/physical-foot/native-ground/solid-and-empty-above checks stay.
.setcpu "6502"
.segment "SUPPORT"
PpCarefulSupport:
 jsr $bde2
 bne Done
 php
 lda $c616
 cmp #1
 beq ActionMode
 cmp #42
 bne Empty
ActionMode:
 lda $c618
 cmp #1
 beq SupportedMode
 cmp #$ff
 bne Empty
SupportedMode:
 lda $c085
 ora $c087
 ora $001e
 bne Empty
 lda $00a4
 cmp #1
 bne Empty
 lda $c084
 cmp $c086
 bne Empty
 lda $00bd
 adc #32
 bcs Empty
 cmp $c084
 bne Empty
 sbc #1
 sta $b36b
 lda #0
 sta $b36c
 lda $c615
 and #11
 adc #1
 adc $0075
 sta $b369
 lda $005c
 adc #0
 sta $b36a
 jsr $b310
 bcc Empty
 and #$fc
 cmp #$10
 bne Empty
 dec $b36b
 jsr $b310
 bcs Empty
 lda $b36b
 adc #1
 sta $c07f
 lda #0
 sta $c080
 plp
 lda #1
 rts
Empty:
 plp
 lda #0
Done:
 rts
