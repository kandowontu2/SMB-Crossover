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

.segment "NATIVE"
DkPlatformDispatch:
    sta SavedA
    lda SelectedCharacter
    cmp #40
    beq DkContact
    lda #<PlatformGeneric
    sta TargetLo
    lda #>PlatformGeneric
    sta TargetHi
    lda #$ba
    jmp FarCallCommon
DkContact:
    lda PlayerBottom
    pha
    cmp #254
    bcs DkContactReady
    inc PlayerBottom
    inc PlayerBottom
DkContactReady:
    jmp DkContactRestore

.segment "RESTORE"
DkContactRestore:
    jsr LargePlatformCollision
    pla
    sta PlayerBottom
    rts

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
