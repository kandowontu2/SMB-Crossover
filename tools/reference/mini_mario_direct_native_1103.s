.setcpu "6502"
.export MiniRareClass, MiniRareTargets, MiniRarePrepare, MiniRarePrepareTail
.export MiniDirectStubs, MiniDirectWorker, MiniDirectEnd

FarTarget = $016c
NextBank = $0162
SafecallA = $016a
CurrentC = $7da1
MapC = $80c2

; GmNrRare Found has original X in Y; native caller Y/P are below the
; two local JSR bytes. GmNrFinish restores them and enters FarCall+3.
.segment "RARE_CLASS"
MiniRareClass:
 lda MiniRareTargets,x
 beq MiniRareForeign
 sta FarTarget
 jmp MiniRarePrepare
MiniRareForeign:
 jmp $a824
.segment "RARE_TABLE"
MiniRareTargets:
 .byte <(MiniDirectStubs+0), <(MiniDirectStubs+3), <(MiniDirectStubs+6)
 .byte 0,<(MiniDirectStubs+12),<(MiniDirectStubs+15)
 .byte <(MiniDirectStubs+18),<(MiniDirectStubs+21),<(MiniDirectStubs+24)
 .byte <(MiniDirectStubs+27),<(MiniDirectStubs+30),<(MiniDirectStubs+33)
 .byte <(MiniDirectStubs+36),<(MiniDirectStubs+39),<(MiniDirectStubs+42)
.segment "RARE_PREPARE"
MiniRarePrepare:
 lda #>MiniDirectStubs
 sta FarTarget+1
 tya
 tax
 pla
 pla
 jmp MiniRarePrepareTail
.segment "RARE_PREPARE_TAIL"
MiniRarePrepareTail:
 lda #$d4
 jmp $a60d

.segment "DIRECT_BODY"
MiniDirectStubs:
 .repeat 15, I
  .if I=9
   jmp MiniDirectYes
  .elseif I=12
   jmp MiniDirectAdder
  .elseif I=13
   jmp MiniDirectBox
  .else
   jmp MiniDirectWorker
  .endif
 .endrepeat
MiniDirectWorker:
 ; No zero-page/global scratch: frame is P,X,Y,old C mapping. Input A
 ; remains in the native SafecallA immediate until the actual call.
 php
 txa
 pha
 tya
 pha
 lda CurrentC
 pha
 lda FarTarget
 sec
 sbc #<MiniDirectStubs
 sta FarTarget
 lda #$a0
 sta FarTarget+1
 lda $0f
 cmp #8
 bne MiniDirectCold
 lda #2
 jsr MapC
 ; Ready2 is reachable only after the authenticated cold data/code copy,
 ; Fresh and first native Main. Both live owner markers below cover every
 ; later frame, including FrameCounter 0; Main retains its own epoch guard.
 lda $c300
 cmp #2
 bne MiniDirectCold
 ldx #3
@header:
 lda $dfe0
 cmp #$a7
 bne MiniDirectCold
 lda $dfe1
 cmp #41
 bne MiniDirectCold
 txa
 jsr MapC
 dex
 cpx #1
 bne @header
 lda #3
 bne MiniDirectCall
MiniDirectCold:
 lda FarTarget
 clc
 adc #$8c
 sta FarTarget
 lda #$b0
 sta FarTarget+1
 lda #$c1
MiniDirectCall:
 sta NextBank
 tsx
 lda $0104,x
 pha
 ldy $0102,x
 lda $0103,x
 tax
 plp
 jsr $015d
 ; Replace our saved input frame with the service's returned P,A,X,Y.
 php
 pha
 txa
 pha
 tya
 pha
 tsx
 lda $0105,x
 sta CurrentC
 sta $5116
 ldy #4
 jmp MiniDirectResult
.segment "DIRECT_RETURN"
MiniDirectResult:
@result:
 lda $0101,x
 sta $0105,x
 inx
 dey
 bne @result
 txs
 jmp MiniDirectFinish
.segment "DIRECT_FINISH"
MiniDirectFinish:
 pla
 tay
 pla
 tax
 pla
 plp
 rts
MiniDirectYes:
 sec
 rts
MiniDirectAdder:
 ldy #2
 sec
 rts
.segment "DIRECT_BOX"
MiniDirectBox:
 ldy #1
 sec
 rts
MiniDirectEnd:
