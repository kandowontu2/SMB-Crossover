; Actual ShotPointer entry: X=slot, A=nonzero original source pose.
; No extra renderer admission on uncommon poses. Scratch world/page
; subtraction is performed directly; its discarded input copies vanish.
.pushseg
.segment "TN_EQUIP_FAST"
.proc TnShotOwnerScope
 cmp #73
 beq Select0
 cmp #74
 beq Select1
 cmp #75
 beq Select2
Legacy:
 tay
 lda TnShotFace,x
 cmp #2
 beq Left
 lda TnWorldRLo,y
 sta R0
 lda TnWorldRHi,y
 sta R1
 jmp Coordinate
Left:
 lda TnWorldLLo,y
 sta R0
 lda TnWorldLHi,y
 sta R1
Coordinate:
 sec
 lda TnShotX,x
 sbc ScreenLeft_X_Pos
 sta R4
 lda TnShotPage,x
 sbc ScreenLeft_PageLoc
 sta R5
 lda TnShotY,x
 sta R6
 lda #1
 sta R7
 lda #0
 sta R3
 jsr TnWorldDraw
 jmp TnDrawEquipment::NextShot
Select0:
 ldy TnShotFace,x
 cpy #2
 beq Left0
 jmp Path0
Left0:
 jmp Path3
Select1:
 ldy TnShotFace,x
 cpy #2
 beq Left1
 jmp Path1
Left1:
 jmp Path4
Select2:
 ldy TnShotFace,x
 cpy #2
 beq Left2
 jmp Path2
Left2:
 jmp Path5
Path0:
 lda #$66
 sta R0
 lda #$d1
 sta R1
 sec
 lda TnShotX,x
 sbc ScreenLeft_X_Pos
 sta R4
 lda TnShotPage,x
 sbc ScreenLeft_PageLoc
 sta R5
 bne PageLegacy0
 php
 lda TnShotY,x
 sta R6
 cmp #24
 bcc RestoreLegacy0
 lda R4
 cmp #8
 bcc RestoreLegacy0
 lda CurrentOAMOffset
 cmp #248
 bcs RestoreLegacy0
 plp
 lda #1
 sta R7
 lda #0
 sta R3
 jsr TnExactShurikenRender::Record0
 jmp TnDrawEquipment::NextShot
RestoreLegacy0:
 plp
LegacyAfterY0:
 lda #1
 sta R7
 lda #0
 sta R3
 jsr TnWorldDraw
 jmp TnDrawEquipment::NextShot
PageLegacy0:
 lda TnShotY,x
 sta R6
 jmp LegacyAfterY0
Path1:
 lda #$6f
 sta R0
 lda #$d1
 sta R1
 sec
 lda TnShotX,x
 sbc ScreenLeft_X_Pos
 sta R4
 lda TnShotPage,x
 sbc ScreenLeft_PageLoc
 sta R5
 bne PageLegacy1
 php
 lda TnShotY,x
 sta R6
 cmp #24
 bcc RestoreLegacy1
 lda R4
 cmp #8
 bcc RestoreLegacy1
 lda CurrentOAMOffset
 cmp #248
 bcs RestoreLegacy1
 plp
 lda #1
 sta R7
 lda #0
 sta R3
 jsr TnExactShurikenRender::Record1
 jmp TnDrawEquipment::NextShot
RestoreLegacy1:
 plp
LegacyAfterY1:
 lda #1
 sta R7
 lda #0
 sta R3
 jsr TnWorldDraw
 jmp TnDrawEquipment::NextShot
PageLegacy1:
 lda TnShotY,x
 sta R6
 jmp LegacyAfterY1
Path2:
 lda #$78
 sta R0
 lda #$d1
 sta R1
 sec
 lda TnShotX,x
 sbc ScreenLeft_X_Pos
 sta R4
 lda TnShotPage,x
 sbc ScreenLeft_PageLoc
 sta R5
 bne PageLegacy2
 php
 lda TnShotY,x
 sta R6
 cmp #24
 bcc RestoreLegacy2
 lda R4
 cmp #8
 bcc RestoreLegacy2
 lda CurrentOAMOffset
 cmp #248
 bcs RestoreLegacy2
 plp
 lda #1
 sta R7
 lda #0
 sta R3
 jsr TnExactShurikenRender::Record2
 jmp TnDrawEquipment::NextShot
RestoreLegacy2:
 plp
LegacyAfterY2:
 lda #1
 sta R7
 lda #0
 sta R3
 jsr TnWorldDraw
 jmp TnDrawEquipment::NextShot
PageLegacy2:
 lda TnShotY,x
 sta R6
 jmp LegacyAfterY2
Path3:
 lda #$cb
 sta R0
 lda #$d2
 sta R1
 sec
 lda TnShotX,x
 sbc ScreenLeft_X_Pos
 sta R4
 lda TnShotPage,x
 sbc ScreenLeft_PageLoc
 sta R5
 bne PageLegacy3
 php
 lda TnShotY,x
 sta R6
 cmp #24
 bcc RestoreLegacy3
 lda R4
 cmp #8
 bcc RestoreLegacy3
 lda CurrentOAMOffset
 cmp #248
 bcs RestoreLegacy3
 plp
 lda #1
 sta R7
 lda #0
 sta R3
 jsr TnExactShurikenRender::Record3
 jmp TnDrawEquipment::NextShot
RestoreLegacy3:
 plp
LegacyAfterY3:
 lda #1
 sta R7
 lda #0
 sta R3
 jsr TnWorldDraw
 jmp TnDrawEquipment::NextShot
PageLegacy3:
 lda TnShotY,x
 sta R6
 jmp LegacyAfterY3
Path4:
 lda #$d4
 sta R0
 lda #$d2
 sta R1
 sec
 lda TnShotX,x
 sbc ScreenLeft_X_Pos
 sta R4
 lda TnShotPage,x
 sbc ScreenLeft_PageLoc
 sta R5
 bne PageLegacy4
 php
 lda TnShotY,x
 sta R6
 cmp #24
 bcc RestoreLegacy4
 lda R4
 cmp #8
 bcc RestoreLegacy4
 lda CurrentOAMOffset
 cmp #248
 bcs RestoreLegacy4
 plp
 lda #1
 sta R7
 lda #0
 sta R3
 jsr TnExactShurikenRender::Record4
 jmp TnDrawEquipment::NextShot
RestoreLegacy4:
 plp
LegacyAfterY4:
 lda #1
 sta R7
 lda #0
 sta R3
 jsr TnWorldDraw
 jmp TnDrawEquipment::NextShot
PageLegacy4:
 lda TnShotY,x
 sta R6
 jmp LegacyAfterY4
Path5:
 lda #$dd
 sta R0
 lda #$d2
 sta R1
 sec
 lda TnShotX,x
 sbc ScreenLeft_X_Pos
 sta R4
 lda TnShotPage,x
 sbc ScreenLeft_PageLoc
 sta R5
 bne PageLegacy5
 php
 lda TnShotY,x
 sta R6
 cmp #24
 bcc RestoreLegacy5
 lda R4
 cmp #8
 bcc RestoreLegacy5
 lda CurrentOAMOffset
 cmp #248
 bcs RestoreLegacy5
 plp
 lda #1
 sta R7
 lda #0
 sta R3
 jsr TnExactShurikenRender::Record5
 jmp TnDrawEquipment::NextShot
RestoreLegacy5:
 plp
LegacyAfterY5:
 lda #1
 sta R7
 lda #0
 sta R3
 jsr TnWorldDraw
 jmp TnDrawEquipment::NextShot
PageLegacy5:
 lda TnShotY,x
 sta R6
 jmp LegacyAfterY5
.endproc
.assert TnShotOwnerScope=$bc8d,lderror,"Verified new A87 tail"
.assert *<=$c000,lderror,"Keep bank87 bounded"
.export TnShotOwnerScope
.popseg
