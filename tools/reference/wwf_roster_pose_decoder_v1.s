; Actual6502 decoder for the compact six-wrestler metadata. Caller owns the
; original SaveRuntime scope and publishes WfPosePage after the complete OAM
; record is ready. No new global/ZP bytes and no hardware writes in this unit.
.setcpu "6502"
.segment "WF_ROSTER_DECODER"
.export WfDecodeRosterPose
WfDecodeRosterPose:
 lda WfState+$32
 cmp WfHoganMetadata
 bcc GroupValid
 lda #0
GroupValid:
 asl
 tay
 lda WfHoganMetadata+2,y
 sta WfPoseIndex
 lda WfHoganMetadata+3,y
 sta WfPoseWidth
 tya
 lsr
 clc
 adc #1
 cmp WfHoganMetadata
 bcc NextGroup
 lda WfHoganMetadata+1
 bcs HaveEnd
NextGroup:
 lda WfHoganMetadata+4,y
HaveEnd:
 sec
 sbc WfPoseIndex
 sta R3
 lda WfState+$34
 cmp R3
 bcc FrameValid
 lda #0
FrameValid:
 clc
 adc WfPoseIndex
 sta WfPoseIndex
 asl
 sta R3
 lda WfHoganMetadata
 asl
 clc
 adc #2
 adc R3
 tay
 lda WfHoganMetadata+1,y
 pha
 and #7
 sta R1
 lda WfHoganMetadata,y
 clc
 adc #<WfHoganMetadata
 sta R0
 lda R1
 adc #>WfHoganMetadata
 sta R1
 pla
 lsr
 lsr
 lsr
 sta WfCellCount
 asl
 asl
 sta WfRenderBuffer
 ldy #0
 lda (R0),y
 sta WfPosePage
 lda WfState+$3a
 and #1
 sta WfRenderFace
 lda #1
 sta WfCellOffset
 ldx #1
Cell:
 ldy WfCellOffset
 lda (R0),y
 sta R3
 and #$fe
 sta WfRenderBuffer,x
 lda R3
 and #1
 ldy WfRenderFace
 beq AttributeReady
 ora #$40
AttributeReady:
 sta WfRenderBuffer+1,x
 ldy WfCellOffset
 iny
 lda (R0),y
 ldy WfRenderFace
 beq XReady
 sta R2
 lda WfPoseWidth
 sec
 sbc R2
XReady:
 sta WfRenderBuffer+3,x
 ldy WfCellOffset
 iny
 iny
 lda (R0),y
 sta WfRenderBuffer+2,x
 lda WfCellOffset
 clc
 adc #3
 sta WfCellOffset
 txa
 clc
 adc #4
 tax
 dec WfCellCount
 bne Cell
 rts
WfDecodeRosterPoseEnd:
.export WfDecodeRosterPoseEnd
