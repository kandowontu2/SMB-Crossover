; Generated from the authenticated Gradius USA ROM. Do not hand-edit.
; Original local screen coordinates/clamps; world/camera adaptation is separate.
VvAlive=$5de8
VvAutoFire=$5de2
VvFireTimer=$5dec
VvFlags=$5de6
VvFresh=$5de4
VvGun=$5ddb
VvHeld=$5de3
VvHudDirty=$5df5
VvInitialized=$5de7
VvMeter=$5dda
VvMissile=$5dd9
VvObjAnim=$5d80
VvObjSub=$5d98
VvObjTimer=$5d8c
VvObjX=$5d40
VvObjXF=$5d60
VvObjY=$5d00
VvObjYF=$5d20
VvOptions=$5ddc
VvPlayer=$5dde
VvPrevious=$5de5
VvRingCursor=$5da4
VvRingX=$5da8
VvRingY=$5dc0
VvScoreBonus=$5deb
VvScoreDigit=$5de9
VvSfxEvent=$5dea
VvShield=$5ddd
VvSpeed=$5dd8
VvStepHi=$5de1
VvStepLo=$5de0
VvTilt=$5ddf
.export VvAlive,VvAutoFire,VvFireTimer,VvFlags,VvFresh,VvGun,VvHeld,VvHudDirty,VvInitialized,VvMeter,VvMissile,VvObjAnim,VvObjSub,VvObjTimer,VvObjX,VvObjXF,VvObjY,VvObjYF,VvOptions,VvPlayer,VvPrevious,VvRingCursor,VvRingX,VvRingY,VvScoreBonus,VvScoreDigit,VvSfxEvent,VvShield,VvSpeed,VvStepHi,VvStepLo,VvTilt
.pushseg
.segment "VIC_CORE"
.proc VvNativeMotion
Vna006: lda VvSpeed ; original$a006
Vna008: clc ; original$a008
Vna009: adc #$02 ; original$a009
Vna00b: cmp #$10 ; original$a00b
Vna00d: jcc Vna011 ; original$a00d
Vna00f: lda #$10 ; original$a00f
Vna011: sta VvStepHi ; original$a011
Vna013: lda #$00 ; original$a013
Vna015: sta VvStepLo ; original$a015
Vna017: lsr VvStepHi ; original$a017
Vna019: ror VvStepLo ; original$a019
Vna01b: ldy #$40 ; original$a01b
Vna01d: ldx VvPlayer ; original$a01d
Vna01f: lda VvHeld,X ; original$a01f
Vna021: and #$01 ; original$a021
Vna023: jeq Vna031 ; original$a023
Vna025: jsr Vna285 ; original$a025
Vna028: cmp #$f0 ; original$a028
Vna02a: jcc Vna02e ; original$a02a
Vna02c: lda #$f0 ; original$a02c
Vna02e: sta VvObjX ; original$a02e
Vna031: lda VvHeld,X ; original$a031
Vna033: and #$02 ; original$a033
Vna035: jeq Vna043 ; original$a035
Vna037: jsr Vna297 ; original$a037
Vna03a: cmp #$10 ; original$a03a
Vna03c: jcs Vna040 ; original$a03c
Vna03e: lda #$10 ; original$a03e
Vna040: sta VvObjX ; original$a040
Vna043: lda #$01 ; original$a043
Vna045: ldy #$00 ; original$a045
Vna047: sta VvTilt ; original$a047
Vna049: lda VvHeld,X ; original$a049
Vna04b: and #$04 ; original$a04b
Vna04d: jeq Vna063 ; original$a04d
Vna04f: lda VvObjY ; original$a04f
Vna052: cmp #$c0 ; original$a052
Vna054: jcs Vna063 ; original$a054
Vna056: jsr Vna285 ; original$a056
Vna059: cmp #$c0 ; original$a059
Vna05b: jcc Vna05f ; original$a05b
Vna05d: lda #$c0 ; original$a05d
Vna05f: ldy #$02 ; original$a05f
Vna061: jne Vna07b ; original$a061
Vna063: lda VvHeld,X ; original$a063
Vna065: and #$08 ; original$a065
Vna067: jeq Vna080 ; original$a067
Vna069: lda VvObjY ; original$a069
Vna06c: cmp #$10 ; original$a06c
Vna06e: jcc Vna080 ; original$a06e
Vna070: jsr Vna297 ; original$a070
Vna073: cmp #$10 ; original$a073
Vna075: jcs Vna079 ; original$a075
Vna077: lda #$10 ; original$a077
Vna079: ldy #$03 ; original$a079
Vna07b: sty VvTilt ; original$a07b
Vna07d: sta VvObjY ; original$a07d
Vna080: lda VvHeld,X ; original$a080
Vna082: and #$0f ; original$a082
Vna084: jeq Vna0ad ; original$a084
Vna086: lda VvRingCursor ; original$a086
Vna089: clc ; original$a089
Vna08a: adc #$01 ; original$a08a
Vna08c: cmp #$18 ; original$a08c
Vna08e: jcc Vna092 ; original$a08e
Vna090: sbc #$18 ; original$a090
Vna092: sta VvRingCursor ; original$a092
Vna095: tay ; original$a095
Vna096: lda VvObjX ; original$a096
Vna099: sta VvRingX,Y ; original$a099
Vna09c: lda VvObjY ; original$a09c
Vna09f: sta VvRingY,Y ; original$a09f
Vna0a2: ldy #$01 ; original$a0a2
Vna0a4: lda VvRingCursor ; original$a0a4
Vna0a7: jsr Vna2a9 ; original$a0a7
Vna0aa: jsr Vna2a9 ; original$a0aa
Vna0ad: inc VvObjTimer ; original$a0ad
Vna0b0: jpl Vna0b7 ; original$a0b0
Vna0b2: lda #$10 ; original$a0b2
Vna0b4: sta VvObjTimer ; original$a0b4
Vna0b7: lda VvObjTimer ; original$a0b7
Vna0ba: cmp #$08 ; original$a0ba
Vna0bc: jcc Vna0c8 ; original$a0bc
Vna0be: lda VvTilt ; original$a0be
Vna0c0: sta VvObjAnim ; original$a0c0
Vna0c3: lda #$00 ; original$a0c3
Vna0c5: sta VvObjTimer ; original$a0c5
Vna0c8: ldx VvOptions ; original$a0c8
Vna0ca: dex ; original$a0ca
Vna0cb: jmi VvMotionEnd ; original$a0cb
Vna0cd: inc VvObjTimer+1,X ; original$a0cd
Vna0d0: lda VvObjTimer+1,X ; original$a0d0
Vna0d3: lsr a ; original$a0d3
Vna0d4: lsr a ; original$a0d4
Vna0d5: lsr a ; original$a0d5
Vna0d6: and #$01 ; original$a0d6
Vna0d8: clc ; original$a0d8
Vna0d9: adc #$04 ; original$a0d9
Vna0db: sta VvObjAnim+1,X ; original$a0db
Vna0de: jne Vna0ca ; original$a0de
VvMotionEnd: rts
Vna285: lda VvStepLo ; original$a285
Vna287: clc ; original$a287
Vna288: adc VvObjYF,Y ; original$a288
Vna28b: sta VvObjYF,Y ; original$a28b
Vna28e: lda VvStepHi ; original$a28e
Vna290: adc VvObjY,Y ; original$a290
Vna293: sta VvObjY,Y ; original$a293
Vna296: rts ; original$a296
Vna297: lda VvObjYF,Y ; original$a297
Vna29a: sec ; original$a29a
Vna29b: sbc VvStepLo ; original$a29b
Vna29d: sta VvObjYF,Y ; original$a29d
Vna2a0: lda VvObjY,Y ; original$a2a0
Vna2a3: sbc VvStepHi ; original$a2a3
Vna2a5: sta VvObjY,Y ; original$a2a5
Vna2a8: rts ; original$a2a8
Vna2a9: sec ; original$a2a9
Vna2aa: sbc #$0b ; original$a2aa
Vna2ac: jcs Vna2b0 ; original$a2ac
Vna2ae: adc #$18 ; original$a2ae
Vna2b0: tax ; original$a2b0
Vna2b1: lda VvRingX,X ; original$a2b1
Vna2b4: sta VvObjX,Y ; original$a2b4
Vna2b7: lda VvRingY,X ; original$a2b7
Vna2ba: sta VvObjY,Y ; original$a2ba
Vna2bd: iny ; original$a2bd
Vna2be: txa ; original$a2be
Vna2bf: rts ; original$a2bf
.endproc
.popseg
.include "vic_gear.s"
.include "vic_native_weapons.s"
