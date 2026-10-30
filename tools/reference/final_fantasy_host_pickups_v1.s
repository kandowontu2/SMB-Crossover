; Native mature-item consumption plus the frozen FF progression API.
; Hosted60-update freeze uses the existing game's exact BeginFreeze sequence.
.setcpu "6502"
.macpack longbranch
.import SelectedCharacter,GamePauseStatus,TimerControl,MmDeathFlag
.import GuestPowerupOld,GuestPowerupDisplay,GuestPowerupTarget,GuestPowerupPose
.import GuestPowerupActive,GuestPowerupAge,GuestLegacyHurt,PlayerStatus,PlayerSize
.import ObjectMetasprite,PlayerChangeSizeFlag,MegaManShotPose,FireballThrowingTimer
.import Square2SoundQueue,StarInvincibleTimer,AreaMusicQueue,FloateyNum_Control
.import MmLastPalette,EraseEnemyObject,SetupFloateyNumber
.importzp Enemy_Flag,Enemy_ID,Enemy_State,ObjectOffset,GameEngineSubroutine,PowerUpType
.importzp PowerUpObject,Sfx_PowerUpGrab,StarPowerMusic
.import FfEnsure,FfPickup,FfPower,FfPaletteAck,FfGraphics
.export FfHostCollect,FfHostPowerupTick,FfHostGraphics
.export FfHostBeginFreeze,FfHostBeginFreezeEnd,FfHostPickupsBegin,FfHostPickupsEnd
.segment "FF_HOST_PICKUPS"
FfHostPickupsBegin:

.proc FfHostCollect
 lda SelectedCharacter
 cmp #22
 jne No
 lda GameEngineSubroutine
 cmp #8
 jne No
 lda GamePauseStatus
 and #1
 jne No
 lda TimerControl
 ora MmDeathFlag
 jne No
 cpx #6
 jcs No
 lda Enemy_Flag,x
 jeq No
 jmi No
 lda Enemy_ID,x
 cmp #PowerUpObject
 jne No
 lda Enemy_State,x
 jpl No                       ; Native rising items are not collectible yet.
 lda PowerUpType,x
 cmp #4
 jcs No
 lda ObjectOffset
 pha
 txa
 pha
 stx ObjectOffset
 jsr FfEnsure
 pla
 tax
 txa
 pha                          ; Actual native actor survives all source calls.
 lda PowerUpType,x
 cmp #2
 bcs Effects
 lda FfPower
 sta GuestPowerupOld
 sta GuestPowerupDisplay
Effects:
 lda PowerUpType,x
 pha
 jsr EraseEnemyObject
 lda #6
 jsr SetupFloateyNumber
 pla
 cmp #2
 bcs NativeItem
 jsr FfPickup                 ; Exact tier/earned/WhiteMage charges and SFX.
 lda FfPower
 sta GuestPowerupTarget
 lda #0
 sta GuestLegacyHurt
 jsr FfHostBeginFreeze
 jmp Done
NativeItem:
 cmp #3
 beq Life
 lda #$23
 sta StarInvincibleTimer
 lda #StarPowerMusic
 sta AreaMusicQueue
 jmp NativeSound
Life:
 pla
 tax
 txa
 pha
 lda #$0b
 sta FloateyNum_Control,x
NativeSound:
 lda #Sfx_PowerUpGrab
 sta Square2SoundQueue
Done:
 pla
 tax
 pla
 sta ObjectOffset
 sec
 rts
No:clc
 rts
.endproc

; Byte-exact clone of the genuine host MarioSourceBeginFreeze. Placement in
; the FF-owned execution image avoids a foreign-A near call or a new gateway.
.proc FfHostBeginFreeze
 lda ObjectMetasprite
 sta GuestPowerupPose
 lda #0
 sta GuestPowerupAge
 sta PlayerChangeSizeFlag
 sta MegaManShotPose
 sta FireballThrowingTimer
 lda #1
 sta GuestPowerupActive
 lda #$ff
 sta TimerControl
 lda #9
 sta GameEngineSubroutine
 rts
.endproc
FfHostBeginFreezeEnd:

; Same native60-update hosted progression for this typed FF owner. The real
; source gear remains acquired; the graphics wrapper chooses the display tier.
; Source palette compositor observes dirty Ack instead of a foreign near call.
.proc FfHostPowerupTick
 lda SelectedCharacter
 cmp #22
 bne Done
 lda GameEngineSubroutine
 cmp #9
 bne Done
 lda GamePauseStatus
 and #1
 bne Done
 lda GuestPowerupActive
 beq Done
 inc GuestPowerupAge
 lda GuestPowerupAge
 cmp #60
 bcs Finish
 lda #$ff
 sta TimerControl
 lda GuestPowerupOld
 sta GuestPowerupDisplay
 beq Done
 lda GuestPowerupAge
 ldx #0
Divide:cmp #6
 bcc Phase
 sbc #6
 inx
 bne Divide
Phase:txa
 and #1
 beq Done
 lda GuestPowerupTarget
 sta GuestPowerupDisplay
Done:rts
Finish:
 lda GuestPowerupTarget
 sta GuestPowerupDisplay
 sta PlayerStatus
 lda #0
 sta GuestPowerupActive
 sta TimerControl
 sta PlayerChangeSizeFlag
 sta PlayerSize
 sta MmLastPalette
 lda #$ff
 sta FfPaletteAck
 lda #8
 sta GameEngineSubroutine
 rts
.endproc

; Actual source body/pose selection with a temporary visual-tier input.
; This restores acquired power before returning and never runs movement.
.proc FfHostGraphics
 jsr FfEnsure
 lda GuestPowerupActive
 beq Native
 lda FfPower
 pha
 lda GuestPowerupDisplay
 sta FfPower
 jsr FfGraphics
 pla
 sta FfPower
 lda ObjectMetasprite
 rts
Native:jmp FfGraphics
.endproc
FfHostPickupsEnd:
