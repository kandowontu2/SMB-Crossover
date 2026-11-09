MiniPlatformFloor:
    ldx MiniLiftActor
    beq @miss
    lda nocollide
    bne @miss
    jsr MiniHostPixelX
    ldx #5
@scan:
    lda $1f,x                ; Only the constructor's Mini marker.
    cmp #$40
    bne @next
    lda $17,x                ; Existing native vertical lift type.
    cmp #$25
    bne @next
    lda Enemy_Flag,x
    cmp #1
    bne @next
    lda MiniCoord
    sec
    sbc MiniLiftEnemyX,x
    tay
    lda MiniCoord+1
    sbc MiniLiftEnemyPage,x
    beq @rightOfEdge
    cmp #$ff
    bne @next
    cpy #250                 ; Right foot at player X+6.
    bcs @checkTop
@next:
    dex
    bpl @scan
@miss:
    lda #0
    sta MiniLiftGround
    clc
    rts
@rightOfEdge:
    cpy #31                  ; Left foot at player X+1, last lift pixel X+31.
    bcs @next
@checkTop:
    ; Authored lift spans are disjoint, so no other lift can cover this X.
    lda MiniLiftEnemyY,x
    sec
    sbc #8                   ; Mini source feet are source Y+8.
    tay
    inx
    cpx MiniLiftGround
    stx MiniLiftGround
    beq @land                ; The same supported lift may move by one pixel.
    tya
    sec
    sbc #24                  ; Native player Y is source Y-24.
    cmp Player_Y_Position
    bcc @miss
    lda Player_Y_HighPos
    cmp #1
    bne @miss
    jsr MiniTempPixel
    lda MiniCoord+1
    bne @miss
    cpy MiniCoord
    bcc @land
    bne @miss
@land:
    tya
    .repeat 4
        asl a
    .endrepeat
    sta MiniTemp
    tya
    .repeat 4
        lsr a
    .endrepeat
    sta MiniTemp+1
    sec
    rts

