; Native manual input for selected22/29. The three named helper bytes were
; retired scratch in the existing91-byte slab; HpConfigure remains reset owner.
; Caller ingress is separately source-funded and qualified. No guest body code.
.setcpu "6502"
.macpack longbranch
.export ManualRosterInput,ManualRosterInputHeadEnd,ManualRosterInputEnd
.export RosterVerticalDecode,RosterVerticalDecodeEnd
.export ManualRosterDispatch,ManualRosterSkipEmpty
.ifndef Selected
Selected=$6002
.endif
CurrentPlayer=$0758
SavedJoypadBits=$dc
OperMode=$0771
OperTask=$0773
Engine=$0f
Pause=$0777
Timer=$074a
Death=$6007
HpCount=$7387
HpSpawnAndTrack=$ad0b
NativeDispatcherResume=$b137
PreviousChord=$73d1
VerticalPending=$73d2
HorizontalPending=$73d3
FarTarget=$016c
.ifndef FarCall
FarCall=$015a
.endif
ManualConstructor=$b378
.ifndef R0
R0=$03
.endif

.segment "ROSTER_INPUT_HEAD"
ManualRosterInput:
    php
    pha
    lda Selected
    cmp #22
    beq Owned
    cmp #29
    beq Owned
    pla
    plp
    rts
Owned:
    txa
    pha
    tya
    pha
    ldx #7
SaveScratch:
    lda R0,x
    pha
    dex
    bpl SaveScratch
    ldx CurrentPlayer
    lda SavedJoypadBits,x
    and #$2c
    ora #$80                 ; zero means newly reset, with no prior sample.
    tax
    lda OperMode
    cmp #1
    jne Inactive
    lda OperTask
    cmp #3
    jne Inactive
    jmp ActiveChecks
Spawn:
    lda #<ManualConstructor
    sta FarTarget
    lda #>ManualConstructor
    sta FarTarget+1
    lda #$c0
    jmp FarCall
; The JSR ends at the next table boundary, where its return resumes below.
ManualRosterDispatch:
    jsr ManualRosterInput
ManualRosterInputHeadEnd:

.segment "ROSTER_VERTICAL"
    lda Selected
    jmp NativeDispatcherResume
; Exact threshold search of the monotone source HpSineVertical256-entry table.
; Candidate>=76 is skipped explicitly, so the source requires only76 bytes.
; Original P/Y are restored and the existing HpTemp2 output is reused.
RosterVerticalDecode:
    php
    tya
    pha
    lda #0
    sta HpTemp2
    ldx #64
VerticalSearch:
    txa
    ora HpTemp2
    tay
    cmp #76
    bcs VerticalSkip
    lda RosterVerticalThresholds,y
    cmp HpSineIndex
    bcs VerticalSkip
    sty HpTemp2
VerticalSkip:
    txa
    lsr a
    tax
    bne VerticalSearch
    pla
    tay
    plp
    lda HpTemp2
    rts
RosterVerticalThresholds:
    .incbin "vertical-thresholds.bin"
RosterVerticalDecodeEnd:

ActiveChecks:
    lda Engine
    cmp #8
    bne Inactive
    lda Pause
    and #1
    ora Timer
    ora Death
    bne Inactive
    ldy PreviousChord
    stx PreviousChord
    tya
    beq Pending
    eor PreviousChord
    beq Pending
    txa
    cmp #$a8
    beq VerticalEdge
    cmp #$a4
    bne Pending
    lda #$80
    sta HorizontalPending
    bmi Pending
VerticalEdge:
    lda #$80
    sta VerticalPending
Pending:
    lda VerticalPending
    bpl Horizontal
    ldx #$41
    ldy #$f8                 ; native32px platform left = playerX+8-16.
    jsr Spawn
    stx VerticalPending
Horizontal:
    lda HorizontalPending
    bpl Leave
    ldx #$42
    ldy #24                  ; always right, independently of player facing.
    jsr Spawn
    stx HorizontalPending
    jmp Leave
Inactive:
    stx PreviousChord
    lda #0
    sta VerticalPending
    sta HorizontalPending
Leave:
    ldx #0
RestoreScratch:
    pla
    sta R0,x
    inx
    cpx #8
    bne RestoreScratch
    pla
    tay
    pla
    tax
    pla
    plp
    rts
; Former fixed-bridge rejects still leave the exact Selected/CMP34 result.
; Never configure or advance authored helpers merely because a new raw ID
; traversed the broadened fixed bridge with HpCount0.
ManualRosterSkipEmpty:
    lda HpCount
    beq EmptyReturn
    jmp HpSpawnAndTrack
EmptyReturn:
    lda Selected
    cmp #34
    rts
ManualRosterInputEnd:
