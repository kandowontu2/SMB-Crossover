.setcpu "6502"
.segment "POSE_OWNER"
; The sole native caller admits only player slot Y=0. Its nested water
; predicate ignores incoming A; every admitted fallback reloads character.
    php
    jsr $af3d
    bcc OtherBody
    plp
    lda #$de
    jmp $80c2
OtherBody:
    plp
    cpy #0
    bne Done
    lda SelectedCharacter
    beq Celeste
    cmp #1
    beq Mega
    cmp #16
    bne Done
    lda SmPosePtr+1
    cmp #$c8
    bne Done
    lda #2
    bne Publish
Mega:
    lda ProtoVariant
    beq MegaBase
    lda #$c1
    bne Publish
MegaBase:
    lda #$a1
Publish:
    jmp $80c2
Done:
    rts
Celeste:
    lda MarioVariant
    cmp #4
    bne Done
    lda #$e2
    bne Publish
