; Private authenticated caller contract, normal gameplay only.
; A source-backed constructor runs once after stage/load retirement and full
; original-state zeroing/code placement; Update runs once per native Main epoch.
.setcpu "6502"
.export PpHostInit,PpHostUpdate,PpHostExport,PpHostImportX
Phase=$c0a6
TmpX=$c0a7
TmpPage=$c0a8
.segment "LIFE_INIT"
PpHostInit:
 ldx #13
CopyActor:
 lda ActorTemplate,x
 sta $c60e,x
 dex
 bpl CopyActor
 lda #5
 sta $c6cf
 sta $c6d1
 lda #0
 sta Phase
 lda #3
 sta $c088
 lda #77
 sta $c089
 lda Player_Y_Position
 sec
 sbc #48
 sta $c611
 sta $c08b
 lda Player_Y_HighPos
 sbc #1
 sta $c08a
 jsr PpHostImportX
 jsr PpWorldPhysicalFoot
 lda $c084
 sta $c086
 lda $c085
 sta $c087
 sec
 rts

.segment "LIFE_COLD"
.export PpHostColdFinalize
; All streams decoded, cold decoder has returned into RAM3. The state-code
; stream was decoded80bytes above its live address to preserve that decoder.
; Copy forward to the lower destination, then erase every cold/source gap
; before the genuine actor constructor. Fresh-copy-only, forcedblank/SEI.
PpHostColdFinalize:
 ldy #0
 ldx #5
ColdPage:
ColdRead:lda $c100,y
ColdWrite:sta $c0b0,y
 iny
 bne ColdPage
 inc ColdRead+2
 inc ColdWrite+2
 dex
 bne ColdPage
ColdTail:
 lda $c600,y
 sta $c5b0,y
 iny
 cpy #$5f
 bne ColdTail
 txa
 tay
ColdPrefix:
 sta $c000,y
 iny
 cpy #$b0
 bne ColdPrefix
 ldy #$0f
ColdActorPage:
 sta $c600,y
 iny
 bne ColdActorPage
ColdLastPage:
 sta $c700,y
 iny
 bne ColdLastPage
 jmp PpHostInit

.segment "LIFE_PHASE"
PpHostUpdate:
 lda GameEngineSubroutine
 cmp #8
 beq Live
 clc
 rts
Live:
 jsr PpHostImportX
 lda Phase
 inc Phase
 and #3
 beq Advance
 cmp #2
 beq Controls
 cmp #3
 beq Physics
 jmp PpHostExport
Advance:
 lda #0
 sta $c02c
 sta $c069
 jsr PpAdvanceActor
 jsr PpHostProject
 jmp PpHostExport
Controls:
 lda #3
 sta $c02c
 lda SavedJoypad1Bits
 sta $c40a
 jsr PpControls
 jmp PpHostExport
Physics:
 lda #4
 sta $c02c
 jsr PpFall
 jsr PpTerrainContact
 jsr PpWorldPhysicalFoot
 lda $c084
 sta $c086
 lda $c085
 sta $c087
 lda #0
 sta $c02c
 jmp PpHostExport
PpHostImportX:
 lda Player_X_Position
 clc
 adc #8
 sta $c60f
 lda Player_PageLoc
 adc #0
 sta $c610
 rts
ActorTemplate:
 ; Exact original bank2:ABBF first actor, prior to actual native spawn import.
 .byte $80,$a0,$00,$80,$00,$db,$96,$ff,$00,$00,$00,$00,$00,$00

.segment "LIFE_EXPORT"
PpHostExport:
 jsr PpWorldPhysicalFoot
 lda $c60f
 sec
 sbc #8
 sta TmpX
 lda $c610
 sbc #0
 sta TmpPage
 lda TmpX
 sec
 sbc Player_X_Position
 sta Player_X_Scroll
 asl
 asl
 asl
 asl
 sta Player_X_Speed
 lda TmpX
 sta Player_X_Position
 lda TmpPage
 sta Player_PageLoc
 lda $c084
 sec
 sbc #32
 sta Player_Y_Position
 lda $c085
 sbc #0
 clc
 adc #1
 sta Player_Y_HighPos
 lda $c618
 cmp #2
 lda #0
 bcc :+
 lda #2
:
 sta Player_State
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sta Player_Pos_ForScroll
 lda $c60f
 sec
 sbc ScreenLeft_X_Pos
 sta PpRenderX
 lda $c610
 sbc ScreenLeft_PageLoc
 sta PpRenderX+1
 lda $c611
 clc
 adc $c089
 sta PpRenderY
 lda $c08a
 adc #1
 sta PpRenderY+1
 sec
 rts
