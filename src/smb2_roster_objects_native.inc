; Genuine ROM1 carry position prefix and full object integrators.
; Carry stops BEFORE original enemy animation/render (host owns it).
.pushseg
.segment "PARODIUS_BELLS"
S2O960F: lda S2Face ;1:960F a59d
S2O9611: eor #$01 ;1:9611 4901
S2O9613: tay  ;1:9613 a8
S2O9614: iny  ;1:9614 c8
S2O9615: pha
 tya
 sta S2ObjectFacing0,x
 pla ; original STY zp,X; next LDA defines NZ
S2O9617: lda S2X ;1:9617 a528
S2O9619: sta S2X+1,x ;1:9619 9529
S2O961B: lda S2Page ;1:961B a514
S2O961D: sta S2Page+1,x ;1:961D 9515
S2O961F: lda S2YPage ;1:961F a51e
S2O9621: sta S2ProbeDirection ;1:9621 8507
S2O9623: lda S2Y ;1:9623 a532
S2O9625: ldy S2ObjectHitbox,x ;1:9625 bc8904
S2O9628: cpy #$03 ;1:9628 c003
S2O962A: jeq S2O9636 ;1:962A f00a
S2O962C: cpy #$02 ;1:962C c002
S2O962E: jeq S2O9636 ;1:962E f006
S2O9630: sbc #$0e ;1:9630 e90e
S2O9632: jcs S2O9636 ;1:9632 b002
S2O9634: dec S2ProbeDirection ;1:9634 c607
S2O9636: ldy S2Animation ;1:9636 a4c7
S2O9638: cpy #$04 ;1:9638 c004
S2O963A: clc  ;1:963A 18
S2O963B: jne S2O964D ;1:963B d010
S2O963D: ldy S2Size ;1:963D acf606
S2O9640: cpy #$01 ;1:9640 c001
S2O9642: ldy S2NativeCharacter ;1:9642 a48f
S2O9644: jcc S2O964A ;1:9644 9004
S2O9646: iny  ;1:9646 c8
S2O9647: iny  ;1:9647 c8
S2O9648: iny  ;1:9648 c8
S2O9649: iny  ;1:9649 c8
S2O964A: adc S2CarryCrouch,y ;1:964A 790796
S2O964D: php  ;1:964D 08
S2O964E: ldy S2ObjectLift,x ;1:964E b4a8
S2O9650: clc  ;1:9650 18
S2O9651: ldx S2Size ;1:9651 aef606
S2O9654: jeq S2O965D ;1:9654 f007
S2O9656: iny  ;1:9656 c8
S2O9657: iny  ;1:9657 c8
S2O9658: iny  ;1:9658 c8
S2O9659: iny  ;1:9659 c8
S2O965A: iny  ;1:965A c8
S2O965B: iny  ;1:965B c8
S2O965C: iny  ;1:965C c8
S2O965D: jsr S2CarryAddLo ; authentic class-patched carry table
S2O9660: ldx S2Source12 ;1:9660 a612
S2O9662: sta S2Y+1,x ;1:9662 9533
S2O9664: lda S2ProbeDirection ;1:9664 a507
S2O9666: jsr S2CarryAddHi ; authentic class-patched carry table
S2O9669: plp  ;1:9669 28
S2O966A: adc #$00 ;1:966A 6900
S2O966C: sta S2YPage+1,x ;1:966C 951f
 jmp S2CarryGeometryReturn
S2O9E4B: txa  ;1:9E4B 8a
S2O9E4C: clc  ;1:9E4C 18
S2O9E4D: adc #$0a ;1:9E4D 690a
S2O9E4F: tax  ;1:9E4F aa
S2O9E50: lda S2VX+1,x ;1:9E50 b53d
S2O9E52: clc  ;1:9E52 18
S2O9E53: adc S2AX+1,x ;1:9E53 7dcc04
S2O9E56: pha  ;1:9E56 48
S2O9E57: asl a ;1:9E57 0a
S2O9E58: asl a ;1:9E58 0a
S2O9E59: asl a ;1:9E59 0a
S2O9E5A: asl a ;1:9E5A 0a
S2O9E5B: sta S2Math1 ;1:9E5B 8501
S2O9E5D: pla  ;1:9E5D 68
S2O9E5E: lsr a ;1:9E5E 4a
S2O9E5F: lsr a ;1:9E5F 4a
S2O9E60: lsr a ;1:9E60 4a
S2O9E61: lsr a ;1:9E61 4a
S2O9E62: cmp #$08 ;1:9E62 c908
S2O9E64: jcc S2O9E68 ;1:9E64 9002
S2O9E66: ora #$f0 ;1:9E66 09f0
S2O9E68: sta S2Math0 ;1:9E68 8500
S2O9E6A: ldy #$00 ;1:9E6A a000
S2O9E6C: asl a ;1:9E6C 0a
S2O9E6D: jcc S2O9E70 ;1:9E6D 9001
S2O9E6F: dey  ;1:9E6F 88
S2O9E70: sty S2Math2 ;1:9E70 8402
S2O9E72: lda S2XF+1,x ;1:9E72 bd0804
S2O9E75: clc  ;1:9E75 18
S2O9E76: adc S2Math1 ;1:9E76 6501
S2O9E78: sta S2XF+1,x ;1:9E78 9d0804
S2O9E7B: lda S2X+1,x ;1:9E7B b529
S2O9E7D: adc S2Math0 ;1:9E7D 6500
S2O9E7F: sta S2X+1,x ;1:9E7F 9529
S2O9E81: rol S2Math1 ;1:9E81 2601
S2O9E83: cpx #$0a ;1:9E83 e00a
S2O9E85: jcs S2O9E9E ;1:9E85 b017
S2O9E87: lda #$00 ;1:9E87 a900
S2O9E89: sta S2ObjectLift,x ;1:9E89 9da404
S2O9E8C: lda S2ObjectType,x ;1:9E8C b590
S2O9E8E: cmp #$1b ;1:9E8E c91b
S2O9E90: jeq S2O9E9E ;1:9E90 f00c
S2O9E92: cmp #$0f ;1:9E92 c90f
S2O9E94: jeq S2O9E9E ;1:9E94 f008
S2O9E96: cmp #$10 ;1:9E96 c910
S2O9E98: jeq S2O9E9E ;1:9E98 f004
S2O9E9A: ldy S2Horizontal ;1:9E9A a4ec
S2O9E9C: jeq S2O9EA6 ;1:9E9C f008
S2O9E9E: lsr S2Math1 ;1:9E9E 4601
S2O9EA0: lda S2Page+1,x ;1:9EA0 b515
S2O9EA2: adc S2Math2 ;1:9EA2 6502
S2O9EA4: sta S2Page+1,x ;1:9EA4 9515
S2O9EA6: ldx S2Source12 ;1:9EA6 a612
S2O9EA8: rts  ;1:9EA8 60
S2CarryGeometryReturn: rts
S2CarryOffsets: .byte 0,250,255,0,8,12,24,26,2,6,10,12,24,26,28,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,246,255,0,8,12,24,26,254,6,10,12,24,26,28,255,255,0,0,0,0,0,255,0,0,0,0,0,0,0,252,255,0,8,12,24,26,4,6,10,12,24,26,28,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,247,255,0,8,12,24,26,255,6,10,12,24,26,28,255,255,0,0,0,0,0,255,0,0,0,0,0,0
S2CarryCrouch: .byte 10,14,10,13,4,7,4,6
.popseg
