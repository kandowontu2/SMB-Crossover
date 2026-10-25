; Redraw only the direct small lifts erased by the rotated guest OAM clear.
; Native collision/movement remains untouched. Use the resolved current actor Y
; so late visible girders and the passenger share one source position.
.pushseg
.segment "Z2_COLD"
.proc Z2LateWorldAdmission
 jsr Z2LateLegacyFirebarAdmission
 jsr Z2DrawLateSmallLifts
 rts
.endproc
.include "z2_platform_late_legacy.inc"

.proc Z2DrawLateSmallLifts
 ; The ordinary nonrotated renderer retains its original direct draw.
 ; Absence is register/flag/scratch exact and does not touch shared draw state.
 php
 pha
 phx
 lda GuestOamRotationActive
 beq Absent
 ldx #5
Scan:
 lda Enemy_Flag,x
 beq ScanNext
 bmi ScanNext
 lda Enemy_ID,x
 cmp #$2b
 beq Present
 cmp #$2c
 beq Present
ScanNext:dex
 bpl Scan
Absent:plx
 pla
 plp
 rts
Present:plx
 pla
 plp
 RP_Save
 lda CurrentBankC
 pha
 lda ObjectOffset
 pha
 lda Enemy_OffscreenBits
 pha
 lda FirebarSlot
 pha
 lda FirebarPart
 pha
 lda FirebarTemp
 pha
 BankPRGC #.bank(Z2LateSmallRows)
 lda #5
 sta FirebarSlot
Slot:
 ldx FirebarSlot
 lda Enemy_Flag,x
 jeq NextSlot
 jmi NextSlot
 lda Enemy_ID,x
 cmp #$2b
 beq Owner
 cmp #$2c
 jne NextSlot
Owner:
 lda Enemy_Y_HighPos,x
 cmp #1
 jne NextSlot
 stx ObjectOffset
 jsr GetEnemyOffscreenBits
 ; Preserve the original per-column suppression, including the native
 ; conservative left-edge masks. Bits3/2/1 hide columns0/1/2.
 lda Enemy_OffscreenBits
 and #14
 lsr
 sta FirebarTemp
 lda #0
 sta FirebarPart
Row:
 ldx FirebarSlot
 lda FirebarPart
 beq First
 lda AreaPointer
 cmp #$62
 bne VanillaSecond
 lda WorldNumber
 cmp #1
 beq SourceSecond
 cmp #4
 bne VanillaSecond
SourceSecond:
 lda Enemy_State,x
 jmp RowY
VanillaSecond:
 lda Enemy_Y_Position,x
 clc
 adc #128
 jmp RowY
First:
 lda Enemy_Y_Position,x
RowY:
 cmp #32
 bcc NextRow
 cmp #240
 bcs NextRow
 sta R6
 lda #1
 sta R7
 sec
 lda Enemy_X_Position,x
 sbc ScreenLeft_X_Pos
 sta R4
 lda Enemy_PageLoc,x
 sbc ScreenLeft_PageLoc
 sta R5
 ldx FirebarTemp
 lda Z2LateSmallRowLo,x
 sta R0
 lda Z2LateSmallRowHi,x
 sta R1
 lda #0
 sta R3
 farcall MetaspriteRenderLoop
NextRow:
 inc FirebarPart
 lda FirebarPart
 cmp #2
 bcc Row
NextSlot:
 dec FirebarSlot
 jpl Slot
 pla
 sta FirebarTemp
 pla
 sta FirebarPart
 pla
 sta FirebarSlot
 pla
 sta Enemy_OffscreenBits
 pla
 sta ObjectOffset
 pla
 BankPRGC a
 RP_Restore
 rts
.endproc
.segment "Z2_GFX"
Z2LateSmallRows:
; The source direct renderer uses tile$5a, palette2, at X+0/8/16.
; RenderLoop reads records backwards; data is reversed to retain that order.
.repeat 8, Mask
 .ident(.concat("Z2LateSmallRow",.string(Mask))):
 .if Mask=0
  .byte 12
 .elseif Mask=1 .or Mask=2 .or Mask=4
  .byte 8
 .elseif Mask=7
  .byte 0
 .else
  .byte 4
 .endif
 .repeat 3, Rev
  .if (Mask & (4 >> (2-Rev)))=0
   .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_1}, 2, 0, (2-Rev)*8
  .endif
 .endrepeat
.endrepeat
Z2LateSmallRowLo:
.repeat 8, I
 .byte <.ident(.concat("Z2LateSmallRow",.string(I)))
.endrepeat
Z2LateSmallRowHi:
.repeat 8, I
 .byte >.ident(.concat("Z2LateSmallRow",.string(I)))
.endrepeat
.popseg
