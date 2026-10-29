.pushseg
.segment "PARODIUS_BELLS"
.proc S2NativeTileProbe
 ; Native X=player0/object1..3,Y=actual hitbox point. R0..R7 are
 ; foreground caller scratch. The original collision response remains native.
 txa
 pha
 lda S2DF011,y
 pha
 asl
 lda #0
 bcc :+
 lda #$ff
:sta R5
 pla
 clc
 adc S2X,x
 and #$f0
 sta R4
 lda S2Page,x
 adc R5
 sta R5
 lda S2DF055,y
 pha
 asl
 lda #0
 bcc :+
 lda #$ff
:sta R7
 pla
 clc
 adc S2Y,x
 and #$f0
 sta R6
 lda S2YPage,x
 adc R7
 bne Empty
 lda R6
 cmp #32
 bcc Empty
 cmp #240
 bcs Empty
 lda R6
 sta R2
 lda R6
 sec
 sbc #32
 pha
 lda R5
 and #1
 .repeat 4
 asl
 .endrepeat
 sta R0
 lda R4
 .repeat 4
 lsr
 .endrepeat
 ora R0
 jsr GetBlockBufferAddr
 pla
 tay
 lda (R6),y
 beq Empty
 cmp #$23
 beq Empty
 cmp #$26
 beq Empty
 cmp #$c2
 beq Empty
 cmp #$c3
 beq Empty
 cmp #$5f
 beq Empty
 cmp #$60
 beq Empty
 tay
 lda MTileAttribute,y
 and #MTILE_SOLID
 beq Empty
 lda S2ProbeDirection
 cmp #2
 bcs Solid
 lda R4
 sta S2HeadX
 lda R5
 sta S2HeadPage
 lda R2
 sta S2HeadY
Solid:
 lda #$ff                     ; ordinary source solid, no invented jar/spike.
 bne Result
Empty:lda #0
Result:sta S2Math0
 pla
 tax
 rts
.endproc
.proc S2WorldInteraction
 ; No SMB2 cherry/climbable/potion room exists in SMB1. Root owns native
 ; pipe/vine/flagpole engine handoffs; this does not pretend to implement them.
 rts
.endproc
.proc S2GroundInteraction
 ; Called by real source downward support detection, not an input-only grant.
 lda S2Fresh
 and #$40
 beq No
 lda S2Duck
 bne No
 lda S2Holding
 bne No
 lda S2Vegetables
 beq No
 jsr S2FreeObject
 bcc No
 lda #$32
 sta S2ObjectType,x
 lda #$ff
 sta S2ObjectHost0,x
 lda #2                       ; genuine EnemyInit_Basic vegetable32 hitbox.
 sta S2ObjectHitbox,x
 jsr S2BeginLift
 dec S2Vegetables             ; only successful allocation spends one.
No:rts
.endproc
.proc S2QuicksandBoundary
 lda #0
 rts
.endproc
.proc S2ChrReloadBoundary
 lda #$ff
 sta S2PaletteAck             ; actual original keyframe toggled S2Size.
 rts
.endproc
.proc S2SwimFrame
 ; Authored SMB1-water adaptation, not an original SMB2 feature.
 ; Native class X/carry controls remain unchanged. SMB1 swim launch
 ; FE:80=-1.5px/update => Q4 E8; actual force13/256 held,10/256 released.
 lda #1
 sta S2Air
 lda S2Charge
 pha                          ; water uses this byte as the32-update stroke gate.
 jsr S2N8C1A
 pla
 sta S2Charge                 ; no dry crouch charge while underwater.
 lda S2Fresh
 bpl Gravity
 lda S2Charge
 bne Stroke
 lda S2VY
 bmi Gravity
Stroke:
 lda #$e8
 sta S2VY
 lda #0
 sta S2Float
 lda #$20
 sta S2Charge
Gravity:
 lda S2Held
 bmi Held
 lda #$a0
 bne Force
Held:lda #$d0
Force:clc
 adc S2Float
 sta S2Float
 bcc Limit
 inc S2VY
Limit:lda S2VY
 bmi Top
 cmp #$40
 bcc Top
 lda #$40
 sta S2VY
Top:lda S2YPage
 bne Collide
 lda S2Y
 cmp #20
 bcs Collide
 lda S2VY
 bpl Collide
 lda #0
 sta S2VY
Collide:jsr S2N8EFA
 jsr S2N9316
 jsr S2N8EA4
 jmp S2N8A50
.endproc
.popseg
