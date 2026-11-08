; Prototype for original bank7:F801 / relocated $B0DA only. No other
; C8D4 alignment caller changes. CPU proof links this at an arena address.
.setcpu "6502"
.segment "CLIMB_EDGE"
.export PpClimbEdgeAlign
ActorX=$c60f
Facing=$c615
Foot=$c084
QueryX=$b369
QueryY=$b36b
ReadPoint=$b310
Align=$c40b

PpClimbEdgeAlign:
 lda Facing
 beq Left
 cpy #24                       ; Original F7FF donor alignment operand.
 bne Fallback
 lda ActorX
 ldx ActorX+1
 clc
 adc #15
 bcc Boundary
 inx
 beq Fallback                  ; Reject wrapped 16-bit right edge.
 bne Boundary
Left:
 cpy #58                       ; Original F7EC donor alignment operand.
 bne Fallback
 lda ActorX
 ldx ActorX+1
Boundary:
 and #$f0
 sta QueryX
 stx QueryX+1
 ora QueryX+1
 beq Fallback                  ; No exterior cell left of world X=0.
 lda Foot
 sec
 sbc #24                       ; Same hand/wall row as WORLD_MATERIAL.
 sta QueryY
 lda Foot+1
 sbc #0
 sta QueryY+1
 bne Fallback
 jsr ReadPoint                  ; Native typed cell on right side of edge.
 lda #0
 rol a
 tax
 lda QueryX
 bne :+
 dec QueryX+1
: dec QueryX
 jsr ReadPoint                  ; Native typed cell on left side of edge.
 txa
 rol a                         ; bit1 right solid; bit0 left solid.
 cpy #24
 beq RightEdge
 cmp #1
 bne Fallback
 beq Top
RightEdge:
 cmp #2
 bne Fallback
 inc QueryX                     ; Restore the right-side interior sample.
 bne Top
 inc QueryX+1
Top:
 lda QueryY
 and #$f0
 sec
 sbc #1
 sta QueryY
 jsr ReadPoint                  ; Reject a wall with no exposed top here.
 bcc Accepted
Fallback:
 jmp Align

Accepted:
 jsr Align                     ; Retain source row, Y, scratch and ABI.
 php
 pha
 lda Facing
 beq CommitLeft
 lda QueryX
 sec
 sbc #8                        ; Host center starts outside by 8px.
 sta ActorX
 lda QueryX+1
 sbc #0
 jmp CommitPage
CommitLeft:
 lda QueryX
 clc
 adc #9                        ; Current sample is edge-1, not edge.
 sta ActorX
 lda QueryX+1
 adc #0
CommitPage:
 sta ActorX+1
 pla
 plp
 rts
