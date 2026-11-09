.setcpu "6502"
.segment "CODE"

CurrentBank = $0145
RemainingEffect = $7fa6
RemainingRequest = $7fa7
RemainingPreviousMask = $7fa9
AudioBank = $5115
RemainingTick = $bfb4
GuestFinish = $a4ec
FinishWorker = $f069
RestoreBank = $f0ce

.ifdef ASSEMBLE_FINISH_WORKER
    jsr GuestFinish
    jmp RestoreBank
.else
; The bank-7 tick has no effect until it has a command, a live effect, or
; an old mask to release. Keep the earlier bank-7 HUD/owner setup intact.
GuestMix:
    lda CurrentBank
    pha
    lda RemainingEffect
    ora RemainingRequest
    ora RemainingPreviousMask
    beq Finish
    lda #$87
    sta AudioBank
    jsr RemainingTick
Finish:
    lda #$9d
    bne PublishMixerBank
    nop
; The separate Rogue/SMB2 scheduler jumps here with its own saved A bank.
.assert *-GuestMix = RestoreBank-$f0b2, error, "Preserve external audio return"
    pla
    sta AudioBank
    rts
PublishMixerBank:
    sta AudioBank
    .byte $d0, <(FinishWorker-$f0d8) ; A is still $9d, so this always branches.
.assert *-GuestMix <= $26, error, "Preserve native audio entry"
.res $26-(*-GuestMix),$ea
.endif
