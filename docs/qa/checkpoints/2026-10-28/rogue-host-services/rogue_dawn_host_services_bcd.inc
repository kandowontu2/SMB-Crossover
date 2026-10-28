; Generated literal BCD instructions from authenticated1.21; do not hand edit.
.export RdHsDecimalAdd
RdHsDecimalAdd:
RdHsBCD_C3DA: JSR RdHsBCD_C41D ; actual62:C3DA 201dc4
RdHsBCD_C3DD: ADC R2 ; actual62:C3DD 6501
RdHsBCD_C3DF: CMP #$0a ; actual62:C3DF c90a
RdHsBCD_C3E1: BCC RdHsBCD_C3E5 ; actual62:C3E1 9002
RdHsBCD_C3E3: ADC #$05 ; actual62:C3E3 6905
RdHsBCD_C3E5: CLC ; actual62:C3E5 18
RdHsBCD_C3E6: ADC R3 ; actual62:C3E6 6502
RdHsBCD_C3E8: STA R3 ; actual62:C3E8 8502
RdHsBCD_C3EA: LDA R4 ; actual62:C3EA a503
RdHsBCD_C3EC: AND #$f0 ; actual62:C3EC 29f0
RdHsBCD_C3EE: ADC R3 ; actual62:C3EE 6502
RdHsBCD_C3F0: BCC RdHsBCD_C3F6 ; actual62:C3F0 9004
RdHsBCD_C3F2: ADC #$5f ; actual62:C3F2 695f
RdHsBCD_C3F4: SEC ; actual62:C3F4 38
RdHsBCD_C3F5: RTS ; actual62:C3F5 60
RdHsBCD_C3F6: CMP #$a0 ; actual62:C3F6 c9a0
RdHsBCD_C3F8: BCS RdHsBCD_C3F2 ; actual62:C3F8 b0f8
RdHsBCD_C3FA: RTS ; actual62:C3FA 60
.export RdHsDecimalSub
RdHsDecimalSub:
RdHsBCD_C3FB: JSR RdHsBCD_C41D ; actual62:C3FB 201dc4
RdHsBCD_C3FE: SBC R2 ; actual62:C3FE e501
RdHsBCD_C400: STA R2 ; actual62:C400 8501
RdHsBCD_C402: BCS RdHsBCD_C40E ; actual62:C402 b00a
RdHsBCD_C404: ADC #$0a ; actual62:C404 690a
RdHsBCD_C406: STA R2 ; actual62:C406 8501
RdHsBCD_C408: LDA R3 ; actual62:C408 a502
RdHsBCD_C40A: ADC #$0f ; actual62:C40A 690f
RdHsBCD_C40C: STA R3 ; actual62:C40C 8502
RdHsBCD_C40E: LDA R4 ; actual62:C40E a503
RdHsBCD_C410: AND #$f0 ; actual62:C410 29f0
RdHsBCD_C412: SEC ; actual62:C412 38
RdHsBCD_C413: SBC R3 ; actual62:C413 e502
RdHsBCD_C415: BCS RdHsBCD_C41A ; actual62:C415 b003
RdHsBCD_C417: ADC #$a0 ; actual62:C417 69a0
RdHsBCD_C419: CLC ; actual62:C419 18
RdHsBCD_C41A: ORA R2 ; actual62:C41A 0501
RdHsBCD_C41C: RTS ; actual62:C41C 60
.export RdHsSplitBCD
RdHsSplitBCD:
RdHsBCD_C41D: PHA ; actual62:C41D 48
RdHsBCD_C41E: AND #$0f ; actual62:C41E 290f
RdHsBCD_C420: STA R2 ; actual62:C420 8501
RdHsBCD_C422: PLA ; actual62:C422 68
RdHsBCD_C423: AND #$f0 ; actual62:C423 29f0
RdHsBCD_C425: STA R3 ; actual62:C425 8502
RdHsBCD_C427: LDA R4 ; actual62:C427 a503
RdHsBCD_C429: AND #$0f ; actual62:C429 290f
RdHsBCD_C42B: RTS ; actual62:C42B 60

.proc RdHsDamage
 jsr RdHostEnabled
 bcc No
 lda R6
 ora R7
 beq No
 lda RdAction
 cmp #7
 beq No
 cmp #8
 beq No
 cmp #$ff
 beq No
 lda RdGear
 and #$20
 beq Debit
 lsr R6
 lsr R7
 bcc Debit
 lda #$4f
 adc R6
 sta R6
Debit:
 lda RdHealthLo
 sta R4
 lda R6
 sec
 jsr RdHsDecimalSub
 sta RdHealthLo
 lda RdHealthHi
 sta R4
 lda R7
 jsr RdHsDecimalSub
 sta RdHealthHi
 RdHsLeaf RD_LEAF_DAMAGE_COMPLETE
 lda #0
 sta R6
 sta R7
 sec
 rts
No:clc
 rts
.endproc
.proc RdHsAddBCD
 lda RdHealthLo
 sta R4
 lda R6
 clc
 jsr RdHsDecimalAdd
 sta RdHealthLo
 lda RdHealthHi
 sta R4
 lda R7
 jsr RdHsDecimalAdd
 sta RdHealthHi
 lda RdTanks
 asl
 asl
 asl
 asl
 ora #$0f
 cmp RdHealthHi
 bcs Done
 and #$f9
 sta RdHealthHi
 lda #$99
 sta RdHealthLo
Done:
 lda #0
 sta R6
 sta R7
 rts
.endproc

