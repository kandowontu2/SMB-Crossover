.setcpu "6502"
.segment "PAIR"
.export PairOffsets, EnemiesCollision, PairCoreCall, PairExit

ObjectOffset = $0d
FrameCounter = $0e
Enemy_Flag = $10
Enemy_ID = $17
Enemy_State = $1f
EnemyOffscrBitsMasked = $05a8
Enemy_CollisionBits = $063d
AreaType = $0753
OtherSlot = $04
ExSFN = $98c8
SetBitsMask = $98c9
SprObjectCollisionCore = $9514
ProcEnemyCollisions = $9958

; Existing private seven-byte ClearBitsMask extent. The only old reader
; now complements SetBitsMask. Native EnemiesAndLoopsCore uses slots 0..5.
PairOffsets:
    .byte $04,$08,$0c,$10,$14,$18,$1c

EnemiesCollision:
    lda FrameCounter
    lsr
    .assert *-PairOffsets=$0a,error,"Preserve parity branch PC"
    .byte $90,$ec               ; BCC ExSFN ($98C8)
    lda AreaType
    .assert *-PairOffsets=$0f,error,"Preserve water branch PC"
    .byte $f0,$e7               ; BEQ ExSFN ($98C8)
    lda Enemy_ID,x
    cmp #$15
    bcs PairExit
    cmp #$11
    beq PairExit
    cmp #$0d
    beq PairExit
    lda EnemyOffscrBitsMasked,x
    bne PairExit

    ; The old offset helper also loaded an offscreen nibble for its other
    ; callers. Here A/C are unused before the next load/compare. The caller
    ; loads ID and compares type on return, including slot zero.
    ldy PairOffsets,x
    clv                         ; old offset ADC sets V=0 for native slots
    dex
    bmi PairExit
NextPair:
    stx OtherSlot
    lda Enemy_Flag,x
    beq NextSlot
    lda Enemy_ID,x
    cmp #$15
    bcs NextSlot
    cmp #$11
    beq NextSlot
    cmp #$0d
    beq NextSlot
    lda EnemyOffscrBitsMasked,x
    bne NextSlot

    ; Rejected slots retain X/Y, so only a real pair needs the old save.
    tya
    pha
    lda PairOffsets,x
    tax
    clv
PairCoreCall:
    jsr SprObjectCollisionCore
    ldx ObjectOffset
    ldy OtherSlot
    bcs Hit

    lda SetBitsMask,x
    eor #$ff
    and Enemy_CollisionBits,y
    sta Enemy_CollisionBits,y
    bcc RestoreSlot             ; native overlap already returned C=0

Hit:
    lda Enemy_State,x
    ora Enemy_State,y
    and #$80
    bne React
    lda Enemy_CollisionBits,y
    and SetBitsMask,x
    bne RestoreSlot
    lda Enemy_CollisionBits,y
    ora SetBitsMask,x
    sta Enemy_CollisionBits,y
React:
    jsr ProcEnemyCollisions
RestoreSlot:
    pla
    tay
    ldx OtherSlot
NextSlot:
    dex
    bpl NextPair
PairExit:
    ldx ObjectOffset
    rts
.assert *-PairOffsets=$88,error,"Existing table and pair-dispatch footprint"
