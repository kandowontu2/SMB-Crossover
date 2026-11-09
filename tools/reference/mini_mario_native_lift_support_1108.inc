; Mini's downward source sweep contacts the top of the actual native lift.
; The native helper manager supplies an authenticated actor slot plus one.
; The ordinary native actor continues to own motion, graphics and culling.
MiniLiftActor = $c30b
MiniLiftGround = $c30d
MiniLiftEnemyX = $76
MiniLiftEnemyPage = $5d
MiniLiftEnemyY = $be

MiniPlatformFloor:
    ldx MiniLiftActor
    beq @miss
    lda nocollide
    bne @miss
    jsr MiniHostPixelX
    ldx MiniLiftActor
    dex
    lda Enemy_Flag,x
    cmp #1
    bne @miss
    lda $17,x                ; Enemy_ID: only a native vertical lift.
    cmp #$25
    bne @miss
    lda $1f,x                ; Enemy_State: Mini helper marker.
    cmp #$40
    bne @miss
    lda MiniCoord
    sec
    sbc MiniLiftEnemyX,x
    tay
    lda MiniCoord+1
    sbc MiniLiftEnemyPage,x
    beq @rightOfEdge
    cmp #$ff
    bne @miss
    cpy #250                 ; Right foot at player X+6.
    bcc @miss
    bcs @checkTop
@rightOfEdge:
    cpy #31                  ; Left foot at player X+1, last lift pixel X+31.
    bcs @miss
@checkTop:
    lda MiniLiftEnemyY,x
    sec
    sbc #8                   ; Mini source feet are source Y+8.
    tay
    lda MiniLiftActor
    cmp MiniLiftGround
    beq @land                ; The same supported lift may move by one pixel.
    tya
    sec
    sbc #24                  ; Native player Y is source Y-24.
    cmp Player_Y_Position
    bcc @miss                ; Do not land from below the lift.
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
    lda MiniLiftActor
    sta MiniLiftGround
    sec
    rts
@miss:
    lda #0
    sta MiniLiftGround
    clc
    rts
