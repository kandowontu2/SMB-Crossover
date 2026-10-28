; Literal source-derived kinematics, from supplied Rogue Dawn1.21 actual bytes.
; Fixed62:CFC3/DC3E/DC4B/DC61/D147 and63:E3A5/E3E5; A61:A2BA/A2DE.
; Full movement must call collision pixel steps using RdDelta, then update the
; source jump-distance/support/action fields. This module does NOT claim those
; external paths, complete player controls, native gameplay, weapons or art.
.pushseg
.segment "ROGUE_DAWN_CORE"
.export RdStartJump,RdStopVertical,RdVerticalAccelerate,RdHorizontalAccelerate
.export RdSetGravity,RdSetJumpGravity,RdSetMaxSpeed,RdSpringAdmitted
.export RdSpringRelease,RdCutOrdinaryJump,RdSetAnimation,RdAddMissileTank
.export RdAirControl,RdSetGroundAcceleration
.export RdGroundCollisionResponse

.proc RdStartJump                 ; exact source62:CFC3..D001
    ldy #$0c
    sty RdAnimReset
    dey
    sty RdAnimIndex
    lda #4
    sta RdAnimDelay
    lda #0
    sta RdJumpDistance
    lda #$fc
    sta RdVY
    ldx RdAction
    dex
    bne NoScrew
    lda RdGear
    and #8
    beq NoScrew
    lda #0
    sta RdSfx+6
    jsr RdScrewRequest
NoScrew:
    jsr RdJumpRequest
    ldy #$18
    lda RdGear
    and #2
    beq SetGravity
    ldy #$12
SetGravity:
    jsr RdSetJumpGravity
    rts
.endproc

.proc RdSetGravity                ; source62:DC3E..DC4A
    pha
    pla
    bit RdEnvironment
    bmi Store
    lda #7
Store:
    sta RdGravity
    rts
.endproc

.proc RdSetJumpGravity            ; source62:DC4B..DC60
    bit RdEnvironment
    bmi Store
    ror a
    beq Normal
    ldy #5
    bit RdGravityFlagProbe        ; source overlapping BIT07A0
    jmp Reduced
Normal:
    ldy #7
Reduced:
    lda #$fe
    sta RdVY
Store:
    sty RdGravity
    rts
.endproc

.proc RdSetMaxSpeed               ; source62:DC61..DC72
    bit RdEnvironment
    bmi Store
    cmp #$12
    beq Wall
    lda #$14
    bit RdSpeedFlagProbe          ; source overlapping BIT0AA9
    jmp Store
Wall:
    lda #$0a
Store:
    sta RdMaxSpeed
    rts
.endproc

.proc RdStopVertical              ; source62:D147..D14F
    ldy #0
    sty RdVY
    sty RdVerticalFraction
    rts
.endproc

.proc RdVerticalAccelerate        ; genuine inner entry63:E3A5..E3E4
    ldx #5
    lda RdVerticalFraction
    clc
    adc RdGravity
    sta RdVerticalFraction
    lda RdVY
    adc #0
    sta RdVY
    bpl Down
    lda #0
    cmp RdVerticalFraction
    sbc RdVY
    cmp #6
    ldx #$fa
    bne Limit
Down:
    cmp #5
Limit:
    bcc Phase
    jsr RdStopVertical
    stx RdVY
Phase:
    lda RdVerticalPhase
    clc
    adc RdVerticalFraction
    sta RdVerticalPhase
    lda #0
    adc RdVY
    sta RdDelta
    rts
.endproc

.proc RdHorizontalAccelerate      ; complete source63:E3E5..E448
    lda RdMaxSpeed
    jsr RdTimes16
    sta RdDelta
    sta RdMath2
    lda RdMaxSpeed
    jsr RdDivide16
    sta RdMath1
    sta RdMath3
    lda RdHorizontalFraction
    clc
    adc RdAcceleration
    sta RdHorizontalFraction
    tax
    lda #0
    bit RdAcceleration
    bpl Positive
    lda #$ff
Positive:
    adc RdVX
    sta RdVX
    tay
    bpl Magnitude
    lda #0
    sec
    sbc RdHorizontalFraction
    tax
    lda #0
    sbc RdVX
    tay
    jsr RdNegateLimit
Magnitude:
    cpx RdMath2
    tya
    sbc RdMath3
    bcc Phase
    lda RdDelta
    sta RdHorizontalFraction
    lda RdMath1
    sta RdVX
Phase:
    lda RdHorizontalPhase
    clc
    adc RdHorizontalFraction
    sta RdHorizontalPhase
    lda #0
    adc RdVX
    sta RdDelta
    rts
.endproc

.proc RdNegateLimit               ; source63:E449..E456
    lda #0
    sec
    sbc RdDelta
    sta RdDelta
    lda #0
    sbc RdMath1
    sta RdMath1
    rts
.endproc

.proc RdSpringAdmitted            ; source61:A2BA after freshA/support admission
    lda RdGear
    and #$10
    beq Done
    lda #0
    sta RdJumpDistance
    lda #$fc
    sta RdVY
    lda #2
    sta RdSfx+3
    ldy #$18
    lda RdGear
    and #2
    beq SetGravity
    ldy #$12
SetGravity:
    jsr RdSetJumpGravity
Done:
    jmp RdSpringRelease
.endproc

.proc RdSpringRelease             ; source61:A2DE..A2FE
    lda RdHeld
    bmi Save
    lda RdPreviousSpring
    bpl Save
    lda RdJumpDistance
    bit RdVY
    bpl Save
    ldy RdVY
    cpy #$fe
    bcs Save
    ldy #$fe
    sty RdVY
Save:
    lda RdHeld
    sta RdPreviousSpring
    rts
.endproc

.proc RdCutOrdinaryJump           ; source62:D002..D014, next native call excluded
    lda RdJumpDistance
    bit RdVY
    bpl Done
    cmp #$20
    bcc Done
    bit RdHeld
    bmi Done
    jsr RdStopVertical
Done:
    rts
.endproc

.proc RdAirControl                ; complete source62:D055..D095
    ldx #1
    ldy #0
    lda RdHeld
    lsr a
    bcs Direction
    dex
    lsr a
    bcc Store
    dex
    iny
Direction:
    cpy RdFacing
    beq Store
    lda RdAction
    cmp #6
    bne Ordinary
    lda RdAnimReset
    cmp PointUp,y
    bne Pose
    lda PointUp+1,y
    jmp Pose
Ordinary:
    lda RdAnimReset
    cmp Spin,y
    bne Pose
    lda Spin+1,y
Pose:
    jsr RdSetAnimation
    lda #8
    sta RdAnimDelay
    sty RdFacing
Store:
    stx RdVX
    rts
Spin: .byte $0c,$0c,$0c           ; actual62:D096..D098
PointUp: .byte $35,$35,$35        ; actual62:D099..D09B
.endproc

.proc RdSetGroundAcceleration     ; source62:CCB7..CCBD; X=0right/1left
    lda Acceleration,x
    sta RdAcceleration
    rts
Acceleration: .byte $30,$d0       ; actual62:CCC0..CCC1
.endproc

.proc RdGroundCollisionResponse   ; source63:E2E8..E318, after real down collision
    lda RdAction
    cmp #3
    bne Walk
    lsr RdVY
    beq Stop
    ror RdVerticalFraction
    lda #0
    sec
    sbc RdVerticalFraction
    sta RdVerticalFraction
    lda #0
    sbc RdVY
    sta RdVY
    jmp Done
Walk:
    jsr RdWalkRequest
Stop:
    jsr RdStopVertical
    sty RdGravity
Done:
    rts                          ; source continuation is horizontal movementE31A
.endproc

.proc RdSetAnimation              ; source62:CF6B..CF76, genuine private helper
    sta RdAnimReset
    sta RdAnimIndex
    lda #0
    sta RdAnimDelay
    rts
.endproc

.proc RdAddMissileTank            ; source62:DD97..DDAF; A=source amount5
    pha
    clc
    adc RdMissiles
    bcc CurrentFits
    lda #$ff
CurrentFits:
    sta RdMissiles
    pla
    clc
    adc RdMaxMissiles
    bcc MaximumFits
    lda #$ff
MaximumFits:
    sta RdMaxMissiles
    rts
.endproc

.proc RdScrewRequest              ; source62:CBCA/CBA0/CBE8
    lda #$40
    ldx #0
    ora RdSfx,x
    sta RdSfx,x
    rts
.endproc
.proc RdJumpRequest               ; source62:CBAC/CBC2/CBE8
    lda #2
    ldx #1
    ora RdSfx,x
    sta RdSfx,x
    rts
.endproc
.proc RdWalkRequest               ; source62:CB96/CBA0/CBE8
    lda #8
    ldx #0
    ora RdSfx,x
    sta RdSfx,x
    rts
.endproc
.proc RdTimes16                   ; source62:C2C5
    asl a
    asl a
    asl a
    asl a
    rts
.endproc
.proc RdDivide16                  ; source62:C2BF
    lsr a
    lsr a
    lsr a
    lsr a
    rts
.endproc
.export RdKernelEnd
RdKernelEnd:
.popseg
