.setcpu "6502"
.segment "HEAD"
.export GfHeadNative,GfHeadEntry,GfHeadEnd
GfHeadEntry:
 php
 pha
 eor #41
 beq Mini
 cmp #3                     ; EntryA is SelectedCharacter from fixed988F.
 beq GfHeadNative
 lda #$b0
 sta $016c
 lda #$bf
 sta $016d
 lda #$9c
 jsr $015a
 ; Authenticated C2 and native fallback share the high byte and return tail.
 lda #$f1
 bcc Low
 lda #$fe
Low:
 sta $016c
 lda #$b6
 sta $016d
 lda #$c2
 bcc Bank
 lda #2
Bank:
 sta $0162
 pla
 plp
 sta $016a
 jmp $015d
Mini:
 pla
 plp
 lda #$3e
 sta $016c
 lda #$b4
 sta $016d
 lda #$d4
 jmp $015a
GfHeadNative:
 pla
 plp
 jmp $9587
GfHeadEnd:
.res 80-(*-GfHeadEntry),$ea
