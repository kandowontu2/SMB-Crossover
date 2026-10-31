; UNADOPTED sizing proposal. No common/ROM/RAM alias/palette permission implied.
; Selected31/full16-cookie importer is mandatory before any A2/A3 opcode.
.setcpu "6502"
.macpack longbranch
.import SelectedCharacter,SmFreezeRenderState,FfMuxNativeROM
.import BtServiceVeneers,DrawAllMetasprites,CurrentBankC,FarCallCommon
.import SafecallA_SMC,FarcallJmpTarget_SMC
.import Sprite_Data,CurrentOAMOffset,ObjectMetasprite,SprObject_SprAttrib
.import CfState,CfTargetBank,CfNativeP1Mask
.import SmFreezePalettePacket,SmFreezePalettePending,SmFreezeLastBlue,SmFreezeTurn
.import SmFreezePaletteControl,AreaType
.export CfSharedDrawSelect,CfWholeDrawAll,CfTagNativeObjects,CfP1Late,CfP1Heartbeat,CfP1Acquire
.export CfP1SavedAttributes,CfP1NativeC
CfP1Temp=CfState+$02f7
CfP1Visible=CfState+$02fa
CfP1Choice=CfState+$02fb

.macro CF_FAR target,tail
 sta SafecallA_SMC+1
 lda #<target
 sta FarcallJmpTarget_SMC+1
 lda #>target
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(target)|$80)
 .if .xmatch({tail},{jmp})
 jmp FarCallCommon
 .else
 jsr FarCallCommon
 .endif
.endmacro
.macro CF_SAVE
 php
 pha
 txa
 pha
 tya
 pha
.endmacro
.macro CF_RESTORE
 pla
 tay
 pla
 tax
 pla
 plp
.endmacro

; Shared proposal replaces ONLY FwNativeDrawAll's original 3B Native tail.
; Full P/A kept on both choices; X/Y untouched. Genuine B020 row6 is the
; required external ROM full-cookie guard before CfWholeDrawAll's first opcode.
.segment "CF_SHARED_DRAW_PROPOSAL"
CfSharedDrawSelect:
 php
 pha
 lda SelectedCharacter
 cmp #31
 bne Foreign
 pla
 plp
 CF_FAR BtServiceVeneers+18,jmp
Foreign:
 pla
 plp
 jmp FfMuxNativeROM

.segment "CF_P1_STATE_PROPOSAL"
CfP1SavedAttributes:.res 24
CfP1NativeC:.res 1

.segment "CF_P1_WHOLE_PROPOSAL"
CfWholeDrawAll:
 CF_SAVE
 ldx #23
:lda SprObject_SprAttrib,x
 sta CfP1SavedAttributes,x
 dex
 bpl :-
 CF_RESTORE
 CF_FAR DrawAllMetasprites,jsr
 ; Keep genuine native output AXYP/C and all native R0..7 intact.
 CF_SAVE
 lda CurrentBankC
 pha
 lda #2
 sta CurrentBankC
 sta $5116
 pla
 sta CfP1NativeC
 ldx #23
:lda CfP1SavedAttributes,x
 sta SprObject_SprAttrib,x
 dex
 bpl :-
 jsr CfP1Late
 ; Proposed explicit own transport return code: A1/A3 worker bank tags
 ; never have bit7. The A2 return must consume this tag and return the
 ; saved genuine native C output, rather than its old caller C.
 lda #$80
 sta CfTargetBank
 CF_RESTORE
 rts

; Called at end of existing early CfHostDraw, after native pointer prepare
; and before the world loop. Native mask table is generated from BOTH exact
; compiled facings and all four real actor palette OR/override inputs.
.segment "CF_P1_TAG_PROPOSAL"
CfTagNativeObjects:
 ldx #23
Actor:
 lda ObjectMetasprite,x
 beq NextActor
 cmp #145
 bcs NextActor                 ; no invented guest/dynamic record semantics
 tay
 lda CfNativeP1Mask,y
 sta CfP1Temp
 lda SprObject_SprAttrib,x
 and #3
 tay
 lda Bits,y
 and CfP1Temp
 beq NextActor
 lda SprObject_SprAttrib,x
 ora #$10
 sta SprObject_SprAttrib,x
NextActor:
 dex
 bne Actor                    ; source body0 is never tagged
 rts
Bits:.byte 1,2,4,8

; CF loan-requiring projectile records must separately tag EVERY emitted
; source part with ignored bit3, including its P0/P2 layers. Existing CfState
; 02DF changes declared meaning from uncommitted loan-admission byte to
; per-object emitter tag0/8. Body0/P0-only shots keep tag0. No new OAM cells.
.segment "CF_P1_LATE_PROPOSAL"
CfP1Late:
 lda #0
 sta CfP1Visible
 ldx #0
Scan:
 lda Sprite_Data,x
 cmp #240
 bcs Next
 lda Sprite_Data+2,x
 and #$18
 cmp #8
 beq Shot
 cmp #16
 bne Next
 lda #2
 bne AddVisible
Shot:lda #1
AddVisible:
 ora CfP1Visible
 sta CfP1Visible
Next:
 inx
 inx
 inx
 inx
 bne Scan
 lda #0
 sta CfP1Choice
 lda CfP1Visible
 cmp #3
 beq Both
 and #1
 beq PaintStart
 lda #1
 bne SetChoice
Both:
 lda SmFreezeTurn
 eor #1
 and #1
 sta SmFreezeTurn
SetChoice:sta CfP1Choice
PaintStart:
 ldx #0
Paint:
 lda Sprite_Data+2,x
 and #$18
 cmp #8
 beq LoanPart
 cmp #16
 bne ClearTag
 lda CfP1Choice
 bne Hide
 beq ClearTag
LoanPart:
 lda CfP1Choice
 bne ClearTag
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
 jmp Packet

.segment "CF_P1_PACKET_PROPOSAL"
Packet:
 lda #0
 sta SmFreezePalettePending    ; clear validity FIRST
 lda #$3f
 sta SmFreezePalettePacket
 lda #$15
 sta SmFreezePalettePacket+1
 lda #3
 sta SmFreezePalettePacket+2
 lda #0
 sta SmFreezePalettePacket+6
 lda CfP1Choice
 bne ShotColors
 ldx SmFreezePaletteControl
 cpx #1
 bcc Area
 cpx #5
 bcc NativeColors
 cpx #8
 bne Area
 ldx #2
 bne NativeColors
Area:
 ldx AreaType
 cpx #4
 bcc :+
 ldx #1
:inx
NativeColors:
 lda Color1-1,x
 sta SmFreezePalettePacket+3
 lda Color2-1,x
 sta SmFreezePalettePacket+4
 lda Color3-1,x
 sta SmFreezePalettePacket+5
 lda #$c0                    ; native restore BEFORE nativequeue
 bne Commit
ShotColors:
 lda #$20
 sta SmFreezePalettePacket+3
 lda #$38
 sta SmFreezePalettePacket+4
 lda #$16
 sta SmFreezePalettePacket+5
 lda #$80                    ; source yellow AFTER nativequeue
Commit:
 pha
 lda CfP1Choice
 ora #$c0
 sta SmFreezeLastBlue          ; CF owner identity, after complete OAM/packet
 pla
 sta SmFreezePalettePending   ; complete paired publication LAST
 rts
Color1:.byte $10,$1a,$1c,$1c
Color2:.byte $30,$30,$36,$36
Color3:.byte $27,$27,$17,$17

.segment "CF_P1_HEARTBEAT_PROPOSAL"
CfP1Heartbeat:
 ; Caller is externally full-cookie/selected31 authenticated. Row29 runs
 ; before pause and draw-skip, and reissues only a complete stable CF epoch.
 php
 pha
 lda SmFreezeLastBlue
 cmp #$c1
 bne Done
 lda #0
 sta SmFreezePalettePending
 lda SmFreezePalettePacket
 cmp #$3f
 bne Done
 lda SmFreezePalettePacket+1
 cmp #$15
 bne Done
 lda SmFreezePalettePacket+2
 cmp #3
 bne Done
 lda SmFreezePalettePacket+6
 bne Done
 lda #$80
 sta SmFreezePalettePending
Done:
 pla
 plp
 rts

.segment "CF_P1_ACQUIRE_PROPOSAL"
CfP1Acquire:
 ; New authenticated CF construction ONLY, after old-owner retirement and
 ; native forcedblank checkpoint. No warm ready/life/scene behavior assumed.
 lda #0
 sta SmFreezePalettePending
 sta SmFreezeLastBlue
 sta SmFreezeTurn
 sta CfP1Choice
 jmp Packet
