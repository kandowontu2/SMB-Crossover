; Pure target resolver. Incoming A=3*service, returned A=rawbank,C=valid.
; It never executes a callback. The original BT row preserves native AXYP.
.setcpu "6502"
.macpack longbranch
.include "common.inc"
.import BtCheck,SafereturnA_SMC,NextBank_SMC
.import BwColdPrepare,BwColdDraw,BwFresh,CmHostFresh,FmQueueName,JnResetDispatch
.import BwColors,BwStatusName,HuNativeWorldPalette,OperMode_Task
.export BwBtResolve
.segment "BW_ROM_ROUTER"
BwBtResolve:
 pha
 lda SelectedCharacter
 cmp #27
 beq BwResolveBowser
 pla
 BwFar BtCheck,jsr
 bcc BwResolveBad
 jmp BwResolveRAM
BwResolveBowser:
 pla
 cmp #6
 bne BwResolveROMTest
 ldx OperMode
 cpx #1
 bne BwResolveColdDraw
 ldx OperMode_Task
 cpx #3
 bne BwResolveColdDraw
BwResolveROMTest:
 ldx #7
BwResolveFind:
 cmp BwColdOffset,x
 beq BwResolveROM
 dex
 bpl BwResolveFind
 BwFar BwCheck,jsr
 bcc BwResolveBad
BwResolveRAM:
 sta FarcallJmpTarget_SMC+1
 lda #$a0
 sta FarcallJmpTarget_SMC+2
 lda #3
 sec
 rts
BwResolveColdDraw:
 ldx #2
BwResolveROM:
 lda BwColdLo,x
 sta FarcallJmpTarget_SMC+1
 lda BwColdHi,x
 sta FarcallJmpTarget_SMC+2
 lda BwColdBank,x
 sec
 rts
BwResolveBad:clc
 rts
BwColdOffset:.byte 9,45,51,54,57,78,90,96
BwColdLo:.byte <BwColdPrepare,<CmHostFresh,<BwColdDraw,<FmQueueName,<JnResetDispatch,<BwColors,<BwStatusName,<HuNativeWorldPalette
BwColdHi:.byte >BwColdPrepare,>CmHostFresh,>BwColdDraw,>FmQueueName,>JnResetDispatch,>BwColors,>BwStatusName,>HuNativeWorldPalette
BwColdBank:.byte .lobyte(.bank(BwColdPrepare)|$80),.lobyte(.bank(CmHostFresh)|$80),.lobyte(.bank(BwColdDraw)|$80),.lobyte(.bank(FmQueueName)|$80),.lobyte(.bank(JnResetDispatch)|$80),.lobyte(.bank(BwColors)|$80),.lobyte(.bank(BwStatusName)|$80),.lobyte(.bank(HuNativeWorldPalette)|$80)
.assert *<=$b300,lderror,"Own A67 target resolver fits213B"
