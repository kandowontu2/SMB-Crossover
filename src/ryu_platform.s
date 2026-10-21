; UNAPPLIED, known native horizontal platform $28 / bbox5 only.
; Geometric anchors use the native Q8 horizontal position, translated to the
; pinned normal-4 HRect32x8 and Ryu normal/climb HRect13.5x25. The native actor
; phase/order remains native; post-enemy follow observes its final position.
.pushseg
.segment "SRAM"
RyPlatformSlot: .res 1           ; zero or native slot+1.
RyPlatformCancel: .res 1         ; bit7 attached-left; low5 cancel updates.
.assert RyPlatformSlot=RyWallScanLast+1, error, "Platform state must append after17 wall bytes"
.assert * <= $8000, error, "Platform state exceeds SRAM"

.macro RP_Save
  php
  pha
  phx
  phy
  .repeat 8, I
    lda R0+I
    pha
  .endrepeat
  lda RgTempX
  pha
  lda RgTempPage
  pha
  lda RgTempY
  pha
  lda RgTemp2
  pha
  lda RgTemp3
  pha
.endmacro
.macro RP_Restore
  pla
  sta RgTemp3
  pla
  sta RgTemp2
  pla
  sta RgTempY
  pla
  sta RgTempPage
  pla
  sta RgTempX
  .repeat 8, I
    pla
    sta R7-I
  .endrepeat
  ply
  plx
  pla
  plp
.endmacro

.segment "ROSTER"
RyuPlatformCodeStart:

; Native platform SideC admission. C=1 suppresses only its ordinary side nudge.
.proc RyuPlatformSide
  RP_Save
  lda R0
  sta R3
  jsr RyuPlatformActor
  jcc No
  lda RyPlatformSlot
  beq New
  ; Source already climbing a platform: another side contact does not steal it.
  jsr RyuPlatformLoad
  jcc No
  jsr RyuPlatformAlign
  jsr RyuPlatformBox
  jmp Yes
New:
  lda RyPlatformCancel
  and #$1f
  jne No
  lda XgWallLock
  ora GuestHurtTicks
  ora RgCrouch
  ora RgAttack                 ; retained attack shape remains unsupported.
  jne No
  lda Player_State
  cmp #1
  jne No
  lda RyWallWasGround          ; zero is previous grounded, not a Boolean air flag.
  jeq No
  lda RyWallSupported
  jeq No
  lda RyWallOldHeight
  cmp #25
  jne No
  lda SavedJoypadBits
  and R3
  jeq No
  lda Player_Y_HighPos
  cmp #1
  jne No
  lda Player_Y_Position
  cmp #176
  jcs No
  jsr RyuPlatformVertical
  jcc No
  ; Exact current overlap in the pinned source width; native bbox alone is not
  ; the oracle. R4..6 hold an actor edge Q16 (its low fractional byte is zero).
  ldy #0
  jsr RyuPlatformEdge
  lda #14
  ldy #$c0
  jsr RyuPlatformCurrentPoint
  jsr RyuPlatformCompare
  jmi No
  ldy #32
  jsr RyuPlatformEdge
  lda #1
  ldy #$40
  jsr RyuPlatformCurrentPoint
  jsr RyuPlatformCompare
  cmp #1
  jeq No
  ; Direct previous-side branch only. Diagonal calcAxis cases are excluded.
  lda R3
  cmp #2
  beq PreviousLeft
  ldy #0
  jsr RyuPlatformEdge
  lda #14
  ldy #$c0
  jsr RyuPlatformOldPoint
  jsr RyuPlatformCompare
  cmp #1
  jeq No
  lda #0
  beq Attach
PreviousLeft:
  ldy #32
  jsr RyuPlatformEdge
  lda #1
  ldy #$40
  jsr RyuPlatformOldPoint
  jsr RyuPlatformCompare
  jmi No
  lda #$80
Attach:
  sta RyPlatformCancel
  txa
  clc
  adc #1
  sta RyPlatformSlot
  lda #0
  sta RyWallSide
  sta RyWallResolved
  sta XgJumpUsed
  sta AvSlash
  sta AvFlip
  lda #AV_SFX_RYUJUMP
  sta AvAudioRequest
::RyuPlatformAttached:
  jsr RyuPlatformAlign
  jsr RyuPlatformBox           ; later native actors must see the new location.
Yes:
  RP_Restore
  sec
  rts
No:
  RP_Restore
  clc
  rts
.endproc

; X is the actual native actor. All rejected types retain native behavior.
.proc RyuPlatformActor
  cpx #6
  bcs No
  lda Enemy_Flag,x
  cmp #1
  bne No
  lda Enemy_ID,x
  cmp #$28
  bne No
  lda Enemy_BoundBoxCtrl,x
  cmp #5
  bne No
  lda Enemy_State,x
  bne No
  lda Enemy_Y_HighPos,x
  cmp #1
  bne No
  lda Enemy_Y_Position,x
  cmp #32
  bcc No
  cmp #208
  bcs No
  sec
  rts
No:
  clc
  rts
.endproc

; Current and previous bodies vertically straddle the platform side. Source
; current overlap is inclusive; previous top/bottom direct-side tests strict.
.proc RyuPlatformVertical
  lda Enemy_Y_Position,x
  clc
  adc #8
  sta R4
  lda Player_Y_Position
  clc
  adc #7
  cmp R4
  bcc CurrentBottom
  bne No
  lda MmYFraction
  ora MmYFraction+1
  bne No
CurrentBottom:
  lda Player_Y_Position
  clc
  adc #32
  cmp Enemy_Y_Position,x
  bcc No
  lda RyWallOldY
  clc
  adc #7
  cmp R4
  bcs No
  lda RyWallOldY
  clc
  adc #32
  cmp Enemy_Y_Position,x
  bcc No
  bne Yes
  lda RyWallOldYFine
  ora RyWallOldYFrac
  beq No
Yes:
  sec
  rts
No:
  clc
  rts
.endproc

; Y=0 left edge,32 right edge. Native force is the Q8 position residue.
.proc RyuPlatformEdge
  sty R4
  clc
  lda Enemy_X_Position,x
  adc R4
  sta R4
  lda Enemy_PageLoc,x
  adc #0
  sta R5
  lda Enemy_X_MoveForce,x
  sta R6
  rts
.endproc
.proc RyuPlatformCurrentPoint
  sta RgTempY
  sty R7
  clc
  lda MmXFraction+1
  adc R7
  sta RgTemp2
  lda Player_X_Position
  adc RgTempY
  sta RgTempX
  lda Player_PageLoc
  adc #0
  sta RgTempPage
  lda MmXFraction
  sta RgTemp3
  rts
.endproc
.proc RyuPlatformOldPoint
  sta RgTempY
  sty R7
  clc
  lda RyWallOldXFrac
  adc R7
  sta RgTemp2
  lda RyWallOldX
  adc RgTempY
  sta RgTempX
  lda RyWallOldPage
  adc #0
  sta RgTempPage
  lda RyWallOldXFine
  sta RgTemp3
  rts
.endproc
; A=$ff/0/1 for point below/equal/above actor edge; all four bytes compared.
.proc RyuPlatformCompare
  lda RgTempPage
  cmp R5
  bcc Less
  bne Greater
  lda RgTempX
  cmp R4
  bcc Less
  bne Greater
  lda RgTemp2
  cmp R6
  bcc Less
  bne Greater
  lda RgTemp3
  beq Equal
Greater:
  lda #1
  rts
Less:
  lda #$ff
  rts
Equal:
  lda #0
  rts
.endproc

; C=1 known live attachment; X=its slot. Identity is invalidated at real
; EraseEnemyObject, so a newly reused slot cannot inherit the old attachment.
.proc RyuPlatformLoad
  lda RyPlatformSlot
  jeq No
  sec
  sbc #1
  tax
  jsr RyuPlatformActor
  jcc No
  lda GuestHurtTicks
  jne No
  lda Player_State
  cmp #1
  jne No
  lda GameEngineSubroutine
  cmp #8
  jne No
  lda RyPlatformCancel
  bmi Left
  lda #1
  bne Side
Left:
  lda #2
Side:
  sta R3
  ; Discontinuous/reused/teleported actor protection. Source MAX_PLAT_DIST=30
  ; Flashpx=15 NESpx. Exact endpoint checks include both fractional bytes.
  lda #8
  ldy #0
  jsr RyuPlatformCurrentPoint
  lda R3
  cmp #1
  beq LeftEdge
  ldy #32
  bne Edge
LeftEdge:
  ldy #0
Edge:
  jsr RyuPlatformEdge
  ; Compare current center against edge +/-15.
  sec
  lda R4
  sbc #15
  sta R4
  lda R5
  sbc #0
  sta R5
  jsr RyuPlatformCompare
  jmi No
  clc
  lda R4
  adc #30
  sta R4
  lda R5
  adc #0
  sta R5
  jsr RyuPlatformCompare
  cmp #1
  jeq No
  ; |canonicalY - platformY +15.5| <=15: Y+30.5 >= PY and Y+0.5 <=PY.
  clc
  lda MmYFraction+1
  adc #$80
  sta R4
  lda Player_Y_Position
  adc #30
  cmp Enemy_Y_Position,x
  jcc No
  clc
  lda MmYFraction+1
  adc #$80
  lda Player_Y_Position
  adc #0
  cmp Enemy_Y_Position,x
  bcc Yes
  jne No
  lda R4
  ora MmYFraction
  jne No
Yes:
  sec
  rts
No:
  clc
  rts
.endproc

.proc RyuPlatformAlign
  lda R3
  sta XgWall
  sta XgWallContact
  sta PlayerFacingDir
  cmp #2
  beq Left
  clc
  lda Enemy_X_MoveForce,x
  adc #$40                    ; left edge -14.75.
  sta MmXFraction+1
  lda Enemy_X_Position,x
  adc #$f1
  sta Player_X_Position
  lda Enemy_PageLoc,x
  adc #$ff
  jmp Page
Left:
  clc
  lda Enemy_X_MoveForce,x
  adc #$c0                    ; right edge -1.25 = left+30.75.
  sta MmXFraction+1
  lda Enemy_X_Position,x
  adc #30
  sta Player_X_Position
  lda Enemy_PageLoc,x
  adc #0
Page:
  sta Player_PageLoc
  sec
  lda Enemy_Y_Position,x
  sbc #16
  sta Player_Y_Position
  lda #$80                    ; source midpoint + half25px body, foot anchor32.
  sta MmYFraction+1
  lda #0
  sta MmXFraction
  sta MmYFraction
  sta RyWallSide
  sta RyWallResolved
  sta MmVX
  sta MmVX+1
  sta MmVX+2
  sta MmVY
  sta MmVY+1
  sta MmVY+2
  sta Player_X_Speed
  sta Player_X_Scroll
  sta Player_Y_Speed
  sta XgGravity
  sta XgGravity+1
  rts
.endproc
.proc RyuPlatformBox
  jsr RelativePlayerPosition
  ldx #0
  jsr BoundingBoxCore
  farcall RyuSourceBodyBox
  rts
.endproc
.proc RyuPlatformClear
  lda #0
  sta RyPlatformSlot
  sta RyPlatformCancel
  sta XgWall
  sta XgWallContact
  sta RyWallSide
  sta RyWallResolved
  rts
.endproc

.proc RyuPlatformBefore
  RP_Save
  jsr RyuPlatformLoad
  bcc Invalid
  jsr RyuPlatformAlign
  RP_Restore
  sec
  rts
Invalid:
  jsr RyuPlatformClear
  RP_Restore
  clc
  rts
.endproc
.proc RyuPlatformAfter
  RP_Save
  jsr RyuPlatformLoad
  bcc Invalid
  ; Before has already aligned/integrated at zero velocity. Static map-side
  ; grappling is not allowed to steal the known platform attachment.
  lda R3
  sta XgWall
  sta XgWallContact
  jmp Done
Invalid:
  jsr RyuPlatformClear
Done:
  RP_Restore
  rts
.endproc
.proc RyuPlatformPost
  RP_Save
  lda RyPlatformSlot
  beq Timer
  jsr RyuPlatformLoad
  bcc Invalid
  ; A real native ceiling stop has priority over platform follow.
  lda Player_Y_Speed
  bne Invalid
  jsr RyuPlatformAlign
  jsr RyuPlatformBox
  jmp Done
Invalid:
  jsr RyuPlatformClear
  jmp Done
Timer:
  lda RyPlatformCancel
  and #$1f
  beq Done
  sec
  sbc #1
  sta RyPlatformCancel
Done:
  RP_Restore
  rts
.endproc

.proc RyuPlatformJump
  lda RyPlatformSlot
  bne Platform
  farcall RyuWallJump, jmp
Platform:
  RP_Save
  lda RgAttack
  beq CanJump
  lda RgAttackKind             ; climbThrowing cannot jump.
  jne No
CanJump:
  jsr RyuPlatformLoad
  jcc No
  lda SavedJoypadBits
  and #Down_Dir
  bne Drop
  jsr RyuPlatformClear
  lda #16                     ; same-update post consumes one, leaving source15.
  sta RyPlatformCancel
  lda #$ab
  sta MmVY
  lda #$6a
  sta MmVY+1
  lda #$fc                    ; source platform topJump always430, even away.
  sta MmVY+2
  lda #24
  sta AvFlip
  lda #0
  sta AvFlipClock
  sta XgJumpUsed              ; existing AfterJumpVelocity increments totrue1.
  sta XgWallLock
  sta XgGravity               ; source gravity preceded attached checkBtns.
  sta XgGravity+1
  lda #AV_SFX_RYUJUMP
  sta AvAudioRequest
  RP_Restore
  sec
  rts
Drop:
  jsr RyuPlatformClear
  lda #0
  sta MmVY
  sta MmVY+1
  sta MmVY+2
  sta XgWallLock
  sta XgGravity
  sta XgGravity+1
  lda #1
  sta XgJumpUsed
  sta Player_State
  RP_Restore
  clc                         ; no AfterJumpVelocity / ordinary jump sound.
  rts
No:
  RP_Restore
  clc
  rts
.endproc
; Actual bank0 cold DrawVine leaf; even alignment prevents2-byte table page-cross.
.align 2, $ea
.proc RyuPlatformOriginalDrawVine
  sty R0                     ;save offset here
  lda Enemy_Rel_YPos         ;get relative vertical coordinate
  clc
  adc VineYPosAdder,y        ;add value using offset in Y to get value
  ldx Vine_ObjOffset,y        ;get offset to vine
  ReserveSpr 6
  sty R2                    ;store sprite data offset here
  ; jsr SixSpriteStacker       ;stack six sprites on top of each other vertically
  ; inlined 
  
.repeat 6, I
  sta Sprite_Data + (I*4),y ;store X or Y coordinate into OAM data
.if I <> 5
  clc
  adc #$08           ;add eight pixels
.endif
.endrepeat

  lda Enemy_Rel_XPos         ;get relative horizontal coordinate
  sta Sprite_X_Position,y    ;store in first, third and fifth sprites
  sta Sprite_X_Position+8,y
  sta Sprite_X_Position+16,y
  clc
  adc #$06                   ;add six pixels to second, fourth and sixth sprites
  sta Sprite_X_Position+4,y  ;to give characteristic staggered vine shape to
  sta Sprite_X_Position+12,y ;our vertical stack of sprites
  sta Sprite_X_Position+20,y
  lda #%00100001             ;set bg priority and palette attribute bits
  sta Sprite_Attributes,y    ;set in first, third and fifth sprites
  sta Sprite_Attributes+8,y
  sta Sprite_Attributes+16,y
  ora #%01000000             ;additionally, set horizontal flip bit
  sta Sprite_Attributes+4,y  ;for second, fourth and sixth sprites
  sta Sprite_Attributes+12,y
  sta Sprite_Attributes+20,y
  ldx #$05                   ;set tiles for six sprites
VineTL:
  lda #VINE_TILE_2           ;set tile number for sprite
  sta Sprite_Tilenumber,y
  iny                        ;move offset to next sprite data
  iny
  iny
  iny
  dex                        ;move onto next sprite
  bpl VineTL                 ;loop until all sprites are done
UpdateOAMPosition
  ldy R2                     ;get original offset
  lda R0                     ;get offset to vine adding data
  bne :+                ;if offset not zero, skip this part
    lda #VINE_TILE_1
    sta Sprite_Tilenumber,y    ;set other tile number for top of vine
  :
  ldx #$00                   ;start with the first sprite again
ChkFTop:
    lda Vine_Start_Y_Position   ;get original starting vertical coordinate
    sec
    sbc Sprite_Y_Position,y    ;subtract top-most sprite's Y coordinate
    cmp #$64                   ;if two coordinates are less than 100/$64 pixels
    bcc :+                ;apart, skip this to leave sprite alone
      lda #$f8
      sta Sprite_Y_Position,y    ;otherwise move sprite offscreen
  :
    iny                        ;move offset to next OAM data
    iny
    iny
    iny
    inx                        ;move onto next sprite
    cpx #$06                   ;do this until all sprites are checked
    bne ChkFTop
  ldy R0                     ;return offset set earlier
  rts

VineYPosAdder:
  .byte $00, $30

.endproc
RyuPlatformCodeEnd:
.assert RyuPlatformCodeEnd-RyuPlatformCodeStart <= 3243, error, "Platform helpers exceed actual privateK ROSTER free bytes"

.segment "SPECIAL_ROSTER"
; Three-byte JMP substitutions and zero-size resume labels keep all old PCs.
.proc RyuPlatformBeforeGate
  lda RyPlatformSlot
  beq Native
  farcall RyuPlatformBefore
  bcs Handled
Native:
  lda RyWallSupported
  jmp RyuSophiaWallBefore::PlatformResume
Handled:
  jmp RyuSophiaWallBefore::Return
.endproc
.proc RyuPlatformAfterGate
  lda RyPlatformSlot
  beq Native
  farcall RyuPlatformAfter
  jmp RyuWallAfterMotion::Done
Native:
  lda RyWallSupported
  jmp RyuWallAfterMotion::PlatformResume
.endproc
.proc RyuPlatformInjuryGate
  sta RyPlatformSlot          ; incoming A=0, preserve original store and flags.
  sta RyPlatformCancel
  sta RyWallSide
  jmp LsrHurtStart::PlatformResume
.endproc

.segment "COLLISION"
.proc RyuPlatformErase
  sta MmEnemyFlash,x          ; exact original A0 store.
  php
  inx
  cpx RyPlatformSlot
  bne Done
  sta RyPlatformSlot
  sta RyPlatformCancel
  sta XgWall
  inc XgJumpUsed              ; attached jump-used was0; source detach sets true.
Done:
  dex
  plp
  rts
.endproc
.popseg
