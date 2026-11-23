.setcpu "6502"

FarLo = $016c
FarHi = $016d
FrameCounter = $0e
CurrentBankC = $7da1
MapperC = $5116
MapC = $80c2
ValidatedFrame = $dfdf
LiveHeader = $dfe0
ExpectedHeader = $bac5
DispatchReady = $b8ab
DispatchFailed = $bfa2
PlatformRequest = $bf90

.segment "ROOT"
    ; Only game-routine calls within Main can share a validation. The
    ; pause service has a separate return address and still checks in full.
    lda $01f9
    cmp #$52
    bne RootFull
    jmp Foreground
RootFull:
    jmp Full

.segment "EPOCH"
Foreground:
    lda FarLo
    beq Full
    lda $01fa
    cmp #$83
    bne Full
    lda #2
    jsr MapC
    lda FrameCounter
    beq Full
    cmp ValidatedFrame
    bne Full
    ; Both banks still check their four owner and revision bytes.
    lda #3
    bne CheckBanks
Full:
    lda #15
CheckBanks:
    jmp ReadBanks

.segment "HEADER"
ReadBanks:
    ; The original dispatch frame retains FarHi. The transport restores
    ; it on rejection and overwrites it with the service page on success.
    sta FarHi
    ldx #3
ReadBank:
    stx CurrentBankC
    stx MapperC
    ldx FarHi
ReadByte:
    lda LiveHeader,x
    cmp ExpectedHeader,x
    bne DispatchFailed
    dex
    bpl ReadByte
    ldx CurrentBankC
    dex
    cpx #1
    bne ReadBank
    lda FrameCounter
    sta ValidatedFrame
SelectService:
    lda FarLo
    cmp #$3c
    beq PlatformRequest
    lda #$a0
    sta FarHi
    jmp DispatchReady
