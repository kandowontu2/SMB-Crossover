.setcpu "6502"
.export GfHorizontalSpeed, GfJumpStart, GfVerticalSpeed, GfIntegrateY
.import GfAction, GfFacing, GfVXLo, GfVXHi, GfVYLo, GfVYHi
.import GfYLo, GfYHi, GfJumpHold, GfSupport, GfPad, GfSign

.segment "GETSU_MOTION"

; Getsu Fuuma Den, fixed PRG15:$EB0B..$EBAE. The caller owns the
; background collision and world/camera projection that follow this leaf.
; Pass effective Left/Right in A after the grounded crouch gate.
.proc GfHorizontalSpeed
    sta GfPad
    and #$01
    beq CheckLeft
    lda #$00
    sta GfFacing
    lda GfVXHi
    bpl Right
    lda #$00
    sta GfVXHi
    sta GfVXLo
Right:
    lda #$20
    jmp Accelerate
CheckLeft:
    lda GfPad
    and #$02
    beq Coast
    lda #$01
    sta GfFacing
    lda GfVXHi
    bmi Left
    lda #$00
    sta GfVXHi
    sta GfVXLo
Left:
    lda #$e0
    jmp Accelerate
Coast:
    lda GfVXLo
    ora GfVXHi
    beq Return
    lda GfAction
    and #$02
    bne Return
    lda GfVXHi
    bmi CoastRight
    lda #$e0
    ldx #$ff
    bne Brake
CoastRight:
    lda #$20
    ldx #$00
Brake:
    stx GfSign
    clc
    adc GfVXLo
    sta GfVXLo
    lda GfVXHi
    adc GfSign
    sta GfVXHi
Return:
    rts
.endproc

; PRG15:$ED0A..$ED57. Preserve the donor's signed Q8.8 clamp,
; including its low-byte threshold after taking the magnitude.
.proc Accelerate
    bpl Positive
    ldx #$ff
    bne Sign
Positive:
    ldx #$00
Sign:
    stx GfSign
    clc
    adc GfVXLo
    sta GfVXLo
    sta GfPad
    lda GfVXHi
    adc GfSign
    sta GfVXHi
    bpl CheckLimit
    lda #$00
    sec
    sbc GfVXLo
    sta GfPad
    lda #$00
    sbc GfVXHi
CheckLimit:
    cmp #$01
    bcc Return
    lda GfPad
    cmp #$80
    bcc Return
    lda GfVXHi
    bpl RightLimit
    lda #$fe
    sta GfVXHi
    lda #$80
    bne StoreLow
RightLimit:
    lda #$01
    sta GfVXHi
    lda #$80
StoreLow:
    sta GfVXLo
Return:
    rts
.endproc

; PRG15:$E336..$E34A. The caller checks the donor action mask,
; fresh A, and the source support state. Top equipment is a separate path.
.proc GfJumpStart
    lda #$02
    sta GfAction
    lda #$80
    sta GfVYLo
    lda #$fd
    sta GfVYHi
    lda #$00
    sta GfJumpHold
    sta GfSupport
    rts
.endproc

; PRG15:$E542..$E572. Holding A cancels gravity for the first 22
; held updates. Terrain admission follows the speed calculation.
.proc GfVerticalSpeed
    and #$80
    beq Gravity
    lda GfJumpHold
    cmp #$16
    bcs Gravity
    inc GfJumpHold
    lda GfVYLo
    sec
    sbc #$40
    sta GfVYLo
    lda GfVYHi
    sbc #$00
    sta GfVYHi
Gravity:
    lda #$40
    clc
    adc GfVYLo
    sta GfVYLo
    lda GfVYHi
    adc #$00
    sta GfVYHi
    rts
.endproc

; PRG15:$ECF5..$ED09. Call after the host admits this terrain step.
.proc GfIntegrateY
    lda GfYLo
    clc
    adc GfVYLo
    sta GfYLo
    lda GfYHi
    adc GfVYHi
    sta GfYHi
    rts
.endproc
