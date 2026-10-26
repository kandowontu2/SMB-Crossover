; Included in the reclaimed Samus adapter padding. All prior fixed PCs remain.
::TnAudioDispatch:
 ; Both actual destinations overwrite A/N/Z and C before reading them.
 ; LDA/CMP preserve V/D/I; no entry register save is live on either path.
 lda a:SelectedCharacter
 cmp #19
 bne TnAudioLegacy
 lda #$bf                      ; Native engine A000 bank63.
 sta $5115
 lda #$fd                      ; Adapter C000 bank7D.
 sta a:CurrentBankC
 sta $5116
 jmp TnAudioUpdate
 .res 4,$ea                    ; Unreachable padding preserves real labels.
::TnAudioLegacy:
 jmp LmNativeMusicGate
 .res 2,$ea                    ; Keep every following owned entry fixed too.

::TnMusicInitCall:
 lda #$e3                      ; Original note data C000 bank7C.
 sta a:CurrentBankC
 sta $5116
 lda a:TnAudioSong
 sec
 sbc #1
 ldx #0
 ldy #0
 jsr TnNativeInit
 jmp TnMusicCallReturn
::TnMusicPlayCall:
 lda #$e3
 sta a:CurrentBankC
 sta $5116
 jsr TnNativePlay
::TnMusicCallReturn:
 lda #$fd
 sta a:CurrentBankC
 sta $5116
 rts
::TnAudioAdapterReturn:
 lda #.bank(ExpandedAudioTick)|MMC5_PRG_ROM
 sta a:CurrentBankC
 sta $5116
 rts

::TnDmcEndedGate:
 php
 lda a:SelectedCharacter
 eor #19
 bne TnDmcLegacyEnd
 lda a:BassDmcActive
 eor #4
 bne TnDmcLegacyEnd
 lda #44
 sta a:TnAudioDacHold
 lda #0
 sta a:BassDmcActive ; completion holds DAC, unlike an explicit owner stop
 plp
 rts
::TnDmcLegacyEnd:
 plp
 jmp Cv3DmcEndedGate

::TnAudioInitGate:
 ; Replaces the original five-byte LDA/STA pair in AudioInit.
 lda #0
 sta a:TnDmcDrain
 sta a:PauseModeFlag
 rts

::TnAudioGlobalGate:
 ; Replaces AudioUpdate's first LDA OperMode, once per audio update. Guest,
 ; Mario and title paths all pass here. EOR/loads preserve incoming C/V.
 lda a:TnDmcDrain
 beq TnAudioCheckOwner
 lda #0
 sta a:TnDmcDrain
 ; A new guest can start its own sample later in the previous update. Its
 ; live owner takes precedence over this old native drum's delayed reset.
 lda a:BassDmcActive
 bne TnAudioCheckOwner
 lda #0
 sta $4011
::TnAudioCheckOwner:
 lda a:XgAudioCharacter
 eor #$fd
 bne TnAudioGateReturn
 lda a:OperMode
 beq TnAudioStop
 lda a:SelectedCharacter
 eor #19
 beq TnAudioGateReturn
::TnAudioStop:
 lda a:BassDmcActive
 beq TnStopOwned
 eor #4
 bne TnForgetOldMusic
::TnStopOwned:
 ; Disabling DMA does not clear the last buffered byte. Reset its held DAC
 ; now and again next update, after those final bits have completed.
 lda #0
 jsr Cv3DmcOwnerWrite
 sta a:TnAudioDacHold
 lda a:GuestCombinedEnable
 and #15
 sta a:GuestCombinedEnable
 sta $4015
 lda #0
 sta $4011
 lda #1
 sta a:TnDmcDrain
::TnForgetOldMusic:
 lda #$ff
 sta a:XgAudioCharacter
::TnAudioGateReturn:
 lda a:OperMode
 rts
.export TnAudioDispatch,TnMusicInitCall,TnMusicPlayCall,TnMusicCallReturn,TnAudioAdapterReturn,TnDmcEndedGate,TnAudioInitGate,TnAudioGlobalGate


::TnDmcOwnerAdmission:
 php
 pha
 cmp #4
 bne TnAdmissionCheckOld
 lda #0
 sta a:TnDmcDrain
::TnAdmissionCheckOld:
 lda a:BassDmcActive
 eor #4
 bne TnAdmissionStore
 pla
 pha
 cmp #4
 beq TnAdmissionStore
 lda a:GuestCombinedEnable
 and #15
 sta $4015
 lda #0
 sta a:TnAudioDacHold
 pla
 pha
 bne TnAdmissionNewOwner
 lda #1
 bne TnAdmissionDrain
::TnAdmissionNewOwner:
 lda #0
::TnAdmissionDrain:
 sta a:TnDmcDrain
::TnAdmissionStore:
 pla
 sta a:BassDmcActive
 plp
 rts
.export TnDmcOwnerAdmission
