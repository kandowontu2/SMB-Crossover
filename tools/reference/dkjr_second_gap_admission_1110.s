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
R0 = $03
FarTarget = $016c
FarCall = $015a
InitEnemyObject = $a74f
NativeOffscreen = $8ae9
NativeRelative = $8aa0
NativeLargeBBox = $b7ca
NativeSmallBBox = $b7d9
DkRefreshSave = $b7ac
FrameSmc = $d2f7

.segment "BOX"
DkSetPipeBox:
    lda #5
    sta EnemyBox,x
    jmp RefreshStart

.segment "CAMERA_START"
CameraStart: .byte $81,$11,$51,$61

.segment "WINDOW_MASK"
WindowMask: .byte $bf,$3f,$bf,$ff

.segment "ROWS"
WorldLeft: .byte $a0,$e0,$30,$70,$b0,$f0,$70,$b0,$80
OscillatorY: .byte 128,128,177,177,169,169,161,161

.segment "PIPE"
DkPipeScope:
    ldx ScreenLeftPage
    cpx #3
    bcc PageReady
    cpx #4
    bne Reject
    dex                         ; Camera page four uses the fourth table entry.
PageReady:
    lda AreaDataLow
    cmp #$ce
    bne Reject
    lda ScreenLeftX
    sbc CameraStart,x
    tay
    and WindowMask,x
    cmp #32
    bcs Reject
    tya
    rol a
    rol a
    rol a
    and #3
    adc OrdinalBase,x
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
    ; Empty slot supplies A0. Carry stays set from successful admission.
    adc ScreenLeftPage
    sta EnemyPage,x
    lda #1
    sta EnemyFlag,x
    sta EnemyYHigh,x
    jsr DkSetPlatformTypeAndPosition
    lda #<InitEnemyObject
    sta FarTarget
    lda #>InitEnemyObject
    sta FarTarget+1
    lda #$82
    jsr FarCall
    ; The constructor retains X. The gap actor keeps its native box 6 and
    ; horizontal counters, which share storage with the vertical center.
    ldy PipeSeenThrough
    inc PipeSeenThrough
    cpy #8
    beq Continue
    lda OscillatorY,y
    sta PlatformCenterY,x
    jmp DkSetPipeBox
OrdinalBase: .byte 0,2,6,8
DkPipeEnd:

.segment "REFRESH_TARGET"
    jmp DkPipeTry

.segment "REFRESH"
DkRefreshPlatform:
    php
    pha
    txa
    pha
    tya
    pha
    jsr DkPipeScope
    ; The single refresh pass below handles an empty pool. The save loops
    ; leave scope carry intact for DkPipeTry.
    ldx #7
PushScratch:
    lda R0,x
    pha
    dex
    bpl PushScratch
    lda ObjectOffset
    pha
    jmp DkRefreshSave
RefreshStart:
    ldx #5
RefreshSlot:
    lda EnemyFlag,x
    beq NextRefresh
    bmi NextRefresh
    lda EnemyID,x
    sec
    sbc #$24
    cmp #9
    bcs NextRefresh
    stx ObjectOffset
    jsr NativeOffscreen
    jsr NativeRelative
    lda EnemyID,x
    cmp #$2b
    bcs RefreshSmall
    jsr NativeLargeBBox
    jmp ReloadRefresh
RefreshSmall:
    jsr NativeSmallBBox
ReloadRefresh:
    ldx ObjectOffset
NextRefresh:
    dex
    bpl RefreshSlot
    ldx #0
PopSMC:
    ldy FrameSmc,x
    pla
    sta $0100,y
    inx
    cpx #5
    bne PopSMC
    pla
    sta ObjectOffset
    ldx #0
PopScratch:
    pla
    sta R0,x
    inx
    cpx #8
    bne PopScratch
    pla
    tay
    pla
    tax
    pla
    plp
    rts

DkSetPlatformTypeAndPosition:
    ldy PipeSeenThrough
    lda WorldLeft,y
    sta EnemyX,x
    cpy #8
    lda #$25
    bcc StoreID
    lda #$28
StoreID:
    sta EnemyID,x
    lda #192
    bcc StoreY
    lda #208
StoreY:
    sta EnemyY,x
    rts
DkRefreshPlatformEnd:
