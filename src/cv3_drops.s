.pushseg
.segment "CV3_COMBAT"
; Two independent physical hearts never consume/replace a native enemy slot.
; Heart1/5 values are originalCV3; enemy probability/locations are SMB adaptation.
.proc Cv3EnemyDropGate
 php
 pha
 phx
 phy
 farcall Cv3IsActive
 jcc Legacy
 stx Cv3HitSlot
 lda PseudoRandomBitReg+1
 and #3
 jne Done
 ldx #1
Find:lda Cv3DropType,x
 jeq Spawn
 dex
 jpl Find
 jmi Done
Spawn:
 lda #1
 ldy PseudoRandomBitReg+2
 cpy #192
 bcc :+
 lda #5
: sta Cv3DropType,x
 lda #0
 sta Cv3DropAge,x
 sta Cv3DropVY,x
 sta Cv3DropFrac,x
 ldy Cv3HitSlot
 lda Enemy_X_Position,y
 clc
 adc #8
 sta Cv3DropX,x
 lda Enemy_PageLoc,y
 adc #0
 sta Cv3DropPage,x
 lda Enemy_Y_Position,y
 clc
 adc #8
 sta Cv3DropY,x
Done:
 ply
 plx
 pla
 plp
 rts
Legacy:
 ply
 plx
 pla
 plp
 farcall Z2EnemyDropGate,jmp
.endproc
.proc Cv3UpdateDrops
 ldx #1
Loop:
 stx Cv3HitSlot
 lda Cv3DropType,x
 jeq Next
 inc Cv3DropAge,x
 lda Cv3DropAge,x
 cmp #240
 jcs Kill
 clc
 lda Cv3DropFrac,x
 adc #64
 sta Cv3DropFrac,x
 jcc Move
 lda Cv3DropVY,x
 cmp #3
 jcs Move
 inc Cv3DropVY,x
Move:
 lda Cv3DropY,x
 clc
 adc Cv3DropVY,x
 sta Cv3DropY,x
 cmp #240
 jcs Kill
 lda Cv3DropX,x
 sta MmProbeX
 lda Cv3DropPage,x
 sta MmProbePage
 lda Cv3DropY,x
 clc
 adc #8
 sta MmProbeY
 jsr Cv3ReadCell
 jcc Collect
 lda MmProbeY
 and #$f0
 sec
 sbc #8
 ldx Cv3HitSlot
 sta Cv3DropY,x
 lda #0
 sta Cv3DropVY,x
 sta Cv3DropFrac,x
Collect:
 ldx Cv3HitSlot
 lda Player_X_Position
 clc
 adc #8
 sec
 sbc Cv3DropX,x
 sta R0
 lda Player_PageLoc
 sbc Cv3DropPage,x
 sta R1
 lda R0
 clc
 adc #11
 sta R0
 lda R1
 adc #0
 jne Next
 lda R0
 cmp #23
 jcs Next
 lda Player_Y_Position
 clc
 adc #16
 sec
 sbc Cv3DropY,x
 clc
 adc #20
 cmp #41
 jcs Next
 ldy Cv3Variant
 dey
 lda Cv3Hearts,y
 clc
 adc Cv3DropType,x
 cmp #100
 bcc :+
 lda #99
: sta Cv3Hearts,y
 lda #Sfx_CoinGrab
 sta Square2SoundQueue
Kill:
 lda #0
 sta Cv3DropType,x
Next:
 ldx Cv3HitSlot
 dex
 jpl Loop
 rts
.endproc
; MmProbeX/Page/Y. Return C=solid, without touching actor or player positions.
.proc Cv3ReadCell
 lda MmProbeY
 cmp #$20
 jcc No
 cmp #$f0
 jcs No
 and #$f0
 sec
 sbc #$20
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
 sta R3
 tay
 lda MTileAttribute,y
 and #MTILE_SOLID
 jeq No
 sec
 rts
No:clc
 rts
.endproc
.popseg
