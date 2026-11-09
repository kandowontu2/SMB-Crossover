.setcpu "6502"
.macpack longbranch
.export DpPlatformTick, DpConfigureRelease, DpPlatformEnd

PlayerCameraPage=$071d
PlayerCameraX=$071f
ScreenWidthPages=1
OffscreenWindow=32
WorldNumber=$0764
LevelNumber=$0761
TimerControl=$074a
GamePauseStatus=$0777
GameEngineSubroutine=$0f
SelectedCharacter=$6002
BehaviorVersion=$7fe1
ObjectOffset=$0d
EnemyFlag=$10
EnemyID=$17
EnemyState=$1f
EnemyPage=$5d
EnemyX=$76
EnemyYHigh=$a5
EnemyY=$be
EnemyBox=$0646
PlatformContact=$0566
Scratch=$03
FarCall=$015a
FarA=$016a
FarTarget=$016c
InitEnemyObject=$a74f
EraseEnemyObject=$8d2f
HpCurrentArea=$ab59
HpReleaseActor=$acdc
HpValid=$7382
HpKey=$7383
HpArea=$7384
HpCharacter=$7385
HpMode=$7386
HpCount=$7387
HpSupport=$7389
HpVisible=$73a8
HpActorSlot=$73ab
HpActorOwner=$73ae
HpSlot=$73d4
DpSupportTag=$d8
DpActorTag=$83

.segment "THOMAS"
.org $b2dd
    lda $b35c,y                ; Six retained native left edges.
    sec
    sbc PlayerCameraX
    sta Scratch
    lda $b362,y
    sbc PlayerCameraPage
    bmi $b34a                  ; Passed, including a resumed room.
    cmp #ScreenWidthPages
    bcc $b34a                  ; The edge has already entered the screen.
    bne $b353                  ; Still more than a full page ahead.
    lda Scratch
    cmp #OffscreenWindow
    bcs $b353
    .res $b303-*, $ea          ; Original free-slot search and constructor.
.reloc

.segment "GOKU_KARNOV"
.proc DpPlatformTick
    lda SelectedCharacter
    cmp #24
    beq Owner
    cmp #34
    jne Done
Owner:
    lda GameEngineSubroutine
    cmp #8
    jne Done
    lda GamePauseStatus
    and #1
    ora TimerControl
    jne Done
    lda WorldNumber
    ora LevelNumber
    bne Outside
    jsr HpCurrentArea
    cmp #$25
    bne Outside
    lda HpValid
    beq Outside
    lda HpCount
    bne Outside
    lda HpArea
    cmp #$25
    bne Outside
    lda HpKey
    bne Outside
    lda HpCharacter
    cmp SelectedCharacter
    bne Outside
    lda HpMode
    cmp BehaviorVersion
    bne Outside
    lda #DpSupportTag
    sta HpSupport

    ldx #0
Scan:
    stx HpSlot
    lda HpVisible,x             ; Each native actor has its own one-shot record.
    bne Next
    lda LeftLo,x
    sec
    sbc PlayerCameraX
    sta Scratch
    lda LeftHi,x
    sbc PlayerCameraPage
    bmi Passed
    cmp #ScreenWidthPages
    bcc Passed
    bne Next
    lda Scratch
    cmp #OffscreenWindow
    bcs Next
    jsr Spawn                   ; A busy allocation retries only while offscreen.
    jmp Next
Passed:
    lda #1
    sta HpVisible,x
Next:
    ldx HpSlot
    inx
    cpx #2
    bcc Scan
    rts

Outside:
    lda HpSupport
    cmp #DpSupportTag
    bne Done
    ldx #1
ReleaseLoop:
    jsr Release
    dex
    bpl ReleaseLoop
    lda #0
    sta HpSupport
Done:
    rts
.endproc

.proc Release
    stx HpSlot
    lda HpActorSlot,x
    beq Clear
    cmp #7
    bcs Clear
    tay
    dey
    txa
    clc
    adc #DpActorTag
    cmp HpActorOwner,y
    bne Clear
    lda #0
    sta HpActorOwner,y
    lda EnemyFlag,y
    cmp #1
    bne Clear
    lda EnemyID,y
    cmp #$25
    bne Clear
    lda EnemyState,y
    cmp #$40
    bne Clear
    lda EnemyX,y
    cmp LeftLo,x
    bne Clear
    lda EnemyPage,y
    cmp LeftHi,x
    bne Clear
    tya
    tax
    jsr EraseEnemyObject
    ldx HpSlot
Clear:
    lda #0
    sta HpActorSlot,x
    sta HpVisible,x
    rts
.endproc

.proc Spawn
    ldy #5
Free:
    lda EnemyFlag,y
    beq Found
    dey
    bpl Free
    rts
Found:
    lda ObjectOffset
    pha
    tya
    tax
    stx ObjectOffset
    ldy HpSlot
    tya
    clc
    adc #DpActorTag
    sta HpActorOwner,x
    txa
    clc
    adc #1
    sta HpActorSlot,y
    lda #$25
    sta EnemyID,x
    lda #1
    sta EnemyFlag,x
    sta EnemyYHigh,x
    lda #0
    sta EnemyState,x
    lda LeftLo,y
    sta EnemyX,x
    lda LeftHi,y
    sta EnemyPage,x
    lda #208
    sta EnemyY,x
    sta FarA
    lda #<InitEnemyObject
    sta FarTarget
    lda #>InitEnemyObject
    sta FarTarget+1
    lda #$82
    jsr FarCall
    ldx ObjectOffset
    lda #5
    sta EnemyBox,x
    lda #$40
    sta EnemyState,x
    lda #$ff
    sta PlatformContact,x
    ldx HpSlot
    lda #1
    sta HpVisible,x
    pla
    sta ObjectOffset
    rts
.endproc

; Area reload and mode/owner rebinding release both old native actors
; before the common configurator clears the existing helper RAM slab.
.proc DpConfigureRelease
    cpx #2
    bcs Shared
    lda HpSupport
    cmp #DpSupportTag
    bne Shared
    jmp Release
Shared:
    jmp HpReleaseActor
.endproc

LeftLo: .byte <688,<872
LeftHi: .byte >688,>872
DpPlatformEnd:
