; Derivative for the real FF native head/side corner defect.
; Read every candidate through the existing cell reader. A rising solid-only
; head candidate must overlap the previous full world-space body horizontally;
; a newly entered side column belongs to the later native side resolver.
; This preserves the source [X+1,X+15) rectangle. It does not narrow the head.
.setcpu "6502"
.segment "HEAD"
FfCornerHeadRead:
 jsr FfHostRead
 beq ReadDone
 ldx Player_Y_Speed
 bpl Return
 tax
 lda MTileAttribute,x
 and #3
 cmp #1
 bne Return
 ; An old endpoint must be in the candidate's actual 16px world column.
 ; EOR/AND/branches preserve the endpoint ADC's page carry.
 lda FfCornerPreviousX
 clc
 adc #1
 eor R5
 and #$f0
 bne RightEndpoint
 lda FfCornerPreviousPage
 adc #0
 cmp FfTerrainPage
 beq Return
RightEndpoint:
 lda FfCornerPreviousX
 clc
 adc #14
 eor R5
 and #$f0
 bne SideOnly
 lda FfCornerPreviousPage
 adc #0
 cmp FfTerrainPage
 beq Return
SideOnly:
 lda #0
 sta R3
Return:
 sec                         ; retain the original valid-cell read carry.
ReadDone:
 jmp FfHostReadReturn
FfCornerHeadReadEnd:

.segment "SNAPSHOT"
FfCornerCapture:
 jsr FfEnsure
 lda Player_X_Position
 sta FfCornerPreviousX
 lda Player_PageLoc
 sta FfCornerPreviousPage
 rts
FfCornerCaptureEnd:
