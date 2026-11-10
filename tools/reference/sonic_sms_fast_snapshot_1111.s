; Live authenticated Sonic RAM3/RAM2 frame. Preserve the complete
; 180-byte rollback buffer and resume the original four-byte SMC copy.
.setcpu "6502"
.segment "SNAPSHOT"
SonicFastSnapshot:
 ldx #44
CopyFour:
 lda $c000,x
 sta $c200,x
 lda $c02d,x
 sta $c22d,x
 lda $c05a,x
 sta $c25a,x
 lda $c087,x
 sta $c287,x
 dex
 bpl CopyFour
 sec
 jmp $bcd1
