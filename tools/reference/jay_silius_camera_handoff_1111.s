; World and camera coordinate handoff for the authenticated Jay update.
; The frozen original input, projection, integrator and terrain code run as-is.
.setcpu "6502"
.segment "HANDOFF"

PrivateUpdate:
 lda OperMode
 cmp #1
 bne Unsupported
 lda OperModeTask
 cmp #3
 bne Unsupported
 lda GameEngineSubroutine
 cmp #8
 bne Unsupported
 lda GamePauseStatus
 lsr A
 bcs Unsupported
 lda NmiDisable
 bpl Unsupported
 lda FamilyMainCommit
 lsr A
 bcc Unsupported
 lda SwimmingFlag
 ora WorldNumber
 ora LevelNumber
 bne Unsupported
 lda Ready
 bne HasActor
 jsr Construct
 jmp Update
HasActor:
 lda FrameCounter
 cmp Epoch
 beq ReturnUpdate
Update:
 lda FrameCounter
 sta Epoch
 lda PlayerX
 sta OldX
 lda CameraPage
 sta CameraXHi
 lda CameraPixel
 ldx #4
CameraToQ4:
 asl A
 rol CameraXHi
 dex
 bne CameraToQ4
 sta CameraXLo
 lda PadNow
 sta PadPrevious
 lda SavedJoypadBits
 sta PadNow
 jsr OriginalInput
 jsr PositionSetup
 ldx #0
 jsr Integrate
 jsr StepAndPublish
ReturnUpdate:
 sec
 rts
Unsupported:
 clc
 rts

Construct:
 ldx #50
CopyActorTemplate:
 lda DonorActorTemplate,x
 sta Actor,x
 dex
 bpl CopyActorTemplate
 lda PlayerPage
 sta XHi
 lda PlayerX
 ldx #4
ActorXToQ4:
 asl A
 rol XHi
 dex
 bne ActorXToQ4
 sta XLo
 lda PlayerY
 clc
 adc #16
 sta Temp
 lda PlayerYPage
 sbc #0
 sta YHi
 lda Temp
 ldx #4
ActorYToQ4:
 asl A
 rol YHi
 dex
 bne ActorYToQ4
 sta YLo
 lda #1
 sta Ready
 rts

PublishPosition:
 lda XHi
 ldx XLo
 jsr Q4ToPixels
 sta PlayerPage
 stx PlayerX
 txa
 sec
 sbc OldX
 sta PlayerXScroll
 txa
 sec
 sbc CameraPixel
 sta PlayerPosForScroll
 lda YHi
 ldx YLo
 jsr Q4ToPixels
 tay
 txa
 sec
 sbc #16
 sta PlayerY
 tya
 adc #0
 and #15
 sta PlayerYPage
 lda DonorVY
 ldx #4
ScaleVY:
 cmp #$80
 ror A
 dex
 bne ScaleVY
 sta PlayerYSpeed
 lda DonorFlags
 and #4
 beq PublishState
 lda #1
 ldx DonorVY
 bmi PublishState
 lda #2
PublishState:
 sta PlayerState
 rts

; Inputs A:X are world Q4. Outputs A:X are whole-pixel page:position.
Q4ToPixels:
 stx Temp
 ldx #4
Q4ToPixelBit:
 lsr A
 ror Temp
 dex
 bne Q4ToPixelBit
 ldx Temp
 rts

DonorActorTemplate:
 .byte TemplateBytes
