; Authored SMB terrain adapter: exact single-cell native block dispatch.
; Source attack motion/art remains CV3; SMB brick durability is an adaptation.
.pushseg
.segment "CV3_COMBAT"
.proc Cv3MeleeBlocks
 lda Cv3MeleeBlockHit
 jne Done
 lda Cv3RectW
 sec
 sbc #1
 sta Cv3BlockRemaining
 ldx PlayerFacingDir
 cpx #2
 bne Right
 lda Cv3RectX
 clc
 adc Cv3BlockRemaining
 sta MmProbeX
 lda Cv3RectPage
 adc #0
 jmp Page
Right:
 lda Cv3RectX
 sta MmProbeX
 lda Cv3RectPage
Page:sta MmProbePage
 lda Cv3RectY
 clc
 adc #4
 sta MmProbeY
Loop:
 jsr Cv3BlockPoint
 bcs Hit
 lda Cv3BlockRemaining
 beq Done
 cmp #8
 bcc Tail
 lda #8
Tail:
 sta Cv3BlockDelta
 lda Cv3BlockRemaining
 sec
 sbc Cv3BlockDelta
 sta Cv3BlockRemaining
 lda PlayerFacingDir
 cmp #2
 beq LeftStep
 clc
 lda MmProbeX
 adc Cv3BlockDelta
 sta MmProbeX
 lda MmProbePage
 adc #0
 sta MmProbePage
 jmp Loop
LeftStep:
 sec
 lda MmProbeX
 sbc Cv3BlockDelta
 sta MmProbeX
 lda MmProbePage
 sbc #0
 sta MmProbePage
 jmp Loop
Hit:
 lda #1
 sta Cv3MeleeBlockHit
Done:rts
.endproc
.proc Cv3ProjectileBlock
 ldx Cv3Slot
 lda Cv3ShotX,x
 sta MmProbeX
 lda Cv3ShotPage,x
 sta MmProbePage
 lda Cv3ShotY,x
 sta MmProbeY
 jsr Cv3BlockPoint
 php
 ldx Cv3Slot
 plp
 rts
.endproc
; MmProbeX/Page/Y -> C=solid/activated. Native object offset is preserved.
.proc Cv3BlockPoint
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
 beq Empty
 cmp #$23
 beq Empty
 cmp #$26
 beq Empty
 cmp #$c2
 beq Empty
 cmp #$c3
 beq Empty
 sta R3
 jsr BlockBumpedChk
 bcs Activate
 lda R3
 cmp #$51
 beq Activate
 cmp #$52
 bne OtherTerrain
 ; The parser marks foundation cells independently of shared brick artwork.
 clc
 lda R6
 adc #<(MmSolidTerrain-Block_Buffer_1)
 sta M0
 lda R7
 adc #>(MmSolidTerrain-Block_Buffer_1)
 sta M1
 ldy R2
 lda (M0),y
 beq Activate
 bne Solid
OtherTerrain:
 ldy R3
 lda MTileAttribute,y
 and #MTILE_SOLID
 beq Empty
Solid:sec
 rts
Empty:clc
 rts
Activate:
 phx
 lda ObjectOffset
 pha
 lda MmProbeX
 sta MmBulletX
 lda MmProbePage
 sta MmBulletPage
 lda MmProbeY
 sta MmBulletY
 lda PlayerFacingDir
 sta MmBulletDir
 lda #10 ; zero-extents native point; never enters the extra melee corner loop
 sta MmBulletType
 ldx #0
 stx MmSlot
 farcall MegaManWeapons::BombPoint
 lda #0
 sta MmBulletType
 pla
 sta ObjectOffset
 plx
 sec
 rts
.endproc
.popseg
