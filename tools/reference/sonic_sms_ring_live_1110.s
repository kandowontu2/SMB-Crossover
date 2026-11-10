; Proposed raw43 ring-state bridge. Enter through authenticated Sonic rows.
; The three test stage cells carry the actual GHZ1 row 5 columns 82..84.
; This sidecar publishes neither native health nor coins, OAM, or audio.

.setcpu "6502"
.segment "RING_SCENE"

SceneTiles = ContextEnd
SceneEnd = SceneTiles+3

RingFresh:
 jsr RingClear
 lda #0
 sta HostReady
 jmp FreshContinue

RingConstruct:
 jsr RingClear
 lda WorldNumber
 ora LevelNumber
 bne ConstructContinue
 lda AreaAddrsLOffset
 cmp #5
 bne ConstructContinue
 lda #$7a
 sta SceneTiles
 lda #$7b
 sta SceneTiles+1
 sta SceneTiles+2
ConstructContinue:
 lda #0
 sta CtorTileX
 jmp CtorContinue

RingClear:
 txa
 pha
 ldx #SceneEnd-RingContext-1
 lda #0
ClearByte:
 sta RingContext,x
 dex
 bpl ClearByte
 pla
 tax
 rts

RingProject:
 php
 pha
 txa
 pha
 tya
 pha
 lda WorldNumber
 ora LevelNumber
 bne ProjectContinue
 lda AreaAddrsLOffset
 cmp #5
 bne ProjectContinue
 lda SourceY+1
 bne ProjectContinue
 lda SourceY
 clc
 adc #8
 bcs ProjectContinue
 and #$e0
 cmp #$a0
 bne ProjectContinue
 lda SourceX
 clc
 adc #12
 tay
 lda SourceX+1
 adc #0
 beq FirstPage
 cmp #1
 bne ProjectContinue
 cpy #32
 bcs ProjectContinue
 ldx #2
 bne RingCell
FirstPage:
 cpy #192
 bcc ProjectContinue
 ldx #0
 cpy #224
 bcc RingCell
 inx
RingCell:
 lda SceneTiles,x
 and #3
 beq ProjectContinue
 txa
 pha
 ldy #1
RingPosition:
 lda SourceX,y
 sta ActorX,y
 lda SourceY,y
 sta ActorY,y
 dey
 bpl RingPosition
 lda SceneTiles,x
 jsr AcquireRingTile
 tay
 pla
 tax
 tya
 bcc ProjectContinue
 sta SceneTiles,x
ProjectContinue:
 pla
 tay
 pla
 tax
 pla
 plp
 lda SourceX
 jmp HostProjectContinue
