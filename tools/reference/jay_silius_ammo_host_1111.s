.setcpu "6502"
.segment "AMMOHOST"

; The stock hit caller supplies the defeated enemy slot in X. Capture before
; the native defeat routine changes its coordinates, and preserve its ABI.
CaptureAmmoDefeat:
 php
 pha
 tya
 pha
 lda DropStage
 pha
 lda FrameCounter
 sta DropSourceClock
 lda #8
 sta DropSourceRoom
 lda #0
 sta DropSourceMode
 lda Enemy_X_Position,x
 clc
 adc #8
 sta DropCandidateX
 lda Enemy_PageLoc,x
 adc #0
 sta DropCandidatePage
 lda DropCandidateX
 asl a
 asl a
 asl a
 asl a
 sta DropSourceXLo
 lda CameraXLo
 sta DropCameraXLo
 lda DropCandidateX
 sec
 sbc CameraPixel
 sta DropScreenX
 jsr RollAmmoDrop
 pla
 bne RestoreDefeat
 lda DropStage
 beq RestoreDefeat
 lda DropCandidateX
 sta DropWorldXLo
 lda DropCandidatePage
 sta DropWorldXHi
 lda Enemy_Y_Position,x
 clc
 adc #8
 ldy #0
 sty DropWorldYHi
 ldy #4
CaptureY:
 asl a
 rol DropWorldYHi
 dey
 bne CaptureY
 sta DropWorldYLo
 lda #0
 sta DropFlags
RestoreDefeat:
 pla
 tay
 pla
 plp
 jmp NativeDefeat

; Run before StepStock, so a newly defeated actor keeps all 24 later ticks.
StepAmmoAndStock:
 jsr StepAmmo
 jmp StepStock
StepAmmo:
 lda FrameCounter
 sta DropSourceClock
 lda DropStage
 bne HasAmmoStage
 rts
HasAmmoStage:
 cmp #$23
 bne ActiveAmmo
 jsr ProjectAmmo
 bcs AdvancePendingAmmo
 lda #0
 sta DropStage
 rts
AdvancePendingAmmo:
 jmp AdvanceAmmoDrop
ActiveAmmo:
 jsr AmmoGravity
 lda DropVelocityY
 beq ProjectActiveAmmo
 clc
 adc DropWorldYLo
 sta DropNextYLo
 lda DropVelocityY
 bmi NegativeAmmoY
 lda #0
 beq AddAmmoY
NegativeAmmoY:
 lda #$ff
AddAmmoY:
 adc DropWorldYHi
 sta DropNextYHi
 jsr ProbeAmmoTerrain
 bne BlockedAmmo
 lda DropNextYLo
 sta DropWorldYLo
 lda DropNextYHi
 sta DropWorldYHi
 lda #5
 sta DropFlags
 bne ProjectActiveAmmo
BlockedAmmo:
 lda #1
 ora DropFlags
 sta DropFlags
 lda DropVelocityY
 bmi StopAmmo
 lda DropFlags
 and #4
 beq StopAmmo
 lda DropNextYHi
 sta DropWorldYHi
 lda DropNextYLo
 and #$80
 sta DropWorldYLo
 lda #1
 sta DropFlags
StopAmmo:
 lda #0
 sta DropVelocityY
ProjectActiveAmmo:
 jsr ProjectAmmo
 bcc RetireAmmo
 jsr AdvanceAmmoDrop
 lda DropStage
 beq StepDone
 lda PlayerCenterX
 sec
 sbc DropVisibleX
 bcs TouchXReady
 eor #$ff
 clc
 adc #1
TouchXReady:
 pha
 lda PlayerCenterY
 sec
 sbc DropVisibleY
 bcs TouchYReady
 eor #$ff
 clc
 adc #1
TouchYReady:
 tax
 lda PlayerFlags
 sta DropPlayerFlags
 pla
 jmp TouchAmmoDrop
RetireAmmo:
 lda #0
 sta DropStage
StepDone:
 rts

; The stationary source actor has bit 0 set and skips side probes. X6 uses
; ordered head (-8,+4),(-8,-4) and foot (+8,+4),(+8,-4) pixel samples.
ProbeAmmoTerrain:
 ldx #0
 lda #0
 sta DropProbeYHi
 lda #2
 ldy DropVelocityY
 bpl SetProbeDirection
 lda #$ff
 sta DropProbeYHi
 lda #0
SetProbeDirection:
 sta QueryDirection
NextAmmoPoint:
 lda DropNextYLo
 clc
 adc #$80
 lda DropNextYHi
 adc DropProbeYHi
 sta QueryY
 and #$0f
 cmp #$0f
 bne CheckAmmoRow
 lda DropVelocityY
 bmi RaiseAmmoRow
 dec QueryY
 bne CheckAmmoRow
RaiseAmmoRow:
 inc QueryY
CheckAmmoRow:
 lda QueryY
 eor CameraYHi
 and #$f0
 beq ProbeAmmoX
 inc QueryY
ProbeAmmoX:
 lda AmmoOffsetsX,x
 tay
 clc
 adc DropWorldXLo
 sta DropProbeX
 tya
 bmi NegativeProbeX
 lda DropWorldXHi
 adc #0
 bcc ScaleProbeX
NegativeProbeX:
 lda DropWorldXHi
 adc #$ff
ScaleProbeX:
 ldy #4
ScaleProbeBit:
 lsr a
 ror DropProbeX
 dey
 bne ScaleProbeBit
 lda DropProbeX
 sta QueryX
 jsr JayHostTile
 bne ProbeAmmoDone
 txa
 and #1
 bne ProbeAmmoClear
 inx
 bne NextAmmoPoint
ProbeAmmoClear:
 lda #0
ProbeAmmoDone:
 rts
AmmoOffsetsX:
 .byte 4,$fc

; Keep the full page subtraction before exposing a screen coordinate.
ProjectAmmo:
 lda DropWorldXLo
 sec
 sbc CameraPixel
 sta DropVisibleX
 lda DropWorldXHi
 sbc CameraPage
 bne InvisibleAmmo
 lda DropWorldYHi
 cmp #$10
 bcs InvisibleAmmo
 sta DropVisibleY
 lda DropWorldYLo
 ldx #4
ProjectYBit:
 lsr DropVisibleY
 ror a
 dex
 bne ProjectYBit
 sta DropVisibleY
 cmp #240
 bcs InvisibleAmmo
 sec
 rts
InvisibleAmmo:
 clc
 rts

; Call after the authenticated stock draw. The shared five-byte native
; metasprite record is consumed synchronously by the real A4 renderer.
.segment "AMMODRAW"
DrawAmmoAndStock:
 jsr DrawStock
 jmp DrawAmmo
DrawAmmo:
 lda DropStage
 cmp #$22
 bne DrawAmmoDone
 lda DropFlags
 beq DrawAmmoDone
 lda OamOffset
 cmp DrawLimit
 bcs DrawAmmoDone
 lda DropTimer
 cmp #$20
 bcs AmmoAnimation
 lda DropSourceClock
 lsr a
 bcs DrawAmmoDone
AmmoAnimation:
 lda DropTimer
 lsr a
 lsr a
 and #3
 tax
 lda #4
 sta ShotMetasprite
 lda AmmoTiles,x
 sta ShotMetasprite+1
 lda AmmoAttributes,x
 sta ShotMetasprite+2
 lda #$f8
 sta ShotMetasprite+3
 lda #0
 sta ShotMetasprite+4
 sta $06
 sta $08
 lda #<ShotMetasprite
 sta $03
 lda #>ShotMetasprite
 sta $04
 lda DropVisibleX
 sta $07
 lda DropVisibleY
 sta $09
 lda #1
 sta $0a
 lda #<NativeRender
 sta $016c
 lda #>NativeRender
 sta $016d
 lda #$84
 jmp $015a
DrawAmmoDone:
 rts
AmmoTiles:
 .byte $2a,$2c,$2a,$2c
AmmoAttributes:
 .byte $c0,$c0,$40,$40
