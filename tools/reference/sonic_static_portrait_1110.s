; The existing intermediate-player caller supplies SelectedCharacter in A.
; Non-Sonic portraits receive the original fallback farcall and registers.
.setcpu "6502"
.segment "PORTRAIT"
SonicStaticPortrait:
 php
 cmp #43
 beq SonicPortrait
 plp
 sta $016a
 lda #$28
 sta $016c
 lda #$a5
 sta $016d
 lda #$dd
 jmp $015a
SonicPortrait:
 plp
 lda #1                       ; Native four-cell standing box, tiles0/2/20/22.
 sta $06e1
 sta $73ee
 sta $0146
 lda #$85                     ; Existing Sonic physical-page NMI mapping.
 sta $73e0
 lda #16                      ; Logical16 maps to genuine source page224.
 sta $0147
 rts
