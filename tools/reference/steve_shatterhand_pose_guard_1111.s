.setcpu "6502"

.segment "POSE_GRAPHICS"
    lda JnHurt
    and #4
    beq Visible
    lda #0
    sta ObjectMetasprite
    rts
Visible:
    lda JnAttack
    beq Walk
    ldx JnWeapon
    cpx #10
    beq AirPose
    ldx #4
    cmp #6
    bcc SetPose
    inx
    bne SetPose
Walk:
    ldx Player_State
    bne AirPose
    lda Player_X_Speed
    beq SetPose
    lda JnClock
    lsr a
    lsr a
    and #3
    tax
    lda $a267,x
    tax
    bpl SetPose
AirPose:
    ldx #3
SetPose:
    jmp $a276

; The body selector leaves the A window on PRG96. The fixed mapper setter
; preserves X/Y, so this code remains executable while each C bank is checked.
StevePoseReady:
    ldy #3
CheckBank:
    tya
    jsr $80c2
    lda $dfe0
    cmp #PoseCookieMarker
    bne StockBank
    dey
    cpy #1
    bne CheckBank
    lda $cecf
    cmp #$8a
    bne StockBank
    jmp $cecf
StockBank:
    lda #$e1
    jsr $80c2
    lda #$dc
    ldy #0
    rts

.segment "POSE_ROM_GATE"
    cmp #$dc
    bne GateReturn
    jmp StevePoseReady
GateReturn:
    rts
