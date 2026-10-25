.pushseg
.segment "VIC_WORLD"
.proc VvGraphics
 lda VvVariant
 beq :+
 lda MmDeathFlag
 beq LiveParodius
 jmp PnDeathGraphics
LiveParodius:
 jmp PnGraphics
:
 BankPRGC #.bank(VicArtBegin)
 lda MmDeathFlag
 beq Live
 lda VvDeathAge
 cmp #50
 bcs Hidden
 ldx #0
Divide:
 cmp #10
 bcc Died
 sec
 sbc #10
 inx
 bne Divide
Died:
 lda DeathPoses,x
 tax
 jmp Pose
Hidden:
 lda #0
 sta ObjectMetasprite
 lda #<VvEmpty
 sta SmPosePtr
 lda #>VvEmpty
 sta SmPosePtr+1
 rts
Live:
 ldx VvObjAnim
 cpx #1
 bcc Stand
 cpx #4
 bcc Pose
Stand:ldx #1
Pose:
 jsr VvSetPose
 rts
DeathPoses:.byte 45,46,47,48,48
.endproc
.proc VvPortrait
 lda VvVariant
 beq :+
 jmp PnPortrait
:
 BankPRGC #.bank(VicArtBegin)
 ldx #1
 jsr VvSetPose
 jsr VvPublishBody
 jmp VvPalette
.endproc
.proc VvSetPose
 stx VvPose
 lda VvRecordLo,x
 sta SmPosePtr
 lda VvRecordHi,x
 sta SmPosePtr+1
 lda VvBodyChr,x
 sta SmChrBank
 lda Player_SprAttrib
 and #$fc
 sta Player_SprAttrib
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sta Player_Pos_ForScroll
 rts
.endproc
.proc VvPublishBody
 lda SmChrBank
 ldx #1
 ldy #0
 farcall X5SetPhysicalChr,jmp
.endproc
.proc VvDraw
 lda VvVariant
 beq :+
 jmp PnDraw
:
 BankPRGC #.bank(VicArtBegin)
 jsr VvPublishBody
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda MmDeathFlag
 jne Done
 inc VvDrawFirst
 lda VvDrawFirst
 cmp #11
 bcc :+
 lda #0
 sta VvDrawFirst
:sta VvSlot
 lda #11
 sta VvDrawCount
Loop:
 ldx VvSlot
 inx
 lda VvObjAnim,x
 beq Next
 cpx #3
 bcs Projectile
 cpx VvOptions
 bcc Option
 bne Next
Option:
 lda VvObjAnim,x
Projectile:
 tay
 lda VvRecordLo,y
 sta R0
 lda VvRecordHi,y
 sta R1
 lda VvObjX,x
 sec
 sbc #8
 sta R4
 lda #0
 sbc #0
 sta R5
 lda VvObjY,x
 clc
 adc #24
 sta R6
 jsr DrawRecord
Next:
 inc VvSlot
 lda VvSlot
 cmp #11
 bcc :+
 lda #0
 sta VvSlot
:dec VvDrawCount
 bne Loop
 lda #3
 sta VvSlot
Caps:
 ldx VvSlot
 lda VvCapActive,x
 beq CapNext
 lda VvClock
 lsr
 lsr
 and #3
 cmp #3
 bcc :+
 lda #1
:clc
 adc #16
 tay
 lda VvRecordLo,y
 sta R0
 lda VvRecordHi,y
 sta R1
 lda VvCapX,x
 sec
 sbc #8
 sta VvRectX
 lda VvCapPage,x
 sbc #0
 sta VvRectPage
 jsr WorldDrawX
 lda VvCapY,x
 sec
 sbc #8
 sta R6
 jsr DrawRecord
CapNext:
 dec VvSlot
 bpl Caps
 ; Native mushroom/flower actors become visible original capsule artwork.
 ; Their actual emergence and pickup collision remain native SMB actors.
 lda #5
 sta VvSlot
Pickups:
 ldx VvSlot
 lda Enemy_Flag,x
 beq PickupNext
 lda Enemy_ID,x
 cmp #PowerUpObject
 bne PickupNext
 lda PowerUpType,x
 cmp #2
 bcs PickupNext
 lda #0
 sta EnemyMetasprite,x
 lda #<VvPose16
 sta R0
 lda #>VvPose16
 sta R1
 lda Enemy_X_Position,x
 sec
 sbc #8
 sta VvRectX
 lda Enemy_PageLoc,x
 sbc #0
 sta VvRectPage
 jsr WorldDrawX
 lda Enemy_Y_Position,x
 sec
 sbc #8
 sta R6
 jsr DrawRecord
PickupNext:
 dec VvSlot
 bpl Pickups
 jsr VvHud
Done:rts
WorldDrawX:
 lda VvRectX
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda VvRectPage
 sbc ScreenLeft_PageLoc
 sta R5
 rts
DrawRecord:
 lda #1
 sta R7
 lda #0
 sta R3
 farcall MetaspriteRenderLoop
 rts
.endproc
.proc VvHud
 lda VvVariant
 beq :+
 jmp PnHud
:
 ;24 original label/frame tiles, followed by six original-style palette
 ; cursor cells. Attribute row0 covers only HUD rows0..3, never the stage.
 lda DisableScreenFlag
 jne Done
 lda #<394
 sta InvHudPhysical
 lda #>394
 sta X5HudChrUpper
 lda InvHudActive
 bne :+
 inc ReloadCHRBank
:lda #1
 sta InvHudActive
 lda VvHudDirty
 jeq Done
 ldx VRAM_Buffer1_Offset
 cpx #48 ;36-byte HUD append plus terminator must fit84-byte queue
 jcs Done
 lda #$20
 sta VRAM_Buffer1,x
 lda #$24                    ; row1 keeps the power bar inside TV overscan
 sta VRAM_Buffer1+1,x
 lda #24
 sta VRAM_Buffer1+2,x
 txa
 clc
 adc #3
 tax
 lda #0
 sta VvTemp
Cell:
 ldy VvTemp
 lda VvCellOwned,y
 beq Native
 tay
 lda VvMissile-1,y
 ldy VvTemp
 cpy #2
 bne CheckLaser
 lda VvGun
 cmp #2
 beq Blank
 bne Native
CheckLaser:
 cpy #3
 bne CheckOptions
 lda VvGun
 cmp #1
 beq Blank
 bne Native
CheckOptions:
 cpy #4
 bne CheckOwned
 lda VvOptions
 cmp #2
 bcs Blank
 bcc Native
CheckOwned:
 cmp #0
 bne Blank
Native:
 lda VvTemp
 asl
 asl
 tay
 jmp Copy
Blank:ldy #24
Copy:
 lda #4
 sta VvTemp2
Byte:
 lda VvHudCells,y
 sta VRAM_Buffer1,x
 inx
 iny
 dec VvTemp2
 bne Byte
 inc VvTemp
 lda VvTemp
 cmp #6
 bcc Cell
 lda #$23
 sta VRAM_Buffer1,x
 lda #$c1
 sta VRAM_Buffer1+1,x
 lda #6
 sta VRAM_Buffer1+2,x
 txa
 clc
 adc #3
 tax
 ldy #1
Attr:
 lda #$aa
 cpy VvMeter
 bne :+
 lda #$a5
:sta VRAM_Buffer1,x
 inx
 iny
 cpy #7
 bcc Attr
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 lda #<394
 sta InvHudPhysical
 lda #>394
 sta X5HudChrUpper
 lda #1
 sta InvHudActive
 inc ReloadCHRBank
 lda #0
 sta VvHudDirty
Done:rts
; Only0 skips ownership; other values are handled explicitly above.
VvCellOwned:.byte 0,1,1,1,1,5
.include "vic_hud.inc"
.endproc
.proc VvPalette
 lda VvVariant
 beq :+
 jmp PnQueuePalette
:
 ldx VRAM_Buffer1_Offset
 cpx #78 ;6-byte palette append plus terminator must fit84-byte queue
 bcs Done
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$11
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 lda #$0c
 sta VRAM_Buffer1+3,x
 lda #$26
 sta VRAM_Buffer1+4,x
 lda #$2c
 sta VRAM_Buffer1+5,x
 txa
 clc
 adc #6
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
Done:rts
.endproc
.proc VvGetPlayerColors
 farcall X5QueueAreaBackdrop
 jmp VvPalette
.endproc
.segment "VIC_GFX"
VvEmpty:.byte 0
VvRecordLo:
.repeat 49,I
 .if I=1 || I=2 || I=3 || I=4 || I=5 || I=6 || I=7 || I=8 || I=10 || I=16 || I=17 || I=18 || I=36 || I=45 || I=46 || I=47 || I=48
  .byte <.ident(.sprintf("VvPose%d",I))
 .else
  .byte <VvEmpty
 .endif
.endrepeat
VvRecordHi:
.repeat 49,I
 .if I=1 || I=2 || I=3 || I=4 || I=5 || I=6 || I=7 || I=8 || I=10 || I=16 || I=17 || I=18 || I=36 || I=45 || I=46 || I=47 || I=48
  .byte >.ident(.sprintf("VvPose%d",I))
 .else
  .byte >VvEmpty
 .endif
.endrepeat
VvBodyChr:
.repeat 49,I
 .if I=2
  .byte <382
 .elseif I=3
  .byte <384
 .elseif I=45
  .byte <386
 .elseif I=46
  .byte <388
 .elseif I=47
  .byte <390
 .elseif I=48
  .byte <392
 .else
  .byte <380
 .endif
.endrepeat
.popseg
