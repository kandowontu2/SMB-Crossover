; Current shared native feet routing. No new RAM or inferred padding.
.setcpu "6502"
.segment "HEAD"
 lda #$e3
 sta $016c
 lda #$b9
 sta $016d
 lda #$85
 jmp $015a
.segment "FOOT"
 lda $6002
 cmp #43
 beq Cold
 cmp #4
 beq Cold
 cmp #11
 beq Cold
 cmp #22
 beq Cold
 cmp #26
 beq Cold
 cmp #28
 bne Native
Cold:
 lda #$e7
 sta $016c
 lda #$b6
 sta $016d
 lda #$bf
 jmp $015a
Native:
 jmp $9586
.segment "SIDE"
 jmp $90e4
.segment "DEFAULT"
 cmp #28
 beq $bcbf
 cmp #11
 bne DefaultCold
 cpy #31
 bne DefaultCold
 bit $6b0f
 bpl DefaultCold
 jmp $9586
DefaultCold:
 lda #$8f
 sta $016c
 lda #$a6
 sta $016d
 lda #$c7
 jmp $015a
SonicHigh:
 lda #$b0
 sta $016d
 jmp $b0f5
 nop
.segment "UNION"
 lda $6002
 cmp #22
 beq $bfeb
 cmp #26
 beq Gimmick
 cmp #43
 beq SonicLow
 jmp $bc93
Gimmick:
 lda #$77
 sta $016c
 lda #$b8
 sta $016d
 jmp $ac10
SonicLow:
 lda #$f5
 sta $016c
 jmp SonicHigh
 nop
.segment "SH_TAIL"
 lda #$98
 jmp $015a
