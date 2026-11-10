; Memory-only D002 replacement proposal for the original CF07 player resolver.
; The private input block and code origin are fixture addresses, not allocations.
; QueryY/QueryX are the unmodified donor coarse coordinates at the D002 call.
; QueryDirection is CF07's incoming Y before it selects the two-point list.
; Return A=class in the original high/even or low/odd nibble, NZ from A,
; X unchanged, Y=original packed index, C=QueryX parity, V/D/I unchanged.
; RawTile/Attributes are evidence for later host effects. Invalid queries
; publish a nonzero Status and class1, without touching the terrain buffers.
.setcpu "6502"

SelectedCharacter = $6002
MikeAlternate = $730b
OperMode = $0771
OperModeTask = $0773
GamePauseStatus = $0777
GameEngineSubroutine = $0f
SwimmingFlag = $0706
ColumnSets = $0721
ParserPhase = $0722
CursorPage = $0728
CursorColumn = $0729
RingColumn = $04a0
ScreenLeftPage = $071d
ScreenLeftX = $071f
NativeBlock1 = $0300
NativeBlock2 = $03d0
MTileAttribute = $ef36

QueryY = Scratch
QueryX = Scratch+1
QueryDirection = Scratch+2
Status = Scratch+3
RawTile = Scratch+4
Attributes = Scratch+5
TileClass = Scratch+6
Index = Scratch+7
CommittedEnd = Scratch+8
ScreenStart = Scratch+9

.segment "JAY_TILE"
JayHostTile:
 txa
 pha
 php
 lda #0
 sta RawTile
 sta Attributes
 ldx #1
 lda SelectedCharacter
 cmp #16
 bne Reject
 lda MikeAlternate
 and #$60
 cmp #$20
 bne Reject
 lda OperMode
 cmp #1
 bne Reject
 lda OperModeTask
 cmp #3
 bne Reject
 lda GameEngineSubroutine
 cmp #8
 bne Reject
 lda GamePauseStatus
 lsr A
 bcs Reject
 lda SwimmingFlag
 bne Reject

 ldx #2
 lda QueryDirection
 cmp #9
 bcs Reject
 lsr A
 bcs Reject
 ldx #3
 lda QueryY
 cmp #2
 bcc Reject
 cmp #15
 bcs Reject
 ldx #4
 lda ColumnSets
 cmp #$ff
 bne Reject
 lda ParserPhase
 cmp #8
 bcc CheckCursor
Reject:
 stx Status
 lda #1
 jmp EncodeClass

CheckCursor:
 tay
 ldx #5
 lda CursorColumn
 cmp #16
 bcs Reject
 lda CursorPage
 cmp #16
 bcs Reject
 asl A
 asl A
 asl A
 asl A
 ora CursorColumn
 sta CommittedEnd
 and #31
 cmp RingColumn
 bne Reject
 lda CommittedEnd
 clc
 adc PhaseAdvance,y
 bcs Reject
 sta CommittedEnd
 lda ScreenLeftPage
 cmp #16
 bcs Reject
 asl A
 asl A
 asl A
 asl A
 sta ScreenStart
 lda ScreenLeftX
 lsr A
 lsr A
 lsr A
 lsr A
 ora ScreenStart
 sta ScreenStart
 ldx #6
 lda CommittedEnd
 sec
 sbc ScreenStart
 beq Reject
 bcc Reject
 cmp #33
 bcs Reject
 lda QueryX
 cmp ScreenStart
 bcc Reject
 cmp CommittedEnd
 bcs Reject

 lda QueryY
 sec
 sbc #2
 asl A
 asl A
 asl A
 asl A
 sta Index
 lda QueryX
 and #15
 ora Index
 tay
 lda QueryX
 and #16
 beq ReadEvenPage
 lda NativeBlock2,y
 jmp ClassifyTile
ReadEvenPage:
 lda NativeBlock1,y
ClassifyTile:
 sta RawTile
 tax
 lda MTileAttribute,x
 sta Attributes
 and #3
 cmp #1
 bne ClearTile
 cpx #$c2
 beq ClearTile
 cpx #$c3
 beq ClearTile
 cpx #$5f
 beq HiddenTile
 cpx #$60
 bne SolidTile
HiddenTile:
 lda QueryDirection
 bne ClearTile
SolidTile:
 lda #1
 bne ValidTile
ClearTile:
 lda #0
ValidTile:
 ldx #0
 stx Status

EncodeClass:
 sta TileClass
 lda QueryY
 and #15
 asl A
 asl A
 asl A
 sta Index
 lda QueryX
 lsr A
 and #7
 ora Index
 tay
 plp
 pla
 tax
 lda QueryX
 lsr A
 lda TileClass
 bcs ReturnClass
 asl A
 asl A
 asl A
 asl A
ReturnClass:
 rts

; AreaParserCore has already written a column during phases1..3 and5..7.
PhaseAdvance:
 .byte 0,1,1,1,0,1,1,1
