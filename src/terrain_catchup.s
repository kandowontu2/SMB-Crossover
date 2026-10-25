; A coin/axe erase writes the secondary VRAM queue from its beginning.
; Catching up before NMI consumes a published terrain packet would discard
; that packet, leaving old tile/attribute data in the scrolling nametable.
::TerrainCatchupPending:
  lda VRAM_Buffer_AddrCtrl
  cmp #6                         ; Published secondary queue needs its NMI.
  beq Done                       ; CMP returns C set when the queue is busy.
  lda #1
  sta ShouldSkipDrawSprites
  clc
Done:
  rts                            ; C means wait; otherwise one catch-up is safe.
  .res 2,$ea                     ; Preserve the original resident bridge span.
