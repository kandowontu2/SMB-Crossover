; Native Bell control in parodius_bell_native.s; explicit SMB delivery below.
PnBombCapturePending=$5d7b
PnBombPaletteReady=$5d7c
PnBombPaletteShadow=MmAudioRamStart+96 ; inactive audio overlay,32 owned bytes
.export PnBombCapturePending,PnBombPaletteReady,PnBombPaletteShadow

.pushseg
.segment "PARODIUS_NMI"
.proc PnPaletteScreenUpdate
 jsr UpdateScreen
 lda SelectedCharacter
 cmp #18
 bne Samus
 lda OperMode
 cmp #1
 bne Samus
 lda VvVariant
 beq Samus
 lda PnBombCapturePending
 beq Samus
 ; Only VBlank reads the live palette. Main code never resets the PPU latch
 ; while rendering, and the exact incoming colors survive the Bell flash.
 lda Mirror_PPUCTRL
 and #$fb
 sta PPUCTRL
 bit PPUSTATUS
 lda #$3f
 sta PPUADDR
 lda #0
 sta PPUADDR
 tax
Copy:
 lda PPUDATA
 sta PnBombPaletteShadow,x
 inx
 cpx #32
 bne Copy
 lda #0
 sta PnBombCapturePending
 lda #1
 sta PnBombPaletteReady
 lda Mirror_PPUCTRL
 sta PPUCTRL
Samus:
 asl SmFreezePalettePending
 jmp SamusFreezeFlushPalette
.endproc
.popseg

.pushseg
.segment "PARODIUS_BELLS"
.proc PnBellTick
 lda VvMeter
 sta VvTempPage
 lda #16
 ldx PnBombPaletteReady
 beq Busy
 ldx VRAM_Buffer1_Offset
 cpx #49
 bcs Busy
 lda #0
Busy:sta PnNativeVramBusy
 lda ScrollAmount
 sta PnNativeScrollXHi
 lda #0
 sta PnNativeScrollXLo
 sta PnNativeScrollFlags
 jsr PnNativeBellUpdate
 lda VvMeter
 cmp VvTempPage
 beq Done
 lda #1
 sta VvHudDirty
Done:rts
.endproc
.proc PnBombPalettePrime
 lda PnNativeVramBusy
 cmp #16
 bcc Publish
 lda #1
 sta PnAux+27
 rts
Publish:
 lda #0
 sta PnAux+27
 jmp PnQueueBombPalette
.endproc
.proc PnBombPaletteAdjust
 lda PnNativeVramBusy
 cmp #16
 bcc Publish
 lda #2
 sta PnAux+27
 rts
Publish:
 lda PnAux+27
 and #$fd
 sta PnAux+27
 jmp PnQueueBombPalette
.endproc
.proc PnQueueBombPalette
 ldx VRAM_Buffer1_Offset
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$10
 sta VRAM_Buffer1+1,x
 lda #32
 sta VRAM_Buffer1+2,x
 inx
 inx
 inx
 ; Match the cartridge's sprite-first/background-last publication. $3F10
 ; aliases the universal backdrop; writing it last would cancel the flash.
 ; The second half streams through $3F20, mirroring $3F00..$3F0F.
 ldy #16
Color:
 cpy #16
 bcs Sprite
 lda PnPhase+27
 cmp #$30
 bcc Ramp
 lda #$20
 bne Store
Ramp:
 lda PnBombPaletteShadow,y
 cpy #0
 beq Store
 and #$f0
 cmp PnPhase+27
 bcs Original
 lda PnBombPaletteShadow,y
 and #$0f
 ora PnPhase+27
 jmp Store
Sprite:
 lda PnNativeStageFlags
 and #2
 beq Original
 tya
 and #3
 beq White
 lda #$0f
 bne Store
White:lda #$30
 bne Store
Original:
 lda PnBombPaletteShadow,y
Store:
 sta VRAM_Buffer1,x
 inx
 iny
 tya
 and #31
 tay
 cpy #16
 bne Color
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 ldx #27
 rts
.endproc
.proc PnBellGainLife
 lda NumberofLives
 cmp #98
 bcs Feedback
 inc NumberofLives
Feedback:
 lda NumberofLives
 sta VvLife
 lda #Sfx_ExtraLife
 sta Square2SoundQueue
 rts
.endproc
.proc PnBellBonusContact
 rts ; no unsupported contact class21 is spawned by the SMB adapter
.endproc
.proc PnGoldBellScore
 ldx PnBellStreak
 cpx #4
 bcc Increase
 ldx #4
 bne Capped
Increase:
 inc PnBellStreak
Capped:
 txa
 pha
 lda Hundreds,x
 sta DigitModifier+PlayerScoreLastIndex-2
 lda Thousands,x
 sta DigitModifier+PlayerScoreLastIndex-3
 lda TenThousands,x
 sta DigitModifier+PlayerScoreLastIndex-4
 farcall AddToScore
 pla
 clc
 adc #11
 ldx VvSlot
 sta PnCapActive,x
 lda #40                      ; original $949A floating score lifetime
 sta PnCapAge,x
 rts
Hundreds:.byte 5,0,5,0,0
Thousands:.byte 0,1,2,5,0
TenThousands:.byte 0,0,0,0,1
.endproc
.proc PnPickupFrame
 ; A = physical pickup kind; Y = native-update animation age.
 ; Native capsule alternates every6 updates; Bell every9.
 sta VvTemp2
 tya
 sta VvTemp
 lda VvTemp2
 cmp #11
 bcs Score
 cmp #6
 bcs Bell
 lda VvTemp
Modulo:
 cmp #12
 bcc Capsule
 sec
 sbc #12
 bcs Modulo
Capsule:
 cmp #6
 lda #241
 adc #0
 rts
Score:
 clc
 adc #240
 rts
Bell:
 cmp #8
 bne Ordinary
 ; Original $94C4 flashes through blue, yellow, red, yellow using
 ; the native animation delay8..0 rather than changing world palettes.
 lda VvTemp
 cmp #9
 bcc Delay
 sbc #9
Delay:
 sta VvTemp2
 lda #8
 sec
 sbc VvTemp2
 and #3
 tax
 lda BigColors,x
 bne Pose
Ordinary:
 sec
 sbc #6
 tax
 lda BellFrames,x
Pose:
 ldy VvTemp
 cpy #9
 adc #0
 rts
BellFrames:.byte 243,245,243,247,249
BigColors:.byte 245,243,247,243
.endproc
.proc PnBombWorldDamage
 farcall PnBombEnemyDamage,jmp
.endproc
.popseg

.pushseg
.segment "VIC_WORLD"
.proc PnBombEnemyDamage
 lda ObjectOffset
 pha
 lda #5
 sta VvEnemySlot
Enemy:
 ldx VvEnemySlot
 lda Enemy_Flag,x
 beq Next
 bmi Next
 lda Enemy_State,x
 and #$20
 bne Next
 lda Enemy_ID,x
 cmp #Bowser
 beq Boss
 cmp #BulletBill_CannonVar
 beq Ordinary
 cmp #$15
 bcs Next
 cmp #Podoboo
 beq Next
Ordinary:
 stx ObjectOffset
 jsr PnDropForEnemy
 ldx VvEnemySlot
 jsr ShellOrBlockDefeat
 jmp Next
Boss:
 lda PnWorldContacts::EnemyBits,x
 and PnHitMask+27
 bne Next
 lda PnWorldContacts::EnemyBits,x
 ora PnHitMask+27
 sta PnHitMask+27
 stx ObjectOffset
 stx R1
 jsr HandleEnemyFBallCol
Next:
 dec VvEnemySlot
 bpl Enemy
 pla
 sta ObjectOffset
 rts
.endproc
.popseg
