; Quiet event boundary for the initial WIP: no host APU stores or invented
; sound mapping. Original event values and actor-visible music return X remain.
.export PpNativeQuietSfx,PpNativeQuietMusic,PpNativeUnpublishedMaterial
.export PpNativeMotionExport
PpNativeQuietSfx:
 sta $c0ad
 stx $c0ae
 sty $c041
 lda #6
 sta $c6d1
 rts
PpNativeQuietMusic:
 sta $c0af
 ; Original6:AA1F/AA46 arithmetic, including ASL carry. All legal source
 ; music values are small; retain all128 low-input results nonetheless.
 cmp #$80
 bcs QuietStop
 sta $c006
 asl
 asl
 adc $c006
 tax
 inx
 inx
 inx
 inx
 lda #3
 rts
QuietStop:
 lda #$e0
 rts
PpNativeUnpublishedMaterial:
 ; Exact original entry guards need materials18/10/22/2 or demo0735!=0.
 ; This adapter only publishes0/1/20 and initializes0735=0. This leaf is
 ; unreachable in the closed initial native material/player domain.
 rts
PpNativeMotionExport:
 ; Native scroll/parser and 4.4 speed consumers have smaller units than
 ; original32px alignment. Bound transport samples; leave source/world X exact.
 lda Player_X_Scroll
 bmi NegativeSample
 cmp #6
 bcc SampleReady
 lda #5
 bne SampleReady
NegativeSample:
 cmp #$fb
 bcs SampleReady
 lda #$fb
SampleReady:
 sta Player_X_Scroll
 asl
 asl
 asl
 asl
 sta Player_X_Speed
 lda $c615
 beq FaceLeft
 lda #1
 bne FaceReady
FaceLeft:
 lda #2
FaceReady:
 sta PlayerFacingDir
 rts
