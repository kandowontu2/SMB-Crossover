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
R1 = $04
FarTarget = $016c
FarCall = $015a
InitEnemyObject = $a74f
NativeOffscreen = $8ae9
NativeRelative = $8aa0
NativeLargeBBox = $be6f
NativeSmallBBox = $a1cb
DkRefreshSave = $b7ac
FrameSmc = $d2f7
FrameSmcCount = 5
RestoreScratchBase = R0+$100-FrameSmcCount ; Reuse the final SMC loop index.
ActorCount = 13

.segment "BOX"
DkSetPipeBox:
    lda #5
    sta EnemyBox,x
DkPipeCreated:
    jmp RefreshStart

.segment "ROWS"
; World positions in 16-pixel columns. No entry starts on a page boundary.
WorldColumns: .byte 26,30,35,39,43,47,55,59,88,161,165,177,190

.segment "PIPE"
DkPipeScope:
    ldx ScreenLeftPage
    cpx #11
    bcs Reject
    lda AreaDataLow
    cmp #$ce
    bne Reject
    ; Left minus camera is 256..287 iff its column is the projected
    ; column or the next one. R1 is the projected page after rounding.
    lda ScreenLeftX
    adc #14
    tay
    txa
    adc #1
    sta R1
    asl a
    asl a
    asl a
    asl a
    sta R0
    tya
    lsr a
    lsr a
    lsr a
    lsr a
    ora R0
    sta R0
    ldy #ActorCount-1
    sec
Search:
    lda WorldColumns,y
    sbc R0
    bcc Reject
    cmp #2
    bcc Found
    dey
    bpl Search
Reject:
    clc
    rts
Found:
    cpy PipeSeenThrough
    bcc Reject
    sty PipeSeenThrough
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
    ; Admitted placements have nonzero low columns, so their page is R1.
    lda R1
    sta EnemyPage,x
    lda #1
    sta EnemyFlag,x
    sta EnemyYHigh,x
    jsr DkSetPlatformTypeAndPosition
    lda #<InitEnemyObject
    ldy #>InitEnemyObject
    jsr DkNativeFarCall
DkAfterNativeConstructor:
    ; The constructor retains X. The gap actor keeps its native box 6 and
    ; horizontal counters, which share storage with the vertical center.
    ldy PipeSeenThrough
    inc PipeSeenThrough
    lda OscillatorY,y
    beq Continue
    sta PlatformCenterY,x
    jmp DkSetPipeBox
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
    ldx #ObjectOffset-R0
PushScratch:
    lda R0,x
    pha
    dex
    bpl PushScratch
    jsr DkPipeScope
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
    jsr DkNativeBBox
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
    cpx #FrameSmcCount
    bne PopSMC
PopScratch:
    pla
    sta RestoreScratchBase,x
    inx
    cpx #ObjectOffset-R0+FrameSmcCount+1
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
    lda WorldColumns,y
    asl a
    asl a
    asl a
    asl a
    sta EnemyX,x
    cpy #8
    beq Horizontal
    lda #$25
    ldy #192
    bne StoreType
Horizontal:
    lda #$28
    ldy #208
StoreType:
    sta EnemyID,x
    tya
    sta EnemyY,x
    sec
    rts

OscillatorY: .byte 128,128,177,177,169,169,161,161,0,177,128,177,128
DkRefreshPlatformEnd:

.segment "NATIVE_CALL"
DkNativeBBox:
    lda EnemyID,x
    cmp #$2b
    bcc LargeBBox
    lda #<NativeSmallBBox
    ldy #>NativeSmallBBox
    clc
    bcc DkNativeFarCall
LargeBBox:
    lda #<NativeLargeBBox
    ldy #>NativeLargeBBox
DkNativeFarCall:
    sta FarTarget
    sty FarTarget+1
    ; C0 selects OBJECT bank $80; C1 selects LEVEL_TILES bank $82.
    lda #$20
    rol a
    asl a
    jmp FarCall
