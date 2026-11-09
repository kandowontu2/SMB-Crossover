.setcpu "6502"
.segment "WORKER"
.export DrawLargePlatform, VisibleActorBounds, BoundsStock, WorkerEnd

; The sole caller immediately follows RelativeEnemyPosition, which reloads
; X from ObjectOffset. Size uses bit 1; cloud switches bits 2 and 3.
; Preserve the frame-parity scratch written by the old renderer.
DrawLargePlatform:
    lda $0e
    and #1
    sta $05
    ora #$54
    ldy $0753
    cpy #3
    beq SizeReady
    ldy $06ca
    bne SizeReady
    ora #2
SizeReady:
    ldy $0746
    beq PoseReady
    eor #$0c
PoseReady:
    sta $06e2,x
Return:
    rts

; GetScreenPosition publishes Right = Left + 255, including page wrap.
; Loopback shifts both edges equally. An unsigned relative X in 0..255
; is inside both extended erase edges for every ordinary/platform ID.
VisibleActorBounds:
    lda $76,x
    cmp $071f
    lda $5d,x
    sbc $071d
    beq Return
BoundsStock:
    jmp $a504
WorkerEnd:
