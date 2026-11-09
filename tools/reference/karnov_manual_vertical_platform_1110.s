; Karnov's held/pressed fields are donor bit order. Up=$10, Select=$04.
; Only the option cycle edge is suppressed while the complete chord is held.
.setcpu "6502"
.export KrManualIngress, KrManualIngressEnd, KrManualOptions, KrManualOptionsEnd
.export KrManualReset, KrManualResetEnd

KrHeld = $c01b
KrPressed = $c021
KrManualPending = $c866
KrTerrainResult = $c800
KrOptionsControls = $dbf8
ManualPlatform = $b378
FarTarget = $016c
FarCallCommon = $015a

.segment "KR_MANUAL_INGRESS"
KrManualIngress:
    lda #<KrManualOptions
    sta FarTarget
    lda #>KrManualOptions
    sta FarTarget+1
    lda #$8b
    jsr FarCallCommon
    jmp KrOptionsControls
KrManualIngressEnd:

.segment "KR_MANUAL_RESET"
KrManualReset:
    sta KrTerrainResult      ; Original scene-reset store (A=0).
    sta KrManualPending
    rts
KrManualResetEnd:

.segment "KR_MANUAL_OPTIONS"
KrManualOptions:
    php
    lda KrHeld
    and #$14
    cmp #$14
    bne Pending
    lda KrPressed
    pha
    and #$fb
    sta KrPressed
    pla
    and #$14                 ; Either key can complete the chord.
    bne Spawn
Pending:
    bit KrManualPending
    bpl Done
Spawn:
    txa
    pha
    tya
    pha
    ldy #$f8                 ; Player X+8 minus half the native 32px girder.
    lda #<ManualPlatform
    sta FarTarget
    lda #>ManualPlatform
    sta FarTarget+1
    lda #$c0
    jsr FarCallCommon
    sta KrManualPending
    pla
    tay
    pla
    tax
Done:
    plp
    rts
KrManualOptionsEnd:
