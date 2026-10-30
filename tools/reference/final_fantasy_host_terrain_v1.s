; Actual SMB cell/response adapter for the frozen FF half-open body rectangle.
; Typed selected22/engine8 services; parent keeps automatic/pause paths native.
.setcpu "6502"
.macpack longbranch
.import SelectedCharacter,PlayerFacingDir,RgCrouch,MmDeathFlag
.import GamePauseStatus,TimerControl,BlockBufferAddr,Block_Buffer_1,MTileAttribute
.import MmVX,MmVY,MmXFraction,MmYFraction,SideCollisionTimer
.import Player_X_Scroll,Player_CollisionBits
.import BoundingBox_UL_Corner,BoundingBox_LR_Corner,ScreenLeft_X_Pos,ScreenLeft_PageLoc,Local_eb
.importzp Player_X_Position,Player_PageLoc,Player_Y_Position,Player_Y_HighPos
.importzp Player_Y_Speed,Player_X_Speed,Player_State,GameEngineSubroutine
.importzp R0,R1,R2,R3,R4,R5,R6,R7,MTILE_SOLID,MTILE_CLIMB
.import FfEnsure,FfMovement,FfRenderBuffer,FfJump,FfGPhase
.export FfHostMovement,FfHostHeadWithin,FfHostHead,FfHostFeet,FfHostSide
.export FfHostWall,FfHostAfterTerrain,FfHostBox,FfHostAdder
.export FfHostTerrainBegin,FfHostTerrainEnd

; Temporal pre-render scratch within the existing61B descriptor. No NMI owns
; these bytes. Genuine FfGraphics/RenderChunk rebuilds them before every draw.
FfTerrainFlags=FfRenderBuffer
FfTerrainTargetY=FfRenderBuffer+1
FfTerrainPreviousY=FfRenderBuffer+2
FfTerrainDX=FfRenderBuffer+3
FfTerrainDY=FfRenderBuffer+4
FfTerrainIndex=FfRenderBuffer+5
FfTerrainPage=FfRenderBuffer+6
FfTerrainY=FfRenderBuffer+7
.export FfTerrainFlags,FfTerrainTargetY,FfTerrainPreviousY
.export FfTerrainDX,FfTerrainDY,FfTerrainIndex,FfTerrainPage,FfTerrainY

.segment "FF_HOST_TERRAIN"
FfHostTerrainBegin:

.proc FfHostMovement
 lda SelectedCharacter
 cmp #22
 bne Native
 jsr FfEnsure
 lda Player_Y_Position
 sta FfTerrainPreviousY
 lda #0
 sta FfTerrainFlags
Native:jmp FfMovement
.endproc

.proc FfHostAdder
 ldy #0
 sec
 rts
.endproc

.proc FfHostTop
 lda #6
 ldx RgCrouch
 beq Done
 lda #17
Done:rts
.endproc

.proc FfHostHeadWithin
 jsr FfHostTop
 clc
 adc Player_Y_Position
 bcs Outside
 cmp #32
 rts
Outside:clc
 rts
.endproc

; R0/R1 and Local_eb remain the real PlayerBGCollision caller's state.
; Return A=metatile,X=0,Y=incoming query index; R2/R3/R5/R6/R7 identify the
; actual cell. This never temporarily moves the player to perform a query.
.proc FfHostRead
 lda Player_X_Position
 clc
 adc FfTerrainDX
 sta R5
 lda Player_PageLoc
 adc #0
 sta FfTerrainPage
 and #1
 tay
 lda #>Block_Buffer_1
 sta R7
 lda R5
 lsr
 lsr
 lsr
 lsr
 clc
 adc BlockBufferAddr,y
 sta R6
 lda Player_Y_HighPos
 cmp #1
 bne Empty
 lda Player_Y_Position
 clc
 adc FfTerrainDY
 sta FfTerrainY
 bcs Empty
 cmp #32
 bcc Empty
 cmp #240
 bcs Empty
 and #$f0
 sec
 sbc #32
 sta R2
 tay
 lda (R6),y
 sta R3
Return:ldx #0
 ldy FfTerrainIndex
 lda R3
 rts
Empty:lda #0
 sta R3
 jmp Return
.endproc

.proc FfHostHead
 sty FfTerrainIndex
 jsr FfHostTop
 sta FfTerrainDY
 lda #8
 sta FfTerrainDX
 jsr FfHostRead
 bne Sampled
 lda #1
 sta FfTerrainDX
 jsr FfHostRead
 bne Sampled
 lda #14
 sta FfTerrainDX
 jsr FfHostRead
Sampled:
 lda Player_Y_Position
 and #15
 sta R4
 lda R3
 beq Done
 ldx Player_Y_Speed
 bpl Done
 tax
 lda MTileAttribute,x
 and #MTILE_SOLID|MTILE_CLIMB
 cmp #MTILE_SOLID
 bne Done
 ; A side overlap while rising must not bump a block. Only a genuine upward
 ; crossing of this cell's lower edge earns a ceiling response and effects.
 lda #0
 sta R4
 lda R2
 clc
 adc #48
 bcs Done
 sta FfTerrainTargetY
 lda FfTerrainPreviousY
 clc
 adc FfTerrainDY
 bcs Done
 cmp FfTerrainTargetY
 bcc Done
 lda FfTerrainTargetY
 sec
 sbc FfTerrainDY
 sta FfTerrainTargetY
 lda #1
 sta FfTerrainFlags
 lda #4
 sta R4
Done:ldx #0
 ldy FfTerrainIndex
 lda R3
 rts
.endproc

.proc FfHostFeet
 iny
 sty FfTerrainIndex
 lda #1
 cpy #1
 beq First
 lda #14
First:sta FfTerrainDX
 lda #32
 sta FfTerrainDY
 jsr FfHostRead
 lda Player_Y_Position
 and #15
 sta R4
 lda R3
 rts
.endproc

.proc FfHostSide
 sty FfTerrainIndex
 lda #1
 ldx R0
 cpx #1
 bne Left
 lda #14
Left:sta FfTerrainDX
 tya
 and #1
 beq Lower
 jsr FfHostTop
 clc
 adc #2
 bne Offset
Lower:lda #30
Offset:sta FfTerrainDY
 jsr FfHostRead
 lda Player_X_Position
 and #15
 sta R4
 lda R3
 rts
.endproc

; Typed native wall response, called only for this actual selected-cell tuple.
; R0=2left/1right. Exact source edges are [X+1,X+15), so neither direction
; changes world page or block identity based on a wrapped screen coordinate.
.proc FfHostWall
 lda R6
 sec
 sbc #<Block_Buffer_1
 and #15
 asl
 asl
 asl
 asl
 ldx R0
 cpx #1
 beq Right
 clc
 adc #15
 sta Player_X_Position
 lda FfTerrainPage
 adc #0
 jmp Page
Right:sec
 sbc #15
 sta Player_X_Position
 lda FfTerrainPage
 sbc #0
Page:sta Player_PageLoc
 lda #16
 sta SideCollisionTimer
 lda R0
 eor #$ff
 and Player_CollisionBits
 sta Player_CollisionBits
 lda #0
 sta MmVX
 sta MmVX+1
 sta MmVX+2
 sta MmXFraction
 sta MmXFraction+1
 sta Player_X_Speed
 sta Player_X_Scroll
 sec
 rts
.endproc

.proc FfHostAfterTerrain
 lda FfTerrainFlags
 beq Ground
 lda FfTerrainTargetY
 sta Player_Y_Position
 lda #1
 sta Player_Y_Speed
 sta MmVY+2
 bne Fractions
Ground:
 lda Player_State
 bne Box
 lda #0
 sta Player_Y_Speed
 sta MmVY+2
 sta FfJump
 sta FfGPhase
Fractions:lda #0
 sta MmVY
 sta MmVY+1
 sta MmYFraction
 sta MmYFraction+1
Box:lda #0
 sta FfTerrainFlags
 jmp FfHostBox
.endproc

; Native collision boxes use inclusive right/bottom pixels. The frozen source
; bounds [1,15)x[6(or17),32) therefore become +1..14,+6(or17)..31.
; Compute camera-relative X in16bits so a partial left clip cannot wrap right.
.proc FfHostBox
 lda Player_Y_HighPos
 cmp #1
 bne Hidden
 jsr FfHostTop
 clc
 adc Player_Y_Position
 bcs Hidden
 sta BoundingBox_UL_Corner+1
 lda Player_Y_Position
 clc
 adc #31
 bcc Bottom
 lda #255
Bottom:sta BoundingBox_LR_Corner+1
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sta FfTerrainDX
 lda Player_PageLoc
 sbc ScreenLeft_PageLoc
 beq Onscreen
 cmp #255
 bne Hidden
 lda FfTerrainDX
 clc
 adc #14
 bcc Hidden
 sta BoundingBox_LR_Corner
 lda #0
 beq Left
Onscreen:
 lda FfTerrainDX
 clc
 adc #14
 bcc Right
 lda #255
Right:sta BoundingBox_LR_Corner
 lda FfTerrainDX
 clc
 adc #1
 bcs Hidden
Left:sta BoundingBox_UL_Corner
 ldx #0
 ldy #0
 rts
Hidden:lda #255
 sta BoundingBox_UL_Corner
 sta BoundingBox_UL_Corner+1
 sta BoundingBox_LR_Corner
 sta BoundingBox_LR_Corner+1
 ldx #0
 ldy #0
 rts
.endproc

FfHostTerrainEnd:
