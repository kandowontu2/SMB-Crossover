.setcpu "6502"

FarA = $016a
FarTarget = $016c
FarCall = $015a
Selected = $6002
ProxyTail = $bf9b

.macro Packet target, bank
    lda #<target
    sta FarTarget
    lda #>target
    sta FarTarget+1
    lda #bank
.endmacro

.segment "POST"
.export GfPostEnemy
GfPostEnemy:
    lda Selected
    cmp #2
    beq Effects
    cmp #5
    beq Effects
    cmp #10
    beq Effects
    cmp #4
    beq Extra
    cmp #42
    bne Done
Extra:
    sta FarA
    Packet $bfe0, $d1
    jsr FarCall
Effects:
    jsr $b93f                 ; Existing effect gate, including stale cleanup.
    beq Done
    ; BF0D immediately stores its input but all enabled bodies then load
    ; their owner and effect state. Foreground result is consumed at $8ACE.
    Packet $bf0d, $cf
    jsr FarCall
Done:
    jmp $8ace
    .res $42-(*-GfPostEnemy),$ea

.segment "PROXY"
.export GfPostProxy
GfPostProxy:
    cmp #4
    beq Link
    Packet $b098, $c1         ; Typed slot 4, with both full header checks.
    .byte $d0, <(ProxyTail-(*+1))
Link:
    Packet $baa7, $c5         ; Exact former direct Link thunk.
    .byte $d0, <(ProxyTail-(*+1))
    .assert *-GfPostProxy=32,error,"Former 32-byte BmName data span"
