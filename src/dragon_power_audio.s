; Independent authentic Dragon Power audio closure. ROOT owns scheduling.
; Raw24-only; no new RAM. RgAudioRam137B and CpuZp5B are identity-exclusive.
; GuestAudioFinish Silent unconditionally clears CV3 aliases in RgAudioZp;
; those are deliberately NOT Dragon driver storage.
DpAudioState=RgAudioRam
.macro DpAudioSaveCaller
 php
 pha
 txa
 pha
 tya
 pha
 lda SelectedCharacter
 cmp #24
 beq :+
 jmp DpAudioReturn
:
.endmacro
.pushseg
.segment "DRAGON_POWER_AUDIO"
.include "dragon_power_audio_native.inc"
.proc DpAudioStore08
 sta GuestNativeApu+8
 php
 inc GuestNativeDirty+8
 plp
 rts
.endproc
.proc DpAudioBorrow
 ldx #4
Loop:lda $12,x
 sta RgAudioCpuZp,x
 lda DpAudioState+132,x
 sta $12,x
 dex
 bpl Loop
 rts
.endproc
.proc DpAudioRelease
 ldx #4
Loop:lda $12,x
 sta DpAudioState+132,x
 lda RgAudioCpuZp,x
 sta $12,x
 dex
 bpl Loop
 rts
.endproc
.proc DpAudioInitialize
 lda #24
 sta RgAudioCharacter
 lda #0
 sta RgAudioSilenced
 ldx #136
Clear:sta DpAudioState,x
 dex
 cpx #$ff
 bne Clear
 lda #$ff
 .repeat 6,I
 sta DpAudioState+20*I
 .endrepeat
 jsr DpAudioBorrow
 ldx #0
Song:txa
 jsr DpAN98A8             ; actual original0:8CE5 startup group0/1/2/3.
 inx
 cpx #4
 bne Song
 jmp DpAudioRelease
.endproc
.proc DpAudioEnsure
 lda RgAudioCharacter
 cmp #24
 bne DpAudioInitialize
 rts
.endproc
.proc DpAudioInit
 DpAudioSaveCaller
 jsr DpAudioInitialize
 jmp DpAudioReturn
.endproc
.proc DpAudioTick
 DpAudioSaveCaller
 jsr DpAudioEnsure
 jsr DpAudioBorrow
 lda RgAudioSilenced
 beq Play
 lda DpAudioState+120      ; actual source03F0 enable image, no DMC source.
 jsr GuestNativeStatusSTA
 lda #1
 ldx #15
Dirty:sta GuestNativeDirty,x ; resume authentic buffered note image/retriggers.
 dex
 bpl Dirty
 lda #0
 sta RgAudioSilenced
Play:jsr DpAN8F68
 jsr DpAudioRelease
 jmp DpAudioReturn
.endproc
.proc DpAudioRequestEvent
 DpAudioSaveCaller
 tsx
 lda $0103,x              ; actual saved callerA, before any RAM owner writes.
 cmp #109
 bcs Invalid
 cmp #33
 bcc Valid
 cmp #36
 bcc Invalid
 cmp #39
 bcc Valid
 cmp #45
 bcc Invalid              ; original unused FFFF descriptor holes, not SFX33hex.
Valid:sta RgAudioRequest
 jsr DpAudioEnsure
 jsr DpAudioBorrow
 lda RgAudioRequest
 jsr DpAN98A8
 jsr DpAudioRelease
 jmp DpAudioReturn
Invalid:lda #$ff
 sta RgAudioRequest       ; explicit refused invalid/placeholder event diagnostic.
 jmp DpAudioReturn
.endproc
.proc DpAudioMute
 DpAudioSaveCaller
 jsr DpAudioEnsure
 lda #1
 sta RgAudioSilenced
 lda #0
 jsr GuestNativeStatusSTA
 jmp DpAudioReturn
.endproc
DpAudioReturn:
 pla
 tay
 pla
 tax
 pla
 plp
 rts
DpAudioEnd:
.assert DpAudioEnd-DpAudioNativeStart<=$1680,error,"Dragon audio exceeds approved96A980..BFFF"
.export DpAudioInit,DpAudioTick,DpAudioRequestEvent,DpAudioMute,DpAudioBorrow,DpAudioRelease,DpAudioState,DpAudioEnd
.popseg
