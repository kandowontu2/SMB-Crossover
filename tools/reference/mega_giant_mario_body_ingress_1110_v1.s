.setcpu "6502"
.import GiantBodyBox
.export GiantBodyRoute

SelectedCharacter = $6002
MarioVariant = $730a
NativeBodyRoute = $b969

.segment "GIANT_GATE"
GiantBodyRoute:
    php
    pha
    lda SelectedCharacter
    bne Legacy
    lda MarioVariant
    cmp #9                      ; private CPU identity until menu admission
    bne Legacy
    pla
    plp
    jmp GiantBodyBox
Legacy:
    pla
    plp
    jmp NativeBodyRoute
