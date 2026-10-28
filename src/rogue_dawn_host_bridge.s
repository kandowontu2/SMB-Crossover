; PROPOSED host bridge only. No shared cfg allocation or integrated ROM yet.
; Requested C94 DF50..DFFE (175B), beside frozen Rogue ART endDF4E.
; All22 direct control callbacks enter while real A124/C94 is owned.
; RdHostDispatch is proposed A95; it MUST return with C94 unchanged.
; New state REQUESTS (not silently allocated): service5C79, transientA5FB7.
; Entry/return AXY/P preserved as callback semantics require; R0 is untouched.
; This bridge does not use/clobber the five shared farcall SMC operands.
.pushseg
.segment "ROGUE_DAWN_HOST_BRIDGE"
.export RdHostBridgeStart,RdHostBridgeEnd,RdHostCall95
.macro RdHostStub Name
Name:
 jsr RdHostCall95
 .byte 0 ; four-byte stride; never executed (common consumes this JSR return).
.endmacro
RdHostBridgeStart:
RdHostStub RdHostCommitPosition
RdHostStub RdHostDoor
RdHostStub RdHostDoorDirection
RdHostStub RdHostDrawPlayer
RdHostStub RdHostElevator
RdHostStub RdHostEnvironment
RdHostStub RdHostFindSupport
RdHostStub RdHostHealthSound
RdHostStub RdHostLowHealthSound
RdHostStub RdHostMoveDown
RdHostStub RdHostMoveLeft
RdHostStub RdHostMoveRight
RdHostStub RdHostMoveUp
RdHostStub RdHostOffsetPosition
RdHostStub RdHostProbeDown
RdHostStub RdHostProbeLeft
RdHostStub RdHostProbeRight
RdHostStub RdHostProbeUp
RdHostStub RdHostRelativeX
RdHostStub RdHostRelativeY
RdHostStub RdHostSpawnProjectile
RdHostStub RdHostStagePosition
.assert *-RdHostBridgeStart=22*4,error,"Fixed callback inventory/stride"

RdHostCall95:
 php
 pha
 txa
 pha
 tsx
 lda $0104,x                 ; actual stub JSR return low byte
 sec
 sbc #<(RdHostBridgeStart+2)
 lsr
 lsr
 sta RdHostService
 lda CurrentBank
 pha                         ; old A bank below temporary callback context
 lda #($80|95)
 sta CurrentBank
 sta $5115
 tsx
 lda $0104,x                 ; input P
 pha
 lda $0103,x                 ; input A
 sta RdHostEntryA
 lda $0102,x                 ; input X
 tax
 lda RdHostEntryA
 plp
 jsr RdHostDispatch          ; genuine C94 execution while A95 is mapped
 php                         ; callback output P/A/X, Y remains untouched
 pha
 txa
 pha
 tsx
 lda $0104,x                 ; true saved A owner, not a constant124
 sta CurrentBank
 sta $5115
 pla                         ; move output context over six dead entry bytes
 sta $0107,x
 pla
 sta $0108,x
 pla
 sta $0109,x
 txa
 clc
 adc #6
 tax
 txs
 pla
 tax
 pla
 plp
 rts                         ; original control caller, consuming no fake PC
RdHostBridgeEnd:
.assert .hibyte(RdHostBridgeStart)=.hibyte(RdHostBridgeStart+22*4-1),error,"Stub low-byte selector cannot wrap"
.assert RdHostBridgeEnd-RdHostBridgeStart<=176,error,"Proposed tail only"
.popseg
