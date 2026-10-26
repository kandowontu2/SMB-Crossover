.proc ProtoLegacyDrawShotsCold
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  jne Done
  lda MmDeathFlag
  beq :+
    farcall MegaManDrawDeath,jmp
  :
  ldx #3
Loop:
  stx MmSlot
  ldy MmBulletType,x
  beq Next
  jsr MmProtoShotMuxAdmission
  lsr
  sta MmTemp
  lda ShotLengths-1,y
  sta MmDamage
  lda MmTemp
Modulo:
  cmp MmDamage
  bcc PhaseReady
  sbc MmDamage
  jmp Modulo
PhaseReady:
  clc
  adc ShotStarts-1,y
  tay
  lda MmBulletDir,x
  cmp #1
  bne Left
  lda ProtoShotRightLo-METASPRITE_MM_BULLET_1,y
  sta R0
  lda ProtoShotRightHi-METASPRITE_MM_BULLET_1,y
  bne Pointer
Left:
  lda ProtoShotLeftLo-METASPRITE_MM_BULLET_1,y
  sta R0
  lda ProtoShotLeftHi-METASPRITE_MM_BULLET_1,y
Pointer:
  sta R1
  lda MmBulletX,x
  sec
  sbc ScreenLeft_X_Pos
  sta R4
  lda MmBulletPage,x
  sbc ScreenLeft_PageLoc
  sta R5
  lda MmBulletY,x
  sta R6
  lda #1
  sta R7
  lda #0
  sta R3
  farcall MetaspriteRenderLoop
Next:
  ldx MmSlot
  dex
  bpl Loop
Done:
  rts
ShotStarts:
  .byte METASPRITE_MM_BULLET_1, METASPRITE_MM_BULLET_2, METASPRITE_MM_BULLET_6
  .byte METASPRITE_MM_BULLET_10, METASPRITE_MM_BULLET_4, METASPRITE_MM_BULLET_13
ShotLengths:
  .byte 1,2,4,3,2,3
.endproc
ProtoShotLeftLo:
 .byte <MmMM_BULLET_1Left,<MmMM_BULLET_2Left,<MmMM_BULLET_3Left,<MmMM_BULLET_4Left,<MmMM_BULLET_5Left,<MmMM_BULLET_6Left,<MmMM_BULLET_7Left,<MmMM_BULLET_8Left,<MmMM_BULLET_9Left,<MmMM_BULLET_10Left,<MmMM_BULLET_11Left,<MmMM_BULLET_12Left,<MmMM_BULLET_13Left,<MmMM_BULLET_14Left,<MmMM_BULLET_15Left,<MmMM_BULLET_16Left
ProtoShotLeftHi:
 .byte >MmMM_BULLET_1Left,>MmMM_BULLET_2Left,>MmMM_BULLET_3Left,>MmMM_BULLET_4Left,>MmMM_BULLET_5Left,>MmMM_BULLET_6Left,>MmMM_BULLET_7Left,>MmMM_BULLET_8Left,>MmMM_BULLET_9Left,>MmMM_BULLET_10Left,>MmMM_BULLET_11Left,>MmMM_BULLET_12Left,>MmMM_BULLET_13Left,>MmMM_BULLET_14Left,>MmMM_BULLET_15Left,>MmMM_BULLET_16Left
ProtoShotRightLo:
 .byte <MmMM_BULLET_1Right,<MmMM_BULLET_2Right,<MmMM_BULLET_3Right,<MmMM_BULLET_4Right,<MmMM_BULLET_5Right,<MmMM_BULLET_6Right,<MmMM_BULLET_7Right,<MmMM_BULLET_8Right,<MmMM_BULLET_9Right,<MmMM_BULLET_10Right,<MmMM_BULLET_11Right,<MmMM_BULLET_12Right,<MmMM_BULLET_13Right,<MmMM_BULLET_14Right,<MmMM_BULLET_15Right,<MmMM_BULLET_16Right
ProtoShotRightHi:
 .byte >MmMM_BULLET_1Right,>MmMM_BULLET_2Right,>MmMM_BULLET_3Right,>MmMM_BULLET_4Right,>MmMM_BULLET_5Right,>MmMM_BULLET_6Right,>MmMM_BULLET_7Right,>MmMM_BULLET_8Right,>MmMM_BULLET_9Right,>MmMM_BULLET_10Right,>MmMM_BULLET_11Right,>MmMM_BULLET_12Right,>MmMM_BULLET_13Right,>MmMM_BULLET_14Right,>MmMM_BULLET_15Right,>MmMM_BULLET_16Right
.assert METASPRITE_MM_BULLET_16-METASPRITE_MM_BULLET_1=15,error,"Bullet IDs remain contiguous"


; Ordinary shot presentation only. No new RAM or projectile-state stores.
; SpecialDrawShots advances the existing SsDrawFirst once per admitted
; live Mega/Proto DrawAll construction, modulo10. No new state is stored.
; The balanced physical-slot cover tolerates changes in other live slots.
; Skipped hardware publication can still alias any construction phase.
; Original live/type/death/family guards execute before this helper.
.pushseg
.segment "MM_PROTO_SHOT_MUX"
.proc MmProtoShotMuxAdmission
 php
 pha
 txa
 pha
 lda #0
 ldx #3
Mask:
 ldy MmBulletType,x
 cpy #1
 rol
 dex
 bpl Mask
 tax
 asl
 asl
 pha
 lda SsDrawFirst
 cmp #10
 bcc PhaseValid
 lda #0 ; Defined safe direct-entry behavior; real DrawAll already normalizes.
PhaseValid:
 tax
 pla
 ora PhaseIndex,x
 tay
 lda Choice,y
 cmp MmSlot
 bne Skip
 pla
 tax
 pla
 plp
 ldy MmBulletType,x
 lda MmBulletAge,x
 rts
Skip:
 pla
 pla
 plp
 tax ; A is live across the old zero-type path; X is reloaded at Next.
 pla ; discard only this helper's genuine inner JSR return address
 pla
 txa
 ldy #0
 jmp ProtoLegacyDrawShotsCold::Next
PhaseIndex:.byte 0,1,2,0,3,1,0,2,1,3
Choice:
 .byte 0,0,0,0,0,0,0,0,1,1,1,1,0,1,1,1,2,2,2,2,0,0,2,2,2,1,2,2,0,1,2,2,3,3,3,3,0,0,0,3,3,1,1,3,0,1,1,3,3,3,2,3,0,0,2,3,3,1,2,3,0,1,2,3
.endproc
.popseg
