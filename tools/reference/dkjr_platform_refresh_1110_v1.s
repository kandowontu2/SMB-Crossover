; Preserve actual mutable farcall operands without stacking the RAM program.
; Two retired private wrappers only mapped a bank to enter fixed low code.
.export DkRefreshPlatform, DkRefreshPlatformEnd, DkRefreshSave, DkRefreshSaveEnd

EnemyFlag = $10
EnemyID = $17
ObjectOffset = $0d
R0 = $03
FarCallCommon = $015a
TargetLo = $016c
TargetHi = $016d
NativeOffscreen = $8ae9
NativeRelative = $8aa0
NativeLargeBBox = $b7ca
NativeSmallBBox = $b7d9
FrameSmc = $d2f7

.segment "REFRESH"
DkRefreshPlatform:
    php
    pha
    txa
    pha
    tya
    pha
    ldx #5
FindPlatform:
    lda EnemyFlag,x
    beq FindNext
    bmi FindNext
    lda EnemyID,x
    cmp #$24
    bcc FindNext
    cmp #$2d
    bcc HasPlatform
FindNext:
    dex
    bpl FindPlatform
    jmp RefreshReturn
HasPlatform:
    ldx #7
PushScratch:
    lda R0,x
    pha
    dex
    bpl PushScratch
    lda ObjectOffset
    pha
.ifdef ORIGINAL
    ldx #32
PushSMC:
    lda $015a,x
    pha
    dex
    bpl PushSMC
.else
    jmp DkRefreshSave
.endif
RefreshStart:
    ldx #5
RefreshSlot:
    lda EnemyFlag,x
    beq NextRefresh
    bmi NextRefresh
    lda EnemyID,x
    cmp #$24
    bcc NextRefresh
    cmp #$2d
    bcs NextRefresh
    stx ObjectOffset
.ifdef ORIGINAL
    jsr DkRefreshSave
    jsr OldRelative
.else
    jsr NativeOffscreen
    jsr NativeRelative
.endif
    ldx ObjectOffset
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
.ifdef ORIGINAL
    pla
    sta $015a,x
    inx
    cpx #33
.else
    ldy FrameSmc,x
    pla
    sta $0100,y
    inx
    cpx #5
.endif
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
RefreshReturn:
    pla
    tay
    pla
    tax
    pla
    plp
    rts
    .res $81-(*-DkRefreshPlatform), $ea
DkRefreshPlatformEnd:

.segment "ALIASES"
DkRefreshSave:
.ifdef ORIGINAL
    lda #<NativeOffscreen
    sta TargetLo
    lda #>NativeOffscreen
    sta TargetHi
    lda #$fe
    jmp FarCallCommon
OldRelative:
    lda #<NativeRelative
    sta TargetLo
    lda #>NativeRelative
    sta TargetHi
    lda #$fe
    jmp FarCallCommon
.else
    ldx #4
SaveSMC:
    ldy FrameSmc,x
    lda $0100,y
    pha
    dex
    bpl SaveSMC
    jmp RefreshStart
.endif
    .res 30-(*-DkRefreshSave), $ea
DkRefreshSaveEnd:
