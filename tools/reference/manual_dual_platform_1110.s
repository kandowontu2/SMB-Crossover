; Shared constructor. X=$41/$42 selects the owned axis, Y is signed left offset.
.setcpu "6502"
.export ManualPlatform, ManualPlatformCreated, ManualPlatformEnd, ManualPlatformTailEnd
EnemyFlag=$10
EnemyID=$17
EnemyState=$1f
PlayerPage=$5c
EnemyPage=$5d
PlayerX=$75
EnemyX=$76
PlayerHigh=$a4
EnemyHigh=$a5
PlayerY=$bd
EnemyY=$be
Floatey=$010d
EnemyBox=$0646
HpOwner=$73ae
EraseEnemyObject=$8d2f
FarTarget=$016c
FarCall=$015a
CheckpointEnemyID=$b67f
Offset=$03
WantID=$04
WantMarker=$05

.segment "MANUAL"
ManualPlatform:
    lda PlayerHigh
    cmp #1
    bne Retry
    lda PlayerY
    cmp #208
    bcc Prepare
Retry:
    ldx #$80
    txa
    rts
Prepare:
    stx WantMarker
    txa
    lsr a
    lda #$25
    bcs Kind
    lda #$28
Kind:
    sta WantID
    txa
    pha
    tya
    pha
    ldy #$ff
    ldx #5
Find:
    lda HpOwner,x
    bne Next
    lda EnemyFlag,x
    lsr a
    bne Next
    bcc Empty
    lda EnemyID,x
    cmp WantID
    bne Next
    lda EnemyState,x
    cmp WantMarker
    beq Spawn
    bne Next
Empty:
    lda Floatey,x
    bne Next
    txa
    tay
Next:
    dex
    bpl Find
    tya
    bpl Free
    pla
    pla
    jmp Retry
Free:
    tax
Spawn:
    jsr EraseEnemyObject
    pla
    sta Offset
    pla
    sta EnemyState,x
    lsr a
    lda #$25
    bcs SetID
    lda #$28
SetID:
    sta EnemyID,x
    lda Offset
    clc
    adc PlayerX
    sta EnemyX,x
    lda #0
    bit Offset
    bpl AddPage
    lda #$ff
AddPage:
    adc PlayerPage
    sta EnemyPage,x
    bit Offset
    bpl Position
    bcs Position
    lda #0
    sta EnemyPage,x
    sta EnemyX,x
Position:
    lda PlayerY
    jmp ManualPositionTail
ManualPlatformEnd:

.segment "MANUAL_TAIL"
ManualPositionTail:
    clc
    adc #32
    sta EnemyY,x
    lda #1
    sta EnemyFlag,x
    sta EnemyHigh,x
    lda #<CheckpointEnemyID
    sta FarTarget
    lda #>CheckpointEnemyID
    sta FarTarget+1
    lda #$87
    jsr FarCall
    lda #5
    sta EnemyBox,x
ManualPlatformCreated:
    inx
    txa
    rts
ManualPlatformTailEnd:
