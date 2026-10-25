; Dedicated front-end/lives renderer. Dynamic player records need the same
; pointer snapshot and art-bank ownership that DrawAll prepares during play.
; Calling DrawMetasprite directly previously consumed stale helper pointers.
X5MenuNameAddress=$2328
.export X5MenuNameAddress
.pushseg
.segment "X5_MENU_UI"
.proc X5PortraitRender
 pha
 phx
 phy
 jsr X5PortraitPosition
 farcall HpPrepareNativePointers
 lda ObjectMetasprite
 cmp #METASPRITE_SAMUS_BODY
 beq NativeReady
 jsr CrossoverGraphicsBank
NativeReady:
 ply
 plx
 pla
 farcall DrawMetasprite,jmp
.endproc
.proc X5PortraitPosition
 lda SelectedCharacter
 cmp #19
 beq Turtle
 cmp #5
 beq Cv3
 cmp #15
 bne Done
 lda OperMode
 cmp #1
 bne Done
 lda Player_Y_Position
 clc
 adc #14                       ; Keep Mac's head below WORLD on the lives card.
 sta Player_Y_Position
Done:rts
Cv3:
 lda Cv3Variant
 cmp #3
 bne Done
 lda OperMode
 cmp #1
 bne Done
 lda #8
 bne Offset
Turtle:
 ldx TnVariant
 lda OperMode
 cmp #1
 beq Lives
 cpx #1
 bne Done
 lda #8                        ; Raphael's raised sai fits the preview card.
 bne Offset
Lives:
 lda LivesOffsets,x
Offset:
 clc
 adc Player_Y_Position
 sta Player_Y_Position
 rts
LivesOffsets:.byte 4,16,8,4
.endproc
.popseg
