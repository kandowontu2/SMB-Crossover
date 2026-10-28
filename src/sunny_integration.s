; ROOT-admission adapter; frozen sunny.s/source art stay unchanged.
.pushseg
.segment "SUNNY_CORE"
SunnyNativePaletteBits=$5c05
.proc SunnyInjuryIntegrated
 jsr SunnyInjuryStart
 sec                           ; genuine ForceInjury handled-result contract
 rts
.endproc
.proc SunnyCollectIntegrated
 phx
 jsr EraseEnemyObject
 lda #6
 jsr SetupFloateyNumber
 lda #Sfx_PowerUpGrab
 sta Square2SoundQueue
 lda PowerUpType,x
 cmp #2
 bcs Native
 jsr SunnyBeginPickup
 plx
 rts
Native:
 cmp #3
 beq Life
 lda #$23
 sta StarInvincibleTimer
 lda #StarPowerMusic
 sta AreaMusicQueue
 plx
 rts
Life:
 lda #$0b
 sta FloateyNum_Control,x
 plx
 rts
.endproc
.proc SunnyGraphicsIntegrated
 jsr SunnyEnsure
 lda Player_SprAttrib
 and #3
 sta SunnyNativePaletteBits
 jsr SunnyGraphics
 php
 pha
 phx
 phy
 lda StarInvincibleTimer
 beq Palette
 lda Player_SprAttrib
 ora SunnyNativePaletteBits
 sta Player_SprAttrib
 jmp Done
Palette:jsr SunnyIntegrationPalette
Done:ply
 plx
 pla
 plp
 rts
.endproc
.proc SunnyColorsIntegrated
 lda #$ff
 sta SunnyPalette
 ; Native star cycles sprite palette attributes; don't recolor its owners.
 lda StarInvincibleTimer
 bne Done
 jmp SunnyIntegrationPalette
Done:rts
.endproc
.proc SunnyIntegrationPalette
 ; Unlike the frozen art leaf, this integration owns transform colors too:
 ; use genuine GuestPowerupDisplay; never temporarily clear active flags.
 jsr SunnyVisualForm
 cmp #2
 lda #0
 rol
 cmp SunnyPalette
 beq Done
 pha
 ldx VRAM_Buffer1_Offset
 cpx #78
 bcs Full
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$11
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 lda #4
 sta VRAM_Buffer1+3,x
 jsr SunnyVisualForm
 cmp #2
 lda #$26
 bcc Color
 lda #$2a
Color:sta VRAM_Buffer1+4,x
 lda #$36
 sta VRAM_Buffer1+5,x
 txa
 clc
 adc #6
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 pla
 sta SunnyPalette
 rts
Full:pla
Done:rts
.endproc
.assert * <= $b700,lderror,"Sunny code must not overlap relocated menu names"
.popseg
