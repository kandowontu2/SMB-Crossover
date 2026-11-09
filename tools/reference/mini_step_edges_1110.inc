; Private Mini step fragments. No foreign owner or movement clock changes.

; === stationary
MiniGroundCollisions:
    ; The only caller has finished ground_x (family 2). Preserve the
    ; full X lane for any effective motion or possible viewport-edge push.
    cmp #0
    bne MiniCollisions
    lda delta
    ora delta+1
    bne MiniCollisions
    lda MiniX+1
    cmp MiniEdgeRight+1
    bcs MiniCollisions
    cmp MiniEdgeLeft+1
    bcc MiniCollisions
    beq MiniCollisions
    jmp MiniYAxis

; === to_subpixel
MiniHostToSubpixel:
    lda MiniCoord
    .repeat 4
        asl a
        rol MiniCoord+1
    .endrepeat
    sta MiniCoord
    ldx #0
    rts
