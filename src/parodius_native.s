; Generated original Famicom Parodius player/weapon component.
; Integration callbacks are mandatory; this file alone is not playable.
.if ::MAPPER_MMC5
PnType=$5c00
.else
PnType=RgAudioRam+0
.endif
.if ::MAPPER_MMC5
PnContact=$5c1c
.else
PnContact=RgAudioRam+28
.endif
.if ::MAPPER_MMC5
PnX=$5c38
.else
PnX=RgAudioRam+56
.endif
.if ::MAPPER_MMC5
PnXF=$5c54
.else
PnXF=RgAudioRam+84
.endif
.if ::MAPPER_MMC5
PnY=$5c70
.else
PnY=RgAudioRam+112
.endif
.if ::MAPPER_MMC5
PnYF=$5c8c
.else
PnYF=RgAudioRam+140
.endif
.if ::MAPPER_MMC5
PnVX=$5ca8
.else
PnVX=RgAudioRam+168
.endif
.if ::MAPPER_MMC5
PnVXF=$5cc4
.else
PnVXF=RgAudioRam+196
.endif
.if ::MAPPER_MMC5
PnVY=$5ce0
.else
PnVY=RgAudioRam+224
.endif
.if ::MAPPER_MMC5
PnVYF=$5e00
.else
PnVYF=MmAudioRamStart+128
.endif
.if ::MAPPER_MMC5
PnDrawFlags=$5e1c
.else
PnDrawFlags=MmAudioRamStart+156
.endif
.if ::MAPPER_MMC5
PnFrame=$5e38
.else
PnFrame=MmAudioRamStart+184
.endif
.if ::MAPPER_MMC5
PnPalette=$5e54
.else
PnPalette=MmAudioRamStart+212
.endif
.if ::MAPPER_MMC5
PnAngle=$5e70
.else
PnAngle=MmAudioRamStart+240
.endif
.if ::MAPPER_MMC5
PnPhase=$5e8c
.else
PnPhase=MmAudioRamStart+268
.endif
.if ::MAPPER_MMC5
PnAux=$5ea8
.else
PnAux=MmAudioRamStart+296
.endif
.if ::MAPPER_MMC5
PnActive=$5ec4
.else
PnActive=MmAudioRamStart+324
.endif
.if ::MAPPER_MMC5
PnAnimDelay=$5ee0
.else
PnAnimDelay=MmAudioRamStart+352
.endif
.if ::MAPPER_MMC5
PnAnimCursor=$5f00
.else
PnAnimCursor=MmAudioRamStart+0
.endif
.if ::MAPPER_MMC5
PnAnimation=$5f1c
.else
PnAnimation=MmAudioRamStart+28
.endif
.if ::MAPPER_MMC5
PnHistory=$5f40
.else
PnHistory=MmAudioRamStart+384
.endif
PnPunch=$5d80
PnEnemyIndex=$5d41
PnEnemyType=$5dec
PnBigStage=$5da9
PnBigTimerHi=$5daa
PnBigTimerLo=$5dab
PnBellFlags=$5da8
PnSkin=$5dac
VvVariant=$5fea
PnAutoMode=$5dad
PnAutoIndex=$5dae
PnNativeStage=$5daf
PnNativeStageFlags=$5db0
PnNativeWindHi=$5db1
PnNativeWindLo=$5db2
PnNativeScroll=$5db3
PnNativeRocketWait=$5db4
PnNativeObjectStart=$5db5
PnNativeStage60=$5db6
PnNativeStage63=$5db7
PnNativeStage64=$5db8
PnScratch04=$5d68
PnScratch05=$5d69
PnScratch06=$5d6a
PnScratch07=$5d6b
PnScratch08=$5d6c
PnScratch09=$5d6d
PnScratch0a=$5d6e
PnScratch0b=$5d6f
PnScratch0c=$5d70
PnScratch0d=$5d71
PnScratch0e=$5d72
PnScratch0f=$5d73
PnScratch15=$5d74
PnScratch17=$5d75
PnScratch18=$5d76
.if ::MAPPER_MMC5
PnHitMask=$5fc0
.else
PnHitMask=MmAudioRamStart+64
.endif
.export PnType,PnContact,PnX,PnXF,PnY,PnYF,PnVX,PnVXF,PnVY,PnVYF,PnDrawFlags,PnFrame,PnPalette,PnAngle,PnPhase,PnAux,PnActive,PnAnimDelay,PnAnimCursor,PnAnimation,PnHistory,PnPunch,PnEnemyIndex,PnEnemyType,PnBigStage,PnBigTimerHi,PnBigTimerLo,PnBellFlags,PnSkin,VvVariant,PnAutoMode,PnAutoIndex,PnNativeStage,PnNativeStageFlags,PnNativeWindHi,PnNativeWindLo,PnNativeScroll,PnNativeRocketWait,PnNativeObjectStart,PnNativeStage60,PnNativeStage63,PnNativeStage64,PnScratch04,PnScratch05,PnScratch06,PnScratch07,PnScratch08,PnScratch09,PnScratch0a,PnScratch0b,PnScratch0c,PnScratch0d,PnScratch0e,PnScratch0f,PnScratch15,PnScratch17,PnScratch18,PnHitMask
.pushseg
.segment "VIC_CORE"
Pn8191: lda PnBigStage ; original $8191
Pn8194: jne Pn81a7 ; original $8194
Pn8196: lda PnPhase ; original $8196
Pn8199: jne Pn81b5 ; original $8199
Pn819b: lda #$20 ; original $819b
Pn819d: sta PnBigTimerHi ; original $819d
Pn81a0: lda #$80 ; original $81a0
Pn81a2: sta PnBigStage ; original $81a2
Pn81a5: jne Pn81b5 ; original $81a5
Pn81a7: asl a ; original $81a7
Pn81a8: jcc Pn81f2 ; original $81a8
Pn81aa: lda PnBigTimerHi ; original $81aa
Pn81ad: jeq Pn81c8 ; original $81ad
Pn81af: dec PnBigTimerHi ; original $81af
Pn81b2: jsr Pn81b8 ; original $81b2
Pn81b5: jmp Pn8268 ; original $81b5
Pn81b8: inc PnPalette ; original $81b8
Pn81bb: lda PnPalette ; original $81bb
Pn81be: cmp #$03 ; original $81be
Pn81c0: jcc Pn81c7 ; original $81c0
Pn81c2: lda #$00 ; original $81c2
Pn81c4: sta PnPalette ; original $81c4
Pn81c7: rts ; original $81c7
Pn81c8: ldy VvVariant ; original $81c8
Pn81ca: lda Pn932a,Y ; original $81ca
Pn81cd: sta PnFrame ; original $81cd
Pn81d0: lsr PnBigStage ; original $81d0
Pn81d3: lda #$04 ; original $81d3
Pn81d5: sta PnBigTimerHi ; original $81d5
Pn81d8: lda #$ff ; original $81d8
Pn81da: sta PnBigTimerLo ; original $81da
Pn81dd: lda #$00 ; original $81dd
Pn81df: sta PnPalette ; original $81df
Pn81e2: lda Pn9326,Y ; original $81e2
Pn81e5: sta PnSkin ; original $81e5
Pn81e7: jsr PnPublishSkin ; original $81e7
Pn81ea: lda #$24 ; original $81ea
Pn81ec: jsr PnSoundEvent ; original $81ec
Pn81ef: jmp Pn8268 ; original $81ef
Pn81f2: asl a ; original $81f2
Pn81f3: jcc Pn822b ; original $81f3
Pn81f5: lda #$08 ; original $81f5
Pn81f7: sta PnType ; original $81f7
Pn81fa: dec PnBigTimerLo ; original $81fa
Pn81fd: ldy PnBigTimerLo ; original $81fd
Pn8200: iny ; original $8200
Pn8201: jne Pn8206 ; original $8201
Pn8203: dec PnBigTimerHi ; original $8203
Pn8206: lda PnBigTimerLo ; original $8206
Pn8209: ora PnBigTimerHi ; original $8209
Pn820c: jne Pn824c ; original $820c
Pn820e: lsr PnBigStage ; original $820e
Pn8211: lda #$00 ; original $8211
Pn8213: sta PnPhase ; original $8213
Pn8216: lda VvVariant ; original $8216
Pn8218: sta PnSkin ; original $8218
Pn821a: lda #$01 ; original $821a
Pn821c: sta PnType ; original $821c
Pn821f: lda #$25 ; original $821f
Pn8221: jsr PnSoundEvent ; original $8221
Pn8224: lda #$40 ; original $8224
Pn8226: sta PnBigTimerHi ; original $8226
Pn8229: jne Pn8268 ; original $8229
Pn822b: lda PnBigTimerHi ; original $822b
Pn822e: jeq Pn823a ; original $822e
Pn8230: jsr Pn81b8 ; original $8230
Pn8233: dec PnBigTimerHi ; original $8233
Pn8236: jne Pn8268 ; original $8236
Pn8238: lda #$00 ; original $8238
Pn823a: sta PnPalette ; original $823a
Pn823d: sta PnBigStage ; original $823d
Pn8240: sta PnBigTimerHi ; original $8240
Pn8243: sta PnBigTimerLo ; original $8243
Pn8246: lda PnBellFlags ; original $8246
Pn8248: and #$10 ; original $8248
Pn824a: sta PnBellFlags ; original $824a
Pn824c: lda VvHeld ; original $824c
Pn824e: and #$0c ; original $824e
Pn8250: jeq Pn8268 ; original $8250
Pn8252: and #$08 ; original $8252
Pn8254: jne Pn825f ; original $8254
Pn8256: lda PnPhase ; original $8256
Pn8259: cmp #$20 ; original $8259
Pn825b: jeq Pn8278 ; original $825b
Pn825d: jne Pn8275 ; original $825d
Pn825f: lda PnPhase ; original $825f
Pn8262: cmp #$df ; original $8262
Pn8264: jeq Pn8278 ; original $8264
Pn8266: jne Pn826f ; original $8266
Pn8268: lda PnPhase ; original $8268
Pn826b: jeq Pn8278 ; original $826b
Pn826d: jmi Pn8275 ; original $826d
Pn826f: dec PnPhase ; original $826f
Pn8272: jmp Pn8278 ; original $8272
Pn8275: inc PnPhase ; original $8275
Pn8278: jsr Pn8c19 ; original $8278
Pn827b: lda PnBigStage ; original $827b
Pn827e: and #$40 ; original $827e
Pn8280: jeq Pn828a ; original $8280
Pn8282: lda Pn9262,Y ; original $8282
Pn8285: sta PnAngle ; original $8285
Pn8288: jne Pn82b1 ; original $8288
Pn828a: lda Pn9244,Y ; original $828a
Pn828d: sta PnAngle ; original $828d
Pn8290: lda PnActive,X ; original $8290
Pn8293: and #$40 ; original $8293
Pn8295: jeq Pn82b1 ; original $8295
Pn8297: lda PnAnimCursor ; original $8297
Pn829a: cmp Pn92a3,Y ; original $829a
Pn829d: jne Pn82a9 ; original $829d
Pn829f: lda PnActive ; original $829f
Pn82a2: and #$bf ; original $82a2
Pn82a4: sta PnActive ; original $82a4
Pn82a7: jne Pn82b1 ; original $82a7
Pn82a9: lda Pn9280,Y ; original $82a9
Pn82ac: sta PnAnimation ; original $82ac
Pn82af: jne Pn82c1 ; original $82af
Pn82b1: lda PnAngle ; original $82b1
Pn82b4: cmp PnAnimation ; original $82b4
Pn82b7: jeq Pn82c1 ; original $82b7
Pn82b9: lda PnAngle ; original $82b9
Pn82bc: ldy #$00 ; original $82bc
Pn82be: jsr Pnc977 ; original $82be
Pn82c1: jsr Pnc98a ; original $82c1
Pn82c4: jsr Pn8b4b ; original $82c4
Pn82c7: lda PnBellFlags ; original $82c7
Pn82c9: and #$40 ; original $82c9
Pn82cb: jeq Pn82d0 ; original $82cb
Pn82cd: jmp PnMotionEnd ; original $82cd
Pn82d0: lda PnXF ; original $82d0
Pn82d3: clc ; original $82d3
Pn82d4: adc PnVXF ; original $82d4
Pn82d7: sta PnXF ; original $82d7
Pn82da: lda PnX ; original $82da
Pn82dd: adc PnVX ; original $82dd
Pn82e0: tay ; original $82e0
Pn82e1: jcs Pn82f0 ; original $82e1
Pn82e3: lda PnVX ; original $82e3
Pn82e6: jmi Pn82fe ; original $82e6
Pn82e8: cpy #$f6 ; original $82e8
Pn82ea: jcc Pn82fb ; original $82ea
Pn82ec: ldy #$f5 ; original $82ec
Pn82ee: jpl Pn82fb ; original $82ee
Pn82f0: lda PnVX ; original $82f0
Pn82f3: jpl Pn82fe ; original $82f3
Pn82f5: cpy #$0e ; original $82f5
Pn82f7: jcs Pn82fb ; original $82f7
Pn82f9: ldy #$0e ; original $82f9
Pn82fb: sty PnX ; original $82fb
Pn82fe: lda PnYF ; original $82fe
Pn8301: clc ; original $8301
Pn8302: adc PnVYF ; original $8302
Pn8305: sta PnYF ; original $8305
Pn8308: lda PnY ; original $8308
Pn830b: adc PnVY ; original $830b
Pn830e: tay ; original $830e
Pn830f: jcs Pn8318 ; original $830f
Pn8311: lda PnVY ; original $8311
Pn8314: jmi Pn8360 ; original $8314
Pn8316: jpl Pn831f ; original $8316
Pn8318: lda PnVY ; original $8318
Pn831b: jpl Pn8360 ; original $831b
Pn831d: jmi Pn831f ; original $831d
Pn831f: cpy #$10 ; original $831f
Pn8321: jcc Pn832b ; original $8321
Pn8323: cpy #$c9 ; original $8323
Pn8325: jcc Pn832d ; original $8325
Pn8327: ldy #$c8 ; original $8327
Pn8329: jne Pn832d ; original $8329
Pn832b: ldy #$10 ; original $832b
Pn832d: lda PnNativeStageFlags ; original $832d
Pn832f: and #$08 ; original $832f
Pn8331: jeq Pn835d ; original $8331
Pn8333: tya ; original $8333
Pn8334: sec ; original $8334
Pn8335: sbc #$40 ; original $8335
Pn8337: jcs Pn8349 ; original $8337
Pn8339: cmp #$fa ; original $8339
Pn833b: jcs Pn8345 ; original $833b
Pn833d: tya ; original $833d
Pn833e: clc ; original $833e
Pn833f: adc VvSpeed ; original $833f
Pn8341: tay ; original $8341
Pn8342: iny ; original $8342
Pn8343: jne Pn835d ; original $8343
Pn8345: ldy #$3f ; original $8345
Pn8347: jne Pn835d ; original $8347
Pn8349: tya ; original $8349
Pn834a: sec ; original $834a
Pn834b: sbc #$90 ; original $834b
Pn834d: jcc Pn835d ; original $834d
Pn834f: cmp #$06 ; original $834f
Pn8351: jcc Pn835b ; original $8351
Pn8353: tya ; original $8353
Pn8354: sec ; original $8354
Pn8355: sbc VvSpeed ; original $8355
Pn8357: tay ; original $8357
Pn8358: dey ; original $8358
Pn8359: jne Pn835d ; original $8359
Pn835b: ldy #$90 ; original $835b
Pn835d: sty PnY ; original $835d
Pn8360: lda VvRingCursor ; original $8360
Pn8362: asl a ; original $8362
Pn8363: tay ; original $8363
Pn8364: lda VvFresh ; original $8364
Pn8366: ora VvHeld ; original $8366
Pn8368: and #$0f ; original $8368
Pn836a: sta M0 ; original $836a
Pn836c: lda VvVariant ; original $836c
Pn836e: cmp #$02 ; original $836e
Pn8370: jcs Pn8378 ; original $8370
Pn8372: lda M0 ; original $8372
Pn8374: jeq PnMotionEnd ; original $8374
Pn8376: jne Pn8378 ; original $8376
Pn8378: inc VvRingCursor ; original $8378
Pn837a: lda VvRingCursor ; original $837a
Pn837c: and #$3f ; original $837c
Pn837e: sta VvRingCursor ; original $837e
Pn8380: asl a ; original $8380
Pn8381: tay ; original $8381
Pn8382: lda PnX ; original $8382
Pn8385: sta PnHistory,Y ; original $8385
Pn8388: lda PnY ; original $8388
Pn838b: sta PnHistory+1,Y ; original $838b
Pn838e: lda PnNativeStageFlags ; original $838e
Pn8390: and #$08 ; original $8390
Pn8392: jeq PnMotionEnd ; original $8392
Pn8394: lda PnNativeWindHi ; original $8394
Pn8396: sta M0 ; original $8396
Pn8398: lda PnNativeWindLo ; original $8398
Pn839a: clc ; original $839a
Pn839b: adc PnNativeScroll ; original $839b
Pn839d: jcc Pn83a1 ; original $839d
Pn839f: inc M0 ; original $839f
Pn83a1: ldy #$00 ; original $83a1
Pn83a3: lda PnHistory+1,Y ; original $83a3
Pn83a6: sec ; original $83a6
Pn83a7: sbc M0 ; original $83a7
Pn83a9: sta PnHistory+1,Y ; original $83a9
Pn83ac: iny ; original $83ac
Pn83ad: iny ; original $83ad
Pn83ae: cpy #$80 ; original $83ae
Pn83b0: jcc Pn83a3 ; original $83b0
PnMotionEnd:rts
Pn83b2: lda PnAutoMode ; original $83b2
Pn83b4: jeq Pn83df ; original $83b4
Pn83b6: ldy PnAutoIndex ; original $83b6
Pn83b8: lda PnNativeStage ; original $83b8
Pn83ba: cmp #$03 ; original $83ba
Pn83bc: jcc Pn83ce ; original $83bc
Pn83be: cpy #$04 ; original $83be
Pn83c0: jcc Pn83ce ; original $83c0
Pn83c2: lda VvSpeed ; original $83c2
Pn83c4: cmp #$02 ; original $83c4
Pn83c6: jcs Pn83ce ; original $83c6
Pn83c8: lda VvMeter ; original $83c8
Pn83ca: cmp #$01 ; original $83ca
Pn83cc: jeq Pn83e5 ; original $83cc
Pn83ce: lda VvMeter ; original $83ce
Pn83d0: cmp Pn933a,Y ; original $83d0
Pn83d3: jne Pn83f1 ; original $83d3
Pn83d5: lda #$09 ; original $83d5
Pn83d7: cmp PnAutoIndex ; original $83d7
Pn83d9: jcc Pn83e5 ; original $83d9
Pn83db: inc PnAutoIndex ; original $83db
Pn83dd: jne Pn83e5 ; original $83dd
Pn83df: lda VvFresh ; original $83df
Pn83e1: and #$80 ; original $83e1
Pn83e3: jeq Pn83f1 ; original $83e3
Pn83e5: lda VvFlags ; original $83e5
Pn83e7: eor #$ff ; original $83e7
Pn83e9: sta M0 ; original $83e9
Pn83eb: lda VvMeter ; original $83eb
Pn83ed: and M0 ; original $83ed
Pn83ef: jne Pn83f4 ; original $83ef
Pn83f1: jmp PnGearEnd ; original $83f1
Pn83f4: pha ; original $83f4
Pn83f5: ldy #$38 ; original $83f5
Pn83f7: cmp #$20 ; original $83f7
Pn83f9: jeq Pn83fd ; original $83f9
Pn83fb: ldy #$39 ; original $83fb
Pn83fd: tya ; original $83fd
Pn83fe: jsr PnSoundEvent ; original $83fe
Pn8401: lda PnBellFlags ; original $8401
Pn8403: and #$ef ; original $8403
Pn8405: sta PnBellFlags ; original $8405
Pn8407: pla ; original $8407
Pn8408: tay ; original $8408
Pn8409: ldx #$00 ; original $8409
Pn840b: lsr a ; original $840b
Pn840c: jcs Pn8411 ; original $840c
Pn840e: inx ; original $840e
Pn840f: jne Pn840b ; original $840f
Pn8411: cpx #$00 ; original $8411
Pn8413: jeq Pn845b ; original $8413
Pn8415: cpx #$05 ; original $8415
Pn8417: jeq Pn8437 ; original $8417
Pn8419: cpx #$04 ; original $8419
Pn841b: jne Pn8442 ; original $841b
Pn841d: inc VvGun ; original $841d
Pn841f: lda VvVariant ; original $841f
Pn8421: cmp #$02 ; original $8421
Pn8423: jcc Pn842f ; original $8423
Pn8425: lda VvGun ; original $8425
Pn8427: and #$03 ; original $8427
Pn8429: cmp #$03 ; original $8429
Pn842b: jne Pn848f ; original $842b
Pn842d: jeq Pn8488 ; original $842d
Pn842f: lda VvGun ; original $842f
Pn8431: and #$04 ; original $8431
Pn8433: jeq Pn848f ; original $8433
Pn8435: jne Pn8488 ; original $8435
Pn8437: jsr Pnc8d7 ; original $8437
Pn843a: jsr Pn90cf ; original $843a
Pn843d: sta PnPunch ; original $843d
Pn8440: jeq Pn8488 ; original $8440
Pn8442: lda Pn9215,X ; original $8442
Pn8445: and #$c0 ; original $8445
Pn8447: jeq Pn844f ; original $8447
Pn8449: lda VvFlags ; original $8449
Pn844b: and #$f3 ; original $844b
Pn844d: sta VvFlags ; original $844d
Pn844f: lda Pn920d,X ; original $844f
Pn8452: and VvGun ; original $8452
Pn8454: ora Pn9215,X ; original $8454
Pn8457: sta VvGun ; original $8457
Pn8459: jne Pn8488 ; original $8459
Pn845b: lda PnNativeStageFlags ; original $845b
Pn845d: and #$20 ; original $845d
Pn845f: jne Pn8480 ; original $845f
Pn8461: lda PnBellFlags ; original $8461
Pn8463: and #$20 ; original $8463
Pn8465: jne Pn8480 ; original $8465
Pn8467: tya ; original $8467
Pn8468: pha ; original $8468
Pn8469: ldx #$00 ; original $8469
Pn846b: jsr Pn8c19 ; original $846b
Pn846e: lda Pn9280,Y ; original $846e
Pn8471: ldy #$00 ; original $8471
Pn8473: jsr Pnc977 ; original $8473
Pn8476: lda #$40 ; original $8476
Pn8478: ora PnActive ; original $8478
Pn847b: sta PnActive ; original $847b
Pn847e: pla ; original $847e
Pn847f: tay ; original $847f
Pn8480: inc VvSpeed ; original $8480
Pn8482: lda VvSpeed ; original $8482
Pn8484: cmp #$04 ; original $8484
Pn8486: jne Pn848f ; original $8486
Pn8488: tya ; original $8488
Pn8489: ora VvFlags ; original $8489
Pn848b: and #$df ; original $848b
Pn848d: sta VvFlags ; original $848d
Pn848f: lda #$00 ; original $848f
Pn8491: sta VvMeter ; original $8491
PnGearEnd:rts
Pn8493: lda VvVariant ; original $8493
Pn8495: cmp #$02 ; original $8495
Pn8497: jne Pn84b4 ; original $8497
Pn8499: lda VvFlags ; original $8499
Pn849b: and #$08 ; original $849b
Pn849d: jne Pn84b4 ; original $849d
Pn849f: lda PnNativeRocketWait ; original $849f
Pn84a1: and #$08 ; original $84a1
Pn84a3: jeq Pn84b4 ; original $84a3
Pn84a5: lda #$00 ; original $84a5
Pn84a7: ldy #$0b ; original $84a7
Pn84a9: sta PnActive,Y ; original $84a9
Pn84ac: sta PnFrame,Y ; original $84ac
Pn84af: iny ; original $84af
Pn84b0: cpy #$10 ; original $84b0
Pn84b2: jne Pn84a9 ; original $84b2
Pn84b4: lda PnBellFlags ; original $84b4
Pn84b6: and #$40 ; original $84b6
Pn84b8: jeq Pn84bd ; original $84b8
Pn84ba: jmp Pn8bff ; original $84ba
Pn84bd: lda PnNativeStageFlags ; original $84bd
Pn84bf: and #$20 ; original $84bf
Pn84c1: jeq Pn84da ; original $84c1
Pn84c3: jsr Pn8bff ; original $84c3
Pn84c6: lda PnNativeObjectStart ; original $84c6
Pn84c8: sta PnScratch17 ; original $84c8
Pn84ca: ldx #$01 ; original $84ca
Pn84cc: dec PnScratch17 ; original $84cc
Pn84ce: jeq Pn84d7 ; original $84ce
Pn84d0: jsr PnSourceExit ; original $84d0
Pn84d3: inx ; original $84d3
Pn84d4: jmp Pn84cc ; original $84d4
Pn84d7: jmp Pn8b15 ; original $84d7
Pn84da: lda PnBellFlags ; original $84da
Pn84dc: and #$02 ; original $84dc
Pn84de: jeq Pn84e6 ; original $84de
Pn84e0: jsr Pn8c03 ; original $84e0
Pn84e3: jmp Pn8b15 ; original $84e3
Pn84e6: lda VvGun ; original $84e6
Pn84e8: and #$07 ; original $84e8
Pn84ea: sta PnScratch17 ; original $84ea
Pn84ec: inc PnScratch17 ; original $84ec
Pn84ee: ldy #$00 ; original $84ee
Pn84f0: sty PnScratch15 ; original $84f0
Pn84f2: cpy #$01 ; original $84f2
Pn84f4: jcc Pn8549 ; original $84f4
Pn84f6: lda Pn921d,Y ; original $84f6
Pn84f9: sta M0 ; original $84f9
Pn84fb: lda VvRingCursor ; original $84fb
Pn84fd: sec ; original $84fd
Pn84fe: sbc M0 ; original $84fe
Pn8500: and #$3f ; original $8500
Pn8502: asl a ; original $8502
Pn8503: tax ; original $8503
Pn8504: lda PnHistory,X ; original $8504
Pn8507: sta PnX,Y ; original $8507
Pn850a: lda PnHistory+1,X ; original $850a
Pn850d: sta PnY,Y ; original $850d
Pn8510: tya ; original $8510
Pn8511: tax ; original $8511
Pn8512: ldy PnScratch15 ; original $8512
Pn8514: lda PnPunch,Y ; original $8514
Pn8517: jeq Pn851d ; original $8517
Pn8519: ldy #$04 ; original $8519
Pn851b: jne Pn851f ; original $851b
Pn851d: ldy VvVariant ; original $851d
Pn851f: lda Pn92e1,Y ; original $851f
Pn8522: sta PnPhase,X ; original $8522
Pn8525: lda PnActive,X ; original $8525
Pn8528: and #$80 ; original $8528
Pn852a: jeq Pn8534 ; original $852a
Pn852c: lda PnPhase,X ; original $852c
Pn852f: cmp PnAnimation,X ; original $852f
Pn8532: jeq Pn8546 ; original $8532
Pn8534: lda #$00 ; original $8534
Pn8536: sta PnDrawFlags,X ; original $8536
Pn8539: lda PnPhase,X ; original $8539
Pn853c: ldy #$00 ; original $853c
Pn853e: jsr Pnc977 ; original $853e
Pn8541: lda #$80 ; original $8541
Pn8543: sta PnActive,X ; original $8543
Pn8546: jsr Pnc98a ; original $8546
Pn8549: ldy PnScratch15 ; original $8549
Pn854b: lda VvGun ; original $854b
Pn854d: and #$c0 ; original $854d
Pn854f: jne Pn8594 ; original $854f
Pn8551: lda #$02 ; original $8551
Pn8553: sta PnScratch0f ; original $8553
Pn8555: lda VvFresh ; original $8555
Pn8557: sta PnScratch0e ; original $8557
Pn8559: lda #$10 ; original $8559
Pn855b: ldy PnScratch15 ; original $855b
Pn855d: jsr Pn8f83 ; original $855d
Pn8560: lda PnActive,X ; original $8560
Pn8563: and #$80 ; original $8563
Pn8565: jne Pn8589 ; original $8565
Pn8567: lda PnScratch0e ; original $8567
Pn8569: and #$40 ; original $8569
Pn856b: jeq Pn858e ; original $856b
Pn856d: lda #$02 ; original $856d
Pn856f: sta PnType,X ; original $856f
Pn8572: jsr Pn8d26 ; original $8572
Pn8575: ldy VvVariant ; original $8575
Pn8577: lda Pn92f2,Y ; original $8577
Pn857a: sta PnFrame,X ; original $857a
Pn857d: lda #$00 ; original $857d
Pn857f: sta PnScratch0e ; original $857f
Pn8581: lda #$07 ; original $8581
Pn8583: jsr PnSoundEvent ; original $8583
Pn8586: jmp Pn858e ; original $8586
Pn8589: ldy PnScratch15 ; original $8589
Pn858b: jsr Pn8d73 ; original $858b
Pn858e: lda #$15 ; original $858e
Pn8590: dec PnScratch0f ; original $8590
Pn8592: jne Pn855b ; original $8592
Pn8594: lda VvGun ; original $8594
Pn8596: and #$08 ; original $8596
Pn8598: jne Pn859d ; original $8598
Pn859a: jmp Pn868b ; original $859a
Pn859d: lda #$00 ; original $859d
Pn859f: sta PnScratch0e ; original $859f
Pn85a1: lda #$02 ; original $85a1
Pn85a3: sta PnScratch0f ; original $85a3
Pn85a5: lda VvVariant ; original $85a5
Pn85a7: cmp #$01 ; original $85a7
Pn85a9: jeq Pn85ad ; original $85a9
Pn85ab: dec PnScratch0f ; original $85ab
Pn85ad: lda #$06 ; original $85ad
Pn85af: ldy PnScratch15 ; original $85af
Pn85b1: jsr Pn8f83 ; original $85b1
Pn85b4: lda PnActive,X ; original $85b4
Pn85b7: and #$80 ; original $85b7
Pn85b9: jeq Pn85be ; original $85b9
Pn85bb: jmp Pn8644 ; original $85bb
Pn85be: lda VvFresh ; original $85be
Pn85c0: and #$40 ; original $85c0
Pn85c2: jne Pn85c7 ; original $85c2
Pn85c4: jmp Pn8682 ; original $85c4
Pn85c7: ldy VvVariant ; original $85c7
Pn85c9: jne Pn85d3 ; original $85c9
Pn85cb: ldy PnScratch15 ; original $85cb
Pn85cd: jsr Pn8df6 ; original $85cd
Pn85d0: jmp Pn8616 ; original $85d0
Pn85d3: dey ; original $85d3
Pn85d4: jne Pn85f1 ; original $85d4
Pn85d6: ldy PnScratch15 ; original $85d6
Pn85d8: lda PnScratch0e ; original $85d8
Pn85da: jne Pn85e9 ; original $85da
Pn85dc: lda PnActive+6,Y ; original $85dc
Pn85df: ora PnActive+11,Y ; original $85df
Pn85e2: jeq Pn85e7 ; original $85e2
Pn85e4: jmp Pn868b ; original $85e4
Pn85e7: inc PnScratch0e ; original $85e7
Pn85e9: ldy PnScratch15 ; original $85e9
Pn85eb: jsr Pn8e8b ; original $85eb
Pn85ee: jmp Pn8616 ; original $85ee
Pn85f1: dey ; original $85f1
Pn85f2: jne Pn860c ; original $85f2
Pn85f4: lda #$0b ; original $85f4
Pn85f6: jsr PnSoundEvent ; original $85f6
Pn85f9: ldy PnScratch15 ; original $85f9
Pn85fb: jsr Pn8db5 ; original $85fb
Pn85fe: ldy PnScratch15 ; original $85fe
Pn8600: lda #$01 ; original $8600
Pn8602: sta PnPunch,Y ; original $8602
Pn8605: lda #$40 ; original $8605
Pn8607: sta PnAngle,X ; original $8607
Pn860a: jne Pn8628 ; original $860a
Pn860c: lda #$01 ; original $860c
Pn860e: sta PnPalette,X ; original $860e
Pn8611: ldy PnScratch15 ; original $8611
Pn8613: jsr Pn8dea ; original $8613
Pn8616: lda PnNativeStage ; original $8616
Pn8618: cmp #$04 ; original $8618
Pn861a: jne Pn8628 ; original $861a
Pn861c: lda PnNativeStage60 ; original $861c
Pn861e: cmp #$03 ; original $861e
Pn8620: jcc Pn8628 ; original $8620
Pn8622: dec PnVX,X ; original $8622
Pn8625: dec PnVX,X ; original $8625
Pn8628: lda #$03 ; original $8628
Pn862a: sta PnType,X ; original $862a
Pn862d: ldy VvVariant ; original $862d
Pn862f: lda Pn92d9,Y ; original $862f
Pn8632: ldy #$00 ; original $8632
Pn8634: jsr Pnc977 ; original $8634
Pn8637: ldy VvVariant ; original $8637
Pn8639: lda Pn92dd,Y ; original $8639
Pn863c: jeq Pn8641 ; original $863c
Pn863e: sta PnFrame,X ; original $863e
Pn8641: jmp Pn8682 ; original $8641
Pn8644: ldy VvVariant ; original $8644
Pn8646: cpy #$02 ; original $8646
Pn8648: jeq Pn8662 ; original $8648
Pn864a: lda Pn92d5,Y ; original $864a
Pn864d: jne Pn8657 ; original $864d
Pn864f: lda PnVY,X ; original $864f
Pn8652: ora PnVYF,X ; original $8652
Pn8655: jne Pn865a ; original $8655
Pn8657: jsr Pnc98a ; original $8657
Pn865a: ldy PnScratch15 ; original $865a
Pn865c: jsr Pn8e0b ; original $865c
Pn865f: jmp Pn8682 ; original $865f
Pn8662: lda PnActive,X ; original $8662
Pn8665: and #$20 ; original $8665
Pn8667: jeq Pn867f ; original $8667
Pn8669: jsr Pnc98a ; original $8669
Pn866c: lda PnAnimCursor,X ; original $866c
Pn866f: cmp #$03 ; original $866f
Pn8671: jne Pn8682 ; original $8671
Pn8673: ldy PnScratch15 ; original $8673
Pn8675: lda #$00 ; original $8675
Pn8677: sta PnPunch,Y ; original $8677
Pn867a: jsr Pn9bba ; original $867a
Pn867d: jeq Pn8682 ; original $867d
Pn867f: jsr Pn8ebe ; original $867f
Pn8682: lda #$0b ; original $8682
Pn8684: dec PnScratch0f ; original $8684
Pn8686: jeq Pn868b ; original $8686
Pn8688: jmp Pn85af ; original $8688
Pn868b: ldy PnScratch15 ; original $868b
Pn868d: lda VvGun ; original $868d
Pn868f: and #$40 ; original $868f
Pn8691: jeq Pn86df ; original $8691
Pn8693: lda #$02 ; original $8693
Pn8695: sta PnScratch0f ; original $8695
Pn8697: lda #$10 ; original $8697
Pn8699: ldy PnScratch15 ; original $8699
Pn869b: jsr Pn8f83 ; original $869b
Pn869e: lda PnActive,X ; original $869e
Pn86a1: and #$80 ; original $86a1
Pn86a3: jne Pn86d4 ; original $86a3
Pn86a5: lda VvFresh ; original $86a5
Pn86a7: and #$40 ; original $86a7
Pn86a9: jeq Pn86d9 ; original $86a9
Pn86ab: lda #$02 ; original $86ab
Pn86ad: sta PnType,X ; original $86ad
Pn86b0: jsr Pn8cf6 ; original $86b0
Pn86b3: ldy VvVariant ; original $86b3
Pn86b5: lda Pn92f6,Y ; original $86b5
Pn86b8: sta PnFrame,X ; original $86b8
Pn86bb: lda #$07 ; original $86bb
Pn86bd: jsr PnSoundEvent ; original $86bd
Pn86c0: lda PnScratch0f ; original $86c0
Pn86c2: cmp #$01 ; original $86c2
Pn86c4: jne Pn86ce ; original $86c4
Pn86c6: ldy VvVariant ; original $86c6
Pn86c8: lda Pn92fa,Y ; original $86c8
Pn86cb: sta PnFrame,X ; original $86cb
Pn86ce: lda #$00 ; original $86ce
Pn86d0: sta PnScratch0e ; original $86d0
Pn86d2: jeq Pn86d9 ; original $86d2
Pn86d4: ldy PnScratch15 ; original $86d4
Pn86d6: jsr Pn8d65 ; original $86d6
Pn86d9: lda #$15 ; original $86d9
Pn86db: dec PnScratch0f ; original $86db
Pn86dd: jne Pn8699 ; original $86dd
Pn86df: ldy PnScratch15 ; original $86df
Pn86e1: lda VvGun ; original $86e1
Pn86e3: and #$80 ; original $86e3
Pn86e5: jne Pn86ea ; original $86e5
Pn86e7: jmp Pn88cd ; original $86e7
Pn86ea: ldy VvVariant ; original $86ea
Pn86ec: jne Pn86f1 ; original $86ec
Pn86ee: jmp Pn878f ; original $86ee
Pn86f1: lda VvFresh ; original $86f1
Pn86f3: sta PnScratch0e ; original $86f3
Pn86f5: lda Pn8787,Y ; original $86f5
Pn86f8: sta PnScratch0f ; original $86f8
Pn86fa: ldy PnScratch0f ; original $86fa
Pn86fc: lda Pn8784,Y ; original $86fc
Pn86ff: ldy PnScratch15 ; original $86ff
Pn8701: jsr Pn8f83 ; original $8701
Pn8704: lda PnActive,X ; original $8704
Pn8707: and #$80 ; original $8707
Pn8709: jne Pn8742 ; original $8709
Pn870b: lda PnScratch0e ; original $870b
Pn870d: and #$40 ; original $870d
Pn870f: jeq Pn877b ; original $870f
Pn8711: jsr Pn8cca ; original $8711
Pn8714: ldy VvVariant ; original $8714
Pn8716: lda Pn9345,Y ; original $8716
Pn8719: sta PnType,X ; original $8719
Pn871c: lda Pn878b,Y ; original $871c
Pn871f: sta PnFrame,X ; original $871f
Pn8722: lda VvVariant ; original $8722
Pn8724: cmp #$03 ; original $8724
Pn8726: jeq Pn8733 ; original $8726
Pn8728: cmp #$01 ; original $8728
Pn872a: jne Pn8737 ; original $872a
Pn872c: lda #$1e ; original $872c
Pn872e: ldy #$00 ; original $872e
Pn8730: jsr Pnc977 ; original $8730
Pn8733: lda #$00 ; original $8733
Pn8735: sta PnScratch0e ; original $8735
Pn8737: ldy VvVariant ; original $8737
Pn8739: lda Pn9336,Y ; original $8739
Pn873c: jsr PnSoundEvent ; original $873c
Pn873f: jmp Pn877b ; original $873f
Pn8742: lda VvVariant ; original $8742
Pn8744: cmp #$01 ; original $8744
Pn8746: jeq Pn8765 ; original $8746
Pn8748: lda PnActive,X ; original $8748
Pn874b: and #$10 ; original $874b
Pn874d: jeq Pn8776 ; original $874d
Pn874f: lda #$05 ; original $874f
Pn8751: sta PnType,X ; original $8751
Pn8754: jsr Pnc98a ; original $8754
Pn8757: ldy PnScratch15 ; original $8757
Pn8759: lda PnAnimCursor,X ; original $8759
Pn875c: cmp #$04 ; original $875c
Pn875e: jcc Pn877b ; original $875e
Pn8760: jsr Pn9bba ; original $8760
Pn8763: jeq Pn877b ; original $8763
Pn8765: lda PnAnimation,X ; original $8765
Pn8768: cmp #$1e ; original $8768
Pn876a: jeq Pn8773 ; original $876a
Pn876c: lda #$1e ; original $876c
Pn876e: ldy #$00 ; original $876e
Pn8770: jsr Pnc977 ; original $8770
Pn8773: jsr Pnc98a ; original $8773
Pn8776: ldy PnScratch15 ; original $8776
Pn8778: jsr Pn8d4d ; original $8778
Pn877b: dec PnScratch0f ; original $877b
Pn877d: jeq Pn8782 ; original $877d
Pn877f: jmp Pn86fa ; original $877f
Pn8782: jmp Pn88cd ; original $8782
Pn878f: lda VvFresh ; original $878f
Pn8791: sta PnScratch0d ; original $8791
Pn8793: lda VvHeld ; original $8793
Pn8795: sta PnScratch0e ; original $8795
Pn8797: lda #$02 ; original $8797
Pn8799: sta PnScratch0f ; original $8799
Pn879b: sta PnScratch0c ; original $879b
Pn879d: lda #$10 ; original $879d
Pn879f: ldy PnScratch15 ; original $879f
Pn87a1: jsr Pn8f83 ; original $87a1
Pn87a4: lda PnActive,X ; original $87a4
Pn87a7: and #$80 ; original $87a7
Pn87a9: jne Pn8809 ; original $87a9
Pn87ab: lda PnScratch0d ; original $87ab
Pn87ad: ora PnScratch0e ; original $87ad
Pn87af: and #$40 ; original $87af
Pn87b1: jne Pn87b6 ; original $87b1
Pn87b3: jmp Pn88bb ; original $87b3
Pn87b6: lda PnScratch0f ; original $87b6
Pn87b8: cmp PnScratch0c ; original $87b8
Pn87ba: jne Pn87b3 ; original $87ba
Pn87bc: cmp #$01 ; original $87bc
Pn87be: jne Pn87c6 ; original $87be
Pn87c0: lda PnScratch0d ; original $87c0
Pn87c2: and #$40 ; original $87c2
Pn87c4: jeq Pn87b3 ; original $87c4
Pn87c6: lda #$09 ; original $87c6
Pn87c8: jsr PnSoundEvent ; original $87c8
Pn87cb: ldy PnScratch15 ; original $87cb
Pn87cd: jsr Pn8c34 ; original $87cd
Pn87d0: lda PnScratch0d ; original $87d0
Pn87d2: and #$40 ; original $87d2
Pn87d4: jeq Pn87de ; original $87d4
Pn87d6: lda PnActive,X ; original $87d6
Pn87d9: ora #$20 ; original $87d9
Pn87db: sta PnActive,X ; original $87db
Pn87de: lda #$00 ; original $87de
Pn87e0: sta PnScratch0d ; original $87e0
Pn87e2: sta PnScratch0e ; original $87e2
Pn87e4: lda PnX,X ; original $87e4
Pn87e7: clc ; original $87e7
Pn87e8: adc #$04 ; original $87e8
Pn87ea: sta PnX,X ; original $87ea
Pn87ed: jcs Pn87fe ; original $87ed
Pn87ef: lda #$00 ; original $87ef
Pn87f1: ldy #$00 ; original $87f1
Pn87f3: jsr Pnc977 ; original $87f3
Pn87f6: lda #$00 ; original $87f6
Pn87f8: sta PnPhase,X ; original $87f8
Pn87fb: jmp Pn88bb ; original $87fb
Pn87fe: lda #$00 ; original $87fe
Pn8800: sta PnActive,X ; original $8800
Pn8803: sta PnFrame,X ; original $8803
Pn8806: jmp Pn88bb ; original $8806
Pn8809: lda PnActive,X ; original $8809
Pn880c: and #$10 ; original $880c
Pn880e: jeq Pn8820 ; original $880e
Pn8810: lda PnPhase,X ; original $8810
Pn8813: jeq Pn881a ; original $8813
Pn8815: dec PnPhase,X ; original $8815
Pn8818: jne Pn8820 ; original $8818
Pn881a: jsr Pn9bba ; original $881a
Pn881d: jmp Pn88bb ; original $881d
Pn8820: lda #$04 ; original $8820
Pn8822: ldy PnPhase,X ; original $8822
Pn8825: cpy #$09 ; original $8825
Pn8827: jcc Pn882b ; original $8827
Pn8829: lda #$0c ; original $8829
Pn882b: sta PnType,X ; original $882b
Pn882e: lda PnPhase,X ; original $882e
Pn8831: cmp #$06 ; original $8831
Pn8833: jcs Pn8844 ; original $8833
Pn8835: lda PnActive,X ; original $8835
Pn8838: and #$20 ; original $8838
Pn883a: jeq Pn8844 ; original $883a
Pn883c: lda PnActive,X ; original $883c
Pn883f: ora #$40 ; original $883f
Pn8841: sta PnActive,X ; original $8841
Pn8844: ldy PnScratch15 ; original $8844
Pn8846: lda PnPhase,X ; original $8846
Pn8849: lsr a ; original $8849
Pn884a: tay ; original $884a
Pn884b: cmp #$04 ; original $884b
Pn884d: jcc Pn8856 ; original $884d
Pn884f: lda PnActive,X ; original $884f
Pn8852: and #$40 ; original $8852
Pn8854: jne Pn88ae ; original $8854
Pn8856: lda Pn9222,Y ; original $8856
Pn8859: cmp PnFrame,X ; original $8859
Pn885c: jeq Pn888e ; original $885c
Pn885e: sta PnFrame,X ; original $885e
Pn8861: lda PnActive,X ; original $8861
Pn8864: and #$10 ; original $8864
Pn8866: jeq Pn8880 ; original $8866
Pn8868: lda PnX,X ; original $8868
Pn886b: clc ; original $886b
Pn886c: adc #$06 ; original $886c
Pn886e: jcs Pn8876 ; original $886e
Pn8870: sta PnX,X ; original $8870
Pn8873: jmp Pn888e ; original $8873
Pn8876: lda PnActive,X ; original $8876
Pn8879: ora #$10 ; original $8879
Pn887b: sta PnActive,X ; original $887b
Pn887e: jne Pn888e ; original $887e
Pn8880: lda Pn922c,Y ; original $8880
Pn8883: ldy PnScratch15 ; original $8883
Pn8885: clc ; original $8885
Pn8886: adc PnX,Y ; original $8886
Pn8889: jcs Pn8876 ; original $8889
Pn888b: sta PnX,X ; original $888b
Pn888e: lda PnPhase,X ; original $888e
Pn8891: cmp #$12 ; original $8891
Pn8893: jcs Pn88ae ; original $8893
Pn8895: ldy PnScratch15 ; original $8895
Pn8897: lda PnY,Y ; original $8897
Pn889a: sta PnY,X ; original $889a
Pn889d: jsr Pn8c99 ; original $889d
Pn88a0: lda PnActive,X ; original $88a0
Pn88a3: and #$10 ; original $88a3
Pn88a5: jne Pn88bb ; original $88a5
Pn88a7: ldy PnScratch15 ; original $88a7
Pn88a9: inc PnPhase,X ; original $88a9
Pn88ac: jne Pn88bb ; original $88ac
Pn88ae: ldy PnScratch15 ; original $88ae
Pn88b0: jsr Pn8c49 ; original $88b0
Pn88b3: ldy PnScratch15 ; original $88b3
Pn88b5: lda PnY,Y ; original $88b5
Pn88b8: sta PnY,X ; original $88b8
Pn88bb: lda PnActive,X ; original $88bb
Pn88be: and #$60 ; original $88be
Pn88c0: jeq Pn88c4 ; original $88c0
Pn88c2: dec PnScratch0c ; original $88c2
Pn88c4: lda #$15 ; original $88c4
Pn88c6: dec PnScratch0f ; original $88c6
Pn88c8: jeq Pn88cd ; original $88c8
Pn88ca: jmp Pn879f ; original $88ca
Pn88cd: ldy PnScratch15 ; original $88cd
Pn88cf: jeq Pn88d4 ; original $88cf
Pn88d1: jmp Pn8b0b ; original $88d1
Pn88d4: lda VvGun ; original $88d4
Pn88d6: and #$20 ; original $88d6
Pn88d8: jne Pn88dd ; original $88d8
Pn88da: jmp Pn8b0b ; original $88da
Pn88dd: lda #$02 ; original $88dd
Pn88df: sta PnScratch0f ; original $88df
Pn88e1: ldx #$05 ; original $88e1
Pn88e3: lda VvVariant ; original $88e3
Pn88e5: asl a ; original $88e5
Pn88e6: sta PnScratch18 ; original $88e6
Pn88e8: lda PnAux ; original $88e8
Pn88eb: and #$08 ; original $88eb
Pn88ed: jeq Pn88f1 ; original $88ed
Pn88ef: inc PnScratch18 ; original $88ef
Pn88f1: ldy PnScratch18 ; original $88f1
Pn88f3: lda Pn9349,Y ; original $88f3
Pn88f6: sta PnType,X ; original $88f6
Pn88f9: lda PnContact,X ; original $88f9
Pn88fc: jeq Pn8910 ; original $88fc
Pn88fe: and #$7f ; original $88fe
Pn8900: cmp #$0b ; original $8900
Pn8902: jcs Pn8908 ; original $8902
Pn8904: cmp #$04 ; original $8904
Pn8906: jcs Pn8910 ; original $8906
Pn8908: lda PnAux ; original $8908
Pn890b: jeq Pn8910 ; original $890b
Pn890d: dec PnAux ; original $890d
Pn8910: lda VvVariant ; original $8910
Pn8912: jne Pn8917 ; original $8912
Pn8914: jmp Pn8a36 ; original $8914
Pn8917: cmp #$01 ; original $8917
Pn8919: jeq Pn8999 ; original $8919
Pn891b: lda PnActive,X ; original $891b
Pn891e: and #$c0 ; original $891e
Pn8920: jne Pn8935 ; original $8920
Pn8922: jsr Pn8db5 ; original $8922
Pn8925: lda #$0f ; original $8925
Pn8927: sta PnAux ; original $8927
Pn892a: lda #$00 ; original $892a
Pn892c: sta PnPhase,X ; original $892c
Pn892f: sta PnAnimation,X ; original $892f
Pn8932: jmp Pn8a08 ; original $8932
Pn8935: lda VvVariant ; original $8935
Pn8937: sec ; original $8937
Pn8938: sbc #$02 ; original $8938
Pn893a: jne Pn894d ; original $893a
Pn893c: pha ; original $893c
Pn893d: lda VvClock ; original $893d
Pn893f: and #$0c ; original $893f
Pn8941: lsr a ; original $8941
Pn8942: lsr a ; original $8942
Pn8943: cmp #$03 ; original $8943
Pn8945: jne Pn8949 ; original $8945
Pn8947: lda #$00 ; original $8947
Pn8949: sta PnPalette,X ; original $8949
Pn894c: pla ; original $894c
Pn894d: asl a ; original $894d
Pn894e: asl a ; original $894e
Pn894f: sta M0 ; original $894f
Pn8951: lda PnAux ; original $8951
Pn8954: lsr a ; original $8954
Pn8955: lsr a ; original $8955
Pn8956: clc ; original $8956
Pn8957: adc M0 ; original $8957
Pn8959: tay ; original $8959
Pn895a: lda Pn92ea,Y ; original $895a
Pn895d: ldy VvVariant ; original $895d
Pn895f: cpy #$02 ; original $895f
Pn8961: jne Pn8969 ; original $8961
Pn8963: sta PnFrame,X ; original $8963
Pn8966: jmp Pn8979 ; original $8966
Pn8969: sta PnPhase,X ; original $8969
Pn896c: cmp PnAnimation,X ; original $896c
Pn896f: jeq Pn8976 ; original $896f
Pn8971: ldy #$00 ; original $8971
Pn8973: jsr Pnc977 ; original $8973
Pn8976: jsr Pnc98a ; original $8976
Pn8979: lda PnY ; original $8979
Pn897c: sta PnY,X ; original $897c
Pn897f: lda PnYF ; original $897f
Pn8982: sta PnYF,X ; original $8982
Pn8985: lda PnX ; original $8985
Pn8988: sta PnX,X ; original $8988
Pn898b: lda PnXF ; original $898b
Pn898e: sta PnXF,X ; original $898e
Pn8991: lda PnAux ; original $8991
Pn8994: jne Pn89b3 ; original $8994
Pn8996: jmp Pn8a8b ; original $8996
Pn8999: lda PnActive,X ; original $8999
Pn899c: and #$c0 ; original $899c
Pn899e: jne Pn89b6 ; original $899e
Pn89a0: jsr Pn8db5 ; original $89a0
Pn89a3: lda #$ff ; original $89a3
Pn89a5: sta PnX,X ; original $89a5
Pn89a8: lda PnY ; original $89a8
Pn89ab: sta PnY,X ; original $89ab
Pn89ae: lda #$0f ; original $89ae
Pn89b0: sta PnAux ; original $89b0
Pn89b3: jmp Pn8a08 ; original $89b3
Pn89b6: lda PnAux ; original $89b6
Pn89b9: jeq Pn89c4 ; original $89b9
Pn89bb: lsr a ; original $89bb
Pn89bc: lsr a ; original $89bc
Pn89bd: tay ; original $89bd
Pn89be: lda Pn92e6,Y ; original $89be
Pn89c1: sta PnFrame,X ; original $89c1
Pn89c4: lda PnY ; original $89c4
Pn89c7: sta PnY,X ; original $89c7
Pn89ca: lda PnYF ; original $89ca
Pn89cd: sta PnYF,X ; original $89cd
Pn89d0: lda PnActive,X ; original $89d0
Pn89d3: and #$40 ; original $89d3
Pn89d5: jeq Pn8a0b ; original $89d5
Pn89d7: jsr Pn8b2f ; original $89d7
Pn89da: lda PnXF ; original $89da
Pn89dd: sta PnXF,X ; original $89dd
Pn89e0: lda PnActive,X ; original $89e0
Pn89e3: and #$20 ; original $89e3
Pn89e5: jeq Pn89f4 ; original $89e5
Pn89e7: jsr Pnc98a ; original $89e7
Pn89ea: lda PnAnimCursor,X ; original $89ea
Pn89ed: cmp #$02 ; original $89ed
Pn89ef: jne Pn8a08 ; original $89ef
Pn89f1: jmp Pn8a8b ; original $89f1
Pn89f4: lda PnAux ; original $89f4
Pn89f7: jne Pn8a08 ; original $89f7
Pn89f9: lda #$20 ; original $89f9
Pn89fb: ldy #$00 ; original $89fb
Pn89fd: jsr Pnc977 ; original $89fd
Pn8a00: lda PnActive,X ; original $8a00
Pn8a03: ora #$20 ; original $8a03
Pn8a05: sta PnActive,X ; original $8a05
Pn8a08: jmp Pn8b0b ; original $8a08
Pn8a0b: lda #$fd ; original $8a0b
Pn8a0d: sta PnVX,X ; original $8a0d
Pn8a10: sta PnVXF,X ; original $8a10
Pn8a13: jsr Pn9080 ; original $8a13
Pn8a16: lda PnX ; original $8a16
Pn8a19: clc ; original $8a19
Pn8a1a: adc #$10 ; original $8a1a
Pn8a1c: sec ; original $8a1c
Pn8a1d: sbc PnX,X ; original $8a1d
Pn8a20: jcs Pn8a27 ; original $8a20
Pn8a22: eor #$ff ; original $8a22
Pn8a24: clc ; original $8a24
Pn8a25: adc #$01 ; original $8a25
Pn8a27: cmp #$03 ; original $8a27
Pn8a29: jcs Pn8a33 ; original $8a29
Pn8a2b: lda #$40 ; original $8a2b
Pn8a2d: ora PnActive,X ; original $8a2d
Pn8a30: sta PnActive,X ; original $8a30
Pn8a33: jmp Pn8b0b ; original $8a33
Pn8a36: lda PnActive,X ; original $8a36
Pn8a39: and #$c0 ; original $8a39
Pn8a3b: jne Pn8a7f ; original $8a3b
Pn8a3d: lda #$ff ; original $8a3d
Pn8a3f: sta PnX,X ; original $8a3f
Pn8a42: lda #$40 ; original $8a42
Pn8a44: sta PnY,X ; original $8a44
Pn8a47: lda PnScratch0f ; original $8a47
Pn8a49: cmp #$01 ; original $8a49
Pn8a4b: jne Pn8a57 ; original $8a4b
Pn8a4d: lda #$80 ; original $8a4d
Pn8a4f: sta PnY,X ; original $8a4f
Pn8a52: lda #$0f ; original $8a52
Pn8a54: sta PnAux ; original $8a54
Pn8a57: lda #$01 ; original $8a57
Pn8a59: sta PnDrawFlags,X ; original $8a59
Pn8a5c: lda #$80 ; original $8a5c
Pn8a5e: sta PnActive,X ; original $8a5e
Pn8a61: lda #$01 ; original $8a61
Pn8a63: sta PnDrawFlags,X ; original $8a63
Pn8a66: lda #$00 ; original $8a66
Pn8a68: sta PnPhase,X ; original $8a68
Pn8a6b: lda #$03 ; original $8a6b
Pn8a6d: ldy PnScratch0f ; original $8a6d
Pn8a6f: dey ; original $8a6f
Pn8a70: jne Pn8a74 ; original $8a70
Pn8a72: lda #$04 ; original $8a72
Pn8a74: sta PnAux,X ; original $8a74
Pn8a77: ldy #$00 ; original $8a77
Pn8a79: jsr Pnc977 ; original $8a79
Pn8a7c: jmp Pn8b00 ; original $8a7c
Pn8a7f: lda PnAux ; original $8a7f
Pn8a82: jne Pn8a9d ; original $8a82
Pn8a84: ldx #$05 ; original $8a84
Pn8a86: jsr Pn9bba ; original $8a86
Pn8a89: ldx #$1a ; original $8a89
Pn8a8b: jsr Pn9bba ; original $8a8b
Pn8a8e: lda VvGun ; original $8a8e
Pn8a90: and #$df ; original $8a90
Pn8a92: sta VvGun ; original $8a92
Pn8a94: lda VvFlags ; original $8a94
Pn8a96: and #$bf ; original $8a96
Pn8a98: sta VvFlags ; original $8a98
Pn8a9a: jmp Pn8b0b ; original $8a9a
Pn8a9d: and #$0c ; original $8a9d
Pn8a9f: lsr a ; original $8a9f
Pn8aa0: clc ; original $8aa0
Pn8aa1: adc PnScratch0f ; original $8aa1
Pn8aa3: tay ; original $8aa3
Pn8aa4: dey ; original $8aa4
Pn8aa5: lda Pn92c1,Y ; original $8aa5
Pn8aa8: cmp PnAux,X ; original $8aa8
Pn8aab: jeq Pn8ab5 ; original $8aab
Pn8aad: sta PnAux,X ; original $8aad
Pn8ab0: ldy #$00 ; original $8ab0
Pn8ab2: jsr Pnc977 ; original $8ab2
Pn8ab5: lda PnActive,X ; original $8ab5
Pn8ab8: and #$40 ; original $8ab8
Pn8aba: jne Pn8adf ; original $8aba
Pn8abc: jsr Pnc98a ; original $8abc
Pn8abf: ldy PnScratch15 ; original $8abf
Pn8ac1: jsr Pn8f8a ; original $8ac1
Pn8ac4: jsr Pn8bbf ; original $8ac4
Pn8ac7: jsr Pn9080 ; original $8ac7
Pn8aca: lda M0 ; original $8aca
Pn8acc: jeq Pn8adc ; original $8acc
Pn8ace: inc PnX,X ; original $8ace
Pn8ad1: lda PnVX,X ; original $8ad1
Pn8ad4: jmi Pn8adc ; original $8ad4
Pn8ad6: dec PnX,X ; original $8ad6
Pn8ad9: dec PnX,X ; original $8ad9
Pn8adc: jmp Pn8b00 ; original $8adc
Pn8adf: jsr Pnc98a ; original $8adf
Pn8ae2: lda PnAux ; original $8ae2
Pn8ae5: lsr a ; original $8ae5
Pn8ae6: lsr a ; original $8ae6
Pn8ae7: tay ; original $8ae7
Pn8ae8: lda Pn92c9,Y ; original $8ae8
Pn8aeb: ldy PnScratch0f ; original $8aeb
Pn8aed: dey ; original $8aed
Pn8aee: jne Pn8af2 ; original $8aee
Pn8af0: eor #$ff ; original $8af0
Pn8af2: sta PnScratch08 ; original $8af2
Pn8af4: jsr Pn8b2f ; original $8af4
Pn8af7: lda PnY ; original $8af7
Pn8afa: sec ; original $8afa
Pn8afb: sbc PnScratch08 ; original $8afb
Pn8afd: sta PnY,X ; original $8afd
Pn8b00: ldx #$1a ; original $8b00
Pn8b02: ldy PnScratch15 ; original $8b02
Pn8b04: dec PnScratch0f ; original $8b04
Pn8b06: jeq Pn8b0b ; original $8b06
Pn8b08: jmp Pn88e3 ; original $8b08
Pn8b0b: ldy PnScratch15 ; original $8b0b
Pn8b0d: iny ; original $8b0d
Pn8b0e: dec PnScratch17 ; original $8b0e
Pn8b10: jeq Pn8b15 ; original $8b10
Pn8b12: jmp Pn84f0 ; original $8b12
Pn8b15: jsr PnBellSpecials ; original $8b15
Pn8b18: lda PnBellFlags ; original $8b18
Pn8b1a: and #$02 ; original $8b1a
Pn8b1c: jeq Pn8b2e ; original $8b1c
Pn8b1e: ldy #$1a ; original $8b1e
Pn8b20: ldx #$01 ; original $8b20
Pn8b22: lda #$00 ; original $8b22
Pn8b24: sta PnDrawFlags,X ; original $8b24
Pn8b27: sta PnFrame,X ; original $8b27
Pn8b2a: inx ; original $8b2a
Pn8b2b: dey ; original $8b2b
Pn8b2c: jne Pn8b24 ; original $8b2c
Pn8b2e: rts ; original $8b2e
Pn8b2f: lda PnDrawFlags,X ; original $8b2f
Pn8b32: and #$ef ; original $8b32
Pn8b34: sta PnDrawFlags,X ; original $8b34
Pn8b37: lda PnX ; original $8b37
Pn8b3a: clc ; original $8b3a
Pn8b3b: adc #$10 ; original $8b3b
Pn8b3d: sta PnX,X ; original $8b3d
Pn8b40: jcc Pn8b4a ; original $8b40
Pn8b42: lda PnDrawFlags,X ; original $8b42
Pn8b45: ora #$10 ; original $8b45
Pn8b47: sta PnDrawFlags,X ; original $8b47
Pn8b4a: rts ; original $8b4a
Pn8b4b: lda #$00 ; original $8b4b
Pn8b4d: sta PnVXF,X ; original $8b4d
Pn8b50: sta PnVX,X ; original $8b50
Pn8b53: sta PnVYF,X ; original $8b53
Pn8b56: sta PnVY,X ; original $8b56
Pn8b59: ldy VvSpeed ; original $8b59
Pn8b5b: lda PnNativeStage ; original $8b5b
Pn8b5d: cmp #$05 ; original $8b5d
Pn8b5f: jne Pn8b7c ; original $8b5f
Pn8b61: lda VvVariant ; original $8b61
Pn8b63: and #$01 ; original $8b63
Pn8b65: jne Pn8b7c ; original $8b65
Pn8b67: lda PnNativeStage60 ; original $8b67
Pn8b69: cmp #$11 ; original $8b69
Pn8b6b: jcs Pn8b7c ; original $8b6b
Pn8b6d: lda PnNativeStage63 ; original $8b6d
Pn8b6f: jne Pn8b77 ; original $8b6f
Pn8b71: lda PnNativeStage64 ; original $8b71
Pn8b73: cmp #$c0 ; original $8b73
Pn8b75: jcc Pn8b7c ; original $8b75
Pn8b77: dey ; original $8b77
Pn8b78: jpl Pn8b7c ; original $8b78
Pn8b7a: ldy #$00 ; original $8b7a
Pn8b7c: lda PnBellFlags ; original $8b7c
Pn8b7e: and #$02 ; original $8b7e
Pn8b80: jeq Pn8b89 ; original $8b80
Pn8b82: iny ; original $8b82
Pn8b83: cpy #$04 ; original $8b83
Pn8b85: jcc Pn8b89 ; original $8b85
Pn8b87: ldy #$04 ; original $8b87
Pn8b89: tya ; original $8b89
Pn8b8a: asl a ; original $8b8a
Pn8b8b: tay ; original $8b8b
Pn8b8c: lda Pn9163,Y ; original $8b8c
Pn8b8f: sta M0 ; original $8b8f
Pn8b91: lda Pn9164,Y ; original $8b91
Pn8b94: sta M1 ; original $8b94
Pn8b96: lda VvHeld ; original $8b96
Pn8b98: jeq Pn8bbe ; original $8b98
Pn8b9a: and #$0f ; original $8b9a
Pn8b9c: tay ; original $8b9c
Pn8b9d: lda Pn9153,Y ; original $8b9d
Pn8ba0: cmp #$ff ; original $8ba0
Pn8ba2: jeq Pn8bbe ; original $8ba2
Pn8ba4: asl a ; original $8ba4
Pn8ba5: asl a ; original $8ba5
Pn8ba6: tay ; original $8ba6
Pn8ba7: lda (M0),Y ; original $8ba7
Pn8ba9: sta PnVXF,X ; original $8ba9
Pn8bac: iny ; original $8bac
Pn8bad: lda (M0),Y ; original $8bad
Pn8baf: sta PnVX,X ; original $8baf
Pn8bb2: iny ; original $8bb2
Pn8bb3: lda (M0),Y ; original $8bb3
Pn8bb5: sta PnVYF,X ; original $8bb5
Pn8bb8: iny ; original $8bb8
Pn8bb9: lda (M0),Y ; original $8bb9
Pn8bbb: sta PnVY,X ; original $8bbb
Pn8bbe: rts ; original $8bbe
Pn8bbf: lda PnPhase,X ; original $8bbf
Pn8bc2: jne Pn8bfb ; original $8bc2
Pn8bc4: jsr Pn8fb2 ; original $8bc4
Pn8bc7: ldy #$00 ; original $8bc7
Pn8bc9: sec ; original $8bc9
Pn8bca: sbc PnAngle,X ; original $8bca
Pn8bcd: jeq Pn8bf3 ; original $8bcd
Pn8bcf: jcs Pn8bd4 ; original $8bcf
Pn8bd1: eor #$ff ; original $8bd1
Pn8bd3: iny ; original $8bd3
Pn8bd4: cmp #$80 ; original $8bd4
Pn8bd6: jcc Pn8bd9 ; original $8bd6
Pn8bd8: iny ; original $8bd8
Pn8bd9: tya ; original $8bd9
Pn8bda: and #$01 ; original $8bda
Pn8bdc: jeq Pn8bea ; original $8bdc
Pn8bde: lda PnAngle,X ; original $8bde
Pn8be1: sec ; original $8be1
Pn8be2: sbc #$04 ; original $8be2
Pn8be4: sta PnAngle,X ; original $8be4
Pn8be7: jmp Pn8bf3 ; original $8be7
Pn8bea: lda PnAngle,X ; original $8bea
Pn8bed: clc ; original $8bed
Pn8bee: adc #$04 ; original $8bee
Pn8bf0: sta PnAngle,X ; original $8bf0
Pn8bf3: jsr Pn900a ; original $8bf3
Pn8bf6: lda #$01 ; original $8bf6
Pn8bf8: sta PnPhase,X ; original $8bf8
Pn8bfb: dec PnPhase,X ; original $8bfb
Pn8bfe: rts ; original $8bfe
Pn8bff: ldx PnNativeObjectStart ; original $8bff
Pn8c01: jne Pn8c05 ; original $8c01
Pn8c03: ldx #$01 ; original $8c03
Pn8c05: lda #$00 ; original $8c05
Pn8c07: sta PnActive,X ; original $8c07
Pn8c0a: sta PnDrawFlags,X ; original $8c0a
Pn8c0d: sta PnFrame,X ; original $8c0d
Pn8c10: sta PnPunch,X ; original $8c10
Pn8c13: inx ; original $8c13
Pn8c14: cpx #$1c ; original $8c14
Pn8c16: jne Pn8c07 ; original $8c16
Pn8c18: rts ; original $8c18
Pn8c19: ldy VvVariant ; original $8c19
Pn8c1b: lda PnPunch ; original $8c1b
Pn8c1e: jeq Pn8c22 ; original $8c1e
Pn8c20: ldy #$04 ; original $8c20
Pn8c22: lda PnPhase ; original $8c22
Pn8c25: and #$f0 ; original $8c25
Pn8c27: clc ; original $8c27
Pn8c28: adc #$30 ; original $8c28
Pn8c2a: lsr a ; original $8c2a
Pn8c2b: lsr a ; original $8c2b
Pn8c2c: lsr a ; original $8c2c
Pn8c2d: lsr a ; original $8c2d
Pn8c2e: clc ; original $8c2e
Pn8c2f: adc Pn929e,Y ; original $8c2f
Pn8c32: tay ; original $8c32
Pn8c33: rts ; original $8c33
Pn8c34: lda #$04 ; original $8c34
Pn8c36: sta PnVX,X ; original $8c36
Pn8c39: lda #$80 ; original $8c39
Pn8c3b: sta PnVXF,X ; original $8c3b
Pn8c3e: lda #$00 ; original $8c3e
Pn8c40: sta PnVY,X ; original $8c40
Pn8c43: sta PnVYF,X ; original $8c43
Pn8c46: jmp Pn8db8 ; original $8c46
Pn8c49: jsr Pn8cb0 ; original $8c49
Pn8c4c: jsr Pn9130 ; original $8c4c
Pn8c4f: cmp #$00 ; original $8c4f
Pn8c51: jeq Pn8c63 ; original $8c51
Pn8c53: cmp #$02 ; original $8c53
Pn8c55: jne Pn8c5a ; original $8c55
Pn8c57: jsr PnTerrainImpact ; original $8c57
Pn8c5a: lda PnActive,X ; original $8c5a
Pn8c5d: ora #$10 ; original $8c5d
Pn8c5f: sta PnActive,X ; original $8c5f
Pn8c62: rts ; original $8c62
Pn8c63: lda PnContact,X ; original $8c63
Pn8c66: jeq Pn8c7c ; original $8c66
Pn8c68: and #$7f ; original $8c68
Pn8c6a: cmp #$06 ; original $8c6a
Pn8c6c: jcc Pn8c72 ; original $8c6c
Pn8c6e: cmp #$0b ; original $8c6e
Pn8c70: jcc Pn8c5a ; original $8c70
Pn8c72: ldy PnEnemyIndex,X ; original $8c72
Pn8c75: lda PnEnemyType,Y ; original $8c75
Pn8c78: cmp #$08 ; original $8c78
Pn8c7a: jcs Pn8c5a ; original $8c7a
Pn8c7c: lda PnActive,X ; original $8c7c
Pn8c7f: and #$10 ; original $8c7f
Pn8c81: jne Pn8c5a ; original $8c81
Pn8c83: jsr Pn9080 ; original $8c83
Pn8c86: lda M0 ; original $8c86
Pn8c88: jne Pn8c5a ; original $8c88
Pn8c8a: lda PnPhase,X ; original $8c8a
Pn8c8d: lsr a ; original $8c8d
Pn8c8e: tay ; original $8c8e
Pn8c8f: lda Pn923a,Y ; original $8c8f
Pn8c92: clc ; original $8c92
Pn8c93: adc PnX,X ; original $8c93
Pn8c96: jcs Pn8c5a ; original $8c96
Pn8c98: rts ; original $8c98
Pn8c99: jsr Pn8cb0 ; original $8c99
Pn8c9c: jsr Pn9130 ; original $8c9c
Pn8c9f: cmp #$00 ; original $8c9f
Pn8ca1: jne Pn8ca6 ; original $8ca1
Pn8ca3: jmp Pn8c8a ; original $8ca3
Pn8ca6: cmp #$02 ; original $8ca6
Pn8ca8: jne Pn8c5a ; original $8ca8
Pn8caa: jsr PnTerrainImpact ; original $8caa
Pn8cad: jmp Pn8c5a ; original $8cad
Pn8cb0: lda PnPhase,X ; original $8cb0
Pn8cb3: lsr a ; original $8cb3
Pn8cb4: tay ; original $8cb4
Pn8cb5: lda Pn923a,Y ; original $8cb5
Pn8cb8: clc ; original $8cb8
Pn8cb9: adc PnX,X ; original $8cb9
Pn8cbc: sta M0 ; original $8cbc
Pn8cbe: lda PnY,X ; original $8cbe
Pn8cc1: sta R0 ; original $8cc1
Pn8cc3: lda #$00 ; original $8cc3
Pn8cc5: sta R1 ; original $8cc5
Pn8cc7: sta M1 ; original $8cc7
Pn8cc9: rts ; original $8cc9
Pn8cca: lda VvVariant ; original $8cca
Pn8ccc: cmp #$02 ; original $8ccc
Pn8cce: jne Pn8d26 ; original $8cce
Pn8cd0: lda #$3e ; original $8cd0
Pn8cd2: sta PnVXF,X ; original $8cd2
Pn8cd5: sta PnVYF,X ; original $8cd5
Pn8cd8: lda #$04 ; original $8cd8
Pn8cda: sta PnVY,X ; original $8cda
Pn8cdd: sta PnVX,X ; original $8cdd
Pn8ce0: lda PnScratch0f ; original $8ce0
Pn8ce2: cmp #$02 ; original $8ce2
Pn8ce4: jeq Pn8d38 ; original $8ce4
Pn8ce6: cmp #$01 ; original $8ce6
Pn8ce8: jne Pn8d26 ; original $8ce8
Pn8cea: lda #$c2 ; original $8cea
Pn8cec: sta PnVYF,X ; original $8cec
Pn8cef: lda #$fb ; original $8cef
Pn8cf1: sta PnVY,X ; original $8cf1
Pn8cf4: jne Pn8d38 ; original $8cf4
Pn8cf6: lda PnScratch0f ; original $8cf6
Pn8cf8: cmp #$01 ; original $8cf8
Pn8cfa: jne Pn8d26 ; original $8cfa
Pn8cfc: lda #$3e ; original $8cfc
Pn8cfe: sta PnVXF,X ; original $8cfe
Pn8d01: lda #$04 ; original $8d01
Pn8d03: sta PnVX,X ; original $8d03
Pn8d06: lda #$c2 ; original $8d06
Pn8d08: sta PnVYF,X ; original $8d08
Pn8d0b: lda #$fb ; original $8d0b
Pn8d0d: sta PnVY,X ; original $8d0d
Pn8d10: lda VvVariant ; original $8d10
Pn8d12: and #$03 ; original $8d12
Pn8d14: jeq Pn8d38 ; original $8d14
Pn8d16: cmp #$03 ; original $8d16
Pn8d18: jeq Pn8d38 ; original $8d18
Pn8d1a: lda #$00 ; original $8d1a
Pn8d1c: sta PnVXF,X ; original $8d1c
Pn8d1f: lda #$f9 ; original $8d1f
Pn8d21: sta PnVX,X ; original $8d21
Pn8d24: jne Pn8d30 ; original $8d24
Pn8d26: lda #$06 ; original $8d26
Pn8d28: sta PnVX,X ; original $8d28
Pn8d2b: lda #$00 ; original $8d2b
Pn8d2d: sta PnVXF,X ; original $8d2d
Pn8d30: lda #$00 ; original $8d30
Pn8d32: sta PnVY,X ; original $8d32
Pn8d35: sta PnVYF,X ; original $8d35
Pn8d38: jmp Pn8db8 ; original $8d38
Pn8d3b: lda PnActive,X ; original $8d3b
Pn8d3e: ora #$10 ; original $8d3e
Pn8d40: sta PnActive,X ; original $8d40
Pn8d43: lda #$49 ; original $8d43
Pn8d45: ldy #$00 ; original $8d45
Pn8d47: jsr Pnc977 ; original $8d47
Pn8d4a: jmp Pn8ddb ; original $8d4a
Pn8d4d: jsr Pn9143 ; original $8d4d
Pn8d50: jeq Pn8d5b ; original $8d50
Pn8d52: lda VvVariant ; original $8d52
Pn8d54: cmp #$03 ; original $8d54
Pn8d56: jeq Pn8d3b ; original $8d56
Pn8d58: jmp Pn9bba ; original $8d58
Pn8d5b: ldy VvVariant ; original $8d5b
Pn8d5d: lda Pn8db1,Y ; original $8d5d
Pn8d60: sta PnScratch07 ; original $8d60
Pn8d62: jmp Pn8d7f ; original $8d62
Pn8d65: jsr Pn9143 ; original $8d65
Pn8d68: jeq Pn8d6d ; original $8d68
Pn8d6a: jmp Pn9bba ; original $8d6a
Pn8d6d: lda #$00 ; original $8d6d
Pn8d6f: sta PnScratch07 ; original $8d6f
Pn8d71: jeq Pn8d7f ; original $8d71
Pn8d73: jsr Pn9143 ; original $8d73
Pn8d76: jeq Pn8d7b ; original $8d76
Pn8d78: jmp Pn9bba ; original $8d78
Pn8d7b: lda #$00 ; original $8d7b
Pn8d7d: sta PnScratch07 ; original $8d7d
Pn8d7f: lda PnX,X ; original $8d7f
Pn8d82: sta M0 ; original $8d82
Pn8d84: lda PnY,X ; original $8d84
Pn8d87: sta R0 ; original $8d87
Pn8d89: lda #$00 ; original $8d89
Pn8d8b: sta R1 ; original $8d8b
Pn8d8d: sta M1 ; original $8d8d
Pn8d8f: jsr Pn9130 ; original $8d8f
Pn8d92: cmp #$00 ; original $8d92
Pn8d94: jeq Pn8da7 ; original $8d94
Pn8d96: cmp #$02 ; original $8d96
Pn8d98: jne Pn8d9d ; original $8d98
Pn8d9a: jsr PnTerrainImpact ; original $8d9a
Pn8d9d: lda PnScratch07 ; original $8d9d
Pn8d9f: jne Pn8da4 ; original $8d9f
Pn8da1: jmp Pn9bba ; original $8da1
Pn8da4: jsr Pn8d3b ; original $8da4
Pn8da7: jsr Pn9080 ; original $8da7
Pn8daa: lda M0 ; original $8daa
Pn8dac: jeq Pn8dda ; original $8dac
Pn8dae: jmp Pn9bba ; original $8dae
Pn8db5: jsr Pn8ddb ; original $8db5
Pn8db8: lda PnX,Y ; original $8db8
Pn8dbb: sta PnX,X ; original $8dbb
Pn8dbe: lda PnXF,Y ; original $8dbe
Pn8dc1: sta PnXF,X ; original $8dc1
Pn8dc4: lda PnY,Y ; original $8dc4
Pn8dc7: sta PnY,X ; original $8dc7
Pn8dca: lda PnYF,Y ; original $8dca
Pn8dcd: sta PnYF,X ; original $8dcd
Pn8dd0: lda #$80 ; original $8dd0
Pn8dd2: sta PnActive,X ; original $8dd2
Pn8dd5: lda #$01 ; original $8dd5
Pn8dd7: sta PnDrawFlags,X ; original $8dd7
Pn8dda: rts ; original $8dda
Pn8ddb: lda #$00 ; original $8ddb
Pn8ddd: sta PnVX,X ; original $8ddd
Pn8de0: sta PnVXF,X ; original $8de0
Pn8de3: sta PnVY,X ; original $8de3
Pn8de6: sta PnVYF,X ; original $8de6
Pn8de9: rts ; original $8de9
Pn8dea: lda #$ff ; original $8dea
Pn8dec: sta PnVX,X ; original $8dec
Pn8def: lda #$e0 ; original $8def
Pn8df1: sta PnVXF,X ; original $8df1
Pn8df4: jne Pn8dfe ; original $8df4
Pn8df6: lda #$01 ; original $8df6
Pn8df8: sta PnVX,X ; original $8df8
Pn8dfb: sta PnVXF,X ; original $8dfb
Pn8dfe: lda #$02 ; original $8dfe
Pn8e00: sta PnVY,X ; original $8e00
Pn8e03: lda #$20 ; original $8e03
Pn8e05: sta PnVYF,X ; original $8e05
Pn8e08: jmp Pn8db8 ; original $8e08
Pn8e0b: jsr Pn9143 ; original $8e0b
Pn8e0e: jeq Pn8e19 ; original $8e0e
Pn8e10: lda VvVariant ; original $8e10
Pn8e12: cmp #$03 ; original $8e12
Pn8e14: jeq Pn8e19 ; original $8e14
Pn8e16: jmp Pn9bba ; original $8e16
Pn8e19: lda PnX,X ; original $8e19
Pn8e1c: sta M0 ; original $8e1c
Pn8e1e: lda PnY,X ; original $8e1e
Pn8e21: sta R0 ; original $8e21
Pn8e23: lda #$00 ; original $8e23
Pn8e25: sta R1 ; original $8e25
Pn8e27: sta M1 ; original $8e27
Pn8e29: ldy VvVariant ; original $8e29
Pn8e2b: cpy #$01 ; original $8e2b
Pn8e2d: jeq Pn8e99 ; original $8e2d
Pn8e2f: lda VvClock ; original $8e2f
Pn8e31: and #$01 ; original $8e31
Pn8e33: jeq Pn8e4c ; original $8e33
Pn8e35: lda M0 ; original $8e35
Pn8e37: clc ; original $8e37
Pn8e38: adc #$04 ; original $8e38
Pn8e3a: sta M0 ; original $8e3a
Pn8e3c: lda M1 ; original $8e3c
Pn8e3e: adc #$00 ; original $8e3e
Pn8e40: sta M1 ; original $8e40
Pn8e42: jsr PnTerrainQuery ; original $8e42
Pn8e45: cmp #$00 ; original $8e45
Pn8e47: jeq Pn8e80 ; original $8e47
Pn8e49: jmp Pn9bba ; original $8e49
Pn8e4c: lda #$02 ; original $8e4c
Pn8e4e: sta PnVY,X ; original $8e4e
Pn8e51: lda #$20 ; original $8e51
Pn8e53: sta PnVYF,X ; original $8e53
Pn8e56: lda R0 ; original $8e56
Pn8e58: clc ; original $8e58
Pn8e59: adc #$04 ; original $8e59
Pn8e5b: sta R0 ; original $8e5b
Pn8e5d: lda R1 ; original $8e5d
Pn8e5f: adc #$00 ; original $8e5f
Pn8e61: sta R1 ; original $8e61
Pn8e63: jsr PnTerrainQuery ; original $8e63
Pn8e66: cmp #$00 ; original $8e66
Pn8e68: jeq Pn8e80 ; original $8e68
Pn8e6a: dec PnY,X ; original $8e6a
Pn8e6d: dec PnY,X ; original $8e6d
Pn8e70: lda #$00 ; original $8e70
Pn8e72: sta PnVY,X ; original $8e72
Pn8e75: sta PnVYF,X ; original $8e75
Pn8e78: lda #$02 ; original $8e78
Pn8e7a: sta PnVX,X ; original $8e7a
Pn8e7d: sta PnVXF,X ; original $8e7d
Pn8e80: jsr Pn9080 ; original $8e80
Pn8e83: lda M0 ; original $8e83
Pn8e85: jeq Pn8e8a ; original $8e85
Pn8e87: jmp Pn9bba ; original $8e87
Pn8e8a: rts ; original $8e8a
Pn8e8b: jsr Pn8ddb ; original $8e8b
Pn8e8e: lda #$01 ; original $8e8e
Pn8e90: sta PnVX,X ; original $8e90
Pn8e93: sta PnVXF,X ; original $8e93
Pn8e96: jmp Pn8db8 ; original $8e96
Pn8e99: jsr Pn9130 ; original $8e99
Pn8e9c: cmp #$00 ; original $8e9c
Pn8e9e: jeq Pn8ea3 ; original $8e9e
Pn8ea0: jmp Pn9bba ; original $8ea0
Pn8ea3: lda #$20 ; original $8ea3
Pn8ea5: ldy PnScratch0f ; original $8ea5
Pn8ea7: dey ; original $8ea7
Pn8ea8: dey ; original $8ea8
Pn8ea9: jeq Pn8ead ; original $8ea9
Pn8eab: lda #$e0 ; original $8eab
Pn8ead: clc ; original $8ead
Pn8eae: adc PnVYF,X ; original $8eae
Pn8eb1: sta PnVYF,X ; original $8eb1
Pn8eb4: tya ; original $8eb4
Pn8eb5: adc PnVY,X ; original $8eb5
Pn8eb8: sta PnVY,X ; original $8eb8
Pn8ebb: jmp Pn8e80 ; original $8ebb
Pn8ebe: jsr Pn9143 ; original $8ebe
Pn8ec1: jeq Pn8ed0 ; original $8ec1
Pn8ec3: ldy PnEnemyIndex,X ; original $8ec3
Pn8ec6: lda PnEnemyType,Y ; original $8ec6
Pn8ec9: cmp #$04 ; original $8ec9
Pn8ecb: jcc Pn8ed0 ; original $8ecb
Pn8ecd: jmp Pn8f6a ; original $8ecd
Pn8ed0: lda PnX,X ; original $8ed0
Pn8ed3: sta M0 ; original $8ed3
Pn8ed5: lda PnY,X ; original $8ed5
Pn8ed8: sta R0 ; original $8ed8
Pn8eda: lda #$00 ; original $8eda
Pn8edc: sta R1 ; original $8edc
Pn8ede: sta M1 ; original $8ede
Pn8ee0: jsr Pn9130 ; original $8ee0
Pn8ee3: cmp #$00 ; original $8ee3
Pn8ee5: jeq Pn8eea ; original $8ee5
Pn8ee7: jmp Pn8f6a ; original $8ee7
Pn8eea: lda PnActive,X ; original $8eea
Pn8eed: and #$40 ; original $8eed
Pn8eef: jeq Pn8f14 ; original $8eef
Pn8ef1: jsr Pn8bbf ; original $8ef1
Pn8ef4: asl PnVXF,X ; original $8ef4
Pn8ef7: rol PnVX,X ; original $8ef7
Pn8efa: asl PnVYF,X ; original $8efa
Pn8efd: rol PnVY,X ; original $8efd
Pn8f00: lda PnAngle,X ; original $8f00
Pn8f03: and #$e0 ; original $8f03
Pn8f05: clc ; original $8f05
Pn8f06: rol a ; original $8f06
Pn8f07: rol a ; original $8f07
Pn8f08: rol a ; original $8f08
Pn8f09: rol a ; original $8f09
Pn8f0a: tay ; original $8f0a
Pn8f0b: lda Pn931e,Y ; original $8f0b
Pn8f0e: sta PnFrame,X ; original $8f0e
Pn8f11: jmp Pn8f24 ; original $8f11
Pn8f14: lda #$04 ; original $8f14
Pn8f16: sta PnVX,X ; original $8f16
Pn8f19: sta PnVXF,X ; original $8f19
Pn8f1c: lda #$00 ; original $8f1c
Pn8f1e: sta PnVY,X ; original $8f1e
Pn8f21: sta PnVYF,X ; original $8f21
Pn8f24: jsr Pn9080 ; original $8f24
Pn8f27: lda M0 ; original $8f27
Pn8f29: jeq Pn8f38 ; original $8f29
Pn8f2b: lda PnActive,X ; original $8f2b
Pn8f2e: ora #$40 ; original $8f2e
Pn8f30: sta PnActive,X ; original $8f30
Pn8f33: lda #$c0 ; original $8f33
Pn8f35: sta PnAngle,X ; original $8f35
Pn8f38: lda PnActive,X ; original $8f38
Pn8f3b: and #$40 ; original $8f3b
Pn8f3d: jeq Pn8f5f ; original $8f3d
Pn8f3f: ldy PnScratch15 ; original $8f3f
Pn8f41: lda PnX,Y ; original $8f41
Pn8f44: sec ; original $8f44
Pn8f45: sbc PnX,X ; original $8f45
Pn8f48: jcs Pn8f4c ; original $8f48
Pn8f4a: eor #$ff ; original $8f4a
Pn8f4c: cmp #$08 ; original $8f4c
Pn8f4e: jcs Pn8f5f ; original $8f4e
Pn8f50: lda PnY,Y ; original $8f50
Pn8f53: sec ; original $8f53
Pn8f54: sbc PnY,X ; original $8f54
Pn8f57: jcs Pn8f5b ; original $8f57
Pn8f59: eor #$ff ; original $8f59
Pn8f5b: cmp #$08 ; original $8f5b
Pn8f5d: jcc Pn8f60 ; original $8f5d
Pn8f5f: rts ; original $8f5f
Pn8f60: ldy PnScratch15 ; original $8f60
Pn8f62: lda #$00 ; original $8f62
Pn8f64: sta PnPunch,Y ; original $8f64
Pn8f67: jmp Pn9bba ; original $8f67
Pn8f6a: lda PnActive,X ; original $8f6a
Pn8f6d: ora #$20 ; original $8f6d
Pn8f6f: sta PnActive,X ; original $8f6f
Pn8f72: ldy #$3a ; original $8f72
Pn8f74: lda PnAngle,X ; original $8f74
Pn8f77: and #$80 ; original $8f77
Pn8f79: jeq Pn8f7d ; original $8f79
Pn8f7b: ldy #$3b ; original $8f7b
Pn8f7d: tya ; original $8f7d
Pn8f7e: ldy #$00 ; original $8f7e
Pn8f80: jmp Pnc977 ; original $8f80
Pn8f83: sty PnScratch08 ; original $8f83
Pn8f85: clc ; original $8f85
Pn8f86: adc PnScratch08 ; original $8f86
Pn8f88: tax ; original $8f88
Pn8f89: rts ; original $8f89
Pn8f8a: lda PnX ; original $8f8a
Pn8f8d: clc ; original $8f8d
Pn8f8e: adc #$10 ; original $8f8e
Pn8f90: sec ; original $8f90
Pn8f91: sbc PnX,X ; original $8f91
Pn8f94: jcc Pn8fb1 ; original $8f94
Pn8f96: cmp #$08 ; original $8f96
Pn8f98: jcs Pn8fb1 ; original $8f98
Pn8f9a: lda PnY ; original $8f9a
Pn8f9d: sec ; original $8f9d
Pn8f9e: sbc PnY,X ; original $8f9e
Pn8fa1: jcs Pn8fa5 ; original $8fa1
Pn8fa3: eor #$ff ; original $8fa3
Pn8fa5: cmp #$08 ; original $8fa5
Pn8fa7: jcs Pn8fb1 ; original $8fa7
Pn8fa9: lda PnActive,X ; original $8fa9
Pn8fac: ora #$40 ; original $8fac
Pn8fae: sta PnActive,X ; original $8fae
Pn8fb1: rts ; original $8fb1
Pn8fb2: lda #$00 ; original $8fb2
Pn8fb4: sta M1 ; original $8fb4
Pn8fb6: ldy PnScratch15 ; original $8fb6
Pn8fb8: lda PnX,Y ; original $8fb8
Pn8fbb: sec ; original $8fbb
Pn8fbc: sbc PnX,X ; original $8fbc
Pn8fbf: tay ; original $8fbf
Pn8fc0: jcs Pn8fc9 ; original $8fc0
Pn8fc2: eor #$ff ; original $8fc2
Pn8fc4: tay ; original $8fc4
Pn8fc5: lda #$01 ; original $8fc5
Pn8fc7: sta M1 ; original $8fc7
Pn8fc9: tya ; original $8fc9
Pn8fca: lsr a ; original $8fca
Pn8fcb: lsr a ; original $8fcb
Pn8fcc: lsr a ; original $8fcc
Pn8fcd: lsr a ; original $8fcd
Pn8fce: sta M0 ; original $8fce
Pn8fd0: ldy PnScratch15 ; original $8fd0
Pn8fd2: lda PnY,Y ; original $8fd2
Pn8fd5: sec ; original $8fd5
Pn8fd6: sbc PnY,X ; original $8fd6
Pn8fd9: tay ; original $8fd9
Pn8fda: jcs Pn8fe5 ; original $8fda
Pn8fdc: eor #$ff ; original $8fdc
Pn8fde: tay ; original $8fde
Pn8fdf: lda M1 ; original $8fdf
Pn8fe1: ora #$02 ; original $8fe1
Pn8fe3: sta M1 ; original $8fe3
Pn8fe5: tya ; original $8fe5
Pn8fe6: and #$f0 ; original $8fe6
Pn8fe8: ora M0 ; original $8fe8
Pn8fea: tay ; original $8fea
Pn8feb: lda Pncbd6,Y ; original $8feb
Pn8fee: tay ; original $8fee
Pn8fef: lda M1 ; original $8fef
Pn8ff1: and #$03 ; original $8ff1
Pn8ff3: cmp #$01 ; original $8ff3
Pn8ff5: jeq Pn8fff ; original $8ff5
Pn8ff7: cmp #$02 ; original $8ff7
Pn8ff9: jeq Pn8fff ; original $8ff9
Pn8ffb: tya ; original $8ffb
Pn8ffc: eor #$3f ; original $8ffc
Pn8ffe: tay ; original $8ffe
Pn8fff: tya ; original $8fff
Pn9000: sta M0 ; original $9000
Pn9002: ldy M1 ; original $9002
Pn9004: lda Pn9236,Y ; original $9004
Pn9007: ora M0 ; original $9007
Pn9009: rts ; original $9009
Pn900a: lda PnAngle,X ; original $900a
Pn900d: tay ; original $900d
Pn900e: and #$c0 ; original $900e
Pn9010: jeq Pn901e ; original $9010
Pn9012: cmp #$80 ; original $9012
Pn9014: jeq Pn901e ; original $9014
Pn9016: lda PnAngle,X ; original $9016
Pn9019: and #$3f ; original $9019
Pn901b: eor #$3f ; original $901b
Pn901d: tay ; original $901d
Pn901e: tya ; original $901e
Pn901f: and #$38 ; original $901f
Pn9021: lsr a ; original $9021
Pn9022: tay ; original $9022
Pn9023: lda Pn92fe,Y ; original $9023
Pn9026: sta R1 ; original $9026
Pn9028: lda Pn92ff,Y ; original $9028
Pn902b: sta R0 ; original $902b
Pn902d: lda PnAngle,X ; original $902d
Pn9030: cmp #$80 ; original $9030
Pn9032: jcc Pn9045 ; original $9032
Pn9034: lda R0 ; original $9034
Pn9036: eor #$ff ; original $9036
Pn9038: clc ; original $9038
Pn9039: adc #$01 ; original $9039
Pn903b: sta R0 ; original $903b
Pn903d: lda R1 ; original $903d
Pn903f: eor #$ff ; original $903f
Pn9041: adc #$00 ; original $9041
Pn9043: sta R1 ; original $9043
Pn9045: lda R0 ; original $9045
Pn9047: sta PnVXF,X ; original $9047
Pn904a: lda R1 ; original $904a
Pn904c: sta PnVX,X ; original $904c
Pn904f: lda Pn9300,Y ; original $904f
Pn9052: sta R1 ; original $9052
Pn9054: lda Pn9301,Y ; original $9054
Pn9057: sta R0 ; original $9057
Pn9059: lda PnAngle,X ; original $9059
Pn905c: and #$c0 ; original $905c
Pn905e: jeq Pn9075 ; original $905e
Pn9060: cmp #$c0 ; original $9060
Pn9062: jeq Pn9075 ; original $9062
Pn9064: lda R0 ; original $9064
Pn9066: eor #$ff ; original $9066
Pn9068: clc ; original $9068
Pn9069: adc #$01 ; original $9069
Pn906b: sta R0 ; original $906b
Pn906d: lda R1 ; original $906d
Pn906f: eor #$ff ; original $906f
Pn9071: adc #$00 ; original $9071
Pn9073: sta R1 ; original $9073
Pn9075: lda R0 ; original $9075
Pn9077: sta PnVYF,X ; original $9077
Pn907a: lda R1 ; original $907a
Pn907c: sta PnVY,X ; original $907c
Pn907f: rts ; original $907f
Pn9080: lda #$00 ; original $9080
Pn9082: sta M0 ; original $9082
Pn9084: lda PnVXF,X ; original $9084
Pn9087: clc ; original $9087
Pn9088: adc PnXF,X ; original $9088
Pn908b: sta PnXF,X ; original $908b
Pn908e: lda PnVX,X ; original $908e
Pn9091: adc PnX,X ; original $9091
Pn9094: sta PnX,X ; original $9094
Pn9097: jcc Pn90a2 ; original $9097
Pn9099: lda PnVX,X ; original $9099
Pn909c: jmi Pn90a9 ; original $909c
Pn909e: inc M0 ; original $909e
Pn90a0: jne Pn90a9 ; original $90a0
Pn90a2: lda PnVX,X ; original $90a2
Pn90a5: jpl Pn90a9 ; original $90a5
Pn90a7: inc M0 ; original $90a7
Pn90a9: lda PnVYF,X ; original $90a9
Pn90ac: clc ; original $90ac
Pn90ad: adc PnYF,X ; original $90ad
Pn90b0: sta PnYF,X ; original $90b0
Pn90b3: lda PnVY,X ; original $90b3
Pn90b6: adc PnY,X ; original $90b6
Pn90b9: sta PnY,X ; original $90b9
Pn90bc: jcc Pn90c7 ; original $90bc
Pn90be: lda PnVY,X ; original $90be
Pn90c1: jmi Pn90ce ; original $90c1
Pn90c3: inc M0 ; original $90c3
Pn90c5: jne Pn90ce ; original $90c5
Pn90c7: lda PnVY,X ; original $90c7
Pn90ca: jpl Pn90ce ; original $90ca
Pn90cc: inc M0 ; original $90cc
Pn90ce: rts ; original $90ce
Pn90cf: ldx #$01 ; original $90cf
Pn90d1: lda #$00 ; original $90d1
Pn90d3: ldy #$1a ; original $90d3
Pn90d5: sta PnActive,X ; original $90d5
Pn90d8: sta PnFrame,X ; original $90d8
Pn90db: sta PnDrawFlags,X ; original $90db
Pn90de: sta PnX,X ; original $90de
Pn90e1: inx ; original $90e1
Pn90e2: dey ; original $90e2
Pn90e3: jne Pn90d5 ; original $90e3
Pn90e5: rts ; original $90e5
Pn9130: txa ; original $9130
Pn9131: and #$01 ; original $9131
Pn9133: sta PnScratch04 ; original $9133
Pn9135: lda VvClock ; original $9135
Pn9137: and #$01 ; original $9137
Pn9139: cmp PnScratch04 ; original $9139
Pn913b: jne Pn9140 ; original $913b
Pn913d: jmp PnTerrainQuery ; original $913d
Pn9140: lda #$00 ; original $9140
Pn9142: rts ; original $9142
Pn9143: lda PnContact,X ; original $9143
Pn9146: jeq Pn914e ; original $9146
Pn9148: and #$7f ; original $9148
Pn914a: tay ; original $914a
Pn914b: lda Pn9351,Y ; original $914b
Pn914e: rts ; original $914e
Pn9bba: lda #$00 ; original $9bba
Pn9bbc: sta PnActive,X ; original $9bbc
Pn9bbf: sta PnDrawFlags,X ; original $9bbf
Pn9bc2: sta PnFrame,X ; original $9bc2
Pn9bc5: sta PnPalette,X ; original $9bc5
Pn9bc8: sta PnType,X ; original $9bc8
Pn9bcb: sta PnAngle,X ; original $9bcb
Pn9bce: sta PnPhase,X ; original $9bce
Pn9bd1: sta PnAux,X ; original $9bd1
Pn9bd4: rts ; original $9bd4
Pnc8d7: lda #$00 ; original $c8d7
Pnc8d9: sta VvGun ; original $c8d9
Pnc8db: sta VvMeter ; original $c8db
Pnc8dd: sta VvFlags ; original $c8dd
Pnc8df: sta VvSpeed ; original $c8df
Pnc8e1: rts ; original $c8e1
Pnc977: sta PnAnimation,X ; original $c977
Pnc97a: tya ; original $c97a
Pnc97b: nop ; animation group is always zero ; original $c97b
Pnc97e: lda #$00 ; original $c97e
Pnc980: sta PnAnimCursor,X ; original $c980
Pnc983: sta PnAnimDelay,X ; original $c983
Pnc986: sta PnFrame,X ; original $c986
Pnc989: rts ; original $c989
Pnc98a: lda PnAnimDelay,X ; original $c98a
Pnc98d: jeq Pnc993 ; original $c98d
Pnc98f: dec PnAnimDelay,X ; original $c98f
Pnc992: rts ; original $c992
Pnc993: lda #0 ; native player/weapon animation group ; original $c993
Pnc996: asl a ; original $c996
Pnc997: tay ; original $c997
Pnc998: lda Pnca03,Y ; original $c998
Pnc99b: sta R4 ; original $c99b
Pnc99d: lda Pnca04,Y ; original $c99d
Pnc9a0: sta R5 ; original $c9a0
Pnc9a2: lda PnAnimation,X ; original $c9a2
Pnc9a5: asl a ; original $c9a5
Pnc9a6: tay ; original $c9a6
Pnc9a7: lda (R4),Y ; original $c9a7
Pnc9a9: sta R6 ; original $c9a9
Pnc9ab: iny ; original $c9ab
Pnc9ac: lda (R4),Y ; original $c9ac
Pnc9ae: sta R7 ; original $c9ae
Pnc9b0: ldy #$00 ; original $c9b0
Pnc9b2: lda (R6),Y ; original $c9b2
Pnc9b4: cmp #$fd ; original $c9b4
Pnc9b6: jne Pnc9db ; original $c9b6
Pnc9b8: iny ; original $c9b8
Pnc9b9: lda (R6),Y ; original $c9b9
Pnc9bb: sta PnAnimDelay,X ; original $c9bb
Pnc9be: ldy PnAnimCursor,X ; original $c9be
Pnc9c1: iny ; original $c9c1
Pnc9c2: iny ; original $c9c2
Pnc9c3: lda (R6),Y ; original $c9c3
Pnc9c5: cmp #$fe ; original $c9c5
Pnc9c7: jeq Pnc9e6 ; original $c9c7
Pnc9c9: cmp #$ff ; original $c9c9
Pnc9cb: jne Pnc9d6 ; original $c9cb
Pnc9cd: ldy #$02 ; original $c9cd
Pnc9cf: lda #$00 ; original $c9cf
Pnc9d1: sta PnAnimCursor,X ; original $c9d1
Pnc9d4: lda (R6),Y ; original $c9d4
Pnc9d6: sta PnFrame,X ; original $c9d6
Pnc9d9: jne Pnc9ff ; original $c9d9
Pnc9db: lda PnAnimCursor,X ; original $c9db
Pnc9de: asl a ; original $c9de
Pnc9df: tay ; original $c9df
Pnc9e0: lda (R6),Y ; original $c9e0
Pnc9e2: cmp #$fe ; original $c9e2
Pnc9e4: jne Pnc9ea ; original $c9e4
Pnc9e6: sta PnAnimDelay,X ; original $c9e6
Pnc9e9: rts ; original $c9e9
Pnc9ea: cmp #$ff ; original $c9ea
Pnc9ec: jne Pnc9f6 ; original $c9ec
Pnc9ee: ldy #$00 ; original $c9ee
Pnc9f0: tya ; original $c9f0
Pnc9f1: sta PnAnimCursor,X ; original $c9f1
Pnc9f4: lda (R6),Y ; original $c9f4
Pnc9f6: sta PnFrame,X ; original $c9f6
Pnc9f9: iny ; original $c9f9
Pnc9fa: lda (R6),Y ; original $c9fa
Pnc9fc: sta PnAnimDelay,X ; original $c9fc
Pnc9ff: inc PnAnimCursor,X ; original $c9ff
Pnca02: rts ; original $ca02
PnNativeBigMotion=Pn8191
.export PnNativeBigMotion
PnNativeMotion=Pn824c
.export PnNativeMotion
PnNativeGear=Pn83b2
.export PnNativeGear
PnNativeWeapons=Pn8493
.export PnNativeWeapons
PnNativeVelocity=Pn8b4b
.export PnNativeVelocity
PnNativeClear=Pn8c03
.export PnNativeClear
PnNativeBodyPose=Pn8c19
.export PnNativeBodyPose
PnNativeSpawn=Pn8db8
.export PnNativeSpawn
PnNativeKill=Pn9bba
.export PnNativeKill
PnNativeSetAnimation=Pnc977
.export PnNativeSetAnimation
PnNativeAnimate=Pnc98a
.export PnNativeAnimate
.popseg
