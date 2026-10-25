; Source-original Grant74/Alucard76 injury reuses exact existing Simon
;193-byte payload, with source rates14/13. Sypha remains unchanged pending
;its distinct payload. No primary72 sample/priority implementation is claimed.
.pushseg
.segment "CV3_GRIP"
.proc Cv3DmcInjuryQueue
 lda Cv3Variant
 cmp #2
 beq Generic
 lda #AV_SFX_SIMONTAKEDAMAGE
 sta AvAudioRequest
 lda #0
 sta Square1SoundQueue
 lda #Sfx_PipeDown_Injury
 rts
Generic:lda #Sfx_PipeDown_Injury
 sta Square1SoundQueue
 rts
.endproc
.segment "SOPHIA_LAND_AUDIO"
.proc Cv3DmcInjuryRate
 tya
 pha
 lda #15
 cpx #1 ; typed22 only; typed21 retains its exact original rate
 bne Store
 ldy SelectedCharacter
 cpy #CHARACTER_SIMON
 bne Store
 ldy Cv3Variant
 lda Cv3DmcInjuryRates,y
Store:sta $4010
 pla
 tay
 sec ; valid request21/22 preceding SEC/SBC always leaves carry set
 rts ; caller immediately executes its original LDA#0, restoring A/NZ
.endproc
.assert Cv3DmcInjuryRate=$bfe3,lderror,"Last bank7 padding begins here"
.assert *=$bfff,lderror,"Leave bank7's final byte free"
.popseg
