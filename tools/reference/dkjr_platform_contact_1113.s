; Proposed native-only platform footer sampling. No donor rectangle, motor,
; jump, fall threshold, platform placement, native AI or persistent RAM changes.
; The native RunLargePlatform caller kills A/P before their next use.
.setcpu "6502"
SelectedCharacter=$6002
TimerControl=$074a
SavedA=$016a
TargetLo=$016c
TargetHi=$016d
FarCallCommon=$015a
LargePlatformCollision=$b453
PlatformPrepare=$bf5c
PlatformFinish=$bf83
PlayerBottom=$065b
EnemyY=$be
EnemyID=$17

.segment "NATIVE"
DkPlatformDispatch:
    lda SelectedCharacter
    cmp #40
    bne PlatformFallback
    lda EnemyID,x
    cmp #$25
    bcc PlatformFallback
DkContact:
    lda PlayerBottom
    pha
    cmp EnemyY,x
    bcs DkContactReady
    adc #2
    bcs DkContactReady
    sta PlayerBottom
DkContactReady:
    jsr LargePlatformCollision
    pla
    sta PlayerBottom
    rts
PlatformFallback:
    lda #<PlatformGeneric
    sta TargetLo
    jmp PlatformFallbackTail

.segment "RESTORE"
PlatformFallbackTail:
    lda #>PlatformGeneric
    sta TargetHi
    lda #$ba
    jmp FarCallCommon

.segment "GENERIC_A"
PlatformGeneric:
    lda SelectedCharacter
    cmp #11
    bcc PlatformFull
    lda TimerControl
    bne PlatformFull
    jmp NativeCollisionFar
PlatformFull:
    jsr PlatformPrepare
    jmp PlatformFullReturn

.segment "GENERIC_B"
PlatformFullReturn:
    jsr NativeCollisionFar
    sta SavedA
    jmp PlatformFinish
NativeCollisionFar:
    lda #<LargePlatformCollision
    sta TargetLo
    lda #>LargePlatformCollision
    sta TargetHi
    lda #$80
    jmp FarCallCommon
