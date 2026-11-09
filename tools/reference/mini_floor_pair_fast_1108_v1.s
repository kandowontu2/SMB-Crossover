.setcpu "6502"

R1 = $04
R4 = $07
Up_Down_Buttons = $0559
Player_Y_Speed = $8e
BlockBufferColli_Feet = $9586

.segment "MINI_FLOOR_PAIR"

; BackgroundGuard already admitted on-screen native Y $20..$CE, zero
; source head events, and Y=14 from the same native head probe group.
; TileInert preserves Y. The second native foot
; read returns that same Y low nibble in R4 and carries out of SBC #$20.
ProbeFloor:
    jsr BlockBufferColli_Feet
    sta R1
    jsr BlockBufferColli_Feet
    ora R1
    sta R1
    beq FloorReady
    ; A native pipe entry requires left $10 + right $11 and Down. Their
    ; OR has bit 2 clear. Ground $54 retains the existing Down fast path.
    eor #$04
    bit Up_Down_Buttons
    bne FloorNo
    ; The fixed attribute table gives no climb bit to any submask of $55.
    ; This domain excludes coins, hidden blocks, axe and spring handlers.
    and #$aa
    bne FloorNo
    ldx Player_Y_Speed
    bmi FloorNo
    ldy R4
    beq FloorReady
FloorNo:
    clc
FloorReady:
    rts
.byte $ff                     ; End of the existing owned pad.
.assert *-ProbeFloor = 36, error, "Keep the existing floor probe span"
