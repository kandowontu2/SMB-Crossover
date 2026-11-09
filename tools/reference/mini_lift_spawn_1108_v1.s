.setcpu "6502"
.export MiniLiftSpawn, MiniLiftSpawnEnd

; Exact expanded MMC5 native addresses on aa02beb0.
ObjectOffset = $0d
Enemy_Flag = $10
Enemy_ID = $17
Enemy_State = $1f
Player_PageLoc = $5c
Enemy_PageLoc = $5d
Enemy_X_Position = $76
Enemy_Y_HighPos = $a5
Enemy_Y_Position = $be
Enemy_BoundBoxCtrl = $0646
FarCallCommon = $015a
FarcallJmpTarget = $016c
InitEnemyObject = $a74f
MiniLiftActor = $c30b

.segment "MINI_LIFT_SPAWN"

; Main-only. Caller owns Mini C2, validated the 1-1 placement and found a
; native free slot or the preceding owned girder. A = left edge low byte.
; Standalone: Y = world page. Chain: same world page as the player.
; Publish slot+1 only after native initialization and ownership marker.
; A/X/Y/P and SMC target are scratch. Keep native ObjectOffset unchanged.
MiniLiftSpawn:
    sta Enemy_X_Position,x
    .ifdef MINI_LIFT_CHAIN
    lda Player_PageLoc
    .else
    tya
    .endif
    sta Enemy_PageLoc,x
    lda ObjectOffset
    pha
    stx ObjectOffset
    lda #192
    sta Enemy_Y_Position,x
    lda #1
    sta Enemy_Flag,x
    sta Enemy_Y_HighPos,x
    lda #$25
    sta Enemy_ID,x
    lda #<InitEnemyObject
    sta FarcallJmpTarget
    lda #>InitEnemyObject
    sta FarcallJmpTarget+1
    lda #$82
    jsr FarCallCommon
    lda #5
    sta Enemy_BoundBoxCtrl,x
    lda #$40
    sta Enemy_State,x
    inx
    stx MiniLiftActor
    pla
    sta ObjectOffset
    rts
MiniLiftSpawnEnd:
.assert MiniLiftSpawnEnd-MiniLiftSpawn <= $39, error, "57-byte native constructor lease"
