.setcpu "6502"
.export GiantAmmoLookup, GiantMenuName, GiantScene, GiantSceneRetire
.export GiantSceneCommit, GiantSceneEnd, GiantAudioMux
.export GiantTailClear, GiantTailMario, GiantDrawOwner, GiantStageDraw

.segment "GIANT_MENU"

; The original reader takes an arbitrary X. Preserve the source table's
; 192 values, the out-of-table indexed results, and non-NZ status bits.
GiantAmmoLookup:
    php
    cpx #$c0
    bcs LegacyAmmo
    cpx #$91
    bcs Late
    cpx #$50
    beq NinetyNine
    cpx #$41
    bcc Early
    cpx #$43
    bcc Twenty
    bcs Zero
Early:
    cpx #$22
    beq Twenty
    cpx #$11
    bcc Zero
    cpx #$19
    bcc OneTwelve
    bcs Zero
Late:
    cpx #$98
    bcc OneTwelve
    cpx #$a0
    beq Fifty
    cpx #$b1
    beq Sixty
    cpx #$b2
    beq Twenty
    cpx #$b3
    bne Zero
    lda #8
    bne ReturnAmmo
Fifty:
    lda #50
    bne ReturnAmmo
Sixty:
    lda #60
    bne ReturnAmmo
Twenty:
    lda #20
    bne ReturnAmmo
NinetyNine:
    lda #99
    bne ReturnAmmo
OneTwelve:
    lda #112
    bne ReturnAmmo
Zero:
    lda #0
ReturnAmmo:
    plp
    ora #0
    rts
LegacyAmmo:
    plp
    lda $a7b2,x
    rts

GiantMenuName:
    php
    pha
    lda CrossoverMenuIndex
    bne StockName
    lda MarioVariant
    cmp #9
    bne StockName
    pla
    plp
    ldx VRAM_Buffer1_Offset
    lda #$23
    sta VRAM_Buffer1,x
    lda #$28
    sta VRAM_Buffer1+1,x
    lda #16
    sta VRAM_Buffer1+2,x
    ldy #0
NameLoop:
    lda GiantName,y
    sta VRAM_Buffer1+3,x
    inx
    iny
    cpy #16
    bcc NameLoop
    inx
    inx
    inx
    stx VRAM_Buffer1_Offset
    lda #0
    sta VRAM_Buffer1,x
    rts
StockName:
    pla
    plp
    lda #$20
    sta $016c
    lda #$b7
    sta $016d
    lda #$cf
    sta $0162
    pla
    pla
    jmp $0161
GiantName:
    .byte $16,$0e,$10,$0a,$24,$10,$12,$0a,$17,$1d,$24,$16,$0a,$1b,$12,$18

.segment "GIANT_SCENE"

.macro Far Target, Bank
    lda #<Target
    sta $016c
    lda #>Target
    sta $016d
    lda #Bank
    jsr $015a
.endmacro

; Entered at the real bank3 blank-screen scene packet. Preserve its
; public input and forward every scene to the incumbent Mini/native mux.
GiantScene:
    php
    pha
    txa
    pha
    tya
    pha
    lda CurrentBankC
    pha
    lda #2
    jsr MapC
    lda SelectedCharacter
    beq CheckMario
    jmp ForeignScene
CheckMario:
    lda MarioVariant
    cmp #9
    bne ForeignScene
    lda OperMode
    cmp #1
    bne ForeignScene
    lda FamilyMainCommit
    and #1
    beq ForeignScene
    jsr Header
    bcc Cold
    lda #3
    jsr MapC
    jsr Header
    bcs SceneFinish
Cold:
    sei
    Far $ae0a,$c1                ; authentic incumbent owner retirement
    ldx #7
PushDescriptor:
    lda Descriptor,x
    pha
    dex
    bpl PushDescriptor
    tsx
    inx
    stx R3
    lda #1
    sta R4
    Far $af40,$fb                ; real buffered copier and readback
    ldx #8
PopDescriptor:
    pla
    dex
    bne PopDescriptor
    bcc RestorePpu
GiantSceneCommit:
    ldx #3
PublishHeader:
    txa
    jsr MapC
    ldy #15
HeaderByte:
    lda SceneCookie,y
    sta $dfe0,y                 ; validity byte is published last
    dey
    bpl HeaderByte
    dex
    cpx #1
    bne PublishHeader
RestorePpu:
    Far $af97,$c1                ; real CHR/scroll restoration from mirrors
    jmp SceneFinish
ForeignScene:
    jsr Header
    bcc SceneFinish
GiantSceneRetire:
    lda #0
    sta $dfe0
    lda #3
    jsr MapC
    jsr Header
    bcc SceneFinish
    lda #0
    sta $dfe0
SceneFinish:
    pla
    jsr MapC
    pla
    tay
    pla
    tax
    pla
    plp
    sta $016a
    lda #$13
    sta $016c
    lda #$b0
    sta $016d
    lda #$c1
    sta $0162
    pla
    pla
    jmp $0161

Header:
    ldy #15
CompareHeader:
    lda $dfe0,y
    cmp SceneCookie,y
    bne NoHeader
    dey
    bpl CompareHeader
    rts
NoHeader:
    clc
    rts
MapC:
    sta CurrentBankC
    sta $5116
    rts
SceneCookie:
    .byte GIANT_SCENE_SIGNATURE
Descriptor:
    ; The immutable copy geometry is also the last four cookie bytes.
    .byte 2,1,1,$d0,214,0,212,0
GiantSceneEnd:

.segment "GIANT_AUDIO_MUX"

; Retain actual mapper writes for the Rogue canonical zero view.
GiantAudioMux:
    ora #$80
    sta $0145
    sta $5115
    ldy #0
    eor #$d4
    beq ReadCanonicalPage
    jsr $b705                   ; incumbent virtual bank90 view
    jmp $c438
ReadCanonicalPage:
    jmp GiantRogue84Read

.segment "GIANT_SCENE_TAIL"

; Original $D4:BE is all zero. The reclaimed prefix of $D4:BF is zero;
; all later bytes still come from the authored physical audio page.
GiantRogue84Read:
    lda $e9
    eor #$be
    beq CanonicalZero
    php
    lda $e8
    cmp #$66
    bcc PrefixZero
    plp
    lda ($e8),y
    jmp $c438
PrefixZero:
    plp
CanonicalZero:
    lda #0
    jmp $c438

; This is reached after native clear/actors. Validate both actual shared
; headers before any execution from RAM3, and restore the C window.
GiantDrawOwner:
    lda SelectedCharacter
    bne DrawReturn
    lda MarioVariant
    cmp #9
    bne DrawReturn
    lda OperMode
    cmp #1
    bne DrawReturn
    lda GameEngineSubroutine
    cmp #8
    bne DrawReturn
    lda CurrentBankC
    pha
    lda #3
    jsr MapC
    jsr Header
    bcc RestoreDraw
    lda #2
    jsr MapC
    jsr Header
    bcc RestoreDraw
    Far GiantStageDraw,3
RestoreDraw:
    pla
    jsr MapC
DrawReturn:
    lda #$f8
    rts

.segment "GIANT_TAIL_CLEAN"

; Reproduce the nonrotating native OAM tail clear with the saved world
; cursor. Mini's selected draw chain never enters the patched tail.
GiantTailClear:
    pha
    lsr
    sta M0
    lsr
    adc M0
    adc #$2c
    sta M0
    lda #$a3                     ; 3*(252/4)+$2c is at most $e9
    sta M1
    lda #$f8
    sta $016a
    lda #$b5
    sta $016c
    lda #$85
    sta $016d
    jmp GiantTailMario

.segment "GIANT_TAIL_OWNER"
GiantTailMario:
    ; Fixed native clear dispatches through a bank4 unrolled table.
    lda #$84
    jsr $015a
    php
    txa
    pha
    tsx
    lda $0103,x                 ; original native actor-end cursor
    tax
    Far GiantDrawOwner,$d4
    pla
    tax
    plp
    pla
    lda #$f8
    rts

.segment "GIANT_STAGE_DRAW"

; Live host pose projection into the original donor row numbers. The
; selected body geometry and CHR match the donor; the original state/timer
; ownership across every power/death transition is a separate component.
GiantStageDraw:
    lda Player_State
    beq StandingPose
    cmp #1
    beq JumpPose
    cmp #3
    beq ClimbPose
    lda #1
    bne EmitPose
StandingPose:
    lda CrouchingFlag
    bne CrouchPose
    lda Player_X_Speed
    ora Left_Right_Buttons
    beq IdlePose
    lda PlayerAnimCtrl
    and #3
    cmp #3
    bcc :+
    lda #0
:
    clc
    adc #1
    bne EmitPose
JumpPose:
    lda #5
    bne EmitPose
ClimbPose:
    lda #9
    bne EmitPose
CrouchPose:
    lda #11
    bne EmitPose
IdlePose:
    lda #0
EmitPose:
    jmp $a000                   ; existing authenticated Giant renderer
