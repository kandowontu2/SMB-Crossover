; Hosted power-ups freeze the world for 1000 ms, hold the current pose,
; cycle replacement colors, and swap character power states at 100 ms.
.pushseg
.segment "SRAM"
GuestPowerupActive: .res 1
GuestPowerupAge: .res 1
GuestPowerupOld: .res 1
GuestPowerupTarget: .res 1
GuestPowerupDisplay: .res 1
GuestPowerupPose: .res 1
GuestPowerupPhase: .res 1
GuestPowerupColor: .res 1
.segment "SAMUS"
.proc GuestClearPowerup
  lda #0
  sta GuestPowerupActive
  sta GuestPowerupAge
  sta GuestLegacyHurt
  jmp RosterClearState
.endproc
.segment "FIXED"
.proc GuestVisualStatus
  lda GuestPowerupActive
  beq Normal
  lda GuestPowerupDisplay
  rts
Normal:
  farcall RemainingPower
  rts
.endproc
.segment "SAMUS"
.proc GuestBeginPowerup
  lda PlayerStatus
  cmp #2
  bcs Done
  sta GuestPowerupOld
  sta GuestPowerupDisplay
  clc
  adc #1
  sta GuestPowerupTarget
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bcc :+
    lda RgPose
    jmp Pose
  :
  cmp #CHARACTER_MEGAMAN
  bne Samus
  farcall MegaManPowerupCharge
  lda MmRenderPose
  jmp Pose
Samus:
  lda SmPose
Pose:
  sta GuestPowerupPose
  lda #1
  sta GuestPowerupActive
  lda #0
  sta GuestPowerupAge
  sta PlayerChangeSizeFlag
  lda #$ff
  sta TimerControl
  lda #9
  sta GameEngineSubroutine
Done:
  rts
.endproc
.proc GuestPowerupUpdate
  lda GuestPowerupActive
  beq Done
  ; Source global animation timers continue during the1000ms freeze. The
  ; player clip remains frozen; ordinary pause never dispatches this update.
  lda CrossoverBehaviorVersion
  bne NativeFreezePhase
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne NativeFreezePhase
  inc RgClock
  lda RgClock
  cmp #36
  bcc NativeFreezePhase
  lda #0
  sta RgClock
NativeFreezePhase:
  inc GuestPowerupAge
  lda GuestPowerupAge
  cmp #60
  bcs Finish
  lda #$ff
  sta TimerControl
  lda GuestPowerupOld
  sta GuestPowerupDisplay
  lda GuestLegacyHurt
  cmp #1
  beq Swap                    ;Old injury alternates both power forms at10Hz.
  ; Mega Man swaps hair/helmet on the first upgrade. Samus swaps
  ; long/wave forms on the flower. Both also cycle their own colors.
  lda SelectedCharacter
  cmp #CHARACTER_LUIGI
  beq Swap
  cmp #CHARACTER_MEGAMAN
  bne Samus
  lda GuestPowerupOld
  bne Done
  jmp Swap
Samus:
  lda GuestPowerupOld
  beq Done
Swap:
  lda GuestPowerupAge
  ldx #0
Divide:
  cmp #6
  bcc Phase
  sbc #6
  inx
  jmp Divide
Phase:
  txa
  and #1
  beq Done
  lda GuestPowerupTarget
  sta GuestPowerupDisplay
Done:
  rts
Finish:
  lda GuestPowerupTarget
  sta PlayerStatus
  lda #0
  sta GuestPowerupActive
  sta TimerControl
  sta PlayerChangeSizeFlag
  sta PlayerSize
  sta MmLastPalette
  lda #8
  sta GameEngineSubroutine
  farcall GetPlayerColors
  rts
.endproc
.proc GuestPowerupPalette
  lda GuestLegacyHurt
  cmp #1
  jeq Original                ;Damage swaps tiers without power-up rainbow.
  lda GuestPowerupAge
  ldx SelectedCharacter
  cpx #CHARACTER_MEGAMAN
  bne Slow
  lsr                            ; Mega Man: 30 Hz color replacement.
  jmp Phase
Slow:
  ldx #0                         ; Samus: 10 Hz color replacement.
Divide:
  cmp #6
  bcc SlowPhase
  sbc #6
  inx
  jmp Divide
SlowPhase:
  txa
Phase:
  and #3
  sta GuestPowerupPhase
  beq Original
  sec
  sbc #1
  sta GuestPowerupColor
  asl
  clc
  adc GuestPowerupColor
  ldx SelectedCharacter
  cpx #CHARACTER_MEGAMAN
  beq Index
  clc
  adc #9
  jmp Index
Original:
  jsr GuestVisualStatus
  sta GuestPowerupColor
  asl
  clc
  adc GuestPowerupColor
  clc
  adc #18
  ldx SelectedCharacter
  cpx #CHARACTER_MEGAMAN
  beq Index
  cpx #CHARACTER_BILL
  bne OriginalRoster
  ldy BillVariant
  beq OriginalRoster
  clc
  adc #108                       ; Lance follows Scrooge in the color table.
  jmp Index
OriginalRoster:
  sta GuestPowerupColor
  txa
  sec
  sbc #1
  sta GuestPowerupPhase
  asl
  asl
  asl
  clc
  adc GuestPowerupPhase
  clc
  adc GuestPowerupColor
  jmp Index
Index:
  tay
  ldx VRAM_Buffer1_Offset
  cpx #$40
  bcs Done
  lda #$3f
  sta VRAM_Buffer1,x
  lda #$11
  sta VRAM_Buffer1+1,x
  lda #3
  sta VRAM_Buffer1+2,x
  lda Colors,y
  sta VRAM_Buffer1+3,x
  lda Colors+1,y
  sta VRAM_Buffer1+4,x
  lda Colors+2,y
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
Colors:
  .byte $06,$27,$38, $0a,$16,$30, $0c,$24,$34 ; Mega Man's flash colors
  .byte $1a,$27,$30, $16,$27,$30, $0f,$24,$30 ; Samus's shared star colors
  .byte $0f,$11,$2c, $0f,$11,$2c, $0f,$16,$28 ; Mega Man's base forms
  .byte $16,$1a,$27, $16,$1a,$36, $15,$2a,$34 ; Samus's base forms
  .byte $12,$36,$0f, $11,$36,$0f, $16,$36,$0f ; Bill: pants, skin, black
  .byte $29,$17,$27, $2c,$17,$27, $16,$17,$27 ; Link: tunic, brown, skin
  .byte $07,$27,$37, $06,$27,$37, $0f,$16,$30 ; Simon: leather, armor, flame
  .byte $07,$26,$30, $07,$27,$30, $07,$36,$30 ; Pit
  .byte $16,$30,$0f, $26,$30,$0f, $28,$30,$0f ; Rygar
  .byte $1a,$27,$17, $1a,$27,$17, $30,$27,$16 ; Luigi
  .byte $0f,$27,$00, $0f,$27,$00, $0f,$27,$00 ; Bass buster suit
  .byte $22,$07,$36, $22,$07,$36, $22,$07,$36 ; Ryu inventory upgrades retain the skin palette
  .byte $15,$30,$0f, $15,$30,$0f, $15,$30,$0f ; Sophia inventory upgrades retain the skin palette
  .byte $0f,$30,$16, $0f,$30,$16, $0f,$30,$16 ; Scrooge
  .byte $1c,$36,$0f, $1c,$36,$0f, $1c,$36,$0f ; Lance skin retains source suit colors.
.endproc
.popseg
