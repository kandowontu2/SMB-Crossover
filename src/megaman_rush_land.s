; Rush-only Hard MegaMan source Land (MM6NSF37), using literal existing
; BassSfxLand stream. This is frame-quantized register-image playback.
; The prior music image is restored before either native music decoder runs;
; source writes/retrigger dirtiness replace only pulse2+noise after decoding.
.pushseg
.segment "CHAR_SELECT"
; Same A-bank29 as GuestAudioBegin, append after its old WATER/SELECT data.
.assert .bank(MegaManRushLandCharacterReset)=.bank(GuestAudioBegin), lderror, "Rush reset leaf must remain in the mapped GuestAudioBegin A bank"
.proc MegaManRushLandCharacterReset
  ; The old caller supplies A=0. STA preserves every incoming register/flag.
  sta BassAudioInit
  sta MmRushLandRequest
  sta MmRushLandActive
  sta MmRushLandPreviousMask
  rts
.endproc
.segment "GUEST_GFX"
.proc MegaManRushLandBeginStatus
  ; Exact one-call context: X=$36,C=1,Y unchanged,A=$0F before old status STA.
  lda MmRushLandPreviousMask
  beq Status
  ldx #15
RestoreMusic:
  lda MmRushLandMusic,x
  sta GuestNativeApu,x
  dex
  bpl RestoreMusic
  ldx #$36
  cpx #$36
Status:
  lda #$0f
  jmp GuestNativeStatusSTA
.endproc
.proc MegaManRushLandEnd
  lda MmRushLandRequest
  ora MmRushLandActive
  ora MmRushLandPreviousMask
  bne Live
Quiet:
  ; Exact displaced5B output: A=0,N=0,Z=1; all other registers/flags retained.
  lda #0
  sta MmAudioPaused
  rts
Live:
  php
  txa
  pha
  tya
  pha
  lda CurrentBank
  pha
  BankPRGA #.bank(BassSfxLand)
  jsr Decode
  pla
  BankPRGA a
  pla
  tay
  pla
  tax
  plp
  jmp Quiet
Decode:
  ldx #15
SaveMusic:
  lda GuestNativeApu,x
  sta MmRushLandMusic,x
  lda #0
  sta MmRushLandDirty,x
  dex
  bpl SaveMusic
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  jne Cancel
  lda CrossoverBehaviorVersion
  cmp #1
  jne Cancel
  lda MmDeathFlag
  jne Cancel
  ; Preserve the existing native higher-priority hurt/life/defeat owners.
  lda MmAudioSfx
  cmp #2
  beq Cancel
  cmp #3
  beq Cancel
  cmp #4
  beq Cancel
  cmp #8
  beq Cancel
  lda MmRushLandRequest
  beq Continue
  lda #0
  sta MmRushLandRequest
  sta MmRushLandIndex
  lda #1
  sta MmRushLandActive
Continue:
  lda MmRushLandActive
  beq Release
  ldy MmRushLandIndex
Read:
  lda BassSfxLand,y
  iny
  cmp #254
  beq FrameDone
  cmp #255
  beq Cancel
  tax
  lda BassSfxLand,y
  iny
  sta MmRushLandImage,x
  lda #1
  sta MmRushLandDirty,x
  bne Read
FrameDone:
  sty MmRushLandIndex
  ldx #15
Mix:
  txa
  and #$0c
  cmp #4
  beq Owned
  cmp #12
  bne Next
Owned:
  lda MmRushLandImage,x
  sta GuestNativeApu,x
  lda MmRushLandDirty,x
  sta GuestNativeDirty,x
  lda MmRushLandPreviousMask
  bne Next
  lda #1
  sta GuestNativeDirty,x
Next:
  dex
  bpl Mix
  lda #10
  sta MmRushLandPreviousMask
  rts
Cancel:
  lda #0
  sta MmRushLandRequest
  sta MmRushLandActive
Release:
  lda MmRushLandPreviousMask
  beq Done
  ldx #15
ReleaseLoop:
  txa
  and #$0c
  cmp #4
  beq Reload
  cmp #12
  bne NextRelease
Reload:
  lda #1
  sta GuestNativeDirty,x
NextRelease:
  dex
  bpl ReleaseLoop
  lda #0
  sta MmRushLandPreviousMask
Done:
  rts
.endproc
.popseg
