.setcpu "6502"

.macro Far target, bank, operation
    lda #<target
    sta $016c
    lda #>target
    sta $016d
    lda #bank
    operation $015a
.endmacro

.segment "TYPED"
; Called only by the existing CoCold frame after blank, SEI, retirement,
; and invalidation. No private code can run before the worker verifies it.
    Far $af40, $fb, jsr
    bcc Done
    lda $6002
    cmp #42
    beq Done                  ; CMP equality keeps worker success carry.
    eor #38
    beq ExistingBootstrap
    eor #14
    lsr a
    bne Done
ExistingBootstrap:
    Far $d25e, 3, jsr         ; Preserve all current Prince, DK and Mini cases.
    bcc Done
    Far $afbf, $c1, jmp       ; Current Prince finalizer and foreign guard.
Done:
    rts
