.setcpu "6502"

; Draft native OBJECT-bank service: no physical placement is granted yet.
; Caller is only DK's authenticated platform refresh. Scope additionally
; excludes other rooms, authored NPC kinds, disabled states and passengers.
.segment "RETIRE"
DkHelperRetireOrBBox:
    lda EnemyID,x
    cmp #$2b
    bcs SmallBBox
    cmp #$25
    bne LargeBBox
    lda SelectedCharacter
    cmp #40
    bne LargeBBox
    lda EnemyFlag,x
    cmp #1
    bne LargeBBox
    lda EnemyState,x
    bne LargeBBox
    lda WorldNumber
    ora LevelNumber
    bne LargeBBox
    lda AreaDataLow
    cmp #$ce
    bne LargeBBox
    lda EnemyBox,x
    cmp #5
    bne LargeBBox
    lda PlatformCollision,x
    bpl LargeBBox
    ; All current normal1-1 visual cells end at left+47, collision at+32.
    ; Requiring left+48 < camera adds one conservative pixel. Keep 16 bits.
    sec
    lda ScreenLeftX
    sbc EnemyX,x
    sta R0
    lda ScreenLeftPage
    sbc EnemyPage,x
    bcc LargeBBox
    bne Retire
    lda R0
    cmp #49
    bcs Retire
LargeBBox:
    jmp NativeLargeBBox
Retire:
    jmp NativeErase
SmallBBox:
    jmp NativeSmallBBox
DkHelperRetireEnd:
