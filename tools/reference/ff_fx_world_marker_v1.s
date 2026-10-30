; Proposed FF-only native-world marker. Genuine C93 ROM must already be live
; through native DrawAll's FF graphics bank contract. No ExRAM or RAM3 access.
; The caller is the selected22 branch of the genuine native flash probe.
.setcpu "6502"
.import SmFreezeNativeFlashEnemy,CurrentOAMOffset,RgOamRotation
.import Sprite_Y_Position,Sprite_Attributes
.segment "FF_FX_WORLD_MARKER"
.export FfMuxWorldDraw,FfMuxWorldDrawEnd

.proc FfMuxWorldDraw
 ; Original selected22 probe supplied A22/Cset. The actual native flash leaf
 ; starts TYA, so incoming A/N/Z are dead; LDA/PHA retain C/V/D/I exactly.
 lda CurrentOAMOffset
 pha
 jsr SmFreezeNativeFlashEnemy
 ; Native flash tail renders and performs all actual flip logic, returning
 ; here once. Preserve its complete returned state around metadata only.
 php
 pha
 txa
 pha
 tya
 pha
 jsr Span
 beq Restore
Scan:
 lda Sprite_Y_Position,x
 cmp #240
 bcs Next
 lda Sprite_Attributes,x
 and #3
 cmp #1
 beq Mark
Next:
 inx
 inx
 inx
 inx
 dey
 dey
 dey
 dey
 bne Scan
 beq Restore
Mark:
 jsr Span
Tag:
 lda Sprite_Attributes,x
 ora #$10
 sta Sprite_Attributes,x
 inx
 inx
 inx
 inx
 dey
 dey
 dey
 dey
 bne Tag
Restore:
 ; Remove initial logical offset under savedY/X/A/P. Return addresses and
 ; all caller-owned live page1 bytes retain the real native stack contract.
 tsx
 lda $0104,x
 sta $0105,x
 lda $0103,x
 sta $0104,x
 lda $0102,x
 sta $0103,x
 lda $0101,x
 sta $0102,x
 inx
 txs
 pla
 tay
 pla
 tax
 pla
 plp
 rts
Span:
 ; Span's own JSR return adds two bytes to the marker's stack. Actual
 ; CurrentOAMOffset is monotonic: native header validation rejects256.
 tsx
 lda $0107,x
 tay
 lda CurrentOAMOffset
 sec
 sbc $0107,x
 beq Empty
 bcc Empty
 pha
 tya
 clc
 adc RgOamRotation
 tax
 pla
 tay
 rts
Empty:
 ldy #0
 rts
.endproc
FfMuxWorldDrawEnd:
.assert FfMuxWorldDrawEnd-FfMuxWorldDraw<=200,error,"FF marker measured source budget"
