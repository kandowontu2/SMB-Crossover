; Raw37 already collects native tier pickups through GuestBeginPowerup.
; Service33 must advance that same native60-update transaction. The loaded
; private kernel's former row33 explicitly rejected every update.
; No donor motor, source timing, actor, body, art or terrain change.
.setcpu "6502"
.segment "TICK"
.export ExHostPowerupProgression
ExHostPowerupProgression:
 sta SafecallA_SMC+1
 lda #<GuestPowerupUpdate
 sta FarcallJmpTarget_SMC+1
 lda #>GuestPowerupUpdate
 sta FarcallJmpTarget_SMC+2
 lda #GuestPowerupBank
 jmp FarCallCommon
