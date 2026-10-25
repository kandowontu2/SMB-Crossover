; Same-bank additions; all existing code, RAM and CHR addresses stay fixed.
.pushseg
.segment "TMNT_CORE"
.proc TnPickupScreenBox
 lda Enemy_Rel_XPos
 clc
 adc #4
 sta EnemyBoundingBoxCoord,y
 lda Enemy_Rel_XPos
 clc
 adc #12
 sta EnemyBoundingBoxCoord+2,y
 inx
 iny
 iny
 iny
 iny
 jsr CheckRightScreenBBox
 dey
 dey
 dey
 dey
 rts
.endproc
.segment "LM_CORE"
; Native gains are short positive modular deltas; loss is DEC (delta FF).
; X5ProfilesNewGame clears the marker before the next session initializes.
; Preserve X/Y and return C for keep/reset, including INC FF->00.
.proc LmLifeAdvanced
 lda NumberofLives
 pha
 sec
 sbc LmLife
 eor #$80
 cmp #$80
 pla
 sta LmLife
 rts
.endproc
.popseg
