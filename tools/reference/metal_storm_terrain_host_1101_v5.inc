; Metal Storm original-actor constructor/terrain component. Not host admission.
; Include after frozen v4 actor/host adapter. MsState=C000, MsPointer=03/04.
; The generated donor leaves keep their instruction order and signed240Y.
; R0/R1 are foreground-only. NMI00..02 and R2..R7 are never borrowed.
.import Block_Buffer_1,BlockBufferAddr,MTileAttribute
.import Player_X_Position,Player_PageLoc,Player_Y_Position,Player_Y_HighPos
.export MsNativeConstruct,MsNativeTileQuery,MsNativePlacement,MsNativeApplyDelta
.export MsNativeFF33,MsNativeFF36,MsNativeFF3F,MsTerrainHostEnd
MsTileFlags=$c810
MsTileId=$c811
MsTileColumn=$c812
MsPlacementBudget=$c813
MsDeltaAppliedEpoch=$c814
MsDeltaAppliedValid=$c815
MsCtorBoundLo=$c816
MsCtorBoundHi=$c817

; FF1E replacement: source59/5A worldX,5B screenY -> (R0/R1),Y=0
; points at one private semantic byte. X retained; A/Y/P volatile, coordinates
; unchanged; native object positions, R2..R7, queues and buffers unchanged.
; Original wall probes require flags&E0=E0. Support probes require bit80.
; Native SOLID without CLIMB mapsE0; air/coins/vines/flagpole map00.
; No unsupported donor hazard/ladder/type bits are manufactured.
MsNativeTileQuery:
 txa
 pha
 lda #0
 sta MsTileFlags
 sta MsTileId
 lda MsState+$5a
 bmi TileDone
 cmp MsState+$733
 bcc TileInBounds
 bne TileDone
 lda MsState+$59
 cmp MsState+$732
 bcc TileInBounds
 beq TileInBounds
 bcs TileDone
TileInBounds:
 lda MsState+$5b
 cmp #$20
 bcc TileDone
 cmp #$f0
 bcs TileDone
 and #$f0
 sec
 sbc #$20
 tay
 lda MsState+$59
 lsr a
 lsr a
 lsr a
 lsr a
 sta MsTileColumn
 lda MsState+$5a
 and #1
 tax
 lda #>Block_Buffer_1
 sta MsPointer+1
 lda MsTileColumn
 clc
 adc BlockBufferAddr,x
 sta MsPointer
 lda (MsPointer),y
 sta MsTileId
 tax
 lda MTileAttribute,x
 and #3
 cmp #1
 bne TileDone
 lda #$e0
 sta MsTileFlags
TileDone:
 pla
 tax
 lda #<MsTileFlags
 sta MsPointer
 lda #>MsTileFlags
 sta MsPointer+1
 ldy #0
 rts

; Native form of original944A..94AB's upward initial placement scan.
; Original startsY=D0 and moves one16px map row at a time. The pointer walk
; becomes typed FF1E queries because native maps use16-column rows, not20.
; All legal source cases preserve scan order/Y/state. A16-row ceiling bounds
; a malformed all-solid native column; C0 indicates that host-only failure.
MsNativePlacement:
 lda #$d0
 sta MsState+$4b0
 lda #0
 sta MsState+$4c8
 sta MsState+$588
 lda #16
 sta MsPlacementBudget
PlacementSeekSolid:
 jsr PlacementQuery
 lda MsTileFlags
 bmi PlacementSeekAir
 jsr PlacementUp
 bcs PlacementSeekSolid
 rts
PlacementSeekAir:
 jsr PlacementUp
 bcc PlacementFailed
 jsr PlacementQuery
 lda MsTileFlags
 bmi PlacementSeekAir
 lda #7
 sta MsState+$4e0
 lda #2
 sta MsState+$4f8
 sec
 rts
PlacementUp:
 dec MsPlacementBudget
 beq PlacementFailed
 lda MsState+$4b0
 sec
 sbc #$10
 sta MsState+$4b0
 sec
 rts
PlacementFailed:
 clc
 rts
PlacementQuery:
 lda MsState+$480
 sta MsState+$59
 lda MsState+$498
 sta MsState+$5a
 lda MsState+$4b0
 clc
 adc #$10 ; donor944A startsmaprowE0 while actorY=D0 (foot-side probe)
 sta MsState+$5b
 jmp MsNativeTileQuery

; Cold/re-entry constructor; caller authenticates both complete owner cookies
; and grants C2 before entry. No captured RAM state is used. The clear is cold
; donor reset equivalence, followed by real911B slots,90EB activation,9371
; pure actor constructor, and943C gravity reset. Donor scene/OAM/PPU/audio
; setup and map scripts remain HOST boundaries, not called or simulated here.
; Source area0 supplies original actor-art profile, not SMB campaign metadata.
; After source-map placement, bind native spawn: sourceX=nativeX-8, sourceY=
; nativeY.32px source body and16px SMB anchor share their center/feet.
; Only normal native YHigh1 entry is admitted. AXYP retained except Cresult.
MsNativeConstruct:
 php
 pha
 txa
 pha
 tya
 pha
 lda #0
 sta MsHostReady
 lda Player_Y_HighPos
 cmp #1
 jne ConstructReject
 lda MsState+$732
 sta MsCtorBoundLo
 lda MsState+$733
 sta MsCtorBoundHi
 ldx #0
 lda #0
ConstructClear:
 .repeat 8,I
 sta MsState+I*$100,x
 .endrepeat
 inx
 bne ConstructClear
 ; Fresh source pointer pair saved AFTER reset, never donor NMI scratch.
 lda MsPointer
 sta MsSaved0
 lda MsPointer+1
 sta MsSaved1
 jsr MsCtor_911B
 sta MsState+$510
 sta MsState+$70
 lda #$80
 sta MsState+$43f
 lda MsCtorBoundLo
 sta MsState+$732
 lda MsCtorBoundHi
 sta MsState+$733
 jsr ConstructBindX
 jsr MsCtor_9371
 jsr MsCtor_943C
 jsr ConstructBindX
 lda Player_Y_Position
 sta MsState+$4b0
 lda #0
 sta MsState+$4c8
 sta MsHostHaveEpoch
 sta MsDeltaAppliedValid
 lda MsSaved0
 sta MsPointer
 lda MsSaved1
 sta MsPointer+1
 lda #$a7
 sta MsHostReady
 tsx
 lda $0104,x
 ora #1
 bne ConstructStatus
ConstructReject:
 tsx
 lda $0104,x
 and #$fe
ConstructStatus:
 sta $0104,x
 pla
 tay
 pla
 tax
 pla
 plp
 rts
ConstructBindX:
 lda Player_X_Position
 sec
 sbc #8
 sta MsState+$480
 lda Player_PageLoc
 sbc #0
 sta MsState+$498
 rts

; Apply accepted source world displacement exactly once per source epoch.
; Host camera runs afterward, once. ScreenLeft is never subtracted here;
; source coordinates and native PageLoc/X are WORLD coordinates. Source
; fractions/velocity/jump latch/gravity remain untouched. AXYP preserved.
MsNativeApplyDelta:
 php
 pha
 lda MsHostHaveEpoch
 beq ApplyDone
 lda MsDeltaAppliedValid
 beq ApplyNew
 lda MsHostEpoch
 cmp MsDeltaAppliedEpoch
 beq ApplyDone
ApplyNew:
 lda Player_X_Position
 clc
 adc MsHostDeltaX
 sta Player_X_Position
 lda Player_PageLoc
 adc MsHostDeltaX+1
 sta Player_PageLoc
 lda Player_Y_Position
 clc
 adc MsHostDeltaY
 sta Player_Y_Position
 lda Player_Y_HighPos
 adc MsHostDeltaY+1
 sta Player_Y_HighPos
 lda MsHostEpoch
 sta MsDeltaAppliedEpoch
 lda #1
 sta MsDeltaAppliedValid
ApplyDone:
 pla
 plp
 rts
MsTerrainHostEnd:
