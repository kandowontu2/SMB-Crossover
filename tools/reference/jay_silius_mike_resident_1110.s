; Exact same current Mike pose envelope, with a new tail for the typed route.
; Fixed80C2 is the actual STA CurrentBankC / STA $5116 / RTS leaf.
.setcpu "6502"
.segment "MIKE_POSE"
CompactMikePose:
 lda #$e1
 jsr $80c2
 stx $5c0b
 jsr $c38c
 sta $6b08
 sta $0147
 pha
 lda $053e
 cmp #2
 bne PoseIndex
 ; Equality gives C1, so ADC #6 is the original X + 7.
 txa
 adc #6
 tax
 sec
PoseIndex:
 lda $c032,x
 sta $6b06
 lda $c040,x
 sta $6b07
 lda #$e9
 sta $06e1
 tya
 tax
 pla
 ldy #0
 sta $016a
 lda #$75
 sta $016c
 lda #$a2
 sta $016d
 lda #$be
 jmp $015a

; Only the original exact raw16 branch at A53D reaches this tail.
JayMovementRoute:
 lda $730b
 and #$60
 cmp #$20
 beq OriginalJayPath
 jmp $a2cb
OriginalJayPath:
 jmp JayTransport
