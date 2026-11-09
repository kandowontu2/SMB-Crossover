; Same native camera windows and result packet as the bank24 $BBCF worker.
; Only the three already-published constructor bits authorize this lane.
MiniLiftSeenFast:
    lda $c30c
    cmp #7
    bne @native
    lda #$98
    sta $0162                 ; FarCallCommon::NextBank operand.
    ldy #2
@window:
    lda $071e
    cmp @page,y
    bne @next
    lda $0720
    sbc @minimum,y            ; Equal page compare established C=1.
    cmp #80
    bcc @seen
@next:
    dey
    bpl @window
    bmi @publish
@seen:
    lda @bits,y               ; Seen is exactly 7, so the old AND is identity.
@publish:
    sta $0179                 ; FarCallCommon::SafereturnA operand.
    ora #0                    ; Original return reload established N/Z from A.
    rts
@native:
    lda #$98
    jmp MiniFarCall           ; Retain original target BBCF and real allocator.
@page: .byte 2,2,3
@minimum: .byte $10,$90,$40
@bits: .byte 1,2,4
