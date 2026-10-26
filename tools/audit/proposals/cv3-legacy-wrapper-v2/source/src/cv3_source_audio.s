; Actual original USA CV3 event1F, isolated noise image in the existing
;160-byte roster-private ZP slab. Kind2 uses only the first24 bytes; kinds0/1
;use17. Bytes24..31 are private to this lane and consume no additional RAM.
Cv3NoiseApu=RgAudioZp+24
Cv3NoiseActive=RgAudioZp+25 ; unused APU noise register13
Cv3NoiseIndex=RgAudioZp+28
Cv3NoiseMusicVolume=RgAudioZp+29
Cv3NoiseMusicPeriod=RgAudioZp+30
Cv3NoiseMusicHigh=RgAudioZp+31
.pushseg
.segment "CV3_COMBAT"
.proc Cv3SpawnAudioType
.if ::MAPPER_MMC5
 jmp Cv3FxSpawn
 .res 15,$ea
.else
 sta Cv3ShotType,x
 cmp #6
 bne Done
 lda AvAudioRequest
 bne Done
 lda #26
 sta AvAudioRequest
Done:rts
.endif
.endproc
.segment "CV3_GRIP"
.proc Cv3NoiseSceneReset
.if ::MAPPER_MMC5
 php
 jsr Cv3DmcSceneRequest
 plp
 lda Cv3Variant
 rts
 .res 28-(*-::Cv3NoiseSceneReset),$ea
.else
 php
 lda AvAudioRequest
 cmp #26
 bne Owner
 lda #0
 sta AvAudioRequest
Owner:lda Cv3NoiseActive
 beq Variant
 lda #$80 ; stop at the next audio owner update, restoring its music image
 sta Cv3NoiseActive
Variant:plp
 lda Cv3Variant
 rts
.endif
.endproc
.segment "CV_WRAP"
.proc Cv3MusicAndNoiseTick
.if ::MAPPER_MMC5
 jmp Cv3FxTick
.else
 jsr CvAudioPlay
.endif
 lda Cv3NoiseActive
 beq Request
KnownActive:lda GuestNativeDirty+12
 beq Period
 lda GuestNativeApu+12
 sta Cv3NoiseMusicVolume
 lda Cv3NoiseApu
 sta GuestNativeApu+12
 lda #0
 sta GuestNativeDirty+12
Period:lda GuestNativeDirty+14
 beq High
 lda GuestNativeApu+14
 sta Cv3NoiseMusicPeriod
 lda Cv3NoiseApu+2
 sta GuestNativeApu+14
 lda #0
 sta GuestNativeDirty+14
High:lda GuestNativeDirty+15
 beq Request
 lda GuestNativeApu+15
 sta Cv3NoiseMusicHigh
 lda Cv3NoiseApu+3
 sta GuestNativeApu+15
 lda #0
 sta GuestNativeDirty+15
Request:
 .if !::MAPPER_MMC5
 lda Cv3NoiseActive
 bmi End
 .endif
 ; Both MMC5 Tick callers enter only with a nonnegative Active value.
 lda AvAudioRequest
 cmp #26
 bne Continue
 lda Cv3NoiseActive
 bne Reset
 lda GuestNativeApu+12
 sta Cv3NoiseMusicVolume
 lda GuestNativeApu+14
 sta Cv3NoiseMusicPeriod
 lda GuestNativeApu+15
 sta Cv3NoiseMusicHigh
Reset:lda #0
 sta AvAudioRequest
 sta Cv3NoiseIndex
 lda #1
 sta Cv3NoiseActive
Continue:
 .if !::MAPPER_MMC5
 lda Cv3NoiseActive
 beq Done
 .endif
 ; Entry is positive, or cold Av26 has just set Active=1. No phase is omitted.
 ldy Cv3NoiseIndex
 cpy #28
 beq End
 inc Cv3NoiseIndex
 lda Cv3NoiseFlags,y
 beq Done
 cmp #3
 bne Volume
 lda Cv3NoisePeriods,y
 sta Cv3NoiseApu+2
 sta GuestNativeApu+14
 .if ::MAPPER_MMC5
 jsr Cv3FxLegacyNoiseHigh
 .res 2,$ea
 .else
 lda #8
 sta Cv3NoiseApu+3
 .endif
 sta GuestNativeApu+15
 lda #1
 sta GuestNativeDirty+14
 sta GuestNativeDirty+15
Volume:lda Cv3NoiseVolumes,y
 sta Cv3NoiseApu
 sta GuestNativeApu+12
 lda #1
 sta GuestNativeDirty+12
Done:rts
End:lda #0
 sta Cv3NoiseActive
RestoreMusic:lda Cv3NoiseMusicVolume
 sta GuestNativeApu+12
 lda Cv3NoiseMusicPeriod
 sta GuestNativeApu+14
 lda Cv3NoiseMusicHigh
 sta GuestNativeApu+15
 lda #1
 sta GuestNativeDirty+12
 sta GuestNativeDirty+14
 sta GuestNativeDirty+15
 rts
 .if ::MAPPER_MMC5
 .assert *-::Cv3MusicAndNoiseTick<=221,error,"Retained genuine public legacy span"
 .res 221-(*-::Cv3MusicAndNoiseTick),$ea
 .endif
.endproc
; The imported driver's one unmarked direct volume store also participates
; in the private music cache. Preserve its original A/X/Y/status contract.
.proc Cv3NoiseVolumeStore
 sta GuestNativeApu+12
 php
 pha
 lda Cv3NoiseActive
 beq Done
 inc GuestNativeDirty+12
Done:pla
 plp
 rts
.endproc
Cv3NoiseFlags:.byte 3,0,0,3,0,0,3,0,0,3,0,0,3,0,0,3,0,0,3,0,0,3,0,0,3,0,0,1
Cv3NoiseVolumes:.byte 57,57,57,48,48,48,57,57,57,53,53,53,52,52,52,51,51,51,50,50,50,49,49,49,49,49,49,48
Cv3NoisePeriods:.byte 7,7,7,0,0,0,8,8,8,15,15,15,1,1,1,10,10,10,5,5,5,8,8,8,11,11,11,11
.segment "CV_WRAP"
.proc Cv3RestoreAudioZp
 lda $60
 sta RgAudioZp+23
 lda RgAudioCpuZp+23
 sta $60
 lda $22
 sta RgAudioZp+22
 lda RgAudioCpuZp+22
 sta $22
 lda $ef
 sta RgAudioZp+21
 lda RgAudioCpuZp+21
 sta $ef
 lda $ee
 sta RgAudioZp+20
 lda RgAudioCpuZp+20
 sta $ee
 lda $ed
 sta RgAudioZp+19
 lda RgAudioCpuZp+19
 sta $ed
 lda $ec
 sta RgAudioZp+18
 lda RgAudioCpuZp+18
 sta $ec
 lda $eb
 sta RgAudioZp+17
 lda RgAudioCpuZp+17
 sta $eb
 lda $ea
 sta RgAudioZp+16
 lda RgAudioCpuZp+16
 sta $ea
 lda $e9
 sta RgAudioZp+15
 lda RgAudioCpuZp+15
 sta $e9
 lda $e8
 sta RgAudioZp+14
 lda RgAudioCpuZp+14
 sta $e8
 lda $e7
 sta RgAudioZp+13
 lda RgAudioCpuZp+13
 sta $e7
 lda $e6
 sta RgAudioZp+12
 lda RgAudioCpuZp+12
 sta $e6
 lda $e5
 sta RgAudioZp+11
 lda RgAudioCpuZp+11
 sta $e5
 lda $e4
 sta RgAudioZp+10
 lda RgAudioCpuZp+10
 sta $e4
 lda $e3
 sta RgAudioZp+9
 lda RgAudioCpuZp+9
 sta $e3
 lda $e2
 sta RgAudioZp+8
 lda RgAudioCpuZp+8
 sta $e2
 lda $e1
 sta RgAudioZp+7
 lda RgAudioCpuZp+7
 sta $e1
 lda $e0
 sta RgAudioZp+6
 lda RgAudioCpuZp+6
 sta $e0
 lda $bf
 sta RgAudioZp+5
 lda RgAudioCpuZp+5
 sta $bf
 lda $be
 sta RgAudioZp+4
 lda RgAudioCpuZp+4
 sta $be
 lda $bd
 sta RgAudioZp+3
 lda RgAudioCpuZp+3
 sta $bd
 lda $bc
 sta RgAudioZp+2
 lda RgAudioCpuZp+2
 sta $bc
 lda $bb
 sta RgAudioZp+1
 lda RgAudioCpuZp+1
 sta $bb
 lda $ba
 sta RgAudioZp+0
 lda RgAudioCpuZp+0
 sta $ba
 ldx #$ba
 ldy #$ff
 cpy #$ff ; match original final comparison and restored registers
 rts
.endproc
.popseg
