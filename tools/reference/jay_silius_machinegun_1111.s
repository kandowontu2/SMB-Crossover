.setcpu "6502"

.segment "MACHINE_GUN"
; Original $81D2 dispatcher checks cooldown before choosing a weapon.
MachineGunDispatch:
 php
 pha
 lda WeaponCooldown
 bne OtherWeapon
 lda WeaponSelection
 cmp #1
 bne OtherWeapon
 pla
 plp
 ldx #$80
 stx DispatchLo
 ldy #4
 lda #$84
 sta DispatchHi
 clc
 ; Original PRG6 $8480 uses held B, including after the first press.
 lda WeaponAmmo
 bne ReadTrigger
 sta WeaponSelection
 rts
ReadTrigger:
 lda PadNow
 and #$40
 beq Return
 lda #5
 jsr FreeSlot
 bne Return
 lda #1
 jsr SpendAmmo
 lda #$12
 jsr OriginalSoundRequest
 lda #4
 sta WeaponCooldown
 lda #$50
 sta ShotRecords+4,x
 lda #0
 sta ShotRecords+5,x
 sta ShotRecords+8,x
 lda #1
 sta ShotRecords+15,x
MachineGunBirth:
 jsr SpawnShot
 jmp ApplyShotStance
Return:
 rts
OtherWeapon:
 pla
 plp
 jmp AlternateInput

; Carry set rejects unsupported areas. Preserve original World 1-1
; admission and admit the walking portions of World 1-2.
StageRejected:
 lda SwimmingFlag
 ora WorldNumber
 bne RejectStage
 lda LevelNumber
 cmp #2
 rts
RejectStage:
 sec
 rts

; This caller has already passed the exact Jay owner and both cache headers.
; A native flagpole slide in 1-1 earns row 1 for the subsequent 1-2 opening.
ProgressMux:
 cpy #$d6
 bne ResumeOtherMux
 lda OperMode
 cmp #1
 bne ResumePause
 lda WorldNumber
 ora LevelNumber
 bne ResumePause
 lda GameEngineSubroutine
 cmp #4
 bne ResumePause
 lda #1
 sta StageOneFlagpole
ResumePause:
 jmp PauseWeapons
ResumeOtherMux:
 jmp OtherMux

ResetStageWeapons:
 jsr ResetWeapons
 lda #0
 sta ShotRecords+$b9
 sta ShotRecords+$c9
 lda LevelNumber
 bne LaterStage
 sta StageOneFlagpole
 rts
LaterStage:
 cmp #1
 bne ReturnReset
 lda StageOneFlagpole
 beq ReturnReset
 lda #3
 sta WeaponUnlocks
ReturnReset:
 rts
