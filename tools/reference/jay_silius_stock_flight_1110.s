.setcpu "6502"

.segment "PREFIX"
; The first scatter row lands at A3:A000 and has already been verified.
; Move its private services out of the subsequent movement decode range.
; Preserve the common cold cookie pointer at $08/$09.
StageStock:
 lda #$60
 sta $03
 lda #$a0
 sta $04
 lda #0
 sta $05
 lda #$b0
 sta $06
 ldy #0
 ldx #CopyPages
CopyPage:
 lda ($03),y
 sta ($05),y
 cmp ($05),y
 bne CopyFailed
 iny
 bne CopyPage
 inc $04
 inc $06
 dex
 bne CopyPage
CopyTail:
 lda ($03),y
 sta ($05),y
 cmp ($05),y
 bne CopyFailed
 iny
 cpy #CopyTailBytes
 bne CopyTail
 jmp $d000
CopyFailed:
 clc
 rts

.segment "FLIGHT"
; Input runs before actor movement; bank 7 $C49E updates these records
; afterward, in D0, E0, F0 order. Keep that order in the native Main.
StepAndPublish:
 jsr StepStock
 jmp PublishPosition

StepStock:
 ldx #$d0
NextSlot:
 lda ShotRecords+9,x
 beq AdvanceSlot
 lda ShotRecords+8,x
 bne AdvanceSlot
 lda ShotRecords+15,x
 cmp #1
 bne AdvanceSlot
 jsr Flight
AdvanceSlot:
 txa
 clc
 adc #$10
 tax
 bne NextSlot
 rts

; Donor stock row $8865 uses $E1AA with X=2. Its horizontal probe is
; the one zero-offset point in the original $D097 record. It samples
; before committing X. Stock VY is zero and no vertical probe runs.
Flight:
 lda ShotRecords+4,x
 beq Project
 bmi ProbeLeft
 ldy #6
 bne Probe
ProbeLeft:
 ldy #4
Probe:
 sty QueryDirection
 lda ShotRecords+2,x
 sta QueryY
 and #$0f
 cmp #$0f
 bne CheckCameraY
 dec QueryY
CheckCameraY:
 lda QueryY
 eor CameraYHi
 and #$f0
 beq ProbeX
 inc QueryY
ProbeX:
 lda ShotRecords,x
 sta QueryX
 jsr JayHostTile
 beq MoveX
 lda #0
 sta ShotRecords+4,x
 jmp ClearSlot
MoveX:
 lda ShotRecords+4,x
 clc
 adc ShotRecords+1,x
 sta ShotRecords+1,x
 lda ShotRecords+4,x
 bmi NegativeVX
 lda #0
 beq CommitX
NegativeVX:
 lda #$ff
CommitX:
 adc ShotRecords,x
 sta ShotRecords,x

; Bank 7 $CD88 relative projection. A far-X result returns before it
; computes Y. Near-X edges still publish Y before $8865 retires the slot.
Project:
 lda ShotRecords+9,x
 and #$df
 sta ShotRecords+9,x
 lda #0
 sta NearX
 lda ShotRecords+1,x
 sec
 sbc CameraXLo
 sta ShotRecords+6,x
 lda ShotRecords,x
 sbc CameraXHi
 lsr a
 ror ShotRecords+6,x
 lsr a
 ror ShotRecords+6,x
 lsr a
 ror ShotRecords+6,x
 lsr a
 ror ShotRecords+6,x
 cmp #0
 beq ProjectY
 cmp #1
 beq NearRight
 cmp #$0f
 bne ClearSlot
 lda ShotRecords+6,x
 cmp #$a0
 bcc ClearSlot
 bcs SetNearX
NearRight:
 lda ShotRecords+6,x
 cmp #$5f
 bcs ClearSlot
SetNearX:
 inc NearX
ProjectY:
 lda ShotRecords+3,x
 sec
 sbc CameraYLo
 sta ShotRecords+7,x
 lda ShotRecords+2,x
 sbc CameraYHi
 lsr a
 ror ShotRecords+7,x
 lsr a
 ror ShotRecords+7,x
 lsr a
 ror ShotRecords+7,x
 lsr a
 ror ShotRecords+7,x
 cmp #0
 bne ClearSlot
 lda NearX
 beq Done
ClearSlot:
 lda #0
 sta ShotRecords+9,x
Done:
 rts
