; Native TMNT NMI-only helpers in verified originalFF A1B2..A1FF.
; Existing TnFastProduct/Proto ownership applies: neither IRQ nor foreground
; reads the product registers. Reads return the product, never old operands.
.assert *=$a1b2,lderror,"Retain real command vectors and all earlier helpers"
.proc TnTempoProduct
 cpx #2
 bcc Original
 stx $5205
 sta $5206
 lda $5206
 bne Original                 ; Early-carry cases retain literal source loop/X.
 lda $5205
 sec
 sbc z:TnAudioZp+2           ; The accumulator before the ORIGINAL last ADC.
 clc
 adc z:TnAudioZp+2           ; Preserve exact last-ADC V, including signed wrap.
 ldx #0
 jmp $aad7                  ; Real original CMP80 / saturation / writer path.
Original:
 lda z:TnAudioZp+2           ; Proven source entry A==E2; no private RAM added.
 dex
 beq Done
 jmp $aacf                  ; Literal original CLC/ADC/carry/DEX loop.
Done:
 jmp $aad7
.endproc
.proc TnParserPointer
 ; Inline EVERY original AF96 instruction except its call/return overhead.
 ; The original numeric AF96 entry remains genuine for all other callers.
 ldy #0
 lda a:TnAudioRam+$22,x
 sta z:TnAudioZp
 lda a:TnAudioRam+$28,x
 sta z:TnAudioZp+1
 lda a:TnAudioRam+$16,x
 dec a:TnAudioRam+$04,x
 beq Expired
 jmp $a67f                  ; Exact original CPX2 flags/returns and parser body.
Expired:
 jmp $a91f                  ; Exact original command stream handler.
.endproc
.assert *<=$a200,lderror,"Retain genuine A200 duration helper and A300 table"
.export TnTempoProduct,TnParserPointer
