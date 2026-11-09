.setcpu "6502"
.segment "WORKER"
.export MiniStompDrop, WorkerEnd

; Bank66 $B592..$B5A7 was the skipped Prince menu envelope. The private
; DK Jr proposal required the same all-EA preimage and needs new funding.
; Sole ingress is the original MaaStomp call. Its first continuation
; instruction is LDA #4 and the following ADC starts with CLC. Keep the
; native Goomba drop scratch write even though Mini has no drop owner.
MiniStompDrop:
    lda $6002
    cmp #$29
    bne Legacy
    lda $17,x
    cmp #6
    bne Return
    stx $6f12
Return:
    rts
Legacy:
    jmp $ee06
WorkerEnd:
