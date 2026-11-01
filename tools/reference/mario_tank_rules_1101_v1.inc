; AleFunky / Mario the Tank a0f6383f (released1.0.2a), from authenticated
; byte-identical author build. Native effects, maps and scripts remain owners.
; Caller MUST admit the Tank identity; these helpers do not globally enable
; tank behavior for every character with native PlayerStatus2.
.import PlayerStatus,RemovedTile,StarInvincibleTimer,Enemy_SprAttrib
.importzp GameEngineSubroutine,FrameCounter,ObjectOffset,PowerUpType
.import MtCheckClimb,MtGetPlayerColors,MtSetPRout
.importzp R2
.export MtTileChecks,MtCellAction,MtContactPolicy,MtInjuryBlocked
.export MtPickupCycle,MtCollectUpgrade,MtWearBootsFlash,MtRulesEnd
.segment "MT_RULES"

; Exact original TileChecks/ForceSolidBlocks, original collision.s1469..1499.
; A=metatile, C=protected/native interaction; A preserved, X clobbered by
; the existing native metatile attribute helper. No new RAM or code lease.
MtTileChecks:
 jsr MtCheckClimb
 bcs MtFoundTile
 cmp #$c2
 beq MtFoundTile
 cmp #$c3
 beq MtFoundTile
 cmp #$6d
 beq MtFoundTile
 cmp #$67
 beq MtFoundTile
 cmp #$68
 beq MtFoundTile
 cmp #$c5
 beq MtFoundTile
 cmp #$1c
 beq MtFoundTile
 cmp #$1f
 beq MtFoundTile
 cmp #$6b
 beq MtFoundTile
 cmp #$6c
 beq MtFoundTile
 clc
 rts
MtFoundTile:
 sec
 rts

; Adapted returning ABI for original CheckForSpeedrunMode. Original used TXS
; to discard its caller's JSR; that must never discard the host farcall frame.
; A action:0=native/inactive,1=protected,2=one-cell budget used,3=destroy.
; C set only for3. Original terrain mutation/particles/50pts/SFX remain an
; explicit native effect callback. Do not run for foot/floor support probes.
MtCellAction:
 jsr MtTileChecks
 bcs MtProtected
 lda GameEngineSubroutine
 cmp #8
 bne MtNative
 lda PlayerStatus
 cmp #2
 bne MtNative
 lda RemovedTile
 bne MtBusy
 lda #3
 sec
 rts
MtProtected:lda #1
 clc
 rts
MtBusy:lda #2
 clc
 rts
MtNative:lda #0
 clc
 rts

; Exact EColl routing predicate: Tank OR star routes ShellOrBlockDefeat.
; C set means defeat; C clear means ordinary native contact.
MtContactPolicy:
 lda PlayerStatus
 cmp #2
 beq MtDefeat
 lda StarInvincibleTimer
 beq MtOrdinary
MtDefeat:sec
 rts
MtOrdinary:clc
 rts

; Exact ForceInjury prefix; Z set means original tank immunity.
MtInjuryBlocked:
 lda PlayerStatus
 cmp #2
 rts

; Exact DrawPowerUp prefix through SkipPaletteCycle; Y retains powerup type.
; Native mushroom/1up remain static, boots(type1) and star(type2) every2frames.
MtPickupCycle:
 ldx ObjectOffset
 ldy PowerUpType
 beq MtPickupDone
 cpy #3
 beq MtPickupDone
 lda FrameCounter
 lsr
 and #3
 sta R2
 lda Enemy_SprAttrib,x
 and #$e0
 ora R2
 sta Enemy_SprAttrib,x
MtPickupDone:rts

; Exact Shroom_Flower_PUp and UpToSuper source, native effect callbacks.
; Outer native pickup owner still erases the object, awards1000 and plays SFX.
MtCollectUpgrade:
 lda PlayerStatus
 beq MtUpToSuper
 cmp #1
 bne MtUpgradeDone
 ldx ObjectOffset
 lda #2
 sta PlayerStatus
 jsr MtGetPlayerColors
 ldx ObjectOffset
 lda #$0c
MtUpgradeDone:rts
MtUpToSuper:
 lda #1
 sta PlayerStatus
 lda #9
 ldy #0
 jmp MtSetPRout

; USER-REQUESTED ADAPTATION, absent from donor: apply the donor's exact2-frame
; palette cadence ONLY to a separately masked worn-boot OAM part. A=attribute,
; A=result, R2 scratch. Caller supplies proper boot-only art/OAM ownership and
; budget; this function does not recolor the player's whole lower body.
MtWearBootsFlash:
 pha
 lda PlayerStatus
 cmp #2
 beq MtWearCycle
 pla
 rts
MtWearCycle:
 lda FrameCounter
 lsr
 and #3
 sta R2
 pla
 and #$e0
 ora R2
 rts
MtRulesEnd:
