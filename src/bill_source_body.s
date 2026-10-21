; Source Bill HRect projection, original 1.0 and 2.02 independently extracted.
; Actor comparisons are inclusive. Ceil lower/floor upper is equivalent ONLY
; against integer native proxy endpoints, not arbitrary fractional enemies.
; Source SWF matrix residuals and mirrored endpoints remain Q16 exact.
.pushseg
.segment "SRAM"
BillSourceBodyForm: .res 1         ; 0 main,1 jumpStart,2 crouch; previous publication.
BillSourceFlagSeen: .res 1         ; bit0 observed flag-slide; bit7 source water epoch consumed.
; Exact prior completed source rectangle epoch; never use current form/facing.
BillBodyPrevX: .res 2              ; world low/page.
BillBodyPrevXF: .res 2
BillBodyPrevY: .res 2              ; native low/high (high1 is source world0).
BillBodyPrevYF: .res 2
BillBodyPrevForm: .res 1
BillBodyPrevFacing: .res 1
BillBodyPrevMode: .res 1
BillBodyPrevValid: .res 1
BillHeadFiltering: .res 1

.assert BillSourceBodyForm=RyuSourceBodyProfile+1,error,"Append source Bill cache only"
.assert * <= $8000,error,"Bill source cache exceeds SRAM"



.segment "BILL_BODY_COLD"
BillSourceBodyStart:
.proc BillBodyDispatch
  cmp #0
  jeq Select
  cmp #1
  jeq Terrain
  cmp #2
  jeq Project
  cmp #3
  jeq Water
  cmp #4
  jeq RawHead
  cmp #5
  jeq FilteredHead
  jmp CachePrevious
.pushseg
.segment "LOWCODE"
Select:
  lda GuestPowerupActive
  jne Cached                       ; lockFrame retains primary HRect in Easy injury/pickup.
  lda MmDeathFlag
  beq Alive
  lda MmDeathPit
  jne Cached                       ; Source pit disables hit types, frame retained.
  lda MmDeathAge
  cmp #18
  jcc Cached
  ldy #2                           ; source die13..18 inherit crouch parent geometry.
  jmp Publish
Alive:
  lda GameEngineSubroutine
  cmp #4
  bne :+
    lda BillSourceFlagSeen
    ora #1
    sta BillSourceFlagSeen
    bne Upright                    ; slideDownFlagPole uses main-height slide2.
  :
  cmp #5
  bne Ordinary
  lda BillSourceFlagSeen
  and #1
  beq DepartContinuing
  lda BillSourceFlagSeen
  and #$fe
  sta BillSourceFlagSeen
  farcall FlagSupported
  bcs FlagGround
  lda #$80
  sta RgDoubleJump                  ; stopFlagPoleSlide when source is not grounded.
DepartContinuing:
  farcall FlagSupported
  bcs FlagGround
  jmp Air
FlagGround:
  lda RgDoubleJump
  and #$7f
  sta RgDoubleJump
  jmp Upright
Ordinary:
  cmp #8
  bne Upright                      ; pipe/entrance source main; no fabricated air-spin.
  lda Player_State
  cmp #3
  beq Upright                      ; vine/climb is full height, actual jumped retained.
  lda Player_State
  bne Air
  lda RgCrouch
  beq Upright
  ldy #2
  bne Publish
Air:
  lda RgDoubleJump
  bpl Upright                      ; walking off does not set source jumped.
  ldy #1
  bne Publish
Upright:
  ldy #0
Publish:
  sty BillSourceBodyForm
Cached:
  ldy BillSourceBodyForm
  lda BodyRows,y
  tay
  rts
.popseg
Terrain:
  jmp BillCachedTerrainRow
Water:
  jmp BillCachedWaterHeight
.pushseg
.segment "LOWCODE"
Project:
  ; Exact thresholds are algebraically derived from the independently
  ; decoded SWF offsets. Strict ceil and inclusive floor equality differ.
  ; No scratch RAM is modified; full caller P/A/X/Y preservation remains.
  php
  pha
  phx
  phy
  lda Player_X_Position
  sec
  sbc ScreenLeft_X_Pos
  clc
  adc #2
  sta BoundingBox_UL_Corner
  clc
  adc #12
  sta BoundingBox_LR_Corner
  lda PlayerFacingDir
  and #2
  lsr
  tax
  lda MmXFraction+1
  cmp XCeilHi,x
  bcc LeftReady
  bne LeftExtra
  lda MmXFraction
  cmp XCeilLo,x
  bcc LeftReady
  beq LeftReady
LeftExtra:
  inc BoundingBox_UL_Corner
LeftReady:
  lda MmXFraction+1
  cmp XFloorHi,x
  bcc RightReady
  bne RightExtra
  lda MmXFraction
  cmp XFloorLo,x
  bcc RightReady
RightExtra:
  inc BoundingBox_LR_Corner
RightReady:
  ldy BillSourceBodyForm
  lda Player_Y_Position
  clc
  adc TopAdd,y
  sta BoundingBox_UL_Corner+1
  lda MmYFraction+1
  cmp TopCeilHi,y
  bcc TopReady
  bne TopExtra
  lda MmYFraction
  beq TopReady
TopExtra:
  inc BoundingBox_UL_Corner+1
TopReady:
  lda Player_Y_Position
  clc
  adc #32
  sta BoundingBox_LR_Corner+1
  lda MmYFraction+1
  cmp #$ff
  bne ProjectDone
  lda BillSourceBodyForm
  beq TallBottom
  ldy #2
  bne CompareBottom
TallBottom:
  ldy #1
  lda CrossoverBehaviorVersion
  bne CompareBottom
  dey
CompareBottom:
  lda MmYFraction
  cmp BottomFloorLo,y
  bcc ProjectDone
  inc BoundingBox_LR_Corner+1
ProjectDone:
  jsr CachePrevious
  ply
  plx
  pla
  plp
  rts
XCeilHi: .byte $c0,$c0
XCeilLo: .byte $00,$8c
XFloorHi:.byte $3f,$40
XFloorLo:.byte $74,$00
TopAdd: .byte 1,16,17
TopCeilHi:.byte $80,$40,$00
BottomFloorLo:.byte $dc,$e0,$f4
.popseg
.pushseg
.segment "BILL_BODY_COLD"
FlagSupported:
  ; A native climbing exit can transiently publish State0 in midair.
  ; Corroborate authored static support; a state token alone is insufficient.
  ; This is a port mapping for the ordinary flag floor, not a source theorem
  ; for custom moving platforms under a flagpole.
  lda Player_State
  bne NoFlagGround
  lda Player_Y_HighPos
  cmp #1
  bne NoFlagGround
  lda Player_Y_Speed
  bne NoFlagGround
  lda Player_Y_Position
  cmp #208
  bcs NoFlagGround
  and #15
  bne NoFlagGround
  phx
  ldx #7
FlagSave:
  lda R0,x
  pha
  dex
  bpl FlagSave
  ldy BlockBufferAdderData+6
  jsr BlockBufferColli_Feet
  jsr FlagSolid
  bcs HasFlagGround
  ldy BlockBufferAdderData+6
  iny
  jsr BlockBufferColli_Feet
  jsr FlagSolid
  bcs HasFlagGround
  ldy #0
  beq FlagRestore
HasFlagGround:
  ldy #1
FlagRestore:
  ldx #0
FlagPop:
  pla
  sta R0,x
  inx
  cpx #8
  bne FlagPop
  plx
  cpy #1
  rts
NoFlagGround:
  clc
  rts
FlagSolid:
  tay
  lda MTileAttribute,y
  and #MTILE_SOLID | MTILE_CLIMB
  cmp #MTILE_SOLID
  beq FlagIsSolid
  clc
  rts
FlagIsSolid:
  sec
  rts
.popseg
; Native head-cell querying stays separate from source response admission.
; Source HitTester only emits Character.hit(ground,"top") after the LAST
; rectangle was below that ground. A simultaneous horizontal crossing uses
; source calcAxis's penetration comparison (vertical wins exact ties).
.pushseg
.segment "LOWCODE"
RawHead:
  lda #0
  sta BillHeadFiltering
  jmp Head
.popseg
FilteredHead:
  lda #$80
  sta BillHeadFiltering
  jsr Head
  pha
  lda #0
  sta BillHeadFiltering
  pla
  cmp #0
  rts
.pushseg
.segment "LOWCODE"
CachePrevious:
  lda Player_X_Position
  sta BillBodyPrevX
  lda Player_PageLoc
  sta BillBodyPrevX+1
  lda MmXFraction
  sta BillBodyPrevXF
  lda MmXFraction+1
  sta BillBodyPrevXF+1
  lda Player_Y_Position
  sta BillBodyPrevY
  lda Player_Y_HighPos
  sta BillBodyPrevY+1
  lda MmYFraction
  sta BillBodyPrevYF
  lda MmYFraction+1
  sta BillBodyPrevYF+1
  lda BillSourceBodyForm
  sta BillBodyPrevForm
  lda PlayerFacingDir
  sta BillBodyPrevFacing
  lda CrossoverBehaviorVersion
  sta BillBodyPrevMode
  lda #1
  sta BillBodyPrevValid
  lda #0
  sta BillHeadFiltering
  rts
.popseg
HeadAdmission:
  ; Coins keep the existing pickup path. Non-solid vine/climb queries keep
  ; their existing native policy; this admission concerns solid ground.
  lda R3
  jeq AdmitImmediate
  cmp #$c2
  jeq AdmitImmediate
  cmp #$c3
  jeq AdmitImmediate
  tax
  lda MTileAttribute,x
  and #MTILE_CLIMB
  jne AdmitImmediate             ; vine is a separate retained native consumer.
  lda MTileAttribute,x
  and #MTILE_SOLID | MTILE_BUMP
  jeq AdmitImmediate
  lda BillBodyPrevValid
  jeq AdmitImmediate             ; pre-active entrance; first Movement arms cache.
  ldx #0
AdmissionSave:
  lda R0,x
  pha
  inx
  cpx #8
  bne AdmissionSave
  lda RgTempX
  and #$f0
  sta R0                        ; full authored cell left = R1:R0.
  lda RgTempPage
  sta R1
  lda R2
  clc
  adc #48
  sta R2                        ; cell bottom, not head lower-nibble rounding.
  lda BillBodyPrevForm
  cmp #2
  jeq AdmissionDenied           ; source LAST cState crouch rejects ceiling.
  asl
  asl
  tax
  clc
  lda BillBodyPrevYF
  adc YEdges,x
  sta R3
  lda BillBodyPrevYF+1
  adc YEdges+1,x
  sta R4
  lda BillBodyPrevY
  adc YEdges+2,x
  sta R5
  lda BillBodyPrevY+1
  adc #0
  cmp #1
  jcc AdmissionDenied
  bne FromBelow
  lda R5
  cmp R2
  jcc AdmissionDenied           ; floor(lastTop)>=integer groundBottom exact.
FromBelow:
  lda BillBodyPrevFacing
  and #2
  asl
  asl
  clc
  adc #4
  tax
  jsr PreviousXEdge
  lda R3
  ora R4
  beq PreviousRightCeil
  inc R5
  bne PreviousRightCeil
  inc R6
PreviousRightCeil:
  lda R6
  cmp R1
  bcc RightCorner
  bne CheckLeftCorner
  lda R5
  cmp R0
  bcc RightCorner
  beq RightCorner               ; ceil(lastRight)<=integer groundLeft exact.
CheckLeftCorner:
  lda BillBodyPrevFacing
  and #2
  asl
  asl
  tax
  jsr PreviousXEdge
  lda R0
  clc
  adc #16
  sta R7
  lda R1
  adc #0
  sta R4
  lda R6
  cmp R4
  jcc AdmissionAllowed
  bne LeftCorner
  lda R5
  cmp R7
  jcc AdmissionAllowed          ; floor(lastLeft)>=groundRight selects left.
LeftCorner:
  lda #1
  sta R7
  bne CompareCorner
RightCorner:
  lda #0
  sta R7
CompareCorner:
  lda MmVX
  ora MmVX+1
  ora MmVX+2
  beq AdmissionDenied           ; exact source Ground calcAxis vx==0 side rule.
  lda MmVY
  ora MmVY+1
  ora MmVY+2
  beq AdmissionAllowed          ; source vy==0 chooses the vertical side.
  jsr CurrentVerticalPen
  lda R5
  pha
  lda R4
  pha
  lda R3
  pha
  lda PlayerFacingDir
  and #2
  asl
  asl
  ldy R7
  bne CurrentLeft
  clc
  adc #4
  tax
  jsr CurrentXEdge
  lda R5
  sec
  sbc R0
  sta R5
  jmp ComparePenetrations
CurrentLeft:
  tax
  jsr CurrentXEdge
  lda R0
  clc
  adc #16
  sta R6
  lda #0
  sec
  sbc R3
  sta R3
  lda #0
  sbc R4
  sta R4
  lda R6
  sbc R5
  sta R5
ComparePenetrations:
  pla
  sta R6
  lda R3
  sec
  sbc R6
  pla
  sta R6
  lda R4
  sbc R6
  pla
  sta R6
  lda R5
  sbc R6
  bcs AdmissionAllowed          ; source verticalPen<=horizontalPen, tie allowed.
AdmissionDenied:
  sec
  bcs AdmissionRestore
AdmissionAllowed:
  clc
AdmissionRestore:
  ldx #7
AdmissionPop:
  pla
  sta R0,x
  dex
  bpl AdmissionPop              ; DEX/BPL preserve the decision carry.
  rts
AdmitImmediate:
  clc
  rts
PreviousXEdge:
  clc
  lda BillBodyPrevXF
  adc XEdges,x
  sta R3
  lda BillBodyPrevXF+1
  adc XEdges+1,x
  sta R4
  lda BillBodyPrevX
  adc XEdges+2,x
  sta R5
  lda BillBodyPrevX+1
  adc #0
  sta R6
  rts
CurrentXEdge:
  clc
  lda MmXFraction
  adc XEdges,x
  sta R3
  lda MmXFraction+1
  adc XEdges+1,x
  sta R4
  lda Player_X_Position
  adc XEdges+2,x
  sta R5
  rts
CurrentVerticalPen:
  lda BillSourceBodyForm
  asl
  asl
  tax
  clc
  lda MmYFraction
  adc YEdges,x
  sta R3
  lda MmYFraction+1
  adc YEdges+1,x
  sta R4
  lda Player_Y_Position
  adc YEdges+2,x
  sta R5
  lda #0
  sec
  sbc R3
  sta R3
  lda #0
  sbc R4
  sta R4
  lda R2
  sbc R5
  sta R5
  rts

.pushseg
.segment "LOWCODE"
Head:
  ; Head cell selection is deliberately distinct from the integer actor
  ; cache. Inclusive touching at a tile underside chooses floor(top-epsilon).
  ; Native terrain resolution and cell-effect order remain native policies.
  ; The complete horizontal source span has at most two authored columns.
  sty RgTemp3
  lda BillSourceBodyForm
  asl
  asl
  tax
  clc
  lda MmYFraction
  adc YEdges,x
  sta R0
  lda MmYFraction+1
  adc YEdges+1,x
  sta R1
  lda Player_Y_Position
  adc YEdges+2,x
  sta RgTempY
  lda R0
  ora R1
  bne HeadRow
  dec RgTempY
HeadRow:
  lda RgTempY
  cmp #32
  jcc Empty
  cmp #240
  jcs Empty
  and #$f0
  sec
  sbc #32
  sta R2
  ; Center first retains the native priority if it already has an effect.
  clc
  lda Player_X_Position
  adc #8
  sta RgTempX
  lda Player_PageLoc
  adc #0
  sta RgTempPage
  jsr ReadCell
  bne HeadDone
  lda PlayerFacingDir
  and #2
  asl
  asl
  tax
  ; Head uses floor(left); inclusive right edge uses floor(right) directly.
  clc
  lda Player_X_Position
  adc XEdges+2,x
  sta RgTempX
  lda Player_PageLoc
  adc #0
  sta RgTempPage
  clc
  lda MmXFraction
  adc XEdges,x
  sta R0
  lda MmXFraction+1
  adc XEdges+1,x
  sta R1
  lda RgTempX
  adc #0
  sta RgTempX
  lda RgTempPage
  adc #0
  sta RgTempPage
  lda R0
  ora R1
  bne HeadLeftReady
    lda RgTempX
    bne HeadLeftDec
    dec RgTempPage
HeadLeftDec:
    dec RgTempX
HeadLeftReady:
  jsr ReadCell
  bne HeadDone
  lda PlayerFacingDir
  and #2
  asl
  asl
  clc
  adc #4
  tax
  clc
  lda MmXFraction
  adc XEdges,x
  lda MmXFraction+1
  adc XEdges+1,x
  lda Player_X_Position
  adc XEdges+2,x
  sta RgTempX
  lda Player_PageLoc
  adc #0
  sta RgTempPage
  jsr ReadCell
HeadDone:
  pha
  lda RgTempY
  and #15
  sta R4
  ldx #0
  ldy RgTemp3
  pla
  rts
Empty:
  lda #0
  beq HeadDone
ReadCell:
  lda RgTempPage
  and #1
  tay
  lda #>Block_Buffer_1
  sta R7
  lda RgTempX
  sta R5
  lsr
  lsr
  lsr
  lsr
  clc
  adc BlockBufferAddr,y
  sta R6
  ldy R2
  lda (R6),y
  sta R3
  bit BillHeadFiltering
  bpl ReadDone
  jsr HeadAdmission
  bcc ReadDone
  lda #0
  sta R3
ReadDone:
  lda R3
  rts
.popseg
.pushseg
.segment "SAMUS_CROUCH_WATER"
BodyRows: .byte 15,16,14
.popseg
; low fraction,high fraction,whole,padding. Left-facing residual is mirrored.
.pushseg
.segment "LOWCODE"
XEdges:
  .byte $00,$40,1,0, $8c,$c0,14,0
  .byte $74,$3f,1,0, $00,$c0,14,0
YEdges:
  .byte $00,$80,0,0, $00,$c0,15,0, $00,$00,17,0
  .byte $24,$00,32,0, $20,$00,32,0, $0c,$00,32,0
.popseg
.endproc
BillSourceBodyEnd:
.assert BillSourceBodyEnd-BillSourceBodyStart <= 1679,error,"Bill body exceeds old MM2 audio FF tail"
.popseg

BillHotSelect = BillBodyDispatch::Select
BillHotProject = BillBodyDispatch::Project
BillHotRawHead = BillBodyDispatch::RawHead
BillHotCache = BillBodyDispatch::CachePrevious
.include "bill_native_rare.s"

.include "bill_bg_empty.s"
