; Interim SMB-native pickup/tier armor policies for all six WWF roles.
; No claim of original WWF endurance, gear, source damage or weapon upgrades.
.setcpu "6502"
.segment "INJURY"
.byte <GuestInjuryStart,>GuestInjuryStart,GuestInjuryBank
.segment "STATUS"
.byte <NativePlayerStatus,>NativePlayerStatus,NativeStatusBank
.segment "MATURE"
.byte <NativeMatureRule,>NativeMatureRule,NativeMatureBank
.segment "COLLECT"
.byte <MarioSourcePowerupCollision,>MarioSourcePowerupCollision,NativeCollectBank
.segment "TICK"
.byte <GuestPowerupUpdate,>GuestPowerupUpdate,NativeTickBank
