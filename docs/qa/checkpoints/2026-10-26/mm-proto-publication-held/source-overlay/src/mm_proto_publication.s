; One new explicitly declared lifecycle owner; never borrow audio/OAM scratch.
MmPublicationState=$5ff8
.export MmPublicationState
.pushseg
.segment "MM_PUBLICATION_COLD"
.proc MmPublicationAudioCore
  ; This real core is reached only by Mega/Proto AudioUpdate. The outer
  ; regularNMI return word lies atSP+5; savedP/X move it toSP+7/+8.
  ; Main cannot mutate page2 while NMI owns this acknowledged transfer.
  php
  bit MmPublicationState
  bpl NoPending
  phx
  tsx
  lda $0107,x
  cmp #<(MmPublicationRegularAudioCall+2)
  bne RestoreX
  lda $0108,x
  cmp #>(MmPublicationRegularAudioCall+2)
  bne RestoreX
  lda OperMode
  cmp #1
  bne Invalidate
  lda OperMode_Task
  cmp #3
  bne Invalidate
  lda GameEngineSubroutine
  cmp #8
  bne Invalidate
  lda MmDeathFlag
  bne Invalidate
  lda MmPublicationState
  eor #$c0                    ; pending80->desired40; pendingC0->desired0.
  sta MmPublicationState
  jmp RestoreX
Invalidate:
  lda #0                      ; scene/death replacement cannot consume a turn.
  sta MmPublicationState
RestoreX:
  plx
NoPending:
  plp
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
.assert *<=$bb50,error,"Publication cold code overlaps pinned menuBB50"
.popseg
