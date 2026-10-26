; Pinned original TMNT source; generated source/storage experiment.
.pushseg
.segment "TMNT_NATIVE_AUDIO_PREFIX"
TnNativeImageStart:
  .assert *=$a000,lderror,"Original instruction offset c000"
  PHA
  .assert *=$a001,lderror,"Original instruction offset c001"
  LDA #$00
  .assert *=$a003,lderror,"Original instruction offset c003"
  .if ::TN_RAW_APU
  STA $4015
.else
  jsr ::TnSourceSTA15
.endif
  .assert *=$a006,lderror,"Original instruction offset c006"
  LDY #$00
  .assert *=$a008,lderror,"Original instruction offset c008"
  .if ::TN_RAW_APU
  STA $4000,y
.else
  jsr ::TnSourceSTA00Y
.endif
  .assert *=$a00b,lderror,"Original instruction offset c00b"
  INY
  .assert *=$a00c,lderror,"Original instruction offset c00c"
  CPY #$14
  .assert *=$a00e,lderror,"Original instruction offset c00e"
  .byte $d0,$f8 ; BNE source$c008
  .assert *=$a010,lderror,"Original instruction offset c010"
  PLA
  .assert *=$a011,lderror,"Original instruction offset c011"
  TAX
  .assert *=$a012,lderror,"Original instruction offset c012"
  LDA $a018,x
  .assert *=$a015,lderror,"Original instruction offset c015"
  JMP $b057
  .byte $4e,$53,$57,$5b,$5f,$63,$67,$6b,$6f,$73,$77,$7b,$7f,$83,$87,$8b,$0f,$00,$01,$08
  .assert *=$a02c,lderror,"Unchanged source bootstrap"
.segment "TMNT_DURATION_HELPER"
.proc TnFastDuration
 lda z:TnAudioZp+2
 asl
 asl
 asl
 asl
 ora TnAudioRam+$10,x
 tax
 lda TnDurationProducts,x
 ldx #1
 stx z:TnAudioZp+2
 ldx TnAudioRam+$92
 clc
 adc TnAudioRam+$10,x
 dec z:TnAudioZp+2
 rts
.endproc
.assert TnFastDuration=$a200,lderror,"Duration helper reserve"
.segment "TMNT_DURATION_TABLE"
TnDurationProducts:
 .byte 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
 .byte 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
 .byte 0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30
 .byte 0,3,6,9,12,15,18,21,24,27,30,33,36,39,42,45
 .byte 0,4,8,12,16,20,24,28,32,36,40,44,48,52,56,60
 .byte 0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75
 .byte 0,6,12,18,24,30,36,42,48,54,60,66,72,78,84,90
 .byte 0,7,14,21,28,35,42,49,56,63,70,77,84,91,98,105
 .byte 0,8,16,24,32,40,48,56,64,72,80,88,96,104,112,120
 .byte 0,9,18,27,36,45,54,63,72,81,90,99,108,117,126,135
 .byte 0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150
 .byte 0,11,22,33,44,55,66,77,88,99,110,121,132,143,154,165
 .byte 0,12,24,36,48,60,72,84,96,108,120,132,144,156,168,180
 .byte 0,13,26,39,52,65,78,91,104,117,130,143,156,169,182,195
 .byte 0,14,28,42,56,70,84,98,112,126,140,154,168,182,196,210
 .byte 0,15,30,45,60,75,90,105,120,135,150,165,180,195,210,225
.assert TnDurationProducts=$a300,lderror,"Duration table reserve"
.segment "TMNT_MOVED_SOURCE"
TnMovedStreamBegin:
  .byte $d7,$20,$cf,$cf,$cf,$cb,$d1,$20,$e3,$b5,$91,$81,$71,$61,$51,$41,$31,$21,$11,$01,$e4,$b1,$fd
  .word $a505 ; source pointer$9f40
  .byte $0d,$2d,$d1,$17,$fd
  .word $bf18 ; source pointer$9f47
  .byte $fd
  .word $a505 ; source pointer$9f4a
  .byte $e4,$76,$06,$e3,$2d,$e4,$96,$26,$e3,$36,$fd
  .word $a51c ; source pointer$9f57
  .byte $96,$e3,$16,$46,$96,$fd
  .word $a588 ; source pointer$9f5f
  .byte $e3,$06,$06,$46,$76,$e2,$06,$d1,$20,$e4,$fd
  .word $a57d ; source pointer$9f6c
  .byte $11,$d1,$01,$e4,$b6,$d1,$20,$e3,$fd
  .word $a57d ; source pointer$9f77
  .byte $10,$00,$e4,$b0,$a0,$90,$80,$70,$60,$50,$d7,$10,$e4,$b0,$b0,$b0,$b0,$90,$a0,$b0,$e3,$20,$fd
  .word $a51c ; source pointer$9f90
  .byte $e3,$96,$96,$e4,$96,$e3,$96,$fd
  .word $a588 ; source pointer$9f9a
  .byte $b6,$d1,$20,$e3,$fd
  .word $a57d ; source pointer$9fa1
  .byte $10,$00,$e4,$b0,$a0,$90,$80,$70,$60,$50,$d1,$01,$fb,$e4,$46,$e2,$46,$fe,$02,$e4,$26,$e2,$26,$e4
  .byte $46,$e2,$46,$e3,$76,$66,$56,$4d,$d1,$01,$46,$76,$96,$d7,$13,$fb,$e4,$b0,$b0,$b0,$e3,$b0,$e4,$b0
  .byte $e3,$b0,$e4,$b0,$e3,$b1,$e4,$b0,$80,$e3,$80,$e4,$90,$e3,$90,$e4,$a0,$e3,$a0,$fe,$03,$e4,$b0,$e3
  .byte $60,$e4,$b0,$90,$e3,$40,$e4,$90,$60,$e3,$10,$e4,$60,$50,$e3,$00,$e4,$50,$40,$b0,$20,$90,$fe,$ff
  .word $a43f ; source pointer$a003
  .byte $d1,$01,$e4,$fb,$46,$fe,$05,$26,$46,$7d,$fb,$76,$fe,$07,$fb,$96,$fe,$05,$76,$96,$e3,$0d,$ff,$d1
  .byte $20,$e4,$49,$30,$20,$10,$00,$e5,$b0,$a0,$90,$80,$70,$61,$d1,$01,$e3,$fb,$46,$fe,$07,$e4,$b6,$b6
  .byte $86,$86,$46,$46,$d1,$20,$e4,$79,$60,$50,$40,$30,$20,$10,$00,$e5,$b0,$a0,$91,$d1,$01,$e3,$fb,$76
  .byte $fe,$07,$26,$26,$e4,$d1,$20,$e3,$79,$60,$50,$40,$30,$20,$10,$00,$e4,$b0,$a0,$90,$80,$70,$60,$50
  .byte $40,$30,$20,$10,$d1,$20,$e4,$99,$80,$70,$60,$50,$40,$30,$20,$10,$00,$e5,$b1,$d1,$01,$e4,$96,$ff
  .byte $b9,$a0,$90,$80,$70,$60,$50,$40,$30,$20,$ff,$d1,$20,$e3,$09,$e4,$b0,$a0,$90,$80,$70,$60,$50,$40
  .byte $30,$21,$d1,$01,$ff
TnMovedStreamEnd:
.assert TnMovedStreamBegin=$a429,lderror,"Page-aligned source stream"
.assert TnMovedStreamEnd=$a59a,lderror,"Complete connected source interval"
.segment "TMNT_NATIVE_AUDIO_A"
TnNativeSourceBegin:
  .assert *=$a612,lderror,"Original instruction offset 8612"
  LDA ::TnAudioRam+$99
  .assert *=$a615,lderror,"Original instruction offset 8615"
  .byte $f0,$2c ; BEQ source$8643
  .assert *=$a617,lderror,"Original instruction offset 8617"
  CMP #$01
  .assert *=$a619,lderror,"Original instruction offset 8619"
  .byte $d0,$03 ; BNE source$861e
  .assert *=$a61b,lderror,"Original instruction offset 861b"
  JMP $b016
  .assert *=$a61e,lderror,"Original instruction offset 861e"
  CMP #$02
  .assert *=$a620,lderror,"Original instruction offset 8620"
  .byte $d0,$0c ; BNE source$862e
  .assert *=$a622,lderror,"Original instruction offset 8622"
  LDA ::TnAudioRam+$98
  .assert *=$a625,lderror,"Original instruction offset 8625"
  CMP #$20
  .assert *=$a627,lderror,"Original instruction offset 8627"
  .byte $d0,$05 ; BNE source$862e
  .assert *=$a629,lderror,"Original instruction offset 8629"
  LDA #$00
  .assert *=$a62b,lderror,"Original instruction offset 862b"
  STA ::TnAudioRam+$0d
  .assert *=$a62e,lderror,"Original instruction offset 862e"
  INC ::TnAudioRam+$98
  .assert *=$a631,lderror,"Original instruction offset 8631"
  LDA #$2f
  .assert *=$a633,lderror,"Original instruction offset 8633"
  CMP ::TnAudioRam+$98
  .assert *=$a636,lderror,"Original instruction offset 8636"
  .byte $d0,$0b ; BNE source$8643
  .assert *=$a638,lderror,"Original instruction offset 8638"
  LDA #$00
  .assert *=$a63a,lderror,"Original instruction offset 863a"
  STA ::TnAudioRam+$98
  .assert *=$a63d,lderror,"Original instruction offset 863d"
  INC ::TnAudioRam+$97
  .assert *=$a640,lderror,"Original instruction offset 8640"
  DEC ::TnAudioRam+$99
  .assert *=$a643,lderror,"Original instruction offset 8643"
  RTS
  .assert *=$a644,lderror,"Original instruction offset 8644"
  JSR $a612
  .assert *=$a647,lderror,"Original instruction offset 8647"
  LDX #$00
  .assert *=$a649,lderror,"Original instruction offset 8649"
  LDY #$00
  .assert *=$a64b,lderror,"Original instruction offset 864b"
  STX ::TnAudioRam+$92
  .assert *=$a64e,lderror,"Original instruction offset 864e"
  STY ::TnAudioRam+$93
  .assert *=$a651,lderror,"Original instruction offset 8651"
  LDA ::TnAudioRam+$0a,x
  .assert *=$a654,lderror,"Original instruction offset 8654"
  .byte $f0,$03 ; BEQ source$8659
  .assert *=$a656,lderror,"Original instruction offset 8656"
  JSR $a671
  .assert *=$a659,lderror,"Original instruction offset 8659"
  INX
  .assert *=$a65a,lderror,"Original instruction offset 865a"
  CPX #$06
  .assert *=$a65c,lderror,"Original instruction offset 865c"
  .byte $f0,$12 ; BEQ source$8670
  .assert *=$a65e,lderror,"Original instruction offset 865e"
  CPX #$05
  .assert *=$a660,lderror,"Original instruction offset 8660"
  .byte $d0,$05 ; BNE source$8667
  .assert *=$a662,lderror,"Original instruction offset 8662"
  LDA #$0c
  .assert *=$a664,lderror,"Original instruction offset 8664"
  JMP $a66c
  .assert *=$a667,lderror,"Original instruction offset 8667"
  TXA
  .assert *=$a668,lderror,"Original instruction offset 8668"
  ASL A
  .assert *=$a669,lderror,"Original instruction offset 8669"
  ASL A
  .assert *=$a66a,lderror,"Original instruction offset 866a"
  AND #$0f
  .assert *=$a66c,lderror,"Original instruction offset 866c"
  TAY
  .assert *=$a66d,lderror,"Original instruction offset 866d"
  JMP $a64b
  .assert *=$a670,lderror,"Original instruction offset 8670"
  RTS
  .assert *=$a671,lderror,"Original instruction offset 8671"
  JSR $af96
  .assert *=$a674,lderror,"Original instruction offset 8674"
  LDA ::TnAudioRam+$16,x
  .assert *=$a677,lderror,"Original instruction offset 8677"
  DEC ::TnAudioRam+$04,x
  .assert *=$a67a,lderror,"Original instruction offset 867a"
  .byte $d0,$03 ; BNE source$867f
  .assert *=$a67c,lderror,"Original instruction offset 867c"
  JMP $a91f
  .assert *=$a67f,lderror,"Original instruction offset 867f"
  CPX #$02
  .assert *=$a681,lderror,"Original instruction offset 8681"
  .byte $b0,$ed ; BCS source$8670
  .assert *=$a683,lderror,"Original instruction offset 8683"
  AND #$41
  .assert *=$a685,lderror,"Original instruction offset 8685"
  .byte $d0,$e9 ; BNE source$8670
  .assert *=$a687,lderror,"Original instruction offset 8687"
  LDA ::TnAudioRam+$8e,x
  .assert *=$a68a,lderror,"Original instruction offset 868a"
  .byte $30,$24 ; BMI source$86b0
  .assert *=$a68c,lderror,"Original instruction offset 868c"
  LDA ::TnAudioRam+$10,x
  .assert *=$a68f,lderror,"Original instruction offset 868f"
  STA ::TnAudioZp+$02
  .assert *=$a691,lderror,"Original instruction offset 8691"
  LDA ::TnAudioRam+$8e,x
  .assert *=$a694,lderror,"Original instruction offset 8694"
  AND #$10
  .assert *=$a696,lderror,"Original instruction offset 8696"
  .byte $f0,$05 ; BEQ source$869d
  .assert *=$a698,lderror,"Original instruction offset 8698"
  LDA ::TnAudioZp+$02
  .assert *=$a69a,lderror,"Original instruction offset 869a"
  ASL A
  .assert *=$a69b,lderror,"Original instruction offset 869b"
  STA ::TnAudioZp+$02
  .assert *=$a69d,lderror,"Original instruction offset 869d"
  LDA ::TnAudioRam+$04,x
  .assert *=$a6a0,lderror,"Original instruction offset 86a0"
  SEC
  .assert *=$a6a1,lderror,"Original instruction offset 86a1"
  SBC ::TnAudioZp+$02
  .assert *=$a6a3,lderror,"Original instruction offset 86a3"
  .byte $f0,$3e ; BEQ source$86e3
  .assert *=$a6a5,lderror,"Original instruction offset 86a5"
  .byte $b0,$f9 ; BCS source$86a0
  .assert *=$a6a7,lderror,"Original instruction offset 86a7"
  LDA ::TnAudioRam+$16,x
  .assert *=$a6aa,lderror,"Original instruction offset 86aa"
  AND #$06
  .assert *=$a6ac,lderror,"Original instruction offset 86ac"
  CMP #$06
  .assert *=$a6ae,lderror,"Original instruction offset 86ae"
  .byte $f0,$15 ; BEQ source$86c5
  .assert *=$a6b0,lderror,"Original instruction offset 86b0"
  LDA ::TnAudioRam+$16,x
  .assert *=$a6b3,lderror,"Original instruction offset 86b3"
  AND #$10
  .assert *=$a6b5,lderror,"Original instruction offset 86b5"
  .byte $f0,$0e ; BEQ source$86c5
  .assert *=$a6b7,lderror,"Original instruction offset 86b7"
  DEC ::TnAudioRam+$80,x
  .assert *=$a6ba,lderror,"Original instruction offset 86ba"
  .byte $d0,$09 ; BNE source$86c5
  .assert *=$a6bc,lderror,"Original instruction offset 86bc"
  INC ::TnAudioRam+$80,x
  .assert *=$a6bf,lderror,"Original instruction offset 86bf"
  JSR $a857
  .assert *=$a6c2,lderror,"Original instruction offset 86c2"
  JSR $abda
  .assert *=$a6c5,lderror,"Original instruction offset 86c5"
  DEC ::TnAudioRam+$66,x
  .assert *=$a6c8,lderror,"Original instruction offset 86c8"
  .byte $d0,$a6 ; BNE source$8670
  .assert *=$a6ca,lderror,"Original instruction offset 86ca"
  INC ::TnAudioRam+$66,x
  .assert *=$a6cd,lderror,"Original instruction offset 86cd"
  JSR $a7b0
  .assert *=$a6d0,lderror,"Original instruction offset 86d0"
  LDA ::TnAudioRam+$16,x
  .assert *=$a6d3,lderror,"Original instruction offset 86d3"
  AND #$06
  .assert *=$a6d5,lderror,"Original instruction offset 86d5"
  TAY
  .assert *=$a6d6,lderror,"Original instruction offset 86d6"
  LDA $afb0,y
  .assert *=$a6d9,lderror,"Original instruction offset 86d9"
  STA ::TnAudioZp+$02
  .assert *=$a6db,lderror,"Original instruction offset 86db"
  LDA $afb1,y
  .assert *=$a6de,lderror,"Original instruction offset 86de"
  STA ::TnAudioZp+$03
  .assert *=$a6e0,lderror,"Original instruction offset 86e0"
  JMP (::TnAudioZp+$02)
  .assert *=$a6e3,lderror,"Original instruction offset 86e3"
  LDA ::TnAudioRam+$7a,x
  .assert *=$a6e6,lderror,"Original instruction offset 86e6"
  STA ::TnAudioZp+$0c
  .assert *=$a6e8,lderror,"Original instruction offset 86e8"
  LDA ::TnAudioRam+$7c,x
  .assert *=$a6eb,lderror,"Original instruction offset 86eb"
  STA ::TnAudioZp+$0d
  .assert *=$a6ed,lderror,"Original instruction offset 86ed"
  JSR $ac24
  .assert *=$a6f0,lderror,"Original instruction offset 86f0"
  JMP $a6a7
  .assert *=$a6f3,lderror,"Original instruction offset 86f3"
  LDA ::TnAudioRam+$64,x
  .assert *=$a6f6,lderror,"Original instruction offset 86f6"
  ASL A
  .assert *=$a6f7,lderror,"Original instruction offset 86f7"
  TAY
  .assert *=$a6f8,lderror,"Original instruction offset 86f8"
  LDA $deb0,y
  .assert *=$a6fb,lderror,"Original instruction offset 86fb"
  STA ::TnAudioZp+$02
  .assert *=$a6fd,lderror,"Original instruction offset 86fd"
  LDA $deb1,y
  .assert *=$a700,lderror,"Original instruction offset 8700"
  STA ::TnAudioZp+$03
  .assert *=$a702,lderror,"Original instruction offset 8702"
  LDA ::TnAudioRam+$68,x
  .assert *=$a705,lderror,"Original instruction offset 8705"
  TAY
  .assert *=$a706,lderror,"Original instruction offset 8706"
  LDA (::TnAudioZp+$02),y
  .assert *=$a708,lderror,"Original instruction offset 8708"
  CMP #$fb
  .assert *=$a70a,lderror,"Original instruction offset 870a"
  .byte $b0,$52 ; BCS source$875e
  .assert *=$a70c,lderror,"Original instruction offset 870c"
  CMP #$10
  .assert *=$a70e,lderror,"Original instruction offset 870e"
  .byte $90,$07 ; BCC source$8717
  .assert *=$a710,lderror,"Original instruction offset 8710"
  LSR A
  .assert *=$a711,lderror,"Original instruction offset 8711"
  LSR A
  .assert *=$a712,lderror,"Original instruction offset 8712"
  LSR A
  .assert *=$a713,lderror,"Original instruction offset 8713"
  LSR A
  .assert *=$a714,lderror,"Original instruction offset 8714"
  STA ::TnAudioRam+$66,x
  .assert *=$a717,lderror,"Original instruction offset 8717"
  INC ::TnAudioRam+$68,x
  .assert *=$a71a,lderror,"Original instruction offset 871a"
  LDA (::TnAudioZp+$02),y
  .assert *=$a71c,lderror,"Original instruction offset 871c"
  AND #$0f
  .assert *=$a71e,lderror,"Original instruction offset 871e"
  STA ::TnAudioRam+$4c,x
  .assert *=$a721,lderror,"Original instruction offset 8721"
  ORA ::TnAudioRam+$4c,x
  .assert *=$a724,lderror,"Original instruction offset 8724"
  .byte $f0,$10 ; BEQ source$8736
  .assert *=$a726,lderror,"Original instruction offset 8726"
  SEC
  .assert *=$a727,lderror,"Original instruction offset 8727"
  SBC ::TnAudioRam+$76,x
  .assert *=$a72a,lderror,"Original instruction offset 872a"
  .byte $90,$24 ; BCC source$8750
  .assert *=$a72c,lderror,"Original instruction offset 872c"
  .byte $f0,$22 ; BEQ source$8750
  .assert *=$a72e,lderror,"Original instruction offset 872e"
  SEC
  .assert *=$a72f,lderror,"Original instruction offset 872f"
  SBC ::TnAudioRam+$97
  .assert *=$a732,lderror,"Original instruction offset 8732"
  .byte $90,$1c ; BCC source$8750
  .assert *=$a734,lderror,"Original instruction offset 8734"
  .byte $f0,$1a ; BEQ source$8750
  .assert *=$a736,lderror,"Original instruction offset 8736"
  STA ::TnAudioZp+$02
  .assert *=$a738,lderror,"Original instruction offset 8738"
  LDA ::TnAudioRam+$16,x
  .assert *=$a73b,lderror,"Original instruction offset 873b"
  AND #$20
  .assert *=$a73d,lderror,"Original instruction offset 873d"
  .byte $d0,$15 ; BNE source$8754
  .assert *=$a73f,lderror,"Original instruction offset 873f"
  LDA ::TnAudioZp+$02
  .assert *=$a741,lderror,"Original instruction offset 8741"
  ORA ::TnAudioRam+$58,x
  .assert *=$a744,lderror,"Original instruction offset 8744"
  JSR $ace8
  .assert *=$a747,lderror,"Original instruction offset 8747"
  .byte $b0,$03 ; BCS source$874c
  .assert *=$a749,lderror,"Original instruction offset 8749"
  .if ::TN_RAW_APU
  STA $4000,x
.else
  jsr ::TnSourceSTA00X
.endif
  .assert *=$a74c,lderror,"Original instruction offset 874c"
  LDX ::TnAudioRam+$92
  .assert *=$a74f,lderror,"Original instruction offset 874f"
  RTS
  .assert *=$a750,lderror,"Original instruction offset 8750"
  LDA #$01
  .assert *=$a752,lderror,"Original instruction offset 8752"
  .byte $d0,$e2 ; BNE source$8736
  .assert *=$a754,lderror,"Original instruction offset 8754"
  LDA ::TnAudioRam+$8c,x
  .assert *=$a757,lderror,"Original instruction offset 8757"
  AND #$f0
  .assert *=$a759,lderror,"Original instruction offset 8759"
  ORA ::TnAudioZp+$02
  .assert *=$a75b,lderror,"Original instruction offset 875b"
  JMP $a744
  .assert *=$a75e,lderror,"Original instruction offset 875e"
  CMP #$fe
  .assert *=$a760,lderror,"Original instruction offset 8760"
  .byte $f0,$0e ; BEQ source$8770
  .assert *=$a762,lderror,"Original instruction offset 8762"
  .byte $b0,$7f ; BCS source$87e3
  .assert *=$a764,lderror,"Original instruction offset 8764"
  INC ::TnAudioRam+$68,x
  .assert *=$a767,lderror,"Original instruction offset 8767"
  LDA ::TnAudioRam+$68,x
  .assert *=$a76a,lderror,"Original instruction offset 876a"
  STA ::TnAudioRam+$6c,x
  .assert *=$a76d,lderror,"Original instruction offset 876d"
  JMP $a702
  .assert *=$a770,lderror,"Original instruction offset 8770"
  INY
  .assert *=$a771,lderror,"Original instruction offset 8771"
  INC ::TnAudioRam+$6a,x
  .assert *=$a774,lderror,"Original instruction offset 8774"
  LDA (::TnAudioZp+$02),y
  .assert *=$a776,lderror,"Original instruction offset 8776"
  CMP ::TnAudioRam+$6a,x
  .assert *=$a779,lderror,"Original instruction offset 8779"
  .byte $d0,$11 ; BNE source$878c
  .assert *=$a77b,lderror,"Original instruction offset 877b"
  LDA #$00
  .assert *=$a77d,lderror,"Original instruction offset 877d"
  STA ::TnAudioRam+$6a,x
  .assert *=$a780,lderror,"Original instruction offset 8780"
  STA ::TnAudioRam+$6c,x
  .assert *=$a783,lderror,"Original instruction offset 8783"
  INC ::TnAudioRam+$68,x
  .assert *=$a786,lderror,"Original instruction offset 8786"
  INC ::TnAudioRam+$68,x
  .assert *=$a789,lderror,"Original instruction offset 8789"
  JMP $a702
  .assert *=$a78c,lderror,"Original instruction offset 878c"
  LDA ::TnAudioRam+$6c,x
  .assert *=$a78f,lderror,"Original instruction offset 878f"
  STA ::TnAudioRam+$68,x
  .assert *=$a792,lderror,"Original instruction offset 8792"
  JMP $a702
  .assert *=$a795,lderror,"Original instruction offset 8795"
  DEC ::TnAudioRam+$68,x
  .assert *=$a798,lderror,"Original instruction offset 8798"
  .byte $30,$49 ; BMI source$87e3
  .assert *=$a79a,lderror,"Original instruction offset 879a"
  DEC ::TnAudioRam+$4c,x
  .assert *=$a79d,lderror,"Original instruction offset 879d"
  .byte $30,$06 ; BMI source$87a5
  .assert *=$a79f,lderror,"Original instruction offset 879f"
  LDA ::TnAudioRam+$4c,x
  .assert *=$a7a2,lderror,"Original instruction offset 87a2"
  JMP $a71e
  .assert *=$a7a5,lderror,"Original instruction offset 87a5"
  INC ::TnAudioRam+$4c,x
  .assert *=$a7a8,lderror,"Original instruction offset 87a8"
  RTS
  .assert *=$a7a9,lderror,"Original instruction offset 87a9"
  LDA ::TnAudioRam+$16,x
  .assert *=$a7ac,lderror,"Original instruction offset 87ac"
  AND #$02
  .assert *=$a7ae,lderror,"Original instruction offset 87ae"
  .byte $d0,$4a ; BNE source$87fa
  .assert *=$a7b0,lderror,"Original instruction offset 87b0"
  LDA ::TnAudioRam+$16,x
  .assert *=$a7b3,lderror,"Original instruction offset 87b3"
  AND #$06
  .assert *=$a7b5,lderror,"Original instruction offset 87b5"
  CMP #$06
  .assert *=$a7b7,lderror,"Original instruction offset 87b7"
  .byte $f0,$34 ; BEQ source$87ed
  .assert *=$a7b9,lderror,"Original instruction offset 87b9"
  LDA ::TnAudioRam+$04,x
  .assert *=$a7bc,lderror,"Original instruction offset 87bc"
  CMP ::TnAudioRam+$6e,x
  .assert *=$a7bf,lderror,"Original instruction offset 87bf"
  .byte $b0,$2c ; BCS source$87ed
  .assert *=$a7c1,lderror,"Original instruction offset 87c1"
  LDA ::TnAudioRam+$16,x
  .assert *=$a7c4,lderror,"Original instruction offset 87c4"
  ORA #$06
  .assert *=$a7c6,lderror,"Original instruction offset 87c6"
  STA ::TnAudioRam+$16,x
  .assert *=$a7c9,lderror,"Original instruction offset 87c9"
  LDA ::TnAudioRam+$8c,x
  .assert *=$a7cc,lderror,"Original instruction offset 87cc"
  AND #$0c
  .assert *=$a7ce,lderror,"Original instruction offset 87ce"
  .byte $d0,$1e ; BNE source$87ee
  .assert *=$a7d0,lderror,"Original instruction offset 87d0"
  JMP $a7d3
  .assert *=$a7d3,lderror,"Original instruction offset 87d3"
  LDA ::TnAudioRam+$8c,x
  .assert *=$a7d6,lderror,"Original instruction offset 87d6"
  AND #$02
  .assert *=$a7d8,lderror,"Original instruction offset 87d8"
  .byte $f0,$08 ; BEQ source$87e2
  .assert *=$a7da,lderror,"Original instruction offset 87da"
  LDA ::TnAudioRam+$16,x
  .assert *=$a7dd,lderror,"Original instruction offset 87dd"
  ORA #$20
  .assert *=$a7df,lderror,"Original instruction offset 87df"
  STA ::TnAudioRam+$16,x
  .assert *=$a7e2,lderror,"Original instruction offset 87e2"
  RTS
  .assert *=$a7e3,lderror,"Original instruction offset 87e3"
  LDA ::TnAudioRam+$16,x
  .assert *=$a7e6,lderror,"Original instruction offset 87e6"
  ORA #$04
  .assert *=$a7e8,lderror,"Original instruction offset 87e8"
  AND #$fd
  .assert *=$a7ea,lderror,"Original instruction offset 87ea"
  STA ::TnAudioRam+$16,x
  .assert *=$a7ed,lderror,"Original instruction offset 87ed"
  RTS
  .assert *=$a7ee,lderror,"Original instruction offset 87ee"
  LSR A
  .assert *=$a7ef,lderror,"Original instruction offset 87ef"
  LSR A
  .assert *=$a7f0,lderror,"Original instruction offset 87f0"
  STA ::TnAudioZp+$02
  .assert *=$a7f2,lderror,"Original instruction offset 87f2"
  JSR $a7d3
  .assert *=$a7f5,lderror,"Original instruction offset 87f5"
  LDA ::TnAudioZp+$02
  .assert *=$a7f7,lderror,"Original instruction offset 87f7"
  JMP $a71e
  .assert *=$a7fa,lderror,"Original instruction offset 87fa"
  LDA ::TnAudioRam+$8e,x
  .assert *=$a7fd,lderror,"Original instruction offset 87fd"
  .byte $30,$2a ; BMI source$8829
  .assert *=$a7ff,lderror,"Original instruction offset 87ff"
  STY ::TnAudioZp+$02
  .assert *=$a801,lderror,"Original instruction offset 8801"
  LDA ::TnAudioRam+$8e,x
  .assert *=$a804,lderror,"Original instruction offset 8804"
  AND #$0f
  .assert *=$a806,lderror,"Original instruction offset 8806"
  STA ::TnAudioZp+$04
  .assert *=$a808,lderror,"Original instruction offset 8808"
  LDA ::TnAudioRam+$90,x
  .assert *=$a80b,lderror,"Original instruction offset 880b"
  SEC
  .assert *=$a80c,lderror,"Original instruction offset 880c"
  SBC #$01
  .assert *=$a80e,lderror,"Original instruction offset 880e"
  AND #$03
  .assert *=$a810,lderror,"Original instruction offset 8810"
  SEC
  .assert *=$a811,lderror,"Original instruction offset 8811"
  SBC ::TnAudioZp+$04
  .assert *=$a813,lderror,"Original instruction offset 8813"
  AND #$03
  .assert *=$a815,lderror,"Original instruction offset 8815"
  CPX #$01
  .assert *=$a817,lderror,"Original instruction offset 8817"
  .byte $d0,$02 ; BNE source$881b
  .assert *=$a819,lderror,"Original instruction offset 8819"
  ORA #$04
  .assert *=$a81b,lderror,"Original instruction offset 881b"
  TAY
  .assert *=$a81c,lderror,"Original instruction offset 881c"
  LDA ::TnAudioRam+$9e,y
  .assert *=$a81f,lderror,"Original instruction offset 881f"
  STA ::TnAudioZp+$0c
  .assert *=$a821,lderror,"Original instruction offset 8821"
  LDA ::TnAudioRam+$a6,y
  .assert *=$a824,lderror,"Original instruction offset 8824"
  STA ::TnAudioZp+$0d
  .assert *=$a826,lderror,"Original instruction offset 8826"
  JSR $abea
  .assert *=$a829,lderror,"Original instruction offset 8829"
  LDA ::TnAudioRam+$8c,x
  .assert *=$a82c,lderror,"Original instruction offset 882c"
  AND #$0c
  .assert *=$a82e,lderror,"Original instruction offset 882e"
  .byte $d0,$bd ; BNE source$87ed
  .assert *=$a830,lderror,"Original instruction offset 8830"
  DEC ::TnAudioRam+$74,x
  .assert *=$a833,lderror,"Original instruction offset 8833"
  .byte $d0,$b8 ; BNE source$87ed
  .assert *=$a835,lderror,"Original instruction offset 8835"
  LDA ::TnAudioRam+$72,x
  .assert *=$a838,lderror,"Original instruction offset 8838"
  .byte $d0,$02 ; BNE source$883c
  .assert *=$a83a,lderror,"Original instruction offset 883a"
  LDA #$01
  .assert *=$a83c,lderror,"Original instruction offset 883c"
  STA ::TnAudioRam+$74,x
  .assert *=$a83f,lderror,"Original instruction offset 883f"
  DEC ::TnAudioRam+$4c,x
  .assert *=$a842,lderror,"Original instruction offset 8842"
  .byte $30,$0f ; BMI source$8853
  .assert *=$a844,lderror,"Original instruction offset 8844"
  LDA #$01
  .assert *=$a846,lderror,"Original instruction offset 8846"
  CMP ::TnAudioRam+$4c,x
  .assert *=$a849,lderror,"Original instruction offset 8849"
  .byte $f0,$02 ; BEQ source$884d
  .assert *=$a84b,lderror,"Original instruction offset 884b"
  .byte $b0,$06 ; BCS source$8853
  .assert *=$a84d,lderror,"Original instruction offset 884d"
  LDA ::TnAudioRam+$4c,x
  .assert *=$a850,lderror,"Original instruction offset 8850"
  JMP $a721
  .assert *=$a853,lderror,"Original instruction offset 8853"
  INC ::TnAudioRam+$4c,x
  .assert *=$a856,lderror,"Original instruction offset 8856"
  RTS
  .assert *=$a857,lderror,"Original instruction offset 8857"
  LDA ::TnAudioRam+$84,x
  .assert *=$a85a,lderror,"Original instruction offset 885a"
  ASL A
  .assert *=$a85b,lderror,"Original instruction offset 885b"
  TAY
  .assert *=$a85c,lderror,"Original instruction offset 885c"
  LDA $dee2,y
  .assert *=$a85f,lderror,"Original instruction offset 885f"
  STA ::TnAudioZp+$02
  .assert *=$a861,lderror,"Original instruction offset 8861"
  LDA $dee3,y
  .assert *=$a864,lderror,"Original instruction offset 8864"
  STA ::TnAudioZp+$03
  .assert *=$a866,lderror,"Original instruction offset 8866"
  LDA ::TnAudioRam+$86,x
  .assert *=$a869,lderror,"Original instruction offset 8869"
  TAY
  .assert *=$a86a,lderror,"Original instruction offset 886a"
  LDA (::TnAudioZp+$02),y
  .assert *=$a86c,lderror,"Original instruction offset 886c"
  CMP #$fb
  .assert *=$a86e,lderror,"Original instruction offset 886e"
  .byte $b0,$72 ; BCS source$88e2
  .assert *=$a870,lderror,"Original instruction offset 8870"
  CMP #$10
  .assert *=$a872,lderror,"Original instruction offset 8872"
  .byte $90,$07 ; BCC source$887b
  .assert *=$a874,lderror,"Original instruction offset 8874"
  LSR A
  .assert *=$a875,lderror,"Original instruction offset 8875"
  LSR A
  .assert *=$a876,lderror,"Original instruction offset 8876"
  LSR A
  .assert *=$a877,lderror,"Original instruction offset 8877"
  LSR A
  .assert *=$a878,lderror,"Original instruction offset 8878"
  STA ::TnAudioRam+$80,x
  .assert *=$a87b,lderror,"Original instruction offset 887b"
  INC ::TnAudioRam+$86,x
  .assert *=$a87e,lderror,"Original instruction offset 887e"
  LDA (::TnAudioZp+$02),y
  .assert *=$a880,lderror,"Original instruction offset 8880"
  AND #$0f
  .assert *=$a882,lderror,"Original instruction offset 8882"
  STA ::TnAudioZp+$02
  .assert *=$a884,lderror,"Original instruction offset 8884"
  CMP #$08
  .assert *=$a886,lderror,"Original instruction offset 8886"
  .byte $b0,$07 ; BCS source$888f
  .assert *=$a888,lderror,"Original instruction offset 8888"
  JSR $a89d
  .assert *=$a88b,lderror,"Original instruction offset 888b"
  JSR $a8b2
  .assert *=$a88e,lderror,"Original instruction offset 888e"
  RTS
  .assert *=$a88f,lderror,"Original instruction offset 888f"
  LDA #$10
  .assert *=$a891,lderror,"Original instruction offset 8891"
  SEC
  .assert *=$a892,lderror,"Original instruction offset 8892"
  SBC ::TnAudioZp+$02
  .assert *=$a894,lderror,"Original instruction offset 8894"
  STA ::TnAudioZp+$02
  .assert *=$a896,lderror,"Original instruction offset 8896"
  JSR $a89d
  .assert *=$a899,lderror,"Original instruction offset 8899"
  JSR $a8c8
  .assert *=$a89c,lderror,"Original instruction offset 889c"
  RTS
  .assert *=$a89d,lderror,"Original instruction offset 889d"
  LDA ::TnAudioRam+$82,x
  .assert *=$a8a0,lderror,"Original instruction offset 88a0"
  TAX
  .assert *=$a8a1,lderror,"Original instruction offset 88a1"
  LDA ::TnAudioZp+$02
  .assert *=$a8a3,lderror,"Original instruction offset 88a3"
  DEX
  .assert *=$a8a4,lderror,"Original instruction offset 88a4"
  .byte $f0,$06 ; BEQ source$88ac
  .assert *=$a8a6,lderror,"Original instruction offset 88a6"
  CLC
  .assert *=$a8a7,lderror,"Original instruction offset 88a7"
  ADC ::TnAudioZp+$02
  .assert *=$a8a9,lderror,"Original instruction offset 88a9"
  JMP $a8a3
  .assert *=$a8ac,lderror,"Original instruction offset 88ac"
  LDX ::TnAudioRam+$92
  .assert *=$a8af,lderror,"Original instruction offset 88af"
  STA ::TnAudioZp+$02
  .assert *=$a8b1,lderror,"Original instruction offset 88b1"
  RTS
  .assert *=$a8b2,lderror,"Original instruction offset 88b2"
  CLC
  .assert *=$a8b3,lderror,"Original instruction offset 88b3"
  ADC ::TnAudioRam+$7a,x
  .assert *=$a8b6,lderror,"Original instruction offset 88b6"
  STA ::TnAudioZp+$0c
  .assert *=$a8b8,lderror,"Original instruction offset 88b8"
  .byte $90,$08 ; BCC source$88c2
  .assert *=$a8ba,lderror,"Original instruction offset 88ba"
  LDA ::TnAudioRam+$7c,x
  .assert *=$a8bd,lderror,"Original instruction offset 88bd"
  STA ::TnAudioZp+$0d
  .assert *=$a8bf,lderror,"Original instruction offset 88bf"
  INC ::TnAudioZp+$0d
  .assert *=$a8c1,lderror,"Original instruction offset 88c1"
  RTS
  .assert *=$a8c2,lderror,"Original instruction offset 88c2"
  LDA ::TnAudioRam+$7c,x
  .assert *=$a8c5,lderror,"Original instruction offset 88c5"
  STA ::TnAudioZp+$0d
  .assert *=$a8c7,lderror,"Original instruction offset 88c7"
  RTS
  .assert *=$a8c8,lderror,"Original instruction offset 88c8"
  LDA ::TnAudioRam+$7a,x
  .assert *=$a8cb,lderror,"Original instruction offset 88cb"
  SEC
  .assert *=$a8cc,lderror,"Original instruction offset 88cc"
  SBC ::TnAudioZp+$02
  .assert *=$a8ce,lderror,"Original instruction offset 88ce"
  .byte $b0,$0a ; BCS source$88da
  .assert *=$a8d0,lderror,"Original instruction offset 88d0"
  STA ::TnAudioZp+$0c
  .assert *=$a8d2,lderror,"Original instruction offset 88d2"
  LDA ::TnAudioRam+$7c,x
  .assert *=$a8d5,lderror,"Original instruction offset 88d5"
  STA ::TnAudioZp+$0d
  .assert *=$a8d7,lderror,"Original instruction offset 88d7"
  DEC ::TnAudioZp+$0d
  .assert *=$a8d9,lderror,"Original instruction offset 88d9"
  RTS
  .assert *=$a8da,lderror,"Original instruction offset 88da"
  STA ::TnAudioZp+$0c
  .assert *=$a8dc,lderror,"Original instruction offset 88dc"
  LDA ::TnAudioRam+$7c,x
  .assert *=$a8df,lderror,"Original instruction offset 88df"
  STA ::TnAudioZp+$0d
  .assert *=$a8e1,lderror,"Original instruction offset 88e1"
  RTS
  .assert *=$a8e2,lderror,"Original instruction offset 88e2"
  CMP #$fe
  .assert *=$a8e4,lderror,"Original instruction offset 88e4"
  .byte $f0,$0e ; BEQ source$88f4
  .assert *=$a8e6,lderror,"Original instruction offset 88e6"
  .byte $b0,$31 ; BCS source$8919
  .assert *=$a8e8,lderror,"Original instruction offset 88e8"
  INC ::TnAudioRam+$86,x
  .assert *=$a8eb,lderror,"Original instruction offset 88eb"
  LDA ::TnAudioRam+$86,x
  .assert *=$a8ee,lderror,"Original instruction offset 88ee"
  STA ::TnAudioRam+$88,x
  .assert *=$a8f1,lderror,"Original instruction offset 88f1"
  JMP $a857
  .assert *=$a8f4,lderror,"Original instruction offset 88f4"
  INY
  .assert *=$a8f5,lderror,"Original instruction offset 88f5"
  INC ::TnAudioRam+$8a,x
  .assert *=$a8f8,lderror,"Original instruction offset 88f8"
  LDA (::TnAudioZp+$02),y
  .assert *=$a8fa,lderror,"Original instruction offset 88fa"
  CMP ::TnAudioRam+$8a,x
  .assert *=$a8fd,lderror,"Original instruction offset 88fd"
  .byte $d0,$11 ; BNE source$8910
  .assert *=$a8ff,lderror,"Original instruction offset 88ff"
  LDA #$00
  .assert *=$a901,lderror,"Original instruction offset 8901"
  STA ::TnAudioRam+$8a,x
  .assert *=$a904,lderror,"Original instruction offset 8904"
  STA ::TnAudioRam+$88,x
  .assert *=$a907,lderror,"Original instruction offset 8907"
  INC ::TnAudioRam+$86,x
  .assert *=$a90a,lderror,"Original instruction offset 890a"
  INC ::TnAudioRam+$86,x
  .assert *=$a90d,lderror,"Original instruction offset 890d"
  JMP $a857
  .assert *=$a910,lderror,"Original instruction offset 8910"
  LDA ::TnAudioRam+$88,x
  .assert *=$a913,lderror,"Original instruction offset 8913"
  STA ::TnAudioRam+$86,x
  .assert *=$a916,lderror,"Original instruction offset 8916"
  JMP $a857
  .assert *=$a919,lderror,"Original instruction offset 8919"
  LDA #$ff
  .assert *=$a91b,lderror,"Original instruction offset 891b"
  STA ::TnAudioRam+$80,x
  .assert *=$a91e,lderror,"Original instruction offset 891e"
  RTS
  .assert *=$a91f,lderror,"Original instruction offset 891f"
  LSR A
  .assert *=$a920,lderror,"Original instruction offset 8920"
  .byte $90,$03 ; BCC source$8925
  .assert *=$a922,lderror,"Original instruction offset 8922"
  JMP $a9cd
  .assert *=$a925,lderror,"Original instruction offset 8925"
  LDA ::TnAudioRam+$92
  .assert *=$a928,lderror,"Original instruction offset 8928"
  CMP #$03
  .assert *=$a92a,lderror,"Original instruction offset 892a"
  .byte $f0,$25 ; BEQ source$8951
  .assert *=$a92c,lderror,"Original instruction offset 892c"
  LDA (::TnAudioZp+$00),y
  .assert *=$a92e,lderror,"Original instruction offset 892e"
  AND #$f0
  .assert *=$a930,lderror,"Original instruction offset 8930"
  CMP #$c0
  .assert *=$a932,lderror,"Original instruction offset 8932"
  .byte $b0,$03 ; BCS source$8937
  .assert *=$a934,lderror,"Original instruction offset 8934"
  JMP $ab3e
  .assert *=$a937,lderror,"Original instruction offset 8937"
  AND #$30
  .assert *=$a939,lderror,"Original instruction offset 8939"
  LSR A
  .assert *=$a93a,lderror,"Original instruction offset 893a"
  LSR A
  .assert *=$a93b,lderror,"Original instruction offset 893b"
  LSR A
  .assert *=$a93c,lderror,"Original instruction offset 893c"
  TAX
  .assert *=$a93d,lderror,"Original instruction offset 893d"
  LDA $afc4,x
  .assert *=$a940,lderror,"Original instruction offset 8940"
  STA ::TnAudioZp+$02
  .assert *=$a942,lderror,"Original instruction offset 8942"
  LDA $afc5,x
  .assert *=$a945,lderror,"Original instruction offset 8945"
  STA ::TnAudioZp+$03
  .assert *=$a947,lderror,"Original instruction offset 8947"
  LDX ::TnAudioRam+$92
  .assert *=$a94a,lderror,"Original instruction offset 894a"
  LDA (::TnAudioZp+$00),y
  .assert *=$a94c,lderror,"Original instruction offset 894c"
  AND #$0f
  .assert *=$a94e,lderror,"Original instruction offset 894e"
  JMP (::TnAudioZp+$02)
  .assert *=$a951,lderror,"Original instruction offset 8951"
  LDA (::TnAudioZp+$00),y
  .assert *=$a953,lderror,"Original instruction offset 8953"
  AND #$f0
  .assert *=$a955,lderror,"Original instruction offset 8955"
  CMP #$f0
  .assert *=$a957,lderror,"Original instruction offset 8957"
  .byte $d0,$07 ; BNE source$8960
  .assert *=$a959,lderror,"Original instruction offset 8959"
  LDA (::TnAudioZp+$00),y
  .assert *=$a95b,lderror,"Original instruction offset 895b"
  AND #$0f
  .assert *=$a95d,lderror,"Original instruction offset 895d"
  JMP $ae66
  .assert *=$a960,lderror,"Original instruction offset 8960"
  CMP #$d0
  .assert *=$a962,lderror,"Original instruction offset 8962"
  .byte $f0,$03 ; BEQ source$8967
  .assert *=$a964,lderror,"Original instruction offset 8964"
  JMP $ac71
  .assert *=$a967,lderror,"Original instruction offset 8967"
  LDA (::TnAudioZp+$00),y
  .assert *=$a969,lderror,"Original instruction offset 8969"
  AND #$0f
  .assert *=$a96b,lderror,"Original instruction offset 896b"
  STA ::TnAudioRam+$10,x
  .assert *=$a96e,lderror,"Original instruction offset 896e"
  INY
  .assert *=$a96f,lderror,"Original instruction offset 896f"
  JMP $a951
  .assert *=$a972,lderror,"Original instruction offset 8972"
  LDA (::TnAudioZp+$00),y
  .assert *=$a974,lderror,"Original instruction offset 8974"
  LSR A
  .assert *=$a975,lderror,"Original instruction offset 8975"
  LSR A
  .assert *=$a976,lderror,"Original instruction offset 8976"
  LSR A
  .assert *=$a977,lderror,"Original instruction offset 8977"
  LSR A
  .assert *=$a978,lderror,"Original instruction offset 8978"
  CMP #$0c
  .assert *=$a97a,lderror,"Original instruction offset 897a"
  .byte $d0,$01 ; BNE source$897d
  .assert *=$a97c,lderror,"Original instruction offset 897c"
  RTS
  .assert *=$a97d,lderror,"Original instruction offset 897d"
  TAX
  .assert *=$a97e,lderror,"Original instruction offset 897e"
  STA ::TnAudioRam+$95
  .assert *=$a981,lderror,"Original instruction offset 8981"
  LDA $a9c1,x
  .assert *=$a984,lderror,"Original instruction offset 8984"
  LDX ::TnAudioRam+$92
  .assert *=$a987,lderror,"Original instruction offset 8987"
  CMP #$8f
  .assert *=$a989,lderror,"Original instruction offset 8989"
  .byte $b0,$03 ; BCS source$898e
  .assert *=$a98b,lderror,"Original instruction offset 898b"
  JMP $b057
  .assert *=$a98e,lderror,"Original instruction offset 898e"
  SEC
  .assert *=$a98f,lderror,"Original instruction offset 898f"
  SBC #$8f
  .assert *=$a991,lderror,"Original instruction offset 8991"
  STA ::TnAudioRam+$94
  .assert *=$a994,lderror,"Original instruction offset 8994"
  TYA
  .assert *=$a995,lderror,"Original instruction offset 8995"
  PHA
  .assert *=$a996,lderror,"Original instruction offset 8996"
  LDA ::TnAudioRam+$94
  .assert *=$a999,lderror,"Original instruction offset 8999"
  ASL A
  .assert *=$a99a,lderror,"Original instruction offset 899a"
  ASL A
  .assert *=$a99b,lderror,"Original instruction offset 899b"
  TAY
  .assert *=$a99c,lderror,"Original instruction offset 899c"
  LDA #$0f
  .assert *=$a99e,lderror,"Original instruction offset 899e"
  .if ::TN_RAW_APU
  STA $4015
.else
  jsr ::TnSourceSTA15
.endif
  .assert *=$a9a1,lderror,"Original instruction offset 89a1"
  LDA $a028,y
  .assert *=$a9a4,lderror,"Original instruction offset 89a4"
  .if ::TN_RAW_APU
  STA $4010
.else
  jsr ::TnSourceSTA10
.endif
  .assert *=$a9a7,lderror,"Original instruction offset 89a7"
  LDA $a029,y
  .assert *=$a9aa,lderror,"Original instruction offset 89aa"
  .if ::TN_RAW_APU
  STA $4011
.else
  jsr ::TnSourceSTA11
.endif
  .assert *=$a9ad,lderror,"Original instruction offset 89ad"
  LDA $a02a,y
  .assert *=$a9b0,lderror,"Original instruction offset 89b0"
  .if ::TN_RAW_APU
  STA $4012
.else
  jsr ::TnSourceSTA12
.endif
  .assert *=$a9b3,lderror,"Original instruction offset 89b3"
  LDA $a02b,y
  .assert *=$a9b6,lderror,"Original instruction offset 89b6"
  .if ::TN_RAW_APU
  STA $4013
.else
  jsr ::TnSourceSTA13
.endif
  .assert *=$a9b9,lderror,"Original instruction offset 89b9"
  LDA #$1f
  .assert *=$a9bb,lderror,"Original instruction offset 89bb"
  .if ::TN_RAW_APU
  STA $4015
.else
  jsr ::TnSourceSTA15
.endif
  .assert *=$a9be,lderror,"Original instruction offset 89be"
  PLA
  .assert *=$a9bf,lderror,"Original instruction offset 89bf"
  TAY
  .assert *=$a9c0,lderror,"Original instruction offset 89c0"
  RTS
  .byte $02,$03,$04,$05,$06,$02,$02,$02,$02,$02,$02,$8f
  .assert *=$a9cd,lderror,"Original instruction offset 89cd"
  LDA (::TnAudioZp+$00),y
  .assert *=$a9cf,lderror,"Original instruction offset 89cf"
  CPX #$05
  .assert *=$a9d1,lderror,"Original instruction offset 89d1"
  .byte $f0,$00 ; BEQ source$89d3
  .assert *=$a9d3,lderror,"Original instruction offset 89d3"
  CMP #$fb
  .assert *=$a9d5,lderror,"Original instruction offset 89d5"
  .byte $90,$05 ; BCC source$89dc
  .assert *=$a9d7,lderror,"Original instruction offset 89d7"
  AND #$0f
  .assert *=$a9d9,lderror,"Original instruction offset 89d9"
  JMP $ae66
  .assert *=$a9dc,lderror,"Original instruction offset 89dc"
  CPX #$05
  .assert *=$a9de,lderror,"Original instruction offset 89de"
  .byte $f0,$26 ; BEQ source$8a06
  .assert *=$a9e0,lderror,"Original instruction offset 89e0"
  CMP #$f8
  .assert *=$a9e2,lderror,"Original instruction offset 89e2"
  .byte $90,$22 ; BCC source$8a06
  .assert *=$a9e4,lderror,"Original instruction offset 89e4"
  AND #$0f
  .assert *=$a9e6,lderror,"Original instruction offset 89e6"
  CMP #$09
  .assert *=$a9e8,lderror,"Original instruction offset 89e8"
  .byte $f0,$12 ; BEQ source$89fc
  .assert *=$a9ea,lderror,"Original instruction offset 89ea"
  .byte $90,$06 ; BCC source$89f2
  .assert *=$a9ec,lderror,"Original instruction offset 89ec"
  INY
  .assert *=$a9ed,lderror,"Original instruction offset 89ed"
  LDA (::TnAudioZp+$00),y
  .assert *=$a9ef,lderror,"Original instruction offset 89ef"
  JMP $aa3f
  .assert *=$a9f2,lderror,"Original instruction offset 89f2"
  INY
  .assert *=$a9f3,lderror,"Original instruction offset 89f3"
  LDA (::TnAudioZp+$00),y
  .assert *=$a9f5,lderror,"Original instruction offset 89f5"
  STA ::TnAudioRam+$10,x
  .assert *=$a9f8,lderror,"Original instruction offset 89f8"
  INY
  .assert *=$a9f9,lderror,"Original instruction offset 89f9"
  JMP $a9cd
  .assert *=$a9fc,lderror,"Original instruction offset 89fc"
  INY
  .assert *=$a9fd,lderror,"Original instruction offset 89fd"
  LDA (::TnAudioZp+$00),y
  .assert *=$a9ff,lderror,"Original instruction offset 89ff"
  STA ::TnAudioRam+$58,x
  .assert *=$aa02,lderror,"Original instruction offset 8a02"
  INY
  .assert *=$aa03,lderror,"Original instruction offset 8a03"
  JMP $a9cd
  .assert *=$aa06,lderror,"Original instruction offset 8a06"
  AND #$f0
  .assert *=$aa08,lderror,"Original instruction offset 8a08"
  CMP #$00
  .assert *=$aa0a,lderror,"Original instruction offset 8a0a"
  .byte $d0,$65 ; BNE source$8a71
  .assert *=$aa0c,lderror,"Original instruction offset 8a0c"
  LDA (::TnAudioZp+$00),y
  .assert *=$aa0e,lderror,"Original instruction offset 8a0e"
  AND #$0f
  .assert *=$aa10,lderror,"Original instruction offset 8a10"
  .byte $d0,$03 ; BNE source$8a15
  .assert *=$aa12,lderror,"Original instruction offset 8a12"
  JMP $aa71
  .assert *=$aa15,lderror,"Original instruction offset 8a15"
  STA ::TnAudioRam+$10,x
  .assert *=$aa18,lderror,"Original instruction offset 8a18"
  INY
  .assert *=$aa19,lderror,"Original instruction offset 8a19"
  LDA (::TnAudioZp+$00),y
  .assert *=$aa1b,lderror,"Original instruction offset 8a1b"
  CPX #$02
  .assert *=$aa1d,lderror,"Original instruction offset 8a1d"
  .byte $f0,$43 ; BEQ source$8a62
  .assert *=$aa1f,lderror,"Original instruction offset 8a1f"
  CPX #$05
  .assert *=$aa21,lderror,"Original instruction offset 8a21"
  .byte $d0,$08 ; BNE source$8a2b
  .assert *=$aa23,lderror,"Original instruction offset 8a23"
  LDA #$30
  .assert *=$aa25,lderror,"Original instruction offset 8a25"
  STA ::TnAudioRam+$58,x
  .assert *=$aa28,lderror,"Original instruction offset 8a28"
  JMP $aa69
  .assert *=$aa2b,lderror,"Original instruction offset 8a2b"
  STA ::TnAudioRam+$58,x
  .assert *=$aa2e,lderror,"Original instruction offset 8a2e"
  INY
  .assert *=$aa2f,lderror,"Original instruction offset 8a2f"
  LDA (::TnAudioZp+$00),y
  .assert *=$aa31,lderror,"Original instruction offset 8a31"
  CMP #$88
  .assert *=$aa33,lderror,"Original instruction offset 8a33"
  .byte $f0,$20 ; BEQ source$8a55
  .assert *=$aa35,lderror,"Original instruction offset 8a35"
  LDA ::TnAudioRam+$16,x
  .assert *=$aa38,lderror,"Original instruction offset 8a38"
  ORA #$80
  .assert *=$aa3a,lderror,"Original instruction offset 8a3a"
  STA ::TnAudioRam+$16,x
  .assert *=$aa3d,lderror,"Original instruction offset 8a3d"
  LDA (::TnAudioZp+$00),y
  .assert *=$aa3f,lderror,"Original instruction offset 8a3f"
  CPX #$04
  .assert *=$aa41,lderror,"Original instruction offset 8a41"
  .byte $d0,$03 ; BNE source$8a46
  .assert *=$aa43,lderror,"Original instruction offset 8a43"
  STA ::TnAudioRam+$9a
  .assert *=$aa46,lderror,"Original instruction offset 8a46"
  JSR $ace8
  .assert *=$aa49,lderror,"Original instruction offset 8a49"
  .byte $b0,$03 ; BCS source$8a4e
  .assert *=$aa4b,lderror,"Original instruction offset 8a4b"
  .if ::TN_RAW_APU
  STA $4001,x
.else
  jsr ::TnSourceSTA01X
.endif
  .assert *=$aa4e,lderror,"Original instruction offset 8a4e"
  LDX ::TnAudioRam+$92
  .assert *=$aa51,lderror,"Original instruction offset 8a51"
  INY
  .assert *=$aa52,lderror,"Original instruction offset 8a52"
  JMP $a9cd
  .assert *=$aa55,lderror,"Original instruction offset 8a55"
  LDA ::TnAudioRam+$16,x
  .assert *=$aa58,lderror,"Original instruction offset 8a58"
  AND #$7f
  .assert *=$aa5a,lderror,"Original instruction offset 8a5a"
  STA ::TnAudioRam+$16,x
  .assert *=$aa5d,lderror,"Original instruction offset 8a5d"
  LDA #$7f
  .assert *=$aa5f,lderror,"Original instruction offset 8a5f"
  JMP $aa3f
  .assert *=$aa62,lderror,"Original instruction offset 8a62"
  .if ::TN_RAW_APU
  STA $4008
.else
  jsr ::TnSourceSTA08
.endif
  .assert *=$aa65,lderror,"Original instruction offset 8a65"
  INY
  .assert *=$aa66,lderror,"Original instruction offset 8a66"
  JMP $a9cd
  .assert *=$aa69,lderror,"Original instruction offset 8a69"
  CMP #$00
  .assert *=$aa6b,lderror,"Original instruction offset 8a6b"
  .byte $d0,$e5 ; BNE source$8a52
  .assert *=$aa6d,lderror,"Original instruction offset 8a6d"
  INY
  .assert *=$aa6e,lderror,"Original instruction offset 8a6e"
  JMP $a9cd
  .assert *=$aa71,lderror,"Original instruction offset 8a71"
  LDA ::TnAudioRam+$10,x
  .assert *=$aa74,lderror,"Original instruction offset 8a74"
  STA ::TnAudioRam+$04,x
  .assert *=$aa77,lderror,"Original instruction offset 8a77"
  LDA (::TnAudioZp+$00),y
  .assert *=$aa79,lderror,"Original instruction offset 8a79"
  CPX #$02
  .assert *=$aa7b,lderror,"Original instruction offset 8a7b"
  .byte $f0,$1c ; BEQ source$8a99
  .assert *=$aa7d,lderror,"Original instruction offset 8a7d"
  LSR A
  .assert *=$aa7e,lderror,"Original instruction offset 8a7e"
  LSR A
  .assert *=$aa7f,lderror,"Original instruction offset 8a7f"
  LSR A
  .assert *=$aa80,lderror,"Original instruction offset 8a80"
  LSR A
  .assert *=$aa81,lderror,"Original instruction offset 8a81"
  STA ::TnAudioRam+$52,x
  .assert *=$aa84,lderror,"Original instruction offset 8a84"
  LDA ::TnAudioRam+$58,x
  .assert *=$aa87,lderror,"Original instruction offset 8a87"
  AND #$10
  .assert *=$aa89,lderror,"Original instruction offset 8a89"
  .byte $f0,$26 ; BEQ source$8ab1
  .assert *=$aa8b,lderror,"Original instruction offset 8a8b"
  LDA ::TnAudioRam+$52,x
  .assert *=$aa8e,lderror,"Original instruction offset 8a8e"
  ORA ::TnAudioRam+$58,x
  .assert *=$aa91,lderror,"Original instruction offset 8a91"
  JSR $ace8
  .assert *=$aa94,lderror,"Original instruction offset 8a94"
  .byte $b0,$03 ; BCS source$8a99
  .assert *=$aa96,lderror,"Original instruction offset 8a96"
  .if ::TN_RAW_APU
  STA $4000,x
.else
  jsr ::TnSourceSTA00X
.endif
  .assert *=$aa99,lderror,"Original instruction offset 8a99"
  LDX ::TnAudioRam+$92
  .assert *=$aa9c,lderror,"Original instruction offset 8a9c"
  LDA (::TnAudioZp+$00),y
  .assert *=$aa9e,lderror,"Original instruction offset 8a9e"
  AND #$0f
  .assert *=$aaa0,lderror,"Original instruction offset 8aa0"
  CPX #$05
  .assert *=$aaa2,lderror,"Original instruction offset 8aa2"
  .byte $f0,$05 ; BEQ source$8aa9
  .assert *=$aaa4,lderror,"Original instruction offset 8aa4"
  STA ::TnAudioZp+$0d
  .assert *=$aaa6,lderror,"Original instruction offset 8aa6"
  INY
  .assert *=$aaa7,lderror,"Original instruction offset 8aa7"
  LDA (::TnAudioZp+$00),y
  .assert *=$aaa9,lderror,"Original instruction offset 8aa9"
  STA ::TnAudioZp+$0c
  .assert *=$aaab,lderror,"Original instruction offset 8aab"
  JSR $abda
  .assert *=$aaae,lderror,"Original instruction offset 8aae"
  JMP $af86
  .assert *=$aab1,lderror,"Original instruction offset 8ab1"
  LDA ::TnAudioRam+$58,x
  .assert *=$aab4,lderror,"Original instruction offset 8ab4"
  JMP $aa91
  .assert *=$aab7,lderror,"Original instruction offset 8ab7"
  LDA (::TnAudioZp+$00),y
  .assert *=$aab9,lderror,"Original instruction offset 8ab9"
  AND #$0f
  .assert *=$aabb,lderror,"Original instruction offset 8abb"
  TAX
  .assert *=$aabc,lderror,"Original instruction offset 8abc"
  INX
  .assert *=$aabd,lderror,"Original instruction offset 8abd"
  LDA ::TnAudioRam+$54
  .assert *=$aac0,lderror,"Original instruction offset 8ac0"
  STA ::TnAudioZp+$02
  .assert *=$aac2,lderror,"Original instruction offset 8ac2"
  .byte $f0,$17 ; BEQ source$8adb
  .assert *=$aac4,lderror,"Original instruction offset 8ac4"
  CMP #$80
  .assert *=$aac6,lderror,"Original instruction offset 8ac6"
  .byte $b0,$1e ; BCS source$8ae6
  .assert *=$aac8,lderror,"Original instruction offset 8ac8"
  INC ::TnAudioZp+$02
  .assert *=$aaca,lderror,"Original instruction offset 8aca"
  LDA ::TnAudioZp+$02
  .assert *=$aacc,lderror,"Original instruction offset 8acc"
  DEX
  .assert *=$aacd,lderror,"Original instruction offset 8acd"
  .byte $f0,$08 ; BEQ source$8ad7
  .assert *=$aacf,lderror,"Original instruction offset 8acf"
  CLC
  .assert *=$aad0,lderror,"Original instruction offset 8ad0"
  ADC ::TnAudioZp+$02
  .assert *=$aad2,lderror,"Original instruction offset 8ad2"
  .byte $b0,$07 ; BCS source$8adb
  .assert *=$aad4,lderror,"Original instruction offset 8ad4"
  JMP $aacc
  .assert *=$aad7,lderror,"Original instruction offset 8ad7"
  CMP #$80
  .assert *=$aad9,lderror,"Original instruction offset 8ad9"
  .byte $90,$02 ; BCC source$8add
  .assert *=$aadb,lderror,"Original instruction offset 8adb"
  LDA #$90
  .assert *=$aadd,lderror,"Original instruction offset 8add"
  .if ::TN_RAW_APU
  STA $4008
.else
  jsr ::TnSourceSTA08
.endif
  .assert *=$aae0,lderror,"Original instruction offset 8ae0"
  STA ::TnAudioRam+$9c
  .assert *=$aae3,lderror,"Original instruction offset 8ae3"
  JMP $ab70
  .assert *=$aae6,lderror,"Original instruction offset 8ae6"
  SEC
  .assert *=$aae7,lderror,"Original instruction offset 8ae7"
  SBC #$80
  .assert *=$aae9,lderror,"Original instruction offset 8ae9"
  JMP $aadd
  .assert *=$aaec,lderror,"Original instruction offset 8aec"
  LDA #$01
  .assert *=$aaee,lderror,"Original instruction offset 8aee"
  STA ::TnAudioRam+$66,x
  .assert *=$aaf1,lderror,"Original instruction offset 8af1"
  LDA ::TnAudioRam+$52,x
  .assert *=$aaf4,lderror,"Original instruction offset 8af4"
  JSR $a71e
  .assert *=$aaf7,lderror,"Original instruction offset 8af7"
  LDA ::TnAudioRam+$64,x
  .assert *=$aafa,lderror,"Original instruction offset 8afa"
  AND #$0f
  .assert *=$aafc,lderror,"Original instruction offset 8afc"
  STA ::TnAudioRam+$68,x
  .assert *=$aaff,lderror,"Original instruction offset 8aff"
  LDA ::TnAudioRam+$16,x
  .assert *=$ab02,lderror,"Original instruction offset 8b02"
  AND #$9b
  .assert *=$ab04,lderror,"Original instruction offset 8b04"
  ORA #$02
  .assert *=$ab06,lderror,"Original instruction offset 8b06"
  STA ::TnAudioRam+$16,x
  .assert *=$ab09,lderror,"Original instruction offset 8b09"
  JMP $ab70
  .assert *=$ab0c,lderror,"Original instruction offset 8b0c"
  AND #$7f
  .assert *=$ab0e,lderror,"Original instruction offset 8b0e"
  STA ::TnAudioZp+$04
  .assert *=$ab10,lderror,"Original instruction offset 8b10"
  TXA
  .assert *=$ab11,lderror,"Original instruction offset 8b11"
  SEC
  .assert *=$ab12,lderror,"Original instruction offset 8b12"
  SBC ::TnAudioZp+$04
  .assert *=$ab14,lderror,"Original instruction offset 8b14"
  .byte $b0,$73 ; BCS source$8b89
  .assert *=$ab16,lderror,"Original instruction offset 8b16"
  SEC
  .assert *=$ab17,lderror,"Original instruction offset 8b17"
  SBC #$e8
  .assert *=$ab19,lderror,"Original instruction offset 8b19"
  TAX
  .assert *=$ab1a,lderror,"Original instruction offset 8b1a"
  LDA $afcc,x
  .assert *=$ab1d,lderror,"Original instruction offset 8b1d"
  STA ::TnAudioZp+$0c
  .assert *=$ab1f,lderror,"Original instruction offset 8b1f"
  LDA $afcd,x
  .assert *=$ab22,lderror,"Original instruction offset 8b22"
  STA ::TnAudioZp+$0d
  .assert *=$ab24,lderror,"Original instruction offset 8b24"
  JMP $ab94
  .assert *=$ab27,lderror,"Original instruction offset 8b27"
  LDA ::TnAudioRam+$16,x
  .assert *=$ab2a,lderror,"Original instruction offset 8b2a"
  AND #$df
  .assert *=$ab2c,lderror,"Original instruction offset 8b2c"
  STA ::TnAudioRam+$16,x
  .assert *=$ab2f,lderror,"Original instruction offset 8b2f"
  LDA ::TnAudioRam+$8c,x
  .assert *=$ab32,lderror,"Original instruction offset 8b32"
  LSR A
  .assert *=$ab33,lderror,"Original instruction offset 8b33"
  .byte $90,$08 ; BCC source$8b3d
  .assert *=$ab35,lderror,"Original instruction offset 8b35"
  LDA ::TnAudioRam+$16,x
  .assert *=$ab38,lderror,"Original instruction offset 8b38"
  ORA #$20
  .assert *=$ab3a,lderror,"Original instruction offset 8b3a"
  STA ::TnAudioRam+$16,x
  .assert *=$ab3d,lderror,"Original instruction offset 8b3d"
  RTS
  .assert *=$ab3e,lderror,"Original instruction offset 8b3e"
  JSR $ac71
  .assert *=$ab41,lderror,"Original instruction offset 8b41"
  CPX #$02
  .assert *=$ab43,lderror,"Original instruction offset 8b43"
  .byte $d0,$03 ; BNE source$8b48
  .assert *=$ab45,lderror,"Original instruction offset 8b45"
  JMP $aab7
  .assert *=$ab48,lderror,"Original instruction offset 8b48"
  JSR $ab27
  .assert *=$ab4b,lderror,"Original instruction offset 8b4b"
  LDA ::TnAudioRam+$64,x
  .assert *=$ab4e,lderror,"Original instruction offset 8b4e"
  .byte $30,$9c ; BMI source$8aec
  .assert *=$ab50,lderror,"Original instruction offset 8b50"
  LDA #$00
  .assert *=$ab52,lderror,"Original instruction offset 8b52"
  STA ::TnAudioRam+$68,x
  .assert *=$ab55,lderror,"Original instruction offset 8b55"
  STA ::TnAudioRam+$6c,x
  .assert *=$ab58,lderror,"Original instruction offset 8b58"
  STA ::TnAudioRam+$6a,x
  .assert *=$ab5b,lderror,"Original instruction offset 8b5b"
  STA ::TnAudioRam+$66,x
  .assert *=$ab5e,lderror,"Original instruction offset 8b5e"
  INC ::TnAudioRam+$66,x
  .assert *=$ab61,lderror,"Original instruction offset 8b61"
  STY ::TnAudioZp+$04
  .assert *=$ab63,lderror,"Original instruction offset 8b63"
  JSR $a6f3
  .assert *=$ab66,lderror,"Original instruction offset 8b66"
  LDY ::TnAudioZp+$04
  .assert *=$ab68,lderror,"Original instruction offset 8b68"
  LDA ::TnAudioRam+$16,x
  .assert *=$ab6b,lderror,"Original instruction offset 8b6b"
  AND #$99
  .assert *=$ab6d,lderror,"Original instruction offset 8b6d"
  STA ::TnAudioRam+$16,x
  .assert *=$ab70,lderror,"Original instruction offset 8b70"
  LDA (::TnAudioZp+$00),y
  .assert *=$ab72,lderror,"Original instruction offset 8b72"
  AND #$f0
  .assert *=$ab74,lderror,"Original instruction offset 8b74"
  LSR A
  .assert *=$ab75,lderror,"Original instruction offset 8b75"
  LSR A
  .assert *=$ab76,lderror,"Original instruction offset 8b76"
  LSR A
  .assert *=$ab77,lderror,"Original instruction offset 8b77"
  TAX
  .assert *=$ab78,lderror,"Original instruction offset 8b78"
  TYA
  .assert *=$ab79,lderror,"Original instruction offset 8b79"
  PHA
  .assert *=$ab7a,lderror,"Original instruction offset 8b7a"
  LDY ::TnAudioRam+$92
  .assert *=$ab7d,lderror,"Original instruction offset 8b7d"
  LDA ::TnAudioRam+$61,y
  .assert *=$ab80,lderror,"Original instruction offset 8b80"
  .byte $f0,$08 ; BEQ source$8b8a
  .assert *=$ab82,lderror,"Original instruction offset 8b82"
  .byte $30,$88 ; BMI source$8b0c
  .assert *=$ab84,lderror,"Original instruction offset 8b84"
  TXA
  .assert *=$ab85,lderror,"Original instruction offset 8b85"
  CLC
  .assert *=$ab86,lderror,"Original instruction offset 8b86"
  ADC ::TnAudioRam+$61,y
  .assert *=$ab89,lderror,"Original instruction offset 8b89"
  TAX
  .assert *=$ab8a,lderror,"Original instruction offset 8b8a"
  LDA $afe4,x
  .assert *=$ab8d,lderror,"Original instruction offset 8b8d"
  STA ::TnAudioZp+$0c
  .assert *=$ab8f,lderror,"Original instruction offset 8b8f"
  LDA $afe5,x
  .assert *=$ab92,lderror,"Original instruction offset 8b92"
  STA ::TnAudioZp+$0d
  .assert *=$ab94,lderror,"Original instruction offset 8b94"
  PLA
  .assert *=$ab95,lderror,"Original instruction offset 8b95"
  TAY
  .assert *=$ab96,lderror,"Original instruction offset 8b96"
  LDX ::TnAudioRam+$92
  .assert *=$ab99,lderror,"Original instruction offset 8b99"
  LDA ::TnAudioRam+$5e,x
  .assert *=$ab9c,lderror,"Original instruction offset 8b9c"
  TAX
  .assert *=$ab9d,lderror,"Original instruction offset 8b9d"
  CPX #$05
  .assert *=$ab9f,lderror,"Original instruction offset 8b9f"
  .byte $f0,$07 ; BEQ source$8ba8
  .assert *=$aba1,lderror,"Original instruction offset 8ba1"
  LSR ::TnAudioZp+$0d
  .assert *=$aba3,lderror,"Original instruction offset 8ba3"
  ROR ::TnAudioZp+$0c
  .assert *=$aba5,lderror,"Original instruction offset 8ba5"
  INX
  .assert *=$aba6,lderror,"Original instruction offset 8ba6"
  .byte $d0,$f5 ; BNE source$8b9d
  .assert *=$aba8,lderror,"Original instruction offset 8ba8"
  LDX ::TnAudioRam+$92
  .assert *=$abab,lderror,"Original instruction offset 8bab"
  CPX #$02
  .assert *=$abad,lderror,"Original instruction offset 8bad"
  .byte $f0,$25 ; BEQ source$8bd4
  .assert *=$abaf,lderror,"Original instruction offset 8baf"
  LDA ::TnAudioRam+$8e,x
  .assert *=$abb2,lderror,"Original instruction offset 8bb2"
  .byte $30,$03 ; BMI source$8bb7
  .assert *=$abb4,lderror,"Original instruction offset 8bb4"
  JSR $ac24
  .assert *=$abb7,lderror,"Original instruction offset 8bb7"
  LDA ::TnAudioZp+$0c
  .assert *=$abb9,lderror,"Original instruction offset 8bb9"
  STA ::TnAudioRam+$7a,x
  .assert *=$abbc,lderror,"Original instruction offset 8bbc"
  LDA ::TnAudioZp+$0d
  .assert *=$abbe,lderror,"Original instruction offset 8bbe"
  STA ::TnAudioRam+$7c,x
  .assert *=$abc1,lderror,"Original instruction offset 8bc1"
  LDA ::TnAudioRam+$16,x
  .assert *=$abc4,lderror,"Original instruction offset 8bc4"
  AND #$10
  .assert *=$abc6,lderror,"Original instruction offset 8bc6"
  .byte $f0,$0c ; BEQ source$8bd4
  .assert *=$abc8,lderror,"Original instruction offset 8bc8"
  LDA ::TnAudioRam+$7e,x
  .assert *=$abcb,lderror,"Original instruction offset 8bcb"
  .byte $d0,$07 ; BNE source$8bd4
  .assert *=$abcd,lderror,"Original instruction offset 8bcd"
  TYA
  .assert *=$abce,lderror,"Original instruction offset 8bce"
  PHA
  .assert *=$abcf,lderror,"Original instruction offset 8bcf"
  JSR $a857
  .assert *=$abd2,lderror,"Original instruction offset 8bd2"
  PLA
  .assert *=$abd3,lderror,"Original instruction offset 8bd3"
  TAY
  .assert *=$abd4,lderror,"Original instruction offset 8bd4"
  JSR $abda
  .assert *=$abd7,lderror,"Original instruction offset 8bd7"
  JMP $af86
  .assert *=$abda,lderror,"Original instruction offset 8bda"
  CPX #$02
  .assert *=$abdc,lderror,"Original instruction offset 8bdc"
  .byte $f0,$1f ; BEQ source$8bfd
  .assert *=$abde,lderror,"Original instruction offset 8bde"
  LDA ::TnAudioRam+$80,x
  .assert *=$abe1,lderror,"Original instruction offset 8be1"
  CMP #$ff
  .assert *=$abe3,lderror,"Original instruction offset 8be3"
  .byte $d0,$01 ; BNE source$8be6
  .assert *=$abe5,lderror,"Original instruction offset 8be5"
  RTS
  .assert *=$abe6,lderror,"Original instruction offset 8be6"
  CPX #$05
  .assert *=$abe8,lderror,"Original instruction offset 8be8"
  .byte $f0,$13 ; BEQ source$8bfd
  .assert *=$abea,lderror,"Original instruction offset 8bea"
  LDA ::TnAudioZp+$0d
  .assert *=$abec,lderror,"Original instruction offset 8bec"
  CMP ::TnAudioRam+$46,x
  .assert *=$abef,lderror,"Original instruction offset 8bef"
  .byte $d0,$0e ; BNE source$8bff
  .assert *=$abf1,lderror,"Original instruction offset 8bf1"
  LDA ::TnAudioRam+$16,x
  .assert *=$abf4,lderror,"Original instruction offset 8bf4"
  .byte $30,$07 ; BMI source$8bfd
  .assert *=$abf6,lderror,"Original instruction offset 8bf6"
  LDA ::TnAudioRam+$58,x
  .assert *=$abf9,lderror,"Original instruction offset 8bf9"
  AND #$10
  .assert *=$abfb,lderror,"Original instruction offset 8bfb"
  .byte $d0,$0f ; BNE source$8c0c
  .assert *=$abfd,lderror,"Original instruction offset 8bfd"
  LDA ::TnAudioZp+$0d
  .assert *=$abff,lderror,"Original instruction offset 8bff"
  STA ::TnAudioRam+$46,x
  .assert *=$ac02,lderror,"Original instruction offset 8c02"
  ORA #$08
  .assert *=$ac04,lderror,"Original instruction offset 8c04"
  JSR $ace8
  .assert *=$ac07,lderror,"Original instruction offset 8c07"
  .byte $b0,$03 ; BCS source$8c0c
  .assert *=$ac09,lderror,"Original instruction offset 8c09"
  .if ::TN_RAW_APU
  STA $4003,x
.else
  jsr ::TnSourceSTA03X
.endif
  .assert *=$ac0c,lderror,"Original instruction offset 8c0c"
  LDA ::TnAudioZp+$0c
  .assert *=$ac0e,lderror,"Original instruction offset 8c0e"
  LDX ::TnAudioRam+$92
  .assert *=$ac11,lderror,"Original instruction offset 8c11"
  CPX #$02
  .assert *=$ac13,lderror,"Original instruction offset 8c13"
  .byte $b0,$03 ; BCS source$8c18
  .assert *=$ac15,lderror,"Original instruction offset 8c15"
  STA ::TnAudioRam+$78,x
  .assert *=$ac18,lderror,"Original instruction offset 8c18"
  JSR $ace8
  .assert *=$ac1b,lderror,"Original instruction offset 8c1b"
  .byte $b0,$03 ; BCS source$8c20
  .assert *=$ac1d,lderror,"Original instruction offset 8c1d"
  .if ::TN_RAW_APU
  STA $4002,x
.else
  jsr ::TnSourceSTA02X
.endif
  .assert *=$ac20,lderror,"Original instruction offset 8c20"
  LDX ::TnAudioRam+$92
  .assert *=$ac23,lderror,"Original instruction offset 8c23"
  RTS
  .assert *=$ac24,lderror,"Original instruction offset 8c24"
  STY ::TnAudioZp+$02
  .assert *=$ac26,lderror,"Original instruction offset 8c26"
  LDA ::TnAudioRam+$90,x
  .assert *=$ac29,lderror,"Original instruction offset 8c29"
  CPX #$01
  .assert *=$ac2b,lderror,"Original instruction offset 8c2b"
  .byte $d0,$02 ; BNE source$8c2f
  .assert *=$ac2d,lderror,"Original instruction offset 8c2d"
  ORA #$04
  .assert *=$ac2f,lderror,"Original instruction offset 8c2f"
  TAY
  .assert *=$ac30,lderror,"Original instruction offset 8c30"
  LDA ::TnAudioZp+$0d
  .assert *=$ac32,lderror,"Original instruction offset 8c32"
  STA ::TnAudioRam+$a6,y
  .assert *=$ac35,lderror,"Original instruction offset 8c35"
  LDA ::TnAudioZp+$0c
  .assert *=$ac37,lderror,"Original instruction offset 8c37"
  STA ::TnAudioRam+$9e,y
  .assert *=$ac3a,lderror,"Original instruction offset 8c3a"
  LDA ::TnAudioRam+$8e,x
  .assert *=$ac3d,lderror,"Original instruction offset 8c3d"
  AND #$40
  .assert *=$ac3f,lderror,"Original instruction offset 8c3f"
  .byte $f0,$1b ; BEQ source$8c5c
  .assert *=$ac41,lderror,"Original instruction offset 8c41"
  LDA ::TnAudioRam+$8e,x
  .assert *=$ac44,lderror,"Original instruction offset 8c44"
  AND #$bf
  .assert *=$ac46,lderror,"Original instruction offset 8c46"
  STA ::TnAudioRam+$8e,x
  .assert *=$ac49,lderror,"Original instruction offset 8c49"
  LDA #$03
  .assert *=$ac4b,lderror,"Original instruction offset 8c4b"
  STA ::TnAudioZp+$04
  .assert *=$ac4d,lderror,"Original instruction offset 8c4d"
  INY
  .assert *=$ac4e,lderror,"Original instruction offset 8c4e"
  LDA ::TnAudioZp+$0d
  .assert *=$ac50,lderror,"Original instruction offset 8c50"
  STA ::TnAudioRam+$a6,y
  .assert *=$ac53,lderror,"Original instruction offset 8c53"
  LDA ::TnAudioZp+$0c
  .assert *=$ac55,lderror,"Original instruction offset 8c55"
  STA ::TnAudioRam+$9e,y
  .assert *=$ac58,lderror,"Original instruction offset 8c58"
  DEC ::TnAudioZp+$04
  .assert *=$ac5a,lderror,"Original instruction offset 8c5a"
  .byte $d0,$f1 ; BNE source$8c4d
  .assert *=$ac5c,lderror,"Original instruction offset 8c5c"
  LDY ::TnAudioZp+$02
  .assert *=$ac5e,lderror,"Original instruction offset 8c5e"
  INC ::TnAudioRam+$90,x
  .assert *=$ac61,lderror,"Original instruction offset 8c61"
  LDA ::TnAudioRam+$90,x
  .assert *=$ac64,lderror,"Original instruction offset 8c64"
  AND #$03
  .assert *=$ac66,lderror,"Original instruction offset 8c66"
  STA ::TnAudioRam+$90,x
  .assert *=$ac69,lderror,"Original instruction offset 8c69"
  RTS
  .assert *=$ac6a,lderror,"Original instruction offset 8c6a"
  JSR $af86
  .assert *=$ac6d,lderror,"Original instruction offset 8c6d"
  DEY
  .assert *=$ac6e,lderror,"Original instruction offset 8c6e"
  JMP $a972
  .assert *=$ac71,lderror,"Original instruction offset 8c71"
  LDA (::TnAudioZp+$00),y
  .assert *=$ac73,lderror,"Original instruction offset 8c73"
  AND #$0f
  .assert *=$ac75,lderror,"Original instruction offset 8c75"
  STA ::TnAudioZp+$02
  .assert *=$ac77,lderror,"Original instruction offset 8c77"
  .byte $f0,$0d ; BEQ source$8c86
  .assert *=$ac79,lderror,"Original instruction offset 8c79"
  LDA ::TnAudioRam+$10,x
  .assert *=$ac7c,lderror,"Original duration entry"
  jsr TnFastDuration
  jmp $ac89
  .res 4,$ea
  .assert *=$ac86,lderror,"Original instruction offset 8c86"
  LDA ::TnAudioRam+$10,x
  .assert *=$ac89,lderror,"Original instruction offset 8c89"
  STA ::TnAudioRam+$04,x
  .assert *=$ac8c,lderror,"Original instruction offset 8c8c"
  CPX #$02
  .assert *=$ac8e,lderror,"Original instruction offset 8c8e"
  .byte $b0,$1b ; BCS source$8cab
  .assert *=$ac90,lderror,"Original instruction offset 8c90"
  LDA ::TnAudioRam+$16,x
  .assert *=$ac93,lderror,"Original instruction offset 8c93"
  AND #$10
  .assert *=$ac95,lderror,"Original instruction offset 8c95"
  .byte $f0,$14 ; BEQ source$8cab
  .assert *=$ac97,lderror,"Original instruction offset 8c97"
  LDA ::TnAudioRam+$7e,x
  .assert *=$ac9a,lderror,"Original instruction offset 8c9a"
  STA ::TnAudioRam+$80,x
  .assert *=$ac9d,lderror,"Original instruction offset 8c9d"
  INC ::TnAudioRam+$80,x
  .assert *=$aca0,lderror,"Original instruction offset 8ca0"
  LDA #$00
  .assert *=$aca2,lderror,"Original instruction offset 8ca2"
  STA ::TnAudioRam+$86,x
  .assert *=$aca5,lderror,"Original instruction offset 8ca5"
  STA ::TnAudioRam+$8a,x
  .assert *=$aca8,lderror,"Original instruction offset 8ca8"
  STA ::TnAudioRam+$88,x
  .assert *=$acab,lderror,"Original instruction offset 8cab"
  CPX #$02
  .assert *=$acad,lderror,"Original instruction offset 8cad"
  .byte $f0,$0d ; BEQ source$8cbc
  .assert *=$acaf,lderror,"Original instruction offset 8caf"
  CPX #$03
  .assert *=$acb1,lderror,"Original instruction offset 8cb1"
  .byte $f0,$b7 ; BEQ source$8c6a
  .assert *=$acb3,lderror,"Original instruction offset 8cb3"
  LDA ::TnAudioRam+$70,x
  .assert *=$acb6,lderror,"Original instruction offset 8cb6"
  JSR $acbd
  .assert *=$acb9,lderror,"Original instruction offset 8cb9"
  STA ::TnAudioRam+$6e,x
  .assert *=$acbc,lderror,"Original instruction offset 8cbc"
  RTS
  .assert *=$acbd,lderror,"Original instruction offset 8cbd"
  JMP ::TnFastProduct
  NOP ; Four-byte span; old internal counter store is no longer an entry.
  .assert *=$acc1,lderror,"Original instruction offset 8cc1"
  LDA #$00
  .assert *=$acc3,lderror,"Original instruction offset 8cc3"
  STA ::TnAudioZp+$04
  .assert *=$acc5,lderror,"Original instruction offset 8cc5"
  STA ::TnAudioZp+$05
  .assert *=$acc7,lderror,"Original instruction offset 8cc7"
  DEC ::TnAudioZp+$02
  .assert *=$acc9,lderror,"Original instruction offset 8cc9"
  .byte $30,$0e ; BMI source$8cd9
  .assert *=$accb,lderror,"Original instruction offset 8ccb"
  CLC
  .assert *=$accc,lderror,"Original instruction offset 8ccc"
  LDA ::TnAudioRam+$04,x
  .assert *=$accf,lderror,"Original instruction offset 8ccf"
  ADC ::TnAudioZp+$04
  .assert *=$acd1,lderror,"Original instruction offset 8cd1"
  STA ::TnAudioZp+$04
  .assert *=$acd3,lderror,"Original instruction offset 8cd3"
  .byte $90,$f2 ; BCC source$8cc7
  .assert *=$acd5,lderror,"Original instruction offset 8cd5"
  INC ::TnAudioZp+$05
  .assert *=$acd7,lderror,"Original instruction offset 8cd7"
  .byte $d0,$ee ; BNE source$8cc7
  .assert *=$acd9,lderror,"Original instruction offset 8cd9"
  ASL A
  .assert *=$acda,lderror,"Original instruction offset 8cda"
  ROL ::TnAudioZp+$05
  .assert *=$acdc,lderror,"Original instruction offset 8cdc"
  ASL A
  .assert *=$acdd,lderror,"Original instruction offset 8cdd"
  ROL ::TnAudioZp+$05
  .assert *=$acdf,lderror,"Original instruction offset 8cdf"
  ASL A
  .assert *=$ace0,lderror,"Original instruction offset 8ce0"
  ROL ::TnAudioZp+$05
  .assert *=$ace2,lderror,"Original instruction offset 8ce2"
  ASL A
  .assert *=$ace3,lderror,"Original instruction offset 8ce3"
  ROL ::TnAudioZp+$05
  .assert *=$ace5,lderror,"Original instruction offset 8ce5"
  LDA ::TnAudioZp+$05
  .assert *=$ace7,lderror,"Original instruction offset 8ce7"
  RTS
  .assert *=$ace8,lderror,"Original instruction offset 8ce8"
  PHA
  .assert *=$ace9,lderror,"Original instruction offset 8ce9"
  CPX #$00
  .assert *=$aceb,lderror,"Original instruction offset 8ceb"
  .byte $f0,$06 ; BEQ source$8cf3
  .assert *=$aced,lderror,"Original instruction offset 8ced"
  LDX ::TnAudioRam+$93
  .assert *=$acf0,lderror,"Original instruction offset 8cf0"
  CLC
  .assert *=$acf1,lderror,"Original instruction offset 8cf1"
  PLA
  .assert *=$acf2,lderror,"Original instruction offset 8cf2"
  RTS
  .assert *=$acf3,lderror,"Original instruction offset 8cf3"
  LDA ::TnAudioRam+$0e
  .assert *=$acf6,lderror,"Original instruction offset 8cf6"
  .byte $f0,$f8 ; BEQ source$8cf0
  .assert *=$acf8,lderror,"Original instruction offset 8cf8"
  SEC
  .assert *=$acf9,lderror,"Original instruction offset 8cf9"
  PLA
  .assert *=$acfa,lderror,"Original instruction offset 8cfa"
  RTS
  .assert *=$acfb,lderror,"Original instruction offset 8cfb"
  JSR $ac75
  .assert *=$acfe,lderror,"Original instruction offset 8cfe"
  LDA #$00
  .assert *=$ad00,lderror,"Original instruction offset 8d00"
  CPX #$02
  .assert *=$ad02,lderror,"Original instruction offset 8d02"
  .byte $d0,$06 ; BNE source$8d0a
  .assert *=$ad04,lderror,"Original instruction offset 8d04"
  JSR $af45
  .assert *=$ad07,lderror,"Original instruction offset 8d07"
  JMP $ad14
  .assert *=$ad0a,lderror,"Original instruction offset 8d0a"
  LDA #$30
  .assert *=$ad0c,lderror,"Original instruction offset 8d0c"
  JSR $ace8
  .assert *=$ad0f,lderror,"Original instruction offset 8d0f"
  .byte $b0,$03 ; BCS source$8d14
  .assert *=$ad11,lderror,"Original instruction offset 8d11"
  .if ::TN_RAW_APU
  STA $4000,x
.else
  jsr ::TnSourceSTA00X
.endif
  .assert *=$ad14,lderror,"Original instruction offset 8d14"
  LDX ::TnAudioRam+$92
  .assert *=$ad17,lderror,"Original instruction offset 8d17"
  LDA ::TnAudioRam+$16,x
  .assert *=$ad1a,lderror,"Original instruction offset 8d1a"
  ORA #$40
  .assert *=$ad1c,lderror,"Original instruction offset 8d1c"
  STA ::TnAudioRam+$16,x
  .assert *=$ad1f,lderror,"Original instruction offset 8d1f"
  JMP $af86
  .assert *=$ad22,lderror,"Original instruction offset 8d22"
  STA ::TnAudioRam+$10,x
  .assert *=$ad25,lderror,"Original instruction offset 8d25"
  INY
  .assert *=$ad26,lderror,"Original instruction offset 8d26"
  LDA (::TnAudioZp+$00),y
  .assert *=$ad28,lderror,"Original instruction offset 8d28"
  CPX #$02
  .assert *=$ad2a,lderror,"Original instruction offset 8d2a"
  .byte $f0,$3d ; BEQ source$8d69
  .assert *=$ad2c,lderror,"Original instruction offset 8d2c"
  AND #$f0
  .assert *=$ad2e,lderror,"Original instruction offset 8d2e"
  STA ::TnAudioRam+$58,x
  .assert *=$ad31,lderror,"Original instruction offset 8d31"
  LDA (::TnAudioZp+$00),y
  .assert *=$ad33,lderror,"Original instruction offset 8d33"
  AND #$0f
  .assert *=$ad35,lderror,"Original instruction offset 8d35"
  STA ::TnAudioRam+$52,x
  .assert *=$ad38,lderror,"Original instruction offset 8d38"
  INY
  .assert *=$ad39,lderror,"Original instruction offset 8d39"
  LDA (::TnAudioZp+$00),y
  .assert *=$ad3b,lderror,"Original instruction offset 8d3b"
  STA ::TnAudioRam+$64,x
  .assert *=$ad3e,lderror,"Original instruction offset 8d3e"
  .byte $10,$04 ; BPL source$8d44
  .assert *=$ad40,lderror,"Original instruction offset 8d40"
  LDA #$00
  .assert *=$ad42,lderror,"Original instruction offset 8d42"
  .byte $f0,$03 ; BEQ source$8d47
  .assert *=$ad44,lderror,"Original instruction offset 8d44"
  LDA ::TnAudioRam+$52,x
  .assert *=$ad47,lderror,"Original instruction offset 8d47"
  STA ::TnAudioRam+$76,x
  .assert *=$ad4a,lderror,"Original instruction offset 8d4a"
  INY
  .assert *=$ad4b,lderror,"Original instruction offset 8d4b"
  LDA (::TnAudioZp+$00),y
  .assert *=$ad4d,lderror,"Original instruction offset 8d4d"
  AND #$0f
  .assert *=$ad4f,lderror,"Original instruction offset 8d4f"
  STA ::TnAudioRam+$70,x
  .assert *=$ad52,lderror,"Original instruction offset 8d52"
  LDA (::TnAudioZp+$00),y
  .assert *=$ad54,lderror,"Original instruction offset 8d54"
  LSR A
  .assert *=$ad55,lderror,"Original instruction offset 8d55"
  LSR A
  .assert *=$ad56,lderror,"Original instruction offset 8d56"
  LSR A
  .assert *=$ad57,lderror,"Original instruction offset 8d57"
  LSR A
  .assert *=$ad58,lderror,"Original instruction offset 8d58"
  STA ::TnAudioRam+$72,x
  .assert *=$ad5b,lderror,"Original instruction offset 8d5b"
  LDA ::TnAudioRam+$72,x
  .assert *=$ad5e,lderror,"Original instruction offset 8d5e"
  .byte $d0,$02 ; BNE source$8d62
  .assert *=$ad60,lderror,"Original instruction offset 8d60"
  LDA #$01
  .assert *=$ad62,lderror,"Original instruction offset 8d62"
  STA ::TnAudioRam+$74,x
  .assert *=$ad65,lderror,"Original instruction offset 8d65"
  INY
  .assert *=$ad66,lderror,"Original instruction offset 8d66"
  JMP $a925
  .assert *=$ad69,lderror,"Original instruction offset 8d69"
  STA ::TnAudioRam+$54
  .assert *=$ad6c,lderror,"Original instruction offset 8d6c"
  INY
  .assert *=$ad6d,lderror,"Original instruction offset 8d6d"
  JMP $a925
  .assert *=$ad70,lderror,"Original instruction offset 8d70"
  CMP #$06
  .assert *=$ad72,lderror,"Original instruction offset 8d72"
  .byte $b0,$07 ; BCS source$8d7b
  .assert *=$ad74,lderror,"Original instruction offset 8d74"
  STA ::TnAudioRam+$5e,x
  .assert *=$ad77,lderror,"Original instruction offset 8d77"
  INY
  .assert *=$ad78,lderror,"Original instruction offset 8d78"
  JMP $a925
  .assert *=$ad7b,lderror,"Original instruction offset 8d7b"
  AND #$0f
  .assert *=$ad7d,lderror,"Original instruction offset 8d7d"
  SEC
  .assert *=$ad7e,lderror,"Original instruction offset 8d7e"
  SBC #$06
  .assert *=$ad80,lderror,"Original instruction offset 8d80"
  ASL A
  .assert *=$ad81,lderror,"Original instruction offset 8d81"
  TAX
  .assert *=$ad82,lderror,"Original instruction offset 8d82"
  LDA $ad92,x
  .assert *=$ad85,lderror,"Original instruction offset 8d85"
  STA ::TnAudioZp+$02
  .assert *=$ad87,lderror,"Original instruction offset 8d87"
  LDA $ad93,x
  .assert *=$ad8a,lderror,"Original instruction offset 8d8a"
  STA ::TnAudioZp+$03
  .assert *=$ad8c,lderror,"Original instruction offset 8d8c"
  LDX ::TnAudioRam+$92
  .assert *=$ad8f,lderror,"Original instruction offset 8d8f"
  JMP (::TnAudioZp+$02)
  .word $ada0 ; source pointer$8d92
  .word $adaa ; source pointer$8d94
  .word $adb4 ; source pointer$8d96
  .word $adb8 ; source pointer$8d98
  .word $ade5 ; source pointer$8d9a
  .word $adf8 ; source pointer$8d9c
  .word $ae43 ; source pointer$8d9e
  .assert *=$ada0,lderror,"Original instruction offset 8da0"
  INY
  .assert *=$ada1,lderror,"Original instruction offset 8da1"
  LDA (::TnAudioZp+$00),y
  .assert *=$ada3,lderror,"Original instruction offset 8da3"
  STA ::TnAudioRam+$10,x
  .assert *=$ada6,lderror,"Original instruction offset 8da6"
  INY
  .assert *=$ada7,lderror,"Original instruction offset 8da7"
  JMP $a925
  .assert *=$adaa,lderror,"Original instruction offset 8daa"
  INY
  .assert *=$adab,lderror,"Original instruction offset 8dab"
  LDA (::TnAudioZp+$00),y
  .assert *=$adad,lderror,"Original instruction offset 8dad"
  STA ::TnAudioRam+$64,x
  .assert *=$adb0,lderror,"Original instruction offset 8db0"
  INY
  .assert *=$adb1,lderror,"Original instruction offset 8db1"
  JMP $a925
  .assert *=$adb4,lderror,"Original instruction offset 8db4"
  INY
  .assert *=$adb5,lderror,"Original instruction offset 8db5"
  JMP $ad4b
  .assert *=$adb8,lderror,"Original instruction offset 8db8"
  INY
  .assert *=$adb9,lderror,"Original instruction offset 8db9"
  LDA (::TnAudioZp+$00),y
  .assert *=$adbb,lderror,"Original instruction offset 8dbb"
  .byte $f0,$15 ; BEQ source$8dd2
  .assert *=$adbd,lderror,"Original instruction offset 8dbd"
  AND #$0f
  .assert *=$adbf,lderror,"Original instruction offset 8dbf"
  .byte $f0,$1c ; BEQ source$8ddd
  .assert *=$adc1,lderror,"Original instruction offset 8dc1"
  LDA (::TnAudioZp+$00),y
  .assert *=$adc3,lderror,"Original instruction offset 8dc3"
  STA ::TnAudioRam+$8c,x
  .assert *=$adc6,lderror,"Original instruction offset 8dc6"
  LDA ::TnAudioRam+$16,x
  .assert *=$adc9,lderror,"Original instruction offset 8dc9"
  ORA #$20
  .assert *=$adcb,lderror,"Original instruction offset 8dcb"
  STA ::TnAudioRam+$16,x
  .assert *=$adce,lderror,"Original instruction offset 8dce"
  INY
  .assert *=$adcf,lderror,"Original instruction offset 8dcf"
  JMP $a925
  .assert *=$add2,lderror,"Original instruction offset 8dd2"
  LDA ::TnAudioRam+$16,x
  .assert *=$add5,lderror,"Original instruction offset 8dd5"
  AND #$df
  .assert *=$add7,lderror,"Original instruction offset 8dd7"
  STA ::TnAudioRam+$16,x
  .assert *=$adda,lderror,"Original instruction offset 8dda"
  JMP $adce
  .assert *=$addd,lderror,"Original instruction offset 8ddd"
  LDA (::TnAudioZp+$00),y
  .assert *=$addf,lderror,"Original instruction offset 8ddf"
  STA ::TnAudioRam+$58,x
  .assert *=$ade2,lderror,"Original instruction offset 8de2"
  JMP $adce
  .assert *=$ade5,lderror,"Original instruction offset 8de5"
  INY
  .assert *=$ade6,lderror,"Original instruction offset 8de6"
  LDA (::TnAudioZp+$00),y
  .assert *=$ade8,lderror,"Original instruction offset 8de8"
  .byte $30,$08 ; BMI source$8df2
  .assert *=$adea,lderror,"Original instruction offset 8dea"
  ASL A
  .assert *=$adeb,lderror,"Original instruction offset 8deb"
  STA ::TnAudioRam+$61,x
  .assert *=$adee,lderror,"Original instruction offset 8dee"
  INY
  .assert *=$adef,lderror,"Original instruction offset 8def"
  JMP $a925
  .assert *=$adf2,lderror,"Original instruction offset 8df2"
  ASL A
  .assert *=$adf3,lderror,"Original instruction offset 8df3"
  ORA #$80
  .assert *=$adf5,lderror,"Original instruction offset 8df5"
  JMP $adeb
  .assert *=$adf8,lderror,"Original instruction offset 8df8"
  INY
  .assert *=$adf9,lderror,"Original instruction offset 8df9"
  LDA (::TnAudioZp+$00),y
  .assert *=$adfb,lderror,"Original instruction offset 8dfb"
  .byte $f0,$3b ; BEQ source$8e38
  .assert *=$adfd,lderror,"Original instruction offset 8dfd"
  AND #$f0
  .assert *=$adff,lderror,"Original instruction offset 8dff"
  LSR A
  .assert *=$ae00,lderror,"Original instruction offset 8e00"
  LSR A
  .assert *=$ae01,lderror,"Original instruction offset 8e01"
  LSR A
  .assert *=$ae02,lderror,"Original instruction offset 8e02"
  LSR A
  .assert *=$ae03,lderror,"Original instruction offset 8e03"
  CMP #$00
  .assert *=$ae05,lderror,"Original instruction offset 8e05"
  .byte $f0,$16 ; BEQ source$8e1d
  .assert *=$ae07,lderror,"Original instruction offset 8e07"
  STA ::TnAudioZp+$02
  .assert *=$ae09,lderror,"Original instruction offset 8e09"
  DEC ::TnAudioZp+$02
  .assert *=$ae0b,lderror,"Original instruction offset 8e0b"
  .byte $f0,$0d ; BEQ source$8e1a
  .assert *=$ae0d,lderror,"Original instruction offset 8e0d"
  LDA ::TnAudioRam+$10,x
  .assert *=$ae10,lderror,"Original instruction offset 8e10"
  CLC
  .assert *=$ae11,lderror,"Original instruction offset 8e11"
  ADC ::TnAudioRam+$10,x
  .assert *=$ae14,lderror,"Original instruction offset 8e14"
  DEC ::TnAudioZp+$02
  .assert *=$ae16,lderror,"Original instruction offset 8e16"
  .byte $d0,$f9 ; BNE source$8e11
  .assert *=$ae18,lderror,"Original instruction offset 8e18"
  .byte $f0,$03 ; BEQ source$8e1d
  .assert *=$ae1a,lderror,"Original instruction offset 8e1a"
  LDA ::TnAudioRam+$10,x
  .assert *=$ae1d,lderror,"Original instruction offset 8e1d"
  STA ::TnAudioRam+$7e,x
  .assert *=$ae20,lderror,"Original instruction offset 8e20"
  LDA (::TnAudioZp+$00),y
  .assert *=$ae22,lderror,"Original instruction offset 8e22"
  AND #$0f
  .assert *=$ae24,lderror,"Original instruction offset 8e24"
  STA ::TnAudioRam+$82,x
  .assert *=$ae27,lderror,"Original instruction offset 8e27"
  INY
  .assert *=$ae28,lderror,"Original instruction offset 8e28"
  LDA (::TnAudioZp+$00),y
  .assert *=$ae2a,lderror,"Original instruction offset 8e2a"
  STA ::TnAudioRam+$84,x
  .assert *=$ae2d,lderror,"Original instruction offset 8e2d"
  LDA ::TnAudioRam+$16,x
  .assert *=$ae30,lderror,"Original instruction offset 8e30"
  ORA #$10
  .assert *=$ae32,lderror,"Original instruction offset 8e32"
  STA ::TnAudioRam+$16,x
  .assert *=$ae35,lderror,"Original instruction offset 8e35"
  JMP $adce
  .assert *=$ae38,lderror,"Original instruction offset 8e38"
  LDA ::TnAudioRam+$16,x
  .assert *=$ae3b,lderror,"Original instruction offset 8e3b"
  AND #$ef
  .assert *=$ae3d,lderror,"Original instruction offset 8e3d"
  STA ::TnAudioRam+$16,x
  .assert *=$ae40,lderror,"Original instruction offset 8e40"
  JMP $adce
  .assert *=$ae43,lderror,"Original instruction offset 8e43"
  INY
  .assert *=$ae44,lderror,"Original instruction offset 8e44"
  LDA (::TnAudioZp+$00),y
  .assert *=$ae46,lderror,"Original instruction offset 8e46"
  .byte $f0,$17 ; BEQ source$8e5f
  .assert *=$ae48,lderror,"Original instruction offset 8e48"
  CMP #$04
  .assert *=$ae4a,lderror,"Original instruction offset 8e4a"
  .byte $90,$05 ; BCC source$8e51
  .assert *=$ae4c,lderror,"Original instruction offset 8e4c"
  SEC
  .assert *=$ae4d,lderror,"Original instruction offset 8e4d"
  SBC #$03
  .assert *=$ae4f,lderror,"Original instruction offset 8e4f"
  ORA #$10
  .assert *=$ae51,lderror,"Original instruction offset 8e51"
  ORA #$40
  .assert *=$ae53,lderror,"Original instruction offset 8e53"
  STA ::TnAudioRam+$8e,x
  .assert *=$ae56,lderror,"Original instruction offset 8e56"
  LDA #$00
  .assert *=$ae58,lderror,"Original instruction offset 8e58"
  STA ::TnAudioRam+$90,x
  .assert *=$ae5b,lderror,"Original instruction offset 8e5b"
  INY
  .assert *=$ae5c,lderror,"Original instruction offset 8e5c"
  JMP $a925
  .assert *=$ae5f,lderror,"Original instruction offset 8e5f"
  LDA #$80
  .assert *=$ae61,lderror,"Original instruction offset 8e61"
  STA ::TnAudioRam+$8e,x
  .assert *=$ae64,lderror,"Original instruction offset 8e64"
  .byte $d0,$f5 ; BNE source$8e5b
  .assert *=$ae66,lderror,"Original instruction offset 8e66"
  CMP #$0e
  .assert *=$ae68,lderror,"Original instruction offset 8e68"
  .byte $f0,$48 ; BEQ source$8eb2
  .assert *=$ae6a,lderror,"Original instruction offset 8e6a"
  .byte $90,$03 ; BCC source$8e6f
  .assert *=$ae6c,lderror,"Original instruction offset 8e6c"
  JMP $af10
  .assert *=$ae6f,lderror,"Original instruction offset 8e6f"
  CMP #$0d
  .assert *=$ae71,lderror,"Original instruction offset 8e71"
  .byte $f0,$0f ; BEQ source$8e82
  .assert *=$ae73,lderror,"Original instruction offset 8e73"
  CMP #$0b
  .assert *=$ae75,lderror,"Original instruction offset 8e75"
  .byte $f0,$29 ; BEQ source$8ea0
  .assert *=$ae77,lderror,"Original instruction offset 8e77"
  LDA (::TnAudioZp+$00),y
  .assert *=$ae79,lderror,"Original instruction offset 8e79"
  AND #$0f
  .assert *=$ae7b,lderror,"Original instruction offset 8e7b"
  STA ::TnAudioRam+$76,x
  .assert *=$ae7e,lderror,"Original instruction offset 8e7e"
  INY
  .assert *=$ae7f,lderror,"Original instruction offset 8e7f"
  JMP $a925
  .assert *=$ae82,lderror,"Original instruction offset 8e82"
  JSR $afa3
  .assert *=$ae85,lderror,"Original instruction offset 8e85"
  INY
  .assert *=$ae86,lderror,"Original instruction offset 8e86"
  TYA
  .assert *=$ae87,lderror,"Original instruction offset 8e87"
  CLC
  .assert *=$ae88,lderror,"Original instruction offset 8e88"
  ADC ::TnAudioZp+$00
  .assert *=$ae8a,lderror,"Original instruction offset 8e8a"
  STA ::TnAudioRam+$3a,x
  .assert *=$ae8d,lderror,"Original instruction offset 8e8d"
  LDA #$00
  .assert *=$ae8f,lderror,"Original instruction offset 8e8f"
  TAY
  .assert *=$ae90,lderror,"Original instruction offset 8e90"
  ADC ::TnAudioZp+$01
  .assert *=$ae92,lderror,"Original instruction offset 8e92"
  STA ::TnAudioRam+$40,x
  .assert *=$ae95,lderror,"Original instruction offset 8e95"
  LDA ::TnAudioRam+$16,x
  .assert *=$ae98,lderror,"Original instruction offset 8e98"
  ORA #$08
  .assert *=$ae9a,lderror,"Original instruction offset 8e9a"
  STA ::TnAudioRam+$16,x
  .assert *=$ae9d,lderror,"Original instruction offset 8e9d"
  JMP $aec5
  .assert *=$aea0,lderror,"Original instruction offset 8ea0"
  INY
  .assert *=$aea1,lderror,"Original instruction offset 8ea1"
  TYA
  .assert *=$aea2,lderror,"Original instruction offset 8ea2"
  CLC
  .assert *=$aea3,lderror,"Original instruction offset 8ea3"
  ADC ::TnAudioZp+$00
  .assert *=$aea5,lderror,"Original instruction offset 8ea5"
  STA ::TnAudioRam+$2e,x
  .assert *=$aea8,lderror,"Original instruction offset 8ea8"
  LDA #$00
  .assert *=$aeaa,lderror,"Original instruction offset 8eaa"
  ADC ::TnAudioZp+$01
  .assert *=$aeac,lderror,"Original instruction offset 8eac"
  STA ::TnAudioRam+$34,x
  .assert *=$aeaf,lderror,"Original instruction offset 8eaf"
  JMP $aec8
  .assert *=$aeb2,lderror,"Original instruction offset 8eb2"
  INC ::TnAudioRam+$1c,x
  .assert *=$aeb5,lderror,"Original instruction offset 8eb5"
  LDA ::TnAudioRam+$1c,x
  .assert *=$aeb8,lderror,"Original instruction offset 8eb8"
  INY
  .assert *=$aeb9,lderror,"Original instruction offset 8eb9"
  CMP (::TnAudioZp+$00),y
  .assert *=$aebb,lderror,"Original instruction offset 8ebb"
  .byte $f0,$17 ; BEQ source$8ed4
  .assert *=$aebd,lderror,"Original instruction offset 8ebd"
  .byte $30,$2b ; BMI source$8eea
  .assert *=$aebf,lderror,"Original instruction offset 8ebf"
  DEC ::TnAudioRam+$1c,x
  .assert *=$aec2,lderror,"Original instruction offset 8ec2"
  JSR $afa3
  .assert *=$aec5,lderror,"Original instruction offset 8ec5"
  JSR $af96
  .assert *=$aec8,lderror,"Original instruction offset 8ec8"
  LDA ::TnAudioRam+$16,x
  .assert *=$aecb,lderror,"Original instruction offset 8ecb"
  LSR A
  .assert *=$aecc,lderror,"Original instruction offset 8ecc"
  .byte $b0,$03 ; BCS source$8ed1
  .assert *=$aece,lderror,"Original instruction offset 8ece"
  JMP $a925
  .assert *=$aed1,lderror,"Original instruction offset 8ed1"
  JMP $a9cd
  .assert *=$aed4,lderror,"Original instruction offset 8ed4"
  LDA #$00
  .assert *=$aed6,lderror,"Original instruction offset 8ed6"
  STA ::TnAudioRam+$1c,x
  .assert *=$aed9,lderror,"Original instruction offset 8ed9"
  INY
  .assert *=$aeda,lderror,"Original instruction offset 8eda"
  TYA
  .assert *=$aedb,lderror,"Original instruction offset 8edb"
  CLC
  .assert *=$aedc,lderror,"Original instruction offset 8edc"
  ADC ::TnAudioZp+$00
  .assert *=$aede,lderror,"Original instruction offset 8ede"
  STA ::TnAudioZp+$00
  .assert *=$aee0,lderror,"Original instruction offset 8ee0"
  LDA #$00
  .assert *=$aee2,lderror,"Original instruction offset 8ee2"
  TAY
  .assert *=$aee3,lderror,"Original instruction offset 8ee3"
  ADC ::TnAudioZp+$01
  .assert *=$aee5,lderror,"Original instruction offset 8ee5"
  STA ::TnAudioZp+$01
  .assert *=$aee7,lderror,"Original instruction offset 8ee7"
  JMP $aec8
  .assert *=$aeea,lderror,"Original instruction offset 8eea"
  LDA ::TnAudioRam+$2e,x
  .assert *=$aeed,lderror,"Original instruction offset 8eed"
  STA ::TnAudioRam+$22,x
  .assert *=$aef0,lderror,"Original instruction offset 8ef0"
  LDA ::TnAudioRam+$34,x
  .assert *=$aef3,lderror,"Original instruction offset 8ef3"
  STA ::TnAudioRam+$28,x
  .assert *=$aef6,lderror,"Original instruction offset 8ef6"
  JMP $aec5
  .assert *=$aef9,lderror,"Original instruction offset 8ef9"
  LDA ::TnAudioRam+$3a,x
  .assert *=$aefc,lderror,"Original instruction offset 8efc"
  STA ::TnAudioZp+$00
  .assert *=$aefe,lderror,"Original instruction offset 8efe"
  LDA ::TnAudioRam+$40,x
  .assert *=$af01,lderror,"Original instruction offset 8f01"
  STA ::TnAudioZp+$01
  .assert *=$af03,lderror,"Original instruction offset 8f03"
  LDA ::TnAudioRam+$16,x
  .assert *=$af06,lderror,"Original instruction offset 8f06"
  AND #$f7
  .assert *=$af08,lderror,"Original instruction offset 8f08"
  STA ::TnAudioRam+$16,x
  .assert *=$af0b,lderror,"Original instruction offset 8f0b"
  LDY #$00
  .assert *=$af0d,lderror,"Original instruction offset 8f0d"
  JMP $aec8
  .assert *=$af10,lderror,"Original instruction offset 8f10"
  LDA ::TnAudioRam+$16,x
  .assert *=$af13,lderror,"Original instruction offset 8f13"
  AND #$08
  .assert *=$af15,lderror,"Original instruction offset 8f15"
  .byte $f0,$03 ; BEQ source$8f1a
  .assert *=$af17,lderror,"Original instruction offset 8f17"
  JMP $aef9
  .assert *=$af1a,lderror,"Original instruction offset 8f1a"
  LDA ::TnAudioRam+$0a,x
  .assert *=$af1d,lderror,"Original instruction offset 8f1d"
  STA ::TnAudioZp+$04
  .assert *=$af1f,lderror,"Original instruction offset 8f1f"
  LDA #$00
  .assert *=$af21,lderror,"Original instruction offset 8f21"
  STA ::TnAudioRam+$0a,x
  .assert *=$af24,lderror,"Original instruction offset 8f24"
  TXA
  .assert *=$af25,lderror,"Original instruction offset 8f25"
  ASL A
  .assert *=$af26,lderror,"Original instruction offset 8f26"
  TAX
  .assert *=$af27,lderror,"Original instruction offset 8f27"
  LDA $afb8,x
  .assert *=$af2a,lderror,"Original instruction offset 8f2a"
  STA ::TnAudioZp+$02
  .assert *=$af2c,lderror,"Original instruction offset 8f2c"
  LDA $afb9,x
  .assert *=$af2f,lderror,"Original instruction offset 8f2f"
  STA ::TnAudioZp+$03
  .assert *=$af31,lderror,"Original instruction offset 8f31"
  LDX ::TnAudioRam+$92
  .assert *=$af34,lderror,"Original instruction offset 8f34"
  JMP (::TnAudioZp+$02)
  .assert *=$af37,lderror,"Original instruction offset 8f37"
  LDA #$30
  .assert *=$af39,lderror,"Original instruction offset 8f39"
  JSR $ace8
  .assert *=$af3c,lderror,"Original instruction offset 8f3c"
  .byte $b0,$03 ; BCS source$8f41
  .assert *=$af3e,lderror,"Original instruction offset 8f3e"
  .if ::TN_RAW_APU
  STA $4000,x
.else
  jsr ::TnSourceSTA00X
.endif
  .assert *=$af41,lderror,"Original instruction offset 8f41"
  LDX ::TnAudioRam+$92
  .assert *=$af44,lderror,"Original instruction offset 8f44"
  RTS
  .assert *=$af45,lderror,"Original instruction offset 8f45"
  LDA #$0b
  .assert *=$af47,lderror,"Original instruction offset 8f47"
  .if ::TN_RAW_APU
  STA $4015
.else
  jsr ::TnSourceSTA15
.endif
  .assert *=$af4a,lderror,"Original instruction offset 8f4a"
  LDA #$00
  .assert *=$af4c,lderror,"Original instruction offset 8f4c"
  .if ::TN_RAW_APU
  STA $4008
.else
  jsr ::TnSourceSTA08
.endif
  .assert *=$af4f,lderror,"Original instruction offset 8f4f"
  LDA #$0f
  .assert *=$af51,lderror,"Original instruction offset 8f51"
  .if ::TN_RAW_APU
  STA $4015
.else
  jsr ::TnSourceSTA15
.endif
  .assert *=$af54,lderror,"Original instruction offset 8f54"
  RTS
  .byte $ae,$93,$01,$a9,$30,$9d,$00,$40,$a9,$7f,$9d,$01,$40,$bd,$0a,$01,$f0,$06,$ac,$93,$01,$20,$f3,$85
  .byte $ae,$92,$01,$60
  .assert *=$af71,lderror,"Original instruction offset 8f71"
  LDA #$30
  .assert *=$af73,lderror,"Original instruction offset 8f73"
  .if ::TN_RAW_APU
  STA $400c
.else
  jsr ::TnSourceSTA0C
.endif
  .assert *=$af76,lderror,"Original instruction offset 8f76"
  LDA ::TnAudioZp+$04
  .assert *=$af78,lderror,"Original instruction offset 8f78"
  CMP #$83
  .assert *=$af7a,lderror,"Original instruction offset 8f7a"
  .byte $f0,$04 ; BEQ source$8f80
  .assert *=$af7c,lderror,"Original instruction offset 8f7c"
  CMP #$7f
  .assert *=$af7e,lderror,"Original instruction offset 8f7e"
  .byte $d0,$15 ; BNE source$8f95
  .assert *=$af80,lderror,"Original instruction offset 8f80"
  LDA #$ff
  .assert *=$af82,lderror,"Original instruction offset 8f82"
  STA ::TnAudioRam+$9d
  .assert *=$af85,lderror,"Original instruction offset 8f85"
  RTS
  .assert *=$af86,lderror,"Original instruction offset 8f86"
  INY
  .assert *=$af87,lderror,"Original instruction offset 8f87"
  TYA
  .assert *=$af88,lderror,"Original instruction offset 8f88"
  CLC
  .assert *=$af89,lderror,"Original instruction offset 8f89"
  ADC ::TnAudioZp+$00
  .assert *=$af8b,lderror,"Original instruction offset 8f8b"
  STA ::TnAudioRam+$22,x
  .assert *=$af8e,lderror,"Original instruction offset 8f8e"
  LDA #$00
  .assert *=$af90,lderror,"Original instruction offset 8f90"
  ADC ::TnAudioZp+$01
  .assert *=$af92,lderror,"Original instruction offset 8f92"
  STA ::TnAudioRam+$28,x
  .assert *=$af95,lderror,"Original instruction offset 8f95"
  RTS
  .assert *=$af96,lderror,"Original instruction offset 8f96"
  LDY #$00
  .assert *=$af98,lderror,"Original instruction offset 8f98"
  LDA ::TnAudioRam+$22,x
  .assert *=$af9b,lderror,"Original instruction offset 8f9b"
  STA ::TnAudioZp+$00
  .assert *=$af9d,lderror,"Original instruction offset 8f9d"
  LDA ::TnAudioRam+$28,x
  .assert *=$afa0,lderror,"Original instruction offset 8fa0"
  STA ::TnAudioZp+$01
  .assert *=$afa2,lderror,"Original instruction offset 8fa2"
  RTS
  .assert *=$afa3,lderror,"Original instruction offset 8fa3"
  INY
  .assert *=$afa4,lderror,"Original instruction offset 8fa4"
  LDA (::TnAudioZp+$00),y
  .assert *=$afa6,lderror,"Original instruction offset 8fa6"
  STA ::TnAudioRam+$22,x
  .assert *=$afa9,lderror,"Original instruction offset 8fa9"
  INY
  .assert *=$afaa,lderror,"Original instruction offset 8faa"
  LDA (::TnAudioZp+$00),y
  .assert *=$afac,lderror,"Original instruction offset 8fac"
  STA ::TnAudioRam+$28,x
  .assert *=$afaf,lderror,"Original instruction offset 8faf"
  RTS
  .word $a6f3 ; source pointer$8fb0
  .word $a795 ; source pointer$8fb2
  .word $a7a9 ; source pointer$8fb4
  .word $a7fa ; source pointer$8fb6
  .word $af37 ; source pointer$8fb8
  .word $af37 ; source pointer$8fba
  .word $af45 ; source pointer$8fbc
  .word $af71 ; source pointer$8fbe
  .byte $55,$8f
  .word $af37 ; source pointer$8fc2
  .word $acfb ; source pointer$8fc4
  .word $ad22 ; source pointer$8fc6
  .word $ad70 ; source pointer$8fc8
  .word $ae66 ; source pointer$8fca
  .byte $5c,$0d,$9c,$0c,$e8,$0b,$3c,$0b,$9c,$0a,$02,$0a,$72,$09,$ec,$08,$6c,$08,$f2,$07,$80,$07,$14,$07
  .byte $ae,$06,$4e,$06,$f4,$05,$9e,$05,$4e,$05,$01,$05,$b9,$04,$76,$04,$36,$04,$f9,$03,$c0,$03,$8a,$03
  .byte $57,$03,$27,$03,$fa,$02,$cf,$02,$a7,$02,$81,$02,$5d,$02,$3b,$02,$1b,$02,$fd,$01,$e0,$01,$c5,$01
  .word $b18b ; source pointer$9014
  .assert *=$b016,lderror,"Original instruction offset 9016"
  LDA ::TnAudioRam+$0d
  .assert *=$b019,lderror,"Original instruction offset 9019"
  CMP #$83
  .assert *=$b01b,lderror,"Original instruction offset 901b"
  .byte $d0,$01 ; BNE source$901e
  .assert *=$b01d,lderror,"Original instruction offset 901d"
  RTS
  .assert *=$b01e,lderror,"Original instruction offset 901e"
  STX ::TnAudioZp+$02
  .assert *=$b020,lderror,"Original instruction offset 9020"
  STY ::TnAudioZp+$03
  .assert *=$b022,lderror,"Original instruction offset 9022"
  LDA #$00
  .assert *=$b024,lderror,"Original instruction offset 9024"
  TAY
  .assert *=$b025,lderror,"Original instruction offset 9025"
  STA ::TnAudioRam+$0a,y
  .assert *=$b028,lderror,"Original instruction offset 9028"
  INY
  .assert *=$b029,lderror,"Original instruction offset 9029"
  CPY #$06
  .assert *=$b02b,lderror,"Original instruction offset 902b"
  .byte $90,$f8 ; BCC source$9025
  .assert *=$b02d,lderror,"Original instruction offset 902d"
  STA ::TnAudioRam+$80
  .assert *=$b030,lderror,"Original instruction offset 9030"
  STA ::TnAudioRam+$81
  .assert *=$b033,lderror,"Original instruction offset 9033"
  STA ::TnAudioRam+$98
  .assert *=$b036,lderror,"Original instruction offset 9036"
  STA ::TnAudioRam+$99
  .assert *=$b039,lderror,"Original instruction offset 9039"
  STA ::TnAudioRam+$97
  .assert *=$b03c,lderror,"Original instruction offset 903c"
  LDX ::TnAudioZp+$02
  .assert *=$b03e,lderror,"Original instruction offset 903e"
  LDY ::TnAudioZp+$03
  .assert *=$b040,lderror,"Original instruction offset 9040"
  JSR $af45
  .assert *=$b043,lderror,"Original instruction offset 9043"
  LDA #$30
  .assert *=$b045,lderror,"Original instruction offset 9045"
  .if ::TN_RAW_APU
  STA $4000
.else
  jsr ::TnSourceSTA00
.endif
  .assert *=$b048,lderror,"Original instruction offset 9048"
  .if ::TN_RAW_APU
  STA $4004
.else
  jsr ::TnSourceSTA04
.endif
  .assert *=$b04b,lderror,"Original instruction offset 904b"
  .if ::TN_RAW_APU
  STA $400c
.else
  jsr ::TnSourceSTA0C
.endif
  .assert *=$b04e,lderror,"Original instruction offset 904e"
  LDA #$7f
  .assert *=$b050,lderror,"Original instruction offset 9050"
  .if ::TN_RAW_APU
  STA $4001
.else
  jsr ::TnSourceSTA01
.endif
  .assert *=$b053,lderror,"Original instruction offset 9053"
  .if ::TN_RAW_APU
  STA $4005
.else
  jsr ::TnSourceSTA05
.endif
  .assert *=$b056,lderror,"Original instruction offset 9056"
  RTS
  .assert *=$b057,lderror,"Original instruction offset 9057"
  STA ::TnAudioRam+$94
  .assert *=$b05a,lderror,"Original instruction offset 905a"
  CMP #$8f
  .assert *=$b05c,lderror,"Original instruction offset 905c"
  .byte $90,$03 ; BCC source$9061
  .assert *=$b05e,lderror,"Original instruction offset 905e"
  JMP $a98e
  .assert *=$b061,lderror,"Original instruction offset 9061"
  CMP #$4b
  .assert *=$b063,lderror,"Original instruction offset 9063"
  .byte $90,$30 ; BCC source$9095
  .assert *=$b065,lderror,"Original instruction offset 9065"
  LDA ::TnAudioRam+$0d
  .assert *=$b068,lderror,"Original instruction offset 9068"
  CMP #$83
  .assert *=$b06a,lderror,"Original instruction offset 906a"
  .byte $d0,$01 ; BNE source$906d
  .assert *=$b06c,lderror,"Original instruction offset 906c"
  RTS
  .assert *=$b06d,lderror,"Original instruction offset 906d"
  LDA #$00
  .assert *=$b06f,lderror,"Original instruction offset 906f"
  STA ::TnAudioRam+$80
  .assert *=$b072,lderror,"Original instruction offset 9072"
  STA ::TnAudioRam+$81
  .assert *=$b075,lderror,"Original instruction offset 9075"
  LDA ::TnAudioRam+$94
  .assert *=$b078,lderror,"Original instruction offset 9078"
  CMP #$77
  .assert *=$b07a,lderror,"Original instruction offset 907a"
  .byte $f0,$07 ; BEQ source$9083
  .assert *=$b07c,lderror,"Original instruction offset 907c"
  CMP #$7f
  .assert *=$b07e,lderror,"Original instruction offset 907e"
  .byte $f0,$0e ; BEQ source$908e
  .assert *=$b080,lderror,"Original instruction offset 9080"
  JSR $b016
  .assert *=$b083,lderror,"Original instruction offset 9083"
  LDA ::TnAudioRam+$94
  .assert *=$b086,lderror,"Original instruction offset 9086"
  CMP #$83
  .assert *=$b088,lderror,"Original instruction offset 9088"
  .byte $f0,$04 ; BEQ source$908e
  .assert *=$b08a,lderror,"Original instruction offset 908a"
  CMP #$7f
  .assert *=$b08c,lderror,"Original instruction offset 908c"
  .byte $d0,$24 ; BNE source$90b2
  .assert *=$b08e,lderror,"Original instruction offset 908e"
  LDA #$00
  .assert *=$b090,lderror,"Original instruction offset 9090"
  STA ::TnAudioRam+$9d
  .assert *=$b093,lderror,"Original instruction offset 9093"
  .byte $f0,$1d ; BEQ source$90b2
  .assert *=$b095,lderror,"Original instruction offset 9095"
  CMP #$16
  .assert *=$b097,lderror,"Original instruction offset 9097"
  .byte $d0,$06 ; BNE source$909f
  .assert *=$b099,lderror,"Original instruction offset 9099"
  CMP ::TnAudioRam+$0f
  .assert *=$b09c,lderror,"Original instruction offset 909c"
  .byte $d0,$01 ; BNE source$909f
  .assert *=$b09e,lderror,"Original instruction offset 909e"
  RTS
  .assert *=$b09f,lderror,"Original instruction offset 909f"
  LDA ::TnAudioRam+$0b
  .assert *=$b0a2,lderror,"Original instruction offset 90a2"
  CMP #$77
  .assert *=$b0a4,lderror,"Original instruction offset 90a4"
  .byte $d0,$0c ; BNE source$90b2
  .assert *=$b0a6,lderror,"Original instruction offset 90a6"
  LDA ::TnAudioRam+$94
  .assert *=$b0a9,lderror,"Original instruction offset 90a9"
  CMP #$07
  .assert *=$b0ab,lderror,"Original instruction offset 90ab"
  .byte $90,$05 ; BCC source$90b2
  .assert *=$b0ad,lderror,"Original instruction offset 90ad"
  CMP #$3e
  .assert *=$b0af,lderror,"Original instruction offset 90af"
  .byte $b0,$01 ; BCS source$90b2
  .assert *=$b0b1,lderror,"Original instruction offset 90b1"
  RTS
  .assert *=$b0b2,lderror,"Original instruction offset 90b2"
  TXA
  .assert *=$b0b3,lderror,"Original instruction offset 90b3"
  PHA
  .assert *=$b0b4,lderror,"Original instruction offset 90b4"
  TYA
  .assert *=$b0b5,lderror,"Original instruction offset 90b5"
  PHA
  .assert *=$b0b6,lderror,"Original instruction offset 90b6"
  LDA $b014
  .assert *=$b0b9,lderror,"Original instruction offset 90b9"
  STA ::TnAudioZp+$08
  .assert *=$b0bb,lderror,"Original instruction offset 90bb"
  LDA $b015
  .assert *=$b0be,lderror,"Original instruction offset 90be"
  STA ::TnAudioZp+$09
  .assert *=$b0c0,lderror,"Original instruction offset 90c0"
  LDA #$03
  .assert *=$b0c2,lderror,"Original instruction offset 90c2"
  STA ::TnAudioZp+$0a
  .assert *=$b0c4,lderror,"Original instruction offset 90c4"
  LDA ::TnAudioRam+$94
  .assert *=$b0c7,lderror,"Original instruction offset 90c7"
  CLC
  .assert *=$b0c8,lderror,"Original instruction offset 90c8"
  ADC ::TnAudioZp+$08
  .assert *=$b0ca,lderror,"Original instruction offset 90ca"
  STA ::TnAudioZp+$08
  .assert *=$b0cc,lderror,"Original instruction offset 90cc"
  LDA #$00
  .assert *=$b0ce,lderror,"Original instruction offset 90ce"
  ADC ::TnAudioZp+$09
  .assert *=$b0d0,lderror,"Original instruction offset 90d0"
  STA ::TnAudioZp+$09
  .assert *=$b0d2,lderror,"Original instruction offset 90d2"
  DEC ::TnAudioZp+$0a
  .assert *=$b0d4,lderror,"Original instruction offset 90d4"
  .byte $d0,$ee ; BNE source$90c4
  .assert *=$b0d6,lderror,"Original instruction offset 90d6"
  LDY #$00
  .assert *=$b0d8,lderror,"Original instruction offset 90d8"
  STY ::TnAudioZp+$0b
  .assert *=$b0da,lderror,"Original instruction offset 90da"
  LDA (::TnAudioZp+$08),y
  .assert *=$b0dc,lderror,"Original instruction offset 90dc"
  LSR A
  .assert *=$b0dd,lderror,"Original instruction offset 90dd"
  LSR A
  .assert *=$b0de,lderror,"Original instruction offset 90de"
  LSR A
  .assert *=$b0df,lderror,"Original instruction offset 90df"
  AND #$03
  .assert *=$b0e1,lderror,"Original instruction offset 90e1"
  STA ::TnAudioZp+$0a
  .assert *=$b0e3,lderror,"Original instruction offset 90e3"
  LDA ::TnAudioZp+$0b
  .assert *=$b0e5,lderror,"Original instruction offset 90e5"
  ASL A
  .assert *=$b0e6,lderror,"Original instruction offset 90e6"
  CLC
  .assert *=$b0e7,lderror,"Original instruction offset 90e7"
  ADC ::TnAudioZp+$0b
  .assert *=$b0e9,lderror,"Original instruction offset 90e9"
  TAY
  .assert *=$b0ea,lderror,"Original instruction offset 90ea"
  LDA (::TnAudioZp+$08),y
  .assert *=$b0ec,lderror,"Original instruction offset 90ec"
  AND #$07
  .assert *=$b0ee,lderror,"Original instruction offset 90ee"
  TAX
  .assert *=$b0ef,lderror,"Original instruction offset 90ef"
  LDA ::TnAudioRam+$94
  .assert *=$b0f2,lderror,"Original instruction offset 90f2"
  CMP ::TnAudioRam+$0a,x
  .assert *=$b0f5,lderror,"Original instruction offset 90f5"
  .byte $b0,$03 ; BCS source$90fa
  .assert *=$b0f7,lderror,"Original instruction offset 90f7"
  JMP $b174
  .assert *=$b0fa,lderror,"Original instruction offset 90fa"
  LDA #$00
  .assert *=$b0fc,lderror,"Original instruction offset 90fc"
  STA ::TnAudioRam+$0a,x
  .assert *=$b0ff,lderror,"Original instruction offset 90ff"
  INY
  .assert *=$b100,lderror,"Original instruction offset 9100"
  LDA (::TnAudioZp+$08),y
  .assert *=$b102,lderror,"Original instruction offset 9102"
  STA ::TnAudioRam+$22,x
  .assert *=$b105,lderror,"Original instruction offset 9105"
  STA ::TnAudioZp+$06
  .assert *=$b107,lderror,"Original instruction offset 9107"
  INY
  .assert *=$b108,lderror,"Original instruction offset 9108"
  LDA (::TnAudioZp+$08),y
  .assert *=$b10a,lderror,"Original instruction offset 910a"
  STA ::TnAudioRam+$28,x
  .assert *=$b10d,lderror,"Original instruction offset 910d"
  STA ::TnAudioZp+$07
  .assert *=$b10f,lderror,"Original instruction offset 910f"
  LDA #$f8
  .assert *=$b111,lderror,"Original instruction offset 9111"
  STA ::TnAudioRam+$46,x
  .assert *=$b114,lderror,"Original instruction offset 9114"
  LDA #$01
  .assert *=$b116,lderror,"Original instruction offset 9116"
  STA ::TnAudioRam+$04,x
  .assert *=$b119,lderror,"Original instruction offset 9119"
  CPX #$03
  .assert *=$b11b,lderror,"Original instruction offset 911b"
  .byte $b0,$16 ; BCS source$9133
  .assert *=$b11d,lderror,"Original instruction offset 911d"
  CPX #$02
  .assert *=$b11f,lderror,"Original instruction offset 911f"
  .byte $f0,$0d ; BEQ source$912e
  .assert *=$b121,lderror,"Original instruction offset 9121"
  LDA #$00
  .assert *=$b123,lderror,"Original instruction offset 9123"
  STA ::TnAudioRam+$76,x
  .assert *=$b126,lderror,"Original instruction offset 9126"
  STA ::TnAudioRam+$8c,x
  .assert *=$b129,lderror,"Original instruction offset 9129"
  LDA #$80
  .assert *=$b12b,lderror,"Original instruction offset 912b"
  STA ::TnAudioRam+$8e,x
  .assert *=$b12e,lderror,"Original instruction offset 912e"
  LDA #$00
  .assert *=$b130,lderror,"Original instruction offset 9130"
  STA ::TnAudioRam+$61,x
  .assert *=$b133,lderror,"Original instruction offset 9133"
  LDA #$00
  .assert *=$b135,lderror,"Original instruction offset 9135"
  STA ::TnAudioRam+$1c,x
  .assert *=$b138,lderror,"Original instruction offset 9138"
  TAY
  .assert *=$b139,lderror,"Original instruction offset 9139"
  LDA (::TnAudioZp+$06),y
  .assert *=$b13b,lderror,"Original instruction offset 913b"
  INY
  .assert *=$b13c,lderror,"Original instruction offset 913c"
  CMP #$30
  .assert *=$b13e,lderror,"Original instruction offset 913e"
  .byte $90,$07 ; BCC source$9147
  .assert *=$b140,lderror,"Original instruction offset 9140"
  DEY
  .assert *=$b141,lderror,"Original instruction offset 9141"
  STY ::TnAudioRam+$98
  .assert *=$b144,lderror,"Original instruction offset 9144"
  STY ::TnAudioRam+$97
  .assert *=$b147,lderror,"Original instruction offset 9147"
  TYA
  .assert *=$b148,lderror,"Original instruction offset 9148"
  STA ::TnAudioRam+$16,x
  .assert *=$b14b,lderror,"Original instruction offset 914b"
  LDA ::TnAudioRam+$94
  .assert *=$b14e,lderror,"Original instruction offset 914e"
  STA ::TnAudioRam+$0a,x
  .assert *=$b151,lderror,"Original instruction offset 9151"
  TXA
  .assert *=$b152,lderror,"Original instruction offset 9152"
  CMP #$01
  .assert *=$b154,lderror,"Original instruction offset 9154"
  .byte $90,$2c ; BCC source$9182
  .assert *=$b156,lderror,"Original instruction offset 9156"
  CPX #$05
  .assert *=$b158,lderror,"Original instruction offset 9158"
  .byte $d0,$05 ; BNE source$915f
  .assert *=$b15a,lderror,"Original instruction offset 915a"
  LDA #$0c
  .assert *=$b15c,lderror,"Original instruction offset 915c"
  JMP $b163
  .assert *=$b15f,lderror,"Original instruction offset 915f"
  ASL A
  .assert *=$b160,lderror,"Original instruction offset 9160"
  ASL A
  .assert *=$b161,lderror,"Original instruction offset 9161"
  AND #$0f
  .assert *=$b163,lderror,"Original instruction offset 9163"
  TAX
  .assert *=$b164,lderror,"Original instruction offset 9164"
  LDA #$00
  .assert *=$b166,lderror,"Original instruction offset 9166"
  CPX #$08
  .assert *=$b168,lderror,"Original instruction offset 9168"
  .byte $f0,$02 ; BEQ source$916c
  .assert *=$b16a,lderror,"Original instruction offset 916a"
  LDA #$30
  .assert *=$b16c,lderror,"Original instruction offset 916c"
  .if ::TN_RAW_APU
  STA $4000,x
.else
  jsr ::TnSourceSTA00X
.endif
  .assert *=$b16f,lderror,"Original instruction offset 916f"
  LDA #$7f
  .assert *=$b171,lderror,"Original instruction offset 9171"
  .if ::TN_RAW_APU
  STA $4001,x
.else
  jsr ::TnSourceSTA01X
.endif
  .assert *=$b174,lderror,"Original instruction offset 9174"
  INC ::TnAudioZp+$0b
  .assert *=$b176,lderror,"Original instruction offset 9176"
  DEC ::TnAudioZp+$0a
  .assert *=$b178,lderror,"Original instruction offset 9178"
  .byte $10,$05 ; BPL source$917f
  .assert *=$b17a,lderror,"Original instruction offset 917a"
  PLA
  .assert *=$b17b,lderror,"Original instruction offset 917b"
  TAY
  .assert *=$b17c,lderror,"Original instruction offset 917c"
  PLA
  .assert *=$b17d,lderror,"Original instruction offset 917d"
  TAX
  .assert *=$b17e,lderror,"Original instruction offset 917e"
  RTS
  .assert *=$b17f,lderror,"Original instruction offset 917f"
  JMP $b0e3
  .assert *=$b182,lderror,"Original instruction offset 9182"
  ORA #$04
  .assert *=$b184,lderror,"Original instruction offset 9184"
  TAY
  .assert *=$b185,lderror,"Original instruction offset 9185"
  LDA ::TnAudioRam+$0a,y
  .assert *=$b188,lderror,"Original instruction offset 9188"
  .byte $d0,$ea ; BNE source$9174
  .assert *=$b18a,lderror,"Original instruction offset 918a"
  TXA
  .assert *=$b18b,lderror,"Original instruction offset 918b"
  JMP $b15f
  .byte $05,$3e,$93,$05,$3b,$93,$05
  .word $b33f ; source pointer$9195
  .byte $05
  .word $b345 ; source pointer$9198
  .byte $05
  .word $b357 ; source pointer$919b
  .byte $05
  .word $b35e ; source pointer$919e
  .byte $04,$6b,$93,$0c,$80,$93,$05,$92,$93,$0c,$99,$93,$05,$a8,$93,$0c,$b7,$93,$05,$c3,$93,$0c,$b7,$93
  .byte $05,$d1,$93,$0c,$e7,$93,$05,$f7,$93,$0c,$e2,$93,$05,$f5,$93,$0c,$00,$94,$05,$10,$94,$05,$15,$94
  .byte $0c,$27,$94,$05,$34,$94,$0c,$5c,$94,$05,$6f,$94,$05,$87,$94,$0c,$97,$94,$05,$aa,$94,$0c,$d2,$94
  .byte $05,$ea,$94,$04,$fc,$94,$04,$0c,$95,$0c,$28,$95,$05,$45,$95,$04,$a6,$95,$0c,$59,$95,$05,$8e,$95
  .byte $05,$91,$95,$05,$ae,$95,$04,$ce,$95,$0c,$36,$96,$05,$61,$96,$05,$79,$96,$0c,$8f,$96,$05,$ae,$96
  .byte $0c,$bd,$96,$05,$cc,$96,$04,$e0,$96,$04,$b0,$94,$04,$e1,$96,$04,$16,$97,$04,$32,$97,$0c,$4a,$97
  .byte $05,$52,$97,$05,$52,$97,$04,$59,$97,$0c,$63,$97,$05,$8d,$97,$04,$bc,$97,$04,$cc,$97,$04,$9f,$97
  .byte $0c,$fa,$97,$05,$09,$98,$04,$23,$98,$0c,$65,$98,$05,$8f,$98,$04,$b5,$98,$04,$b5,$98,$0c,$46,$99
  .byte $05,$b7,$99,$14,$f7,$98,$01,$ec,$98,$05,$23,$99,$14,$1b,$9a,$01,$16,$9a,$05,$4d,$9a,$18
  .word $ba65 ; source pointer$9276
  .byte $01
  .word $bd18 ; source pointer$9279
  .byte $02
  .word $a429 ; source pointer$927c
  .byte $03
  .word $c09a ; source pointer$927f
  .byte $03,$2d,$a1,$18
  .word $c134 ; source pointer$9285
  .byte $01
  .word $c211 ; source pointer$9288
  .byte $02
  .word $c2e0 ; source pointer$928b
  .byte $03
  .word $c358 ; source pointer$928e
  .byte $18
  .word $c3a1 ; source pointer$9291
  .byte $01
  .word $c4ab ; source pointer$9294
  .byte $02
  .word $c5ab ; source pointer$9297
  .byte $03
  .word $c68a ; source pointer$929a
  .byte $18
  .word $c6cc ; source pointer$929d
  .byte $01
  .word $c7a3 ; source pointer$92a0
  .byte $02
  .word $c899 ; source pointer$92a3
  .byte $03
  .word $c948 ; source pointer$92a6
  .byte $18
  .word $c99e ; source pointer$92a9
  .byte $01
  .word $ca9c ; source pointer$92ac
  .byte $02
  .word $cb81 ; source pointer$92af
  .byte $03
  .word $cbff ; source pointer$92b2
  .byte $18
  .word $cc5d ; source pointer$92b5
  .byte $01
  .word $cc86 ; source pointer$92b8
  .byte $02
  .word $cc97 ; source pointer$92bb
  .byte $03
  .word $ccdd ; source pointer$92be
  .byte $18
  .word $cd00 ; source pointer$92c1
  .byte $01
  .word $cd0d ; source pointer$92c4
  .byte $02
  .word $cd1c ; source pointer$92c7
  .byte $03
  .word $cd25 ; source pointer$92ca
  .byte $18
  .word $cd2d ; source pointer$92cd
  .byte $01
  .word $ce1d ; source pointer$92d0
  .byte $02
  .word $cf0a ; source pointer$92d3
  .byte $03
  .word $cfbc ; source pointer$92d6
  .byte $18
  .word $d01b ; source pointer$92d9
  .byte $01
  .word $d165 ; source pointer$92dc
  .byte $02
  .word $d266 ; source pointer$92df
  .byte $03
  .word $d327 ; source pointer$92e2
  .byte $18
  .word $d3a0 ; source pointer$92e5
  .byte $01
  .word $d46c ; source pointer$92e8
  .byte $02
  .word $d541 ; source pointer$92eb
  .byte $03
  .word $d5da ; source pointer$92ee
  .byte $18
  .word $d635 ; source pointer$92f1
  .byte $01
  .word $d672 ; source pointer$92f4
  .byte $02
  .word $d6a9 ; source pointer$92f7
  .byte $03
  .word $d6c9 ; source pointer$92fa
  .byte $18
  .word $d6d2 ; source pointer$92fd
  .byte $01
  .word $d787 ; source pointer$9300
  .byte $02
  .word $d84f ; source pointer$9303
  .byte $03
  .word $d8f8 ; source pointer$9306
  .byte $18
  .word $d9e9 ; source pointer$9309
  .byte $01
  .word $da2c ; source pointer$930c
  .byte $02
  .word $da73 ; source pointer$930f
  .byte $03
  .word $da98 ; source pointer$9312
  .byte $18
  .word $d959 ; source pointer$9315
  .byte $01
  .word $d9a3 ; source pointer$9318
  .byte $02
  .word $d9bf ; source pointer$931b
  .byte $03
  .word $d9d3 ; source pointer$931e
  .byte $18
  .word $dabb ; source pointer$9321
  .byte $01
  .word $dc51 ; source pointer$9324
  .byte $02
  .word $dd1e ; source pointer$9327
  .byte $03
  .word $dd9f ; source pointer$932a
  .byte $18
  .word $ddee ; source pointer$932d
  .byte $01
  .word $de34 ; source pointer$9330
  .byte $02
  .word $de73 ; source pointer$9333
  .byte $03
  .word $de96 ; source pointer$9336
  .byte $06,$41,$fe,$01,$00,$f2,$ff,$01,$65,$24,$21,$11,$ff,$01,$a2,$a1,$71,$61,$61,$50,$51,$50,$51,$50
  .byte $41,$30,$20,$20,$06,$10,$ff,$01,$b6,$96,$76,$54,$36,$ff,$01,$ee,$76,$34,$43,$24,$13,$12,$12,$10
  .byte $10,$10,$ff,$04,$b0,$9c,$51,$40,$70,$fe,$50,$a9,$f8,$01,$00,$00,$05,$b0,$8c,$30,$a0,$10,$a0,$ff
  .byte $01,$b0,$88,$30,$20,$00,$00,$00,$00,$f8,$02,$40,$10,$20,$10,$10,$10,$ff,$01,$9b,$03,$00,$02,$96
  .byte $ff,$06,$b0,$8b,$32,$3b,$0a,$70,$dc,$40,$13,$f8,$06,$30,$11,$ff,$01,$b2,$bc,$ba,$02,$bd,$ba,$b7
  .byte $a6,$95,$84,$73,$72,$71,$ff,$03,$b0,$85,$30,$0f,$30,$1b,$20,$2a,$20,$1e,$ff,$01,$8a,$8e,$8c,$89
  .byte $87,$86,$8c,$7d,$7f,$83,$8e,$8c,$ff,$02,$9e,$9d,$9a,$9e,$98,$6a,$59,$69,$5c,$7d,$01,$6f,$6a,$6e
  .byte $7f,$ff,$07,$b0,$83,$10,$00,$03,$b0,$83,$80,$d5,$80,$fe,$71,$94,$51,$a6,$51,$ae,$ff,$07,$10,$02
  .byte $8c,$99,$7a,$04,$8a,$8c,$8e,$ff,$06,$30,$8c,$50,$40,$90,$20,$f8,$01,$00,$00,$f8,$06,$10,$20,$ff
  .byte $02,$f5,$f3,$f1,$ff,$01,$5a,$79,$97,$b7,$d8,$98,$78,$79,$7a,$5a,$5a,$5b,$3d,$3d,$3a,$1d,$ff,$04
  .byte $b0,$8b,$43,$66,$0c,$70,$8b,$32,$66,$12,$66,$ff,$01,$00,$ed,$ec,$eb,$ea,$e9,$e8,$e7,$e6,$e5,$e4
  .byte $03,$00,$01,$5d,$5c,$5b,$5a,$59,$58,$57,$56,$55,$54,$53,$52,$2d,$2c,$2b,$2a,$29,$28,$27,$26,$25
  .byte $24,$23,$22,$ff,$03,$b0,$83,$fb,$00,$00,$50,$a6,$40,$cd,$31,$64,$21,$76,$11,$7f,$fe,$05,$ff,$01
  .byte $fb,$3a,$59,$97,$87,$68,$01,$58,$48,$49,$4a,$3a,$3a,$3b,$2d,$2d,$2a,$1b,$1d,$1d,$fe,$05,$ff,$02
  .byte $fb,$01,$d4,$54,$02,$d4,$54,$fe,$02,$94,$54,$33,$23,$12,$ff,$03,$30,$88,$70,$12,$70,$16,$70,$20
  .byte $70,$17,$02,$b0,$88,$30,$12,$10,$11,$ff,$03,$b8,$98,$55,$34,$ff,$02,$b0,$88,$80,$fe,$80,$d4,$80
  .byte $9c,$80,$7f,$80,$6a,$50,$fe,$50,$d4,$50,$9c,$50,$7f,$50,$6a,$30,$fe,$30,$d4,$20,$9c,$20,$7f,$20
  .byte $6a,$ff,$05,$f0,$9a,$10,$00,$f8,$02,$82,$55,$f8,$03,$10,$00,$41,$aa,$10,$00,$32,$21,$10,$00,$12
  .byte $21,$ff,$05,$10,$01,$e6,$10,$de,$10,$04,$4a,$3b,$2c,$01,$10,$04,$19,$1a,$1b,$ff,$01,$30,$83,$c1
  .byte $ae,$91,$58,$80,$80,$10,$00,$f8,$14,$80,$2a,$ff,$01,$70,$88,$10,$00,$04,$70,$82,$c0,$fe,$05,$30
  .byte $82,$b0,$2a,$90,$2b,$70,$2a,$50,$2b,$30,$2a,$20,$2b,$10,$2a,$ff,$02,$70,$82,$a0,$20,$01,$30,$8a
  .byte $71,$40,$01,$30,$8a,$92,$a0,$09,$b0,$8a,$52,$a0,$f8,$0a,$32,$a0,$22,$a0,$12,$a0,$ff,$01,$7d,$02
  .byte $00,$01,$97,$02,$b3,$03,$00,$77,$00,$57,$00,$37,$00,$27,$00,$17,$ff,$01,$30,$83,$f3,$34,$f3,$58
  .byte $f3,$84,$b3,$fb,$b4,$54,$94,$ef,$95,$35,$35,$a4,$73,$34,$73,$58,$53,$84,$33,$a6,$02,$30,$89,$73
  .byte $34,$73,$46,$93,$4f,$93,$58,$b3,$64,$73,$84,$53,$91,$43,$fb,$34,$03,$24,$13,$14,$25,$ff,$01,$7c
  .byte $ff,$02,$ea,$df,$cb,$ba,$a8,$00,$9a,$8b,$00,$7a,$68,$5a,$00,$48,$35,$2f,$00,$1a,$18,$ff,$0f,$b0
  .byte $a5,$f8,$30,$60,$22,$ff,$01,$fb,$ee,$ef,$fe,$02,$02,$ef,$e8,$ef,$e8,$ef,$ec,$eb,$eb,$eb,$db,$cb
  .byte $bd,$ac,$9b,$8b,$ab,$6b,$5b,$03,$4b,$3b,$2c,$1c,$1b,$ff,$02,$b0,$88,$70,$35,$80,$36,$90,$37,$a0
  .byte $38,$b0,$39,$b0,$3a,$b0,$3b,$b0,$3c,$b0,$3d,$b0,$3e,$b0,$3f,$b0,$40,$b0,$41,$b0,$42,$b0,$43,$b0
  .byte $44,$b0,$45,$b0,$46,$b0,$47,$b0,$48,$b0,$49,$b0,$4a,$b0,$4b,$b0,$4c,$b0,$4d,$b0,$4e,$b0,$4f,$a0
  .byte $50,$a0,$51,$90,$52,$90,$53,$80,$54,$80,$55,$70,$56,$70,$57,$60,$58,$60,$59,$50,$5a,$50,$5b,$40
  .byte $5c,$40,$5d,$30,$5e,$30,$5f,$20,$60,$20,$61,$10,$62,$10,$63,$10,$64,$10,$65,$10,$66,$ff,$01,$b0
  .byte $82,$f2,$70,$00,$00,$04,$b0,$82,$f1,$ab,$f1,$53,$e1,$ab,$d1,$53,$c1,$ab,$b1,$53,$a1,$ab,$91,$53
  .byte $81,$ab,$71,$53,$61,$ab,$51,$53,$41,$ab,$31,$53,$21,$ab,$11,$53,$ff,$01,$ec,$02,$df,$c9,$bf,$01
  .byte $b9,$cf,$03,$99,$9f,$04,$89,$7f,$69,$5f,$05,$49,$3f,$29,$1f,$19,$ff,$03,$ef,$ee,$01,$d7,$bd,$c8
  .byte $04,$c7,$c9,$a7,$a9,$97,$89,$79,$57,$49,$47,$39,$29,$17,$ff,$01,$b0,$8a,$fb,$60,$21,$60,$42,$60
  .byte $84,$fe,$07,$30,$21,$30,$42,$30,$84,$20,$21,$20,$42,$20,$84,$10,$21,$10,$42,$10,$84,$ff,$01,$77
  .byte $01,$fb,$72,$f1,$10,$77,$fe,$04,$00,$32,$00,$12,$ff,$01,$30,$a9,$fb,$f8,$01,$f1,$fe,$f8,$01,$50
  .byte $1d,$fe,$0c,$ff,$01,$f8,$5f,$58,$5f,$59,$01,$fb,$75,$fe,$14,$15,$25,$35,$45,$00,$00,$15,$15,$ff
  .byte $ff,$03,$70,$88,$fb,$d0,$3c,$50,$1d,$d0,$3c,$50,$1d,$d0,$3c,$50,$1d,$d0,$3c,$50,$1d,$d0,$3c,$d0
  .byte $3c,$f9,$30,$50,$1d,$50,$3c,$00,$00,$30,$3c,$00,$00,$20,$3c,$00,$00,$10,$3c,$f9,$70,$00,$00,$00
  .byte $00,$00,$00,$fe,$04,$ff,$05,$b0,$9c,$70,$fe,$90,$e2,$b0,$d5,$f8,$0a,$b0,$be,$90,$a9,$70,$8e,$f8
  .byte $0b,$50,$7f,$30,$7f,$20,$7f,$10,$7f,$ff,$08,$b0,$9b,$70,$d5,$90,$6a,$02,$b0,$8c,$00,$00,$08,$b0
  .byte $9b,$50,$6a,$30,$6a,$20,$6a,$10,$6a,$ff,$06,$30,$99,$50,$b0,$10,$b0,$ff,$01,$c7,$82,$77,$42,$12
  .byte $ff,$03,$b0,$88,$50,$35,$20,$1d,$10,$35,$ff,$03,$70,$88,$b0,$12,$b0,$16,$b0,$20,$b0,$17,$02,$30
  .byte $88,$a0,$12,$03,$b0,$88,$b0,$18,$a0,$18,$90,$18,$80,$18,$70,$18,$60,$18,$50,$18,$40,$18,$30,$18
  .byte $20,$18,$10,$18,$ff,$01,$df,$03,$d8,$b8,$95,$14,$24,$34,$54,$74,$11,$34,$11,$24,$11,$14,$ff,$05
  .byte $82,$88,$10,$d5,$10,$8e,$10,$a9,$02,$b0,$88,$e0,$6a,$d0,$6a,$b0,$6a,$a0,$6a,$90,$6a,$70,$6a,$50
  .byte $6a,$40,$6a,$ff,$05,$b0,$8c,$a0,$4d,$a0,$40,$50,$4b,$50,$3e,$30,$49,$30,$3c,$ff,$03,$70,$88,$e0
  .byte $ef,$31,$3b,$e0,$bc,$30,$ee,$e0,$9c,$30,$ba,$e0,$74,$21,$3b,$70,$bc,$20,$ef,$70,$9c,$20,$ba,$70
  .byte $74,$20,$ee,$11,$3b,$20,$bc,$10,$ee,$20,$9c,$10,$ba,$20,$74,$11,$3b,$ff,$01,$30,$a2,$d3,$8a,$53
  .byte $57,$43,$27,$33,$27,$fe,$ff,$fd,$97,$02,$fb,$7e,$5e,$fe,$13,$fb,$9e,$7e,$fe,$13,$fb,$be,$9e,$fe
  .byte $13,$fb,$ce,$ae,$fe,$13,$de,$fe,$ff,$1e,$98,$01,$70,$83,$f1,$f0,$f1,$d0,$f1,$ae,$f1,$8f,$f1,$68
  .byte $f1,$40,$f1,$2a,$f1,$0c,$01,$f0,$82,$fb,$f0,$d5,$fe,$0b,$01,$f0,$83,$e1,$10,$d1,$30,$c1,$50,$b1
  .byte $70,$a1,$90,$81,$b0,$01,$f0,$82,$fb,$30,$d5,$fe,$0b,$01,$f0,$83,$31,$10,$31,$30,$21,$50,$21,$70
  .byte $11,$90,$11,$b0,$ff,$04,$f0,$83,$f2,$34,$f9,$b0,$91,$e7,$f4,$56,$d2,$34,$61,$e7,$d4,$56,$a2,$34
  .byte $41,$e7,$a4,$56,$52,$34,$21,$e7,$54,$56,$32,$34,$11,$e7,$34,$56,$22,$34,$10,$00,$24,$56,$ff,$02
  .byte $ef,$dc,$df,$cc,$bb,$aa,$bf,$ac,$af,$9c,$8b,$7a,$8f,$7c,$7f,$6c,$5b,$4a,$5f,$4c,$4f,$3c,$2b,$1a
  .byte $3f,$2c,$2f,$2c,$1b,$1a,$2f,$2c,$1f,$1c,$1b,$1a,$ff,$06,$30,$81,$fb,$f1,$cc,$f1,$cd,$21,$24,$21
  .byte $33,$f1,$cc,$21,$35,$f1,$dd,$f1,$ee,$21,$35,$f1,$ee,$21,$3a,$fe,$02,$05,$30,$81,$fb,$f1,$fe,$21
  .byte $3a,$21,$3a,$f2,$33,$fe,$02,$f2,$36,$21,$35,$f2,$42,$21,$22,$21,$54,$f2,$52,$ff,$04,$f0,$82,$10
  .byte $00,$f8,$02,$10,$00,$ed,$05,$04,$f0,$82,$10,$00,$f8,$04,$fb,$f1,$00,$e1,$90,$a1,$ce,$10,$00,$fe
  .byte $07,$0a,$f0,$84,$e1,$44,$e1,$66,$d1,$88,$c1,$aa,$1b,$cc,$a1,$ee,$92,$11,$72,$33,$52,$55,$32,$77
  .byte $12,$99,$ff,$04,$10,$04,$fb,$ed,$ee,$dd,$10,$fe,$04,$fb,$ce,$cb,$dd,$10,$fe,$03,$04,$9b,$c9,$ec
  .byte $db,$da,$dc,$eb,$cd,$ee,$0f,$ee,$ce,$ae,$6e,$6e,$3f,$ff,$02,$b0,$81,$fb,$e1,$33,$c1,$55,$a1,$88
  .byte $a1,$dd,$a2,$00,$92,$22,$92,$03,$fe,$07,$fb,$e1,$78,$d1,$fa,$c2,$02,$b2,$25,$a2,$44,$fe,$07,$fb
  .byte $03,$b0,$83,$e2,$22,$d2,$44,$c2,$66,$01,$b0,$81,$a2,$af,$fe,$05,$fb,$03,$b0,$83,$a2,$22,$92,$44
  .byte $01,$b0,$81,$54,$a2,$34,$a3,$fe,$02,$fb,$03,$b0,$83,$a2,$22,$92,$44,$01,$b0,$82,$34,$a2,$fe,$06
  .byte $fb,$03,$b0,$83,$82,$22,$62,$44,$01,$b0,$82,$44,$a2,$fe,$06,$fb,$03,$b0,$83,$42,$22,$32,$44,$01
  .byte $b0,$82,$24,$a2,$fe,$04,$ff,$01,$fb,$ec,$ee,$ed,$ac,$9b,$9a,$9a,$8a,$8f,$9a,$9b,$8c,$9d,$ae,$fe
  .byte $07,$fb,$ee,$ee,$de,$af,$9d,$8c,$7b,$6c,$5d,$4a,$fe,$07,$fb,$8e,$8c,$8d,$7e,$7d,$7d,$6d,$5e,$5e
  .byte $4f,$fe,$05,$fb,$5c,$5d,$5d,$4d,$4d,$3e,$2e,$2f,$fe,$02,$fb,$4d,$5d,$6e,$5e,$4e,$3f,$3f,$fe,$06
  .byte $fb,$3d,$4d,$5e,$4e,$3e,$2f,$1f,$fe,$06,$fb,$2d,$3d,$4e,$3e,$2e,$1f,$1f,$fe,$04,$fb,$1d,$1d,$2e
  .byte $2e,$1e,$1f,$fe,$04,$ff,$03,$b0,$8b,$00,$00,$08,$b0,$8b,$f0,$22,$fa,$83,$f0,$99,$fa,$8b,$f0,$22
  .byte $fa,$83,$c0,$99,$fa,$8b,$a0,$22,$fa,$83,$80,$99,$fa,$8b,$60,$22,$fa,$83,$40,$99,$fa,$8b,$40,$22
  .byte $fa,$83,$30,$99,$fa,$8b,$20,$22,$fa,$83,$10,$99,$ff,$04,$9d,$9b,$9d,$9b,$9c,$9a,$9c,$9a,$9b,$99
  .byte $7b,$79,$5a,$58,$49,$47,$38,$36,$27,$25,$16,$14,$ff,$d7,$33,$81,$68,$cf,$cf,$e6,$01,$cc,$f3,$fd
  .word $bbe1 ; source pointer$9a70
  .byte $f2,$fd
  .word $bbe1 ; source pointer$9a74
  .byte $f1,$fd
  .word $bbe1 ; source pointer$9a78
  .byte $f0,$e0,$43,$e1,$b4,$44,$e0,$23,$44,$e1,$94,$b3,$74,$94,$40,$fd
  .word $bcc2 ; source pointer$9a8a
  .byte $e4,$20,$e8,$19,$e9,$31,$e5,$70,$b0,$f1,$e4,$20,$e5,$70,$f0,$b0,$e4,$20,$e5,$70,$b0,$f2,$fd
  .word $bcd1 ; source pointer$9aa3
  .byte $e8,$1e,$71,$71,$91,$e9,$00,$f0,$d1,$76,$80,$00,$ea,$85,$fd
  .word $bf18 ; source pointer$9ab4
  .byte $ea,$00,$fd
  .word $bcc2 ; source pointer$9ab9
  .byte $d1,$38,$81,$00,$e9,$00,$f2,$e4,$2d,$16,$f1,$06,$e5,$b6,$93,$f0,$83,$73,$63,$52,$42,$31,$21,$10
  .byte $00,$fd
  .word $bcd1 ; source pointer$9ad5
  .byte $70,$f2,$70,$f0,$00,$e5,$70,$e4,$90,$f2,$90,$f0,$20,$e5,$90,$e4,$a0,$e9,$00,$fd
  .word $bbf2 ; source pointer$9aeb
  .byte $90,$f4,$e3,$79,$60,$50,$40,$30,$20,$f5,$10,$00,$e4,$b0,$a0,$90,$f6,$e3,$79,$60,$50,$40,$30,$20
  .byte $10,$f0,$d1,$f7,$80,$00,$e3,$69,$50,$40,$30,$20,$f1,$10,$00,$e4,$b0,$f2,$a0,$90,$80,$f4,$e3,$69
  .byte $50,$40,$30,$20,$10,$f5,$00,$e4,$b0,$a0,$90,$80,$f6,$e3,$69,$50,$40,$30,$20,$10,$00,$f0,$d7,$78
  .byte $84,$19,$e4,$60,$60,$60,$60,$40,$50,$60,$90,$fd
  .word $bbf2 ; source pointer$9b41
  .byte $91,$f0,$e3,$69,$50,$40,$30,$20,$f1,$10,$00,$e4,$b0,$f2,$a0,$90,$80,$f4,$e3,$69,$50,$40,$30,$20
  .byte $10,$f0,$d7,$77,$85,$19,$e9,$b1,$fd
  .word $bcdf ; source pointer$9b64
  .byte $d7,$fb,$85,$1e,$e9,$71,$e4,$60,$e6,$01,$64,$d7,$32,$81,$00,$e9,$00,$fb,$e2,$b0,$90,$60,$fe,$04
  .byte $b0,$90,$e6,$01,$61,$d7,$fb,$85,$1e,$e9,$71,$e4,$60,$e6,$01,$64,$d7,$32,$81,$00,$e9,$00,$fd
  .word $bcf3 ; source pointer$9b95
  .byte $e6,$01,$a1,$d7,$fb,$85,$1e,$e9,$71,$e4,$60,$e6,$01,$64,$d7,$32,$81,$00,$e9,$00,$fd
  .word $bd05 ; source pointer$9bac
  .byte $e6,$01,$51,$d7,$f6,$80,$00,$eb,$01,$02,$e4,$60,$f5,$e1,$b1,$f0,$e4,$40,$f5,$e1,$b1,$f0,$e4,$10
  .byte $f4,$e1,$b1,$f0,$e4,$00,$f4,$e1,$b1,$f0,$e5,$b0,$f4,$e1,$b0,$f0,$e5,$90,$f3,$e1,$b0,$eb,$00,$fe
  .byte $ff
  .word $ba89 ; source pointer$9bdf
  .byte $e0,$43,$e1,$b4,$44,$e0,$23,$44,$e1,$94,$b3,$74,$94,$43,$74,$24,$ff,$d1,$f7,$80,$00,$e4,$b9,$a0
  .byte $90,$80,$70,$f1,$60,$50,$40,$f2,$30,$20,$10,$f4,$b9,$a0,$90,$80,$70,$60,$d7,$72,$08,$19,$e9,$31
  .byte $ec,$01,$e4,$40,$80,$b0,$b0,$e3,$40,$80,$f0,$d1,$73,$80,$00,$e9,$00,$b9,$a0,$90,$80,$70,$f1,$60
  .byte $50,$40,$30,$f2,$20,$10,$b9,$a0,$90,$80,$70,$60,$f0,$ec,$00,$d1,$f7,$80,$00,$e3,$29,$10,$00,$e4
  .byte $b0,$a0,$f1,$90,$80,$70,$f2,$60,$50,$40,$f4,$e3,$29,$10,$00,$e4,$b0,$a0,$f5,$90,$d7,$72,$08,$19
  .byte $e9,$31,$ec,$01,$e4,$70,$b0,$e3,$20,$20,$70,$b0,$f0,$d1,$73,$80,$00,$e9,$00,$e2,$29,$10,$00,$e3
  .byte $b0,$a0,$f1,$90,$80,$70,$60,$f2,$50,$40,$e2,$29,$10,$00,$e3,$b0,$a0,$90,$ec,$00,$f0,$d1,$f7,$80
  .byte $00,$e3,$49,$30,$20,$10,$00,$f1,$e4,$b0,$a0,$90,$f2,$80,$70,$60,$f4,$e3,$49,$30,$20,$10,$00,$f5
  .byte $e4,$b0,$a0,$90,$80,$70,$60,$f6,$e3,$49,$30,$20,$10,$00,$e4,$b0,$a0,$f0,$e3,$79,$60,$50,$40,$30
  .byte $f1,$20,$10,$00,$f2,$e4,$b0,$a0,$ff,$d7,$7a,$84,$19,$e9,$b1,$f2,$e5,$fb,$b0,$fe,$05,$90,$b0,$ff
  .byte $d7,$78,$84,$19,$e9,$b1,$e4,$fb,$40,$fe,$05,$20,$40,$ff,$e5,$b0,$b0,$b0,$b0,$90,$90,$b0,$b0,$e4
  .byte $20,$10,$00,$e5,$b1,$b0,$e4,$20,$40,$ff,$e1,$40,$20,$40,$20,$e2,$b0,$90,$a0,$b0,$90,$60,$40,$20
  .byte $e3,$b0,$90,$ff,$e2,$20,$e3,$b0,$e2,$20,$40,$20,$40,$60,$40,$60,$90,$a0,$b0,$e1,$20,$40,$ff,$d7
  .byte $76,$82,$19,$cf,$cf,$e6,$01,$f4,$fd
  .word $bbe1 ; source pointer$9d22
  .byte $f3,$fd
  .word $bbe1 ; source pointer$9d26
  .byte $f2,$fd
  .word $bbe1 ; source pointer$9d2a
  .byte $f0,$fd
  .word $bbe1 ; source pointer$9d2e
  .byte $ec,$00,$fd
  .word $be0b ; source pointer$9d33
  .byte $e8,$1e,$e3,$01,$01,$21,$e9,$00,$d1,$75,$80,$00,$fd
  .word $bf18 ; source pointer$9d42
  .byte $fd
  .word $be0b ; source pointer$9d45
  .byte $d7,$78,$85,$1a,$e9,$31,$e3,$00,$e9,$71,$f4,$00,$f1,$e4,$70,$00,$e9,$31,$e3,$20,$e9,$71,$f4,$20
  .byte $f1,$e4,$90,$20,$e3,$30,$e9,$00,$fd
  .word $be29 ; source pointer$9d68
  .byte $20,$f4,$e2,$09,$e3,$b0,$a0,$90,$80,$70,$f5,$60,$50,$40,$30,$20,$f6,$e2,$09,$e3,$b0,$a0,$90,$80
  .byte $70,$60,$f0,$d1,$37,$80,$00,$e3,$b9,$a0,$90,$80,$70,$f1,$60,$50,$f2,$40,$30,$20,$10,$f4,$b9,$a0
  .byte $90,$80,$70,$60,$f5,$50,$40,$30,$20,$10,$f6,$b9,$a0,$90,$80,$70,$60,$50,$f0,$d7,$70,$15,$1a,$e4
  .byte $b0,$b0,$b0,$b0,$90,$a0,$b0,$e3,$20,$fd
  .word $be29 ; source pointer$9dbc
  .byte $21,$f0,$e3,$b9,$a0,$90,$80,$70,$f1,$60,$50,$40,$f2,$30,$20,$10,$f4,$b9,$a0,$90,$80,$70,$60,$f0
  .byte $d7,$7a,$89,$11,$e9,$31,$ea,$05,$fd
  .word $bcdf ; source pointer$9ddf
  .byte $ea,$00,$d7,$79,$87,$18,$e2,$ec,$02,$e9,$31,$fb,$b0,$90,$60,$fe,$05,$b0,$fd
  .word $bcf3 ; source pointer$9df4
  .byte $a0,$b0,$fd
  .word $bd05 ; source pointer$9df9
  .byte $50,$60,$ec,$00,$d7,$74,$81,$a3,$eb,$21,$00,$bf,$fe,$ff
  .word $bd32 ; source pointer$9e09
  .byte $d7,$70,$15,$1a,$e9,$31,$e4,$fb,$40,$fe,$05,$20,$40,$e8,$89,$eb,$37,$04,$78,$e8,$1a,$eb,$00,$fb
  .byte $90,$fe,$05,$70,$90,$ff,$d1,$37,$80,$00,$e3,$49,$30,$20,$10,$00,$f1,$e4,$b0,$a0,$f2,$90,$80,$70
  .byte $60,$f4,$e3,$49,$30,$20,$10,$00,$e4,$b0,$f5,$a0,$90,$80,$70,$60,$f6,$e3,$49,$30,$20,$10,$00,$e4
  .byte $b0,$90,$f0,$d7,$70,$08,$19,$e9,$b1,$ec,$01,$e3,$40,$80,$b0,$d1,$75,$80,$00,$e9,$00,$e2,$49,$30
  .byte $20,$f1,$10,$00,$f2,$e3,$b0,$a0,$f3,$90,$80,$f4,$70,$60,$f2,$e2,$49,$30,$20,$f3,$10,$00,$e3,$b0
  .byte $f0,$d1,$37,$80,$00,$e3,$79,$60,$50,$40,$30,$f1,$20,$10,$00,$e4,$f2,$b0,$a0,$90,$f4,$e3,$79,$60
  .byte $50,$40,$30,$20,$f5,$10,$00,$e4,$b0,$a0,$90,$f6,$e3,$79,$60,$50,$40,$30,$20,$10,$d7,$70,$08,$19
  .byte $e9,$b1,$ec,$01,$e3,$70,$b0,$e2,$20,$d1,$75,$80,$00,$e9,$00,$79,$60,$50,$f1,$40,$30,$f2,$20,$10
  .byte $f3,$00,$e3,$b0,$f4,$a0,$90,$f2,$e2,$79,$60,$50,$f3,$40,$30,$20,$ec,$00,$d1,$37,$80,$00,$e3,$99
  .byte $80,$70,$60,$50,$f1,$40,$30,$f2,$20,$10,$00,$e4,$b0,$f4,$e3,$99,$80,$70,$60,$50,$40,$f5,$30,$20
  .byte $10,$00,$e4,$b0,$f6,$e3,$99,$80,$70,$60,$50,$40,$30,$f0,$e2,$09,$e3,$b0,$a0,$90,$80,$f1,$70,$60
  .byte $f2,$50,$40,$30,$ff,$26,$10,$00,$e4,$b0,$a0,$90,$80,$70,$60,$50,$40,$30,$20,$10,$00,$ff,$d7,$20
  .byte $cf,$cf,$cf,$cb,$d1,$20,$e3,$b5,$91,$81,$71,$61,$51,$41,$31,$21,$11,$01,$e4,$b1,$fd
  .word $a505 ; source pointer$9f40
  .byte $0d,$2d,$d1,$17,$fd
  .word $bf18 ; source pointer$9f47
  .byte $fd
  .word $a505 ; source pointer$9f4a
  .byte $e4,$76,$06,$e3,$2d,$e4,$96,$26,$e3,$36,$fd
  .word $a51c ; source pointer$9f57
  .byte $96,$e3,$16,$46,$96,$fd
  .word $a588 ; source pointer$9f5f
  .byte $e3,$06,$06,$46,$76,$e2,$06,$d1,$20,$e4,$fd
  .word $a57d ; source pointer$9f6c
  .byte $11,$d1,$01,$e4,$b6,$d1,$20,$e3,$fd
  .word $a57d ; source pointer$9f77
  .byte $10,$00,$e4,$b0,$a0,$90,$80,$70,$60,$50,$d7,$10,$e4,$b0,$b0,$b0,$b0,$90,$a0,$b0,$e3,$20,$fd
  .word $a51c ; source pointer$9f90
  .byte $e3,$96,$96,$e4,$96,$e3,$96,$fd
  .word $a588 ; source pointer$9f9a
  .byte $b6,$d1,$20,$e3,$fd
  .word $a57d ; source pointer$9fa1
  .byte $10,$00,$e4,$b0,$a0,$90,$80,$70,$60,$50,$d1,$01,$fb,$e4,$46,$e2,$46,$fe,$02,$e4,$26,$e2,$26,$e4
  .byte $46,$e2,$46,$e3,$76,$66,$56,$4d,$d1,$01,$46,$76,$96,$d7,$13,$fb,$e4,$b0,$b0,$b0,$e3,$b0,$e4,$b0
  .byte $e3,$b0,$e4,$b0,$e3,$b1,$e4,$b0,$80,$e3,$80,$e4,$90,$e3,$90,$e4,$a0,$e3,$a0,$fe,$03,$e4,$b0,$e3
  .byte $60,$e4,$b0,$90,$e3,$40,$e4,$90,$60,$e3,$10,$e4,$60,$50,$e3,$00,$e4,$50,$40,$b0,$20
  .assert *=$c000,lderror,"Native A footprint"
.segment "TMNT_NATIVE_AUDIO_B"
  .byte $e3,$09,$e4,$b0,$a0,$90,$80,$70,$60,$50,$40,$30,$21,$d1,$01,$ff,$fd
  .word $c100 ; source pointer$a09b
  .byte $fd
  .word $c0dd ; source pointer$a09e
  .byte $fb,$b0,$2c,$fe,$04,$41,$44,$fd
  .word $c0dd ; source pointer$a0a8
  .byte $fb,$b0,$2c,$46,$46,$fe,$02,$46,$fd
  .word $c100 ; source pointer$a0b3
  .byte $fd
  .word $c100 ; source pointer$a0b6
  .byte $fd
  .word $c0dd ; source pointer$a0b9
  .byte $d1,$b6,$26,$b6,$41,$24,$b6,$fb,$46,$fe,$04,$fb,$b0,$25,$b6,$41,$24,$b6,$fe,$04,$fb,$41,$2f,$c2
  .byte $fe,$04,$41,$3b,$46,$46,$fe,$ff
  .word $c09d ; source pointer$a0db
  .byte $d1,$b0,$25,$b6,$41,$24,$b6,$b0,$25,$b6,$41,$24,$b6,$26,$b6,$41,$24,$b6,$b0,$25,$b6,$41,$2b,$b0
  .byte $25,$b6,$41,$24,$b6,$b0,$25,$b6,$41,$24,$ff,$d1,$fb,$b0,$2c,$41,$2b,$b0,$25,$b6,$41,$24,$b6,$26
  .byte $b6,$41,$24,$b6,$b0,$25,$b6,$41,$2b,$fe,$03,$b0,$2c,$41,$2b,$b0,$25,$b6,$41,$24,$b6,$26,$41,$44
  .byte $b6,$b6,$41,$44,$b6,$46,$46,$ff,$fd,$00,$a1,$fe,$ff,$2d,$a1,$d7,$77,$84,$12,$c7,$e6,$01,$c0,$e6
  .byte $07,$d7,$75,$82,$1a,$fd
  .word $c1e6 ; source pointer$a143
  .byte $e6,$01,$e4,$25,$e6,$07,$e3,$fb,$a0,$f1,$a0,$f2,$a0,$f0,$fe,$02,$e8,$45,$73,$a1,$71,$e6,$01,$ae
  .byte $e6,$07,$e8,$1a,$fd
  .word $c1e6 ; source pointer$a162
  .byte $e6,$01,$e5,$a5,$e6,$07,$e3,$a0,$f1,$a0,$f2,$a0,$f0,$e2,$00,$f1,$00,$f2,$00,$f0,$eb,$21,$04,$e8
  .byte $76,$e3,$47,$eb,$00,$40,$90,$d7,$33,$81,$12,$eb,$31,$00,$e3,$a7,$eb,$00,$31,$e2,$01,$e3,$a1,$91
  .byte $a2,$51,$e7,$80,$e8,$1a,$e9,$71,$e2,$50,$31,$21,$31,$51,$e7,$81,$e3,$70,$90,$a0,$f1,$a0,$f2,$a0
  .byte $f0,$70,$f1,$70,$f2,$70,$f0,$40,$f1,$40,$f2,$40,$f0,$a0,$f1,$a0,$f0,$a0,$e9,$00,$e8,$12,$91,$a1
  .byte $e9,$71,$e8,$1a,$e2,$fd
  .word $c202 ; source pointer$a1ca
  .byte $d1,$32,$80,$00,$25,$20,$30,$40,$50,$60,$70,$80,$90,$a0,$c3,$f1,$22,$30,$40,$50,$cf,$cf,$fe,$ff
  .word $c13e ; source pointer$a1e4
  .byte $e4,$20,$e5,$a0,$e4,$30,$e5,$a0,$e4,$50,$e5,$51,$e4,$20,$e5,$a0,$e4,$20,$e5,$a0,$e4,$30,$50,$e5
  .byte $50,$e4,$30,$ff,$fb,$f0,$00,$f3,$00,$f5,$00,$fe,$02,$f0,$10,$f3,$10,$f0,$ff,$d7,$77,$84,$12,$c7
  .byte $fd
  .word $c2d0 ; source pointer$a217
  .byte $d7,$77,$85,$1a,$e9,$31,$fb,$f0,$e2,$20,$f3,$20,$f5,$20,$fe,$02,$f0,$d7,$70,$05,$45,$03,$e9,$00
  .byte $21,$01,$21,$f0,$fd
  .word $c2d0 ; source pointer$a236
  .byte $d7,$77,$85,$1a,$e9,$31,$f0,$e2,$20,$f3,$20,$f5,$20,$f0,$40,$f3,$40,$f5,$40,$f0,$d7,$70,$05,$76
  .byte $eb,$21,$04,$07,$eb,$00,$d7,$77,$85,$1a,$00,$20,$f0,$d7,$71,$05,$12,$eb,$31,$00,$e9,$31,$e2,$37
  .byte $e9,$00,$e3,$71,$e2,$31,$21,$01,$22,$e8,$97,$e3,$aa,$eb,$00,$a0,$e2,$00,$e8,$1a,$e9,$31,$f0,$20
  .byte $f3,$20,$f5,$20,$f0,$00,$f3,$00,$f5,$00,$f0,$e3,$70,$f3,$70,$f5,$70,$f0,$e2,$20,$f3,$20,$f1,$e8
  .byte $97,$20,$e9,$00,$01,$21,$e9,$31,$e8,$1a,$ea,$04,$fd
  .word $c202 ; source pointer$a2a5
  .byte $ea,$00,$d1,$75,$80,$00,$65,$60,$70,$f1,$80,$90,$f2,$a0,$b0,$f4,$e1,$00,$f5,$10,$20,$c3,$e2,$62
  .byte $70,$80,$f6,$90,$a0,$b0,$e1,$00,$10,$20,$e6,$02,$cc,$fe,$ff
  .word $c216 ; source pointer$a2ce
  .byte $d7,$30,$05,$1a,$e9,$71,$e4,$51,$71,$a2,$51,$51,$70,$a1,$71,$ff,$d7,$10,$c3,$d1,$20,$e3,$25,$20
  .byte $10,$00,$e4,$b0,$a0,$90,$80,$70,$60,$50,$40,$30,$20,$10,$00,$e5,$b0,$a0,$90,$80,$70,$60,$50,$d1
  .byte $01,$fd
  .word $c334 ; source pointer$a302
  .byte $e4,$7d,$e3,$0d,$fd
  .word $c334 ; source pointer$a309
  .byte $0d,$2d,$fd
  .word $c34a ; source pointer$a30e
  .byte $e3,$3d,$ea,$85,$fd
  .word $c34a ; source pointer$a315
  .byte $ea,$00,$e3,$2d,$0f,$c4,$06,$0d,$e4,$76,$e3,$06,$0f,$c4,$06,$0d,$2d,$e4,$2f,$c4,$d7,$10,$22,$91
  .byte $23,$fe,$ff
  .word $c2e3 ; source pointer$a332
  .byte $e4,$af,$c4,$a6,$5f,$c4,$ad,$ad,$a6,$5d,$e3,$2d,$0d,$0d,$e4,$7f,$c4,$e3,$0d,$0d,$06,$ff,$e3,$3f
  .byte $c4,$36,$e4,$af,$c4,$e3,$3d,$3d,$36,$e4,$ad,$ff,$d1,$41,$44,$bd,$b6,$41,$4b,$d7,$40,$40,$fb,$d7
  .byte $b1,$10,$b0,$41,$10,$b1,$b0,$10,$b0,$41,$10,$10,$b1,$b0,$10,$41,$10,$b1,$b0,$10,$b0,$41,$d1,$46
  .byte $46,$fe,$02,$fb,$d7,$b1,$10,$b0,$41,$10,$b1,$b0,$10,$b0,$41,$10,$10,$fe,$03,$d1,$fb,$b0,$2f,$c3
  .byte $fe,$02,$41,$4b,$41,$4b,$cd,$d7,$b3,$fe,$ff
  .word $c362 ; source pointer$a39f
  .byte $fb,$fd
  .word $c498 ; source pointer$a3a3
  .byte $50,$40,$00,$e4,$70,$50,$70,$92,$e7,$82,$f1,$e4,$54,$c0,$da,$b2,$13,$12,$eb,$01,$07,$e2,$21,$eb
  .byte $00,$e3,$91,$f0,$fe,$02,$da,$b5,$82,$12,$c5,$eb,$01,$02,$f1,$e4,$53,$f0,$e7,$85,$e3,$fd
  .word $c47d ; source pointer$a3d3
  .byte $da,$b4,$82,$12,$eb,$02,$07,$e4,$21,$12,$eb,$00,$da,$73,$82,$34,$e3,$00,$00,$e4,$90,$e3,$00,$20
  .byte $01,$fd
  .word $c498 ; source pointer$a3ef
  .byte $00,$70,$80,$91,$f2,$91,$f0,$da,$75,$82,$19,$eb,$01,$02,$ec,$01,$fd
  .word $c488 ; source pointer$a402
  .byte $ec,$00,$d5,$75,$85,$17,$fb,$e3,$71,$61,$51,$41,$71,$61,$51,$41,$eb,$01,$02,$e2,$01,$eb,$00,$e4
  .byte $21,$eb,$01,$02,$e2,$21,$41,$eb,$00,$e4,$21,$41,$71,$91,$fe,$02,$e4,$21,$e9,$31,$e3,$51,$91,$51
  .byte $e2,$01,$e3,$51,$e9,$00,$e4,$21,$e9,$31,$e3,$51,$a1,$e9,$00,$d5,$74,$81,$11,$e4,$20,$40,$50,$90
  .byte $e3,$00,$40,$d5,$74,$84,$11,$51,$91,$e2,$01,$41,$d5,$74,$84,$1c,$e9,$35,$fb,$e2,$21,$e3,$b1,$fe
  .byte $03,$e2,$21,$01,$ec,$02,$fb,$e2,$11,$e3,$91,$e2,$41,$e3,$91,$fe,$02,$e9,$00,$ec,$00,$fe,$ff
  .word $c3a1 ; source pointer$a47b
  .byte $70,$50,$40,$50,$40,$00,$70,$50,$70,$90,$ff,$e5,$90,$e4,$00,$20,$50,$70,$50,$70,$80,$90,$e3,$00
  .byte $20,$50,$ff,$da,$b5,$82,$12,$c5,$f1,$eb,$01,$02,$e4,$53,$f0,$e7,$85,$e3,$70,$50,$40,$ff,$fb,$fd
  .word $c593 ; source pointer$a4ad
  .byte $50,$40,$00,$e5,$70,$50,$70,$90,$ec,$00,$f4,$91,$f0,$da,$75,$82,$12,$e9,$00,$e4,$54,$c0,$da,$b0
  .byte $13,$12,$eb,$02,$07,$e2,$51,$eb,$00,$01,$fe,$02,$da,$75,$82,$18,$e5,$71,$71,$21,$e8,$12,$e4,$53
  .byte $da,$70,$11,$19,$ec,$01,$e9,$31,$fd
  .word $c47d ; source pointer$a4e8
  .byte $ec,$00,$da,$74,$82,$12,$eb,$05,$07,$e3,$21,$12,$eb,$00,$da,$30,$12,$16,$e9,$71,$e3,$50,$50,$20
  .byte $50,$70,$51,$fd
  .word $c593 ; source pointer$a506
  .byte $00,$70,$80,$fb,$90,$f3,$90,$f0,$fe,$02,$ec,$00,$da,$35,$85,$19,$ea,$0c,$fd
  .word $c488 ; source pointer$a51b
  .byte $ea,$00,$e9,$00,$da,$78,$88,$15,$ec,$01,$fd
  .word $c57d ; source pointer$a528
  .byte $20,$fd
  .word $c57d ; source pointer$a52c
  .byte $e2,$50,$e4,$a0,$e2,$50,$50,$20,$50,$70,$e4,$a0,$e7,$84,$ec,$00,$e2,$51,$d5,$75,$85,$00,$e4,$70
  .byte $90,$a0,$e3,$20,$50,$90,$da,$79,$89,$15,$ec,$01,$e9,$74,$a0,$e2,$20,$50,$90,$70,$f2,$70,$f4,$70
  .byte $f0,$80,$f2,$80,$f4,$80,$f0,$e6,$04,$93,$f1,$93,$f2,$93,$f3,$93,$f4,$93,$f5,$93,$f6,$90,$f0,$e9
  .byte $00,$ec,$00,$fe,$ff
  .word $c4ab ; source pointer$a57b
  .byte $fb,$e2,$00,$e3,$b0,$a0,$90,$fe,$02,$e2,$00,$e4,$70,$e2,$20,$40,$e4,$70,$90,$e3,$00,$ff,$da,$75
  .byte $82,$18,$e5,$21,$21,$91,$e8,$12,$e4,$53,$da,$70,$11,$19,$e9,$31,$ec,$01,$70,$50,$40,$ff,$fb,$da
  .byte $10,$fd
  .word $c665 ; source pointer$a5af
  .byte $db,$26,$e3,$01,$da,$10,$e4,$70,$90,$e3,$00,$e4,$53,$fd
  .word $c665 ; source pointer$a5bf
  .byte $d2,$3f,$e3,$0a,$d1,$20,$e2,$60,$50,$40,$30,$20,$10,$00,$e3,$b0,$a0,$90,$e2,$61,$51,$41,$31,$21
  .byte $11,$01,$e3,$b1,$a1,$91,$da,$14,$e4,$53,$fe,$02,$da,$10,$e4,$71,$71,$21,$d1,$21,$61,$71,$81,$91
  .byte $db,$26,$a1,$da,$10,$20,$50,$60,$a3,$70,$20,$71,$81,$da,$14,$95,$fd
  .word $c670 ; source pointer$a602
  .byte $da,$10,$fd
  .word $c665 ; source pointer$a607
  .byte $db,$20,$e3,$01,$d1,$20,$e2,$40,$30,$20,$10,$00,$e3,$b0,$a0,$90,$80,$70,$e2,$41,$31,$21,$11,$01
  .byte $e3,$b1,$a1,$91,$81,$71,$da,$13,$e4,$53,$23,$da,$10,$fd
  .word $c488 ; source pointer$a62f
  .byte $da,$10,$fb,$e4,$91,$91,$90,$e3,$91,$e4,$90,$91,$91,$20,$40,$70,$90,$fe,$02,$71,$71,$70,$e3,$71
  .byte $e4,$70,$71,$71,$70,$e3,$70,$e4,$80,$e3,$80,$e4,$94,$e3,$90,$e4,$90,$e3,$90,$e4,$93,$fd
  .word $c670 ; source pointer$a65f
  .byte $fe,$ff
  .word $c5ab ; source pointer$a663
  .byte $e4,$21,$21,$91,$d1,$21,$81,$91,$a1,$b1,$ff,$d1,$20,$e3,$51,$41,$31,$21,$11,$01,$e4,$b1,$a1,$91
  .byte $81,$71,$61,$51,$41,$31,$21,$11,$01,$e5,$b1,$a1,$ff,$fb,$da,$31,$b1,$b1,$43,$fd
  .word $c6c4 ; source pointer$a691
  .byte $b1,$b0,$30,$31,$43,$fd
  .word $c6c4 ; source pointer$a699
  .byte $fe,$03,$31,$b1,$30,$30,$43,$fd
  .word $c6c4 ; source pointer$a6a3
  .byte $b1,$b0,$30,$32,$20,$42,$30,$b3,$fb,$b1,$b1,$41,$21,$b0,$41,$b0,$41,$40,$40,$fe,$03,$43,$20,$20
  .byte $21,$43,$b3,$fe,$ff
  .word $c68a ; source pointer$a6c2
  .byte $d7,$20,$20,$d6,$20,$da,$23,$ff,$d8,$36,$82,$1a,$f2,$e5,$80,$80,$e4,$00,$00,$10,$10,$20,$20,$f0
  .byte $e3,$30,$30,$50,$50,$60,$60,$70,$70,$ea,$89,$d8,$34,$81,$1a,$c0,$e9,$71,$fd
  .word $c75d ; source pointer$a6ef
  .byte $e3,$40,$50,$00,$e4,$92,$c0,$fd
  .word $c75d ; source pointer$a6f9
  .byte $00,$00,$ec,$01,$90,$e2,$00,$50,$90,$ec,$00,$e9,$f1,$fd
  .word $c771 ; source pointer$a709
  .byte $91,$70,$e2,$40,$50,$40,$50,$fd
  .word $c771 ; source pointer$a713
  .byte $90,$70,$50,$e8,$12,$31,$20,$00,$ea,$03,$d8,$33,$81,$17,$fd
  .word $c790 ; source pointer$a724
  .byte $70,$70,$70,$70,$ea,$06,$fd
  .word $c790 ; source pointer$a72d
  .byte $ea,$03,$e5,$a1,$b1,$ea,$03,$d8,$33,$81,$18,$e3,$c0,$fb,$91,$90,$70,$50,$30,$fe,$02,$e4,$30,$40
  .byte $50,$c0,$e3,$91,$90,$70,$50,$30,$e2,$41,$fb,$50,$40,$fe,$03,$50,$ec,$00,$fe,$ff
  .word $c6e5 ; source pointer$a75b
  .byte $fb,$e4,$40,$50,$90,$fe,$05,$e3,$40,$50,$40,$50,$00,$e4,$91,$e3,$40,$40,$50,$ff,$ea,$89,$d8,$f3
  .byte $81,$88,$e3,$36,$31,$30,$20,$00,$31,$20,$00,$c0,$e4,$80,$90,$a0,$e3,$00,$30,$c0,$d8,$33,$81,$1c
  .byte $e3,$91,$ff,$eb,$02,$02,$e4,$00,$00,$00,$00,$eb,$00,$00,$00,$00,$00,$40,$40,$40,$40,$ff,$d8,$36
  .byte $84,$18,$e9,$71,$e3,$80,$80,$60,$60,$50,$50,$40,$40,$30,$30,$10,$10,$e4,$b0,$b0,$a0,$a0,$e9,$31
  .byte $ea,$89,$d8,$31,$05,$1a,$c0,$e9,$71,$fd
  .word $c842 ; source pointer$a7c7
  .byte $80,$90,$50,$e8,$49,$32,$c0,$e8,$1a,$fd
  .word $c842 ; source pointer$a7d3
  .byte $50,$ec,$01,$e8,$19,$30,$50,$90,$e2,$00,$50,$f0,$ec,$00,$e9,$00,$fd
  .word $c858 ; source pointer$a7e6
  .byte $50,$f2,$50,$f0,$30,$e9,$70,$e9,$32,$80,$90,$80,$90,$e9,$72,$fd
  .word $c858 ; source pointer$a7f8
  .byte $50,$30,$20,$e8,$12,$01,$e4,$a0,$90,$d8,$36,$83,$17,$e9,$b1,$fd
  .word $c88b ; source pointer$a80a
  .byte $a0,$a0,$a0,$a0,$ea,$06,$fd
  .word $c88b ; source pointer$a813
  .byte $ea,$03,$e3,$31,$41,$e9,$71,$ea,$89,$d8,$76,$84,$18,$c0,$e9,$31,$fb,$fd
  .word $c881 ; source pointer$a827
  .byte $fe,$02,$e4,$30,$40,$50,$c0,$fd
  .word $c881 ; source pointer$a831
  .byte $81,$fb,$90,$80,$fe,$03,$90,$ec,$00,$e9,$31,$fe,$ff
  .word $c7bd ; source pointer$a840
  .byte $fb,$e4,$80,$90,$e3,$50,$fe,$05,$80,$90,$80,$90,$50,$e8,$49,$31,$e8,$1a,$80,$80,$90,$ff,$ea,$03
  .byte $d8,$77,$84,$12,$f1,$eb,$01,$04,$e3,$36,$31,$30,$20,$00,$31,$20,$00,$c0,$e4,$80,$90,$a0,$e3,$00
  .byte $30,$c0,$eb,$00,$f0,$d8,$37,$85,$1c,$e3,$50,$f2,$50,$f0,$ff,$e2,$50,$f2,$50,$f0,$50,$30,$20,$00
  .byte $ff,$e4,$00,$00,$00,$00,$40,$40,$40,$40,$70,$70,$70,$70,$ff,$ea,$03,$d1,$09,$c0,$d8,$11,$e4,$50
  .byte $50,$90,$90,$a0,$a0,$b0,$b0,$e3,$00,$00,$20,$20,$30,$30,$40,$d1,$01,$46,$fb,$e4,$57,$e3,$59,$c5
  .byte $e4,$57,$37,$e3,$39,$c5,$e4,$37,$57,$e3,$59,$c5,$d8,$10,$e4,$31,$d1,$01,$07,$37,$47,$fe,$04,$fd
  .word $c926 ; source pointer$a8d2
  .byte $e3,$39,$c5,$e4,$37,$57,$e3,$57,$e4,$37,$d8,$10,$e3,$b1,$d1,$01,$e2,$07,$e3,$b7,$e2,$07,$fd
  .word $c926 ; source pointer$a8eb
  .byte $e3,$37,$e4,$37,$e3,$37,$e4,$57,$e3,$57,$37,$27,$07,$e4,$37,$47,$57,$d8,$10,$fb,$e4,$00,$fe,$0e
  .byte $20,$20,$fb,$30,$fe,$0c,$31,$41,$d1,$01,$fd
  .word $c926 ; source pointer$a910
  .byte $e3,$37,$e4,$37,$d8,$10,$e3,$81,$d1,$01,$fb,$97,$87,$fe,$03,$97,$fe,$ff
  .word $c8b4 ; source pointer$a924
  .byte $e4,$57,$e3,$59,$c5,$e4,$57,$37,$e3,$39,$c5,$e4,$37,$57,$e3,$59,$c5,$d8,$10,$e4,$31,$d1,$01,$07
  .byte $37,$47,$57,$e3,$59,$c5,$e4,$57,$37,$ff,$d8,$c7,$b0,$40,$40,$40,$40,$40,$40,$40,$d8,$fb,$fd
  .word $c985 ; source pointer$a955
  .byte $fe,$05,$b1,$41,$b0,$b0,$40,$b1,$b0,$40,$b0,$b0,$b0,$40,$40,$fb,$fd
  .word $c985 ; source pointer$a968
  .byte $fe,$03,$fd
  .word $c992 ; source pointer$a96d
  .byte $b0,$2e,$b0,$2e,$d8,$fd
  .word $c985 ; source pointer$a975
  .byte $fd
  .word $c992 ; source pointer$a978
  .byte $47,$47,$d1,$40,$46,$40,$46,$fe,$ff
  .word $c952 ; source pointer$a983
  .byte $b1,$41,$b0,$b0,$40,$b1,$b0,$40,$b0,$b0,$b0,$41,$ff,$b1,$41,$b0,$b0,$40,$b1,$d1,$41,$45,$b7,$b7
  .byte $ff,$e9,$b8,$d4,$b5,$81,$19,$f2,$eb,$01,$02,$fb,$fd
  .word $ca6e ; source pointer$a9aa
  .byte $fe,$02,$f0,$ec,$03,$fb,$fd
  .word $ca6e ; source pointer$a9b3
  .byte $fe,$02,$eb,$00,$fb,$fd
  .word $ca77 ; source pointer$a9bb
  .byte $fe,$02,$f1,$fd
  .word $ca77 ; source pointer$a9c1
  .byte $f2,$fd
  .word $ca77 ; source pointer$a9c5
  .byte $ec,$00,$d4,$70,$09,$00,$e3,$03,$03,$e4,$a3,$e3,$03,$f1,$03,$e4,$a3,$fb,$f0,$e3,$33,$53,$f1,$53
  .byte $fe,$02,$f0,$03,$03,$e4,$a3,$e3,$03,$f1,$03,$e4,$a3,$f0,$e3,$73,$63,$f1,$63,$f0,$53,$33,$f1,$33
  .byte $f0,$03,$03,$e4,$a3,$e3,$03,$f1,$03,$e4,$a3,$fb,$f0,$e3,$33,$53,$f1,$53,$fe,$02,$f0,$61,$71,$a1
  .byte $71,$51,$31,$01,$e4,$a1,$b1,$e3,$0b,$e9,$b4,$d4,$b3,$81,$19,$ec,$02,$fb,$e5,$51,$e4,$01,$31,$71
  .byte $51,$31,$fe,$03,$ec,$00,$fd
  .word $ca62 ; source pointer$aa2e
  .byte $e8,$14,$e6,$06,$eb,$42,$00,$5f,$eb,$00,$e8,$18,$fd
  .word $ca62 ; source pointer$aa3d
  .byte $fd
  .word $ca80 ; source pointer$aa40
  .byte $e6,$06,$e8,$14,$eb,$42,$00,$e4,$0b,$fd
  .word $ca8e ; source pointer$aa4c
  .byte $eb,$42,$00,$e3,$0b,$e3,$fd
  .word $ca8e ; source pointer$aa55
  .byte $eb,$41,$00,$e2,$0f,$eb,$00,$fe,$ff
  .word $c99e ; source pointer$aa60
  .byte $d4,$35,$83,$18,$e3,$53,$73,$83,$a3,$83,$73,$ff,$e5,$51,$e4,$01,$31,$71,$51,$31,$ff,$01,$71,$a1
  .byte $e3,$21,$01,$e4,$a1,$ff,$e3,$53,$73,$53,$33,$23,$13,$03,$23,$33,$53,$33,$23,$ff,$eb,$00,$e8,$18
  .byte $e6,$04,$a1,$a1,$a1,$e6,$06,$e8,$14,$ff,$e9,$b1,$d4,$77,$82,$19,$f3,$fb,$fd
  .word $ca6e ; source pointer$aaa5
  .byte $fe,$02,$f1,$fb,$fd
  .word $ca77 ; source pointer$aaac
  .byte $fe,$02,$f0,$fb,$ea,$0c,$fd
  .word $ca6e ; source pointer$aab5
  .byte $fe,$02,$f1,$fd
  .word $ca6e ; source pointer$aabb
  .byte $f2,$fd
  .word $ca6e ; source pointer$aabf
  .byte $ea,$00,$d4,$b0,$08,$27,$e3,$53,$53,$33,$53,$f2,$53,$f4,$33,$fb,$f0,$83,$a3,$f3,$a3,$fe,$02,$f0
  .byte $53,$53,$33,$53,$f2,$53,$f4,$33,$f0,$e2,$03,$e3,$b3,$f3,$b3,$f0,$a3,$83,$f3,$83,$f0,$53,$53,$33
  .byte $53,$f2,$53,$f4,$33,$fb,$f0,$83,$a3,$f3,$a3,$fe,$02,$f0,$b1,$e2,$01,$31,$01,$e3,$a1,$81,$51,$31
  .byte $41,$d8,$b8,$85,$a8,$eb,$53,$00,$5b,$eb,$00,$e9,$b1,$d4,$76,$82,$19,$fb,$e4,$fd
  .word $ca77 ; source pointer$ab1d
  .byte $fe,$02,$e9,$00,$fd
  .word $cb60 ; source pointer$ab24
  .byte $ec,$00,$d6,$b0,$15,$86,$eb,$42,$00,$e3,$af,$eb,$00,$fd
  .word $cb60 ; source pointer$ab34
  .byte $ea,$05,$fd
  .word $ca80 ; source pointer$ab39
  .byte $ea,$00,$ec,$00,$d6,$b0,$15,$86,$eb,$42,$00,$5b,$fd
  .word $cb6f ; source pointer$ab48
  .byte $eb,$42,$00,$5b,$ea,$0c,$fd
  .word $cb6f ; source pointer$ab51
  .byte $ea,$00,$eb,$41,$00,$e2,$5f,$eb,$00,$fe,$ff
  .word $ca9c ; source pointer$ab5e
  .byte $d4,$b0,$15,$19,$ec,$05,$e3,$a3,$e2,$03,$13,$33,$13,$03,$ff,$eb,$00,$d4,$b8,$82,$19,$e9,$31,$31
  .byte $31,$31,$e9,$00,$d6,$b0,$15,$86,$ff,$d4,$09,$fb,$fd
  .word $cbf6 ; source pointer$ab85
  .byte $fe,$0e,$e4,$81,$e3,$31,$81,$11,$71,$e2,$11,$e4,$71,$e3,$21,$71,$e4,$01,$71,$e3,$01,$fb,$e4,$51
  .byte $e3,$01,$31,$71,$51,$31,$fe,$04,$e4,$81,$e3,$31,$81,$11,$81,$e2,$11,$e4,$61,$e3,$11,$61,$fb,$fd
  .word $cbf6 ; source pointer$abb7
  .byte $fe,$04,$d4,$09,$fb,$ea,$05,$fd
  .word $cbf6 ; source pointer$abc1
  .byte $fe,$07,$ea,$00,$e4,$a1,$e3,$51,$a1,$e4,$81,$e3,$81,$e4,$61,$fb,$fd
  .word $cbf6 ; source pointer$abd4
  .byte $fe,$02,$fb,$e4,$51,$e3,$01,$31,$71,$51,$31,$e4,$51,$e3,$01,$31,$e3,$31,$31,$31,$fe,$02,$fb,$fd
  .word $cbf6 ; source pointer$abee
  .byte $fe,$02,$fe,$ff
  .word $cb81 ; source pointer$abf4
  .byte $e4,$51,$e3,$01,$31,$71,$51,$31,$ff,$d4,$c1,$fb,$13,$fe,$15,$d1,$b0,$2e,$b0,$2e,$b0,$26,$d4,$fb
  .byte $fd
  .word $cc51 ; source pointer$ac0f
  .byte $fe,$06,$fb,$b1,$41,$41,$fe,$03,$b1,$fb,$13,$fe,$06,$43,$43,$41,$b1,$fb,$41,$fe,$05,$fb,$fd
  .word $cc51 ; source pointer$ac28
  .byte $fe,$03,$fb,$b1,$11,$41,$11,$fe,$02,$21,$41,$41,$41,$fd
  .word $cc51 ; source pointer$ac38
  .byte $fb,$b1,$11,$b1,$43,$11,$b1,$11,$b1,$41,$41,$41,$fe,$02,$b1,$fb,$13,$fe,$06,$fe,$ff
  .word $cc01 ; source pointer$ac4f
  .byte $b1,$11,$b1,$43,$11,$b1,$11,$b1,$11,$21,$41,$ff,$ea,$81,$d6,$33,$17,$15,$e9,$b1,$fd
  .word $cc6c ; source pointer$ac66
  .byte $fe,$ff
  .word $cc65 ; source pointer$ac6a
  .byte $fb,$e4,$12,$22,$32,$40,$50,$60,$fe,$02,$32,$42,$52,$60,$70,$80,$32,$42,$50,$30,$00,$e5,$b0,$a0
  .byte $80,$ff,$ea,$81,$d6,$70,$17,$16,$e9,$31,$ea,$04,$fd
  .word $cc6c ; source pointer$ac91
  .byte $fe,$ff
  .word $cc90 ; source pointer$ac95
  .byte $ea,$81,$d6,$10,$fd
  .word $cca2 ; source pointer$ac9c
  .byte $fe,$ff
  .word $cc9b ; source pointer$aca0
  .byte $fb,$e4,$60,$e3,$10,$60,$e4,$70,$e3,$20,$70,$e4,$80,$e3,$30,$80,$e4,$90,$a0,$b0,$fe,$02,$e4,$80
  .byte $e3,$30,$80,$e4,$90,$e3,$40,$90,$e4,$a0,$e3,$50,$a0,$e4,$b0,$e3,$00,$10,$e4,$80,$e3,$30,$80,$e4
  .byte $90,$e3,$40,$90,$a0,$80,$50,$40,$30,$10,$ff,$d6,$fd
  .word $cce5 ; source pointer$acdf
  .byte $fe,$ff
  .word $ccdd ; source pointer$ace3
  .byte $fb,$b0,$10,$10,$41,$10,$fe,$03,$b0,$10,$10,$40,$40,$40,$fb,$b0,$10,$10,$41,$10,$fe,$03,$fb,$40
  .byte $fe,$06,$ff,$d5,$33,$17,$15,$e9,$b1,$fd
  .word $cc6c ; source pointer$ad07
  .byte $fe,$ff
  .word $cd06 ; source pointer$ad0b
  .byte $d5,$70,$17,$16,$e9,$31,$ea,$05,$fd
  .word $cc6c ; source pointer$ad16
  .byte $fe,$ff
  .word $cc90 ; source pointer$ad1a
  .byte $d5,$10,$fd
  .word $cca2 ; source pointer$ad1f
  .byte $fe,$ff
  .word $cc9b ; source pointer$ad23
  .byte $d5,$fd
  .word $cce5 ; source pointer$ad27
  .byte $fe,$ff
  .word $cd25 ; source pointer$ad2b
  .byte $d1,$73,$80,$00,$eb,$01,$02,$fd
  .word $cdec ; source pointer$ad35
  .byte $d7,$74,$82,$19,$e4,$50,$70,$eb,$00,$d7,$35,$83,$19,$e5,$70,$e4,$20,$d7,$74,$0f,$68,$eb,$02,$06
  .byte $fd
  .word $cdd4 ; source pointer$ad50
  .byte $e4,$a1,$e9,$00,$e5,$70,$e4,$20,$d7,$74,$0f,$68,$eb,$02,$06,$fd
  .word $cdd4 ; source pointer$ad62
  .byte $11,$e9,$00,$d1,$73,$80,$10,$c6,$e3,$21,$31,$42,$d7,$74,$82,$1a,$fd
  .word $ce0d ; source pointer$ad75
  .byte $fd
  .word $ce03 ; source pointer$ad78
  .byte $e8,$1b,$e9,$31,$fb,$e2,$00,$e3,$80,$fe,$04,$fb,$e2,$20,$e3,$b0,$fe,$03,$70,$70,$e9,$00,$e4,$70
  .byte $71,$a0,$a1,$90,$91,$80,$81,$71,$c1,$d7,$36,$82,$1b,$fb,$e4,$32,$02,$31,$22,$e5,$b2,$e4,$21,$fe
  .byte $02,$d7,$35,$83,$1a,$e3,$90,$80,$90,$80,$90,$e2,$00,$e3,$b0,$90,$e8,$aa,$72,$24,$e8,$1a,$fb,$e2
  .byte $00,$e3,$b0,$fe,$02,$e2,$00,$30,$20,$00,$fd
  .word $ce03 ; source pointer$adcd
  .byte $00,$fe,$ff
  .word $cd40 ; source pointer$add2
  .byte $e3,$21,$21,$11,$22,$22,$01,$e4,$a2,$74,$f0,$d7,$35,$83,$19,$eb,$00,$e9,$b1,$e4,$a2,$e3,$02,$ff
  .byte $e4,$77,$61,$51,$41,$31,$f1,$21,$11,$01,$e5,$b1,$a1,$91,$81,$71,$61,$51,$41,$31,$21,$f0,$ff,$e2
  .byte $20,$00,$e3,$90,$80,$70,$50,$20,$ff,$e3,$51,$51,$21,$52,$51,$50,$22,$20,$50,$70,$80,$70,$50,$21
  .byte $ff,$d1,$b4,$80,$00,$00,$fd
  .word $cdec ; source pointer$ae23
  .byte $d7,$33,$0f,$19,$e5,$50,$70,$d7,$37,$84,$19,$e4,$00,$70,$fd
  .word $cedc ; source pointer$ae34
  .byte $31,$00,$70,$fd
  .word $cedc ; source pointer$ae3a
  .byte $61,$d1,$74,$80,$00,$c6,$e3,$71,$81,$92,$d7,$70,$0e,$19,$f2,$e9,$b1,$ea,$05,$fd
  .word $ce0d ; source pointer$ae50
  .byte $fd
  .word $ce03 ; source pointer$ae53
  .byte $ea,$00,$f0,$d7,$30,$0f,$65,$f3,$eb,$15,$04,$e3,$52,$72,$50,$30,$52,$71,$50,$30,$e4,$a0,$f0,$d7
  .byte $37,$84,$19,$eb,$00,$e3,$00,$01,$30,$31,$20,$21,$10,$11,$01,$d1,$75,$82,$00,$e4,$94,$a4,$b3,$fd
  .word $cef7 ; source pointer$ae85
  .byte $d7,$77,$83,$aa,$eb,$03,$04,$e4,$b2,$74,$fd
  .word $cef7 ; source pointer$ae92
  .byte $d7,$77,$83,$aa,$eb,$02,$04,$77,$d7,$76,$86,$1a,$eb,$00,$fb,$e2,$00,$e3,$b0,$fe,$02,$e2,$00,$30
  .byte $20,$00,$d7,$77,$83,$aa,$eb,$01,$04,$e3,$b2,$74,$d7,$76,$86,$1a,$eb,$00,$e2,$30,$20,$30,$20,$30
  .byte $60,$50,$e6,$01,$32,$f3,$63,$f0,$e6,$07,$e9,$31,$ea,$05,$fd
  .word $ce03 ; source pointer$aed3
  .byte $ea,$00,$50,$fe,$ff
  .word $ce2c ; source pointer$aeda
  .byte $d7,$33,$0f,$58,$eb,$03,$06,$e3,$71,$71,$61,$72,$72,$51,$32,$04,$f0,$d7,$37,$84,$19,$eb,$00,$e4
  .byte $32,$52,$ff,$d7,$76,$83,$45,$e3,$00,$e4,$b0,$e3,$00,$e8,$1a,$31,$e8,$45,$30,$20,$00,$ff,$d1,$18
  .byte $e4,$77,$61,$51,$41,$31,$21,$11,$01,$e5,$b0,$a1,$91,$81,$71,$61,$51,$41,$31,$21,$d7,$10,$e4,$50
  .byte $70,$fd
  .word $cf9e ; source pointer$af26
  .byte $00,$70,$e3,$01,$e4,$50,$60,$71,$32,$52,$31,$fd
  .word $cf9e ; source pointer$af34
  .byte $30,$a0,$e3,$31,$e4,$31,$a1,$32,$52,$61,$fb,$e4,$72,$a1,$e3,$00,$10,$20,$fe,$04,$fb,$e4,$51,$e3
  .byte $00,$fe,$02,$e4,$50,$e3,$00,$fb,$e4,$71,$e3,$20,$fe,$02,$e4,$70,$e3,$20,$d1,$01,$e4,$06,$76,$e3
  .byte $06,$e4,$36,$a6,$e3,$36,$e4,$26,$96,$e3,$26,$e4,$16,$86,$e3,$16,$d7,$10,$e4,$01,$c1,$fb,$e4,$62
  .byte $62,$61,$72,$72,$71,$fe,$02,$d1,$01,$fd
  .word $cfad ; source pointer$af88
  .byte $76,$76,$76,$76,$fd
  .word $cfad ; source pointer$af8f
  .byte $d7,$10,$e4,$70,$a0,$e3,$20,$e4,$20,$fe,$ff
  .word $cf25 ; source pointer$af9c
  .byte $e4,$00,$70,$e3,$01,$e4,$51,$61,$71,$c0,$31,$50,$70,$30,$ff,$fb,$e4,$66,$e3,$66,$fe,$04,$fb,$e4
  .byte $76,$e3,$76,$fe,$02,$ff,$d7,$21,$10,$10,$40,$40,$b0,$b0,$fb,$d7,$40,$40,$41,$b1,$41,$b1,$40,$b1
  .byte $b0,$41,$40,$40,$41,$b1,$41,$40,$b0,$b0,$40,$b0,$b0,$40,$40,$fe,$02,$fb,$b1,$41,$b1,$41,$b1,$40
  .byte $d1,$b0,$2c,$d7,$b0,$41,$fe,$03,$b1,$41,$b0,$40,$41,$b1,$fb,$40,$fe,$06,$40,$10,$10,$fb,$40,$10
  .byte $10,$40,$b0,$b0,$10,$10,$fe,$03,$b0,$41,$40,$40,$fb,$b1,$41,$b1,$41,$b1,$40,$b1,$b0,$40,$40,$fe
  .byte $02,$fe,$ff
  .word $cfc4 ; source pointer$b019
  .byte $d6,$78,$84,$12,$c3,$ea,$81,$d6,$b2,$81,$18,$eb,$01,$02,$fd
  .word $d0e7 ; source pointer$b02a
  .byte $fb,$e9,$b1,$d2,$31,$02,$12,$eb,$01,$02,$fd
  .word $d0f4 ; source pointer$b037
  .byte $92,$fd
  .word $d0ff ; source pointer$b03b
  .byte $fd
  .word $d114 ; source pointer$b03e
  .byte $72,$fd
  .word $d0ff ; source pointer$b042
  .byte $fd
  .word $d0f4 ; source pointer$b045
  .byte $f0,$e8,$1a,$e5,$72,$52,$71,$a0,$f1,$e8,$12,$e6,$02,$fd
  .word $d114 ; source pointer$b055
  .byte $f0,$e8,$1a,$e5,$72,$52,$71,$a0,$f1,$e8,$12,$e6,$02,$e3,$30,$40,$50,$e6,$06,$61,$a1,$61,$50,$30
  .byte $03,$f0,$e8,$1a,$e5,$71,$a3,$e4,$03,$f2,$e5,$72,$52,$71,$c0,$f0,$fe,$02,$d6,$70,$02,$18,$e9,$b1
  .byte $e5,$70,$a0,$b0,$e4,$00,$30,$90,$a0,$e9,$00,$d6,$b0,$01,$19,$e5,$71,$71,$fd
  .word $d120 ; source pointer$b09a
  .byte $f0,$e5,$a1,$a1,$ea,$04,$fd
  .word $d120 ; source pointer$b0a3
  .byte $ea,$81,$f0,$ec,$03,$e9,$b5,$d6,$74,$82,$18,$f0,$e3,$01,$01,$21,$01,$32,$22,$01,$31,$31,$51,$31
  .byte $62,$52,$31,$ec,$00,$e9,$b1,$d6,$72,$00,$15,$e4,$52,$52,$e3,$01,$27,$e4,$82,$81,$e3,$30,$e4,$a2
  .byte $a1,$e3,$50,$c1,$ea,$87,$d1,$b2,$80,$00,$c6,$fd
  .word $d12f ; source pointer$b0e1
  .byte $fe,$ff
  .word $d020 ; source pointer$b0e5
  .byte $f0,$e4,$02,$e5,$a2,$e4,$01,$33,$53,$72,$52,$72,$ff,$e3,$70,$80,$90,$e6,$06,$e3,$a1,$31,$a1,$ff
  .byte $f0,$e8,$1a,$e5,$52,$71,$a3,$e4,$03,$f2,$e5,$72,$52,$71,$c0,$f1,$e8,$12,$e6,$02,$ff,$e3,$50,$60
  .byte $70,$e6,$06,$81,$e4,$b1,$e3,$81,$ff,$f3,$e3,$01,$21,$32,$52,$31,$22,$02,$21,$32,$51,$30,$c1,$ff
  .byte $f2,$e3,$00,$10,$f1,$20,$30,$40,$50,$60,$f0,$80,$a0,$b0,$e2,$00,$20,$40,$60,$80,$e1,$30,$70,$90
  .byte $b0,$e0,$00,$e1,$b0,$a0,$90,$80,$f1,$70,$60,$50,$40,$30,$20,$f2,$10,$00,$e2,$b0,$a0,$90,$80,$70
  .byte $f3,$60,$50,$40,$30,$ff,$d6,$78,$84,$12,$c3,$ea,$81,$d6,$b6,$83,$18,$fd
  .word $d0e7 ; source pointer$b171
  .byte $fb,$e9,$b1,$d2,$75,$81,$11,$eb,$62,$05,$fd
  .word $d0f4 ; source pointer$b17e
  .byte $9f,$fd
  .word $d236 ; source pointer$b182
  .byte $d2,$75,$81,$11,$fd
  .word $d114 ; source pointer$b189
  .byte $7f,$fd
  .word $d236 ; source pointer$b18d
  .byte $d2,$75,$81,$11,$fd
  .word $d0f4 ; source pointer$b194
  .byte $98,$e6,$02,$e8,$11,$fd
  .word $d114 ; source pointer$b19c
  .byte $78,$e6,$02,$e8,$11,$30,$40,$50,$e6,$06,$e8,$d8,$61,$a1,$61,$50,$30,$0d,$fd
  .word $d236 ; source pointer$b1b1
  .byte $fe,$02,$e9,$71,$d6,$30,$01,$17,$e4,$20,$50,$60,$70,$a0,$e3,$00,$10,$e9,$71,$e4,$21,$21,$fd
  .word $d249 ; source pointer$b1ca
  .byte $e6,$06,$e8,$17,$f0,$51,$51,$ea,$04,$fd
  .word $d249 ; source pointer$b1d6
  .byte $ea,$81,$f0,$e9,$b1,$d6,$70,$01,$18,$e3,$71,$71,$91,$71,$e8,$14,$e6,$01,$90,$e6,$11,$a0,$e6,$06
  .byte $92,$71,$e8,$18,$a1,$a1,$e2,$01,$e3,$a1,$e2,$e8,$14,$e6,$01,$00,$e6,$11,$10,$e6,$06,$02,$e3,$a1
  .byte $e9,$71,$d6,$70,$01,$15,$02,$02,$51,$77,$32,$31,$80,$52,$51,$a0,$e6,$02,$f3,$a0,$90,$80,$70,$60
  .byte $50,$ea,$87,$d1,$b3,$80,$00,$fd
  .word $d12f ; source pointer$b228
  .byte $20,$10,$00,$e3,$b0,$a0,$90,$80,$fe,$ff
  .word $d16a ; source pointer$b234
  .byte $e8,$18,$e9,$30,$e4,$f0,$71,$f2,$70,$f0,$51,$f2,$50,$f0,$71,$f2,$70,$f0,$ff,$d6,$30,$16,$11,$e3
  .byte $51,$71,$82,$a2,$81,$72,$52,$71,$82,$a1,$80,$d2,$30,$01,$17,$f2,$70,$50,$20,$00,$e4,$b0,$80,$ff
  .byte $d6,$12,$c3,$ea,$81,$d3,$06,$e3,$05,$e4,$a5,$e3,$03,$d3,$06,$37,$57,$d3,$05,$05,$e4,$a5,$e3,$05
  .byte $fd
  .word $d2cc ; source pointer$b27f
  .byte $fd
  .word $d2cc ; source pointer$b282
  .byte $d3,$06,$e4,$71,$a1,$b1,$e3,$01,$31,$e4,$51,$61,$d3,$07,$e4,$73,$73,$fd
  .word $d306 ; source pointer$b296
  .byte $d3,$07,$a3,$a3,$ea,$04,$fd
  .word $d306 ; source pointer$b29f
  .byte $ea,$81,$fd
  .word $d315 ; source pointer$b2a4
  .byte $ea,$8a,$fd
  .word $d315 ; source pointer$b2a9
  .byte $ea,$81,$d3,$06,$55,$e3,$05,$53,$e4,$75,$e3,$25,$73,$e4,$85,$e3,$33,$81,$e4,$a5,$e3,$53,$d2,$20
  .byte $a3,$c4,$d6,$12,$c7,$fe,$ff
  .word $d269 ; source pointer$b2ca
  .byte $d6,$09,$c6,$fb,$d3,$06,$e3,$05,$e4,$a5,$e3,$03,$d3,$07,$37,$57,$d3,$05,$05,$e4,$a5,$e3,$03,$d6
  .byte $09,$c7,$fe,$02,$d3,$06,$fb,$05,$e4,$a5,$e3,$03,$35,$55,$33,$fe,$02,$05,$e4,$a5,$e3,$03,$d3,$07
  .byte $37,$57,$d3,$05,$05,$e4,$a5,$e3,$05,$ff,$d6,$10,$cb,$d3,$06,$e3,$75,$55,$73,$85,$a3,$81,$71,$51
  .byte $ff,$d6,$09,$e3,$01,$01,$d3,$06,$05,$d6,$09,$01,$01,$00,$d3,$06,$03,$03,$ff,$d6,$b0,$b1,$b0,$d6
  .byte $b2,$42,$40,$40,$21,$11,$21,$11,$b1,$40,$41,$40,$d1,$b0,$2f,$c0,$d4,$10,$10,$10,$d6,$24,$fd
  .word $d383 ; source pointer$b343
  .byte $fb,$1b,$15,$15,$fe,$02,$d6,$fd
  .word $d383 ; source pointer$b34d
  .byte $41,$43,$d6,$b2,$d4,$22,$42,$d6,$fd
  .word $d397 ; source pointer$b358
  .byte $21,$11,$fd
  .word $d397 ; source pointer$b35d
  .byte $41,$b1,$d6,$fb,$b1,$41,$b1,$40,$b1,$b0,$41,$b1,$41,$fe,$03,$b1,$41,$b1,$41,$b0,$fb,$40,$fe,$05
  .byte $d6,$40,$41,$10,$40,$10,$40,$40,$fe,$ff
  .word $d32b ; source pointer$b381
  .byte $fb,$b2,$42,$41,$21,$11,$21,$11,$fe,$07,$d1,$fb,$b0,$2f,$c0,$fe,$02,$b0,$2a,$ff,$b1,$b1,$fb,$11
  .byte $10,$10,$fe,$06,$ff,$ea,$85,$fd
  .word $d450 ; source pointer$b3a3
  .byte $ea,$00,$fd
  .word $d3fb ; source pointer$b3a8
  .byte $e4,$90,$70,$40,$30,$20,$00,$fd
  .word $d3fb ; source pointer$b3b2
  .byte $e3,$90,$70,$40,$30,$20,$00,$ea,$8c,$d6,$7a,$80,$1c,$fb,$e5,$91,$90,$90,$a3,$fe,$03,$e4,$00,$01
  .byte $00,$20,$40,$60,$80,$fb,$e5,$91,$90,$90,$a3,$fe,$02,$90,$91,$90,$a3,$d1,$34,$82,$11,$c8,$eb,$01
  .byte $02,$e1,$75,$45,$12,$d8,$bd,$86,$19,$e5,$90,$f2,$90,$f4,$90,$eb,$00,$ea,$00,$fe,$ff
  .word $d3a7 ; source pointer$b3f9
  .byte $d6,$bd,$86,$19,$e9,$71,$e5,$20,$20,$21,$d6,$32,$18,$12,$e4,$71,$91,$e3,$02,$e4,$b2,$a1,$d6,$bd
  .byte $86,$19,$e5,$20,$20,$21,$d6,$32,$18,$12,$e4,$71,$91,$e3,$02,$22,$41,$d6,$3d,$86,$19,$e5,$80,$80
  .byte $81,$d6,$32,$18,$12,$e3,$21,$31,$d6,$3d,$86,$19,$e5,$70,$70,$71,$d6,$32,$18,$12,$e3,$01,$21,$d6
  .byte $3d,$86,$11,$e5,$51,$21,$01,$23,$d6,$36,$83,$19,$ff,$d1,$75,$80,$00,$cb,$f2,$e2,$21,$11,$01,$e3
  .byte $f1,$b1,$a1,$91,$81,$f0,$71,$61,$51,$41,$31,$21,$11,$01,$e4,$b1,$ff,$fd
  .word $d450 ; source pointer$b46d
  .byte $fd
  .word $d4ed ; source pointer$b470
  .byte $e3,$20,$00,$e4,$90,$80,$70,$50,$e9,$00,$f0,$fd
  .word $d4ed ; source pointer$b47e
  .byte $e2,$20,$00,$e3,$90,$80,$70,$50,$e9,$00,$f0,$d6,$3a,$86,$19,$e9,$b1,$fb,$e4,$71,$70,$70,$e8,$49
  .byte $eb,$16,$00,$83,$eb,$00,$e8,$19,$fe,$03,$e8,$19,$a0,$a1,$a0,$e9,$31,$e3,$00,$20,$40,$60,$e9,$b1
  .byte $fb,$71,$70,$70,$e8,$49,$eb,$13,$00,$83,$eb,$00,$e8,$19,$fe,$02,$70,$71,$70,$e8,$49,$eb,$13,$00
  .byte $83,$eb,$00,$d6,$38,$84,$18,$e9,$71,$ec,$03,$e2,$70,$40,$10,$e3,$a0,$d8,$3a,$86,$19,$e9,$b1,$e4
  .byte $90,$f2,$90,$f4,$90,$e9,$00,$ec,$00,$fe,$ff
  .word $d46f ; source pointer$b4eb
  .byte $d6,$70,$18,$19,$e9,$31,$e3,$20,$20,$20,$f4,$e9,$00,$20,$f0,$e9,$31,$01,$21,$e8,$49,$52,$42,$31
  .byte $e8,$19,$e9,$31,$20,$20,$20,$f4,$e9,$00,$20,$f0,$e9,$31,$01,$21,$e8,$49,$52,$72,$91,$e8,$19,$e9
  .byte $31,$80,$80,$80,$f4,$e9,$00,$80,$f0,$e9,$31,$71,$81,$70,$70,$70,$f4,$e9,$00,$70,$f0,$e9,$31,$51
  .byte $71,$51,$21,$01,$eb,$24,$04,$23,$eb,$00,$f1,$ff,$d1,$20,$cb,$e2,$21,$11,$01,$e3,$b1,$a1,$91,$81
  .byte $71,$61,$51,$41,$31,$21,$11,$01,$e4,$b0,$fb,$fd
  .word $d5d0 ; source pointer$b559
  .byte $cb,$fd
  .word $d5d0 ; source pointer$b55d
  .byte $c5,$d1,$20,$e2,$b0,$a0,$90,$80,$70,$60,$b0,$a0,$90,$80,$70,$60,$80,$70,$60,$50,$40,$30,$20,$10
  .byte $00,$e3,$b0,$a0,$90,$80,$70,$60,$50,$40,$30,$c5,$d1,$02,$e4,$35,$35,$e3,$3b,$d6,$10,$c3,$d1,$02
  .byte $e4,$25,$25,$e3,$2b,$d6,$10,$c3,$01,$e4,$91,$71,$93,$c1,$d1,$20,$e2,$26,$10,$00,$e3,$b0,$a0,$90
  .byte $80,$70,$61,$51,$41,$31,$21,$fe,$02,$d3,$06,$fb,$e4,$37,$47,$fe,$03,$67,$87,$d3,$05,$fb,$e3,$37
  .byte $47,$fe,$03,$d1,$20,$e4,$9f,$81,$71,$61,$51,$9f,$c7,$fe,$ff
  .word $d557 ; source pointer$b5ce
  .byte $d1,$02,$e4,$95,$95,$e3,$9b,$d6,$10,$ff,$d1,$b3,$b3,$b3,$b0,$2f,$c6,$c1,$b0,$34,$fd
  .word $d602 ; source pointer$b5e5
  .byte $fd
  .word $d602 ; source pointer$b5e8
  .byte $fd
  .word $d629 ; source pointer$b5eb
  .byte $b5,$bb,$b5,$fb,$b0,$31,$22,$fe,$04,$fd
  .word $d629 ; source pointer$b5f7
  .byte $cb,$cb,$b0,$2a,$cb,$fe,$ff
  .word $d5e4 ; source pointer$b600
  .byte $fb,$d1,$b0,$24,$b0,$24,$b0,$2a,$cb,$4b,$cb,$4b,$cb,$4b,$fe,$02,$fb,$b0,$24,$b0,$24,$b0,$2a,$cb
  .byte $4b,$fe,$02,$b5,$b5,$bb,$bb,$bb,$40,$2a,$fb,$45,$fe,$06,$ff,$fb,$b0,$2a,$b5,$b5,$b0,$3a,$15,$15
  .byte $fe,$03,$ff,$d3,$78,$84,$12,$e4,$90,$b0,$e3,$10,$20,$40,$60,$70,$d6,$7a,$87,$1e,$e9,$31,$90,$90
  .byte $90,$f3,$e9,$00,$90,$f0,$d1,$78,$84,$12,$fd
  .word $d665 ; source pointer$b655
  .byte $12,$22,$42,$62,$72,$d3,$78,$84,$6a,$eb,$41,$00,$9f,$ff,$e4,$92,$b2,$e3,$12,$22,$42,$62,$72,$92
  .byte $b2,$e2,$ff,$d3,$36,$83,$12,$eb,$01,$02,$e4,$90,$b0,$e3,$10,$20,$40,$60,$70,$eb,$00,$d6,$38,$84
  .byte $19,$10,$10,$10,$f3,$10,$d1,$35,$82,$12,$eb,$01,$02,$e4,$92,$b2,$e3,$12,$22,$42,$eb,$00,$fd
  .word $d665 ; source pointer$b69e
  .byte $d3,$75,$82,$6a,$eb,$42,$00,$1f,$ff,$d3,$10,$c6,$d6,$10,$e4,$90,$90,$90,$c0,$d3,$20,$e5,$93,$d1
  .byte $20,$a1,$b1,$e4,$01,$11,$21,$31,$41,$51,$61,$71,$81,$d3,$20,$9f,$ff,$d3,$c6,$d1,$fb,$b0,$34,$fe
  .byte $03,$ff,$d4,$7a,$88,$1e,$e9,$31,$c5,$e5,$21,$21,$21,$41,$41,$41,$51,$51,$51,$71,$81,$91,$e9,$00
  .byte $e6,$01,$93,$93,$d1,$7a,$88,$1d,$c0,$e6,$06,$e5,$fd
  .word $d77f ; source pointer$b6f5
  .byte $ea,$8c,$fb,$90,$91,$fe,$03,$90,$e6,$01,$9a,$d6,$71,$0c,$12,$e2,$00,$20,$40,$70,$ea,$00,$d1,$7a
  .byte $88,$1a,$c0,$e6,$03,$e9,$31,$e5,$fd
  .word $d769 ; source pointer$b718
  .byte $93,$71,$51,$41,$fd
  .word $d769 ; source pointer$b71f
  .byte $75,$a3,$ea,$8e,$d3,$7d,$88,$1e,$e9,$31,$e5,$b1,$b1,$b1,$b1,$e6,$01,$ba,$ea,$82,$d6,$73,$11,$18
  .byte $ec,$02,$e9,$39,$e2,$50,$40,$30,$20,$10,$00,$e3,$b0,$a0,$90,$e6,$01,$86,$ec,$00,$d3,$7a,$88,$1a
  .byte $e9,$31,$e5,$fb,$b1,$b3,$fe,$04,$ea,$8e,$d3,$7d,$88,$1e,$b3,$e6,$01,$ba,$ea,$00,$fe,$ff
  .word $d6ec ; source pointer$b767
  .byte $21,$23,$23,$91,$e4,$21,$e5,$21,$41,$43,$49,$51,$53,$53,$e4,$01,$51,$e5,$51,$71,$73,$ff,$21,$21
  .byte $51,$21,$72,$82,$91,$ff,$ea,$8c,$d4,$78,$84,$18,$c5,$ec,$04,$e9,$39,$e2,$21,$11,$01,$e3,$b1,$a1
  .byte $91,$81,$71,$61,$51,$41,$31,$e6,$01,$93,$93,$e9,$00,$ec,$00,$ea,$00,$d6,$70,$0c,$12,$e9,$31,$e3
  .byte $fd
  .word $d77f ; source pointer$b7b2
  .byte $e9,$31,$e2,$00,$00,$f3,$e9,$00,$00,$f0,$e9,$31,$e3,$90,$90,$f3,$e9,$00,$90,$f0,$e9,$31,$80,$80
  .byte $f3,$e9,$00,$80,$f0,$e9,$31,$70,$70,$f3,$e9,$00,$70,$f0,$e9,$31,$50,$70,$90,$e2,$00,$e9,$71,$ea
  .byte $82,$d3,$76,$80,$18,$ec,$03,$e9,$3b,$fb,$e3,$71,$61,$41,$e4,$b1,$e3,$41,$61,$71,$91,$fe,$03,$b1
  .byte $71,$91,$b1,$e2,$11,$21,$41,$61,$fb,$71,$61,$41,$e3,$b1,$e2,$41,$61,$71,$91,$fe,$04,$e9,$00,$ec
  .byte $00,$f0,$ea,$82,$d6,$77,$82,$28,$eb,$21,$04,$e2,$b4,$eb,$00,$d6,$76,$80,$18,$ec,$02,$e9,$3b,$b0
  .byte $a0,$90,$80,$70,$60,$50,$40,$30,$20,$10,$ec,$00,$e9,$31,$d6,$30,$0c,$12,$e3,$b0,$b1,$a0,$a1,$90
  .byte $91,$80,$81,$71,$61,$ea,$00,$fe,$ff
  .word $d7aa ; source pointer$b84d
  .byte $d4,$0a,$c5,$e3,$91,$81,$71,$61,$51,$41,$31,$21,$11,$01,$e4,$b1,$a1,$d1,$01,$e3,$43,$43,$d3,$05
  .byte $e4,$93,$93,$e3,$03,$e4,$93,$e3,$25,$35,$43,$e4,$fb,$41,$43,$fe,$04,$d1,$20,$e3,$94,$81,$71,$61
  .byte $51,$41,$31,$20,$10,$00,$e4,$b0,$a0,$90,$80,$d6,$18,$e3,$24,$e4,$90,$80,$90,$53,$43,$55,$70,$80
  .byte $95,$b0,$e3,$10,$24,$e4,$90,$80,$90,$e3,$45,$50,$70,$55,$41,$21,$71,$a1,$e2,$21,$d6,$18,$e2,$13
  .byte $d1,$20,$13,$00,$e3,$b0,$a0,$90,$80,$70,$60,$50,$d6,$18,$e5,$c5,$d1,$20,$e2,$45,$31,$21,$11,$01
  .byte $e3,$b1,$a0,$90,$80,$70,$60,$50,$40,$30,$d6,$18,$e4,$90,$e3,$10,$40,$70,$10,$40,$70,$a0,$40,$70
  .byte $a0,$e2,$10,$d4,$14,$e3,$a0,$e2,$10,$40,$70,$d1,$20,$70,$60,$50,$40,$30,$20,$10,$00,$fe,$ff
  .word $d865 ; source pointer$b8f6
  .byte $d1,$43,$43,$43,$43,$b3,$b3,$fb,$47,$fe,$06,$40,$26,$40,$26,$fb,$b0,$26,$fe,$04,$b0,$32,$b0,$32
  .byte $d1,$bb,$bb,$b0,$3a,$bb,$b0,$2f,$c0,$b0,$2f,$c0,$b0,$34,$b0,$34,$fb,$b5,$bb,$b5,$b0,$3a,$fe,$02
  .byte $fb,$b0,$34,$fe,$04,$d1,$fb,$b5,$b5,$b0,$34,$b5,$b0,$2a,$b0,$3a,$fe,$07,$b5,$fb,$b5,$b0,$34,$fe
  .byte $02,$b0,$34,$b0,$34,$fb,$b0,$24,$fe,$05,$b0,$2a,$d6,$c9,$d1,$fb,$b5,$fe,$0e,$b0,$2a,$fe,$ff
  .word $d910 ; source pointer$b957
  .byte $d1,$36,$82,$19,$e9,$71,$e4,$63,$73,$93,$b3,$e3,$13,$23,$43,$ea,$85,$fd
  .word $d990 ; source pointer$b96b
  .byte $d5,$36,$82,$6a,$64,$e9,$00,$eb,$01,$02,$f4,$70,$b0,$70,$f3,$b0,$70,$b0,$70,$f2,$b0,$70,$b0,$70
  .byte $b0,$70,$f4,$b0,$70,$b0,$f5,$70,$b0,$70,$ff,$e2,$24,$04,$e3,$b4,$e8,$3b,$9f,$e8,$19,$e2,$04,$e3
  .byte $b4,$95,$75,$46,$57,$ff,$d1,$78,$84,$19,$f2,$e3,$23,$43,$63,$f1,$73,$93,$b3,$f0,$e2,$13,$fd
  .word $d990 ; source pointer$b9b4
  .byte $d8,$78,$84,$ea,$eb,$42,$00,$6f,$ff,$d4,$10,$c6,$d5,$10,$e3,$25,$d4,$07,$03,$d1,$10,$c1,$d3,$06
  .byte $76,$d5,$20,$2f,$ff,$d1,$fb,$13,$fe,$07,$b4,$44,$44,$40,$23,$14,$14,$b4,$44,$45,$45,$46,$47,$41
  .byte $d8,$25,$ff,$d7,$b4,$83,$12,$c3,$e9,$31,$fd
  .word $da12 ; source pointer$b9f1
  .byte $e3,$70,$fd
  .word $da12 ; source pointer$b9f6
  .byte $e3,$b0,$fd
  .word $da12 ; source pointer$b9fb
  .byte $e3,$80,$e8,$18,$90,$90,$90,$90,$e6,$01,$c0,$e8,$9c,$7f,$e6,$07,$eb,$21,$05,$96,$ff,$e3,$90,$ec
  .byte $02,$20,$e8,$1a,$e4,$91,$e3,$91,$21,$e8,$12,$ec,$00,$70,$00,$e4,$70,$e3,$71,$00,$e4,$70,$ff,$d7
  .byte $77,$84,$12,$c3,$e9,$b1,$fd
  .word $da57 ; source pointer$ba34
  .byte $e2,$00,$fd
  .word $da57 ; source pointer$ba39
  .byte $e2,$40,$fd
  .word $da57 ; source pointer$ba3e
  .byte $e2,$10,$e8,$18,$20,$20,$20,$20,$e6,$01,$c0,$e8,$9a,$0f,$e6,$07,$e7,$83,$eb,$22,$00,$27,$ff,$e2
  .byte $20,$ec,$02,$e3,$90,$e8,$1a,$21,$e2,$21,$e3,$91,$e8,$12,$ec,$00,$e2,$00,$e3,$70,$00,$e2,$01,$e3
  .byte $70,$00,$ff,$d7,$09,$c3,$d1,$01,$fb,$e4,$26,$96,$e3,$2d,$e4,$2d,$9d,$26,$96,$e3,$26,$e4,$2d,$96
  .byte $e3,$2d,$fe,$03,$e4,$26,$26,$26,$26,$c0,$0e,$c0,$d7,$11,$27,$ff,$d1,$41,$4b,$41,$4b,$d7,$fb,$b0
  .byte $b0,$41,$b1,$41,$b0,$b0,$40,$b1,$b0,$40,$b0,$fe,$03,$40,$40,$40,$40,$d1,$c0,$b0,$2e,$b0,$2f,$cf
  .byte $cf,$cf,$ff,$d4,$74,$80,$10,$f2,$e4,$00,$20,$f1,$40,$50,$70,$f0,$90,$b0,$d6,$b5,$83,$66,$eb,$22
  .byte $00,$e3,$09,$e4,$71,$42,$e3,$40,$0b,$02,$00,$01,$09,$02,$00,$01,$03,$01,$03,$e4,$83,$79,$41,$72
  .byte $e3,$00,$45,$41,$43,$43,$e8,$66,$57,$97,$87,$57,$e8,$10,$fb,$e9,$b0,$e3,$01,$f1,$e9,$70,$e9,$31
  .byte $ec,$01,$e8,$19,$00,$40,$70,$e2,$00,$40,$70,$e1,$00,$e2,$70,$40,$00,$e3,$70,$40,$00,$e4,$70,$e9
  .byte $00,$ec,$00,$f0,$e8,$10,$fe,$02,$e9,$b0,$e3,$01,$f1,$e9,$70,$e9,$31,$ec,$01,$e8,$19,$00,$50,$90
  .byte $e2,$00,$50,$90,$e1,$00,$e2,$90,$50,$00,$e3,$90,$50,$00,$e4,$90,$e9,$00,$ec,$00,$f0,$e8,$10,$e9
  .byte $b0,$e3,$01,$f1,$e9,$70,$e9,$31,$ec,$01,$e8,$19,$e4,$80,$e3,$00,$50,$80,$e2,$00,$50,$e1,$00,$e2
  .byte $80,$50,$00,$e3,$80,$50,$00,$e4,$80,$ec,$00,$e9,$00,$f0,$d6,$b5,$82,$66,$e3,$77,$e2,$01,$e4,$71
  .byte $e3,$02,$40,$43,$e9,$31,$41,$ec,$01,$01,$e8,$19,$e9,$70,$f1,$40,$00,$40,$00,$90,$80,$70,$60,$e9
  .byte $00,$ec,$00,$f0,$e8,$22,$51,$f2,$e9,$70,$e9,$31,$e8,$19,$ec,$01,$e2,$00,$20,$e3,$90,$f1,$e2,$00
  .byte $20,$50,$00,$f0,$20,$50,$90,$20,$50,$90,$e1,$00,$f0,$e9,$00,$e9,$b0,$e8,$22,$ec,$00,$e3,$81,$f2
  .byte $e9,$70,$e9,$31,$e8,$19,$ec,$01,$e2,$20,$50,$e3,$b0,$f1,$e2,$20,$50,$80,$20,$f0,$50,$80,$b0,$50
  .byte $80,$b0,$e1,$20,$ec,$00,$e9,$00,$d4,$b5,$83,$16,$fb,$fd
  .word $dc25 ; source pointer$bbe6
  .byte $fd
  .word $dc25 ; source pointer$bbe9
  .byte $21,$e9,$70,$f1,$51,$e2,$01,$e9,$b0,$f0,$e3,$21,$21,$21,$23,$23,$23,$fe,$02,$e9,$70,$fb,$e4,$41
  .byte $f2,$41,$f3,$41,$f0,$41,$41,$41,$fe,$02,$21,$f2,$21,$f3,$21,$f0,$21,$21,$21,$fb,$21,$f2,$21,$f0
  .byte $fe,$03,$d1,$73,$80,$00,$fd
  .word $dc3a ; source pointer$bc22
  .byte $ff,$e3,$41,$e9,$70,$f1,$71,$eb,$01,$02,$e2,$01,$eb,$00,$e9,$b0,$f0,$e3,$41,$41,$41,$ff,$e4,$4b
  .byte $30,$20,$10,$f1,$00,$e5,$b0,$a0,$90,$f2,$80,$70,$60,$50,$40,$f3,$30,$20,$10,$00,$ff,$d4,$76,$83
  .byte $15,$f2,$e4,$40,$50,$70,$f1,$90,$b0,$e3,$f0,$00,$20,$d6,$30,$05,$66,$e9,$71,$eb,$22,$00,$e3,$49
  .byte $01,$e4,$72,$e3,$90,$7b,$52,$40,$e8,$18,$71,$e8,$66,$59,$52,$40,$e8,$18,$71,$e8,$66,$53,$31,$23
  .byte $02,$20,$49,$e4,$71,$e3,$02,$40,$eb,$00,$95,$91,$eb,$21,$00,$b3,$e2,$03,$e8,$64,$0d,$e8,$18,$e9
  .byte $00,$f1,$20,$00,$f0,$e9,$71,$e8,$64,$e3,$bf,$e8,$66,$eb,$22,$00,$e3,$49,$e4,$71,$e3,$02,$40,$7b
  .byte $e2,$02,$40,$e8,$18,$71,$e8,$66,$eb,$21,$00,$59,$52,$40,$e8,$18,$71,$e8,$66,$53,$31,$23,$02,$20
  .byte $e2,$49,$e3,$01,$42,$70,$eb,$00,$95,$91,$eb,$21,$00,$b3,$e2,$03,$e8,$96,$0f,$2f,$dc,$30,$05,$00
  .byte $e2,$0f,$dc,$34,$80,$f8,$eb,$01,$00,$e9,$31,$0f,$d4,$78,$84,$16,$eb,$00,$fb,$e9,$31,$e3,$01,$e9
  .byte $71,$f3,$01,$f4,$01,$f0,$e9,$31,$01,$01,$01,$fe,$03,$fb,$01,$f3,$e9,$71,$01,$f0,$e9,$31,$fe,$03
  .byte $d1,$75,$80,$00,$ea,$08,$fd
  .word $dc3a ; source pointer$bd1b
  .byte $ff,$d4,$10,$c3,$d1,$20,$e3,$77,$60,$50,$40,$30,$fd
  .word $dd5c ; source pointer$bd2a
  .byte $fb,$fd
  .word $dd95 ; source pointer$bd2e
  .byte $fe,$02,$fd
  .word $dd5c ; source pointer$bd33
  .byte $e3,$d3,$06,$2d,$d3,$05,$21,$23,$27,$23,$e4,$fd
  .word $dd95 ; source pointer$bd41
  .byte $d4,$06,$fb,$e3,$05,$01,$01,$01,$05,$01,$01,$01,$e4,$a5,$a1,$a1,$a1,$a3,$a3,$a3,$fe,$03,$e3,$04
  .byte $ff,$d3,$06,$e3,$0d,$d3,$05,$01,$03,$07,$03,$d3,$06,$e4,$ad,$d3,$05,$a1,$a3,$a7,$a3,$d3,$06,$9d
  .byte $d3,$05,$91,$93,$97,$93,$d3,$06,$8d,$d3,$05,$81,$83,$87,$83,$d3,$06,$7d,$d3,$05,$71,$73,$77,$73
  .byte $d3,$06,$6d,$d3,$05,$61,$63,$67,$63,$ff,$d3,$06,$7d,$d3,$05,$71,$73,$77,$73,$ff,$d4,$c6,$fb,$fd
  .word $dde3 ; source pointer$bda3
  .byte $fe,$08,$d1,$fb,$bb,$1b,$4b,$15,$b5,$bb,$b0,$2a,$cb,$4b,$fe,$04,$fb,$fd
  .word $dde3 ; source pointer$bdb7
  .byte $fe,$04,$d1,$fb,$b0,$2f,$c6,$b0,$26,$b0,$26,$b0,$26,$b0,$2f,$c6,$b0,$26,$b0,$26,$b0,$26,$b0,$2f
  .byte $c6,$b0,$26,$b0,$26,$b0,$26,$b0,$2e,$b0,$2e,$b0,$2e,$fe,$03,$b0,$26,$ff,$d6,$b1,$11,$41,$10,$b0
  .byte $b1,$b1,$41,$b1,$ff,$d7,$75,$83,$12,$e3,$20,$00,$20,$f2,$00,$20,$f0,$e4,$90,$e3,$00,$20,$e4,$72
  .byte $62,$51,$e8,$1a,$e9,$31,$e5,$90,$e4,$00,$20,$50,$70,$90,$e3,$00,$d1,$73,$80,$00,$26,$e9,$00,$10
  .byte $00,$e4,$b0,$a0,$90,$f1,$80,$f2,$70,$f3,$60,$f4,$50,$f5,$40,$c2,$f7,$e3,$26,$10,$00,$f8,$e4,$b0
  .byte $a0,$90,$ff,$d7,$37,$84,$12,$e3,$70,$50,$70,$f4,$50,$70,$f0,$20,$50,$70,$e8,$53,$02,$e4,$b2,$a1
  .byte $e8,$1a,$20,$50,$70,$a0,$e3,$00,$20,$50,$d1,$35,$80,$00,$76,$60,$50,$40,$30,$20,$f1,$10,$f2,$00
  .byte $f3,$e4,$b0,$f4,$a0,$f5,$90,$c2,$f7,$e3,$76,$60,$50,$f8,$40,$30,$20,$ff,$d7,$10,$e4,$70,$50,$70
  .byte $e3,$70,$e4,$70,$20,$50,$70,$e3,$02,$e4,$b2,$a1,$20,$50,$70,$a0,$e3,$00,$20,$50,$d1,$20,$76,$40
  .byte $30,$20,$10,$00,$ff,$d7,$b0,$40,$42,$40,$40,$40,$d1,$b0,$29,$c9,$b0,$29,$c9,$b0,$2c,$d7,$b0,$fb
  .byte $40,$fe,$06,$d1,$40,$29,$ff
  .word $def2 ; source pointer$beb0
  .word $def7 ; source pointer$beb2
  .word $defc ; source pointer$beb4
  .byte $00,$bf,$00,$bf
  .word $df00 ; source pointer$beba
  .byte $06,$bf,$06,$bf
  .word $df06 ; source pointer$bec0
  .word $df11 ; source pointer$bec2
  .byte $18,$bf,$18,$bf
  .word $df18 ; source pointer$bec8
  .byte $20,$bf
  .word $df20 ; source pointer$becc
  .word $df26 ; source pointer$bece
  .byte $2e,$bf
  .word $df2e ; source pointer$bed2
  .word $df36 ; source pointer$bed4
  .word $df3e ; source pointer$bed6
  .byte $46,$bf
  .word $df46 ; source pointer$beda
  .word $df50 ; source pointer$bedc
  .word $df5b ; source pointer$bede
  .word $df65 ; source pointer$bee0
  .word $df74 ; source pointer$bee2
  .byte $84,$bf
  .word $df84 ; source pointer$bee6
  .byte $86,$bf
  .word $df8a ; source pointer$beea
  .word $df95 ; source pointer$beec
  .word $df9e ; source pointer$beee
  .word $dfaa ; source pointer$bef0
  .byte $17,$16,$25,$14,$ff,$17,$16,$25,$14,$ff,$13,$14,$13,$ff,$16,$17,$16,$15,$14,$ff,$18,$17,$16,$15
  .byte $14,$13,$21,$15,$14,$23,$ff,$12,$13,$14,$13,$12,$11,$ff,$17,$16,$25,$14,$21,$22,$11,$ff,$17,$18
  .byte $17,$16,$15,$ff,$16,$17,$18,$19,$18,$17,$16,$ff,$1a,$19,$18,$17,$16,$15,$10,$ff,$18,$17,$16,$15
  .byte $14,$20,$13,$ff,$13,$14,$15,$16,$15,$14,$13,$ff,$18,$14,$18,$14,$17,$14,$16,$15,$14,$ff,$16,$25
  .byte $24,$13,$12,$51,$14,$13,$12,$11,$ff,$29,$28,$27,$16,$15,$14,$30,$17,$16,$ff,$17,$16,$15,$14,$13
  .byte $12,$15,$14,$13,$22,$13,$15,$13,$12,$ff,$20,$fb,$11,$12,$13,$12,$11,$10,$1f,$1e,$1d,$1e,$1f,$10
  .byte $fe,$ff,$11,$ff,$14,$11,$10,$ff,$fb,$11,$12,$11,$20,$1f,$1e,$1f,$20,$fe,$ff,$fb,$11,$12,$11,$20
  .byte $3f,$20,$fe,$ff,$16,$14,$12,$11,$10,$fb,$31,$20,$3f,$20,$fe,$ff,$17,$16,$15,$14,$13,$12,$11,$10
  .byte $fb,$11,$12,$11,$20,$1f,$1e,$1f,$20,$fe,$ff,$ff,$ff,$ff,$ff,$ff,$ff,$ff,$ff,$ff,$ff,$ff,$ff,$ff
  .byte $ff,$ff,$ff,$ff,$ff,$ff,$ff,$ff,$ff,$ff,$ff,$ff,$ff,$ff,$d8,$78,$ee,$ff,$ff,$4c,$10,$c3,$00,$00
  .byte $00,$00,$00,$00,$00,$00,$00,$53,$54,$49,$4e,$47,$45,$52,$00,$00,$00,$00,$38,$02,$01,$06,$a4,$1b
  .byte $a3,$c3,$d8,$bf,$12,$c4
.assert *=$e000,lderror,"Native B footprint"
TnNativeInit=$a000
TnNativePlay=$a644
TnNativeCommand=$b057
.export TnNativeInit,TnNativePlay,TnNativeCommand
.popseg
