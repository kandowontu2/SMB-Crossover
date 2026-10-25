; Original nine-track Punch-Out music; non-indirect ZP fields directly owned.
.pushseg
.segment "MAC_NATIVE_AUDIO"
LmNativeDirectZp=1
LmNativeRam=XgLzHistory
LmNativeZp=XgLzHistory+$100
LmNativeSavedZp=XgLzHistory+$110
LmNativePending=XgAudioSelection
LmNativeBankStart:
::LmDirect8000:
  LDA #$c0
  STA $4017
  JSR ::LmDirect8025
  JSR ::LmDirect80CA
  JSR ::LmDirect84B1
  JSR ::LmDirect88E2
  LDA #$00
  STA ::LmNativeZp+$00
  STA ::LmNativeZp+$01
  STA ::LmNativeZp+$02
  STA ::LmNativeZp+$03
  RTS
  .byte $a4,$f7,$c0,$06,$b0,$59,$c8,$84,$f3
::LmDirect8025:
  LDY ::LmNativeZp+$03
  BMI ::LmDirect807B
  BNE ::LmDirect8040
  LDA ::LmNativeZp+$07
  CMP #$01
  BEQ ::LmDirect8084
  LDA ::LmNativeZp+$07
  BEQ ::LmDirect807F
  .byte $ce,$1e,$07,$f0,$e2,$ce,$1f,$07,$f0,$40,$60
::LmDirect8040:
  .byte $84,$f7,$a9,$0e,$8d,$1e,$07,$a2,$05,$a5,$f7,$c9,$07,$d0,$02,$a2
  .byte $03,$8e,$1f,$07,$98,$0a,$a8,$b9,$66,$f7,$8d,$12,$40,$b9,$67,$f7
  .byte $8d,$13,$40,$a2,$4f,$a5,$f7,$c9,$01,$f0,$02,$a2,$0f,$8e,$10,$40
  .byte $a9,$0f,$8d,$15,$40,$a9,$1f,$8d,$15,$40,$60
::LmDirect807B:
  .byte $a9,$00,$85,$f7
::LmDirect807F:
  LDA #$0f
  jsr GuestNativeStatusSTA
::LmDirect8084:
  RTS
::LmDirect8085:
  .byte $a9,$40,$20,$ef,$f4,$a9,$1a,$8d,$13,$07,$a2,$9f,$a0,$83,$20,$0b
  .byte $f4
::LmDirect8096:
  .byte $ad,$12,$07,$c9,$40,$b0,$07,$4a,$4a,$09,$90,$8d,$00,$40,$ad,$12
  .byte $07,$29,$07,$d0,$1c,$ad,$13,$07,$4a,$4a,$4a,$4a,$38,$6d,$13,$07
  .byte $8d,$13,$07,$2a,$2a,$2a,$8d,$02,$40,$2a,$29,$07,$09,$08,$8d,$03
  .byte $40,$4c,$3e,$81
::LmDirect80CA:
  LDY ::LmNativeZp+$00
  BMI ::LmDirect8143
  LDA ::LmNativeZp+$04
  CPY #$01
  BEQ ::LmDirect8085
  CMP #$01
  BEQ ::LmDirect8096
  CPY #$02
  BEQ ::LmDirect80EB
  CMP #$02
  BEQ ::LmDirect80F9
  CPY #$03
  BEQ ::LmDirect8124
  CMP #$03
  BEQ ::LmDirect8132
  JMP ::LmDirect81C7
::LmDirect80EB:
  .byte $a9,$7f,$20,$ef,$f4,$a2,$9c,$a0,$7f,$a9,$62,$20,$26,$f4
::LmDirect80F9:
  .byte $ad,$12,$07,$c9,$6c,$f0,$21,$90,$0b,$29,$07,$a8,$b9,$76,$f7,$8d
  .byte $01,$40,$d0,$14,$c9,$6b,$d0,$05,$a0,$a5,$8c,$01,$40,$c9,$30,$b0
  .byte $07,$4a,$4a,$09,$90,$8d,$00,$40,$4c,$3e,$81
::LmDirect8124:
  .byte $a9,$16,$20,$ef,$f4,$a2,$5f,$a0,$8b,$a9,$12,$20,$26,$f4
::LmDirect8132:
  .byte $ad,$12,$07,$c9,$10,$b0,$05,$09,$50,$8d,$00,$40,$ce,$12,$07,$d0
  .byte $2c
::LmDirect8143:
  .byte $ad,$24,$07,$f0,$0a,$a9,$10,$8d,$0c,$40,$a9,$00,$8d,$24,$07,$ad
  .byte $25,$07,$f0,$0a,$a9,$10,$8d,$04,$40,$a9,$00,$8d,$25,$07,$a9,$00
  .byte $8d,$26,$07,$a9,$00,$85,$f4,$a9,$10,$8d,$00,$40,$60
::LmDirect8170:
  .byte $a9,$04,$20,$18,$f5,$a2,$0a,$a9,$1a,$a0,$08,$8c,$0f,$40,$8e,$0e
  .byte $40,$8d,$0c,$40,$a2,$da,$a0,$85,$a9,$24,$20,$26,$f4
::LmDirect818D:
  .byte $4c,$3e,$81
::LmDirect8190:
  .byte $a9,$20,$20,$ef,$f4,$a9,$ff,$8d,$13,$07,$a2,$1e,$a0,$81,$20,$0b
  .byte $f4
::LmDirect81A1:
  .byte $ad,$13,$07,$a8,$20,$50,$f4,$8d,$13,$07,$2a,$2a,$8d,$02,$40,$2a
  .byte $29,$03,$09,$08,$8d,$03,$40,$ad,$12,$07,$c9,$0e,$b0,$05,$09,$90
  .byte $8d,$00,$40,$4c,$3e,$81
::LmDirect81C7:
  CPY #$04
  BEQ ::LmDirect8170
  CMP #$04
  BEQ ::LmDirect818D
  CPY #$05
  BEQ ::LmDirect8190
  CMP #$05
  BEQ ::LmDirect81A1
  CPY #$06
  BEQ ::LmDirect81F2
  CMP #$06
  BEQ ::LmDirect81F7
  CPY #$07
  BEQ ::LmDirect8215
  CMP #$07
  BEQ ::LmDirect821A
  CPY #$08
  BEQ ::LmDirect8222
  CMP #$08
  BEQ ::LmDirect8230
  JMP ::LmDirect827F
::LmDirect81F2:
  .byte $a9,$10,$20,$18,$f5
::LmDirect81F7:
  .byte $ac,$12,$07,$b9,$7d,$f7,$aa,$29,$0f,$8d,$0e,$40,$8a,$4a,$4a,$4a
  .byte $4a,$09,$10,$8d,$0c,$40,$a9,$08,$8d,$0f,$40,$4c,$3e,$81
::LmDirect8215:
  .byte $a9,$0a,$20,$18,$f5
::LmDirect821A:
  .byte $ac,$12,$07,$b9,$8d,$f7,$d0,$db
::LmDirect8222:
  .byte $a9,$10,$20,$ef,$f4,$a2,$43,$a0,$84,$a9,$4c,$20,$26,$f4
::LmDirect8230:
  .byte $4c,$3e,$81
::LmDirect8233:
  .byte $a9,$04,$20,$ef,$f4,$a9,$7f,$8d,$01,$40,$ee,$13,$07,$ad,$13,$07
  .byte $29,$0f,$a8,$b9,$9c,$f7,$20,$29,$f4
::LmDirect824C:
  .byte $ac,$12,$07,$b9,$97,$f7,$8d,$00,$40,$4c,$3e,$81
::LmDirect8258:
  .byte $a9,$04,$20,$ef,$f4,$a9,$bc,$8d,$01,$40,$ee,$13,$07,$ad,$13,$07
  .byte $29,$0f,$a8,$a5,$f4,$c9,$0b,$f0,$05,$b9,$ac,$f7,$d0,$03,$b9,$bc
  .byte $f7,$20,$29,$f4
::LmDirect827C:
  .byte $4c,$4c,$82
::LmDirect827F:
  CPY #$09
  BEQ ::LmDirect8233
  CMP #$09
  BEQ ::LmDirect824C
  CPY #$0a
  BEQ ::LmDirect8258
  CMP #$0a
  BEQ ::LmDirect827C
  CPY #$0b
  BEQ ::LmDirect8258
  CMP #$0b
  BEQ ::LmDirect827C
  CPY #$0c
  BEQ ::LmDirect82A2
  CMP #$0c
  BEQ ::LmDirect82BE
  JMP ::LmDirect8316
::LmDirect82A2:
  .byte $a9,$40,$20,$94,$f4,$a2,$88,$8e,$00,$40,$8e,$04,$40,$a9,$58,$20
  .byte $29,$f4,$a9,$22,$8d,$06,$40,$a9,$08,$8d,$07,$40
::LmDirect82BE:
  .byte $ad,$12,$07,$c9,$28,$d0,$08,$a2,$8f,$8e,$00,$40,$8e,$04,$40,$4c
  .byte $3e,$81
::LmDirect82D0:
  .byte $a9,$0f,$20,$94,$f4,$a9,$00,$8d,$13,$07
::LmDirect82DA:
  .byte $ad,$12,$07,$4a,$18,$6d,$13,$07,$a8,$b9,$cc,$f7,$20,$cd,$f4,$b9
  .byte $eb,$f7,$20,$dd,$f4,$4c,$3e,$81
::LmDirect82F2:
  .byte $a9,$12,$20,$94,$f4,$a9,$08,$8d,$13,$07,$d0,$dc
::LmDirect82FE:
  .byte $a9,$1e,$20,$94,$f4,$a9,$08,$8d,$13,$07,$d0,$d0
::LmDirect830A:
  .byte $a9,$0c,$20,$94,$f4,$a9,$18,$8d,$13,$07,$d0,$c4
::LmDirect8316:
  CPY #$0d
  BEQ ::LmDirect82D0
  CMP #$0d
  BEQ ::LmDirect82DA
  CPY #$0e
  BEQ ::LmDirect82F2
  CMP #$0e
  BEQ ::LmDirect82DA
  CPY #$0f
  BEQ ::LmDirect82FE
  CMP #$0f
  BEQ ::LmDirect82DA
  CPY #$10
  BEQ ::LmDirect830A
  CMP #$10
  BEQ ::LmDirect82DA
  CPY #$11
  BEQ ::LmDirect8359
  CMP #$11
  BEQ ::LmDirect835E
  CPY #$12
  BEQ ::LmDirect8367
  CMP #$12
  BEQ ::LmDirect8375
  CPY #$13
  BEQ ::LmDirect8378
  CMP #$13
  BEQ ::LmDirect8386
  CPY #$14
  BEQ ::LmDirect8395
  CMP #$14
  BEQ ::LmDirect83A3
  JMP ::LmDirect8402
::LmDirect8359:
  .byte $a9,$05,$20,$18,$f5
::LmDirect835E:
  .byte $ac,$12,$07,$b9,$09,$f8,$4c,$fd,$81
::LmDirect8367:
  .byte $a9,$20,$20,$ef,$f4,$a2,$98,$a0,$7f,$a9,$64,$20,$26,$f4
::LmDirect8375:
  .byte $4c,$3e,$81
::LmDirect8378:
  .byte $a9,$12,$20,$ef,$f4,$a2,$5f,$a0,$8b,$a9,$0e,$20,$26,$f4
::LmDirect8386:
  .byte $ad,$12,$07,$c9,$0c,$b0,$05,$09,$50,$8d,$00,$40,$4c,$3e,$81
::LmDirect8395:
  .byte $a9,$06,$20,$ef,$f4,$a2,$95,$a0,$7f,$a9,$4a,$20,$26,$f4
::LmDirect83A3:
  .byte $ad,$12,$07,$c9,$03,$d0,$05,$a9,$42,$20,$29,$f4,$4c,$3e,$81
::LmDirect83B2:
  .byte $a9,$04,$8d,$13,$07,$a9,$18,$a0,$15,$4c,$a4,$82
::LmDirect83BE:
  .byte $ad,$12,$07,$c9,$01,$d0,$05,$ce,$13,$07,$d0,$ed,$4c,$be,$82
::LmDirect83CD:
  .byte $a9,$24,$20,$ef,$f4,$ce,$12,$07,$a9,$8f,$8d,$13,$07,$a2,$9c,$a0
  .byte $82,$20,$0b,$f4
::LmDirect83E1:
  .byte $ad,$12,$07,$c9,$12,$f0,$ea,$ad,$13,$07,$a8,$20,$4f,$f4,$8d,$13
  .byte $07,$2a,$2a,$8d,$02,$40,$2a,$29,$03,$09,$08,$8d,$03,$40,$4c,$3e
  .byte $81
::LmDirect8402:
  CPY #$15
  BEQ ::LmDirect83B2
  CMP #$15
  BEQ ::LmDirect83BE
  CPY #$16
  BEQ ::LmDirect83CD
  CMP #$16
  BEQ ::LmDirect83E1
  CPY #$17
  BEQ ::LmDirect8423
  CMP #$17
  BEQ ::LmDirect8431
  CPY #$18
  BEQ ::LmDirect8440
  CMP #$18
  BEQ ::LmDirect8463
  RTS
::LmDirect8423:
  .byte $a9,$10,$20,$ef,$f4,$a2,$82,$a0,$a2,$a9,$56,$20,$26,$f4
::LmDirect8431:
  .byte $ad,$12,$07,$c9,$0e,$d0,$05,$a9,$3e,$20,$29,$f4,$4c,$3e,$81
::LmDirect8440:
  .byte $a9,$20,$20,$18,$f5,$a9,$09,$8d,$0c,$40,$a9,$0f,$8d,$0e,$40,$a9
  .byte $08,$8d,$0f,$40,$a9,$0f,$8d,$08,$40,$a9,$00,$8d,$0a,$40,$a9,$09
  .byte $8d,$0b,$40
::LmDirect8463:
  .byte $4c,$3e,$81,$ad,$15,$07,$29,$07,$d0,$1c,$ad,$16,$07,$4a,$4a,$4a
  .byte $4a,$38,$6d,$16,$07,$8d,$16,$07,$2a,$2a,$2a,$8d,$06,$40,$2a,$29
  .byte $07,$09,$08,$8d,$07,$40,$60
::LmDirect848A:
  .byte $84,$f5,$a9,$40,$8d,$15,$07,$a9,$1a,$8d,$16,$07,$a2,$9f,$a0,$83
  .byte $20,$14,$f4
::LmDirect849D:
  .byte $ad,$15,$07,$c9,$40,$b0,$07,$4a,$4a,$09,$90,$8d,$04,$40,$20,$66
  .byte $84,$4c,$14,$85
::LmDirect84B1:
  LDA ::LmNativeRam+$25
  BEQ ::LmDirect84BB
  .byte $a9,$00,$85,$f5,$60
::LmDirect84BB:
  LDY ::LmNativeZp+$01
  BMI ::LmDirect8519
  LDA ::LmNativeZp+$05
  CPY #$01
  BEQ ::LmDirect848A
  CMP #$01
  BEQ ::LmDirect849D
  CPY #$02
  BEQ ::LmDirect84DC
  CMP #$02
  BEQ ::LmDirect84EC
  CPY #$03
  BEQ ::LmDirect8523
  CMP #$03
  BEQ ::LmDirect852F
  JMP ::LmDirect85B0
::LmDirect84DC:
  .byte $84,$f5,$a9,$7f,$8d,$15,$07,$a2,$9c,$a0,$7f,$a9,$62,$20,$1b,$f4
::LmDirect84EC:
  .byte $ad,$15,$07,$c9,$6c,$f0,$21,$90,$0b,$29,$07,$a8,$b9,$0f,$f8,$8d
  .byte $05,$40,$d0,$14,$c9,$6b,$d0,$05,$a0,$a5,$8c,$05,$40,$c9,$30,$b0
  .byte $07,$4a,$4a,$09,$90,$8d,$04,$40,$ce,$15,$07,$d0,$09
::LmDirect8519:
  .byte $a9,$00,$85,$f5,$a9,$10,$8d,$04,$40,$60
::LmDirect8523:
  .byte $84,$f5,$a9,$10,$8d,$15,$07,$a9,$04,$8d,$16,$07
::LmDirect852F:
  .byte $ac,$16,$07,$ad,$15,$07,$d9,$16,$f8,$d0,$16,$a2,$84,$20,$12,$f4
  .byte $ac,$16,$07,$b9,$1a,$f8,$8d,$06,$40,$a9,$08,$8d,$07,$40,$ce,$16
  .byte $07,$4c,$14,$85
::LmDirect8553:
  .byte $84,$f5,$a9,$20,$8d,$15,$07,$a2,$1a,$a0,$cd,$a9,$42,$d0,$0d
::LmDirect8562:
  .byte $ad,$15,$07,$c9,$18,$d0,$09,$a2,$94,$a0,$c5,$a9,$50,$20,$1b,$f4
  .byte $4c,$14,$85
::LmDirect8575:
  .byte $84,$f5,$a9,$10,$8d,$15,$07,$a9,$38,$d0,$09
::LmDirect8580:
  .byte $ad,$15,$07,$c9,$0c,$d0,$0a,$a9,$44,$a2,$cd,$8e,$05,$40,$20,$1e
  .byte $f4,$ac,$15,$07,$b9,$58,$f8,$8d,$04,$40,$4c,$14,$85
::LmDirect859D:
  .byte $84,$f5,$a9,$10,$8d,$15,$07,$a2,$43,$a0,$84,$a9,$4c,$20,$1b,$f4
::LmDirect85AD:
  .byte $4c,$14,$85
::LmDirect85B0:
  CPY #$04
  BEQ ::LmDirect8553
  CMP #$04
  BEQ ::LmDirect8562
  CPY #$05
  BEQ ::LmDirect8575
  CMP #$05
  BEQ ::LmDirect8580
  CPY #$06
  BEQ ::LmDirect859D
  CMP #$06
  BEQ ::LmDirect85AD
  CPY #$07
  BEQ ::LmDirect85DB
  CMP #$07
  BEQ ::LmDirect85EB
  CPY #$08
  BEQ ::LmDirect85FA
  CMP #$08
  BEQ ::LmDirect860A
  JMP ::LmDirect8666
::LmDirect85DB:
  .byte $84,$f5,$a9,$16,$8d,$15,$07,$a2,$5f,$a0,$8b,$a9,$0e,$20,$1b,$f4
::LmDirect85EB:
  .byte $ad,$15,$07,$c9,$10,$b0,$05,$09,$50,$8d,$04,$40,$4c,$14,$85
::LmDirect85FA:
  .byte $84,$f5,$a9,$10,$8d,$15,$07,$a2,$85,$a0,$85,$a9,$1c,$20,$1b,$f4
::LmDirect860A:
  .byte $4c,$14,$85
::LmDirect860D:
  .byte $84,$f5,$a9,$20,$8d,$15,$07,$a9,$8f,$8d,$16,$07,$a2,$5d,$a0,$81
  .byte $20,$14,$f4
::LmDirect8620:
  .byte $ad,$16,$07,$a8,$20,$4f,$f4,$8d,$16,$07,$2a,$2a,$8d,$06,$40,$2a
  .byte $29,$03,$09,$08,$8d,$07,$40,$ad,$15,$07,$c9,$0d,$b0,$05,$09,$90
  .byte $8d,$04,$40,$4c,$14,$85
::LmDirect8646:
  .byte $84,$f5,$a9,$10,$8d,$15,$07,$a9,$ff,$8d,$16,$07,$a2,$5d,$a0,$81
  .byte $20,$14,$f4
::LmDirect8659:
  .byte $ad,$16,$07,$a8,$20,$50,$f4,$8d,$16,$07,$4c,$2a,$86
::LmDirect8666:
  CPY #$09
  BEQ ::LmDirect860D
  CMP #$09
  BEQ ::LmDirect8620
  CPY #$0a
  BEQ ::LmDirect8646
  CMP #$0a
  BEQ ::LmDirect8659
  CPY #$0b
  BEQ ::LmDirect8681
  CMP #$0b
  BEQ ::LmDirect8691
  JMP ::LmDirect86D9
::LmDirect8681:
  .byte $84,$f5,$a9,$18,$8d,$15,$07,$a2,$c8,$a0,$cc,$a9,$34,$20,$1b,$f4
::LmDirect8691:
  .byte $4c,$14,$85
::LmDirect8694:
  .byte $84,$f5,$a9,$0c,$8d,$15,$07,$a2,$03,$a0,$c5,$20,$14,$f4,$a9,$38
  .byte $d0,$10
::LmDirect86A6:
  .byte $ad,$15,$07,$c9,$08,$d0,$0c,$a2,$02,$a0,$cc,$20,$14,$f4,$a9,$48
  .byte $4c,$6f,$85,$4c,$14,$85
::LmDirect86BC:
  .byte $84,$f5,$a9,$10,$8d,$15,$07,$a2,$88,$a0,$d3,$a9,$1c,$20,$1b,$f4
  .byte $a9,$3a,$20,$22,$f4,$a9,$1c,$8d,$08,$40
::LmDirect86D6:
  .byte $4c,$14,$85
::LmDirect86D9:
  CPY #$0c
  BEQ ::LmDirect8694
  CMP #$0c
  BEQ ::LmDirect86A6
  CPY #$0d
  BEQ ::LmDirect86BC
  CMP #$0d
  BEQ ::LmDirect86D6
  CPY #$0e
  BEQ ::LmDirect86FC
  CMP #$0e
  BEQ ::LmDirect870F
  CPY #$0f
  BEQ ::LmDirect872B
  CMP #$0f
  BEQ ::LmDirect873F
  JMP ::LmDirect87D9
::LmDirect86FC:
  .byte $84,$f5,$a9,$0a,$8d,$15,$07,$a9,$1a,$8d,$16,$07,$a2,$9f,$a0,$83
  .byte $20,$14,$f4
::LmDirect870F:
  .byte $ad,$15,$07,$c9,$06,$90,$05,$20,$66,$84,$d0,$0d,$c9,$05,$d0,$09
  .byte $a2,$81,$a0,$8b,$a9,$34,$20,$1b,$f4,$4c,$14,$85
::LmDirect872B:
  .byte $84,$f5,$a9,$18,$8d,$15,$07,$a9,$14,$8d,$16,$07,$a2,$9e,$a0,$b3
  .byte $a9,$40,$d0,$0e
::LmDirect873F:
  .byte $ad,$15,$07,$cd,$16,$07,$d0,$09,$a2,$86,$a0,$c5,$a9,$5e,$20,$1b
  .byte $f4,$4c,$14,$85,$84,$f5,$a9,$60,$8d,$15,$07,$a9,$0c,$8d,$16,$07
  .byte $a9,$0f,$8d,$17,$07,$a9,$00,$8d,$28,$07,$a9,$04,$8d,$29,$07
::LmDirect876E:
  .byte $ac,$17,$07,$ad,$28,$07,$f0,$05,$b9,$45,$f8,$d0,$03,$b9,$35,$f8
  .byte $8d,$04,$40,$ad,$15,$07,$ac,$16,$07,$d9,$22,$f8,$d0,$3f,$c8,$98
  .byte $4a,$a8,$b9,$2e,$f8,$8d,$17,$07,$ad,$16,$07,$4a,$b0,$06,$a9,$ca
  .byte $a2,$00,$f0,$04,$a9,$bb,$a2,$01,$8e,$28,$07,$8d,$05,$40,$ad,$16
  .byte $07,$f0,$03,$ce,$16,$07,$ac,$29,$07,$b9,$1e,$f8,$8d,$06,$40,$b9
  .byte $54,$f8,$8d,$07,$40,$88,$d0,$02,$a0,$04,$8c,$29,$07,$ad,$17,$07
  .byte $f0,$03,$ce,$17,$07,$4c,$14,$85
::LmDirect87D6:
  .byte $4c,$53,$87
::LmDirect87D9:
  CPY #$10
  BEQ ::LmDirect87D6
  CMP #$10
  BEQ ::LmDirect876E
  CPY #$11
  BEQ ::LmDirect87F4
  CMP #$11
  BEQ ::LmDirect8807
  CPY #$12
  BEQ ::LmDirect8823
  CMP #$12
  BEQ ::LmDirect8836
  JMP ::LmDirect88B6
::LmDirect87F4:
  .byte $84,$f5,$a9,$08,$8d,$15,$07,$a9,$1f,$8d,$16,$07,$a2,$9a,$a0,$83
  .byte $20,$14,$f4
::LmDirect8807:
  .byte $ad,$15,$07,$c9,$04,$90,$05,$20,$66,$84,$d0,$0d,$c9,$03,$d0,$09
  .byte $a2,$81,$a0,$8b,$a9,$50,$20,$1b,$f4,$4c,$14,$85
::LmDirect8823:
  .byte $84,$f5,$a9,$40,$8d,$15,$07,$a9,$ff,$8d,$16,$07,$a2,$1e,$a0,$82
  .byte $20,$14,$f4
::LmDirect8836:
  .byte $ad,$16,$07,$a8,$20,$4f,$f4,$8d,$16,$07,$2a,$2a,$8d,$06,$40,$2a
  .byte $29,$03,$09,$08,$8d,$07,$40,$ad,$15,$07,$c9,$0c,$b0,$05,$09,$90
  .byte $8d,$04,$40,$4c,$14,$85
::LmDirect885C:
  .byte $84,$f5,$a9,$10,$8d,$15,$07,$a2,$82,$a0,$a2,$a9,$56,$20,$1b,$f4
::LmDirect886C:
  .byte $ad,$15,$07,$c9,$0e,$d0,$05,$a9,$3e,$20,$1e,$f4,$4c,$14,$85
::LmDirect887B:
  .byte $84,$f5,$a9,$20,$8d,$15,$07,$a9,$7f,$d0,$05,$a9,$5f,$ce,$15,$07
  .byte $8d,$16,$07,$a2,$9e,$a0,$82,$20,$14,$f4
::LmDirect8895:
  .byte $ad,$15,$07,$c9,$10,$f0,$ea,$ad,$16,$07,$a8,$20,$4e,$f4,$8d,$16
  .byte $07,$2a,$2a,$8d,$06,$40,$2a,$29,$03,$09,$08,$8d,$07,$40,$4c,$14
  .byte $85
::LmDirect88B6:
  CPY #$13
  BEQ ::LmDirect885C
  CMP #$13
  BEQ ::LmDirect886C
  CPY #$14
  BEQ ::LmDirect887B
  CMP #$14
  BEQ ::LmDirect8895
  CPY #$15
  BEQ ::LmDirect88CF
  CMP #$15
  BEQ ::LmDirect88DF
  RTS
::LmDirect88CF:
  .byte $84,$f5,$a9,$10,$8d,$15,$07,$a2,$c8,$a0,$ac,$a9,$42,$20,$1b,$f4
::LmDirect88DF:
  .byte $4c,$14,$85
::LmDirect88E2:
  LDA ::LmNativeZp+$02
  BMI ::LmDirect8902
  CMP #$1b
  BEQ ::LmDirect8902
  CMP #$1c
  BEQ ::LmDirect8902
  LDA ::LmNativeZp+$02
  BNE ::LmDirect88F9
  LDA ::LmNativeZp+$06
  BEQ ::LmDirect8960
  JMP ::LmDirect8A0A
::LmDirect88F9:
  JMP ::LmDirect8964
::LmDirect88FC:
  LDA ::LmNativeZp+$06
  CMP #$1a
  BCS ::LmDirect8969
::LmDirect8902:
  LDA #$00
  STA ::LmNativeZp+$06
::LmDirect8906:
  LDA ::LmNativeRam+$24
  BEQ ::LmDirect8922
  .byte $a5,$f5,$f0,$0c,$a9,$10,$8d,$00,$40,$a9,$00,$8d,$08,$40,$f0,$3a
  .byte $a9,$10,$8d,$04,$40,$d0,$ef
::LmDirect8922:
  LDA ::LmNativeRam+$26
  BEQ ::LmDirect8934
  .byte $a5,$f5,$f0,$02,$d0,$0c,$a9,$10,$8d,$04,$40,$d0,$19
::LmDirect8934:
  LDA ::LmNativeRam+$25
  BEQ ::LmDirect893D
  .byte $a9,$10,$d0,$10
::LmDirect893D:
  LDA ::LmNativeZp+$05
  BEQ ::LmDirect8945
  .byte $a9,$10,$d0,$05
::LmDirect8945:
  LDA #$10
  jsr LmNativeSTA04
  jsr LmNativeSTA00
  jsr LmNativeSTA0C
  LDA #$00
  jsr LmNativeSTA08
  LDA #$00
  STA ::LmNativeRam+$08
  STA ::LmNativeRam+$09
  STA ::LmNativeRam+$20
::LmDirect8960:
  RTS
::LmDirect8961:
  JMP ::LmDirect88FC
::LmDirect8964:
  TAX
  JSR ::LmDirect8906
  TXA
::LmDirect8969:
  STA ::LmNativeZp+$06
  STA ::LmNativeRam+$0a
  LDY #$00
  STY ::LmNativeRam+$0b
::LmDirect8973:
  LDY ::LmNativeRam+$0a
  LDA ::LmDirect8FFF,y
  CLC
  ADC ::LmNativeRam+$0b
  INC ::LmNativeRam+$0b
  TAY
  LDA ::LmDirect9000,y
  TAY
  BEQ ::LmDirect8961
  LDA ::LmNativeZp+$06
  CMP #$10
  BCS ::LmDirect89C3
  LDA ::LmDirect9069,y
  STA ::LmNativeRam+$0d
  LDA ::LmDirect906A,y
  STA $f8
  LDA ::LmDirect906B,y
  STA $f9
  LDA ::LmDirect906C,y
  STA ::LmNativeRam+$22
  LDA ::LmDirect906D,y
  STA ::LmNativeZp+$0d
  LDA ::LmDirect906E,y
  STA ::LmNativeRam+$23
  STA ::LmNativeRam+$0c
  LDA ::LmDirect906F,y
  STA ::LmNativeRam+$1c
  LDA ::LmDirect9070,y
  STA ::LmNativeRam+$1d
  JMP ::LmDirect89F3
::LmDirect89C0:
  JMP ::LmDirect8973
::LmDirect89C3:
  LDA ::LmDirect90DE,y
  STA ::LmNativeRam+$0d
  LDA ::LmDirect90DF,y
  STA $f8
  LDA ::LmDirect90E0,y
  STA $f9
  LDA ::LmDirect90E1,y
  STA ::LmNativeRam+$22
  LDA ::LmDirect90E2,y
  STA ::LmNativeZp+$0d
  LDA ::LmDirect90E3,y
  STA ::LmNativeRam+$23
  STA ::LmNativeRam+$0c
  LDA ::LmDirect90E4,y
  STA ::LmNativeRam+$1c
  LDA ::LmDirect90E5,y
  STA ::LmNativeRam+$1d
::LmDirect89F3:
  LDA #$00
  STA ::LmNativeZp+$0c
  LDA #$01
  STA ::LmNativeRam+$00
  STA ::LmNativeRam+$01
  STA ::LmNativeRam+$02
  STA ::LmNativeRam+$03
  LDA #$7f
  STA ::LmNativeRam+$0e
::LmDirect8A0A:
  LDA ::LmNativeZp+$05
  BNE ::LmDirect8A13
  LDA ::LmNativeRam+$25
  BEQ ::LmDirect8A2B
::LmDirect8A13:
  .byte $ad,$1c,$07,$c9,$40,$b0,$0c,$a9,$3f,$8d,$08,$07,$a9,$01,$8d,$1a
  .byte $07,$d0,$05,$a9,$00,$8d,$08,$07
::LmDirect8A2B:
  DEC ::LmNativeRam+$00
  BEQ ::LmDirect8A38
  BNE ::LmDirect8A69
::LmDirect8A32:
  JSR ::LmDirectF400
  STA ::LmNativeRam+$04
::LmDirect8A38:
  LDY ::LmNativeZp+$0c
  INC ::LmNativeZp+$0c
  LDA ($f8),Y
  jeq ::LmDirect89C0
  BMI ::LmDirect8A32
  STA ::LmNativeRam+$18
  LDY ::LmNativeZp+$05
  BNE ::LmDirect8A63
  LDY ::LmNativeRam+$25
  BNE ::LmDirect8A63
  JSR ::LmDirectF41E
  BEQ ::LmDirect8A63
  LDA ::LmNativeRam+$1c
  CMP #$80
  BCC ::LmDirect8A5E
  LDA #$7f
  BNE ::LmDirect8A60
::LmDirect8A5E:
  LDA #$3f
::LmDirect8A60:
  STA ::LmNativeRam+$08
::LmDirect8A63:
  LDA ::LmNativeRam+$04
  STA ::LmNativeRam+$00
::LmDirect8A69:
  LDA ::LmNativeZp+$05
  BNE ::LmDirect8AB1
  LDA ::LmNativeRam+$25
  BNE ::LmDirect8AB1
  LDA ::LmNativeRam+$1c
  CMP #$40
  BCS ::LmDirect8A98
  LDA ::LmNativeRam+$18
  CMP #$02
  BEQ ::LmDirect8A94
  LDX ::LmNativeRam+$1a
  BEQ ::LmDirect8A8D
  .byte $20,$1e,$f4,$a2,$00,$8e,$1a,$07
::LmDirect8A8D:
  LDA ::LmNativeRam+$00
  CMP #$02
  BCS ::LmDirect8A98
::LmDirect8A94:
  LDX #$10
  BNE ::LmDirect8AAE
::LmDirect8A98:
  JSR ::LmDirectF472
  LDA ::LmNativeRam+$08
  BEQ ::LmDirect8AA5
  LSR A
  LSR A
  DEC ::LmNativeRam+$08
::LmDirect8AA5:
  CLC
  ADC ::LmNativeRam+$1c
  TAY
  LDA ::LmDirectF674,y
  TAX
::LmDirect8AAE:
  JSR ::LmDirectF412
::LmDirect8AB1:
  LDA ::LmNativeZp+$0d
  BNE ::LmDirect8AB8
  .byte $4c,$63,$8b
::LmDirect8AB8:
  LDA ::LmNativeZp+$04
  BEQ ::LmDirect8AD4
  .byte $ad,$1d,$07,$c9,$40,$b0,$0c,$a9,$3f,$8d,$09,$07,$a9,$01,$8d,$1b
  .byte $07,$d0,$05,$a9,$00,$8d,$09,$07
::LmDirect8AD4:
  DEC ::LmNativeRam+$01
  BEQ ::LmDirect8AE1
  BNE ::LmDirect8B18
::LmDirect8ADB:
  JSR ::LmDirectF400
  STA ::LmNativeRam+$05
::LmDirect8AE1:
  LDY ::LmNativeZp+$0d
  INC ::LmNativeZp+$0d
  LDA ($f8),Y
  BMI ::LmDirect8ADB
  BNE ::LmDirect8AF6
  .byte $a4,$fd,$e6,$fd,$b1,$f8,$8d,$0e,$07,$d0,$eb
::LmDirect8AF6:
  STA ::LmNativeRam+$19
  LDY ::LmNativeZp+$04
  BNE ::LmDirect8B12
  JSR ::LmDirectF429
  BEQ ::LmDirect8B12
  LDA ::LmNativeRam+$1d
  CMP #$80
  BCC ::LmDirect8B0D
  .byte $a9,$7f,$d0,$02
::LmDirect8B0D:
  LDA #$3f
  STA ::LmNativeRam+$09
::LmDirect8B12:
  LDA ::LmNativeRam+$05
  STA ::LmNativeRam+$01
::LmDirect8B18:
  LDA ::LmNativeZp+$04
  BNE ::LmDirect8B63
  LDA ::LmNativeRam+$1d
  CMP #$40
  BCS ::LmDirect8B42
  LDA ::LmNativeRam+$19
  CMP #$02
  BEQ ::LmDirect8B3E
  LDX ::LmNativeRam+$1b
  BEQ ::LmDirect8B37
  .byte $20,$29,$f4,$a2,$00,$8e,$1b,$07
::LmDirect8B37:
  LDA ::LmNativeRam+$01
  CMP #$02
  BCS ::LmDirect8B42
::LmDirect8B3E:
  LDX #$10
  BNE ::LmDirect8B58
::LmDirect8B42:
  JSR ::LmDirectF463
  LDA ::LmNativeRam+$09
  BEQ ::LmDirect8B4F
  LSR A
  LSR A
  DEC ::LmNativeRam+$09
::LmDirect8B4F:
  CLC
  ADC ::LmNativeRam+$1d
  TAY
  LDA ::LmDirectF674,y
  TAX
::LmDirect8B58:
  LDY ::LmNativeRam+$0e
  JSR ::LmDirectF40B
  BNE ::LmDirect8B63
::LmDirect8B60:
  .byte $4c,$1b,$8c
::LmDirect8B63:
  LDY ::LmNativeRam+$22
  BEQ ::LmDirect8B60
  DEC ::LmNativeRam+$2a
  DEC ::LmNativeRam+$02
  BEQ ::LmDirect8B78
  BNE ::LmDirect8BD2
::LmDirect8B72:
  JSR ::LmDirectF400
  STA ::LmNativeRam+$06
::LmDirect8B78:
  LDY ::LmNativeRam+$22
  INC ::LmNativeRam+$22
  LDA ($f8),Y
  BMI ::LmDirect8B72
  LDY ::LmNativeZp+$05
  CPY #$0d
  BEQ ::LmDirect8BA1
  LDY ::LmNativeZp+$04
  CPY #$18
  BEQ ::LmDirect8BA1
  CMP #$02
  BNE ::LmDirect8B99
  LDY #$00
  jsr LmNativeSTY08
  BEQ ::LmDirect8BA1
::LmDirect8B99:
  LDY #$81
  jsr LmNativeSTY08
  JSR ::LmDirectF422
::LmDirect8BA1:
  LDA ::LmNativeRam+$06
  STA ::LmNativeRam+$02
  LDY ::LmNativeZp+$06
  CPY #$15
  BEQ ::LmDirect8BB1
  CPY #$04
  BCS ::LmDirect8BD2
::LmDirect8BB1:
  CMP #$0b
  BCS ::LmDirect8BCD
  TAX
  SEC
  SBC #$02
  STA ::LmNativeRam+$2b
  TXA
  LSR A
  STA ::LmNativeRam+$2a
  CMP #$04
  BCS ::LmDirect8BC9
  LDA #$00
  BEQ ::LmDirect8BCF
::LmDirect8BC9:
  LDA #$01
  BNE ::LmDirect8BCF
::LmDirect8BCD:
  LDA #$02
::LmDirect8BCF:
  STA ::LmNativeRam+$2c
::LmDirect8BD2:
  LDA ::LmNativeZp+$05
  CMP #$0d
  BEQ ::LmDirect8C1B
  LDA ::LmNativeZp+$04
  CMP #$18
  BEQ ::LmDirect8C1B
  LDA ::LmNativeZp+$06
  CMP #$15
  BEQ ::LmDirect8BE8
  CMP #$04
  BCS ::LmDirect8C0F
::LmDirect8BE8:
  LDA ::LmNativeRam+$2c
  CMP #$01
  BEQ ::LmDirect8BFD
  CMP #$02
  BEQ ::LmDirect8C06
  LDA ::LmNativeRam+$02
  CMP ::LmNativeRam+$2b
  BNE ::LmDirect8C1B
  BEQ ::LmDirect8C16
::LmDirect8BFD:
  LDA ::LmNativeRam+$2a
  CMP #$02
  BNE ::LmDirect8C1B
  BEQ ::LmDirect8C16
::LmDirect8C06:
  LDA ::LmNativeRam+$02
  CMP #$07
  BNE ::LmDirect8C1B
  BEQ ::LmDirect8C16
::LmDirect8C0F:
  LDA ::LmNativeRam+$02
  CMP #$02
  BNE ::LmDirect8C1B
::LmDirect8C16:
  LDA #$00
  jsr LmNativeSTA08
::LmDirect8C1B:
  LDA ::LmNativeRam+$23
  BEQ ::LmDirect8C8B
  LDA ::LmNativeRam+$24
  BEQ ::LmDirect8C2A
  .byte $a9,$00,$8d,$20,$07
::LmDirect8C2A:
  DEC ::LmNativeRam+$03
  BEQ ::LmDirect8C37
  BNE ::LmDirect8C71
::LmDirect8C31:
  JSR ::LmDirectF400
  STA ::LmNativeRam+$07
::LmDirect8C37:
  LDY ::LmNativeRam+$23
  INC ::LmNativeRam+$23
  LDA ($f8),Y
  BMI ::LmDirect8C31
  BNE ::LmDirect8C4B
  LDA ::LmNativeRam+$0c
  STA ::LmNativeRam+$23
  BNE ::LmDirect8C37
::LmDirect8C4B:
  TAY
  STA ::LmNativeRam+$21
  LDA ::LmNativeRam+$24
  BNE ::LmDirect8C6B
  LDA ::LmDirectF73A,y
  jsr LmNativeSTA0C
  LDA ::LmDirectF73B,y
  jsr LmNativeSTA0E
  LDA ::LmDirectF73C,y
  jsr GuestNativeStoreSTA0f
  LDA #$27
  STA ::LmNativeRam+$20
::LmDirect8C6B:
  LDA ::LmNativeRam+$07
  STA ::LmNativeRam+$03
::LmDirect8C71:
  LDA ::LmNativeRam+$21
  CMP #$26
  BCC ::LmDirect8C8B
  LDA ::LmNativeRam+$24
  BNE ::LmDirect8C8B
  LDY ::LmNativeRam+$20
  BEQ ::LmDirect8C85
  DEC ::LmNativeRam+$20
::LmDirect8C85:
  LDA ::LmDirectF714,y
  jsr LmNativeSTA0C
::LmDirect8C8B:
  RTS
::LmDirectF400:
  AND #$1f
  CLC
  ADC ::LmNativeRam+$0d
  TAY
  LDA ::LmDirectF5BC,y
  RTS
::LmDirectF40B:
  jsr LmNativeSTX00
  jsr GuestNativeStoreSTY01
  RTS
::LmDirectF412:
  LDY #$7f
  jsr LmNativeSTX04
  jsr GuestNativeStoreSTY05
  RTS
  .byte $20,$14,$f4
::LmDirectF41E:
  LDX #$04
  BNE ::LmDirectF42B
::LmDirectF422:
  LDX #$08
  BNE ::LmDirectF42B
  .byte $20,$0b,$f4
::LmDirectF429:
  LDX #$00
::LmDirectF42B:
  TAY
  LDA ::LmDirectF53D,y
  BEQ ::LmDirectF44C
  jsr GuestNativeStoreSTA02X
  CPX #$00
  BNE ::LmDirectF43D
  STA ::LmNativeRam+$0f
  BNE ::LmDirectF444
::LmDirectF43D:
  CPX #$04
  BNE ::LmDirectF444
  STA ::LmNativeRam+$10
::LmDirectF444:
  LDA ::LmDirectF53C,y
  ORA #$08
  jsr GuestNativeStoreSTA03X
::LmDirectF44C:
  RTS
  .byte $4a,$4a,$4a,$4a,$4a,$4a,$85,$e0,$d0,$02,$e6,$e0,$98,$38,$e5,$e0
  .byte $60,$ad,$12,$07,$d0,$03
::LmDirectF463:
  LDA ::LmNativeRam+$01
  LDX #$00
  LDY ::LmNativeRam+$0f
  BNE ::LmDirectF47A
  LDA ::LmNativeRam+$15
  BNE ::LmDirectF475
::LmDirectF472:
  LDA ::LmNativeRam+$00
::LmDirectF475:
  LDX #$04
  LDY ::LmNativeRam+$10
::LmDirectF47A:
  STY ::LmNativeRam+$11
  LSR A
  LSR A
  LSR A
  BCS ::LmDirectF48A
  LDA #$ff
  CLC
  ADC ::LmNativeRam+$11
  BNE ::LmDirectF490
::LmDirectF48A:
  LDA #$01
  CLC
  ADC ::LmNativeRam+$11
::LmDirectF490:
  jsr GuestNativeStoreSTA02X
  RTS
::LmDirectF53C:
  .byte $00
::LmDirectF53D:
  .byte $00,$00,$00,$06,$ae,$06,$4e,$05,$f3,$05,$9e,$05,$4d,$05,$02,$04
  .byte $b9,$04,$75,$04,$35,$03,$f8,$03,$bf,$03,$89,$03,$57,$03,$27,$02
  .byte $f9,$02,$cf,$02,$a6,$02,$80,$02,$5c,$02,$3a,$02,$1a,$01,$fc,$01
  .byte $df,$01,$c4,$01,$ab,$01,$93,$01,$7c,$01,$67,$01,$52,$01,$3f,$01
  .byte $2d,$01,$1c,$01,$0c,$00,$fd,$00,$ee,$00,$e1,$00,$d4,$00,$c8,$00
  .byte $bd,$00,$b2,$00,$a8,$00,$9f,$00,$96,$00,$8d,$00,$85,$00,$7e,$00
  .byte $76,$00,$70,$00,$6a,$00,$64,$00,$5f,$00,$59,$00,$54,$00,$50,$00
  .byte $4b,$00,$47,$00,$43,$00,$3f,$00,$3b,$00,$38,$00,$35,$00,$32
::LmDirectF5BC:
  .byte $08,$18,$10,$20,$30,$40,$60,$80,$0b,$0a,$15,$16,$50,$ff,$05,$06
  .byte $16,$00,$00,$00,$00,$00,$00,$07,$15,$0e,$1c,$2a,$38,$54,$70,$09
  .byte $0a,$13,$12,$46,$e0,$05,$04,$12,$00,$00,$10,$04,$00,$00,$06,$13
  .byte $0d,$1a,$27,$34,$4e,$68,$09,$08,$11,$12,$41,$d0,$04,$05,$12,$00
  .byte $00,$00,$00,$07,$14,$06,$12,$0c,$18,$24,$30,$48,$60,$08,$08,$10
  .byte $10,$3c,$c0,$04,$04,$10,$6c,$54,$0f,$03,$00,$00,$06,$11,$0b,$16
  .byte $21,$2c,$42,$58,$07,$08,$0f,$0e,$37,$b0,$04,$03,$0e,$00,$00,$00
  .byte $00,$05,$10,$05,$0f,$0a,$14,$1e,$28,$3c,$50,$07,$06,$0d,$0e,$32
  .byte $a0,$03,$04
::LmDirectF674:
  .byte $da,$da,$da,$d9,$d9,$d9,$d8,$d8,$d8,$d7,$d7,$d7,$d6,$d6,$d6,$d5
  .byte $9a,$9a,$9a,$99,$99,$99,$98,$98,$98,$97,$97,$97,$96,$1e,$03,$48
  .byte $d3,$d3,$d3,$d3,$d3,$d3,$d3,$d3,$d3,$d3,$d4,$d4,$d4,$d5,$d5,$d6
  .byte $53,$53,$53,$53,$53,$53,$53,$53,$53,$53,$54,$54,$54,$15,$15,$56
  .byte $50,$50,$51,$51,$52,$52,$53,$53,$54,$55,$56,$57,$58,$59,$5a,$5b
  .byte $90,$90,$91,$91,$92,$92,$93,$93,$94,$95,$96,$97,$98,$99,$9a,$9b
  .byte $50,$50,$50,$50,$50,$50,$50,$50,$50,$50,$51,$52,$53,$54,$55,$56
  .byte $90,$90,$90,$90,$90,$90,$90,$90,$90,$91,$93,$94,$96,$97,$99,$9a
  .byte $10,$10,$10,$10,$12,$95,$d3,$14,$95,$17,$d4,$15,$97,$18,$da,$d0
  .byte $0c,$13,$d4,$15,$97,$d5,$16,$97,$19,$d6,$17,$99,$17,$db,$d0,$0c
::LmDirectF714:
  .byte $10,$11,$11,$11,$11,$12,$11,$12,$11,$12,$11,$12,$11,$12,$13,$12
  .byte $13,$12,$13,$12,$13,$14,$13,$14,$13,$14,$15,$14,$15,$14,$15,$16
  .byte $15,$16,$17,$18,$19,$1a
::LmDirectF73A:
  .byte $1b
::LmDirectF73B:
  .byte $1d
::LmDirectF73C:
  .byte $1d,$03,$48,$00,$19,$06,$38,$00,$19,$08,$38,$00,$19,$0a,$38,$00
  .byte $16,$07,$98,$00,$10,$00,$00,$00,$80,$00,$08,$00,$80,$01,$08,$00
  .byte $81,$01,$08,$00,$1d,$02,$08,$00,$1d,$03,$08
.assert *-LmNativeBankStart <= $1000,error,"Mac direct-ZP core exceeds blank source gap"
.res $1000-(*-LmNativeBankStart),$ff
LmDirect8FFF=LmDirect9000-1
::LmDirect9000:
  .byte $1f,$2b,$48,$2f,$31,$33,$35,$37,$39,$3c,$3e,$3f,$48,$4c,$4e,$4f
  .byte $51,$53,$55,$57,$59,$5b,$5c,$5d,$5e,$5f,$63,$64,$65,$67,$69,$05
  .byte $0d,$15,$05,$0d,$15,$05,$0d,$1d,$25,$2d,$00,$35,$15,$00,$00,$3d
  .byte $00,$45,$00,$4d,$00,$55,$00,$5d,$00,$65,$6d,$00,$75,$00,$00,$05
  .byte $0d,$15,$05,$0d,$1d,$25,$2d,$00,$05,$0d,$15,$00,$7d,$00,$00,$10
  .byte $00,$18,$00,$20,$00,$28,$00,$30,$00,$38,$00,$00,$00,$00,$00,$40
  .byte $48,$50,$00,$00,$00,$78,$00,$80,$00
::LmDirect9069:
  .byte $58
::LmDirect906A:
  .byte $60
::LmDirect906B:
  .byte $68
::LmDirect906C:
  .byte $70
::LmDirect906D:
  .byte $00
::LmDirect906E:
  .byte $17
::LmDirect906F:
::LmDirect9070 = *+1
  .word ::LmDirect9166
  .byte $5d,$40,$7b,$00,$60,$17
  .word ::LmDirect91EF
  .byte $5d,$24,$7e,$70,$60,$17
  .word ::LmDirect9296
  .byte $4b,$1a,$71,$70,$60,$17
  .word ::LmDirect9338
  .byte $38,$15,$52,$70,$60,$17
  .word ::LmDirect93B7
  .byte $11,$09,$19,$70,$60,$17
  .word ::LmDirect93D8
  .byte $05,$03,$08,$70,$60,$17
  .word ::LmDirect93E2
  .byte $05,$03,$00,$70,$60,$45
  .word ::LmDirect93E9
  .byte $3f,$20,$76,$10,$10,$45,$6a,$94,$43,$22,$00,$00,$00,$45
  .word ::LmDirect94D9
  .byte $31,$19,$00,$00,$00,$45
  .word ::LmDirect9602
  .byte $21,$11,$00,$00,$00,$45,$29,$95,$2f,$18,$4b,$00,$00,$73
  .word ::LmDirect963C
  .byte $35,$1b,$59,$00,$00,$73
  .word ::LmDirect96AC
  .byte $35,$1b,$59,$00,$00
::LmDirect90DE:
  .byte $45
::LmDirect90DF:
  .byte $d4
::LmDirect90E0:
  .byte $95
::LmDirect90E1:
  .byte $25
::LmDirect90E2:
  .byte $0d
::LmDirect90E3:
  .byte $00
::LmDirect90E4:
  .byte $00
::LmDirect90E5:
  .byte $60,$45,$92,$95,$27,$14,$2f,$00,$00,$45,$2d,$97,$47,$1f,$65,$00
  .byte $00,$45,$a0,$97,$63,$31,$8d,$00,$00,$45,$66,$98,$82,$41,$93,$00
  .byte $00,$45,$3c,$99,$21,$11,$33,$80,$00,$45,$7c,$99,$35,$1b,$62,$00
  .byte $00,$45,$f2,$99,$51,$16,$00,$00,$00,$73
  .word ::LmDirect9A80
  .byte $73,$3d,$d4,$10,$00,$73
  .word ::LmDirect9B61
  .byte $8c,$34,$bd,$80,$10,$73
  .word ::LmDirect9C2B
  .byte $14,$12,$22,$80,$10,$5c
  .word ::LmDirect9C5A
  .byte $41,$21,$00,$20,$20,$5c
  .word ::LmDirect9CCD
  .byte $47,$24,$00,$20,$20,$5c
  .word ::LmDirect9D35
  .byte $4d,$27,$00,$20,$20,$5c
  .word ::LmDirect9DA3
  .byte $59,$2d,$00,$20,$20,$73,$43,$9e,$41,$21,$00,$20,$20,$73
  .word ::LmDirect9EA5
  .byte $51,$29,$00,$20,$20
::LmDirect9166:
  .byte $93,$02,$94,$4c,$4c,$4c,$88,$4c,$42,$89,$4c,$88,$54,$4c,$89,$42
  .byte $83,$4c,$93,$02,$94,$54,$54,$54,$88,$54,$4c,$89,$54,$88,$5a,$54
  .byte $89,$4c,$83,$54,$82,$02,$80,$4c,$54,$83,$5a,$88,$42,$4c,$89,$54
  .byte $81,$5a,$80,$5e,$81,$62,$80,$60,$81,$5e,$80,$5c,$83,$5a,$42,$00
  .byte $87,$02,$02,$83,$02,$80,$5a,$5e,$5a,$5e,$5a,$5e,$5a,$5e,$5a,$5e
  .byte $5a,$56,$81,$5a,$80,$58,$81,$56,$80,$54,$83,$50,$02,$82,$34,$02
  .byte $86,$02,$82,$3c,$02,$86,$02,$82,$42,$02,$85,$02,$81,$02,$80,$46
  .byte $81,$4a,$80,$48,$81,$46,$80,$44,$83,$42,$02,$87,$2a,$26,$26,$81
  .byte $26,$80,$22,$81,$26,$80,$22,$85,$26
::LmDirect91EF:
  .byte $83,$54,$84,$4c,$82,$02,$42,$44,$83,$46,$82,$44,$83,$42,$82,$02
  .byte $83,$42,$56,$84,$50,$82,$02,$42,$44,$83,$46,$82,$44,$83,$42,$82
  .byte $02,$83,$42,$00,$83,$02,$80,$42,$44,$46,$48,$4a,$4c,$54,$56,$54
  .byte $56,$54,$56,$54,$56,$54,$56,$54,$56,$54,$56,$54,$56,$82,$54,$83
  .byte $02,$02,$80,$46,$48,$4a,$4c,$4e,$50,$56,$5a,$56,$5a,$56,$5a,$56
  .byte $5a,$56,$5a,$56,$5a,$56,$5a,$56,$5a,$82,$56,$83,$02,$82,$34,$42
  .byte $2a,$42,$34,$42,$2a,$42,$34,$42,$2a,$42,$34,$42,$2a,$42,$38,$42
  .byte $2a,$42,$38,$42,$2a,$42,$38,$42,$2a,$42,$38,$42,$2a,$42,$82,$1a
  .byte $1a,$83,$26,$82,$1a,$80,$1a,$1a,$82,$1e,$1a,$1a,$1a,$1e,$1a,$1a
  .byte $1a,$1e,$1a,$1a,$1a,$83,$26,$82,$1a,$1a,$1e,$80,$1a,$1a,$82,$1a
  .byte $1a,$1e,$1a,$1a,$1a,$1e,$1a
::LmDirect9296:
  .byte $83,$5a,$84,$54,$82,$02,$4a,$4c,$83,$50,$4c,$4a,$82,$46,$44,$42
  .byte $44,$46,$48,$83,$4a,$54,$85,$4c,$02,$00,$80,$58,$5a,$58,$5a,$58
  .byte $5a,$58,$5a,$5a,$5c,$5a,$5c,$5a,$5c,$5a,$5c,$5c,$5e,$5c,$5e,$5c
  .byte $5e,$5c,$5e,$83,$40,$82,$40,$40,$42,$40,$3e,$3c,$83,$38,$32,$82
  .byte $34,$80,$50,$54,$56,$5a,$5e,$62,$83,$64,$02,$82,$34,$42,$2a,$42
  .byte $34,$44,$3c,$44,$26,$3e,$34,$3e,$28,$40,$34,$40,$2a,$2c,$2e,$30
  .byte $32,$42,$3c,$42,$34,$80,$20,$24,$26,$2a,$2e,$32,$82,$34,$02,$34
  .byte $02,$82,$1e,$80,$1e,$1e,$82,$1e,$80,$1e,$1e,$82,$1e,$80,$1e,$1e
  .byte $82,$1e,$80,$1e,$1e,$82,$1e,$80,$1e,$1e,$82,$1e,$80,$1e,$1e,$82
  .byte $1e,$80,$1e,$1e,$82,$1e,$80,$1e,$1e,$85,$26,$83,$26,$26,$86,$26
  .byte $83,$26
::LmDirect9338:
  .byte $83,$5a,$84,$54,$82,$02,$4a,$4c,$83,$50,$4c,$4a,$82,$46,$44,$83
  .byte $42,$44,$46,$4a,$00,$80,$58,$5a,$58,$5a,$58,$5a,$58,$5a,$5a,$5c
  .byte $5a,$5c,$5a,$5c,$5a,$5c,$5c,$5e,$5c,$5e,$5c,$5e,$5c,$5e,$83,$40
  .byte $82,$40,$40,$83,$3c,$3e,$3e,$42,$82,$34,$42,$2a,$42,$34,$44,$3c
  .byte $44,$26,$3e,$34,$3e,$28,$40,$34,$40,$82,$2a,$42,$2a,$42,$2a,$42
  .byte $2a,$42,$82,$1e,$80,$1e,$1e,$82,$1e,$80,$1e,$1e,$82,$1e,$80,$1e
  .byte $1e,$82,$1e,$80,$1e,$1e,$82,$1e,$80,$1e,$1e,$82,$1e,$80,$1e,$1e
  .byte $82,$1e,$80,$1e,$1e,$82,$1e,$80,$1e,$1e,$85,$26,$83,$26,$26
::LmDirect93B7:
  .byte $83,$4c,$88,$34,$88,$34,$89,$34,$00,$83,$42,$88,$2a,$88,$2a,$89
  .byte $2a,$83,$4c,$88,$34,$88,$34,$89,$34,$83,$26,$88,$2a,$88,$2a,$89
  .byte $2a
::LmDirect93D8:
  .byte $85,$34,$00,$85,$2a,$83,$34,$02,$85,$2a
::LmDirect93E2:
  .byte $83,$42,$00,$83,$02,$83,$02
::LmDirect93E9:
  .byte $85,$4c,$83,$42,$4c,$81,$50,$80,$50,$85,$50,$82,$4c,$50,$85,$54
  .byte $83,$4c,$54,$81,$56,$80,$56,$85,$56,$82,$54,$56,$87,$5a,$02,$00
  .byte $85,$3c,$83,$3c,$3c,$81,$3e,$80,$3e,$85,$3e,$82,$3e,$3e,$85,$42
  .byte $83,$42,$42,$81,$50,$80,$50,$85,$50,$82,$4c,$50,$87,$54,$02,$83
  .byte $34,$88,$34,$34,$89,$34,$83,$34,$34,$30,$88,$30,$30,$89,$30,$83
  .byte $30,$30,$34,$88,$34,$34,$89,$34,$83,$34,$34,$30,$88,$30,$30,$89
  .byte $30,$83,$30,$30,$34,$88,$34,$34,$89,$34,$83,$34,$34,$34,$88,$34
  .byte $34,$89,$34,$83,$34,$34,$83,$02,$88,$02,$02,$89,$02,$83,$02,$02
  .byte $00,$83,$48,$80,$48,$48,$48,$48,$83,$44,$81,$42,$80,$3e,$81,$3c
  .byte $80,$42,$85,$4c,$82,$42,$4c,$85,$48,$83,$44,$88,$48,$44,$89,$48
  .byte $87,$4c,$00,$83,$38,$80,$38,$38,$38,$38,$83,$38,$81,$38,$80,$38
  .byte $81,$3c,$80,$3c,$85,$3c,$82,$3c,$3c,$85,$38,$83,$38,$88,$38,$38
  .byte $89,$38,$87,$3c,$83,$48,$80,$48,$48,$48,$48,$83,$48,$81,$48,$80
  .byte $48,$83,$4c,$80,$4c,$4c,$4c,$4c,$83,$4c,$82,$34,$4c,$83,$48,$80
  .byte $48,$48,$48,$48,$83,$48,$48,$83,$4c,$80,$34,$34,$34,$34,$85,$34
::LmDirect94D9:
  .byte $82,$4c,$4c,$5a,$80,$5a,$56,$02,$56,$02,$54,$82,$56,$5a,$81,$60
  .byte $5e,$60,$5e,$82,$60,$5e,$86,$64,$00,$82,$3c,$3c,$4c,$80,$4c,$4c
  .byte $02,$4c,$02,$4c,$82,$4c,$4c,$81,$50,$4c,$50,$4c,$82,$50,$4c,$86
  .byte $54,$82,$34,$34,$34,$80,$34,$34,$02,$34,$02,$34,$82,$34,$34,$81
  .byte $56,$56,$56,$56,$82,$56,$56,$83,$4c,$88,$34,$34,$89,$34,$83,$34
  .byte $82,$46,$4a,$4c,$83,$4a,$82,$4c,$83,$50,$82,$4c,$50,$54,$83,$50
  .byte $54,$82,$5a,$87,$5e,$83,$02,$00,$82,$3e,$3e,$3e,$83,$42,$82,$42
  .byte $83,$42,$82,$46,$46,$46,$83,$4a,$4a,$82,$4a,$87,$4e,$83,$02,$82
  .byte $46,$46,$46,$42,$42,$42,$42,$42,$3e,$3e,$3e,$42,$42,$42,$42,$42
  .byte $46,$46,$2e,$2e,$46,$2e,$2e,$83,$46,$82,$02,$82,$02,$02,$02,$83
  .byte $2a,$82,$02,$02,$02,$82,$02,$02,$02,$83,$2a,$82,$02,$02,$02,$82
  .byte $2a,$2a,$2a,$2a,$2a,$2a,$2a,$84,$2a,$83,$42,$83,$42,$82,$42,$42
  .byte $83,$4a,$82,$42,$4a,$82,$50,$42,$4a,$50,$87,$5a,$00,$83,$02,$83
  .byte $32,$82,$32,$32,$83,$38,$82,$38,$38,$82,$38,$38,$38,$38,$87,$62
  .byte $83,$02,$85,$38,$42,$4a,$87,$50,$83,$2a,$83,$2a,$82,$2a,$2a,$83
  .byte $2a,$82,$2a,$2a,$82,$2a,$2a,$2a,$2a,$87,$2a,$90,$34,$89,$34,$86
  .byte $3e,$89,$42,$3e,$42,$86,$4c,$00,$83,$02,$89,$56,$4c,$46,$56,$4c
  .byte $46,$56,$4c,$46,$56,$4c,$46,$5e,$56,$4c,$5e,$56,$4c,$5e,$56,$4c
  .byte $83,$02,$3e,$34,$3e,$34,$3e,$34,$3e
::LmDirect9602:
  .byte $84,$34,$82,$02,$83,$34,$82,$38,$92,$3a,$8e,$38,$88,$3a,$91,$38
  .byte $00,$84,$2a,$82,$02,$83,$2a,$82,$2e,$92,$30,$8e,$2e,$88,$30,$91
  .byte $2e,$82,$34,$2a,$34,$2a,$34,$2a,$34,$2a,$3a,$30,$3a,$30,$3a,$30
  .byte $3a,$30,$38,$2e,$38,$2e,$38,$2e,$38,$2e
::LmDirect963C:
  .byte $82,$42,$4c,$50,$83,$52,$50,$48,$85,$3e,$82,$44,$42,$3e,$82,$42
  .byte $4c,$50,$83,$52,$50,$56,$85,$48,$84,$02,$00,$82,$3a,$42,$42,$83
  .byte $42,$42,$3e,$85,$38,$82,$38,$38,$38,$82,$3a,$42,$42,$83,$42,$42
  .byte $50,$85,$38,$84,$02,$82,$34,$34,$34,$34,$34,$34,$34,$34,$82,$48
  .byte $48,$48,$48,$48,$48,$48,$48,$82,$34,$34,$34,$34,$34,$34,$34,$34
  .byte $82,$48,$48,$48,$48,$48,$48,$48,$48,$82,$0a,$0a,$02,$0a,$82,$0a
  .byte $0a,$02,$0a,$82,$0a,$0a,$02,$0a,$82,$0a,$0a,$02,$80,$0a,$02,$00
::LmDirect96AC:
  .byte $82,$42,$4c,$50,$83,$52,$50,$48,$85,$3e,$82,$44,$42,$3e,$83,$52
  .byte $88,$56,$5a,$89,$56,$83,$50,$48,$87,$4c,$00,$82,$3a,$42,$42,$83
  .byte $42,$42,$3e,$85,$38,$82,$38,$38,$38,$83,$4c,$88,$4c,$4c,$89,$4c
  .byte $83,$3e,$38,$87,$3c,$82,$34,$34,$34,$34,$34,$34,$34,$34,$82,$48
  .byte $48,$48,$48,$48,$48,$48,$48,$83,$44,$88,$44,$44,$89,$44,$83,$48
  .byte $48,$4c,$80,$34,$34,$34,$34,$85,$34,$82,$0a,$0a,$02,$0a,$82,$0a
  .byte $0a,$02,$0a,$82,$0a,$0a,$02,$0a,$82,$0a,$0a,$02,$80,$0a,$02,$83
  .byte $0a,$88,$0a,$0a,$89,$0a,$83,$02,$02,$0a,$80,$02,$06,$0a,$0e,$85
  .byte $12,$82,$34,$80,$2e,$34,$83,$3c,$34,$82,$3c,$80,$34,$3c,$83,$42
  .byte $3c,$82,$42,$80,$3c,$42,$83,$4a,$89,$32,$32,$88,$32,$85,$3c,$00
  .byte $80,$5e,$54,$4c,$54,$5e,$54,$4c,$54,$5e,$54,$4c,$54,$5a,$54,$4c
  .byte $54,$5a,$54,$4c,$54,$5a,$54,$4c,$54,$5a,$54,$4a,$54,$5a,$54,$4a
  .byte $54,$89,$24,$24,$88,$24,$85,$34,$82,$2e,$80,$26,$2e,$83,$34,$2e
  .byte $82,$34,$80,$2e,$34,$83,$3c,$34,$82,$3c,$80,$34,$3c,$83,$42,$89
  .byte $2a,$2a,$88,$2a,$85,$34,$85,$16,$86,$2a,$86,$2a,$89,$26,$89,$26
  .byte $88,$26,$85,$2a,$82,$38,$80,$38,$38,$82,$42,$42,$80,$02,$42,$02
  .byte $42,$82,$46,$46,$80,$02,$46,$02,$46,$84,$50,$82,$4a,$42,$42,$4a
  .byte $42,$83,$3c,$85,$4c,$88,$4a,$4c,$89,$46,$82,$42,$02,$88,$42,$42
  .byte $89,$42,$83,$42,$00,$82,$02,$80,$02,$02,$82,$38,$38,$80,$02,$38
  .byte $02,$38,$82,$3e,$3e,$80,$02,$3e,$02,$3e,$84,$4a,$82,$42,$83,$02
  .byte $82,$42,$02,$83,$02,$85,$3c,$88,$38,$38,$89,$3e,$82,$38,$02,$88
  .byte $38,$38,$89,$38

; Nine source music tracks only. $fc is not a compressed playlist index.
.proc LmNativeMusicUpdate
  lda #0
  sta RgAudioRequest
  lda OperMode
  jeq Mute
  lda XgAudioCharacter
  cmp #$fc
  beq Initialized
  lda #$fc
  sta XgAudioCharacter
  lda #0
  sta RgAudioSong
  sta RgAudioSilenced
  sta XgAudioEvent
  lda #20
  sta LmNativePending
Initialized:
  lda AreaMusicQueue
  ora EventMusicQueue
  and #Silence
  beq Area
  lda #1
  sta RgAudioSilenced
Area:
  lda AreaMusicQueue
  and #$7f
  beq Event
  ldx #0
FindArea:
  lsr
  bcs AreaFound
  inx
  bne FindArea
AreaFound:
  lda Areas,x
  sta LmNativePending
  lda #0
  sta RgAudioSilenced
  sta XgAudioEvent
Event:
  lda EventMusicQueue
  and #$7f
  beq Pause
  ldx #0
FindEvent:
  lsr
  bcs EventFound
  inx
  bne FindEvent
EventFound:
  lda Events,x
  sta LmNativePending
  lda #0
  sta RgAudioSilenced
  lda #1
  sta XgAudioEvent
  cpx #6
  bne Pause
  lda #4
  sta XgAudioEvent
Pause:
  lda GamePauseStatus
  and #1
  jne Mute
  lda RgAudioSilenced
  jne Mute
  lda LmNativePending
  sta RgAudioRequest
  bne Restart
  lda XgAudioEvent
  cmp #2
  jeq Mute
  ; Source $f6 becomes zero only at the complete finite tune's end.
  ; A fresh NSF init queues the selection in $f2 until its first play call.
  lda LmNativeZp+6
  ora LmNativeZp+2
  bne SaveCpu
  lda XgAudioEvent
  beq LoopWholeTune
  lda #2
  sta XgAudioEvent
  jmp Mute
LoopWholeTune:
  lda RgAudioSong
  sta RgAudioRequest
Restart:
  lda RgAudioRequest
  sta RgAudioSong
  inc XgAudioSong
  lda #0
  ldx #47
ResetState:
  sta LmNativeRam,x
  dex
  bpl ResetState
  ldx #15
ResetImage:
  sta LmNativeZp,x
  sta GuestNativeApu,x
  lda #1
  sta GuestNativeDirty,x
  lda #0
  dex
  bpl ResetImage
SaveCpu:
  lda $f8
  sta LmNativeSavedZp+8
  lda LmNativeZp+8
  sta $f8
  lda $f9
  sta LmNativeSavedZp+9
  lda LmNativeZp+9
  sta $f9
  lda RgAudioRequest
  beq Play
  sec
  sbc #1
  ldx #0
  ldy #0
  jsr LmNativeSourceInit
  lda #0
  sta LmNativePending
  jmp Restore
Play:
  lda GuestNativeEnable
  cmp #15
  beq Enabled
  lda #15
  jsr GuestNativeStatusSTA
Enabled:
  ldx #0
  ldy #0
  jsr LmNativeMusicPlay
Restore:
  lda $f8
  sta LmNativeZp+8
  lda LmNativeSavedZp+8
  sta $f8
  lda $f9
  sta LmNativeZp+9
  lda LmNativeSavedZp+9
  sta $f9
  jmp Queues
Mute:
  lda #0
  jsr GuestNativeStatusSTA
Queues:
  lda #0
  sta AreaMusicQueue
  sta EventMusicQueue
  sta Square1SoundQueue
  sta Square2SoundQueue
  sta NoiseSoundQueue
  rts
Areas:
  .byte 20,22,1,23,2,1,23
Events:
  .byte 7,9,6,4,9,6,23
.endproc
; The public adapter supplies music, never original Punch-Out SFX requests.
; Keep the source's two ordered hardware-control stores, original music
; routine, and queue-clearing epilogue. Only the inactive SFX bit scans are
; omitted. Retain the complete source entry for any nonzero source SFX flag.
.proc LmNativeMusicPlay
  lda LmNativeZp+$00
  ora LmNativeZp+$01
  ora LmNativeZp+$03
  ora LmNativeZp+$04
  ora LmNativeZp+$05
  ora LmNativeZp+$07
  bne FullSource
  lda #$c0
  sta $4017
  lda #15
  jsr GuestNativeStatusSTA
  jsr LmDirect88E2
  lda #0
  sta LmNativeZp+$00
  sta LmNativeZp+$01
  sta LmNativeZp+$02
  sta LmNativeZp+$03
  rts
FullSource:
  jmp LmNativeSourcePlay
.endproc
; These stores use the established guest/world-effect mixer. The original
; source's direct $4017 store remains direct and occurs once per native play.
.macro LmNativeWriter Name,Op,Offset
.proc Name
  Op GuestNativeApu+Offset
  php
  inc GuestNativeDirty+Offset
  plp
  rts
.endproc
.endmacro
LmNativeWriter LmNativeSTA00,sta,0
LmNativeWriter LmNativeSTA04,sta,4
LmNativeWriter LmNativeSTA08,sta,8
LmNativeWriter LmNativeSTA0C,sta,12
LmNativeWriter LmNativeSTA0E,sta,14
LmNativeWriter LmNativeSTX00,stx,0
LmNativeWriter LmNativeSTX04,stx,4
LmNativeWriter LmNativeSTY08,sty,8
LmNativeAdapterEnd:
.assert LmNativeAdapterEnd-LmNativeMusicUpdate <= $200,error,"Mac adapter exceeds its 512-byte source hole"
.res $200-(*-LmNativeMusicUpdate),$ff

  .byte $4a,$46,$82,$4a,$46,$85,$3e,$00,$80,$34,$3c,$38,$34,$34,$3c,$38
  .byte $34,$38,$3e,$3c,$38,$38,$3e,$3c,$38,$34,$3c,$38,$34,$34,$3c,$38
  .byte $34,$38,$3e,$3c,$38,$3c,$38,$34,$4a,$34,$3c,$34,$3c,$38,$3e,$38
  .byte $3e,$3c,$42,$3c,$42,$38,$3e,$38,$3e,$34,$2e,$3c,$34,$34,$3c,$34
  .byte $3c,$85,$38,$81,$2e,$80,$34,$82,$3c,$46,$81,$2c,$80,$38,$82,$3e
  .byte $42,$81,$2e,$80,$34,$82,$3c,$46,$81,$2c,$80,$38,$82,$3e,$42,$2e
  .byte $80,$46,$2e,$82,$2c,$80,$42,$2a,$82,$2a,$80,$42,$2e,$82,$2c,$80
  .byte $42,$2a,$81,$2e,$80,$32,$82,$34,$3c,$80,$02,$38,$3e,$46,$83,$4a
::LmDirect9A80:
  .byte $87,$46,$83,$54,$82,$50,$83,$4c,$4a,$87,$42,$82,$02,$83,$50,$82
  .byte $4c,$83,$4a,$46,$87,$3e,$82,$02,$83,$4c,$82,$4a,$83,$46,$42,$8d
  .byte $3c,$82,$02,$88,$38,$3c,$87,$3e,$83,$02,$89,$02,$82,$3c,$83,$3a
  .byte $87,$3c,$82,$02,$82,$46,$83,$46,$84,$44,$83,$02,$00,$87,$3c,$83
  .byte $3c,$82,$3c,$83,$3c,$3c,$87,$38,$82,$02,$83,$38,$82,$38,$83,$38
  .byte $38,$87,$34,$82,$02,$83,$34,$82,$34,$83,$34,$34,$8d,$32,$82,$02
  .byte $87,$2e,$85,$02,$84,$02,$87,$32,$82,$02,$82,$3c,$3e,$40,$42,$44
  .byte $46,$48,$4a,$82,$2e,$46,$2e,$46,$2e,$46,$2e,$46,$2e,$46,$2e,$46
  .byte $2e,$46,$2e,$46,$2a,$42,$2a,$42,$2a,$42,$2a,$42,$2a,$42,$2a,$42
  .byte $2a,$42,$2a,$42,$26,$3e,$26,$3e,$26,$3e,$26,$3e,$26,$3e,$26,$3e
  .byte $26,$3e,$26,$3e,$24,$3c,$24,$3c,$24,$3c,$24,$3c,$24,$3c,$24,$3c
  .byte $24,$3c,$24,$3c,$20,$38,$20,$38,$20,$38,$20,$38,$20,$38,$20,$38
  .byte $20,$38,$20,$38,$24,$3c,$24,$3c,$24,$3c,$24,$3c,$34,$38,$34,$38
  .byte $34,$32,$2e,$2a,$82,$0a,$0e,$12,$0a,$0a,$0e,$80,$12,$12,$82,$0a
  .byte $00
::LmDirect9B61:
  .byte $82,$5e,$83,$02,$82,$5e,$83,$02,$82,$5e,$02,$02,$5e,$83,$02,$5e
  .byte $5e,$82,$5a,$83,$02,$82,$5a,$83,$02,$82,$5a,$02,$02,$5a,$83,$02
  .byte $5a,$5a,$82,$56,$83,$02,$82,$56,$83,$02,$82,$56,$02,$02,$56,$83
  .byte $02,$56,$56,$00,$8e,$46,$4a,$8f,$4c,$83,$02,$8e,$46,$4a,$8f,$4c
  .byte $83,$02,$8e,$46,$4a,$8f,$4c,$82,$02,$02,$46,$4a,$4c,$54,$83,$50
  .byte $82,$4c,$8e,$42,$46,$8f,$4a,$83,$02,$8e,$42,$46,$8f,$4a,$83,$02
  .byte $8e,$42,$46,$8f,$4a,$82,$02,$02,$42,$46,$4a,$50,$83,$4c,$8e,$3e
  .byte $42,$8f,$46,$83,$02,$8e,$3e,$42,$8f,$46,$83,$02,$8e,$3e,$42,$8f
  .byte $46,$82,$02,$02,$3e,$42,$46,$4c,$83,$4a,$82,$46,$82,$46,$2e,$2e
  .byte $46,$2e,$2e,$46,$2e,$46,$2e,$2e,$46,$2e,$2e,$46,$2e,$42,$2a,$2a
  .byte $42,$2a,$2a,$42,$2a,$42,$2a,$2a,$42,$2a,$2a,$42,$2a,$3e,$26,$26
  .byte $3e,$26,$26,$3e,$26,$3e,$26,$26,$3e,$26,$26,$3e,$26,$82,$0a,$0e
  .byte $12,$0a,$0a,$0e,$80,$12,$12,$82,$0a,$00
::LmDirect9C2B:
  .byte $82,$3c,$83,$02,$82,$3c,$83,$02,$82,$3c,$82,$02,$83,$3c,$38,$34
  .byte $32,$00,$8d,$3c,$82,$3c,$24,$24,$3c,$24,$24,$3c,$24,$83,$3c,$38
  .byte $34,$32,$82,$0a,$0e,$12,$0a,$0a,$0e,$80,$12,$12,$82,$0a,$00
::LmDirect9C5A:
  .byte $83,$3c,$84,$02,$82,$3c,$3c,$83,$38,$86,$02,$82,$02,$83,$34,$84
  .byte $02,$82,$34,$34,$83,$38,$86,$02,$82,$38,$83,$3c,$86,$02,$87,$02
  .byte $00,$83,$34,$84,$02,$82,$34,$34,$83,$32,$86,$02,$82,$02,$83,$2e
  .byte $84,$02,$82,$2e,$2e,$83,$32,$86,$02,$82,$32,$83,$34,$86,$02,$87
  .byte $02,$82,$2e,$2e,$2e,$2e,$2e,$2e,$2e,$2e,$2a,$2a,$2a,$2a,$2a,$2a
  .byte $2a,$2a,$26,$26,$26,$26,$26,$26,$26,$26,$42,$2a,$2a,$42,$2a,$2a
  .byte $42,$2a,$82,$46,$2e,$2e,$46,$2e,$2e,$46,$2e,$46,$2e,$46,$2e,$2e
  .byte $2e,$46,$2e
::LmDirect9CCD:
  .byte $86,$46,$83,$4a,$82,$4c,$02,$4c,$02,$4a,$46,$83,$02,$80,$44,$83
  .byte $46,$80,$02,$82,$42,$83,$02,$80,$44,$83,$46,$80,$02,$82,$42,$83
  .byte $02,$4c,$4a,$00,$86,$3c,$83,$3c,$82,$3c,$02,$3c,$02,$3c,$3c,$83
  .byte $02,$80,$3a,$83,$3c,$80,$02,$82,$38,$83,$02,$80,$3a,$83,$3c,$80
  .byte $02,$82,$38,$83,$02,$3c,$3c,$82,$46,$2e,$2e,$46,$2e,$2e,$46,$2e
  .byte $46,$2e,$46,$2e,$2e,$2e,$46,$2e,$42,$2a,$2a,$42,$2a,$2a,$42,$2a
  .byte $42,$2a,$2a,$42,$2a,$2a,$42,$2a
::LmDirect9D35:
  .byte $86,$46,$83,$4a,$82,$4c,$02,$4c,$02,$4a,$4c,$83,$02,$80,$52,$83
  .byte $54,$80,$02,$82,$50,$83,$02,$80,$52,$83,$54,$80,$02,$82,$50,$83
  .byte $02,$82,$54,$50,$54,$50,$00,$86,$3c,$83,$3c,$82,$42,$02,$42,$02
  .byte $42,$42,$83,$02,$80,$44,$83,$46,$80,$02,$82,$46,$83,$02,$80,$44
  .byte $83,$46,$80,$02,$82,$46,$83,$02,$82,$46,$46,$46,$46,$82,$46,$2e
  .byte $2e,$46,$2e,$2e,$46,$2e,$46,$2e,$46,$2e,$2e,$2e,$46,$2e,$3c,$24
  .byte $24,$3c,$24,$24,$3c,$24,$3c,$24,$24,$3c,$24,$24,$3c,$24
::LmDirect9DA3:
  .byte $86,$46,$82,$4c,$54,$02,$5e,$02,$64,$02,$62,$02,$86,$5a,$82,$02
  .byte $5e,$62,$02,$64,$02,$62,$02,$64,$62,$02,$86,$56,$82,$5a,$5e,$02
  .byte $5e,$02,$5e,$64,$83,$62,$82,$02,$87,$6c,$87,$02,$00,$86,$3c,$82
  .byte $3c,$3c,$02,$54,$02,$54,$02,$54,$02,$86,$4a,$82,$02,$54,$54,$02
  .byte $54,$02,$54,$02,$54,$50,$02,$86,$46,$82,$46,$4c,$02,$50,$02,$50
  .byte $50,$83,$50,$82,$02,$87,$4a,$87,$02,$82,$46,$2e,$2e,$46,$2e,$2e
  .byte $46,$2e,$46,$2e,$46,$2e,$2e,$2e,$46,$2e,$82,$42,$2a,$2a,$42,$2a
  .byte $2a,$42,$2a,$2a,$32,$2a,$38,$2a,$3e,$2a,$42,$82,$3e,$26,$26,$3e
  .byte $26,$26,$3e,$26,$26,$2e,$26,$34,$26,$3c,$26,$3e,$24,$3c,$24,$3c
  .byte $24,$3c,$24,$3c,$80,$3c,$3c,$02,$3c,$3c,$38,$34,$2e,$83,$3c,$02
  .byte $82,$34,$34,$38,$34,$02,$83,$3c,$82,$34,$83,$3e,$82,$3c,$8c,$38
  .byte $82,$38,$38,$3c,$38,$02,$83,$3e,$82,$3c,$83,$42,$82,$3e,$8c,$3c
  .byte $00,$82,$2a,$2a,$2a,$2a,$02,$83,$34,$82,$2a,$83,$38,$82,$34,$8c
  .byte $32,$82,$2a,$2a,$2a,$2a,$02,$83,$32,$82,$32,$83,$34,$82,$34,$8c
  .byte $34,$82,$34,$34,$34,$34,$34,$34,$34,$34,$34,$34,$34,$34,$34,$34
  .byte $34,$34,$38,$38,$38,$38,$38,$38,$38,$38,$42,$42,$42,$42,$42,$42
  .byte $42,$42
::LmDirect9EA5:
  .byte $82,$54,$4c,$46,$83,$54,$82,$3c,$3c,$02,$82,$56,$50,$46,$83,$56
  .byte $82,$3e,$3e,$02,$82,$54,$4c,$46,$83,$54,$82,$3c,$3c,$02,$82,$50
  .byte $4a,$42,$83,$50,$82,$38,$38,$02,$00,$82,$4c,$46,$3c,$83,$4c,$82
  .byte $34,$34,$02,$82,$50,$46,$3e,$83,$50,$82,$38,$38,$02,$82,$4c,$46
  .byte $3c,$83,$4c,$82,$34,$34,$02,$82,$4a,$42,$38,$83,$4a,$82,$32,$32
  .byte $02,$82,$46,$46,$46,$46,$46,$46,$46,$46,$82,$3e,$3e,$3e,$3e,$3e
  .byte $3e,$3e,$3e,$82,$46,$46,$46,$46,$46,$46,$46,$46,$82,$42,$42,$42
  .byte $42,$42,$42,$42,$42,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
  .byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
  .byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
  .byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
  .byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
  .byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
  .byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
::LmDirect9F80:
  PHA
  LDA #$0f
  jsr GuestNativeStatusSTA
  PLA
  CMP #$17
  BCS ::LmDirect9FA0
  TAX
  LDA ::LmDirect9FD0,x
  STA ::LmNativeZp+$02
  RTS
.assert *-LmNativeBankStart <= $1fa0,error,"Mac direct init exceeds original unused pad"
.res $1fa0-(*-LmNativeBankStart),$ff
::LmDirect9FA0:
  .byte $38,$e9,$16,$c9,$19,$b0,$09,$85,$f0,$60,$00,$00,$00,$00,$00,$00
  .byte $38,$e9,$18,$c9,$16,$b0,$09,$85,$f1,$60,$00,$00,$00,$00,$00,$00
  .byte $38,$e9,$15,$c9,$08,$b0,$04,$85,$f3,$60,$00,$a9,$01,$85,$f2,$60
::LmDirect9FD0:
  .byte $01,$02,$03,$04,$05,$06,$07,$08,$09,$0a,$0c,$0d,$0e,$10,$11,$12
  .byte $13,$14,$15,$1a,$1d,$1e,$1f,$00,$00,$00,$00,$00,$00,$00,$00,$00
  .byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
.assert *-LmNativeBankStart=$2000,error,"Mac direct-ZP bank must remain 8 KiB"
LmNativeSourceInit=LmDirect9F80
LmNativeSourcePlay=LmDirect8000
.popseg
