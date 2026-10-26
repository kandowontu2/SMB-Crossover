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
  lda MmBulletAge,x
  lsr
  sta MmTemp
  lda ShotLengths-1,y
  sta MmDamage
  lda MmTemp
Modulo:
  cmp MmDamage
  bcc PhaseReady
  ; Keep the zero-remainder admission and all original entry addresses.
  ; Only positive remainders need the cold type-one specialization.
  jmp MmBasicRemainderCold
  .res 3,$ea
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

; Source-exact basic-shot remainder shortcut; no projectile update is omitted.
.pushseg
.segment "MM_BASIC_REMAINDER"
.proc MmBasicRemainderCold
  ; Y is the legal live type1..6. The resident CMP has already set C=1.
  cpy #1
  beq Basic
  ; CPY leaves C=1 for every other legal type, preserving the original SBC.
  sbc MmDamage
Loop:
  cmp MmDamage
  bcc Ready
  sbc MmDamage
  jmp Loop
Basic:
  lda #0
Ready:
  jmp ProtoLegacyDrawShotsCold::PhaseReady
.endproc
.assert *-MmBasicRemainderCold=23,error,"Basic remainder helper span"
.popseg
