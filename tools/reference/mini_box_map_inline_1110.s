.setcpu "6502"

CurrentBankC = $7da1
BankCPort = $5116
Epoch = $c3f0
FrameCounter = $0e
ReturnA = $0179
LiveHeader = $b06b
RestoreC = $b07b

.macro MapCInline
    sta CurrentBankC
    sta BankCPort
.endmacro

.segment "BANK_GATE"
CheckMini:
    lda CurrentBankC
    pha
    lda #2
    MapCInline
    lda FrameCounter
    beq Miss
    cmp Epoch
    bne Miss
    jsr LiveHeader
    bcc Miss
    jmp CheckCodeHeader
Miss:
    clc
    jmp RestoreC
    .assert *-CheckMini=33,error,"Inline state map footprint"
    .res 36-(*-CheckMini),$ff

.segment "BANK_CODE_HEADER"
CheckCodeHeader:
    lda #3
    MapCInline
    jsr LiveHeader
    jmp RestoreC
    .assert *-CheckCodeHeader=14,error,"Inline code map footprint"
    .res 16-(*-CheckCodeHeader),$ff

.segment "RESTORE86"
MiniBoxRestore:
    pla
    MapCInline
    lda ReturnA
    rts
    .assert *-MiniBoxRestore=11,error,"Inline return map footprint"
    .res 12-(*-MiniBoxRestore),$ea
