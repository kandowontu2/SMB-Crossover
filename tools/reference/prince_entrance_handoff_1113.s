; Native PLAYER bank1 only. The ordinary entrance hook has already excluded
; AltEntranceControl2 and header6/7. Every other owner/water enters the exact
; original PlayerRdy. Prince receives one unchanged neutral native update;
; its resulting floor state controls the handoff, never a source fall flag.
.setcpu "6502"
PrinceOrdinaryEntrance:
 lda SelectedCharacter
 cmp #38
 bne Ready
 lda AreaType
 beq Ready
 lda #0
 jsr AutoControlPlayer
 lda Player_State
 beq Ready
 rts
Ready:
 jmp PlayerRdy
