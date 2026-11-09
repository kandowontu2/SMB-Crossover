.setcpu "6502"
.macpack longbranch
.export GfHostSwordContact
.import GfFacing, GfSwordActive, GfSwordPhase, GfSwordX, GfSwordPage, GfSwordYBias, GfSwordDifference
.import SelectedCharacter, GameEngineSubroutine, ObjectOffset
.import Player_Rel_XPos, Player_X_Position, Player_PageLoc, Player_Y_Position, Player_Y_HighPos
.import Enemy_ID, Enemy_State, Enemy_Flag, Enemy_X_Position, Enemy_PageLoc, Enemy_Y_Position
.import Enemy_Y_HighPos, Enemy_BoundBoxCtrl, ShellOrBlockDefeat

.segment "GETSU_HOST_SWORD"

; Call after the native enemy body check. Basic sword source D19F admits
; phases 2 and later, with a radius of 8 horizontally and 16 vertically.
; This first host contact row adapts the original envelope to the native
; Goomba box. Other enemy classes keep their own native contact path.
.proc GfHostSwordContact
    lda SelectedCharacter
    cmp #42
    jne NoHit
    lda GameEngineSubroutine
    cmp #8
    jne NoHit
    lda GfSwordActive
    jeq NoHit
    lda GfSwordPhase
    cmp #2
    jcc NoHit
    lda Enemy_Flag,x
    cmp #1
    jne NoHit
    lda Enemy_ID,x
    cmp #6
    jne NoHit
    lda Enemy_State,x
    and #$20
    jne NoHit
    lda Enemy_BoundBoxCtrl,x
    cmp #9
    jne NoHit
    lda Enemy_Y_HighPos,x
    cmp #1
    jne NoHit
    cmp Player_Y_HighPos
    jne NoHit
    lda Player_Y_Position
    cmp #$e0
    jcs NoHit

    ; The donor adds its screen-relative X offset with carry from CMP#2.
    ; That carry also determines whether the following Y subtraction
    ; borrows. Keep the effect while comparing world X across pages.
    ldy GfFacing
    lda Player_Rel_XPos
    clc
    adc #8
    sec
    adc SourceXOffset,y
    lda #8
    sbc #0
    sta GfSwordYBias
    lda Player_X_Position
    clc
    adc WorldXOffset,y
    sta GfSwordX
    lda Player_PageLoc
    adc WorldXPage,y
    sta GfSwordPage

    ; The strict donor radius gives a 15-by-31 interval. Box 9 has
    ; native offsets (3,14)..(13,20), so E-X lies in [-20,4].
    lda Enemy_X_Position,x
    sec
    sbc GfSwordX
    sta GfSwordDifference
    lda Enemy_PageLoc,x
    sbc GfSwordPage
    tay
    lda GfSwordDifference
    clc
    adc #20
    sta GfSwordDifference
    tya
    adc #0
    bne NoHit
    lda GfSwordDifference
    cmp #25
    bcs NoHit

    ; For Y, E-C lies in [-35,1]. Vertical page ownership is above.
    lda Player_Y_Position
    clc
    adc GfSwordYBias
    sta GfSwordDifference
    lda Enemy_Y_Position,x
    sec
    sbc GfSwordDifference
    sta GfSwordDifference
    lda #0
    sbc #0
    tay
    lda GfSwordDifference
    clc
    adc #35
    sta GfSwordDifference
    tya
    adc #0
    bne NoHit
    lda GfSwordDifference
    cmp #37
    bcs NoHit
    lda ObjectOffset
    pha
    stx ObjectOffset
    jsr ShellOrBlockDefeat
    pla
    sta ObjectOffset
    sec
    rts
NoHit:
    clc
    rts
SourceXOffset:
    .byte $0f,$f1
WorldXOffset:
    .byte $18,$fa
WorldXPage:
    .byte $00,$ff
.endproc
