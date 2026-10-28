; Root-owned shared integration additions; original frozen asset leaf stays intact.
.pushseg
.segment "MAC_ROSTER_CORE"
.proc MacRosterRestDue
 jsr MacRosterVariant
 tax
 lda LmRest
 cmp MacRosterRestPeriod,x
 rts
.endproc

; The status name owns exactly seven cells; the next WORLD command starts
; at +18. Longer menu names never spill into that native command header.
.proc MacRosterStatusName
 cmp #0
 bne Done
 phx
 phy
 jsr MacRosterVariant
 tax
 lda Offsets,x
 tax
 ldy #0
Copy:
 lda Names,x
 sta VRAM_Buffer1+11,y
 inx
 iny
 cpy #7
 bcc Copy
 ply
 plx
 lda #0
Done:rts
Offsets:.byte 0,7,14
Names:.byte "L MAC  ","DOC    ","TYSON  "
.endproc
.popseg
