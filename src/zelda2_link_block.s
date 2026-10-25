.pushseg
.segment "Z2_LOGIC"
; MmProbeX/Page/Y exact world point; A=0sword/1projectile. C=solid.
.proc Z2BlockPoint
 sta Z2BodyScratch+9
 lda MmProbeY
 cmp #$20
 jcc Empty
 cmp #$f0
 jcs Empty
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
 jeq Empty
 cmp #$23
 jeq Empty
 cmp #$26
 jeq Empty
 cmp #$c2
 jeq Empty
 cmp #$c3
 jeq Empty
 sta R3
 jsr BlockBumpedChk
 bcs Activate
 lda Z2BodyScratch+9
 jne Solid
 lda Z2Tech
 and #$80
 jeq Solid
 lda R3
 cmp #$51
 beq Activate
 cmp #$52
 jne Solid
 clc
 lda R6
 adc #<(MmSolidTerrain-Block_Buffer_1)
 sta M0
 lda R7
 adc #>(MmSolidTerrain-Block_Buffer_1)
 sta M1
 ldy R2
 lda (M0),y
 bne Solid
Activate:
 lda #14
 sta MmBulletType
 lda MmProbeX
 sta MmBulletX
 lda MmProbePage
 sta MmBulletPage
 lda MmProbeY
 sta MmBulletY
 lda PlayerFacingDir
 sta MmBulletDir
 lda #0
 sta MmSlot
 tax
 farcall MegaManWeapons::BombPoint
 lda #0
 sta MmBulletType
Solid:sec
 rts
Empty:clc
 rts
.endproc
.proc Z2SwordBlocks
 lda Z2RectW
 beq Done
 lda Z2RectX
 clc
 adc #7
 sta MmProbeX
 lda Z2RectPage
 adc #0
 sta MmProbePage
 lda Z2RectY
 clc
 adc #1
 sta MmProbeY
 lda #0
 jsr Z2BlockPoint
Done:rts
.endproc
.popseg
