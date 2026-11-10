; Bank26 source-funded wide horizontal manual girder. No new RAM.
.setcpu "6502"
EnemyFlag=$10
EnemyID=$17
EnemyState=$1f
Speed=$47
Travel=$8f
Direction=$0603
PlatformFlag=$0566
HpOwner=$73ae
Selected=$6002
MoveEnemyHorizontally=$8c83
PositionPlayerOnHPlat=$b683
FarCall=$015a
TargetLo=$016c
TargetHi=$016d
R0=$03

.segment "HORIZONTAL"
.export ManualMotionGate,ManualWideHorizontal,ManualSineDecode,ManualHorizontalEnd
ManualMotionGate:
    lda EnemyID,x
    cmp #$28
    bne Native
    lda EnemyState,x
    cmp #$42
    bne Native
    lda HpOwner,x
    bne Native
    lda EnemyFlag,x
    cmp #1
    bne Native
    lda Selected
    cmp #41
    beq ManualWideHorizontal
    cmp #34
    beq ManualWideHorizontal
Native:
    lda EnemyID,x
    sec
    jmp NativeMotionResume

ManualWideHorizontal:
    lda Direction,x
    bne Left
    lda Travel,x
    cmp #112
    bcc Right
    inc Direction,x
Left:
    lda Travel,x
    beq TurnRight
    dec Travel,x
    lda #$f0
    bne Move
TurnRight:
    dec Direction,x
Right:
    inc Travel,x
    lda #$10
Move:
    sta Speed,x
    jsr MoveEnemyHorizontally
    ; Fixed ±$10 has fractional low nibble0: native R0 and A are ±1.
    lda PlatformFlag,x
    bmi Done
    lda #<PositionPlayerOnHPlat
    sta TargetLo
    lda #>PositionPlayerOnHPlat
    sta TargetHi
    lda #$80
    jmp FarCall
Done:
    rts

; Exact binary search of the monotone quantized original256-entry table.
; Threshold[i] is the last sample before amplitude i; i31 is sentinel255.
; HpTemp2 is already the original output cell. Signed tail restores sourceX.
ManualSineDecode:
    php
    tya
    pha
    lda #0
    sta HpTemp2
    ldx #16
Search:
    txa
    ora HpTemp2
    tay
    lda ManualSineThresholds,y
    cmp HpSineIndex
    bcs Skip
    sty HpTemp2
Skip:
    txa
    lsr a
    tax
    bne Search
    pla
    tay
    plp
    lda HpTemp2
    rts
ManualSineThresholds:
    .incbin "thresholds.bin"
ManualHorizontalEnd:
