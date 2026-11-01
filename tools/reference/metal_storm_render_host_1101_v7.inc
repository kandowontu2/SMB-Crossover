; Separate proposed C2 renderer/lifecycle. Source actorA3 remains underBFE0.
; No runtime resource grant is implied. ROM frontgate must authenticate BOTH
; complete C2/C3 headers before any C2 opcode. All native calls are actual APIs.
.import MetaspriteRenderLoop,X5SetPhysicalChr,FarCallCommon
.import SafecallA_SMC,FarcallJmpTarget_SMC,CurrentBank,CurrentBankC
.import ScreenLeft_X_Pos,ScreenLeft_PageLoc,Player_SprAttrib
.import CurrentOAMOffset,SsChrActive,VRAM_Buffer1,VRAM_Buffer1_Offset
.import ObjectMetasprite,SmPosePtr
.import SelectedCharacter,OperMode,GameEngineSubroutine
.import MsBodyPhysical0,MsBodyPhysical1,MsBodyPhysical2,MsBodyPhysical3,MsBodyPhysical4,MsShotPhysical
.import MS_NATIVE_DRAW_BANK,MS_NATIVE_CHR_BANK
.importzp R0,R1,R2,R3,R4,R5,R6,R7
.export MsRenderGraphics,MsRenderDraw,MsRenderColors,MsObjectLifecycle,MsRenderEnd
.export MsRenderGate,MsColorsGate,MsGraphicsGate,MsGateEnd
MsRS=$c81a
MsSmc=$c826
MsSlot=$c829
MsBits=$c82a
MsCount=$c82b
MsIndex=$c82c
MsBaseLo=$c82d
MsBaseHi=$c82e
MsPage0=$c82f
MsPage1=$c830
MsCellDx=$c831
MsCellDy=$c832
MsCellPattern=$c833
MsCellAttr=$c834
MsPacketAt=$c835
MsOrderLo=$c836
MsOrderHi=$c837
MsYMulLo=$c838
MsYMulHi=$c839
MsTemp=$c83a
MsFlip=$c83b
MsPriority=$c83c
MsPacket=$c880

.macro MsRFar Target,Bank
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #<Bank
 jsr FarCallCommon
.endmacro

.segment "RENDER"
MsRSave:
 sta MsRS
 stx MsRS+1
 sty MsRS+2
 php
 pla
 sta MsRS+3
 ldx #7
:lda R0,x
 sta MsRS+4,x
 dex
 bpl :-
 lda SafecallA_SMC+1
 sta MsSmc
 lda FarcallJmpTarget_SMC+1
 sta MsSmc+1
 lda FarcallJmpTarget_SMC+2
 sta MsSmc+2
 rts
MsRRestore:
 lda MsSmc
 sta SafecallA_SMC+1
 lda MsSmc+1
 sta FarcallJmpTarget_SMC+1
 lda MsSmc+2
 sta FarcallJmpTarget_SMC+2
 ldx #7
:lda MsRS+4,x
 sta R0,x
 dex
 bpl :-
 lda MsRS+3
 pha
 lda MsRS
 ldx MsRS+1
 ldy MsRS+2
 plp
 sec
 rts

; Native world anchors, not an additional source/world camera integration.
; Source signed240Y is converted exactly to nativeYHigh1 domain.
MsRPosition:
 ldx MsSlot
 lda MsState+$480,x
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda MsState+$498,x
 sbc ScreenLeft_PageLoc
 sta R5
 lda MsState+$4c8,x
 sta MsYMulLo
 lda #0
 bit MsYMulLo
 bpl :+
 lda #$ff
:sta MsYMulHi
 .repeat 4
 asl MsYMulLo
 rol MsYMulHi
 .endrepeat
 lda MsState+$4b0,x
 sec
 sbc MsYMulLo
 sta R6
 lda MsState+$4c8,x
 sbc MsYMulHi
 clc
 adc #1
 sta R7
 rts

MsRenderDraw:
 jsr MsRSave
 lda #0
 sta SsChrActive             ; selected owner removes stale window4 override
 lda MsState+$53
 and #1
 bne MsOddOrder
 jsr MsRBody
 lda #1
 sta MsSlot
MsEvenShot:
 jsr MsRShot
 inc MsSlot
 lda MsSlot
 cmp #4
 bcc MsEvenShot
 jmp MsRRestore

MsRenderGraphics:
 jsr MsRSave
 lda #0
 sta SsChrActive
 sta ObjectMetasprite
 lda #<MsEmptyPose
 sta SmPosePtr
 lda #>MsEmptyPose
 sta SmPosePtr+1
 jmp MsRRestore
MsOddOrder:
 lda #3
 sta MsSlot
MsOddShot:
 jsr MsRShot
 dec MsSlot
 bne MsOddShot
 jsr MsRBody
 jmp MsRRestore

MsRBody:
 lda MsState+$510
 jpl MsBodyDone
 lda MsState+$4e0
 cmp #8
 jcs MsBodyDone
 asl a
 asl a
 asl a
 sta MsTemp
 lda MsState+$4f8
 and #7
 ora MsTemp
 tax
 lda MsBodyMap,x
 cmp #$ff
 jeq MsBodyDone
 tax
 lda MsBodyCounts,x
 sta MsCount
 asl a
 asl a
 sta MsPacket
 lda MsBodyOffsets,x
 ldx #0
 stx R1
 asl a
 rol R1
 asl a
 rol R1
 clc
 adc #<MsBodyCells
 sta MsBaseLo
 lda R1
 adc #>MsBodyCells
 sta MsBaseHi
 lda MsState+$540
 and #$c0
 sta MsFlip
 .repeat 6
 lsr a
 .endrepeat
 sta MsBits
 ldx MsCount
 cpx #6
 bne MsOrderEight
 asl a
 sta MsTemp
 asl a
 clc
 adc MsTemp
 clc
 adc #<MsBodyOrders6
 sta MsOrderLo
 lda #>MsBodyOrders6
 adc #0
 jmp MsOrderHigh
MsOrderEight:
 asl a
 asl a
 asl a
 clc
 adc #<MsBodyOrders8
 sta MsOrderLo
 lda #>MsBodyOrders8
 adc #0
MsOrderHigh:
 sta MsOrderHi
 lda #$ff
 sta MsPage0
 sta MsPage1
 lda #0
 sta MsIndex
MsBodyCell:
 lda MsOrderLo
 sta R0
 lda MsOrderHi
 sta R1
 ldy MsIndex
 lda (R0),y
 asl a
 asl a
 clc
 adc MsBaseLo
 sta R0
 lda MsBaseHi
 adc #0
 sta R1
 ldy #0
 lda (R0),y
 sta MsCellDx
 iny
 lda (R0),y
 sta MsCellDy
 iny
 lda (R0),y
 sta MsCellPattern
 iny
 lda (R0),y
 eor MsFlip
 sta MsCellAttr
 lda MsIndex
 asl a
 asl a
 clc
 adc #1
 sta MsPacketAt
 lda MsCellPattern
 .repeat 5
 lsr a
 .endrepeat
 cmp MsPage0
 beq MsTileFirst
 ldx MsPage0
 cpx #$ff
 bne MsTileSecond
 sta MsPage0
 jmp MsTileFirst
MsTileSecond:
 cmp MsPage1
 beq MsTileSecondReady
 ldx MsPage1
 cpx #$ff
 jne MsBodyDone              ; frozen source packets never require3pages
 sta MsPage1
MsTileSecondReady:
 lda MsCellPattern
 and #31
 asl a
 ora #$41                   ; odd tile: spriteP1/window5, preserving worldP0
 bne MsTileStore
MsTileFirst:
 lda MsCellPattern
 and #31
 asl a
 ora #1                     ; spriteP1/window4
MsTileStore:
 ldy MsPacketAt
 sta MsPacket,y
 iny
 lda MsCellAttr
 sta MsPacket,y
 iny
 lda MsBits
 and #2
 beq MsDyPlain
 lda #18
 sec
 sbc MsCellDy
 jmp MsDyReady
MsDyPlain:lda MsCellDy
MsDyReady:
 sec
 sbc #1                     ; source metadata dy includes OAMY+1
 sta MsPacket,y
 iny
 lda MsBits
 and #1
 beq MsDxPlain
 lda #24
 sec
 sbc MsCellDx
 jmp MsDxReady
MsDxPlain:lda MsCellDx
MsDxReady:sta MsPacket,y
 inc MsIndex
 lda MsIndex
 cmp MsCount
 jne MsBodyCell
 ldx MsPage0
 lda MsBodyPhysicalLo,x
 ldy MsBodyPhysicalHi,x
 sty MsTemp
 ldx MsTemp
 ldy #4
 MsRFar X5SetPhysicalChr,MS_NATIVE_CHR_BANK
 ldx MsPage1
 cpx #$ff
 beq MsBodyMapped
 lda MsBodyPhysicalLo,x
 ldy MsBodyPhysicalHi,x
 sty MsTemp
 ldx MsTemp
 ldy #5
 MsRFar X5SetPhysicalChr,MS_NATIVE_CHR_BANK
MsBodyMapped:
 lda #0
 sta MsSlot
 jsr MsRPosition
 lda Player_SprAttrib
 and #$20
 sta R3
 jsr MsEmitPacket
MsBodyDone:rts

MsRShot:
 ldx MsSlot
 lda MsState+$510,x
 jpl MsShotDone
 lda MsState+$648,x
 jne MsShotDone
 lda MsState+$528,x
 cmp #$80
 beq MsShotNormal
 cmp #$81
 beq MsShotUpgraded
 cmp #$83
 jne MsShotDone
 lda MsState+$630,x
 cmp #2
 bcc MsShotImpact
 jne MsShotDone             ; unreachable post-terminator metadata not admitted
 jsr MsLife_EEAE            ; exact source impact termination fields
 rts
MsShotImpact:
 clc
 adc #3
 bne MsShotIndex
MsShotNormal:lda #0
 beq MsShotIndex
MsShotUpgraded:
 lda #1
 ldy MsState+$558,x
 bne MsShotIndex
 lda #2
MsShotIndex:
 sta MsPriority
 tax
 lda MsShotOffsets,x
 clc
 adc #<MsShotMeta
 sta R0
 lda #>MsShotMeta
 adc #0
 sta R1
 ldy #0
 lda (R0),y
 sta MsPacket
 tay
MsShotCopy:
 lda (R0),y
 sta MsPacket,y
 dey
 bne MsShotCopy
 lda MsPacket
 sta MsCount
 lda #1
 sta MsPacketAt
 ldx MsSlot
 lda MsState+$540,x
 sta MsFlip
 lda MsPriority
 cmp #3
 bcc MsShotMoving
 lda #0                     ; source impact metadata ignores shot orientation
 sta MsFlip
 beq MsShotCell
MsShotMoving:
 cmp #2
 bne MsShotCell
 lda MsFlip
 and #$bf                  ; source vertical first clearsH; second forcesH
 sta MsFlip
MsShotCell:
 ldy MsPacketAt
 lda MsPacket,y
 asl a
 ora #$81                   ; spriteP1/window6, worldP0 andBG unaffected
 sta MsPacket,y
 iny
 lda MsPacket,y
 ora MsFlip
 sta MsPacket,y
 lda MsPacketAt
 clc
 adc #4
 sta MsPacketAt
 cmp MsCount
 bcc MsShotCell
 lda #<MsShotPhysical
 ldx #>MsShotPhysical
 ldy #6
 MsRFar X5SetPhysicalChr,MS_NATIVE_CHR_BANK
 jsr MsRPosition
 lda #0
 sta R3
 jsr MsEmitPacket
MsShotDone:rts

MsEmitPacket:
 lda CurrentOAMOffset
 sta MsPriority             ; source F274 visibility is cursor-change based
 lda #<MsPacket
 sta R0
 lda #>MsPacket
 sta R1
 MsRFar MetaspriteRenderLoop,MS_NATIVE_DRAW_BANK
 lda CurrentOAMOffset
 cmp MsPriority
 beq :+
 lda #$80
 bne :++
:lda #0
:ldx MsSlot
 sta MsState+$6a8,x
 rts

MsRenderColors:
 jsr MsRSave
 ldx VRAM_Buffer1_Offset
 cpx #72
 bcs MsColorsDone
 ldy #0
MsPaletteByte:
 lda MsPalettePacket,y
 sta VRAM_Buffer1,x
 inx
 iny
 cpy #12
 bcc MsPaletteByte
 lda #0
 sta VRAM_Buffer1,x
 stx VRAM_Buffer1_Offset
MsColorsDone:jmp MsRRestore

; Real original entityAI runs after AD8C/FF27 and before source rendering.
; Called once by accepted source step-tail, never by repeated draw epochs.
MsObjectLifecycle:
 php
 pha
 txa
 pha
 tya
 pha
 ldx #3
MsLifeLoop:
 lda MsState+$510,x
 bpl MsLifeNext
 lda MsState+$528,x
 cmp #$80
 beq MsLifeShot
 cmp #$81
 beq MsLifeShot
 cmp #$83
 bne MsLifeNext
 jsr MsLife_8E54
 jmp MsLifeNext
MsLifeShot:jsr MsLife_8EAE
MsLifeNext:
 dex
 bne MsLifeLoop
 pla
 tay
 pla
 tax
 pla
 plp
 rts

.include "render-life.inc"
MsBodyMap:.incbin "body-meta.bin"
MsBodyOffsets=MsBodyMap+64
MsBodyCounts=MsBodyMap+97
MsBodyCells=MsBodyMap+130
MsBodyOrders6=MsBodyMap+946
MsBodyOrders8=MsBodyMap+970
MsShotMeta:.incbin "shot-meta.bin"
MsShotOffsets:.byte 0,5,10,19,28,37
MsBodyPhysicalLo:.lobytes MsBodyPhysical0,MsBodyPhysical1,MsBodyPhysical2,MsBodyPhysical3,MsBodyPhysical4
MsBodyPhysicalHi:.hibytes MsBodyPhysical0,MsBodyPhysical1,MsBodyPhysical2,MsBodyPhysical3,MsBodyPhysical4
MsPalettePacket:.byte $3f,$11,3,$26,$0f,$15,$3f,$15,3,$21,$20,$01
MsEmptyPose:.byte 0
MsRenderEnd:

.segment "GATE"
; Independent ROM frontgate fragment.9000 is a TEST arena, NOT a host lease.
; Resident owner transport must map/authenticate C2+C3 before these calls.
MsGraphicsGate:
 jsr MsRenderAuthenticate
 bcc MsGateDone
 jmp MsRenderGraphics
MsRenderGate:
 jsr MsRenderAuthenticate
 bcc MsGateDone
 jmp MsRenderDraw
MsColorsGate:
 jsr MsRenderAuthenticate
 bcc MsGateDone
 jmp MsRenderColors
MsGateDone:rts
MsRenderAuthenticate:
 php
 pha
 txa
 pha
 lda SelectedCharacter
 cmp #35
 bne MsAuthBad
 lda MsState+$800
 cmp #$a7
 bne MsAuthBad
 lda OperMode
 cmp #1
 bne MsAuthBad
 lda GameEngineSubroutine
 cmp #8
 bne MsAuthBad
 ldx #15
MsAuthBytes:
 lda $dfe0,x
 cmp MsExpectedC2,x
 bne MsAuthBad
 lda $bfe0,x
 cmp MsExpectedC3,x
 bne MsAuthBad
 dex
 bpl MsAuthBytes
 tsx
 lda $0103,x
 ora #1
 bne MsAuthResult
MsAuthBad:
 tsx
 lda $0103,x
 and #$fe
MsAuthResult:
 sta $0103,x
 pla
 tax
 pla
 plp
 rts
MsExpectedC2:.incbin "render-cookie.bin"
MsExpectedC3:.incbin "actor-cookie.bin"
MsGateEnd:

