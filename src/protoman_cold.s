; Private expanded-MMC5 presentation. MegaMan remains family/inventory owner1.
; ProtoVariant/ProtoAudioState are early fixed aliases; no SRAM layout change.
.include "protoman_pose_ids.inc"
.pushseg
.segment "PROTO_COLD"

.proc ProtoGlobalInit
  farcall X5InventoryInit
  lda #0
  sta ProtoVariant
  sta ProtoAudioState
  rts
.endproc

; NMI-only. Caller explicitly mapped this A bank without shared farcall SMC.
; Native wrapper saves/restores the A-window itself. Preserve actual C hardware
; and its shadow together before returning to the original C-wrapper dispatcher.
.proc ProtoNmiAudioCore
  ; Resident14B entry mapped A hardware only; its old shadow is our return bank.
  lda CurrentBank
  pha
  lda #.bank(ProtoNmiAudioCore) | MMC5_PRG_ROM
  sta CurrentBank
  lda CurrentBankC
  pha
  lda ProtoVariant
  beq Original
  BankPRGC #.bank(ProtoNativeAudioUpdate)
  jsr ProtoNativeAudioUpdate
  jmp Restore
Original:
  BankPRGC #.bank(MegaManAudioNativeUpdate)
  jsr MegaManAudioNativeUpdate
Restore:
  pla
  BankPRGC a
  pla
  sta CurrentBank
  ; Caller immediately publishes A to5115 from resident code.
  rts
.endproc

.proc ProtoMenuPrepare
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  bne Legacy
  lda ProtoVariant
  bne Done
Legacy:
  lda X5WideChrActive
  beq Done
  farcall X5ClearChrModes
Done:
  rts
.endproc

.proc ProtoPoseSelector
  lda ProtoVariant
  bne Proto
  farcall SpecialMegaPose,jmp
Proto:
  lda ObjectMetasprite
  jeq Done
  lda MmDeathFlag
  jne Done
  ldx MmRenderPose
  cpx #16
  bcc :+
    ldx #PROTO_POSE_STAND
  :
  lda GuestPowerupActive
  jne Pointer
  lda GuestHurtTicks
  beq NotHurt
    ldx #PROTO_POSE_HURT
    bne Pointer
NotHurt:
  lda GameEngineSubroutine
  cmp #8
  jne Pointer
  lda SsHeld
  beq Attack
    ldx #PROTO_POSE_CARRY
    lda Player_State
    beq GroundCarry
      ldx #PROTO_POSE_CARRY_JUMP
      jmp Pointer
GroundCarry:
    lda MmStepTimer
    beq :+
      ldx #PROTO_POSE_CARRY_STEP
      jmp Pointer
    :
    lda Player_X_Speed
    jeq Pointer
    lda MmWalkFrame
    cmp #3
    bcc :+
      lda #1
    :
    clc
    adc #PROTO_POSE_CARRY_WALK1
    tax
    jmp Pointer
Attack:
  lda MegaManShotPose
  beq Step
  lda InvSelected+CHARACTER_MEGAMAN
  beq Step
  cmp #5
  bcs Step
    ldx #PROTO_POSE_THROW
    lda Player_State
    beq :+
      ldx #PROTO_POSE_AIR_THROW
    :
    lda InvSelected+CHARACTER_MEGAMAN
    cmp #3
    bne Pointer
    ldx #PROTO_POSE_FIST
    lda Player_State
    beq Pointer
    ldx #PROTO_POSE_AIR_FIST
    bne Pointer
Step:
  cpx #PROTO_POSE_STAND
  bne Pointer
  lda MmStepTimer
  beq Pointer
    ldx #PROTO_POSE_STEP
Pointer:
  jsr ProtoSetPose
  jsr ProtoFixQueuedPalette
Done:
  rts
.endproc

; X=private pose. C-window is left owning these immutable tables for rendering.
.proc ProtoSetPose
  BankPRGC #.bank(ProtoArtBegin)
  lda ProtoPoseChrLo,x
  sta SmChrBank
  lda PlayerFacingDir
  cmp #2
  beq Left
  lda ProtoPoseRightLo,x
  sta SmPosePtr
  lda ProtoPoseRightHi,x
  jmp Ready
Left:
  lda ProtoPoseLeftLo,x
  sta SmPosePtr
  lda ProtoPoseLeftHi,x
Ready:
  sta SmPosePtr+1
  lda #METASPRITE_SAMUS_BODY
  sta ObjectMetasprite
  rts
.endproc

.proc ProtoPortrait
  jsr CrossoverGraphicsBank
  lda PlayerStatus
  asl
  asl
  asl
  asl
  clc
  adc #METASPRITE_MM_HAIR_STAND
  sta ObjectMetasprite
  lda PlayerStatus
  asl
  asl
  asl
  asl
  clc
  adc #$40
  sta PlayerChrBank
  inc ReloadCHRBank
  lda ProtoVariant
  beq Done
  ldx #PROTO_POSE_STAND
  jsr ProtoSetPose
  jsr ProtoPublishBody
  jsr ProtoQueueBasePalette
Done:
  rts
.endproc

; Called from the outlined DrawShots entry before world/player OAM allocation.
.proc ProtoDrawShots
  BankPRGC #.bank(MmMM_HAIR_STANDRight)
  jsr ProtoLegacyDrawShotsCold
  lda ProtoVariant
  beq Done
  lda MmDeathFlag
  beq Alive
    lda #0
    sta X5ChrMode
    sta X5WideChrActive
    inc ReloadCHRBank
    rts
Alive:
  BankPRGC #.bank(ProtoArtBegin)
  ; Invisible injury frames still draw the original white injury glyphs.
  lda GuestHurtTicks
  beq Ordinary
    lda #.lobyte(PROTO_CHR_FIRST+PROTO_HURT_BANK_OFFSET)
    sta SmChrBank
    lda #.hibyte(PROTO_CHR_FIRST+PROTO_HURT_BANK_OFFSET)
    tax
    jmp Publish
Ordinary:
  ; Body's selected physical low byte is cached in existing presentation RAM.
  ; All20 pages in this assigned family lie in the same256-page CHR quarter.
  ldx #.hibyte(PROTO_CHR_FIRST)
Publish:
  lda SmChrBank
  ldy #0
  farcall X5SetPhysicalChr
Done:
  rts
.endproc

.proc ProtoPublishBody
  lda SmChrBank
  ldx #.hibyte(PROTO_CHR_FIRST)
  ldy #0
  farcall X5SetPhysicalChr,jmp
.endproc

; Source base colors black/red/gray; face/white share stable world palettes.
.proc ProtoQueueBasePalette
  ldx VRAM_Buffer1_Offset
  cpx #$4e                      ; Six command bytes plus terminator fit 84 bytes.
  bcs Done
  lda #$3f
  sta VRAM_Buffer1,x
  lda #$11
  sta VRAM_Buffer1+1,x
  lda #3
  sta VRAM_Buffer1+2,x
  lda #$0f
  sta VRAM_Buffer1+3,x
  lda #$16
  sta VRAM_Buffer1+4,x
  lda #$10
  ldy PlayerStatus
  cpy #2
  bne :+
    lda #$28
  :
  sta VRAM_Buffer1+5,x
  txa
  clc
  adc #6
  tax
  stx VRAM_Buffer1_Offset
  lda #0
  sta VRAM_Buffer1,x
Done:
  rts
.endproc

; Walk complete VRAM commands. Only known player palette entries are replaced;
; no world palette, background color or selected-special suit row is touched.
.proc ProtoFixQueuedPalette
  lda InvSelected+CHARACTER_MEGAMAN
  beq Scan
  lda GuestPowerupActive
  ora StarInvincibleTimer
  beq Done
Scan:
  ldx #0
Loop:
  cpx VRAM_Buffer1_Offset
  bcs Done
  lda VRAM_Buffer1,x
  beq Done
  lda VRAM_Buffer1+2,x
  and #$40
  beq NormalLength
  lda #1
  bne LengthReady
NormalLength:
  lda VRAM_Buffer1+2,x
  and #$3f
LengthReady:
  sta R0
  txa
  clc
  adc R0
  bcs Done
  adc #3
  bcs Done
  sta R0                        ; next command index, independent of color loop
  cmp VRAM_Buffer1_Offset
  bcc :+
  bne Done
  :
  lda VRAM_Buffer1,x
  cmp #$3f
  bne Next
  lda VRAM_Buffer1+1,x
  cmp #$11
  beq Player3
  cmp #$10
  bne Next
  lda VRAM_Buffer1+2,x
  cmp #4
  bne Next
  txa
  clc
  adc #4                        ; skip universal background byte in4-byte row
  tay
  bne Convert
Player3:
  lda VRAM_Buffer1+2,x
  cmp #3
  bne Next
  txa
  clc
  adc #3
  tay
Convert:
  ldx #3
Colors:
  lda VRAM_Buffer1,y
  cmp #$11
  bne :+
    lda #$16
  :
  cmp #$2c
  bne :+
    lda #$10
  :
  sta VRAM_Buffer1,y
  iny
  dex
  bne Colors
Next:
  ldx R0
  jmp Loop
Done:
  rts
.endproc

.proc ProtoStatusName
  cmp #0
  bne Done
  pha
  txa
  pha
  lda SelectedCharacter
  cmp #CHARACTER_TMNT
  bne :+
  lda TnVariant
  clc
  adc #16
  jmp NameIndex
:
  cmp #CHARACTER_KIRBY
  bne :+
  lda KbVariant
  beq KirbyName
  lda #20
  jmp NameIndex
KirbyName:
  lda #15
  jmp NameIndex
:
  cmp #0
  beq Restore
  cmp #CHARACTER_MEGAMAN
  bne Bill
  ldx ProtoVariant
  beq NameIndex
  lda #14
  bne NameIndex
Bill:
  cmp #CHARACTER_BILL
  bne NameIndex
  ldx BillVariant
  beq NameIndex
  lda #CHARACTER_COUNT
NameIndex:
  sta R0
  asl
  asl
  asl
  sec
  sbc R0
  sta R0
  ldy #6
Copy:
  tya
  clc
  adc R0
  tax
  lda Names,x
  sta VRAM_Buffer1+11,y
  dey
  bpl Copy
Restore:
  pla
  tax
  pla
Done:
  rts
Names:
  .byte "MARIO  ","MEGAMAN","SAMUS  ","BILL   ","LINK   ","SIMON  ","PIT    "
  .byte "RYGAR  ","LUIGI  ","BASS   ","RYU    ","SOPHIA ","SCROOGE","LANCE  ","PROTO  ","KIRBY  ","LEO    ","RAPH   ","MIKE   ","DON    "
  .byte "META   "
.endproc
.popseg
