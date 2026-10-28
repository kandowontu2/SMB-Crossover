; Independent unused2.02 four-class port. ROOT owns all shared dispatch/hooks.
.ifndef __FINAL_FANTASY_STATE_INC
__FINAL_FANTASY_STATE_INC=1
.ifndef CHARACTER_FINAL_FANTASY
CHARACTER_FINAL_FANTASY=22
.endif
.ifndef FF_FIRST_CHR
FF_FIRST_CHR=756                 ; Configurable verified integration reservation.
.endif
FfVariant=$5fef                  ;0Fighter,1WhiteMage,2BlackMage,3Thief.
FfReady=$5fc1
FfLife=$5fc2
FfArea=$5fc3
FfWorld=$5fc4
FfPower=$5fc5                    ; crossover0/1/2, never an original FF upgrade.
FfEarned=$5fc6                   ; highest earned tier; Heal cannot exceed this.
FfHealCharges=$5fc7              ; White only; actual pickups earn, max3.
FfPaletteAck=$5fc8
FfWalk=$5fc9                    ; area-reset animation state, not acquired gear.
FfWalkDelay=$5fca
FfFireClock=$5fcb                ; shared33ms source AnimationTimers phase,16bit.
FfModerateClock=$5fcd            ; shared75ms phase,16bit; ends5FCE.
FfPrevious=$5c00
FfFresh=$5c01
FfClock=$5c02                   ; current shared animation events:bit0Fire/1other.
FfAction=$5c03                   ;0idle,1melee,2prepare,3cast.
FfAge=$5c04                      ; elapsed complete60Hz logical updates.
FfSpell=$5c05                    ;1Fire,2Bolt,3Ice,4White light,5Heal.
FfHits=$5c06                     ; six native enemy identities per melee action.
FfHurt=$5c07
FfHurtMove=$5c08
FfJump=$5c09
FfHPhase=$5c0a                   ; 2/3 Q8.8 horizontal residual.
FfGPhase=$5c0b                   ; 28/36 dry gravity residual.
FfPose=$5c0c
FfTemp=$5c0d
FfTemp2=$5c0e
FfSlot=$5c0f
FfTargetX=$5c10                  ; host's actual eligible target bounding box.
FfTargetPage=$5c11
FfTargetY=$5c12
FfTargetW=$5c13
FfTargetH=$5c14
FfDamage=$5c15                   ; actual source HP units; host must consume exact.
FfRectX=$5c16
FfRectPage=$5c17
FfRectY=$5c18
FfRectW=$5c19
FfRectH=$5c1a
FfEnemyBit=$5c1b
FfProjectile=$5c1c               ; three12-byte records, ends5C3F.
; kind,frame,reserved0,reserved0,x,page,xFraction,y,face,hitMask,tier,yFraction
FfRenderBuffer=$5c40             ; complete descriptor <=61bytes; ends5C7C.
FfRenderYOffset=$5c7d            ; signed16bit chunk origin adjustment.
FfRenderPage=$5c7f               ; relative physical1KB page.
.export FfVariant,FfReady,FfPower,FfEarned,FfHealCharges,FfAction,FfAge,FfPose
.export FfProjectile,FfTargetX,FfTargetPage,FfTargetY,FfTargetW,FfTargetH,FfDamage
.export FfRenderBuffer,FfRenderYOffset,FfRenderPage
.export FfLife,FfArea,FfWorld,FfPaletteAck,FfPrevious,FfFresh,FfClock,FfSpell,FfHits
.export FfHurt,FfHurtMove,FfJump,FfHPhase,FfGPhase,FfSlot,FfTemp,FfTemp2
.export FfWalk,FfWalkDelay
.export FfFireClock,FfModerateClock
.endif
