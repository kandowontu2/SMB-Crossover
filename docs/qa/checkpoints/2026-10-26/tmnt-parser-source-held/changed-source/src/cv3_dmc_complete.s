; MMC5 expanded only. Original CV3 request priority occupies four previously
; unused bytes after the existing CV1 private image and noise lane.
Cv3DmcPriority=RgAudioZp+32
Cv3DmcPending=RgAudioZp+33
Cv3DmcSavedC=RgAudioZp+34
Cv3DmcEntryA=RgAudioZp+35
.pushseg
.segment "CV3_COMBAT"
.proc Cv3DmcPrimaryQueue
 php
 lda Cv3AttackKind
 cmp #1
 bne Done
 lda Cv3Variant
 cmp #3
 bcs Done
 lda Cv3DmcPending
 cmp #$74
 bcs Done
 lda #$72
 sta Cv3DmcPending
Done:plp
 lda #4
 sta RgSfx
 rts
.endproc
.segment "CV3_GRIP"
.proc Cv3DmcFullInjuryQueue
 php
 lda Cv3Variant
 clc
 adc #$73
 sta Cv3DmcPending
 lda #0
 sta Square1SoundQueue
 plp
 lda Cv3Variant
 cmp #2
 lda #Sfx_PipeDown_Injury
 rts
.endproc
.proc Cv3DmcSceneRequest
 jmp Cv3FxSceneRequest ; original PHP/LDA0 relocated, following PCs exact
 sta Cv3DmcPending
 lda BassDmcActive
 cmp #3
 beq Owned
 lda #0
 sta Cv3DmcPriority
 jmp Done
Owned:lda #0
 jsr Cv3DmcOwnerWrite
Done:
 plp
 lda AvAudioRequest
 rts
.endproc
.segment "CV_WRAP"
.proc Cv3DmcBeforeCv1
 ; CvAudioPlay begins with authenticated LDA $e2, overwriting A/N/Z.
 ; Idle only uses LDA/ORA/branch/JMP, preserving every other input flag.
 lda Cv3DmcPending
 ora Cv3DmcPriority
 bne Work
 jmp CvAudioPlay
Work:php
 lda MmDeathFlag
 bne Cancel
 lda GameEngineSubroutine
 cmp #$0b
 beq Cancel
 lda Cv3DmcPending
 beq Play
 jsr Cv3DmcStartGate
 jmp Play
Cancel:lda #0
 sta Cv3DmcPending
 lda BassDmcActive
 cmp #3
 bne Unowned
 lda #0
 jsr Cv3DmcOwnerWrite
 jmp Play
Unowned:lda #0
 sta Cv3DmcPriority
Play:plp
 jmp CvAudioPlay
.endproc
.segment "X5_AUDIO_MIX"
.proc Cv3DmcResetOwner
 php
 jsr Cv3FxOwnerInit ; fixed original3B span, original outer PHP owns status
 lda BassDmcActive
 cmp #3
 beq Owned
 lda #0
 sta Cv3DmcPriority
Owned:lda #0
 jsr Cv3DmcOwnerWrite
 plp
 rts
.endproc
.segment "CV3_DMC_MANAGER"
Cv3DmcManagerStart:
.proc Cv3DmcStart
 php
 pha
 txa
 pha
 tya
 pha
 lda #0
 sta Cv3DmcPending
 lda Cv3DmcEntryA
 cmp #$72
 beq Valid
 cmp #$74
 bcc Done
 cmp #$77
 bcs Done
Valid:lda Cv3DmcPriority
 beq Incoming
 lda $4015
 and #$10
 bne Incoming
 lda #0
 jsr Cv3DmcOwnerWrite ; exact original completion resets source priority
Incoming:lda Cv3DmcEntryA
 sec
 sbc #$6d
 tax
 lda Cv3DmcPriority
 cmp #5
 bcc Start
 txa
 cmp Cv3DmcPriority
 bcc Done
Start:lda GuestCombinedEnable
 and #15
 sta $4015
 lda #0
 sta $4011
 stx Cv3DmcPriority
 lda Cv3DmcEntryA
 sec
 sbc #$72
 tay
 lda Rates,y
 sta $4010
 lda Addresses,y
 sta $4012
 lda Lengths,y
 sta $4013
 lda #$fd
 sta $5117 ; E mirror: identical resident code/vectors, source-only samples
 lda #3
 jsr TnDmcOwnerAdmission
 lda GuestCombinedEnable
 ora #$10
 sta GuestCombinedEnable
 sta $4015
Done:pla
 tay
 pla
 tax
 pla
 plp
 rts
Rates:.byte 15,15,14,15,13
Addresses:.byte ($f140-$c000)/64,0,($ff00-$c000)/64,($f5c0-$c000)/64,($ff00-$c000)/64
Lengths:.byte $44,0,$0c,$0c,$0c
.endproc
Cv3DmcManagerEnd:
.assert Cv3DmcManagerStart=$daf7,lderror,"Share bank125 after future TMNT cold adapter"
.assert Cv3DmcManagerEnd<=$de11,lderror,"Do not overwrite copied resident helpers or samples"
.popseg

; The source CV1 image ends atD836. This is recorded unused same-C28 slack,
; before the fixedDC00 wrapper; all original driver bytes/entrypoints stay exact.
.pushseg
.segment "CV_AUDIO"
.proc Cv3SaveAudioZp
 lda $60
 sta RgAudioCpuZp+23
 lda RgAudioZp+23
 sta $60
 lda $22
 sta RgAudioCpuZp+22
 lda RgAudioZp+22
 sta $22
 lda $ef
 sta RgAudioCpuZp+21
 lda RgAudioZp+21
 sta $ef
 lda $ee
 sta RgAudioCpuZp+20
 lda RgAudioZp+20
 sta $ee
 lda $ed
 sta RgAudioCpuZp+19
 lda RgAudioZp+19
 sta $ed
 lda $ec
 sta RgAudioCpuZp+18
 lda RgAudioZp+18
 sta $ec
 lda $eb
 sta RgAudioCpuZp+17
 lda RgAudioZp+17
 sta $eb
 lda $ea
 sta RgAudioCpuZp+16
 lda RgAudioZp+16
 sta $ea
 lda $e9
 sta RgAudioCpuZp+15
 lda RgAudioZp+15
 sta $e9
 lda $e8
 sta RgAudioCpuZp+14
 lda RgAudioZp+14
 sta $e8
 lda $e7
 sta RgAudioCpuZp+13
 lda RgAudioZp+13
 sta $e7
 lda $e6
 sta RgAudioCpuZp+12
 lda RgAudioZp+12
 sta $e6
 lda $e5
 sta RgAudioCpuZp+11
 lda RgAudioZp+11
 sta $e5
 lda $e4
 sta RgAudioCpuZp+10
 lda RgAudioZp+10
 sta $e4
 lda $e3
 sta RgAudioCpuZp+9
 lda RgAudioZp+9
 sta $e3
 lda $e2
 sta RgAudioCpuZp+8
 lda RgAudioZp+8
 sta $e2
 lda $e1
 sta RgAudioCpuZp+7
 lda RgAudioZp+7
 sta $e1
 lda $e0
 sta RgAudioCpuZp+6
 lda RgAudioZp+6
 sta $e0
 lda $bf
 sta RgAudioCpuZp+5
 lda RgAudioZp+5
 sta $bf
 lda $be
 sta RgAudioCpuZp+4
 lda RgAudioZp+4
 sta $be
 lda $bd
 sta RgAudioCpuZp+3
 lda RgAudioZp+3
 sta $bd
 lda $bc
 sta RgAudioCpuZp+2
 lda RgAudioZp+2
 sta $bc
 lda $bb
 sta RgAudioCpuZp+1
 lda RgAudioZp+1
 sta $bb
 lda $ba
 sta RgAudioCpuZp+0
 lda RgAudioZp+0
 sta $ba
 ldx #$ba
 ldy #$ff
 cpy #$ff ; exact final indexed-loop register/status contract
 rts
.endproc
.assert Cv3SaveAudioZp=$d837,lderror,"Recorded unused source-CV1 slack start"
.assert *<=$dc00,lderror,"Preserve fixed wrapper and every existing source byte"
.popseg
