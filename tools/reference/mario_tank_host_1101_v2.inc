; Tank Mario host proposal. MarioVariant7 remains NOT menu-admitted here.
; Conditional RAM2 worker, assembled at its A-window alias B600. Existing
; FarCallCommon rawbank2 owns mapping/restoration around native callbacks.
; No RAM/code/CHR lease or global identity admission is allocated here.
.import SelectedCharacter,MarioVariant,PlayerStatus,PlayerSize,TimerControl
.import GameEngineSubroutine,InjuryTimer,Square1SoundQueue,Square2SoundQueue
.import Enemy_ID,Enemy_State,Enemy_Y_HighPos,Enemy_Flag,PowerUpType
.import ObjectOffset,Player_State,StarInvincibleTimer
.import MtRemovedTile
.import ChkToStunEnemies,SetupFloateyNumber,EraseEnemyObject,SetPRout
.import InitChangeSize,DonePlayerTask
.export MtHostSelected,MtHostBooted,MtHostContact,MtHostInjury
.export MtHostMovement,MtHostBeginPowerup,MtHostGrowthUpdate,MtHostEnd
.segment "MT_HOST"

; Identity and powered predicate. A/flags consumed, X/Y preserved.
MtHostSelected:
 lda SelectedCharacter
 bne MtHostNo
 lda MarioVariant
 cmp #7
 beq MtHostYes
MtHostNo:clc
 rts
MtHostYes:sec
 rts
MtHostBooted:
 jsr MtHostSelected
 bcc MtHostNo
 lda PlayerStatus
 cmp #2
 beq MtHostYes
 clc
 rts

; Replacement for the existing EColl farcall S2BoundaryImmunity. All native
; collision eligibility/offscreen/overlap checks still precede this boundary.
; Source original Tank defeat uses1000points and erases piranha after effects.
; No ordinary host ShellOrBlockDefeat's100/200point substitution is allowed.
MtHostContact:
 php
 pha
 jsr MtHostSelected
 bcc MtHostContactLegacy
 lda PlayerStatus
 cmp #2
 beq MtHostContactPowered
 pla
 plp
 clc                         ; Tank never inherits Flash Mario's blooper quirk
 rts
MtHostContactPowered:
 pla
 plp
 lda Enemy_ID,x
 pha
 jsr ChkToStunEnemies
 lda Enemy_State,x
 and #$1f
 ora #$20
 sta Enemy_State,x
 lda #6
 jsr SetupFloateyNumber
 lda #$08                   ; actual donor/host Sfx_EnemySmack; binding asserts it
 sta Square1SoundQueue
 pla
 cmp #$0d                   ; actual donor/host PiranhaPlant; binding asserts it
 bne MtHostContactDone
 lda #2
 sta Enemy_Y_HighPos,x
 lda #0
 sta Enemy_Flag,x
MtHostContactDone:sec
 rts
MtHostContactLegacy:
 pla
 plp
 MtHostFar S2BoundaryImmunity
 rts

; Existing ForceInjury already checks GuestInjuryStatus and kills smallMario.
; Replace its Mario-only CmHostMarioInjury farcall, keeping its native exit.
MtHostInjury:
 php
 pha
 jsr MtHostSelected
 bcc MtHostInjuryLegacy
 lda PlayerStatus
 cmp #2
 beq MtHostImmune
 pla
 plp
 lda #0
 sta PlayerStatus
 lda #8
 sta InjuryTimer
 asl
 sta Square1SoundQueue
 MtHostFar GetPlayerColors
 lda #$0a
 ldy #1
 jmp SetPRout
MtHostImmune:
 pla
 plp
 rts
MtHostInjuryLegacy:
 pla
 plp
 MtHostFar CmHostMarioInjury
 rts

; Current default Mario uses Flash movement. Tank uses the original native
; donor physics, via the already present genuine native SMB route.
MtHostMovement:
 php
 pha
 jsr MtHostSelected
 bcc MtHostMovementLegacy
 lda #0
 sta MtRemovedTile            ; actual once-per-update owner, before BG probes
 pla
 plp
 MtHostFar CrossoverVanillaMovement
 rts
MtHostMovementLegacy:
 pla
 plp
 MtHostFar BmMarioMovement
 rts

; Native outer pickup owner retains erasure,1000points and pickupSFX. Hook
; only its existing MarioSourceBeginPowerup call, after all item admission.
MtHostBeginPowerup:
 php
 pha
 jsr MtHostSelected
 bcc MtHostPowerupLegacy
 pla
 plp
 lda PlayerStatus
 beq MtHostGrow
 cmp #1
 bne MtHostUpgradeDone
 ldx ObjectOffset
 lda #2
 sta PlayerStatus
 MtHostFar GetPlayerColors
 ldx ObjectOffset
 lda #$0c                   ; original donor does not SetPRout for boots
MtHostUpgradeDone:rts
MtHostGrow:
 lda #1
 sta PlayerStatus
 lda #9
 ldy #0
 jmp SetPRout
MtHostPowerupLegacy:
 pla
 plp
 MtHostFar MarioSourceBeginPowerup
 rts

; Current PlayerChangeSize routes Mario to Flash's source updater, which
; would stall a native SetPRout9 growth. Hook that existing farcall too.
MtHostGrowthUpdate:
 php
 pha
 jsr MtHostSelected
 bcc MtHostGrowthLegacy
 pla
 plp
 lda TimerControl
 cmp #$f8
 bne MtHostGrowthEnd
 MtHostFar InitChangeSize
 rts
MtHostGrowthEnd:
 cmp #$c4
 bne MtHostGrowthDone
 MtHostFar DonePlayerTask
MtHostGrowthDone:rts
MtHostGrowthLegacy:
 pla
 plp
 MtHostFar MarioSourcePowerupUpdate
 rts
MtHostEnd:
