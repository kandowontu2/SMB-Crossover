.setcpu "6502"

Player_PageLoc = $5c
Player_X_Position = $75
SelectedCharacter = $6002
AreaAddrsLOffset = $0754
LevelNumber = $0761
WorldNumber = $0764
FarCallCommon = $015a
SafecallA = $016a
FarcallJmpTarget = $016c
MiniLiftSeen = $c30c
MiniLiftAllocateBank = $bfeb
PublishBits = $bffd

.segment "MINI_LIFT_SCAN"
; Called only by the authenticated Mini Main. The downstream scope still
; checks raw 41 before any owned writes or native allocation.
MiniLiftTick:
    ldy #2
FindWindow:
    lda Player_PageLoc
    cmp Page,y
    bne Next
    lda Player_X_Position
    sbc Minimum,y             ; Equal page comparison established carry.
    cmp #80
    bcc Candidate
Next:
    dey
    bpl FindWindow
NoCandidate:
    rts
Candidate:
    lda MiniLiftSeen
    and ScanBits,y
    bne NoCandidate
    lda Minimum,y
    ora #$20
    sta SafecallA
    jmp MiniLiftScopeBank
Page: .byte 2,2,3
Minimum: .byte $10,$90,$40

.segment "MINI_LIFT_SCAN_CALL"
MiniLiftScopeBank:
    lda #<MiniLiftScope
    sta FarcallJmpTarget
    lda #>MiniLiftScope
    sta FarcallJmpTarget+1
    lda #$bd
    jmp FarCallCommon
ScanBits: .byte 1,2,4

.segment "MINI_LIFT_SCOPE"
MiniLiftScope:
    lda SelectedCharacter
    cmp #41
    bne ScopeDone
    lda WorldNumber
    ora LevelNumber
    bne ScopeDone
    lda AreaAddrsLOffset
    cmp #5
    bne ScopeDone
    lda PublishBits,y
    pha
    jmp MiniLiftAllocateBank
PublishSeen:
    .assert PublishSeen = $b3b9, lderror, "Existing scope return stays fixed"
    pla
    bcs ScopeDone
    ora MiniLiftSeen
    sta MiniLiftSeen
ScopeDone:
    rts
