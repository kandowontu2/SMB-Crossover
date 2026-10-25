; Generated from original TMNT USA machine instructions; retain provenance.
TnVYHi=$5c00
TnVYLo=$5c01
TnVXHi=$5c02
TnVXLo=$5c03
TnNativeFlags=$5c04
TnHeld=$5c05
TnJumpHold=$5c06
TnJumpStage=$5c07
TnNativeState=$5c08
.export TnVYHi,TnVYLo,TnVXHi,TnVXLo,TnNativeFlags,TnHeld,TnJumpHold,TnJumpStage,TnNativeState
.export TnNativeGravity,TnNativeVariableJump,TnNativeXVelocity
.pushseg
.segment "TMNT_CORE"
.proc TnNativeGravity
Na5f0: lda TnVYLo ; TMNT4:$A5F0
Na5f3: clc ; TMNT4:$A5F3
Na5f4: adc #$54 ; TMNT4:$A5F4
Na5f6: sta TnVYLo ; TMNT4:$A5F6
Na5f9: lda TnVYHi ; TMNT4:$A5F9
Na5fc: adc #$00 ; TMNT4:$A5FC
Na5fe: jpl Na608 ; TMNT4:$A5FE
Na600: cmp #$f9 ; TMNT4:$A600
Na602: jcs Na60e ; TMNT4:$A602
Na604: lda #$f9 ; TMNT4:$A604
Na606: jne Na60e ; TMNT4:$A606
Na608: cmp #$09 ; TMNT4:$A608
Na60a: jcc Na60e ; TMNT4:$A60A
Na60c: lda #$09 ; TMNT4:$A60C
Na60e: sta TnVYHi ; TMNT4:$A60E
Na611: rts ; TMNT4:$A611
.endproc
.proc TnNativeVariableJump
Na007: lda TnHeld ; TMNT4:$A007
Na009: and #$80 ; TMNT4:$A009
Na00b: and TnJumpHold ; TMNT4:$A00B
Na00e: sta TnJumpHold ; TMNT4:$A00E
Na011: ldy TnJumpStage ; TMNT4:$A011
Na014: cpy #$08 ; TMNT4:$A014
Na016: jcs Done ; TMNT4:$A016
Na018: inc TnJumpStage ; TMNT4:$A018
Na01b: iny ; TMNT4:$A01B
Na01c: cpy #$04 ; TMNT4:$A01C
Na01e: jeq Na026 ; TMNT4:$A01E
Na020: cpy #$08 ; TMNT4:$A020
Na022: jeq Na032 ; TMNT4:$A022
Na024: jne Done ; TMNT4:$A024
Na026: lda TnJumpHold ; TMNT4:$A026
Na029: jne Done ; TMNT4:$A029
Na02b: lda #$fd ; TMNT4:$A02B
Na02d: ldy #$90 ; TMNT4:$A02D
Na02f: jmp Na047 ; TMNT4:$A02F
Na032: lda TnJumpHold ; TMNT4:$A032
Na035: jeq Done ; TMNT4:$A035
Na037: lda TnNativeFlags ; TMNT4:$A037
Na03a: and #$04 ; TMNT4:$A03A
Na03c: jne Na043 ; TMNT4:$A03C
Na03e: lda #$08 ; TMNT4:$A03E
Na040: sta TnNativeState ; TMNT4:$A040
Na043: lda #$fa ; TMNT4:$A043
Na045: ldy #$00 ; TMNT4:$A045
Na047: sta TnVYHi ; TMNT4:$A047
Na04a: sty TnVYLo ; TMNT4:$A04A
Done:rts
.endproc
.proc TnNativeXVelocity
Na764: lda TnNativeFlags ; TMNT4:$A764
Na767: and #$10 ; TMNT4:$A767
Na769: jeq Na76d ; TMNT4:$A769
Na76b: iny ; TMNT4:$A76B
Na76c: iny ; TMNT4:$A76C
Na76d: tya ; TMNT4:$A76D
Na76e: asl a ; TMNT4:$A76E
Na76f: tay ; TMNT4:$A76F
Na770: lda TnVelocityTable,Y ; TMNT4:$A770
Na773: sta TnVXHi ; TMNT4:$A773
Na776: lda TnVelocityTable+1,Y ; TMNT4:$A776
Na779: sta TnVXLo ; TMNT4:$A779
Na77c: rts ; TMNT4:$A77C
.endproc
TnVelocityTable:
.byte $00,$00,$02,$40,$fd,$c0,$03,$00,$fd,$00,$c0,$fe,$40,$01
.popseg
