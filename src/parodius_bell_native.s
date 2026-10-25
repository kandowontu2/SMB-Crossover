; Original Famicom Parodius Bell state; generated, not hand tuned.
PnNativeVramBusy=$5da7
.export PnNativeVramBusy
PnNativePaletteStyle=$5da6
.export PnNativePaletteStyle
PnNativePaletteMode=$5d77
.export PnNativePaletteMode
PnNativePaletteRestore=$5d78
.export PnNativePaletteRestore
PnBombTerrainCursor=$5d79
.export PnBombTerrainCursor
PnNativeLives=$5da5
.export PnNativeLives
PnNativeScrollXHi=$5de1
.export PnNativeScrollXHi
PnNativeScrollXLo=$5de0
.export PnNativeScrollXLo
PnNativeScrollFlags=$5de2
.export PnNativeScrollFlags
PnRedRemaining=$5dd7
.export PnRedRemaining
.pushseg
.segment "PARODIUS_BELLS"
Pb80b5: lda PnContact ; original $80b5
Pb80b8: jeq PbPickupDone ; original $80b8
Pb80ba: and #$7f ; original $80ba
Pb80bc: cmp #$04 ; original $80bc
Pb80be: jeq Pb8125 ; original $80be
Pb80c0: cmp #$05 ; original $80c0
Pb80c2: jeq Pb811d ; original $80c2
Pb80c4: cmp #$0b ; original $80c4
Pb80c6: jcc Pb80f1 ; original $80c6
Pb80c8: cmp #$14 ; original $80c8
Pb80ca: jeq PbPickupDone ; original $80ca
Pb80cc: cmp #$15 ; original $80cc
Pb80ce: jeq Pb80e8 ; original $80ce
Pb80d0: cmp #$17 ; original $80d0
Pb80d2: jeq Pb80da ; original $80d2
Pb80d4: cmp #$0d ; original $80d4
Pb80d6: jne PbPickupDone ; original $80d6
Pb80d8: jeq PbPickupDone ; original $80d8
Pb80da: lda PnBellFlags ; original $80da
Pb80dc: and #$02 ; original $80dc
Pb80de: jne PbPickupDone ; original $80de
Pb80e0: sta VvFresh ; original $80e0
Pb80e2: lda PnBellFlags ; original $80e2
Pb80e4: ora #$40 ; original $80e4
Pb80e6: jne Pb8121 ; original $80e6
Pb80e8: ldy PnEnemyIndex ; original $80e8
Pb80eb: jsr PbCallback9756 ; original $80eb
Pb80ee: jmp PbPickupDone ; original $80ee
Pb80f1: sec ; original $80f1
Pb80f2: sbc #$06 ; original $80f2
Pb80f4: jcc PbPickupDone ; original $80f4
Pb80f6: jeq PbPickupDone ; original $80f6
Pb80f8: cmp #$03 ; original $80f8
Pb80fa: jne Pb80ff ; original $80fa
Pb80fc: sta PnRedRemaining ; original $80fc
Pb80ff: pha ; original $80ff
Pb8100: lda PnBellFlags ; original $8100
Pb8102: and #$02 ; original $8102
Pb8104: jne Pb810b ; original $8104
Pb8106: lda #$22 ; original $8106
Pb8108: jsr PbCallbackfe20 ; original $8108
Pb810b: pla ; original $810b
Pb810c: tay ; original $810c
Pb810d: dey ; original $810d
Pb810e: lda PnBellFlags ; original $810e
Pb8110: and #$07 ; original $8110
Pb8112: jne PbPickupDone ; original $8112
Pb8114: lda PnBellFlags ; original $8114
Pb8116: and #$18 ; original $8116
Pb8118: ora Pn92cd,Y ; original $8118
Pb811b: jne Pb8121 ; original $811b
Pb811d: lda PnBellFlags ; original $811d
Pb811f: ora #$10 ; original $811f
Pb8121: sta PnBellFlags ; original $8121
Pb8123: jne PbPickupDone ; original $8123
Pb8125: lda #$1c ; original $8125
Pb8127: jsr PbCallbackfe20 ; original $8127
Pb812a: lda VvMeter ; original $812a
Pb812c: jeq Pb8132 ; original $812c
Pb812e: asl VvMeter ; original $812e
Pb8130: jpl PbPickupDone ; original $8130
Pb8132: lda #$01 ; original $8132
Pb8134: sta VvMeter ; original $8134
PbPickupDone:rts
Pb97fc: ldx #$1b ; original $97fc
Pb97fe: jsr Pb9c1e ; original $97fe
Pb9801: ldx #$1b ; original $9801
Pb9803: lda PnBellFlags ; original $9803
Pb9805: and #$0f ; original $9805
Pb9807: jne Pb980a ; original $9807
Pb9809: rts ; original $9809
Pb980a: lsr a ; original $980a
Pb980b: jcs Pb9810 ; original $980b
Pb980d: jmp Pb9a6b ; original $980d
Pb9810: lda PnNativePaletteStyle ; original $9810
Pb9812: jne Pb9837 ; original $9812
Pb9814: lda PnNativeStage ; original $9814
Pb9816: cmp #$01 ; original $9816
Pb9818: jne Pb9827 ; original $9818
Pb981a: ldy PnNativeStage60 ; original $981a
Pb981c: lda Pb9a57,Y ; original $981c
Pb981f: jeq Pb9837 ; original $981f
Pb9821: lda #$0d ; original $9821
Pb9823: sta PnNativePaletteMode ; original $9823
Pb9825: jne Pb983b ; original $9825
Pb9827: cmp #$04 ; original $9827
Pb9829: jne Pb9837 ; original $9829
Pb982b: lda PnNativeStage60 ; original $982b
Pb982d: cmp #$03 ; original $982d
Pb982f: jcc Pb9837 ; original $982f
Pb9831: lda #$0c ; original $9831
Pb9833: sta PnNativePaletteMode ; original $9833
Pb9835: jne Pb983b ; original $9835
Pb9837: lda PnNativePaletteStyle ; original $9837
Pb9839: sta PnNativePaletteMode ; original $9839
Pb983b: lda PnActive,X ; original $983b
Pb983e: jne Pb986e ; original $983e
Pb9840: jsr Pb9c3d ; original $9840
Pb9843: jeq Pb985e ; original $9843
Pb9845: lda #$3c ; original $9845
Pb9847: jsr PbCallbackfe20 ; original $9847
Pb984a: lda #$08 ; original $984a
Pb984c: sta PnActive,X ; original $984c
Pb984f: lda #$00 ; original $984f
Pb9851: sta PnBombTerrainCursor ; original $9851
Pb9853: sta PnPhase,X ; original $9853
Pb9856: sta PnAux,X ; original $9856
Pb9859: lda #$08 ; original $9859
Pb985b: sta PnAngle,X ; original $985b
Pb985e: rts ; original $985e
Pb985f: lda PnActive,X ; original $985f
Pb9862: and #$04 ; original $9862
Pb9864: jne Pb986b ; original $9864
Pb9866: lda PnPhase,X ; original $9866
Pb9869: jeq Pb985e ; original $9869
Pb986b: jmp PbCallbackfb1d ; original $986b
Pb986e: lda PnAux,X ; original $986e
Pb9871: cmp #$01 ; original $9871
Pb9873: jeq PbCallback98a8 ; original $9873
Pb9875: cmp #$02 ; original $9875
Pb9877: jeq Pb98f5 ; original $9877
Pb9879: dec PnAngle,X ; original $9879
Pb987c: jne Pb985f ; original $987c
Pb987e: jsr Pb9859 ; original $987e
Pb9881: lda PnActive,X ; original $9881
Pb9884: and #$04 ; original $9884
Pb9886: jne Pb98f9 ; original $9886
Pb9888: lda PnPhase,X ; original $9888
Pb988b: clc ; original $988b
Pb988c: adc #$10 ; original $988c
Pb988e: cmp #$50 ; original $988e
Pb9890: jne Pb989b ; original $9890
Pb9892: lsr PnActive,X ; original $9892
Pb9895: lda #$10 ; original $9895
Pb9897: sta PnAngle,X ; original $9897
Pb989a: rts ; original $989a
Pb989b: sta PnPhase,X ; original $989b
Pb989e: cmp #$40 ; original $989e
Pb98a0: jne Pb98f5 ; original $98a0
Pb98a2: lda PnNativeStageFlags ; original $98a2
Pb98a4: ora #$02 ; original $98a4
Pb98a6: sta PnNativeStageFlags ; original $98a6
jmp PbCallback98a8 ; native fallthrough into palette publication
Pb98f5: jsr PbCallback991e ; original $98f5
Pb98f8: rts ; original $98f8
Pb98f9: lda PnPhase,X ; original $98f9
Pb98fc: sec ; original $98fc
Pb98fd: sbc #$10 ; original $98fd
Pb98ff: jcs Pb990a ; original $98ff
Pb9901: lda PnBellFlags ; original $9901
Pb9903: and #$fe ; original $9903
Pb9905: sta PnBellFlags ; original $9905
Pb9907: jmp PbCallback9bba ; original $9907
Pb990a: sta PnPhase,X ; original $990a
Pb990d: cmp #$30 ; original $990d
Pb990f: jne Pb98f5 ; original $990f
Pb9911: lda PnNativeStageFlags ; original $9911
Pb9913: and #$fd ; original $9913
Pb9915: sta PnNativeStageFlags ; original $9915
Pb9917: lda #$02 ; original $9917
Pb9919: sta PnNativePaletteRestore ; original $9919
Pb991b: jmp Pb98f5 ; original $991b
Pb9a6b: lsr a ; original $9a6b
Pb9a6c: lsr a ; original $9a6c
Pb9a6d: jcs Pb9a72 ; original $9a6d
Pb9a6f: jmp Pb9bf7 ; original $9a6f
Pb9a72: lda PnActive,X ; original $9a72
Pb9a75: jne Pb9ac6 ; original $9a75
Pb9a77: lda PnRedRemaining ; original $9a77
Pb9a7a: jne Pb9a81 ; original $9a7a
Pb9a7c: lda #$03 ; original $9a7c
Pb9a7e: sta PnRedRemaining ; original $9a7e
Pb9a81: jsr Pb9c3d ; original $9a81
Pb9a84: jeq Pb9ac5 ; original $9a84
Pb9a86: lda #$27 ; original $9a86
Pb9a88: jsr PbCallbackfe20 ; original $9a88
Pb9a8b: dec PnRedRemaining ; original $9a8b
Pb9a8e: lda #$07 ; original $9a8e
Pb9a90: sta PnType,X ; original $9a90
Pb9a93: lda #$01 ; original $9a93
Pb9a95: sta PnDrawFlags,X ; original $9a95
Pb9a98: lda #$80 ; original $9a98
Pb9a9a: sta PnActive,X ; original $9a9a
Pb9a9d: lda PnX ; original $9a9d
Pb9aa0: sta PnX,X ; original $9aa0
Pb9aa3: lda PnY ; original $9aa3
Pb9aa6: sta PnY,X ; original $9aa6
Pb9aa9: lda #$10 ; original $9aa9
Pb9aab: sta PnAngle,X ; original $9aab
Pb9aae: ldy VvVariant ; original $9aae
Pb9ab0: lda Pb9bef,Y ; original $9ab0
Pb9ab3: sta PnFrame,X ; original $9ab3
Pb9ab6: lda #$00 ; original $9ab6
Pb9ab8: sta PnPalette,X ; original $9ab8
Pb9abb: lda #$ff ; original $9abb
Pb9abd: sta PnPhase,X ; original $9abd
Pb9ac0: lda #$01 ; original $9ac0
Pb9ac2: sta PnAux,X ; original $9ac2
Pb9ac5: rts ; original $9ac5
Pb9ac6: asl a ; original $9ac6
Pb9ac7: jcc Pb9b0f ; original $9ac7
Pb9ac9: dec PnAngle,X ; original $9ac9
Pb9acc: jne Pb9ae0 ; original $9acc
Pb9ace: lsr PnActive,X ; original $9ace
Pb9ad1: lda #$29 ; original $9ad1
Pb9ad3: jsr PbCallbackfe20 ; original $9ad3
Pb9ad6: ldy VvVariant ; original $9ad6
Pb9ad8: lda Pb9bf3,Y ; original $9ad8
Pb9adb: ldy #$00 ; original $9adb
Pb9add: jmp PbCallbackc977 ; original $9add
Pb9ae0: lda PnX,X ; original $9ae0
Pb9ae3: clc ; original $9ae3
Pb9ae4: adc #$04 ; original $9ae4
Pb9ae6: sta PnX,X ; original $9ae6
Pb9ae9: jcs Pb9aef ; original $9ae9
Pb9aeb: cmp #$f8 ; original $9aeb
Pb9aed: jcc Pb9af4 ; original $9aed
Pb9aef: lda #$f8 ; original $9aef
Pb9af1: sta PnX,X ; original $9af1
Pb9af4: lda PnY,X ; original $9af4
Pb9af7: sta R0 ; original $9af7
Pb9af9: lda PnX,X ; original $9af9
Pb9afc: sta M0 ; original $9afc
Pb9afe: lda #$00 ; original $9afe
Pb9b00: sta M1 ; original $9b00
Pb9b02: sta R1 ; original $9b02
Pb9b04: jsr PbCallbackc905 ; original $9b04
Pb9b07: cmp #$02 ; original $9b07
Pb9b09: jne Pb9b0e ; original $9b09
Pb9b0b: jmp PbCallback90e6 ; original $9b0b
Pb9b0e: rts ; original $9b0e
Pb9b0f: asl a ; original $9b0f
Pb9b10: jcc Pb9b2b ; original $9b10
Pb9b12: jsr Pb9bd5 ; original $9b12
Pb9b15: jsr Pb9b77 ; original $9b15
Pb9b18: jsr PbCallbackc98a ; original $9b18
Pb9b1b: lda PnAnimCursor,X ; original $9b1b
Pb9b1e: cmp #$04 ; original $9b1e
Pb9b20: jcc Pb9b2a ; original $9b20
Pb9b22: lsr PnActive,X ; original $9b22
Pb9b25: lda #$00 ; original $9b25
Pb9b27: sta PnEnemyIndex,X ; original $9b27
Pb9b2a: rts ; original $9b2a
Pb9b2b: asl a ; original $9b2b
Pb9b2c: jcc Pb9ba2 ; original $9b2c
Pb9b2e: lda PnEnemyIndex,X ; original $9b2e
Pb9b31: cmp #$10 ; original $9b31
Pb9b33: jcs Pb9b4f ; original $9b33
Pb9b35: and #$01 ; original $9b35
Pb9b37: tay ; original $9b37
Pb9b38: lda PnEnemyIndex,X ; original $9b38
Pb9b3b: inc PnEnemyIndex,X ; original $9b3b
Pb9b3e: and #$fe ; original $9b3e
Pb9b40: asl a ; original $9b40
Pb9b41: asl a ; original $9b41
Pb9b42: cpy #$01 ; original $9b42
Pb9b44: jeq Pb9b48 ; original $9b44
Pb9b46: eor #$ff ; original $9b46
Pb9b48: clc ; original $9b48
Pb9b49: adc PnY,X ; original $9b49
Pb9b4c: jsr Pb9af7 ; original $9b4c
Pb9b4f: lda PnX,X ; original $9b4f
Pb9b52: cmp #$10 ; original $9b52
Pb9b54: jcc Pb9b5e ; original $9b54
Pb9b56: lda PnPhase,X ; original $9b56
Pb9b59: ora PnAux,X ; original $9b59
Pb9b5c: jne Pb9b6b ; original $9b5c
Pb9b5e: lsr PnActive,X ; original $9b5e
Pb9b61: ldy VvVariant ; original $9b61
Pb9b63: lda Pb9beb,Y ; original $9b63
Pb9b66: ldy #$00 ; original $9b66
Pb9b68: jmp PbCallbackc977 ; original $9b68
Pb9b6b: dec PnPhase,X ; original $9b6b
Pb9b6e: ldy PnPhase,X ; original $9b6e
Pb9b71: iny ; original $9b71
Pb9b72: jne Pb9b77 ; original $9b72
Pb9b74: dec PnAux,X ; original $9b74
Pb9b77: lda PnXF,X ; original $9b77
Pb9b7a: sec ; original $9b7a
Pb9b7b: sbc PnNativeScrollXLo ; original $9b7b
Pb9b7d: sta PnXF,X ; original $9b7d
Pb9b80: lda PnX,X ; original $9b80
Pb9b83: sbc PnNativeScrollXHi ; original $9b83
Pb9b85: sta PnX,X ; original $9b85
Pb9b88: lda PnNativeScrollFlags ; original $9b88
Pb9b8a: and #$07 ; original $9b8a
Pb9b8c: jeq Pb9b9f ; original $9b8c
Pb9b8e: lda PnYF,X ; original $9b8e
Pb9b91: sec ; original $9b91
Pb9b92: sbc PnNativeWindLo ; original $9b92
Pb9b94: sta PnYF,X ; original $9b94
Pb9b97: lda PnY,X ; original $9b97
Pb9b9a: sbc PnNativeWindHi ; original $9b9a
Pb9b9c: sta PnY,X ; original $9b9c
Pb9b9f: jmp Pb9bd5 ; original $9b9f
Pb9ba2: jsr PbCallbackc98a ; original $9ba2
Pb9ba5: jsr Pb9b77 ; original $9ba5
Pb9ba8: lda PnAnimCursor,X ; original $9ba8
Pb9bab: cmp #$04 ; original $9bab
Pb9bad: jcc PbReturn ; original $9bad
Pb9baf: lda PnRedRemaining ; original $9baf
Pb9bb2: jne PbCallback9bba ; original $9bb2
Pb9bb4: lda PnBellFlags ; original $9bb4
Pb9bb6: and #$fb ; original $9bb6
Pb9bb8: sta PnBellFlags ; original $9bb8
jmp PbCallback9bba ; native final Red cleanup
Pb9bd5: lda VvClock ; original $9bd5
Pb9bd7: and #$03 ; original $9bd7
Pb9bd9: jne Pb9bea ; original $9bd9
Pb9bdb: inc PnPalette,X ; original $9bdb
Pb9bde: lda PnPalette,X ; original $9bde
Pb9be1: cmp #$03 ; original $9be1
Pb9be3: jcc Pb9bea ; original $9be3
Pb9be5: lda #$00 ; original $9be5
Pb9be7: sta PnPalette,X ; original $9be7
Pb9bea: rts ; original $9bea
Pb9bf7: lsr a ; original $9bf7
Pb9bf8: jcc Pb9c1d ; original $9bf8
Pb9bfa: ldx PnNativeVramBusy ; original $9bfa
Pb9bfc: cpx #$10 ; original $9bfc
Pb9bfe: jcs Pb9c1d ; original $9bfe
Pb9c00: lda PnBellFlags ; original $9c00
Pb9c02: and #$f7 ; original $9c02
Pb9c04: sta PnBellFlags ; original $9c04
Pb9c06: inc PnNativeLives ; original $9c06
Pb9c08: lda PnNativeLives ; original $9c08
Pb9c0a: and #$0f ; original $9c0a
Pb9c0c: cmp #$0a ; original $9c0c
Pb9c0e: jne Pb9c1a ; original $9c0e
Pb9c10: dec PnNativeLives ; original $9c10
Pb9c12: lda PnNativeLives ; original $9c12
Pb9c14: and #$f0 ; original $9c14
Pb9c16: adc #$10 ; original $9c16
Pb9c18: sta PnNativeLives ; original $9c18
Pb9c1a: jsr PbCallbackfd4e ; original $9c1a
Pb9c1d: rts ; original $9c1d
Pb9c1e: lda PnBellFlags ; original $9c1e
Pb9c20: and #$10 ; original $9c20
Pb9c22: jeq Pb9c3c ; original $9c22
Pb9c24: lda VvClock ; original $9c24
Pb9c26: and #$03 ; original $9c26
Pb9c28: jne Pb9c3c ; original $9c28
Pb9c2a: lda VvMeter ; original $9c2a
Pb9c2c: jne Pb9c30 ; original $9c2c
Pb9c2e: inc VvMeter ; original $9c2e
Pb9c30: asl VvMeter ; original $9c30
Pb9c32: lda VvMeter ; original $9c32
Pb9c34: and #$80 ; original $9c34
Pb9c36: jeq Pb9c3c ; original $9c36
Pb9c38: lda #$01 ; original $9c38
Pb9c3a: sta VvMeter ; original $9c3a
Pb9c3c: rts ; original $9c3c
Pb9c3d: lda VvFresh ; original $9c3d
Pb9c3f: and #$40 ; original $9c3f
Pb9c41: rts ; original $9c41
PbReturn:rts
PbCallback98a8:
 jmp PnBombPalettePrime
PbCallback991e:
 jmp PnBombPaletteAdjust
PbCallbackfb1d:
 jmp PnBombWorldDamage
PbCallbackfd4e:
 jmp PnBellGainLife
PbCallback9756:
 jmp PnBellBonusContact
PbCallbackfe20:
.ifdef PARODIUS_CPU_FIXTURE
 jmp PnSoundEvent
.else
 farcall PnSoundEvent,jmp
.endif
PbCallbackc905:
.ifdef PARODIUS_CPU_FIXTURE
 jmp PnTerrainQuery
.else
 farcall PnTerrainQuery,jmp
.endif
PbCallback90e6:
.ifdef PARODIUS_CPU_FIXTURE
 jmp PnTerrainImpact
.else
 farcall PnTerrainImpact,jmp
.endif
PbCallbackc977:
.ifdef PARODIUS_CPU_FIXTURE
 jmp PnNativeSetAnimation
.else
 farcall PnNativeSetAnimation,jmp
.endif
PbCallbackc98a:
.ifdef PARODIUS_CPU_FIXTURE
 jmp PnNativeAnimate
.else
 farcall PnNativeAnimate,jmp
.endif
PbCallback9bba:
.ifdef PARODIUS_CPU_FIXTURE
 jmp PnNativeKill
.else
 farcall PnNativeKill,jmp
.endif
PnNativePickup=Pb80b5
.export PnNativePickup
PnNativeBellUpdate=Pb97fc
.export PnNativeBellUpdate
PnNativeRoulette=Pb9c1e
.export PnNativeRoulette
.popseg
.pushseg
.segment "VIC_GFX"
Pb9a57:.byte 0
Pb9a58:.byte 0
Pb9a59:.byte 0
Pb9a5a:.byte 0
Pb9a5b:.byte 0
Pb9a5c:.byte 1
Pb9a5d:.byte 1
Pb9a5e:.byte 1
Pb9a5f:.byte 1
Pb9a60:.byte 1
Pb9a61:.byte 1
Pb9a62:.byte 0
Pb9a63:.byte 0
Pb9a64:.byte 0
Pb9a65:.byte 0
Pb9a66:.byte 0
Pb9a67:.byte 0
Pb9a68:.byte 0
Pb9a69:.byte 0
Pb9a6a:.byte 0
Pb9beb:.byte 19
Pb9bec:.byte 79
Pb9bed:.byte 19
Pb9bee:.byte 79
Pb9bef:.byte 57
Pb9bf0:.byte 185
Pb9bf1:.byte 57
Pb9bf2:.byte 185
Pb9bf3:.byte 18
Pb9bf4:.byte 78
Pb9bf5:.byte 18
Pb9bf6:.byte 78
.popseg
.ifndef PARODIUS_CPU_FIXTURE
.pushseg
.segment "VIC_WORLD"
PnBellColorSteps:.byte 0,1,0,2,0,4,0,3,0,1,0,2,0,4,0,3,0
PnBellContactTypes:.byte 6,7,9,10,8
.popseg
.endif
