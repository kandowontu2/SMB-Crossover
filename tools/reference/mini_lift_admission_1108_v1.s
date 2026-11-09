.setcpu "6502"
.import MiniLiftSpawn
.export MiniLiftTick, MiniLiftAllocate, MiniLiftScope

Enemy_Flag = $10
Enemy_ID = $17
Enemy_State = $1f
Player_PageLoc = $5c
Player_X_Position = $75
SelectedCharacter = $6002
AreaAddrsLOffset = $0754
LevelNumber = $0761
WorldNumber = $0764
FarCallCommon = $015a
SafecallA = $016a
FarcallJmpTarget = $016c
MiniLiftActor = $c30b
MiniLiftSeen = $c30c

; SafecallA remains the authored left edge low byte across both routing
; leaves. All leaves are Main-only with the authenticated Mini C2 mapped.
.macro MapTarget Addr, Tag
    lda #<Addr
    sta FarcallJmpTarget
    lda #>Addr
    sta FarcallJmpTarget+1
    lda #Tag
.endmacro

.segment "MINI_LIFT_SCAN"
; Native selected Mini Main calls this only in its active movement update.
; Each window begins 32 px before a lift and ends at the pipe left edge.
MiniLiftTick:
    lda SelectedCharacter
    cmp #41
    bne NoCandidate
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
    lda Minimum,y
    ora #$20                 ; Each minimum has bit5 clear, left is +32.
    sta SafecallA
    jmp MiniLiftScopeBank
Page: .byte 2,2,3
Minimum: .byte $10,$90,$40

.segment "MINI_LIFT_SCAN_CALL"
MiniLiftScopeBank:
    MapTarget MiniLiftScope, $bd
    jmp FarCallCommon

.segment "MINI_LIFT_SCOPE"
MiniLiftScope:
    lda WorldNumber
    ora LevelNumber
    bne ScopeDone
    lda AreaAddrsLOffset
    cmp #5                   ; Stable loaded 1-1 area, not pipe destination.
    bne ScopeDone
    lda Bits,y
    pha
    and MiniLiftSeen
    bne AlreadySeen
    jmp MiniLiftAllocateBank
AlreadySeen:
    pla
ScopeDone:
    rts
PublishSeen:
    pla
    bcs ScopeDone            ; All six native slots busy. Retry later.
    ora MiniLiftSeen
    sta MiniLiftSeen
    rts

.segment "MINI_LIFT_SCOPE_CALL"
MiniLiftAllocateBank:
    MapTarget MiniLiftAllocate, $a4
    jsr FarCallCommon
    jmp PublishSeen
Bits: .byte 1,2,4

.segment "MINI_LIFT_ALLOCATE"
MiniLiftAllocate:
    ldx MiniLiftActor
    beq SearchFree
    dex
    lda Enemy_Flag,x
    cmp #1
    bne SearchFree
    lda Enemy_ID,x
    cmp #$25
    bne SearchFree
    lda Enemy_State,x
    cmp #$40
    beq Construct
    ; Active native actors keep their slots. The authenticated previous lift
    ; is the only live slot this admits. Its body cannot overlap any other
    ; placement window, so the player is already clear before retargeting.
SearchFree:
    ldx #5
ScanFree:
    lda Enemy_Flag,x
    beq Construct
    dex
    bpl ScanFree
    sec
    rts
Construct:
    jmp MiniLiftSpawnBank

.segment "MINI_LIFT_ALLOCATE_CALL"
MiniLiftSpawnBank:
    MapTarget MiniLiftSpawn, $ce
    ; InitVertPlatform's CPY #3 leaves carry clear for the owned 1-1 area.
    jmp FarCallCommon
