; Rogue Dawn1.21 actual action/control instruction projection. Source9271411a.
; Include AFTER frozen kernel/weapons/art/render. No default Samus delegation.
; ROOT owns all RdHost* boundaries; no source Metroid room RAM is constructed.
; Native source radius/center and all canonical input bits remain source units.
.include "rogue_dawn_state.inc"
.macpack longbranch
RdPlayerUpdating=$5c17 ; source0055
RdWalkDelay=$5c18 ; source0053
RdMoveCount=$5c19 ; source0065
RdSlow=$5c1a ; source0064
RdMorphCooldown=$5c1b ; source002A
RdHurtClock=$5c1c ; source0070
RdHurtDirection=$5c1d ; source0072
RdContactFlags=$5c1e ; source0073
RdHurtBlink=$5c1f ; source0077
RdDoorMove=$5c7e ; source0058
RdControlTemp=$5c7f ; source000E
.pushseg
.segment "ROGUE_DAWN_CORE"

.export RdControlStep,RdControlDispatch,RdControlJump,RdControlSpring
.export RdControlScrew,RdControlPhysics,RdControlDamageComplete
.proc RdControlStep
 lda RdSourceAltPalette
 bne Unsupported
 ldx #0
 stx RdSlot
 inx
 stx RdPlayerUpdating
 jsr RdControlDispatch
 dec RdPlayerUpdating
 rts
Unsupported:clc
 rts
.endproc
.pushseg
.segment "ROGUE_DAWN_CONTROL_AUX"
.proc RdControlDispatch
 lda RdAction
 bmi Stand
 cmp #0
 beq Stand0
 cmp #1
 beq Run
 cmp #2
 beq Jump
 cmp #3
 beq Ball
 cmp #4
 beq Aim
 cmp #5
 beq Door
 cmp #6
 beq JumpAim
 cmp #7
 beq Dead
 cmp #8
 beq Dead2
 cmp #9
 beq Elevator
 clc
 rts
Stand0:clc
 lda #$cc
Stand:jmp RdC_CC36
Run:clc
 lda #$da
 jmp RdC_DA25
Jump:clc
 lda #$da
 jmp RdC_DA0A
Ball:clc
 lda #$d0
 jmp RdC_D0E1
Aim:clc
 lda #$d1
 jmp RdC_D198
Door:clc
 lda #$d3
 jmp RdHostDoor
JumpAim:clc
 lda #$da
 jmp RdC_DA72
Dead:clc
 lda #$d4
 jmp RdC_D41A
Dead2:clc
 lda #$d4
 jmp RdC_D41F
Elevator:clc
 lda #$d4
 jmp RdHostElevator
.endproc
.proc RdControlStandFollow
 cmp #1
 beq Run
 cmp #2
 beq Jump
 cmp #3
 beq Morph
 cmp #4
 beq Aim
 clc
 lda #$c4
 rts
Run:clc
 lda #$cc
 jmp RdC_CC98
Jump:clc
 lda #$cf
 jmp RdStartJump
Morph:clc
 lda #$d0
 jmp RdC_D0B5
Aim:clc
 lda #$cf
 jmp RdC_CF77
.endproc
.proc RdControlAimFollow
 cmp #0
 beq Stand
 cmp #1
 beq Run
 cmp #3
 beq Morph
 cmp #6
 beq Jump
 clc
 lda #$c4
 rts
Stand:clc
 lda #$cf
 jmp RdC_CF55
Run:clc
 lda #$cc
 jmp RdC_CC98
Morph:clc
 lda #$d0
 jmp RdC_D0B5
Jump:clc
 lda #$cf
 jmp RdControlUpJump
.endproc
.popseg
RdControlJump:
 jsr RdCutOrdinaryJump
 jmp RdC_D015
.pushseg
.segment "ROGUE_DAWN_CONTROL_AUX"
RdControlSetIndex:
 sta RdAnimIndex
 lda #0
 sta RdAnimDelay
 rts
RdControlReturn:rts
RdControlUnmorphNotify:
 bit RdVY
 bpl RdControlReturn
 jmp RdStopVertical
RdControlNegate:
 eor #$ff
 clc
 adc #1
 rts
RdControlBitIndex:
 stx RdControlTemp
 ldx #0
Loop:lsr
 bcs Found
 inx
 cpx #8
 bne Loop
Found:txa
 ldx RdControlTemp
 rts
RdControlAdvance:
 pha
 lda #0
 sta RdWeaponColor
 pla
 ldx #0
 ldy RdAnimDelay
 beq Advance
 dec RdAnimDelay
 bne AdvanceDone
Advance:sta RdAnimDelay
 ldy RdAnimIndex
AdvanceRead:cpy #$99
 bcc AdvanceOriginal
 lda RdControlRunExtension-$99,y
 jmp AdvanceCompare
AdvanceOriginal:lda RdArtAnimation,y
AdvanceCompare:cmp #$ff
 beq AdvanceLoop
 sta RdAnimFrame
 iny
 tya
 sta RdAnimIndex
AdvanceDone:rts
AdvanceLoop:ldy RdAnimReset
 jmp AdvanceRead
RdControlRunExtension:.byte 4,3,5,3,$ff ; actual02:860B..860F
RdControlSpring:
 bit RdFresh
 bpl Release
 lda RdFrozenSupport
 bne Admit
 jsr RdHostProbeDown
 bcs Release
Admit:jsr RdSpringAdmitted
 jmp RdC_D11E
Release:jsr RdSpringRelease
 jmp RdC_D11E
RdControlHurtSound:
 lda #4
 ldx #4
 jmp RdControlSound
RdControlDeathSound:
 lda #$80
 ldx #3
 jmp RdControlSound
RdControlMorphSound:
 lda #2
 ldx #3
RdControlSound:
 ora RdSfx,x
 sta RdSfx,x
 rts
RdControlUpJump:
 ldy #$35
 sty RdAnimReset
 dey
 sty RdAnimIndex
 lda #4
 sta RdAnimDelay
 lda #0
 sta RdJumpDistance
 lda #$fc
 sta RdVY
 jsr RdJumpRequest
 ldy #$18
 lda RdGear
 and #2
 beq Gravity
 ldy #$12
Gravity:jsr RdSetJumpGravity
 rts
RdControlHurtLaunch:
 lda RdEnvironment
 bmi Dry
 jsr RdHostProbeDown
 bcs Done
Dry:lda RdVY
 beq Launch
 bpl Done
Launch:lda #$fd
 sta RdVY
 lda #$38
 jsr RdSetGravity
 bit RdEnvironment
 bmi Done
 lda #$fe
 sta RdVY
Done:rts
; Host must apply real native-style BCD damage before this continuation;
; ordinary Samus HP is never read. This is actual post-damage CEDA..CEF9.
RdControlDamageComplete:
 lda RdHealthLo
 and #$f0
 ora RdHealthHi
 beq Death
 bcs RdControlDamageDone
Death:lda #0
 sta RdHealthLo
 sta RdHealthHi
 lda #7
 sta RdAction
 jsr RdControlDeathSound
 jmp RdC_CC8B
RdControlDamageDone:lda #0
 rts
; Public aliases refer to the actual source handlers below.
RdControlScrew=RdC_CD9C
RdControlActionFromDirection:.byte 1,1,3,4
RdControlRunAnimation:.byte $99,$37
RdControlRunFireAnimation:.byte $3f,$3b,$3d,$3f
RdControlFire:
 lda RdHeld
 and #8
 beq RdControlFireHorizontal
 jmp RdControlFireUp
RdControlFireHorizontal:
 jsr RdPrepareHorizontalShot
 bpl FireDenied
 jsr RdHostSpawnProjectile
 jmp RdFireHorizontalFinish
FireDenied:rts
RdControlFireUp:
 jsr RdPrepareUpShot
 bpl FireDenied
 jsr RdHostSpawnProjectile
 jmp RdFireUpFinish
.popseg
; Real source DBE6 environment boundary precedes E2A9 movement. Host geometry
; callbacks have source carryclear=blocked, carryset=one pixel committed.
.proc RdControlPhysics
 jsr RdHostEnvironment
 jsr RdControlVerticalAdmission
 jsr RdHostRelativeY
 lda RdDelta
 bpl Down
 jsr RdControlNegate
 ldy RdSlow
 beq UpCount
 lsr
 beq Horizontal
UpCount:sta RdMoveCount
Up:jsr RdHostMoveUp
 bcs NextUp
 sec
 ror RdVY
 ror RdVerticalFraction
 jmp Horizontal
NextUp:dec RdMoveCount
 bne Up
 beq Horizontal
Down:beq Horizontal
 ldy RdSlow
 beq DownCount
 lsr
 lsr
 beq Horizontal
DownCount:sta RdMoveCount
DownLoop:jsr RdHostMoveDown
 bcs NextDown
 jsr RdGroundCollisionResponse
 jmp Horizontal
NextDown:dec RdMoveCount
 bne DownLoop
Horizontal:jsr RdHorizontalAccelerate
 jsr RdHostRelativeX
 lda RdDelta
 bpl Right
 jsr RdControlNegate
 ldy RdSlow
 beq LeftCount
 lsr
 beq End
LeftCount:sta RdMoveCount
Left:jsr RdHostMoveLeft
 jsr RdControlSideResponse
 dec RdMoveCount
 bne Left
 lda RdDoorMove
 beq End
 lda #1
 jmp RdHostDoorDirection
Right:beq End
 ldy RdSlow
 beq RightCount
 lsr
 beq End
RightCount:sta RdMoveCount
RightLoop:jsr RdHostMoveRight
 jsr RdControlSideResponse
 dec RdMoveCount
 bne RightLoop
 lda RdDoorMove
 beq End
 lda #0
 jmp RdHostDoorDirection
End:rts
.endproc
.proc RdControlSideResponse
 bcs End
 lda #1
 sta RdMoveCount
 lda RdGravity
 bne End
 lda RdAction
 cmp #3
 beq End
 jmp RdC_CF55
End:rts
.endproc
.proc RdControlVerticalAdmission
 lda RdGravity
 bne Accelerate
 lda #$18
 jsr RdSetMaxSpeed
 lda RdY
 clc
 adc RdRadiusY
 and #7
 bne Support
 jsr RdHostProbeDown
 bcc Accelerate
Support:jsr RdHostFindSupport
 lda RdElevator
 bne Accelerate
 lda RdFrozenSupport
 bne Accelerate
 lda #$1a
 jsr RdSetGravity
Accelerate:jmp RdVerticalAccelerate
.endproc
RdC_CC36: lda $5c29 ; source62:CC36
RdC_CC38: and #$cf ; source62:CC38
RdC_CC3A: BEQ RdC_CC41 ; source62:CC3A
RdC_CC3C: JSR RdC_CF5D ; source62:CC3C
RdC_CC3F: lda $5c29 ; source62:CC3F
RdC_CC41: and #$07 ; source62:CC41
RdC_CC43: BNE RdC_CC4B ; source62:CC43
RdC_CC45: lda $5c28 ; source62:CC45
RdC_CC47: and #$08 ; source62:CC47
RdC_CC49: BEQ RdC_CC5B ; source62:CC49
RdC_CC4B: JSR RdControlBitIndex ; source62:CC4B
RdC_CC4E: cmp #$02 ; source62:CC4E
RdC_CC50: BCS RdC_CC54 ; source62:CC50
RdC_CC52: sta $5c2c ; source62:CC52
RdC_CC54: tax ; source62:CC54
RdC_CC55: LDA RdControlActionFromDirection,X ; source62:CC55
RdC_CC58: sta $5c00 ; source62:CC58
RdC_CC5B: lda $5c28 ; source62:CC5B
RdC_CC5D: ora $5c34 ; source62:CC5D
RdC_CC5F: asl a ; source62:CC5F
RdC_CC60: BPL RdC_CC65 ; source62:CC60
RdC_CC62: JSR RdControlFire ; source62:CC62
RdC_CC65: bit $5c28 ; source62:CC65
RdC_CC67: BPL RdC_CC6E ; source62:CC67
RdC_CC69: lda #$02 ; source62:CC69
RdC_CC6B: sta $5c00 ; source62:CC6B
RdC_CC6E: lda #$04 ; source62:CC6E
RdC_CC70: JSR RdC_CD6D ; source62:CC70
RdC_CC73: lda $5c00 ; source62:CC73
RdC_CC76: cmp #$05 ; source62:CC76
RdC_CC78: BCS RdC_CC97 ; source62:CC78
RdC_CC7A: JMP RdControlStandFollow ; source62:CC7A
RdC_CC8B: lda #$50 ; source62:CC8B
RdC_CC8D: sta $5c0f ; source62:CC8D
RdC_CC90: lda #$32 ; source62:CC90
RdC_CC92: JSR RdSetAnimation ; source62:CC92
RdC_CC95: sta $5c19 ; source62:CC95
RdC_CC97: rts ; source62:CC97
RdC_CC98: lda #$09 ; source62:CC98
RdC_CC9A: sta $5c18 ; source62:CC9A
RdC_CC9C: ldx #$00 ; source62:CC9C
RdC_CC9E: lda $5c05 ; source62:CC9E
RdC_CCA1: cmp #$07 ; source62:CCA1
RdC_CCA3: BEQ RdC_CCAF ; source62:CCA3
RdC_CCA5: inx ; source62:CCA5
RdC_CCA6: cmp #$27 ; source62:CCA6
RdC_CCA8: BEQ RdC_CCAF ; source62:CCA8
RdC_CCAA: lda #$04 ; source62:CCAA
RdC_CCAC: JSR RdControlSetIndex ; source62:CCAC
RdC_CCAF: LDA RdControlRunAnimation,X ; source62:CCAF
RdC_CCB2: sta $5c05 ; source62:CCB2
RdC_CCB5: ldx $5c2c ; source62:CCB5
RdC_CCB7: LDA RdSetGroundAcceleration::Acceleration,X ; source62:CCB7
RdC_CCBA: sta $5c15 ; source62:CCBA
RdC_CCBD: rts ; source62:CCBD
RdC_CCC2: ldx $5c2c ; source62:CCC2
RdC_CCC4: lda $5c14 ; source62:CCC4
RdC_CCC7: BEQ RdC_CD23 ; source62:CCC7
RdC_CCC9: ldy $5c0f ; source62:CCC9
RdC_CCCC: bit $5c08 ; source62:CCCC
RdC_CCCF: BMI RdC_CCDC ; source62:CCCF
RdC_CCD1: cpy #$00 ; source62:CCD1
RdC_CCD3: BCS RdC_CD02 ; source62:CCD3
RdC_CCD5: lda #$0c ; source62:CCD5
RdC_CCD7: sta $5c05 ; source62:CCD7
RdC_CCDA: BCC RdC_CD02 ; source62:CCDA
RdC_CCDC: cpy #$18 ; source62:CCDC
RdC_CCDE: BCC RdC_CD02 ; source62:CCDE
RdC_CCE0: lda $5c05 ; source62:CCE0
RdC_CCE3: cmp #$20 ; source62:CCE3
RdC_CCE5: BEQ RdC_CCEC ; source62:CCE5
RdC_CCE7: lda #$0e ; source62:CCE7
RdC_CCE9: sta $5c05 ; source62:CCE9
RdC_CCEC: cpy #$20 ; source62:CCEC
RdC_CCEE: BCC RdC_CD02 ; source62:CCEE
RdC_CCF0: lda $5c29 ; source62:CCF0
RdC_CCF2: and #$08 ; source62:CCF2
RdC_CCF4: BEQ RdC_CCFB ; source62:CCF4
RdC_CCF6: lda #$35 ; source62:CCF6
RdC_CCF8: sta $5c05 ; source62:CCF8
RdC_CCFB: bit $5c29 ; source62:CCFB
RdC_CCFD: BMI RdC_CD02 ; source62:CCFD
RdC_CCFF: JSR RdStopVertical ; source62:CCFF
RdC_CD02: lda #$99 ; source62:CD02
RdC_CD04: cmp $5c05 ; source62:CD04
RdC_CD07: BNE RdC_CD0E ; source62:CD07
RdC_CD09: lda #$0c ; source62:CD09
RdC_CD0B: sta $5c05 ; source62:CD0B
RdC_CD0E: lda $5c1a ; source62:CD0E
RdC_CD10: BEQ RdC_CD16 ; source62:CD10
RdC_CD12: lda $5c28 ; source62:CD12
RdC_CD14: BMI RdC_CD40 ; source62:CD14
RdC_CD16: JSR RdC_CF88 ; source62:CD16
RdC_CD19: JSR RdC_D09C ; source62:CD19
RdC_CD1C: JSR RdC_CF2E ; source62:CD1C
RdC_CD1F: lda #$02 ; source62:CD1F
RdC_CD21: BNE RdC_CD6D ; source62:CD21
RdC_CD23: lda $5c07 ; source62:CD23
RdC_CD26: BNE RdC_CD2B ; source62:CD26
RdC_CD28: JSR RdC_CCB7 ; source62:CD28
RdC_CD2B: JSR RdC_CDBF ; source62:CD2B
RdC_CD2E: dec $5c18 ; source62:CD2E
RdC_CD30: BNE RdC_CD39 ; source62:CD30
RdC_CD32: lda #$09 ; source62:CD32
RdC_CD34: sta $5c18 ; source62:CD34
RdC_CD36: JSR RdWalkRequest ; source62:CD36
RdC_CD39: JSR RdC_CF2E ; source62:CD39
RdC_CD3C: lda $5c28 ; source62:CD3C
RdC_CD3E: BPL RdC_CD4B ; source62:CD3E
RdC_CD40: JSR RdStartJump ; source62:CD40
RdC_CD43: lda #$12 ; source62:CD43
RdC_CD45: JSR RdSetMaxSpeed ; source62:CD45
RdC_CD48: JMP RdC_CD6B ; source62:CD48
RdC_CD4B: ora $5c34 ; source62:CD4B
RdC_CD4D: asl a ; source62:CD4D
RdC_CD4E: BPL RdC_CD53 ; source62:CD4E
RdC_CD50: JSR RdC_CDD7 ; source62:CD50
RdC_CD53: lda $5c29 ; source62:CD53
RdC_CD55: and #$03 ; source62:CD55
RdC_CD57: BNE RdC_CD5F ; source62:CD57
RdC_CD59: JSR RdC_CF55 ; source62:CD59
RdC_CD5C: JMP RdC_CD6B ; source62:CD5C
RdC_CD5F: JSR RdControlBitIndex ; source62:CD5F
RdC_CD62: cmp $5c2c ; source62:CD62
RdC_CD64: BEQ RdC_CD6B ; source62:CD64
RdC_CD66: sta $5c2c ; source62:CD66
RdC_CD68: JSR RdC_CC98 ; source62:CD68
RdC_CD6B: lda #$05 ; source62:CD6B
RdC_CD6D: JSR RdControlAdvance ; source62:CD6D
RdC_CD70: JSR RdC_CD9C ; source62:CD70
RdC_CD73: BCS RdC_CD7E ; source62:CD73
RdC_CD75: lda $5c2e ; source62:CD75
RdC_CD77: lsr a ; source62:CD77
RdC_CD78: and #$03 ; source62:CD78
RdC_CD7A: ora #$a0 ; source62:CD7A
RdC_CD7C: sta $5c3c ; source62:CD7C
RdC_CD7E: JSR RdC_CDFA ; source62:CD7E
RdC_CD81: JSR RdControlPhysics ; source62:CD81
RdC_CD84: lda $5c7b ; source62:CD84
RdC_CD86: BEQ RdC_CD8C ; source62:CD86
RdC_CD88: lda #$a1 ; source62:CD88
RdC_CD8A: sta $5c3c ; source62:CD8A
RdC_CD8C: JSR RdC_CD92 ; source62:CD8C
RdC_CD8F: JMP RdHostDrawPlayer ; source62:CD8F
RdC_CD92: lda $5c2c ; source62:CD92
RdC_CD94: JSR RdTimes16 ; source62:CD94
RdC_CD97: ora $5c3c ; source62:CD97
RdC_CD99: sta $5c3c ; source62:CD99
RdC_CD9B: rts ; source62:CD9B
RdC_CD9C: sec ; source62:CD9C
RdC_CD9D: ldy $5c00 ; source62:CD9D
RdC_CDA0: dey ; source62:CDA0
RdC_CDA1: BNE RdC_CDBE ; source62:CDA1
RdC_CDA3: lda $5fb0 ; source62:CDA3
RdC_CDA6: and #$08 ; source62:CDA6
RdC_CDA8: BEQ RdC_CDBE ; source62:CDA8
RdC_CDAA: lda $5c05 ; source62:CDAA
RdC_CDAD: cmp #$0e ; source62:CDAD
RdC_CDAF: BEQ RdC_CDBB ; source62:CDAF
RdC_CDB1: cmp #$0c ; source62:CDB1
RdC_CDB3: sec ; source62:CDB3
RdC_CDB4: BNE RdC_CDBE ; source62:CDB4
RdC_CDB6: bit $5c08 ; source62:CDB6
RdC_CDB9: BPL RdC_CDBE ; source62:CDB9
RdC_CDBB: cmp $5c06 ; source62:CDBB
RdC_CDBE: rts ; source62:CDBE
RdC_CDBF: lda $5c29 ; source62:CDBF
RdC_CDC1: and #$08 ; source62:CDC1
RdC_CDC3: lsr a ; source62:CDC3
RdC_CDC4: lsr a ; source62:CDC4
RdC_CDC5: lsr a ; source62:CDC5
RdC_CDC6: tax ; source62:CDC6
RdC_CDC7: LDA RdControlRunAnimation,X ; source62:CDC7
RdC_CDCA: cmp $5c05 ; source62:CDCA
RdC_CDCD: BEQ RdC_CDBE ; source62:CDCD
RdC_CDCF: JSR RdSetAnimation ; source62:CDCF
RdC_CDD2: pla ; source62:CDD2
RdC_CDD3: pla ; source62:CDD3
RdC_CDD4: JMP RdC_CD6B ; source62:CDD4
RdC_CDD7: JSR RdControlFire ; source62:CDD7
RdC_CDDA: lda $5c29 ; source62:CDDA
RdC_CDDC: and #$08 ; source62:CDDC
RdC_CDDE: BNE RdC_CDE6 ; source62:CDDE
RdC_CDE0: lda #$22 ; source62:CDE0
RdC_CDE2: sta $5c06 ; source62:CDE2
RdC_CDE5: rts ; source62:CDE5
RdC_CDE6: lda $5c06 ; source62:CDE6
RdC_CDE9: sec ; source62:CDE9
RdC_CDEA: sbc $5c05 ; source62:CDEA
RdC_CDED: and #$03 ; source62:CDED
RdC_CDEF: tax ; source62:CDEF
RdC_CDF0: LDA RdControlRunFireAnimation,X ; source62:CDF0
RdC_CDF3: JMP RdControlSetIndex ; source62:CDF3
RdC_CDFA: lda $5c0a ; source62:CDFA
RdC_CDFD: and #$20 ; source62:CDFD
RdC_CDFF: BEQ RdC_CE30 ; source62:CDFF
RdC_CE01: lda #$32 ; source62:CE01
RdC_CE03: sta $5c1c ; source62:CE03
RdC_CE05: lda #$ff ; source62:CE05
RdC_CE07: sta $5c1d ; source62:CE07
RdC_CE09: lda $5c1e ; source62:CE09
RdC_CE0B: sta $5c1f ; source62:CE0B
RdC_CE0D: BEQ RdC_CE1E ; source62:CE0D
RdC_CE0F: BPL RdC_CE14 ; source62:CE0F
RdC_CE11: JSR RdControlHurtSound ; source62:CE11
RdC_CE14: lda $5c0a ; source62:CE14
RdC_CE17: and #$08 ; source62:CE17
RdC_CE19: lsr a ; source62:CE19
RdC_CE1A: lsr a ; source62:CE1A
RdC_CE1B: lsr a ; source62:CE1B
RdC_CE1C: sta $5c1d ; source62:CE1C
RdC_CE1E: JSR RdControlHurtLaunch ; source62:CE1E
RdC_CE21: nop ; source62:CE21
RdC_CE22: nop ; source62:CE22
RdC_CE23: nop ; source62:CE23
RdC_CE24: nop ; source62:CE24
RdC_CE25: nop ; source62:CE25
RdC_CE26: nop ; source62:CE26
RdC_CE27: nop ; source62:CE27
RdC_CE28: JSR RdC_CE84 ; source62:CE28
RdC_CE2B: BNE RdC_CE30 ; source62:CE2B
RdC_CE2D: JMP RdC_CE66 ; source62:CE2D
RdC_CE30: lda $5c1c ; source62:CE30
RdC_CE32: BEQ RdC_CE66 ; source62:CE32
RdC_CE34: dec $5c1c ; source62:CE34
RdC_CE36: ldx $5c1d ; source62:CE36
RdC_CE38: inx ; source62:CE38
RdC_CE39: BEQ RdC_CE53 ; source62:CE39
RdC_CE3B: JSR RdDivide16 ; source62:CE3B
RdC_CE3E: cmp #$03 ; source62:CE3E
RdC_CE40: BCS RdC_CE4A ; source62:CE40
RdC_CE42: ldy $5c15 ; source62:CE42
RdC_CE45: BNE RdC_CE53 ; source62:CE45
RdC_CE47: JSR RdC_CF4E ; source62:CE47
RdC_CE4A: dex ; source62:CE4A
RdC_CE4B: BNE RdC_CE50 ; source62:CE4B
RdC_CE4D: JSR RdControlNegate ; source62:CE4D
RdC_CE50: sta $5c09 ; source62:CE50
RdC_CE53: lda $5c1f ; source62:CE53
RdC_CE55: BPL RdC_CE66 ; source62:CE55
RdC_CE57: lda $5c2e ; source62:CE57
RdC_CE59: and #$01 ; source62:CE59
RdC_CE5B: BNE RdC_CE66 ; source62:CE5B
RdC_CE5D: tay ; source62:CE5D
RdC_CE5E: sty $5c04 ; source62:CE5E
RdC_CE61: ldy #$f7 ; source62:CE61
RdC_CE63: sty $5c03 ; source62:CE63
RdC_CE66: ldy $5fb5 ; source62:CE66
RdC_CE69: dey ; source62:CE69
RdC_CE6A: BMI RdC_CE75 ; source62:CE6A
RdC_CE6C: BNE RdC_CE7E ; source62:CE6C
RdC_CE6E: lda $5fb4 ; source62:CE6E
RdC_CE71: cmp #$70 ; source62:CE71
RdC_CE73: BCS RdC_CE7E ; source62:CE73
RdC_CE75: lda $5c2e ; source62:CE75
RdC_CE77: and #$0f ; source62:CE77
RdC_CE79: BNE RdC_CE7E ; source62:CE79
RdC_CE7B: JSR RdHostLowHealthSound ; source62:CE7B
RdC_CE7E: lda #$00 ; source62:CE7E
RdC_CE80: JSR RdHostHealthSound ; source62:CE80
RdC_CE83: rts ; source62:CE83
RdC_CE84: lda $5c00 ; source62:CE84
RdC_CE87: cmp #$07 ; source62:CE87
RdC_CE89: BEQ RdC_CE91 ; source62:CE89
RdC_CE8B: cmp #$08 ; source62:CE8B
RdC_CE8D: BEQ RdC_CE91 ; source62:CE8D
RdC_CE8F: cmp #$ff ; source62:CE8F
RdC_CE91: rts ; source62:CE91
RdC_CF2E: lda $5c0a ; source62:CF2E
RdC_CF31: lsr a ; source62:CF31
RdC_CF32: and #$02 ; source62:CF32
RdC_CF34: BEQ RdC_CF54 ; source62:CF34
RdC_CF36: BCS RdC_CF3F ; source62:CF36
RdC_CF38: lda $5c15 ; source62:CF38
RdC_CF3B: BMI RdC_CF54 ; source62:CF3B
RdC_CF3D: BPL RdC_CF46 ; source62:CF3D
RdC_CF3F: lda $5c15 ; source62:CF3F
RdC_CF42: BMI RdC_CF46 ; source62:CF42
RdC_CF44: BNE RdC_CF54 ; source62:CF44
RdC_CF46: JSR RdControlNegate ; source62:CF46
RdC_CF49: sta $5c15 ; source62:CF49
RdC_CF4C: ldy #$00 ; source62:CF4C
RdC_CF4E: sty $5c09 ; source62:CF4E
RdC_CF51: sty $5c13 ; source62:CF51
RdC_CF54: rts ; source62:CF54
RdC_CF55: lda $5c15 ; source62:CF55
RdC_CF58: BNE RdC_CF5D ; source62:CF58
RdC_CF5A: JSR RdWalkRequest ; source62:CF5A
RdC_CF5D: JSR RdC_CF81 ; source62:CF5D
RdC_CF60: sty $5c00 ; source62:CF60
RdC_CF63: lda $5c29 ; source62:CF63
RdC_CF65: and #$08 ; source62:CF65
RdC_CF67: BNE RdC_CF77 ; source62:CF67
RdC_CF69: lda #$07 ; source62:CF69
 jmp RdSetAnimation
RdC_CF77: lda #$04 ; source62:CF77
RdC_CF79: sta $5c00 ; source62:CF79
RdC_CF7C: lda #$27 ; source62:CF7C
RdC_CF7E: JSR RdSetAnimation ; source62:CF7E
RdC_CF81: JSR RdC_CFB7 ; source62:CF81
RdC_CF84: sty $5c04 ; source62:CF84
RdC_CF87: rts ; source62:CF87
RdC_CF88: lda $5c29 ; source62:CF88
RdC_CF8A: and #$03 ; source62:CF8A
RdC_CF8C: BEQ RdC_CFA9 ; source62:CF8C
RdC_CF8E: JSR RdControlBitIndex ; source62:CF8E
RdC_CF91: tax ; source62:CF91
RdC_CF92: JSR RdC_CCB7 ; source62:CF92
RdC_CF95: lda $5c14 ; source62:CF95
RdC_CF98: BMI RdC_CFBD ; source62:CF98
RdC_CF9A: lda $5c05 ; source62:CF9A
RdC_CF9D: cmp #$0e ; source62:CF9D
RdC_CF9F: BEQ RdC_CFBD ; source62:CF9F
RdC_CFA1: stx $5c2c ; source62:CFA1
RdC_CFA3: LDA RdAirControl::Spin+1,X ; source62:CFA3
RdC_CFA6: JMP RdSetAnimation ; source62:CFA6
RdC_CFA9: lda $5c14 ; source62:CFA9
RdC_CFAC: BMI RdC_CFBD ; source62:CFAC
RdC_CFAE: BEQ RdC_CFBD ; source62:CFAE
RdC_CFB0: lda $5c05 ; source62:CFB0
RdC_CFB3: cmp #$0c ; source62:CFB3
RdC_CFB5: BNE RdC_CFBD ; source62:CFB5
RdC_CFB7: JSR RdC_CF4C ; source62:CFB7
RdC_CFBA: sty $5c15 ; source62:CFBA
RdC_CFBD: rts ; source62:CFBD
RdC_D015: JSR RdAirControl ; source62:D015
RdC_D018: JSR RdC_CF2E ; source62:D018
RdC_D01B: lda $5c29 ; source62:D01B
RdC_D01D: and #$08 ; source62:D01D
RdC_D01F: BEQ RdC_D02B ; source62:D01F
RdC_D021: lda #$35 ; source62:D021
RdC_D023: sta $5c05 ; source62:D023
RdC_D026: lda #$06 ; source62:D026
RdC_D028: sta $5c00 ; source62:D028
RdC_D02B: JSR RdC_D09C ; source62:D02B
RdC_D02E: lda $5c1a ; source62:D02E
RdC_D030: BEQ RdC_D03C ; source62:D030
RdC_D032: lda $5c28 ; source62:D032
RdC_D034: BPL RdC_D03C ; source62:D034
RdC_D036: JSR RdStartJump ; source62:D036
RdC_D039: JMP RdC_CD6B ; source62:D039
RdC_D03C: lda $5c14 ; source62:D03C
RdC_D03F: BNE RdC_D050 ; source62:D03F
RdC_D041: lda $5c00 ; source62:D041
RdC_D044: cmp #$06 ; source62:D044
RdC_D046: BNE RdC_D04D ; source62:D046
RdC_D048: JSR RdC_CF77 ; source62:D048
RdC_D04B: BNE RdC_D050 ; source62:D04B
RdC_D04D: JSR RdC_CF55 ; source62:D04D
RdC_D050: lda #$03 ; source62:D050
RdC_D052: JMP RdC_CD6D ; source62:D052
RdC_D09C: lda $5c28 ; source62:D09C
RdC_D09E: ora $5c34 ; source62:D09E
RdC_D0A0: asl a ; source62:D0A0
RdC_D0A1: jpl RdControlReturn ; source62:D0A1
RdC_D0A3: lda $5c05 ; source62:D0A3
RdC_D0A6: cmp #$35 ; source62:D0A6
RdC_D0A8: BNE RdC_D0AD ; source62:D0A8
RdC_D0AA: JMP RdControlFireUp ; source62:D0AA
RdC_D0AD: JSR RdControlFireHorizontal ; source62:D0AD
RdC_D0B0: lda #$20 ; source62:D0B0
RdC_D0B2: JMP RdSetAnimation ; source62:D0B2
RdC_D0B5: lda $5c0d ; source62:D0B5
RdC_D0B8: cmp #$e9 ; source62:D0B8
RdC_D0BA: BEQ RdC_D0C1 ; source62:D0BA
RdC_D0BC: adc #$03 ; source62:D0BC
RdC_D0BE: inc $5c08 ; source62:D0BE
RdC_D0C1: lda $5c2c ; source62:D0C1
RdC_D0C3: lda #$16 ; source62:D0C3
RdC_D0C5: sta $5c05 ; source62:D0C5
RdC_D0C8: sta $5c06 ; source62:D0C8
RdC_D0CB: nop ; source62:D0CB
RdC_D0CC: nop ; source62:D0CC
RdC_D0CD: LDA RdControlMorphByteWindow,X ; source62:D0CD
RdC_D0D0: sta $5c15 ; source62:D0D0
RdC_D0D3: lda #$01 ; source62:D0D3
RdC_D0D5: sta $5c26 ; source62:D0D5
RdC_D0D8: JMP RdControlMorphSound ; source62:D0D8
RdC_D0DB: lda #$00 ; source62:D0DB
RdC_D0DD: sta $5c00 ; source62:D0DD
RdC_D0E0: rts ; source62:D0E0
RdC_D0E1: lda $5c28 ; source62:D0E1
RdC_D0E3: and #$08 ; source62:D0E3
RdC_D0E5: BNE RdC_D0F1 ; source62:D0E5
RdC_D0E7: JMP RdControlSpring ; source62:D0E7
RdC_D0EB: lda $5c29 ; source62:D0EB
RdC_D0ED: and #$04 ; source62:D0ED
RdC_D0EF: BNE RdC_D11E ; source62:D0EF
RdC_D0F1: lda $5c01 ; source62:D0F1
RdC_D0F4: clc ; source62:D0F4
RdC_D0F5: adc #$08 ; source62:D0F5
RdC_D0F7: sta $5c01 ; source62:D0F7
RdC_D0FA: JSR RdHostProbeUp ; source62:D0FA
RdC_D0FD: BCC RdC_D11E ; source62:D0FD
RdC_D0FF: ldx #$00 ; source62:D0FF
RdC_D101: JSR RdHostStagePosition ; source62:D101
RdC_D104: stx $5c3e ; source62:D104
RdC_D106: lda #$f5 ; source62:D106
RdC_D108: sta $5c3f ; source62:D108
RdC_D10A: JSR RdHostOffsetPosition ; source62:D10A
RdC_D10D: JSR RdHostCommitPosition ; source62:D10D
RdC_D110: JSR RdC_CF55 ; source62:D110
RdC_D113: dec $5c06 ; source62:D113
RdC_D116: JSR RdControlUnmorphNotify ; source62:D116
RdC_D119: lda #$04 ; source62:D119
RdC_D11B: JMP RdC_D9D4 ; source62:D11B
RdC_D11E: lda $5c28 ; source62:D11E
RdC_D120: JSR RdControlBitIndex ; source62:D120
RdC_D123: cmp #$02 ; source62:D123
RdC_D125: BCS RdC_D12E ; source62:D125
RdC_D127: sta $5c2c ; source62:D127
RdC_D129: lda #$16 ; source62:D129
RdC_D12B: JSR RdSetAnimation ; source62:D12B
RdC_D12E: ldx $5c2c ; source62:D12E
RdC_D130: JSR RdC_CCB7 ; source62:D130
RdC_D133: JSR RdC_CF2E ; source62:D133
RdC_D136: JSR RdBombAllocate ; source62:D136
RdC_D139: lda $5c29 ; source62:D139
RdC_D13B: and #$03 ; source62:D13B
RdC_D13D: BNE RdC_D142 ; source62:D13D
RdC_D13F: JSR RdC_CFB7 ; source62:D13F
RdC_D142: lda #$02 ; source62:D142
RdC_D144: JMP RdC_CD6D ; source62:D144
RdC_D198: lda $5c29 ; source62:D198
RdC_D19A: and #$08 ; source62:D19A
RdC_D19C: BNE RdC_D1A3 ; source62:D19C
RdC_D19E: lda #$00 ; source62:D19E
RdC_D1A0: sta $5c00 ; source62:D1A0
RdC_D1A3: lda $5c29 ; source62:D1A3
RdC_D1A5: and #$07 ; source62:D1A5
RdC_D1A7: BEQ RdC_D1B9 ; source62:D1A7
RdC_D1A9: JSR RdControlBitIndex ; source62:D1A9
RdC_D1AC: cmp #$02 ; source62:D1AC
RdC_D1AE: BCS RdC_D1B2 ; source62:D1AE
RdC_D1B0: sta $5c2c ; source62:D1B0
RdC_D1B2: tax ; source62:D1B2
RdC_D1B3: LDA RdControlActionFromDirection,X ; source62:D1B3
RdC_D1B6: sta $5c00 ; source62:D1B6
RdC_D1B9: lda $5c28 ; source62:D1B9
RdC_D1BB: ora $5c34 ; source62:D1BB
RdC_D1BD: asl a ; source62:D1BD
RdC_D1BE: BPL RdC_D1C3 ; source62:D1BE
RdC_D1C0: JSR RdControlFire ; source62:D1C0
RdC_D1C3: bit $5c28 ; source62:D1C3
RdC_D1C5: BPL RdC_D1CC ; source62:D1C5
RdC_D1C7: lda #$06 ; source62:D1C7
RdC_D1C9: sta $5c00 ; source62:D1C9
RdC_D1CC: lda #$04 ; source62:D1CC
RdC_D1CE: JSR RdC_CD6D ; source62:D1CE
RdC_D1D1: lda $5c00 ; source62:D1D1
 jmp RdControlAimFollow
RdC_D41A: lda #$01 ; source62:D41A
RdC_D41C: JMP RdC_CD6D ; source62:D41C
RdC_D41F: dec $5c04 ; source62:D41F
RdC_D422: rts ; source62:D422
RdC_D9D4: JSR RdHostProbeDown ; source62:D9D4
RdC_D9D7: BCC RdC_DA07 ; source62:D9D7
RdC_D9D9: lda $5c0d ; source62:D9D9
RdC_D9DC: cmp #$03 ; source62:D9DC
RdC_D9DE: BCC RdC_D9E5 ; source62:D9DE
RdC_D9E0: sbc #$03 ; source62:D9E0
RdC_D9E2: sta $5c0d ; source62:D9E2
RdC_D9E5: lda #$08 ; source62:D9E5
RdC_D9E7: sta $5c1b ; source62:D9E7
RdC_D9E9: lda $5c08 ; source62:D9E9
RdC_D9EC: lsr a ; source62:D9EC
RdC_D9ED: pha ; source62:D9ED
RdC_D9EE: JSR RdStartJump ; source62:D9EE
RdC_D9F1: pla ; source62:D9F1
RdC_D9F2: BPL RdC_D9F6 ; source62:D9F2
RdC_D9F4: lda #$00 ; source62:D9F4
RdC_D9F6: sta $5c08 ; source62:D9F6
RdC_D9F9: lda #$0c ; source62:D9F9
RdC_D9FB: JSR RdSetAnimation ; source62:D9FB
RdC_D9FE: JSR RdC_D144 ; source62:D9FE
RdC_DA01: lda #$02 ; source62:DA01
RdC_DA03: sta $5c00 ; source62:DA03
RdC_DA06: rts ; source62:DA06
RdC_DA07: JMP RdC_D144 ; source62:DA07
RdC_DA0A: lda $5c1b ; source62:DA0A
RdC_DA0C: BNE RdC_DA22 ; source62:DA0C
RdC_DA0E: lda $5fb0 ; source62:DA0E
RdC_DA11: and #$10 ; source62:DA11
RdC_DA13: BEQ RdC_DA22 ; source62:DA13
RdC_DA15: lda $5c28 ; source62:DA15
RdC_DA17: and #$04 ; source62:DA17
RdC_DA19: BEQ RdC_DA22 ; source62:DA19
RdC_DA1B: sta $5c28 ; source62:DA1B
RdC_DA1D: sta $5c29 ; source62:DA1D
RdC_DA1F: JMP RdC_CC36 ; source62:DA1F
RdC_DA22: JMP RdControlJump ; source62:DA22
RdC_DA25: lda $5c28 ; source62:DA25
RdC_DA27: and #$04 ; source62:DA27
RdC_DA29: BEQ RdC_DA40 ; source62:DA29
RdC_DA2B: lda $5fb0 ; source62:DA2B
RdC_DA2E: and #$10 ; source62:DA2E
RdC_DA30: BNE RdC_DA37 ; source62:DA30
RdC_DA32: JSR RdHostProbeDown ; source62:DA32
RdC_DA35: BCS RdC_DA40 ; source62:DA35
RdC_DA37: lda #$04 ; source62:DA37
RdC_DA39: sta $5c28 ; source62:DA39
RdC_DA3B: sta $5c29 ; source62:DA3B
RdC_DA3D: JMP RdC_CC36 ; source62:DA3D
RdC_DA40: lda $5c08 ; source62:DA40
RdC_DA43: BEQ RdC_DA46 ; source62:DA43
RdC_DA45: nop ; source62:DA45
RdC_DA46: lda $5fb0 ; source62:DA46
RdC_DA49: and #$04 ; source62:DA49
RdC_DA4B: BEQ RdC_DA6B ; source62:DA4B
RdC_DA4D: lda $5c28 ; source62:DA4D
RdC_DA4F: BPL RdC_DA6B ; source62:DA4F
RdC_DA51: lda #$01 ; source62:DA51
RdC_DA53: bit $5c29 ; source62:DA53
RdC_DA55: BNE RdC_DA63 ; source62:DA55
RdC_DA57: asl a ; source62:DA57
RdC_DA58: bit $5c29 ; source62:DA58
RdC_DA5A: BEQ RdC_DA6B ; source62:DA5A
RdC_DA5C: JSR RdHostProbeLeft ; source62:DA5C
RdC_DA5F: BCS RdC_DA6B ; source62:DA5F
RdC_DA61: BCC RdC_DA68 ; source62:DA61
RdC_DA63: JSR RdHostProbeRight ; source62:DA63
RdC_DA66: BCS RdC_DA6B ; source62:DA66
RdC_DA68: JSR RdC_CD40 ; source62:DA68
RdC_DA6B: lda #$00 ; source62:DA6B
RdC_DA6D: sta $5c7e ; source62:DA6D
RdC_DA6F: JMP RdC_CCC2 ; source62:DA6F
RdC_DA72: lda $5c29 ; source62:DA72
RdC_DA74: and #$08 ; source62:DA74
RdC_DA76: BNE RdC_DA82 ; source62:DA76
RdC_DA78: lda #$0c ; source62:DA78
RdC_DA7A: sta $5c05 ; source62:DA7A
RdC_DA7D: lda #$02 ; source62:DA7D
RdC_DA7F: sta $5c00 ; source62:DA7F
RdC_DA82: JMP RdC_DA0A ; source62:DA82
RdControlMorphByteWindow:
 .byte $30,$d0,$a6,$4d,$ad,$14,$03,$f0,$5a,$ac,$0f,$03,$2c,$08,$03,$30
 .byte $0b,$c0,$00,$b0,$2d,$a9,$0c,$8d,$05,$03,$90,$26,$c0,$18,$90,$22
 .byte $ad,$05,$03,$c9,$20,$f0,$05,$a9,$0e,$8d,$05,$03,$c0,$20,$90,$12
 .byte $a5,$14,$29,$08,$f0,$05,$a9,$35,$8d,$05,$03,$24,$14,$30,$03,$20
 .byte $47,$d1,$a9,$99,$cd,$05,$03,$d0,$05,$a9,$0c,$8d,$05,$03,$a5,$64
 .byte $f0,$04,$a5,$12,$30,$2a,$20,$88,$cf,$20,$9c,$d0,$20,$2e,$cf,$a9
 .byte $02,$d0,$4a,$ad,$07,$03,$d0,$03,$20,$b7,$cc,$20,$bf,$cd,$c6,$53
 .byte $d0,$07,$a9,$09,$85,$53,$20,$96,$cb,$20,$2e,$cf,$a5,$12,$10,$0b
 .byte $20,$c3,$cf,$a9,$12,$20,$61,$dc,$4c,$6b,$cd,$05,$16,$0a,$10,$03
 .byte $20,$d7,$cd,$a5,$14,$29,$03,$d0,$06,$20,$55,$cf,$4c,$6b,$cd,$20
 .byte $e1,$e1,$c5,$4d,$f0,$05,$85,$4d,$20,$98,$cc,$a9,$05,$20,$96,$db
 .byte $20,$9c,$cd,$b0,$09,$a5,$2d,$4a,$29,$03,$09,$a0,$85,$6b,$20,$fa
 .byte $cd,$20,$e6,$db,$a5,$92,$f0,$04,$a9,$a1,$85,$6b,$20,$92,$cd,$4c
 .byte $4a,$de,$a5,$4d,$20,$c5,$c2,$05,$6b,$85,$6b,$60,$38,$ac,$00,$03
 .byte $88,$d0,$1b,$ad,$78,$68,$29,$08,$f0,$14,$ad,$05,$03,$c9,$0e,$f0
 .byte $0a,$c9,$0c,$38,$d0,$08,$2c,$08,$03,$10,$03,$cd,$06,$03,$60,$a5
.export RdControlEnd
RdControlEnd:
.popseg
