; Two formerly rejected native policies only. Ordinary native item maturity
; precedes the unchanged ThomasHostPickup/MarioSourcePowerupCollision path.
.setcpu "6502"
.segment "POLICIES"
.export ThomasNativeMature,ThomasNativePowerupTick
ThomasNativeMature:
 lda PowerUpType,x
 cmp #2
 bcs Allowed
 lda Enemy_State,x
 bmi Allowed
 clc
 rts
Allowed:
 sec
 rts
ThomasNativePowerupTick:
 sta SafecallA_SMC+1
 lda #<GuestPowerupUpdate
 sta FarcallJmpTarget_SMC+1
 lda #>GuestPowerupUpdate
 sta FarcallJmpTarget_SMC+2
 lda #GuestPowerupBank
 jmp FarCallCommon
