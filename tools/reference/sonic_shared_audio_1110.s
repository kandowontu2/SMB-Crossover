; Relocated native audio fallback, physical63 B53B..<B57C only.
; The entry owns stack [saved P, old software A bank]. Avoid swapping it
; into [saved A, saved P] and back around cleanup that reads neither input.
; The final LDA OperMode restores N/Z before every original branch;
; original C/V/I and old A-bank publication remain owned by the caller.
.setcpu "6502"
.segment "AUDIO"
SonicSharedAudio:
 lda $5fff
 and #1
 sta $5fff
 lda $72da
 cmp #$82
 bne Restore
 lda #$ff
 sta $72da
 lda #0
 sta $4011
 sta $4015
 sta $5015
Restore:
 plp
 pla
 lda $0771
 beq Vanilla
 lda $6002
 beq Vanilla
 cmp #8
 beq Vanilla
 cmp #43
 beq Vanilla
 cmp #23
 beq Vanilla
 cmp #28
 beq Vanilla
 jmp $f06f
Vanilla:
 jmp $f0d8
