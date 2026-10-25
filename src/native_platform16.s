; Private native-platform extension. No alternate actor/collision/render engine.
; Include after the root's HpRects and before use of these routines.
; Root supplies resident HpGraphicsBankCopy (15B) and patches DrawAll's existing
; JSR CrossoverGraphicsBank to JSR HpGraphicsBankCopy. That bridge snapshots
; SmPosePtr into [Lo0,Hi0], then JMPs CrossoverGraphicsBank. See native16.md.
;
; Native helper actor IDs are $25/$28. Enemy_State bit6 marks a helper;
; bit5 additionally selects16px. Root assigns native bbox ctrl5/6 for32/48.
HpNativeDrawLo = HpRects
HpNativeDrawHi = HpRects+7
HpNativeSmallDescriptor = HpRects+14

.pushseg
.segment "CROSSOVER_HELPERS"

; Call during root helper initialization, before publishing any16px actor's
; EnemyMetasprite=METASPRITE_SAMUS_BODY. Slot0 remains the real player pointer;
; slots1..6 all use the same immutable native-girder two-record descriptor.
; A/X/P volatile. No bank/palette/CHR/OAM writes; no new allocated RAM.
.proc HpNativeInitSmallDescriptor
  ldx #8
Copy:
  lda Descriptor,x
  sta HpNativeSmallDescriptor,x
  dex
  bpl Copy
  ldx #6
Pointers:
  lda #<HpNativeSmallDescriptor
  sta HpNativeDrawLo,x
  lda #>HpNativeSmallDescriptor
  sta HpNativeDrawHi,x
  dex
  bne Pointers
  rts
Descriptor:
  ; The first two records of native MetaspritePlatformGirderSmall. The tile
  ; constant carries the mapper's original sprite-bank/pattern-table bits.
  .byte 8, PLATFORM_GIRDER,2,0,0, PLATFORM_GIRDER,2,0,8
.endproc

; Real native large-platform bbox preparation. Same offscreen admission,
; BoundingBoxCore and CheckRightScreenBBox; only tagged helper dimensions
; differ. Must run BEFORE clipping, because clipped endpoints cannot safely
; be shortened afterward. No RAM beyond original native scratch/bbox arrays.
.proc HpNativePlatformBBoxCold
  inx
  jsr GetXOffscreenBits
  dex
  cmp #$fe
  bcc Onscreen
  jmp MoveBoundBoxOffscreen
Onscreen:
  txa
  clc
  adc #1
  tax
  ldy #1
  jsr BoundingBoxCore             ; X=actor+1,Y=4*(actor+1),raw native endpoints.
  lda Enemy_State-1,x
  and #$20
  beq Height
  lda BoundingBox_UL_XPos,y
  clc
  adc #16
  sta BoundingBox_DR_XPos,y
Height:
  lda BoundingBox_UL_YPos,y
  clc
  adc #8
  sta BoundingBox_DR_YPos,y
  jmp CheckRightScreenBBox        ; Native clipping restores ObjectOffset inX.
.endproc
.popseg
