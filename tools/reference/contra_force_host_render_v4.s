; Source-exact predecoded CF body and projectile records. Private RAM worker.
; Full verified CF cookie/C2 + selected31 are outer importer preconditions.
; SourceP3 yellow shots are mapped to a prospective P1 owner; ENTIRE such
; objects are rejected until CfShotPaletteOwned is committed by a qualified
; protocol. This module does not publish/assume that ownership or readiness.
.setcpu "6502"
.macpack longbranch
.import CfState,CfBodyFrameIndex,CfBodyPage,CfBodyBytes,CfBodyLo,CfBodyHi
.import CfShotFrameIndex,CfShotBytes,CfShotLo,CfShotHi,CfShotNeedsLoan
.import CurrentOAMOffset,Sprite_Data,SmChrBank,Player_X_Position,Player_PageLoc
.import ObjectMetasprite,SmPosePtr,BlankPalette,RgOamRotation,GuestOamRotationActive,OperMode
.import CfHostForcePalette
.import InjuryTimer,MmDeathFlag,FrameCounter
.import Player_Y_Position,Player_Y_HighPos,ScreenLeft_X_Pos,ScreenLeft_PageLoc
.import CurrentCHRBank,X5ChrMode,X5WideChrActive,ReloadCHRBank
.importzp CfPointers
.export CfHostRenderBody,CfHostRenderShot,CfHostRenderAll,CfShotPaletteOwned
.export CfHostGraphics,CfHostDraw,CfHostPortrait,CfHostVisible
.export CfRenderSlot,CfRenderRemaining,CfRenderXLo,CfRenderXHi,CfRenderYLo,CfRenderYHi
CfShotPaletteOwned=CfState+$02df ; originally unused source03DF, own selected alias
CfRenderSlot=CfState+$02f1
CfRenderRemaining=CfState+$02f2
CfRenderXLo=CfState+$02f3
CfRenderXHi=CfState+$02f4
CfRenderYLo=CfState+$02f5
CfRenderYHi=CfState+$02f6
CfRenderTemp=CfState+$02f7
CfRenderOutX=CfState+$02f8
CfRenderOutY=CfState+$02f9
CfRenderClip=CfState+$02fa
CfRenderTurn=CfState+$02fb

.segment "CF_HOST_RENDER"
; This genuine resident palette-packet terminator is0 in fixed8000..9FFF,
; independently of current A/C maps. It is DATA, not an instruction alias.
; Native RosterProjectileOamReady may safely read its zero reservation.
CfHostVisible:
 lda MmDeathFlag
 bne CfHostHidden
 lda InjuryTimer
 beq CfHostShown
 lda FrameCounter
 and #1
 bne CfHostHidden
CfHostShown:sec
 rts
CfHostHidden:clc
 rts
CfHostGraphics:
 lda #0
 sta ObjectMetasprite
CfHostEmptyPointer:
 lda #<(BlankPalette+7)
 sta SmPosePtr
 lda #>(BlankPalette+7)
 sta SmPosePtr+1
 rts
CfHostDraw:
 jsr CfHostRenderAll
 jsr CfHostGraphics
 lda CurrentOAMOffset
 sec
 rts
; Original first zero-input player step produces these actual idle frames;
; don't assume freshly zeroed source frame0 contains standing artwork.
CfHostPortrait:
 jsr CfHostForcePalette
 lda CfState+$031a
 pha
 lda CfState+$0334
 pha
 lda Player_Y_Position
 pha
 lda OperMode
 cmp #1
 bne :+
 lda Player_Y_Position
 clc
 adc #56                     ; body center beside native lives x3, below WORLD
 sta Player_Y_Position
:
 lda #0
 sta CfState+$0334
 ldx CfState+$00b1
 lda CfStandingFrames,x
 sta CfState+$031a
 jsr CfHostRenderBody
 pla
 sta Player_Y_Position
 pla
 sta CfState+$0334
 pla
 sta CfState+$031a
 lda CurrentOAMOffset
 sec
 rts
CfStandingFrames:.byte 25,75,117,159
CfHostRenderAll:
 jsr CfHostVisible
 bcc :+
 jsr CfHostRenderBody
:
 lda CfState+$0023
CfModulo12:
 cmp #12
 bcc :+
 sbc #12
 bcs CfModulo12
:
 clc
 adc #10
 sta CfRenderTurn
 ldx #12
CfNextShot:
 txa
 pha
 ldx CfRenderTurn
 jsr CfHostRenderShot
 inc CfRenderTurn
 lda CfRenderTurn
 cmp #22
 bcc :+
 lda #10
 sta CfRenderTurn
:
 pla
 tax
 dex
 bne CfNextShot
 lda CurrentOAMOffset
 sec
 rts

CfHostRenderBody:
 lda #0
 sta CfRenderSlot
 lda CfState+$0334
 jne CfRenderReturn
 ldx CfState+$031a
 cpx #192
 jcs CfRenderReturn
 lda CfBodyFrameIndex,x
 cmp #$ff
 jeq CfRenderReturn
 tax
 lda CfBodyBytes,x
 sta CfRenderRemaining
 lda CfBodyLo,x
 pha
 lda CfBodyHi,x
 pha
 lda CfBodyPage,x
 clc
 adc #$bf                    ; physical959..<968, upper3/window0
 sta SmChrBank               ; preserve genuine final native body publisher
 ldy #0
 ldx #3
 jsr CfRenderPhysicalChr
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sta CfRenderXLo
 lda Player_PageLoc
 sbc ScreenLeft_PageLoc
 sta CfRenderXHi
 lda CfRenderXLo
 clc
 adc #8
 sta CfRenderXLo
 bcc :+
 inc CfRenderXHi
:
 lda Player_Y_Position
 clc
 adc #16
 sta CfRenderYLo
 lda Player_Y_HighPos
 adc #0
 sec
 sbc #1
 sta CfRenderYHi
 jmp CfRenderRecord

CfHostRenderShot:
 stx CfRenderSlot
 cpx #10
 jcc CfRenderReturn
 cpx #22
 jcs CfRenderReturn
 lda CfState+$0382,x
 jeq CfRenderReturn
 lda CfState+$0334,x
 cmp #28
 jne CfRenderReturn
 ldy CfState+$031a,x
 cpy #139
 jcs CfRenderReturn
 lda CfShotFrameIndex,y
 cmp #$ff
 jeq CfRenderReturn
 tay
 lda CfShotNeedsLoan,y
 beq :+
 lda CfShotPaletteOwned
 jeq CfRenderReturn          ; whole object, never an orphan source layer
:
 lda CfShotBytes,y
 sta CfRenderRemaining
 lda CfShotLo,y
 pha
 lda CfShotHi,y
 pha
 lda CfState+$0300,x
 lsr
 lsr
 lsr
 and #$1e
 tay
 lda CfSourceWindowHigh+1,y  ; exact original source viewport admission
 jne CfRenderDropPointer
 lda CfSourceWindowHigh,y
 sta CfRenderXHi
 lda CfState+$034e,x
 sta CfRenderXLo
 lda CfState+$0368,x
 sta CfRenderYLo
 lda #0
 sta CfRenderYHi
 lda #$c8                    ; physical968, upper3/window6
 ldx #3
 ldy #6
 jsr CfRenderPhysicalChr
CfRenderRecord:
 ; Preserve the native borrowed pair even in isolated callback use. Source
 ; fields/actor arrays remain read-only; only own declared render work moves.
 pla
 tay
 pla
 tax
 lda CfPointers
 pha
 lda CfPointers+1
 pha
 stx CfPointers
 sty CfPointers+1
 lda CurrentOAMOffset
 clc
 adc CfRenderRemaining
 jcs CfRenderRestorePointer
 cmp #221                    ; leave32B native world under252B software end
 jcs CfRenderRestorePointer
 ldx CurrentOAMOffset
 lda GuestOamRotationActive
 beq :+
 txa
 clc
 adc RgOamRotation
 tax
:
 ldy #0
CfRenderPart:
 lda #0
 sta CfRenderClip
 lda (CfPointers),y          ; actual source-derived rawOAMdy
 sta CfRenderTemp
 iny
 clc
 adc CfRenderYLo
 sta CfRenderOutY
 lda CfRenderTemp
 bpl :+
 lda #$ff
 bne :++
:
 lda #0
:
 adc CfRenderYHi
 bne CfClipY
 lda CfRenderOutY
 cmp #240
 bcc CfYReady
CfClipY:inc CfRenderClip
CfYReady:
 lda (CfPointers),y          ; source-derived signeddx
 sta CfRenderTemp
 iny
 clc
 adc CfRenderXLo
 sta CfRenderOutX
 lda CfRenderTemp
 bpl :+
 lda #$ff
 bne :++
:
 lda #0
:
 adc CfRenderXHi
 beq CfXReady
 inc CfRenderClip
CfXReady:
 lda CfRenderClip
 bne CfSkipPart
 lda CfRenderOutY
 sta Sprite_Data,x
 lda (CfPointers),y
 sta Sprite_Data+1,x
 iny
 lda (CfPointers),y
 sta Sprite_Data+2,x
 iny
 lda CfRenderOutX
 sta Sprite_Data+3,x
 inx
 inx
 inx
 inx
 jmp CfPartDone
CfSkipPart:
 iny
 iny
CfPartDone:
 cpy CfRenderRemaining
 jne CfRenderPart
 txa
 ldy GuestOamRotationActive
 beq :+
 sec
 sbc RgOamRotation
:
 sta CurrentOAMOffset
CfRenderRestorePointer:
 pla
 sta CfPointers+1
 pla
 sta CfPointers
CfRenderReturn:
 lda CurrentOAMOffset
 sec
 rts
CfRenderDropPointer:
 pla
 pla
 jmp CfRenderReturn

; Byte-for-byte genuine current X5SetPhysicalChr20B, placed in selected C2
; so it stays mapped across rawA changes. A=lowpage X=upper Y=window.
.segment "CF_C2_RENDER_PUBLISHER"
CfRenderPhysicalChr:
 sta CurrentCHRBank,y
 txa
 and #3
 ora #$80
 sta X5ChrMode,y
 lda #1
 sta X5WideChrActive
 sta ReloadCHRBank
 rts

.segment "CF_HOST_RENDER"
; Exact original tbl_D53B/3C, shared by original object-flags viewport math.
CfSourceWindowHigh:
 .byte 0,0,1,0,$ff,0,0,0,0,1,1,1,$ff,1,0,1
 .byte 0,$ff,1,$ff,$ff,$ff,0,$ff,0,0,1,0,$ff,0,0,0
