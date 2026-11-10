.setcpu "6502"

AreaDataLow = $d6
ScreenLeftPage = $071d
ScreenLeftX = $071f
PipeSeenThrough = $c8fd
EnemyFlag = $10
EnemyID = $17
PlatformCenterY = $47
EnemyPage = $5d
EnemyX = $76
EnemyYHigh = $a5
EnemyY = $be
EnemyBox = $0646
ObjectOffset = $0d
FarTarget = $016c
FarCall = $015a
InitEnemyObject = $a74f
RefreshStart = $b654

.segment "BOX"
DkSetPipeBox:
    lda #5
    sta EnemyBox,x
DkPipeCreated:
    jmp RefreshStart

.segment "CAMERA_START"
CameraStart: .byte $81,$11

.segment "WORLD_LEFT"
WorldLeft: .byte $a0,$e0,$30,$70

.segment "PIPE"
DkPipeScope:
    ldx ScreenLeftPage
    cpx #2
    bcs Reject
    ; Loaded AreaData identifies the actual 1-1 map, including return trips.
    ; The mutable AreaPointer can already name the underground destination.
    lda AreaDataLow
    cmp #$ce
    bne Reject
    lda ScreenLeftX
    sbc CameraStart,x
    tay
    and #$bf
    cmp #32
    bcs Reject
    tya
    cmp #$40
    txa
    rol a
    cmp PipeSeenThrough
    bcc Reject
    sta PipeSeenThrough
    rts
Reject:
    clc
    rts

DkPipeTry:
    bcc Continue
    ldx #5
Find:
    lda EnemyFlag,x
    beq Birth
    dex
    bpl Find
Continue:
    jmp RefreshStart
Birth:
    stx ObjectOffset
    ldy PipeSeenThrough
    lda WorldLeft,y
    sta EnemyX,x
    lda #1
    sta EnemyFlag,x
    sta EnemyYHigh,x
    clc
    adc ScreenLeftPage
    sta EnemyPage,x
    lda #$25
    sta EnemyID,x
    lda #192
    sta EnemyY,x
    lda #<InitEnemyObject
    sta FarTarget
    lda #>InitEnemyObject
    sta FarTarget+1
    lda #$82
    jsr FarCall
    ; The stock vertical constructor retains X. The taller second pipe uses
    ; a nearer motion center. Page 1 keeps the first pair's native trajectory.
    lda EnemyPage,x
    lsr a
    bcs KeepCenter
    lda #177
    sta PlatformCenterY,x
KeepCenter:
    inc PipeSeenThrough
    jmp DkSetPipeBox
    .byte $ea
DkPipeEnd:
