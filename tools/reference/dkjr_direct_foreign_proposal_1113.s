; SOURCE/FIT PROPOSAL ONLY. Not covered by the current packing amendment.
.setcpu "6502"
Selected=$6002
Timer=$074a
SavedA=$016a
TargetLo=$016c
TargetHi=$016d
Far=$015a
LPC=$b453
Footer=$065b
EnemyID=$17
EnemySpeed=$8f
EnemyY=$be

.segment "RYU"
RyuBridge:
    lda Selected
    cmp #10
    bne RyuNative
    ; RyuPlatformActor repeats ID28 and every source eligibility predicate.
    ; Its wrong-ID path must explicitly return ALLOW/C1.
    lda #$54
    sta TargetLo
    lda #$b8
    sta TargetHi
    lda #$96
    jsr Far
    bcc RyuDone
RyuNative:
    jmp $9a2c
RyuDone:
    rts

.segment "NATIVE"
Dispatch:
    lda Selected
    cmp #40
    bne Generic
    lda #<DkWorker
    sta TargetLo
    lda #>DkWorker
    sta TargetHi
    lda #$ba
    jmp Far
Generic:
    jsr Policy
    bcc Slow
    bne Slow
    jmp LPC
Slow:
    lda #$5c
    jsr LegacyFar
    jsr LPC
    sta SavedA
    lda #$83
LegacyFar:
    sta TargetLo
    lda #$bf
    sta TargetHi
    lda #$ba
    jmp Far

.segment "POLICY"
Policy:
    lda Selected
    cmp #11
    lda Timer
    rts

.segment "WORKER_A"
DkWorker:
    lda Footer
    pha
    lda EnemyID,x
    cmp #$25
    bcc DkNative
    lda EnemySpeed,x
    bmi DkNative
    lda Footer
    cmp EnemyY,x
    bcs DkNative
    adc #2
    jmp SampleReady

.segment "WORKER_B"
SampleReady:
    bcs DkNative
    sta Footer
DkNative:
    lda #$53
    sta TargetLo
    lda #$b4
    sta TargetHi
    lda #$80
    jsr Far
    pla
    sta Footer
    rts
