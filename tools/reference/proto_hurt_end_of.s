; Keep MM/Proto/Bass's last committed injury page through skipped draws.
; Restore legacy buster pages only inside an actual OAM drawing transaction;
; Proto's existing explicit publisher continues to own its alternate pages.
.pushseg
.segment "PROTO_HURT_END"
.proc ProtoHurtEndCore
 phx
 phy
 lda ObjectOffset
 pha
 lda SelectedCharacter
 cmp #CHARACTER_MEGAMAN
 beq DeferredMega
 cmp #CHARACTER_BASS
 bne LegacyBank
 lda #BASS_HURT_NORMAL_BANK
 cmp PlayerChrBank
 jmp Motion
DeferredMega:
 lda #MM_HURT_NORMAL_BANK
 cmp PlayerChrBank             ; preserve the old public carry result
 jmp Motion
LegacyBank:
 lda #MM_HURT_NORMAL_BANK
 ldx SelectedCharacter
 cpx #CHARACTER_BASS
 bne :+
  lda #BASS_HURT_NORMAL_BANK
:cmp PlayerChrBank
 beq :+
  sta PlayerChrBank
  inc ReloadCHRBank
:
Motion:
 lda Player_State
 bne Done
 lda #0
 sta MmVX
 sta MmVX+1
 sta MmVX+2
 sta Player_X_Speed
 sta MmLastXSpeed
Done:
 pla
 sta ObjectOffset
 ply
 plx
 rts
.endproc
.export ProtoHurtEndCore

; Called only by the old hurt-draw zero-timer branch during DrawAll. The
; public bank10 gate admits only low bytes129/130 and restores caller flags/A.
.proc ProtoRecoveryDrawCore
 lda GuestHurtTicks
 bne Done
 lda X5ChrMode
 bne Done
 lda SelectedCharacter
 cmp #CHARACTER_MEGAMAN
 beq Mega
 cmp #CHARACTER_BASS
 bne Done
 lda RlVariant
 bne Done
 lda PlayerChrBank
 cmp #BASS_HURT_BODY_BANK
 bne Done
 lda #BASS_HURT_NORMAL_BANK
 bne Store
Mega:
 lda ProtoVariant
 bne Done
 lda PlayerChrBank
 cmp #MM_HURT_BODY_BANK
 bne Done
 lda #MM_HURT_NORMAL_BANK
Store:
 sta PlayerChrBank
 inc ReloadCHRBank
Done:
 rts
.endproc
.export ProtoRecoveryDrawCore
.popseg
