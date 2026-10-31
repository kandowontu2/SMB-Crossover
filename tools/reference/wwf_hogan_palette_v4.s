; PRIVATE source proposal. All WWF phase/turn/palette state is selected C2.
; Existing CF route/fields remain genuine and separate.
.setcpu "6502"
.macpack longbranch
.include "runtime-macros.inc"
.import WfAuthC2,WfExpectedCookie,WfOwnerCookie,WfHostReady
.import WfRuntimeReturnOriginal,CurrentBankC,ReloadCHRBank
.import NextBank_SMC,SafereturnA_SMC,SafecallA_SMC,FarcallJmpTarget_SMC,FarCallCommon
.import SelectedCharacter,AreaType,SmFreezePaletteControl,SmFreezePalettePending
.import Sprite_Data,SprObject_SprAttrib,ObjectMetasprite,VRAM_Buffer1,VRAM_Buffer1_Offset
.import CfP1NativeRestore,FwMuxNativeSelect
.importzp R0,R1,R2,R3,R4,R5,R6,R7
.export WfP1Early,WfP1LateDispatch,WfP1Retire,WfP1Acquire
.export WfPaletteState,WfPaletteStateEnd,WfP1Epoch,WfP1Turn,WfP1Choice,WfP1Packet,WfP1Temp

.macro P1Far Target
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(Target)|$80)
 jsr FarCallCommon
.endmacro

.segment "WF_PALETTE_STATE"
WfPaletteState:
WfP1SavedAttributes:.res 24
WfP1Epoch:.res 1
WfP1Turn:.res 1
WfP1Choice:.res 1
WfP1Visible:.res 1
WfP1Packet:.res 7
WfP1Temp:.res 1
WfPaletteStateEnd:
.assert WfPaletteStateEnd-WfPaletteState=36,error,"Own measured palette state"

; These selected-code entries are INTERNAL: resident has already checked
; the complete cookie and owns C2; arbitrary direct calls are not an API.
.segment "WF_PALETTE_CODE"
WfP1Acquire:
 lda #0
 ldx #35
:sta WfPaletteState,x
 dex
 bpl :-
 rts
WfP1RestoreAttributes:
 ldx #23
:lda WfP1SavedAttributes,x
 sta SprObject_SprAttrib,x
 dex
 bpl :-
 rts
WfP1Early:
 lda WfP1Epoch
 cmp #$a7
 bne :+
 jsr WfP1RestoreAttributes
:
 ldx #23
EarlyActor:
 lda SprObject_SprAttrib,x
 sta WfP1SavedAttributes,x
 cpx #0
 beq EarlyNext
 lda ObjectMetasprite,x
 beq EarlyNext
 cmp #145
 bcs EarlyNext
 tay
 lda WfNativeP1Mask,y
 sta WfP1Temp
 lda SprObject_SprAttrib,x
 and #3
 tay
 lda Bits,y
 and WfP1Temp
 beq EarlyNext
 lda SprObject_SprAttrib,x
 ora #$10                    ; tags the COMPLETE native group
 sta SprObject_SprAttrib,x
EarlyNext:dex
 bpl EarlyActor
 lda #$a7
 sta WfP1Epoch                ; publish only after all originalattrs are saved
 rts
Bits:.byte 1,2,4,8

WfP1LateCore:
 lda WfP1Epoch
 cmp #$a7
 jne LateDone
 lda #0
 sta WfP1Epoch                ; consume before publication, never twice
 jsr WfP1RestoreAttributes
 lda #0
 sta WfP1Visible
 ldx #0
Scan:
 lda Sprite_Data,x
 cmp #240
 bcs ScanNext
 lda Sprite_Data+2,x
 and #$18
 cmp #8
 beq OwnPart
 cmp #16
 bne ScanNext
 lda #2
 bne Visible
OwnPart:lda #1
Visible:ora WfP1Visible
 sta WfP1Visible
ScanNext:inx
 inx
 inx
 inx
 bne Scan
 lda #2                       ; no queue room: hide both loan groups safely
 sta WfP1Choice
 ldx VRAM_Buffer1_Offset
 cpx #77
 bcs PaintStart
 lda WfP1Visible
 cmp #3
 beq Both
 and #1
 beq SetChoice
 lda #1
 bne SetChoice
Both:
 lda WfP1Turn
 eor #1
 and #1
 sta WfP1Turn                 ; advance only when the actual packet can fit
SetChoice:sta WfP1Choice
 jsr WfP1MakePacket
PaintStart:
 ldx #0
Paint:
 lda Sprite_Data+2,x
 and #$18
 cmp #8
 beq PaintOwn
 cmp #16
 bne ClearTag
 lda WfP1Choice
 beq ClearTag
 bne Hide
PaintOwn:
 lda WfP1Choice
 cmp #1
 beq ClearTag
Hide:lda #248
 sta Sprite_Data,x
ClearTag:
 lda Sprite_Data+2,x
 and #$e7
 sta Sprite_Data+2,x
 inx
 inx
 inx
 inx
 bne Paint
 lda WfP1Choice
 cmp #2
 beq LateDone
 jsr WfP1PublishPacket        ; complete OAM and packet before queue offset
LateDone:rts

.segment "WF_RUNTIME_A"
; Native DrawAll has completed. Non-WWF genuinely retains the old CF
; restore callback and its exact result; it is never routed into WWF C2.
WfP1LateDispatch:
 php
 pha
 lda SelectedCharacter
 cmp #29
 beq OwnLate
 pla
 plp
 P1Far CfP1NativeRestore
 rts
OwnLate:
 pla
 plp
 SaveRuntime
 jsr WfAuthC2
 bcc InvalidLate
 lda WfHostReady
 cmp #$a7
 bne InvalidLate
 jsr WfP1LateCore
 jmp WfRuntimeReturnOriginal
InvalidLate:
 jsr WfP1ClearInvalidTags
 jsr WfP1NativeRestore      ; genuine existing PRE-native restore request
 jmp WfRuntimeReturnOriginal

; No selected-state read or opcode occurs until all16 cookie bytes match.
; This independent path is called BEFORE WfRetire invalidates the cache.
WfP1Retire:
 SaveRuntime
 lda #2
 sta CurrentBankC
 sta $5116
 ldx #15
RetireByte:
 lda WfOwnerCookie,x
 cmp WfExpectedCookie,x
 bne RetireBad
 dex
 bpl RetireByte
 lda WfP1Epoch
 cmp #$a7
 bne :+
 jsr WfP1RestoreAttributes
:
 lda #0
 sta WfP1Epoch
 sta WfP1Turn
 jsr WfP1ClearOamTags
 jsr WfP1NativeRestore
 jmp WfRuntimeReturnOriginal
RetireBad:
 lda SelectedCharacter
 cmp #29
 bne RetireDone
 jsr WfP1ClearInvalidTags
 jsr WfP1NativeRestore
RetireDone:jmp WfRuntimeReturnOriginal

WfP1ClearInvalidTags:
 ldx #23
:lda SprObject_SprAttrib,x
 and #$ef
 sta SprObject_SprAttrib,x
 dex
 bpl :-
WfP1ClearOamTags:
 ldx #0
:lda Sprite_Data+2,x
 and #8
 beq :+
 lda #248
 sta Sprite_Data,x
:
 lda Sprite_Data+2,x
 and #$e7
 sta Sprite_Data+2,x
 inx
 inx
 inx
 inx
 bne :--
 rts

; Retire every complete ordinary queued WWF packet BEFORE the PRE-native
; restore is published. A complete command parser respects both native
; repeat and vertical flags; unsupported/malformed/zero256 tails are left
; untouched. No queue data or unrelated command is searched as a header.
; Actual Main/menu/scene calls own the in-flight negative-NmiDisable phase.
; Native PRE publication is LAST, and native-only shared data remains native.
WfP1NativeRestore:
 lda #0
 sta SmFreezePalettePending
 jsr WfP1CancelQueuedOwn
 P1Far FwMuxNativeSelect
 rts
WfP1CancelQueuedOwn:
 ldx SmFreezePaletteControl
 cpx #1
 bcc CancelArea
 cpx #5
 bcc CancelColors
 cpx #8
 bne CancelArea
 ldx #2
 bne CancelColors
CancelArea:
 ldx AreaType
 cpx #4
 bcc :+
 ldx #1
:inx
CancelColors:
 lda Native1-1,x
 sta R2
 lda Native2-1,x
 sta R3
 lda Native3-1,x
 sta R4
 ldx #0
CancelScan:
 cpx #77
 bcs CancelDone               ; last possible own packet header is76
 cpx VRAM_Buffer1_Offset
 bcs CancelDone
 lda VRAM_Buffer1,x
 beq CancelDone
 ; All native commands need a complete 3-byte header and payload.
 txa
 clc
 adc #3
 cmp VRAM_Buffer1_Offset
 bcs CancelDone
 lda VRAM_Buffer1+2,x
 and #$3f
 beq CancelDone              ; zero means256 native writes, cannot fit here
 sta R1
 lda VRAM_Buffer1+2,x
 and #$40
 beq :+
 lda #1                     ; repeat consumes just one payload byte
 sta R1
:txa
 clc
 adc #3
 adc R1
 bcs CancelDone
 cmp #84
 bcs CancelDone               ; native Buffer1 capacity, regardless bad offset
 cmp VRAM_Buffer1_Offset
 bcc :+
 bne CancelDone
:sta R0                     ; exact next native command, independent of data
 lda VRAM_Buffer1,x
 cmp #$3f
 bne CancelNext
 lda VRAM_Buffer1+1,x
 cmp #$15
 bne CancelNext
 lda VRAM_Buffer1+2,x
 cmp #3
 bne CancelNext
 lda VRAM_Buffer1+3,x
 cmp #$16
 bne CancelNext
 lda VRAM_Buffer1+4,x
 cmp #$05
 bne CancelNext
 lda VRAM_Buffer1+5,x
 cmp #$0f
 bne CancelNext
 lda R2
 sta VRAM_Buffer1+3,x
 lda R3
 sta VRAM_Buffer1+4,x
 lda R4
 sta VRAM_Buffer1+5,x
CancelNext:
 ldx R0
 jmp CancelScan
CancelDone:rts

WfP1MakePacket:
 lda #$3f
 sta WfP1Packet
 lda #$15
 sta WfP1Packet+1
 lda #3
 sta WfP1Packet+2
 lda #0
 sta WfP1Packet+6
 lda WfP1Choice
 bne OwnColors
 ldx SmFreezePaletteControl
 cpx #1
 bcc UseArea
 cpx #5
 bcc NativeColors
 cpx #8
 bne UseArea
 ldx #2
 bne NativeColors
UseArea:ldx AreaType
 cpx #4
 bcc :+
 ldx #1
:inx
NativeColors:
 lda Native1-1,x
 sta WfP1Packet+3
 lda Native2-1,x
 sta WfP1Packet+4
 lda Native3-1,x
 sta WfP1Packet+5
 rts
OwnColors:
 lda #$16
 sta WfP1Packet+3
 lda #$05
 sta WfP1Packet+4
 lda #$0f
 sta WfP1Packet+5
 rts
WfP1PublishPacket:
 ldx VRAM_Buffer1_Offset
 ldy #0
:lda WfP1Packet,y
 sta VRAM_Buffer1,x
 inx
 iny
 cpy #7
 bcc :-
 dex
 stx VRAM_Buffer1_Offset
 rts
Native1:.byte $10,$1a,$1c,$1c
Native2:.byte $30,$30,$36,$36
Native3:.byte $27,$27,$17,$17
.include "native-p1-mask.inc"
