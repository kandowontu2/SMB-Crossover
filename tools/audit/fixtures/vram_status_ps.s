; Both native numeric printers share the84-byte queue with terrain and
; character HUDs. A blocked field is coalesced to its latest native digits.
.pushseg
.segment "X5_BOUNCE"
.proc X5NativeStatusReserve
  ; Input Y=2*slot, with the caller's slot still on its own stack.
  ; Keep Y and all R0..R7 intact: R0 owns the second packed request.
  lda OperMode
  cmp #1
  bne Fits
  tya
  lsr
  tax
  lda SelectedCharacter
  cmp #4
  bne Capacity
  lda Z2Variant
  beq Capacity
  cpx #1
  bcc Capacity
  cpx #5
  bcc Suppressed              ; score and coins overlap the spell/EXP row
Capacity:
  lda VRAM_Buffer1_Offset
  clc
  adc Lengths,x
  bcs Deferred
  cmp #81                    ; last terminator <=83, before Buffer2 offset
  bcc Fits
Deferred:
  lda Bits,x
  ora NativeStatusPending
  sta NativeStatusPending
Suppressed:
  lda #0
  rts
Fits:
  lda #1
  rts
Lengths:.byte 6,6,6,2,2,3
Bits:.byte 1,2,4,8,16,32
.endproc

.proc X5NativeStatusFlush
  lda OperMode
  cmp #1
  bne Clear
  lda NativeStatusPending
  beq Done
  lda OperMode_Task
  cmp #3
  bne Done
  lda GameEngineSubroutine
  cmp #8
  bne Done
  lda GamePauseStatus
  and #1
  bne Done
  lda R0
  pha
  lda #0
  sta NativeStatusCursor
Next:
  ldx NativeStatusCursor
  lda X5NativeStatusReserve::Bits,x
  and NativeStatusPending
  beq Advance
  eor NativeStatusPending
  sta NativeStatusPending
  txa
  sec
  sbc #1
  and #$0f
  ora #$50                   ; high5 increments to6: truly invalid slot
  farcall HudUpdateNumberLocal
Advance:
  inc NativeStatusCursor
  lda NativeStatusCursor
  cmp #6
  bcc Next
  pla
  sta R0
Done:
  rts
Clear:
  lda #0
  sta NativeStatusPending
  rts
.endproc
.popseg
