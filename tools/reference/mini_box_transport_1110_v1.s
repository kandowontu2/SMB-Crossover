.setcpu "6502"

CurrentBankC = $7da1
MapC = $80c2
TargetLo = $016c
TargetHi = $016d
FarCall = $015a
ReturnA = $0179
MiniBoxService = $b0bc
NativeBox = $9f4e
MiniBoxVector = $a030

.export MiniBoxStage, MiniBoxProbe, MiniBoxMiss, MiniBoxRestore

.segment "STAGE86"
MiniBoxStage:
    php
    lda #<MiniBoxService
    sta TargetLo
    lda #>MiniBoxService
    sta TargetHi
    jmp MiniBoxProbe
    .res 15-(*-MiniBoxStage),$ea

.segment "PROBE86"
MiniBoxProbe:
    ; The same D5 veneer performs the original nonzero epoch and both
    ; live header checks. No WRAM window remains mapped on its return.
    lda #$d5
    jsr FarCall
    bcs Warm
    jmp MiniBoxMiss
Warm:
    plp
    lda CurrentBankC
    pha
    lda #2
    jsr MapC
    lda #<MiniBoxVector
    sta TargetLo
    lda #>MiniBoxVector
    sta TargetHi
    lda #3
    jsr FarCall
    jmp MiniBoxRestore
    .assert *-MiniBoxProbe=38,error,"Reclaimed lifecycle footprint"

.segment "FALLBACK86"
MiniBoxMiss:
    plp
    ; The incumbent full-cookie route and stock rejection remain intact.
    lda #$c1
    jsr FarCall
    bcs Done
    jmp NativeBox
Done:
    rts
    .res 15-(*-MiniBoxMiss),$ea

.segment "RESTORE86"
MiniBoxRestore:
    pla
    jsr MapC
    lda ReturnA
    rts
    .res 12-(*-MiniBoxRestore),$ea
