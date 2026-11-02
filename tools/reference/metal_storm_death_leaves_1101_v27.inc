; Original bank 0:$966A..$9735 and data $9736..$9744.
; Entry excludes the original moving-platform coordinate adjustment at $9634.
; Graphics upload requests remain donor state, requiring host renderer mapping.
Ms27DeathInit:
 ldx #$17
@clear:
 lda #0
 sta MsState+$510,x
 lda #$80
 sta MsState+$498,x
 dex
 bne @clear
 lda #0
 sta MsState+$648
 sta MsState+$74b
 lda #$80
 sta MsState+$70
 lda #2
 sta MsState+$528
 lda MsState+$480
 sec
 sbc #$10
 sta MsState+$480
 bcs @y
 dec MsState+$498
@y:
 lda MsState+$4b0
 sec
 sbc #$10
 sta MsState+$4b0
 ldy MsState+$50
 bne @wrap
 bcs @pose
 dec MsState+$4c8
 jmp @pose
@wrap:
 bcs @normalize
 adc #$f0
@normalize:
 cmp #$f0
 bcc @store
 sbc #$f0
@store:
 sta MsState+$4b0
 lda #0
 sta MsState+$4c8
@pose:
 lda #0
 sta MsState+$4e0
 sta MsState+$4f8
 lda #3
 sta MsState+$53
 lda #$a3
 sta MsState+$759
 lda Ms27DeathChrLo
 sta MsState+$75a
 lda Ms27DeathChrHi
 sta MsState+$75b
 lda #1
 sta MsState+$540
 lda #$80
 sta MsState+$755
 sta MsState+$715
 inc MsState+$35
 rts

Ms27DeathAnimate:
 dec MsState+$53
 beq @advance
 rts
@advance:
 lda #3
 sta MsState+$53
 inc MsState+$4f8
 ldx MsState+$4e0
 lda MsState+$4f8
 cmp Ms27DeathCounts,x
 beq @next
 rts
@next:
 lda #0
 sta MsState+$4f8
 inc MsState+$4e0
 ldx MsState+$4e0
 cpx #5
 beq @done
 lda Ms27DeathChrLo,x
 sta MsState+$75a
 lda Ms27DeathChrHi,x
 sta MsState+$75b
 lda #$80
 sta MsState+$755
 rts
@done:
 inc MsState+$35
 lda #4
 sta MsState+$4e0
 lda #0
 sta MsState+$4f8
 lda #$3c
 sta MsState+$53
 rts
Ms27DeathCounts:
 .byte 5,3,4,3,1
Ms27DeathChrLo:
 .byte $a1,$a5,$a9,$ad,$b1
Ms27DeathChrHi:
 .byte $a3,$a7,$ab,$af,$b1
