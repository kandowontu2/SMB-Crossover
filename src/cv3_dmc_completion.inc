; Original CV3 clears request priority after DMA fetch completion without
; clearing4011: the last buffered byte must drain and its actual DAC is held.
.proc Cv3DmcEndedGate
 php
 lda BassDmcActive
 cmp #3
 beq SourceCompletion
 lda #0
 jsr Cv3DmcOwnerWrite
 sta $4011 ; exact existing ordinary completion behavior
 plp
 rts
SourceCompletion:lda #0
 jsr Cv3DmcOwnerWrite
 plp
 rts
.endproc
.assert Cv3DmcEndedGate=$9a10,lderror,"After the exact18-byte Mac gate"
.assert *=$9a29,lderror,"Leave the final original tail byte unused"
