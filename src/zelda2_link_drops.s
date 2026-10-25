.pushseg
.segment "Z2_LOGIC"
.proc Z2UpdateDropsGate
 jsr Z2IsActive
 bcs Active
 farcall InventoryUpdateDrops,jmp
Active:
 lda TimerControl
 jne Done
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda #5
 sta InvDropSlot
Loop:
 ldx InvDropSlot
 lda Z2DropKind,x
 jeq Next
 inc Z2DropAge,x
 lda Z2DropFraction,x
 clc
 adc #64
 sta Z2DropFraction,x
 bcc Move
 lda Z2DropVY,x
 cmp #3
 bcs Move
 inc Z2DropVY,x
Move:
 lda Z2DropY,x
 clc
 adc Z2DropVY,x
 sta Z2DropY,x
 cmp #240
 jcs Kill
 clc
 adc #15
 sta MmProbeY
 lda Z2DropX,x
 sta MmProbeX
 lda Z2DropPage,x
 sta MmProbePage
 jsr Z2ReadCell
 beq Collect
 cmp #$23
 beq Collect
 cmp #$26
 beq Collect
 cmp #$c2
 beq Collect
 cmp #$c3
 beq Collect
 ldx InvDropSlot
 lda MmProbeY
 and #$f0
 sec
 sbc #16
 sta Z2DropY,x
 lda #0
 sta Z2DropVY,x
 sta Z2DropFraction,x
Collect:
 ldx InvDropSlot
 lda Z2DropX,x
 sec
 sbc ScreenLeft_X_Pos
 sta R0
 lda Z2DropPage,x
 sbc ScreenLeft_PageLoc
 bmi Kill
 cmp #2
 bcs Next
 lda Player_Y_HighPos
 cmp #1
 jne Next
 lda Player_X_Position
 clc
 adc #8
 sta R0
 lda Player_PageLoc
 adc #0
 sta R1
 lda R0
 sec
 sbc Z2DropX,x
 sta R0
 lda R1
 sbc Z2DropPage,x
 sta R1
 clc
 lda R0
 adc #12
 sta R0
 lda R1
 adc #0
 jne Next
 lda R0
 cmp #25
 bcs Next
 lda Player_Y_Position
 sec
 sbc Z2DropY,x
 clc
 adc #32
 cmp #49
 bcs Next
 lda Z2DropKind,x
 cmp #$90
 bcs Jar
 sec
 sbc #$8a
 cmp #4
 bcs Kill
 tay
 lda BagExpHi,y
 pha
 lda BagExpLo,y
 sta R0
 pla
 tay
 lda R0
 jsr Z2QueueExp
 jmp Sound
Jar:jsr Z2JarPickup
Sound:
 lda #Sfx_PowerUpGrab
 sta Square2SoundQueue
Kill:ldx InvDropSlot
 lda #0
 sta Z2DropKind,x
Next:dec InvDropSlot
 jpl Loop
Done:rts
BagExpLo:.byte <50,<100,<200,<500
BagExpHi:.byte >50,>100,>200,>500
.endproc
.proc Z2ReadCell
 lda MmProbeY
 cmp #32
 bcc Empty
 cmp #240
 bcs Empty
 and #$f0
 sec
 sbc #32
 sta R2
 lda MmProbePage
 and #1
 asl
 asl
 asl
 asl
 sta R0
 lda MmProbeX
 lsr
 lsr
 lsr
 lsr
 ora R0
 jsr GetBlockBufferAddr
 ldy R2
 lda (R6),y
 rts
Empty:lda #0
 rts
.endproc
.popseg
