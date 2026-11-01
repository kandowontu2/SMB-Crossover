; SMB Easy-mode stomp is an explicit host addition: Karnov's donor game has
; no SMB enemies. Restart the donor's normal jump selector/timer and let its
; unchanged F491..F58D motion supply every subsequent pixel. Do not integrate
; a second step here or leave the bounce solely in native Player_Y_Speed.
.export KrBounce
KrBounce:
 php
 pha
 lda KrReady
 cmp #$a7
 bne KrBounceNo
 lda GameEngineSubroutine
 cmp #8
 bne KrBounceNo
 lda GamePauseStatus
 and #1
 bne KrBounceNo
 lda KrState+$62
 and #$80
 ora #8
 sta KrState+$62
 lda #$20                  ; original normal jump's rising phase
 sta KrState+$66
 lda #0
 sta KrState+$6a
 sta KrState+$6b
 lda #1
 sta Player_State
 lda #$fd
 sta Player_Y_Speed
 sta KrDeltaY
 pla
 plp
 sec
 rts
KrBounceNo:
 pla
 plp
 clc
 rts
