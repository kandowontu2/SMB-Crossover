; SMB wall-contact adapter: keep the original foot probe and the
; side contact that admitted the grip. A short floating block can touch
; Grant's body while ending above his feet. Source wall speed stays +/-1.
.pushseg
.segment "CV3_GRIP"
.proc Cv3GripWall
 stx Cv3Temp3
 jsr Cv3SolidPoint
 bcs Done
 ldx Cv3Temp3
 ldy #20
 jmp Cv3SolidPoint
Done:rts
.endproc
.popseg
