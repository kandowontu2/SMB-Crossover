; Whole private update. Native host still owns scroll advancement after return.
.segment "BB_HOST"
.export BbNativeUpdate,BbNativeShiftCamera
BbNativeUpdate:
 jsr BbNativeInput
 bcs BbNativeUpdateBegin
 rts                         ; Input already returned carryclear unchanged.
BbNativeUpdateBegin:
 jsr BbNativeShiftCamera
 jsr BbNativeIn
 ldx #3
:
 lda $c309,x
 sta $c380,x
 dex
 bpl :-
 lda #0
 sta $c3ef
 jsr BbNativeProxiesIn
 jsr BbNativeActor
 jsr BbPlayerStep
 jsr BbNativeOut
 jsr BbNativeCeiling
 bcc :+
 inc $c3ef
:
 lda Player_PageLoc
 cmp ScreenLeft_PageLoc
 bcc BbNativeClampLeft
 bne BbNativeLeftReady
 lda Player_X_Position
 cmp ScreenLeft_X_Pos
 bcs BbNativeLeftReady
BbNativeClampLeft:
 lda ScreenLeft_X_Pos
 sta Player_X_Position
 lda ScreenLeft_PageLoc
 sta Player_PageLoc
BbNativeLeftReady:
 jsr BbNativeIn
 jsr BbBubbleStep
 ldx #0
BbNativeTrappedNext:
 jsr BbNativeProxyIndices
 ldx $c3c1
 lda $c000,x
 beq BbNativeTrappedDone
 lda $c002,x
 and #16
 beq BbNativeTrappedDone
 stx $c026
 ldy $c3c2
 jsr BbTrappedEnemyStep
BbNativeTrappedDone:
 ldx $c3c0
 inx
 cpx #6
 bne BbNativeTrappedNext
 jsr BbNativeProxiesOut
 jsr BbNativeContacts
 jsr BbSourceClock
 lda Player_X_Position
 sec
 sbc $c380
 sta Player_X_Scroll
 asl
 asl
 asl
 asl
 sta Player_X_Speed
 lda Player_Y_Position
 sec
 sbc $c382
 sta Player_Y_Speed
 jsr BbNativeActor
 lda $c003,x
 beq :+
 lda #1
:
 sta Player_State
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sta Player_Pos_ForScroll
 jsr BbNativeDeath
 sec
 rts

BbNativeShiftCamera:
 jsr BbNativeObserve
 lda ScreenLeft_X_Pos
 sec
 sbc $c305
 sta $c3f0
 lda ScreenLeft_PageLoc
 sbc $c306
 sta $c3f1
 ora $c3f0
 beq BbNativeCameraDone
 ldx #$88
 ldy #$88
BbNativeCameraBubble:
 jsr BbNativeCameraActor
 inx
 inx
 inx
 inx
 tya
 clc
 adc #8
 tay
 cpx #$c4
 bne BbNativeCameraBubble
 ldx #$68
 ldy #$10
BbNativeCameraProxy:
 lda $c002,x
 and #16
 beq :+
 jsr BbNativeCameraActor
:
 inx
 inx
 inx
 inx
 tya
 clc
 adc #8
 tay
 cpx #$80
 bne BbNativeCameraProxy
BbNativeCameraDone:
 lda ScreenLeft_X_Pos
 sta $c305
 lda ScreenLeft_PageLoc
 sta $c306
 rts

BbNativeCameraActor:
 lda $c000,x
 beq BbNativeCameraReturn
 stx $c3f3
 sty $c3f4
 lda $c103,y
 sec
 sbc $c3f0
 sta $c3f2
 lda #0
 sbc $c3f1
 bne BbNativeCameraRetire
 lda $c3f2
 cmp #240
 bcs BbNativeCameraRetire
 sta $c103,y
 clc
 adc #8
 sta $c107,y
 rts
BbNativeCameraRetire:
 cpx #$88
 bcs BbNativeCameraRetireBubble
 txa
 sec
 sbc #$68
 lsr
 lsr
 tax
 jsr BbNativeProxyRestore
 ldx $c3f3
 lda #0
 sta $c000,x
 beq BbNativeCameraRestore
BbNativeCameraRetireBubble:
 jsr BbOriginal_DAB2
BbNativeCameraRestore:
 ldx $c3f3
 ldy $c3f4
BbNativeCameraReturn:
 rts
