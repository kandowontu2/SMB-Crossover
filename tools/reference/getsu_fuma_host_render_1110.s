.setcpu "6502"
.macpack longbranch
.export GfDraw, GfBuildRecord, GfWalkAdvance, GfDrawEnd
.import GfClock, GfAction, GfFacing, GfVXLo, GfVXHi, GfBodyPose, GfBodyFacing
.import GfSwordActive, GfSwordPhase, GfSwordPose, GfSwordFacing
.import SelectedCharacter
.import Player_State, Player_X_Position, Player_PageLoc, Player_Y_Position, Player_Y_HighPos
.import ScreenLeft_X_Pos, ScreenLeft_PageLoc, StarInvincibleTimer, GuestPowerupActive
.import CurrentCHRBank, X5ChrMode, VRAM_Buffer1, VRAM_Buffer1_Offset
.import MetaspriteRenderLoop, X5SetPhysicalChr, R0, R1, R2, R3, R4, R5, R6, R7

.segment "GETSU_HOST_RENDER"

RenderValid = $c020
RenderClock = $c021
PriorAir = $c022
WalkIndex = $c023
WalkLo = $c024
WalkHi = $c025
SpeedLo = R0
SpeedHi = R1
UpperPose = $c028
UpperFacing = $c029
WasSword = $c02a
WriteIndex = R0
Parts = R1
LayerFacing = R2
LayerLift = R3
PoseOffset = R4
PaletteQueued = $c030
Record = $c040

.macro Far target, bank
    sta $016a
    lda #<target
    sta $016c
    lda #>target
    sta $016d
    lda #bank
    jsr $015a
.endmacro

; Called only through an authenticated RAM3 owner gate in the stage draw.
; The caller maps C=2 and controls the OAM cursor and injury flicker.
.proc GfDraw
    lda SelectedCharacter
    cmp #42
    jne Rejected
    jsr UpdatePose
    ldx UpperPose
    jsr GfBuildRecord
    lda #<Record
    sta R0
    lda #>Record
    sta R1
    lda #0
    sta R3
    lda Player_X_Position
    sec
    sbc ScreenLeft_X_Pos
    sta R4
    lda Player_PageLoc
    sbc ScreenLeft_PageLoc
    sta R5
    lda R4
    clc
    adc #8
    sta R4
    bcc :+
    inc R5
:
    lda Player_Y_Position
    clc
    adc #32
    sta R6
    lda Player_Y_HighPos
    adc #0
    sta R7
    Far MetaspriteRenderLoop, $84
    bcc Rejected
    lda CurrentCHRBank
    cmp #<990
    bne Publish
    lda X5ChrMode
    cmp #$83
    beq Palette
Publish:
    lda #<990
    ldx #>990
    ldy #0
    Far X5SetPhysicalChr, $be
Palette:
    jsr QueuePalette
    sec
    rts
Rejected:
    clc
    rts
.endproc

; Update the gait once per donor tick. The original keeps the last walk pose
; in the air, advances a step on landing, and resets the body on crouch exit.
.proc UpdatePose
    lda RenderValid
    bne Ready
    inc RenderValid
    lda #12
    sta GfBodyPose
    lda #3
    sta UpperPose
    lda GfFacing
    sta GfBodyFacing
    sta UpperFacing
    jmp NewTick
Ready:
    lda GfClock
    cmp RenderClock
    bne NewTick
    rts
NewTick:
    lda GfClock
    sta RenderClock
    lda GfAction
    and #1
    beq CheckAir
    lda #22
    sta GfBodyPose
    lda GfFacing
    sta GfBodyFacing
    jmp CheckSword
CheckAir:
    lda Player_State
    beq Ground
    sta PriorAir
    bne CheckSword
Ground:
    lda GfBodyPose
    cmp #22
    bne Landing
    lda #12
    sta GfBodyPose
    lda GfFacing
    sta GfBodyFacing
Landing:
    lda PriorAir
    beq Walk
    lda #0
    sta PriorAir
    jsr NextWalkPose
    jmp IdleCheck
Walk:
    jsr GfWalkAdvance
IdleCheck:
    lda GfVXLo
    ora GfVXHi
    bne CheckSword
    lda #12
    sta GfBodyPose
    lda GfFacing
    sta GfBodyFacing
CheckSword:
    lda GfSwordActive
    beq FinishedSword
    lda GfSwordPhase
    beq Done
    sta WasSword
SwordPose:
    lda GfSwordPose
    sta UpperPose
    lda GfSwordFacing
    sta UpperFacing
    rts
FinishedSword:
    lda WasSword
    beq Done
    lda #0
    sta WasSword
    beq SwordPose
Done:
    rts
.endproc

; Donor fixed15 EE67..EEBA. The next walk pose is chosen after eight
; pixels of signed Q8.8 motion, with the source's initial zero timer.
.proc GfWalkAdvance
    lda GfAction
    and #3
    bne Done
    lda GfVXHi
    bmi Left
    sta SpeedHi
    lda GfVXLo
    jmp Subtract
Left:
    lda #0
    sec
    sbc GfVXLo
    sta SpeedLo
    lda #0
    sbc GfVXHi
    sta SpeedHi
    lda SpeedLo
Subtract:
    sta SpeedLo
    lda WalkLo
    sec
    sbc SpeedLo
    sta WalkLo
    lda WalkHi
    sbc SpeedHi
    sta WalkHi
    bcs Done
    lda #0
    sta WalkLo
    lda #8
    sta WalkHi
    jmp NextWalkPose
Done:
    rts
.endproc

.proc NextWalkPose
    lda WalkIndex
    cmp #4
    bcc InRange
    lda #0
    sta WalkIndex
InRange:
    tay
    lda WalkBody,y
    sta GfBodyPose
    lda GfFacing
    sta GfBodyFacing
    inc WalkIndex
    lda WalkUpper,y
    sta UpperPose
    lda GfFacing
    sta UpperFacing
    rts
WalkBody:  .byte 4,5,6,5
WalkUpper: .byte 1,2,3,2
.endproc

; X=upper, body in GfBodyPose. The shared renderer traverses records backwards, so
; append the upper layer last to give it the first emitted hardware sprites.
.proc GfBuildRecord
    txa
    pha
    lda #0
    sta WriteIndex
    sta Record
    lda GfBodyFacing
    lsr
    lda #0
    ror
    sta LayerFacing
    ldx #0
    lda GfBodyPose
    jsr WriteLayer
    lda UpperFacing
    lsr
    lda #0
    ror
    sta LayerFacing
    lda GfAction
    and #1
    asl
    asl
    asl
    tax
    pla
    jsr WriteLayer
    lda WriteIndex
    sta Record
    rts
.endproc

.proc WriteLayer
    stx LayerLift
    cmp #GfPoseRecords-GfPoseOffsets
    bcs Done
    tay
    lda GfPoseOffsets,y
    cmp #$ff
    beq Done
    tay
    sty PoseOffset
    lda GfPoseRecords,y
    sta Parts
    asl
    adc Parts
    adc PoseOffset
    tay
    ldx WriteIndex
Loop:
    lda GfPoseRecords,y
    and #$7e
    sta Record+1,x
    lda GfPoseRecords,y
    lsr
    and #$40
    bit LayerFacing
    bpl Attribute
    eor #$40
Attribute:
    sta Record+2,x
    dey
    lda GfPoseRecords,y
    clc
    adc LayerLift
    sta Record+3,x
    dey
    lda GfPoseRecords,y
    bit LayerFacing
    bpl SaveDX
    eor #$ff
    sec
    sbc #8
SaveDX:
    sta Record+4,x
    dey
    txa
    clc
    adc #4
    tax
    dec Parts
    bne Loop
    stx WriteIndex
Done:
    rts
.endproc

.proc QueuePalette
    lda StarInvincibleTimer
    ora GuestPowerupActive
    bne Reset
    lda PaletteQueued
    bne Done
    ldx VRAM_Buffer1_Offset
    cpx #78
    bcs Done
    lda #$3f
    sta VRAM_Buffer1,x
    lda #$11
    sta VRAM_Buffer1+1,x
    lda #3
    sta VRAM_Buffer1+2,x
    ldy #0
Colors:
    lda GfSpriteColors,y
    sta VRAM_Buffer1+3,x
    inx
    iny
    cpy #3
    bne Colors
    inx
    inx
    inx
    stx VRAM_Buffer1_Offset
    lda #0
    sta VRAM_Buffer1,x
    inc PaletteQueued
Done:
    rts
Reset:
    lda #0
    sta PaletteQueued
    rts
.endproc

; The extractor appends the pinned donor pose records here.
GfDrawEnd:
