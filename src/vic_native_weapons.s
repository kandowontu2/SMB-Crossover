; Generated original Gradius USA firing, missile and shot program.
VvStage=$5df9
.export VvStage
VvWeaponFresh=$5dfb
.export VvWeaponFresh
VvWeaponScratch=$5dfa
.export VvWeaponScratch
VvProbeX=$5df7
.export VvProbeX
VvProbeY=$5df6
.export VvProbeY
VvWeaponLoop=$5df8
.export VvWeaponLoop
.pushseg
.segment "VIC_CORE"
.proc VvNativeWeapons
Vwa0e9: ldx VvGun ; original$a0e9
Vwa0eb: lda Vwa0e0,X ; original$a0eb
Vwa0ee: sta VvStepLo ; original$a0ee
Vwa0f0: lda Vwa0e6,X ; original$a0f0
Vwa0f3: sta VvStepHi ; original$a0f3
Vwa0f5: lda Vwa0e3,X ; original$a0f5
Vwa0f8: sta VvWeaponScratch ; original$a0f8
Vwa0fa: ldx VvPlayer ; original$a0fa
Vwa0fc: lda VvFresh,X ; original$a0fc
Vwa0fe: and #$80 ; original$a0fe
Vwa100: sta VvWeaponFresh ; original$a100
Vwa102: lda VvHeld,X ; original$a102
Vwa104: and #$80 ; original$a104
Vwa106: sta VvTilt ; original$a106
Vwa108: ldx VvOptions ; original$a108
Vwa10a: lda VvObjAnim+3,X ; original$a10a
Vwa10d: jne Vwa134 ; original$a10d
Vwa10f: lda VvWeaponFresh ; original$a10f
Vwa111: jne Vwa11c ; original$a111
Vwa113: lda VvFireTimer,X ; original$a113
Vwa116: jne Vwa131 ; original$a116
Vwa118: lda VvTilt ; original$a118
Vwa11a: jeq Vwa134 ; original$a11a
Vwa11c: jsr Vwa235 ; original$a11c
Vwa11f: lda VvAutoFire ; original$a11f
Vwa121: sta VvFireTimer,X ; original$a121
Vwa124: lda VvGun ; original$a124
Vwa126: cmp #$02 ; original$a126
Vwa128: jeq Vwa134 ; original$a128
Vwa12a: lda VvAutoFire ; original$a12a
Vwa12c: sta VvFireTimer+3,X ; original$a12c
Vwa12f: jne Vwa15c ; original$a12f
Vwa131: dec VvFireTimer,X ; original$a131
Vwa134: lda VvObjAnim+6,X ; original$a134
Vwa137: jne Vwa15c ; original$a137
Vwa139: lda VvWeaponFresh ; original$a139
Vwa13b: jne Vwa146 ; original$a13b
Vwa13d: lda VvFireTimer+3,X ; original$a13d
Vwa140: jne Vwa159 ; original$a140
Vwa142: lda VvTilt ; original$a142
Vwa144: jeq Vwa15c ; original$a144
Vwa146: jsr Vwa250 ; original$a146
Vwa149: lda VvAutoFire ; original$a149
Vwa14b: sta VvFireTimer+3,X ; original$a14b
Vwa14e: lda VvGun ; original$a14e
Vwa150: cmp #$02 ; original$a150
Vwa152: jeq Vwa15c ; original$a152
Vwa154: lda VvAutoFire ; original$a154
Vwa156: sta VvFireTimer,X ; original$a156
Vwa159: dec VvFireTimer+3,X ; original$a159
Vwa15c: lda VvMissile ; original$a15c
Vwa15e: jeq Vwa16c ; original$a15e
Vwa160: lda VvObjAnim+9,X ; original$a160
Vwa163: jne Vwa16c ; original$a163
Vwa165: lda VvTilt ; original$a165
Vwa167: jeq Vwa16c ; original$a167
Vwa169: jsr Vwa26b ; original$a169
Vwa16c: dex ; original$a16c
Vwa16d: jpl Vwa10a ; original$a16d
Vwa16f: ldx #$08 ; original$a16f
Vwa171: stx VvWeaponLoop ; original$a171
Vwa173: ldy #$00 ; original$a173
Vwa175: ldx VvWeaponLoop ; original$a175
Vwa177: lda VvObjSub+3,X ; original$a177
Vwa17a: jeq Vwa1de ; original$a17a
Vwa17c: lda VvStage ; original$a17c
Vwa17e: cmp #$04 ; original$a17e
Vwa180: jeq Vwa1aa ; original$a180
Vwa182: jsr VvTerrainUnder ; original$a182
Vwa185: ldy #$00 ; original$a185
Vwa187: cmp #$00 ; original$a187
Vwa189: jeq Vwa1aa ; original$a189
Vwa18b: lda VvProbeY ; original$a18b
Vwa18d: sec ; original$a18d
Vwa18e: sbc #$08 ; original$a18e
Vwa190: sta VvProbeY ; original$a190
Vwa192: lda VvProbeX ; original$a192
Vwa194: clc ; original$a194
Vwa195: adc #$08 ; original$a195
Vwa197: sta VvProbeX ; original$a197
Vwa199: jsr VvTerrainSide ; original$a199
Vwa19c: jne Vwa1d6 ; original$a19c
Vwa19e: ldy #$01 ; original$a19e
Vwa1a0: lda #$08 ; original$a1a0
Vwa1a2: jne Vwa1ac ; original$a1a2
Vwa1aa: lda #$0a ; original$a1aa
Vwa1ac: sta VvObjAnim+3,X ; original$a1ac
Vwa1af: lda Vwa1a4,Y ; original$a1af
Vwa1b2: clc ; original$a1b2
Vwa1b3: adc VvObjY+3,X ; original$a1b3
Vwa1b6: sta VvObjY+3,X ; original$a1b6
Vwa1b9: cmp #$c8 ; original$a1b9
Vwa1bb: jcs Vwa1d6 ; original$a1bb
Vwa1bd: lda Vwa1a8,Y ; original$a1bd
Vwa1c0: clc ; original$a1c0
Vwa1c1: adc VvObjXF+3,X ; original$a1c1
Vwa1c4: sta VvObjXF+3,X ; original$a1c4
Vwa1c7: lda VvObjX+3,X ; original$a1c7
Vwa1ca: adc Vwa1a6,Y ; original$a1ca
Vwa1cd: sta VvObjX+3,X ; original$a1cd
Vwa1d0: jcs Vwa1d6 ; original$a1d0
Vwa1d2: cmp #$f8 ; original$a1d2
Vwa1d4: jcc Vwa1de ; original$a1d4
Vwa1d6: lda #$00 ; original$a1d6
Vwa1d8: sta VvObjAnim+3,X ; original$a1d8
Vwa1db: sta VvObjSub+3,X ; original$a1db
Vwa1de: dec VvWeaponLoop ; original$a1de
Vwa1e0: lda VvWeaponLoop ; original$a1e0
Vwa1e2: cmp #$06 ; original$a1e2
Vwa1e4: jcs Vwa173 ; original$a1e4
Vwa1e6: ldx #$00 ; original$a1e6
Vwa1e8: stx VvStepLo ; original$a1e8
Vwa1ea: lda VvObjAnim+3,X ; original$a1ea
Vwa1ed: jeq Vwa22f ; original$a1ed
Vwa1ef: lda VvObjSub+3,X ; original$a1ef
Vwa1f2: jne Vwa20b ; original$a1f2
Vwa1f4: lda #$07 ; original$a1f4
Vwa1f6: clc ; original$a1f6
Vwa1f7: adc VvObjX+3,X ; original$a1f7
Vwa1fa: sta VvObjX+3,X ; original$a1fa
Vwa1fd: cmp #$f8 ; original$a1fd
Vwa1ff: jcc Vwa22f ; original$a1ff
Vwa201: lda #$00 ; original$a201
Vwa203: sta VvObjSub+3,X ; original$a203
Vwa206: sta VvObjAnim+3,X ; original$a206
Vwa209: jeq Vwa22f ; original$a209
Vwa20b: cmp #$02 ; original$a20b
Vwa20d: jne Vwa220 ; original$a20d
Vwa20f: lda VvObjY+3,X ; original$a20f
Vwa212: sec ; original$a212
Vwa213: sbc #$04 ; original$a213
Vwa215: sta VvObjY+3,X ; original$a215
Vwa218: cmp #$10 ; original$a218
Vwa21a: jcc Vwa201 ; original$a21a
Vwa21c: lda #$04 ; original$a21c
Vwa21e: jne Vwa1f6 ; original$a21e
Vwa220: lda VvObjX+3,X ; original$a220
Vwa223: clc ; original$a223
Vwa224: adc #$0c ; original$a224
Vwa226: sta VvObjX+3,X ; original$a226
Vwa229: jcs Vwa201 ; original$a229
Vwa22b: cmp #$f0 ; original$a22b
Vwa22d: jcs Vwa201 ; original$a22d
Vwa22f: inx ; original$a22f
Vwa230: cpx #$06 ; original$a230
Vwa232: jcc Vwa1ea ; original$a232
Vwa234: rts ; original$a234
Vwa235: lda VvObjX,X ; original$a235
Vwa238: sta VvObjX+3,X ; original$a238
Vwa23b: lda VvObjY,X ; original$a23b
Vwa23e: sta VvObjY+3,X ; original$a23e
Vwa241: lda VvStepLo ; original$a241
Vwa243: sta VvObjAnim+3,X ; original$a243
Vwa246: lda VvGun ; original$a246
Vwa248: and #$01 ; original$a248
Vwa24a: sta VvObjSub+3,X ; original$a24a
Vwa24d: jmp Vwa266 ; original$a24d
Vwa250: lda VvObjX,X ; original$a250
Vwa253: sta VvObjX+6,X ; original$a253
Vwa256: lda VvObjY,X ; original$a256
Vwa259: sta VvObjY+6,X ; original$a259
Vwa25c: lda VvWeaponScratch ; original$a25c
Vwa25e: sta VvObjAnim+6,X ; original$a25e
Vwa261: lda VvGun ; original$a261
Vwa263: sta VvObjSub+6,X ; original$a263
Vwa266: lda VvStepHi ; original$a266
Vwa268: jmp VvSoundEvent ; original$a268
Vwa26b: lda VvObjX,X ; original$a26b
Vwa26e: sta VvObjX+9,X ; original$a26e
Vwa271: lda VvObjY,X ; original$a271
Vwa274: clc ; original$a274
Vwa275: adc #$06 ; original$a275
Vwa277: sta VvObjY+9,X ; original$a277
Vwa27a: lda #$0a ; original$a27a
Vwa27c: sta VvObjAnim+9,X ; original$a27c
Vwa27f: lda #$03 ; original$a27f
Vwa281: sta VvObjSub+9,X ; original$a281
Vwa284: rts ; original$a284
Vwa0e0: .byte $06,$07,$06
Vwa0e3: .byte $06,$07,$24
Vwa0e6: .byte $01,$02,$01
Vwa1a4: .byte $02,$00
Vwa1a6: .byte $00,$02
Vwa1a8: .byte $80,$00
.endproc
VvNativeMissiles=VvNativeWeapons::Vwa16f
VvNativeShots=VvNativeWeapons::Vwa1e6
.export VvNativeMissiles,VvNativeShots
.proc VvSoundEvent
  sta VvSfxEvent
  rts
.endproc
.popseg
.include "vic_world_queries.s"
