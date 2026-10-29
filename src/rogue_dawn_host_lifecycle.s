; PRIVATE successor to immutable f1ed39. No menu/playable/native admission.
; Real source hurt controls remain in literal124; native life/death clock is
; an explicit SMB adaptation. No additional global flags/RAM/segments.
; Root supplies authenticated right95:BF00 / left95:BF19 / CHR689 separately.
.pushseg
.segment "ROGUE_DAWN_HOST"
.export RdLifeStart,RdLifeEnd,RdLifeFresh,RdLifeArea,RdLifeVisible
.export RdLifeGameRoutines,RdLifeCheatRoutines,RdLifeMovement
.export RdLifeUi
.export RdLifeStatus,RdLifeInjury,RdLifeBody,RdLifeDeathStart,RdLifeDeathTick
.export RdLifeDraw,RdLifeGraphics,RdLifeDynamicPrg
RdLifeStart:

; Native pause remains in real PauseRoutine before this UI slot. Rogue's
; sourceSelect/gear is not legacySamus inventory: do not interpret its dormant
; InvSelected as a live weapon or let that UI write this active overlay.
.proc RdLifeUi
 php
 pha
 jsr RdHostEnabled
 bcc Foreign
 pla
 plp
 rts
Foreign:pla
 plp
 farcall X5BounceUiDispatch,jmp
.endproc

.proc RdLifeGameRoutines
 php
 pha
 jsr RdHostEnabled
 bcc Foreign
 pla
 plp
 jsr RdLifePrepareMain
 farcall GameRoutines,jmp
Foreign:pla
 plp
 farcall GameRoutines,jmp
.endproc
.proc RdLifeCheatRoutines
 php
 pha
 jsr RdHostEnabled
 bcc Foreign
 pla
 plp
 jsr RdLifePrepareMain
 farcall GameRoutines,jmp
Foreign:pla
 plp
 farcall CheatsGameRoutinesGate,jmp
.endproc
; Both real GameRoutinesBridge routes converge here before any legacy
; GuestHurt/Powerup alias can suppress input or replace source movement.
; Only exact owner calls this internal helper. Native pause bypasses Main.
.proc RdLifePrepareMain
 lda #0
 sta GuestHurtKind
 sta GuestHurtTicks
 sta GuestInvulTicks
 sta GuestLegacyHurt
 sta InjuryTimer
 sta GuestPowerupActive
 sta PlayerChangeSizeFlag
 lda GameEngineSubroutine
 cmp #8
 bne Done
 lda #0
 sta TimerControl
 lda RdAction
 cmp #7
 bcs Done
 lda #0
 sta MmDeathFlag                 ; stale foreign flag, not real engine11 death
Done:rts
.endproc

; Real menu Start's LAST fresh-game child; all prior generic clearing has
; completed. Continue deliberately skips this original fresh-game owner.
.proc RdLifeFresh
 php
 pha
 jsr RdHostEnabled
 bcc Foreign
 pla
 plp
 farcall CmHostFresh
 jsr RdBodyNewSession
 jmp RdLifePrepareMain
Foreign:pla
 plp
 farcall CmHostFresh,jmp
.endproc

; InitializeArea's original18B Z2ResetAreaGate target. Source active overlay
; is initialized AFTER actual native guest clearing; old Z2's unconditional
; overlay clear is never run after new Rogue initialization. MmDeathFlag is
; an existing real death receipt, not a new inferred life counter. Earned1Up
; alone never calls this as a life-loss hook and never refills source health.
.proc RdLifeArea
 php
 pha
 jsr RdHostEnabled
 bcc Foreign
 pla
 plp
 lda MmDeathFlag
 pha
 farcall MegaManResetArea
 pla
 bne Life
 lda RdHealthLo
 ora RdHealthHi
 bne Scene
 ; Actual newly activated scene cannot expose a dead source player. Empty
 ; first-use Continue and a completed death both refill the same legal cap;
 ; no equipment/tank/missile byte is discarded as an inferred "new game".
Life:jsr RdBodyNewLife
 jmp Ready
Scene:jsr RdBodyEnterScene
Ready:jmp RdLifePrepareMain
Foreign:pla
 plp
 farcall Z2ResetAreaGate,jmp
.endproc

.proc RdLifeMovement
 php
 pha
 jsr RdHostEnabled
 bcc Foreign
 pla
 plp
 jsr RdTxMovement
 lda RdHealthLo
 and #$f0
 ora RdHealthHi
 bne Done
 jmp RdLifeBeginDeath
Done:rts
Foreign:pla
 plp
 jmp RdTxMovement
.endproc

; Exact source current-frame visibility, including its literalF7 hurt flash.
; No native InjuryTimer/GuestHurt flag chooses a Rogue body frame anymore.
.proc RdLifeVisible
 php
 pha
 jsr RdHostEnabled
 bcc Foreign
 pla
 plp
 lda RdAnimFrame
 cmp #$f7
 beq Hide
 sec
 rts
Hide:clc
 rts
Foreign:pla
 plp
 farcall RlVisibleDispatch,jmp
.endproc
.proc RdLifeStatus
 php
 pha
 jsr RdHostEnabled
 bcc Foreign
 pla
 plp
 lda #1
 tax
 rts
Foreign:pla
 plp
 farcall RlInjuryStatusDispatch,jmp
.endproc

; Real full-page native contact has already been established. Explicit
; authored SMB mapping: ordinary listed live primary actors take source8HP
; (starting-area02:95CE/CF80/00), genuine Suit halving. No Hard multiplier.
; Hazards/boss/unknown classes are NOT admitted by this bounded unit. They
; return protected pending a separately approved mapping, never alias Samus.
.proc RdLifeInjury
 php
 pha
 jsr RdHostEnabled
 bcc Foreign
 pla
 plp
 lda GamePauseStatus
 and #1
 bne Protected
 lda RdHurtClock
 bne Protected
 lda RdHit
 and #$20
 bne Protected                   ; one paid contact per real source update
 ldx ObjectOffset
 cpx #5
 bcs Protected
 lda Enemy_Flag,x
 cmp #1
 bne Protected
 lda Enemy_State,x
 and #$20
 bne Protected
 lda Enemy_ID,x
 ldy #EligibleEnd-Eligible-1
Find:cmp Eligible,y
 beq Admit
 dey
 bpl Find
 jmp Protected
Admit:
 lda Player_X_Position
 sec
 sbc Enemy_X_Position,x
 lda Player_PageLoc
 sbc Enemy_PageLoc,x
 bpl LeftAttacker
 lda #$20                      ; recoil left, actual attacker to the right
 bne Hit
LeftAttacker:lda #$28           ; recoil right, actual attacker to the left
Hit:sta RdHit
 lda #$80
 sta RdContactFlags
 lda #$80
 ldy #0
 jsr RdHsDamage                 ; real source BCD + lethal continuation
 lda RdHealthLo
 and #$f0
 ora RdHealthHi
 bne Protected
 jsr RdLifeBeginDeath
Protected:sec
 rts
Foreign:pla
 plp
 farcall RlInjuryDispatch,jmp
Eligible:
 .byte $00,$01,$02,$03,$04,$05,$06,$07,$08,$09,$0a,$0b,$0d,$0e,$0f,$11,$12,$14,$33
EligibleEnd:
.endproc

; Real contact wrapper rejects old Samus SmFlip/inventory Screw aliases.
; Source weapon/Screw enemy-HP consumers remain their separate OPEN unit.
.proc RdLifeBody
 php
 pha
 jsr RdHostEnabled
 bcc Foreign
 pla
 plp
 lda AreaType
 sta GuestBodyStompAllowed
 lda #1
 sta GuestBodyNoStomp
 clc
 rts
Foreign:pla
 plp
 farcall LmBodyGate,jmp
.endproc

.proc RdLifeBeginDeath
 lda GameEngineSubroutine
 cmp #11
 beq Done
 lda #0
 sta MmDeathFlag
 jsr KillPlayer                  ; genuine fixed LOW126 engine11/life owner
Done:rts
.endproc
.proc RdLifeDeathStart
 php
 pha
 jsr RdHostEnabled
 bcc Foreign
 pla
 plp
 lda #0
 sta RdHealthLo
 sta RdHealthHi
 farcall RdControlDamageComplete ; actual source action7/animation32/request
 rts
Foreign:pla
 plp
 farcall Cv3FxDeathDispatch,jmp
.endproc
.proc RdLifeDeathTick
 php
 pha
 jsr RdHostEnabled
 bcc Foreign
 pla
 plp
 lda GamePauseStatus
 and #1
 bne Done
 jsr RdTxMovement               ; original source action/motion/draw, no weapons
 farcall SamusDeathUpdate       ; native180/150 clock -> actual engine6
Done:rts
Foreign:pla
 plp
 farcall SamusDeathUpdate,jmp
.endproc

; Narrow service3 vector successor. C94 MUST remain mapped for the genuine
; immutable callback continuation; no C95 descriptor read occurs here.
; Source death35, virtual original8x8 priorcursor0:6parts/X24/radii0/0.
; Other frames execute the actual unchanged callback immediately.
.proc RdLifeDraw
 php
 pha
 jsr RdHostEnabled
 bcc NotOwner
 pla
 plp
 lda RdAnimFrame
 cmp #$35
 bne Legacy
 lda RdSourceAltPalette
 bne Legacy
 lda RdFacing
 cmp #2
 bcs Legacy
 jsr RdLifeDeathMetadata
 ldx #24
 ldy #12
 lda RdRoomHi
 and #1
 sec
 rts
Legacy:jmp RdHsDraw
NotOwner:pla
 plp
 clc
 rts
.endproc
.proc RdLifeDeathMetadata
 lda #0
 sta RdRadiusX
 sta RdRadiusY
 ldx RdFacing
 lda DeathLow,x
 sta SmPosePtr
 lda #>RD_DEATH_RECORD_C
 sta SmPosePtr+1
 lda #<689
 sta SmChrBank
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 rts
DeathLow:.byte <RD_DEATH_RECORD_C,<RD_DEATH_RECORD_LEFT_C
.endproc
.proc RdLifeGraphics
 php
 pha
 jsr RdHostEnabled
 bcc Foreign
 lda RdAnimFrame
 cmp #$35
 bne Foreign
 lda RdSourceAltPalette
 bne Foreign
 lda RdFacing
 cmp #2
 bcs Foreign
 pla
 plp
 jsr RdLifeDeathMetadata
 jsr RdBodyPublishChr
 lda RdColorRequest
 beq Done
 jsr RdBodyQueuePalette
Done:lda Player_Rel_XPos
 sta Player_Pos_ForScroll
 rts
Foreign:pla
 plp
 jmp RdBodyGraphics
.endproc
.proc RdLifeDynamicPrg
 php
 pha
 jsr RdHostEnabled
 bcc Foreign
 lda RdAnimFrame
 cmp #$35
 bne Foreign
 lda RdSourceAltPalette
 bne Foreign
 lda RdFacing
 cmp #2
 bcs Foreign
 pla
 plp
 BankPRGC #95                  ; first genuine death-record consumer
 rts
Foreign:pla
 plp
 jmp RdBodyDynamicPrg
.endproc
RdLifeEnd:
.assert RdLifeStart=$b803,error,"Frozen body tail"
.assert * <= $bf00,error,"Reserved root death/item descriptors BF00..BFFF"
.popseg
