; Independent component, not yet included by the shared entrypoint.
; Code: reserved physical95 A310+; art: physical94 C2C0+.
.include "mac_roster_state.inc"
.pushseg
.segment "MAC_ROSTER_CORE"
MacRosterCoreBegin:

; A=validated variant, X/Y unchanged. Invalid persistent values use Mac.
.proc MacRosterVariant
 lda MacVariant
 cmp #MAC_ROSTER_VARIANTS
 bcc Done
 lda #MAC_ROSTER_MAC
Done:rts
.endproc

; New callable replacement for LmSetPose, via a genuine farcall from bank93.
; X=old semantic pose0..9, or10 for portrait. Caller X/Y retained; A=the
; original body metasprite sentinel. C matches the original facing CMP#2;
; V/D/I retain the post-palette state. No new scratch/application masks.
.proc MacRosterSetPose
 phx
 phy
 jsr MacRosterQueuePalette
 php
 BankPRGC #94
 jsr MacRosterSelectFrame
 tax
 lda PlayerFacingDir
 cmp #2
 beq Left
 lda MacRosterRLo,x
 sta SmPosePtr
 lda MacRosterRHi,x
 sta SmPosePtr+1
 jmp Store
Left:
 lda MacRosterLLo,x
 sta SmPosePtr
 lda MacRosterLHi,x
 sta SmPosePtr+1
Store:
 lda MacRosterChrLow,x
 sta SmChrBank
 lda Player_SprAttrib
 and #$fc
 sta Player_SprAttrib
 plp
 ply
 plx
 lda PlayerFacingDir
 cmp #2
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 rts
.endproc

; C94 must already be mapped. Returns A=real frame table index.
; All attack poses show windup, active punch and recovery; timing is a
; deliberate platform boxing profile, not a claim of original NPC AI.
.proc MacRosterSelectFrame
 jsr MacRosterVariant
 tay
 cpx #MAC_ROSTER_PORTRAIT
 jeq Portrait
 cpx #10
 bcc :+
 ldx #0
:
 cpx #8
 jcs DuckAttack
 cpx #4
 bcc Locomotion
 cpx #6
 jcc Attack
 cpx #7
 jeq Hurt
 lda Player_Y_Speed
 bmi Rising
 lda MacRosterPose_jump1,y
 rts
Rising:
 lda MacRosterPose_jump0,y
 rts
Locomotion:
 cpx #0
 jeq Idle
 cpx #3
 jeq Duck
 lda LmWalk
 cmp #14
 bcc Walk0
 cmp #27
 bcc Walk1
 lda MacRosterPose_walk2,y
 rts
Walk0:
 lda MacRosterPose_walk0,y
 rts
Walk1:
 lda MacRosterPose_walk1,y
 rts
Attack:
 lda LmSuper
 bne Super
 lda LmAttack
 cmp MacRosterNormalStartExclusive,y
 bcs Windup
 cmp MacRosterNormalEnd,y
 bcc Idle
 lda MacRosterPose_punch,y
 rts
Super:
 lda LmAttack
 cmp MacRosterSuperStartExclusive,y
 bcs Windup
 cmp MacRosterSuperEnd,y
 bcc Idle
 lda MacRosterPose_uppercut,y
 rts
DuckAttack:
 lda LmSuper
 bne DuckSuper
 lda LmAttack
 cmp MacRosterNormalStartExclusive,y
 bcs Duck
 cmp MacRosterNormalEnd,y
 bcc Duck
 lda MacRosterPose_duckpunch,y
 rts
DuckSuper:
 lda LmAttack
 cmp MacRosterSuperStartExclusive,y
 bcs Duck
 cmp MacRosterSuperEnd,y
 bcc Duck
 ; Supplied Mac has no crouched uppercut cell; the authored crouched punch
 ; is reused honestly, with the existing taller super hit volume retained.
 lda MacRosterPose_duckpunch,y
 rts
Windup:
 lda MacRosterPose_windup,y
 rts
Idle:
 lda MacRosterPose_idle,y
 rts
Duck:
 lda MacRosterPose_duck,y
 rts
Hurt:
 lda MacRosterPose_hurt,y
 rts
Portrait:
 lda MacRosterPortraitFrames,y
 rts
.endproc

.proc MacRosterPublish
 lda SmChrBank
 ldx #2
 ldy #0
 farcall X5SetPhysicalChr
 lda #<704
 ldx #>704
 farcall X5SetSpecialChr,jmp
.endproc

; Shared root portrait dispatcher should call LmEnsure first, as before.
.proc MacRosterPortrait
 ldx #MAC_ROSTER_PORTRAIT
 jsr MacRosterSetPose
 jsr MacRosterPublish
 jmp MacRosterForcePalette
.endproc

.proc MacRosterForcePalette
 lda #0
 sta LmPalette
 jmp MacRosterQueuePalette
.endproc

; Same six-byte palette command and original84-byte queue guard. Only the
; player subpalette0 is touched; original star palette2 remains its owner.
; X/Y preserved. ROOT must invalidate LmPalette after Select variant changes.
.proc MacRosterQueuePalette
 phx
 phy
 lda LmPalette
 bne Done
 ldx VRAM_Buffer1_Offset
 cpx #78
 bcs Done
 jsr MacRosterVariant
 tay
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$11
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 lda MacRosterPalette1,y
 sta VRAM_Buffer1+3,x
 lda MacRosterPalette2,y
 sta VRAM_Buffer1+4,x
 lda MacRosterPalette3,y
 sta VRAM_Buffer1+5,x
 txa
 clc
 adc #6
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 inc LmPalette
Done:
 ply
 plx
 rts
.endproc

; Caller chooses attack kind in the existing LmSuper field. Return A=total,
; X=clamped variant, Y retained. Does not spend or grant any resource itself.
.proc MacRosterAttackTotal
 jsr MacRosterVariant
 tax
 lda LmSuper
 beq Normal
 lda MacRosterSuperTotal,x
 rts
Normal:
 lda MacRosterNormalTotal,x
 rts
.endproc

; C=1 only in this variant's real remaining-age active interval. A/X/P are
; results, Y retained; existing combat owns hits, debit, collision and cleanup.
.proc MacRosterAttackWindow
 jsr MacRosterVariant
 tax
 lda LmSuper
 beq Normal
 lda LmAttack
 cmp MacRosterSuperStartExclusive,x
 bcs No
 cmp MacRosterSuperEnd,x
 bcc No
 sec
 rts
Normal:
 lda LmAttack
 cmp MacRosterNormalStartExclusive,x
 bcs No
 cmp MacRosterNormalEnd,x
 bcc No
 sec
 rts
No:
 clc
 rts
.endproc

; Use before debiting a star/starting a punch. C admits exactly the complete
; heart cost, including Tyson's2; one remaining heart cannot wrap to255.
.proc MacRosterCanAfford
 jsr MacRosterVariant
 tax
 lda LmHearts
 cmp MacRosterHeartCost,x
 rts
.endproc

; Called only when the genuine fresh attack is accepted; returns C=success.
; Insufficient spirit never mutates it. Existing hit refund remains +1.
.proc MacRosterSpendHearts
 jsr MacRosterCanAfford
 bcc No
 sec
 sbc MacRosterHeartCost,x
 sta LmHearts
 sec
 rts
No:
 clc
 rts
.endproc

; Platform adaptations. Original Mac's health96/hearts20/star cap3 remain
; unchanged for every alternate; earned pickups keep the existing owner.
MacRosterNormalTotal:          .byte 34,42,28
MacRosterNormalStartExclusive: .byte 27,33,23
MacRosterNormalEnd:            .byte 12,14,9
MacRosterSuperTotal:           .byte 88,96,76
MacRosterSuperStartExclusive:  .byte 71,78,60
MacRosterSuperEnd:             .byte 42,44,30
MacRosterPunchReach:           .byte 18,20,24
MacRosterNormalHeight:         .byte 10,12,12
MacRosterSuperHeight:          .byte 38,38,42
MacRosterHeartCost:            .byte 1,1,2
MacRosterRestPeriod:           .byte 30,24,36
MacRosterPalette1:             .byte $36,$17,$18
MacRosterPalette2:             .byte $0a,$0f,$0f
MacRosterPalette3:             .byte $2a,$30,$16
MacRosterCoreEnd:
.assert MacRosterCoreEnd-MacRosterCoreBegin<=$1cf0,error,"Reserved95 A310..BFFF"
.popseg

.include "mac_roster_data.inc"
.pushseg
.segment "MAC_ROSTER_CHR"
.incbin "chr/characters/mac-roster.chr"
.popseg
