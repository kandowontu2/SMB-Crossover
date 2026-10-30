; Front-end only admission layer. Pending profiles never reach gameplay tables.
; Two previously unused ExRAM variant bytes; cleared on screen entry and launch.
.if ::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5
FmAlts=$5fe5                   ; Karnov/Metal/Shinobi/Bowser/Prince/Quick/Thomas
FmGroups=$5fe8                 ; WWF low3, ContraForce bits3..4
.pushseg
.segment "FULL_ROSTER_MENU"

; Carry set: A is a pending portrait/name index. Carry clear: playable owner.
.proc FmPending
 ldx CrossoverMenuIndex
 cpx #0
 bne NotMario
 lda MarioVariant
 cmp #2
 bne Ready
 lda #0
 sec
 rts
NotMario:
 cpx #2
 bne NotRogue
 lda $5fee
 and #1
 beq Ready
 lda #1
 sec
 rts
NotRogue:
 cpx #7
 bne NotKarnov
 lda FmAlts
 and #1
 beq Ready
 lda #2
 sec
 rts
NotKarnov:
 cpx #9
 bne NotQuickMan
 lda FmAlts
 and #32
 beq Ready
 lda #31
 sec
 rts
NotQuickMan:
 cpx #10
 bne NotShinobi
 lda FmAlts
 and #4
 bne Shinobi
 lda FmAlts
 and #64
 beq Ready
 lda #32
 sec
 rts
Shinobi:
 lda #3
 sec
 rts
NotShinobi:
 cpx #11
 bne Groups
 lda FmAlts
 and #2
 beq Ready
 lda #4
 sec
 rts
Ready:
 clc
 rts
Groups:
 cpx #21
 bne NotFF
 lda $5fef
 and #3
 clc
 adc #5
 sec
 rts
NotFF:
 cpx #23
 bcc Ready
 lda #9
 cpx #23
 beq Pending
 cpx #24
 bne NotSMB2
 lda $5fe3
 and #3
 clc
 adc #10
 bne Pending
NotSMB2:
 lda #14
 cpx #25
 beq Pending
 cpx #26
 bne NotBowser
 lda FmAlts
 and #8
 beq Bowser3
 lda #16
 bne Pending
Bowser3:lda #15
 bne Pending
NotBowser:
 lda #17
 cpx #27
 beq Pending
 cpx #28
 bne NotWWF
 lda FmGroups
 and #7
 clc
 adc #18
 bne Pending
NotWWF:
 cpx #29
 bne ContraForce
 lda FmAlts
 and #16
 beq Bike
 lda #25
 bne Pending
Bike:lda #24
 bne Pending
ContraForce:
 cpx #31
 bne ForceVariant
 lda #30
 sec
 rts
ForceVariant:
 lda FmGroups
 and #24
 lsr
 lsr
 lsr
 clc
 adc #26
Pending:sec
 rts
.endproc

.proc FmResolve
 jsr FmPending
 bcc Native
 lda #0
 sta SelectedCharacter
 sta CmActive
 rts
Native:
 farcall CmHostResolveCharacter,jmp
.endproc

; Handle the newly visible alternate families before legacy Select handlers.
.proc FmToggle
 lda CrossoverMenuPressed
 and #Select_Button
 jeq No
 ldx CrossoverMenuIndex
 bne NotMario
 inc MarioVariant
 lda MarioVariant
 cmp #5
 jcc Yes
 lda #0
 sta MarioVariant
 jeq Yes
NotMario:
 cpx #2
 bne NotRogue
 lda $5fee
 eor #1
 sta $5fee
 jmp Yes
NotRogue:
 cpx #7
 bne NotKarnov
 lda #1
 jmp Flip
NotKarnov:
 cpx #9
 bne NotBass
 lda FmAlts
 and #32
 beq BassOrRoll
 lda FmAlts
 and #$df
 sta FmAlts
 lda #0
 sta RlVariant
 beq BassReady
BassOrRoll:
 lda RlVariant
 beq Roll
 lda FmAlts
 ora #32
 sta FmAlts
 lda #0
 sta RlVariant
 beq BassReady
Roll:inc RlVariant
BassReady:
 lda #0
 sta RlPalette
 jmp Yes
NotBass:
 cpx #10
 bne NotShinobi
 lda FmAlts
 and #68
 beq SelectShinobi
 cmp #4
 beq SelectThomas
 lda #0
 beq RyuAlt
SelectShinobi:lda #4
 bne RyuAlt
SelectThomas:lda #64
RyuAlt:sta R0
 lda FmAlts
 and #$bb
 ora R0
 sta FmAlts
 jmp Yes
NotShinobi:
 cpx #11
 bne NotMetal
 lda #2
 bne Flip
NotMetal:
 cpx #26
 bne NotBowser
 lda #8
 bne Flip
NotBowser:
 cpx #29
 bne NotPrince
 lda #16
Flip:eor FmAlts
 sta FmAlts
 jmp Yes
NotPrince:
 cpx #21
 bne NotFF
 inc $5fef
 lda $5fef
 and #3
 sta $5fef
 jmp Yes
NotFF:
 cpx #24
 bne NotSMB2
 inc $5fe3
 lda $5fe3
 and #3
 sta $5fe3
 jmp Yes
NotSMB2:
 cpx #28
 bne NotWWF
 lda FmGroups
 and #7
 clc
 adc #1
 cmp #6
 bcc WwfLegal
 lda #0
WwfLegal:sta R0
 lda FmGroups
 and #$f8
 ora R0
 sta FmGroups
 jmp Yes
NotWWF:
 cpx #30
 bne No
 lda FmGroups
 clc
 adc #8
 and #31
 sta FmGroups
Yes:sec
 rts
No:clc
 rts
.endproc

.proc FmQueueName
 jsr FmPending
 ; Fixed-width rows, index*16 forms a real16-bit pointer without wrap.
 ldx #<FmNames
 stx R2
 ldx #>FmNames
 stx R3
Page:cmp #16
 bcc Low
 inc R3
 sec
 sbc #16
 bcs Page
Low:asl
 asl
 asl
 asl
 tay
 ldx VRAM_Buffer1_Offset
 lda #$23
 sta VRAM_Buffer1,x
 lda #$28
 sta VRAM_Buffer1+1,x
 lda #16
 sta VRAM_Buffer1+2,x
 sta R0
Copy:lda (R2),y
 sta VRAM_Buffer1+3,x
 inx
 iny
 dec R0
 bne Copy
 txa
 clc
 adc #3
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 rts
.endproc

; Pending previews borrow all four body windows. Restore both the page bytes
; and their direct/legacy interpretation before a native owner rebuilds art.
.proc FmNativePrepare
 farcall X5ClearChrModes
 ldx #7
Restore:
 lda CHRBankInitValues,x
 sta CurrentCHRBank,x
 dex
 bpl Restore
 rts
.endproc

.proc FmDrawPreview
 farcall MoveAllSpritesOffscreen
 farcall X5ClearChrModes
 ldy #0
Map:
 tya
 clc
 adc #$bc                     ; physical700..703, direct MMC5 upper2
 ldx #2
 farcall X5SetPhysicalChr
 iny
 cpy #4
 bcc Map
 jsr FmPending
 pha
 asl
 asl
 tay
 ldx #0
Copy:
 lda FmPreviewTiles,y
 sta Sprite_Data+1,x
 lda #0
 sta Sprite_Data+2,x
 lda FmPreviewX,x
 sta Sprite_Data+3,x
 lda FmPreviewY,x
 sta Sprite_Data,x
 iny
 inx
 inx
 inx
 inx
 cpx #16
 bcc Copy
 stx CurrentOAMOffset
 pla
 sta R0
 asl
 clc
 adc R0
 tay
 ldx VRAM_Buffer1_Offset
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$11
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 lda FmPreviewColors,y
 sta VRAM_Buffer1+3,x
 lda FmPreviewColors+1,y
 sta VRAM_Buffer1+4,x
 lda FmPreviewColors+2,y
 sta VRAM_Buffer1+5,x
 txa
 clc
 adc #6
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 rts
FmPreviewX:.byte 120,0,0,0,128,0,0,0,120,0,0,0,128,0,0,0
FmPreviewY:.byte 159,0,0,0,159,0,0,0,175,0,0,0,175,0,0,0
.endproc

.include "full_roster_menu_art.inc"
.assert * <= $c000,lderror,"Full roster UI exceeds bank76 A-view tail"
.popseg
.endif
