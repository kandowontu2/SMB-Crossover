; Included in the reclaimed Samus adapter padding. All prior fixed PCs remain.
::TnAudioDispatch:
 lda a:SelectedCharacter
 cmp #19
 bne TnAudioLegacy
 lda #$fb                      ; Native engine A000 bank7B.
 sta $5115
 lda #$fd                      ; Adapter C000 bank7D.
 sta a:CurrentBankC
 sta $5116
 jmp TnAudioUpdate
::TnAudioLegacy:
 jmp ExpandedAudioTick

::TnMusicInitCall:
 lda #$fc                      ; Original note data C000 bank7C.
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
 lda #$fc
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

::TnDmcEnded:
 ; The common entry already saved its incoming A. EOR/loads preserve C/V.
 lda a:SelectedCharacter
 eor #19
 bne TnDmcLegacyEnd
 lda a:BassDmcActive
 eor #4
 bne TnDmcLegacyEnd
 lda #44                       ; Original129-byte drum holds its final DAC.
 sta a:TnAudioDacHold
 lda #0
 sta a:BassDmcActive
 jmp DmcOff
::TnDmcLegacyEnd:
 lda #0
 sta a:BassDmcActive
 sta $4011
 jmp DmcOff

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
 ; Disabling DMA does not clear the last buffered byte. Reset its held DAC
 ; now and again next update, after those final bits have completed.
 lda #0
 sta a:BassDmcActive
 sta a:TnAudioDacHold
 lda a:GuestCombinedEnable
 and #15
 sta a:GuestCombinedEnable
 sta $4015
 lda #0
 sta $4011
 lda #1
 sta a:TnDmcDrain
 lda #$ff
 sta a:XgAudioCharacter
::TnAudioGateReturn:
 lda a:OperMode
 rts
.export TnAudioDispatch,TnMusicInitCall,TnMusicPlayCall,TnMusicCallReturn,TnAudioAdapterReturn,TnDmcEnded,TnAudioInitGate,TnAudioGlobalGate

; Exact-ID foreground admissions avoid walking through unrelated alternate
; dispatchers. Other identities retain the original entry and input A/P.
::TnFastGraphicsGate:
 php
 pha
 lda a:SelectedCharacter
 cmp #19
 bne TnFastGraphicsLegacy
 pla
 plp
 farcall TnGraphics,jmp
::TnFastGraphicsLegacy:
 pla
 plp
 farcall RlGraphicsDispatch,jmp

::TnFastSpecialGate:
 php
 pha
 lda a:SelectedCharacter
 cmp #19
 bne TnFastSpecialLegacy
 pla
 plp
 farcall TnSpecialDrawDispatch,jmp
::TnFastSpecialLegacy:
 pla
 plp
 farcall RlSpecialDrawDispatch,jmp

::TnFastDrawGate:
 lda a:SelectedCharacter
 cmp #19
 bne TnFastDrawLegacy
 cmp #CHARACTER_KIRBY          ; Same native A/N/Z/C as the old outer gate.
 farcall TnDraw,jmp
::TnFastDrawLegacy:
 jmp KbDrawDispatch
.export TnFastGraphicsGate,TnFastSpecialGate,TnFastDrawGate
