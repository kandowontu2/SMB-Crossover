; Immediate numeric updates, coalescing only a whole final coin+score pair.
.pushseg
.segment "HUD_TAIL_COLD"
.proc HudUpdateNumberLocal
  pha
  cmp #$02
  beq CheckTail
  cmp #$13
  bne Print
CheckTail:
  jsr ReuseTail
Print:
  pla
  jsr HudPrintStatusNumbersLocal
  ldy VRAM_Buffer1_Offset
.if ::ENABLE_MMC5_EXPANDED
  cpy #9
  bcc NoZSup
  lda VRAM_Buffer1-9,y
  cmp #$20
  bne NoZSup
  lda VRAM_Buffer1-8,y
  cmp #$62
  bne NoZSup
  lda VRAM_Buffer1-7,y
  cmp #6
  bne NoZSup
.endif
  lda VRAM_Buffer1-6,y
  bne NoZSup
  lda #$24
  sta VRAM_Buffer1-6,y
NoZSup:
  ldx ObjectOffset
  rts
ReuseTail:
  ldy VRAM_Buffer1_Offset
  cpy #14
  bcc Done
  cpy #85
  bcs Done
  lda VRAM_Buffer1,y
  bne Done
  lda VRAM_Buffer1-14,y
  cmp #$20
  bne Done
  lda VRAM_Buffer1-13,y
  cmp #$6d
  bne Done
  lda VRAM_Buffer1-12,y
  cmp #2
  bne Done
  lda VRAM_Buffer1-9,y
  cmp #$20
  bne Done
  lda VRAM_Buffer1-8,y
  cmp #$62
  bne Done
  lda VRAM_Buffer1-7,y
  cmp #6
  bne Done
  tya
  sec
  sbc #14
  sta R3
  ldx #0
Packet:
  cpx R3
  beq Reuse
  bcs Done
  lda VRAM_Buffer1,x
  beq Done
  ; The target is <=70. X<target, so reading X+2 stays within the
  ; 85-byte queue even for a truncated foreign header. Every packet
  ; advances at least4 bytes. Reject overshoot at Packet; no additional
  ; header/end comparison or 8-bit overflow check is required (sum<=135).
  lda VRAM_Buffer1+2,x
  and #$3f
  beq Done
  sta R2
  lda VRAM_Buffer1+2,x
  and #$40
  beq CountReady
  lda #1
  sta R2
CountReady:
  txa
  clc
  adc #3
  adc R2
  tax
  jmp Packet
Reuse:
  stx VRAM_Buffer1_Offset
Done:
  rts
.endproc
.popseg

.pushseg
.segment "HUD_TAIL_COLD"
.proc HudPrintStatusNumbersLocal
  sta R0             ;store player-specific offset
  jsr OutputNumbers  ;use first nybble to print the coin display
  lda R0             ;move high nybble to low
  lsr                ;and print to score display
  lsr
  lsr
  lsr
OutputNumbers:
  clc                      ;add 1 to low nybble
  adc #$01
  and #%00001111           ;mask out high nybble
  cmp #$06
  bcs ExitOutputN
  pha                      ;save incremented value to stack for now and
    asl                      ;shift to left and use as offset
    tay
 .if ::ENABLE_MMC5_EXPANDED
    jsr HudNativeStatusReserve
    bcs RejectedNumbers
 .else
    ldx VRAM_Buffer1_Offset  ;get current buffer pointer
    lda #$20                 ;put at top of screen by default
 .endif
    cpy #$00                 ;are we writing top score on title screen?
    bne SetupNums
    lda #$22                 ;if so, put further down on the screen
SetupNums:
    sta VRAM_Buffer1,x
    lda StatusBarData,y      ;write low vram address and length of thing
    sta VRAM_Buffer1+1,x     ;we're printing to the buffer
    lda StatusBarData+1,y
    sta VRAM_Buffer1+2,x
    sta R3                   ;save length byte in counter
    stx R2                   ;and buffer pointer elsewhere for now
  pla                      ;pull original incremented value from stack
  tax
  lda StatusBarOffset,x    ;load offset to value we want to write
  sec
  sbc StatusBarData+1,y    ;subtract from length byte we read before
  tay                      ;use value as offset to display digits
  ldx R2 
DigitPLoop:
  lda DisplayDigits,y      ;write digits to the buffer
  sta VRAM_Buffer1+3,x    
  inx
  iny
  dec R3                   ;do this until all the digits are written
  bne DigitPLoop
  lda #$00                 ;put null terminator at end
  sta VRAM_Buffer1+3,x
  inx                      ;increment buffer pointer by 3
  inx
  inx
  stx VRAM_Buffer1_Offset  ;store it in case we want to use it again
ExitOutputN:
  rts
.if ::ENABLE_MMC5_EXPANDED
RejectedNumbers:
  pla
  rts
.endif
  

;-------------------------------------------------------------------------------------
;$00 - used to store status bar nybbles
;$02 - used as temp vram offset
;$03 - used to store length of status bar number

;status bar name table offset and length data
StatusBarData:
  .byte $f0, $06 ; top score display on title screen
  .byte $62, $06 ; player score
  .byte $62, $06
  .byte $6d, $02 ; coin tally
  .byte $6d, $02
  .byte $7a, $03 ; game timer

StatusBarOffset:
  .byte TopScoreDisplay + TopScoreLastIndex - DisplayDigits + 1
  .byte Player1ScoreDisplay + PlayerScoreLastIndex - DisplayDigits + 1
  .byte Player2ScoreDisplay + PlayerScoreLastIndex - DisplayDigits + 1
  .byte Player1CoinDisplay + PlayerCoinLastIndex - DisplayDigits + 1
  .byte Player2CoinDisplay + PlayerCoinLastIndex - DisplayDigits + 1
  .byte GameTimerDisplay + GameTimerLastIndex - DisplayDigits + 1
.endproc
.popseg

.pushseg
.segment "HUD_TAIL_COLD"

.if ::ENABLE_MMC5_EXPANDED
.proc HudNativeStatusReserve
  farcall X5NativeStatusReserve
  beq Full
  ldx VRAM_Buffer1_Offset
  lda #$20
  clc
  rts
Full:sec
  rts
.endproc
.endif

.popseg
