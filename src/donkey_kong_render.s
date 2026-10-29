; Genuine original48x32 poses and16x16 barrels, source3-color palettes.
; Uses normal 8x16 native OAM/rotation/capacity; no sprite-limit bypass.
.pushseg
.segment "DONKEY_KONG_ART"
.proc DkGraphics
 DkGate
 farcall DkEnsure
 lda Player_Rel_XPos
 sta Player_Pos_ForScroll
 lda #0
 sta DkMirror
 lda MmDeathFlag
 beq Live
 ldx #8
 bne Set
Live:
 lda DkAttack
 beq Travel
 ldx #0
 lda DkAge
 cmp #8
 bcc Set
 inx
 cmp #16
 bcc Set
 inx
 bne Set
Travel:
 ldx #3
 lda Player_State
 bne Set
 lda Player_X_Speed
 beq Set
 ; The original NPC has no walking animation. This is a disclosed waddle
 ; using his authentic pickup/toss poses, with facing corrected per pose.
 ldx #2
 lda DkWalk
 bne Set
 ldx #0
 inc DkMirror
Set:
 jmp DkSetPose
.endproc
.proc DkPortrait
 DkGate
 lda #0
 sta DkMirror
 lda #$ff
 sta DkPaletteAck
 ldx #9
 jsr DkSetPose
 jmp DkColors
.endproc

; X=0..8 original pose,9 compact complete menu silhouette. Preserve actual
; input X/Y and R0/R1. Publish the copied descriptor in active RAM so later
; world bank changes cannot turn its pointer into another character's data.
.proc DkSetPose
 stx DkPose
 txa
 pha
 tya
 pha
 lda R0
 pha
 lda R1
 pha
 cpx #9
 beq Menu
 lda DkPoseLo,x
 sta R0
 lda DkPoseHi,x
 sta R1
 lda DkPosePages,x
 clc
 adc #<DK_FIRST_CHR
 bne Page
Menu:
 lda #<DkMenuRecord
 sta R0
 lda #>DkMenuRecord
 sta R1
 lda #<(DK_FIRST_CHR+3)
Page:
 sta DkRenderPage
 sta SmChrBank
 ldy #0
 lda (R0),y
 sta DkTemp
Copy:
 lda (R0),y
 sta DkRenderBuffer,y
 iny
 cpy DkTemp
 bcc Copy
 beq Copy
 ; Mirror around the native PlayerX+8 center: x' =8-x, not -x.
 lda PlayerFacingDir
 cmp #2
 lda #0
 rol
 eor DkMirror
 beq Pointer
 ldy #2
Flip:
 lda DkRenderBuffer,y
 eor #$40
 sta DkRenderBuffer,y
 iny
 iny
 lda #8
 sec
 sbc DkRenderBuffer,y
 sta DkRenderBuffer,y
 iny
 iny
 cpy DkTemp
 bcc Flip
Pointer:
 lda #<DkRenderBuffer
 sta SmPosePtr
 lda #>DkRenderBuffer
 sta SmPosePtr+1
 lda Player_SprAttrib
 and #$fc
 sta Player_SprAttrib
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 jsr DkQueuePalette
 pla
 sta R1
 pla
 sta R0
 pla
 tay
 pla
 tax
 lda #METASPRITE_SAMUS_BODY
 rts
.endproc

; Source P0=DK BG2 and P1=barrels original sprite3. No universal color
; publication here: the native area remains the backdrop owner.
.proc DkColors
 DkGate
 farcall X5QueueAreaBackdrop
 lda #$ff
 sta DkPaletteAck
 jmp DkQueuePalette
.endproc
.proc DkQueuePalette
 lda StarInvincibleTimer
 ora GuestPowerupActive
 beq Normal
 lda #$ff
 sta DkPaletteAck
 rts
Normal:
 lda DkPaletteAck
 beq Done
 ldx VRAM_Buffer1_Offset
 cpx #72                       ;12 bytes plus terminator within84B.
 bcs Done
 lda #$3f
 sta VRAM_Buffer1,x
 sta VRAM_Buffer1+6,x
 lda #$11
 sta VRAM_Buffer1+1,x
 lda #$15
 sta VRAM_Buffer1+7,x
 lda #3
 sta VRAM_Buffer1+2,x
 sta VRAM_Buffer1+8,x
 lda #$30
 sta VRAM_Buffer1+3,x
 lda #$36
 sta VRAM_Buffer1+4,x
 lda #6
 sta VRAM_Buffer1+5,x
 sta VRAM_Buffer1+9,x
 lda #$27
 sta VRAM_Buffer1+10,x
 lda #2
 sta VRAM_Buffer1+11,x
 txa
 clc
 adc #12
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 sta DkPaletteAck
Done:
 rts
.endproc

; Body and projectiles occupy distinct1KB sprite windows. This only queues
; the genuine publisher; no direct visible-time PPU/CHR writes are added.
.proc DkDraw
 DkGate
 lda DkRenderPage
 ldx #>DK_FIRST_CHR
 ldy #0
 farcall X5SetPhysicalChr
 lda #<(DK_FIRST_CHR+3)
 ldx #>(DK_FIRST_CHR+3)
 ldy #1
 farcall X5SetPhysicalChr
 lda #0
 sta DkSlot
Loop:
 ldx DkSlot
 lda DkShots,x
 beq Next
 lda DkShots+1,x
 cmp #6
 bcs Next
 tay
 lda DkBarrelLo,y
 sta R0
 lda DkBarrelHi,y
 sta R1
 ldy #0
Copy:
 lda (R0),y
 sta DkShotBuffer,y
 iny
 cpy #9
 bcc Copy
 lda DkShotBuffer+1
 ora #$40                      ;window1, original8x16 source pair retained.
 sta DkShotBuffer+1
 lda DkShotBuffer+5
 ora #$40
 sta DkShotBuffer+5
 lda #<DkShotBuffer
 sta R0
 lda #>DkShotBuffer
 sta R1
 lda #0
 sta R3
 lda DkShots+4,x
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda DkShots+5,x
 sbc ScreenLeft_PageLoc
 sta R5
 lda DkShots+6,x
 sta R6
 lda #1
 sta R7
 farcall MetaspriteRenderLoop
Next:
 lda DkSlot
 clc
 adc #12
 sta DkSlot
 cmp #36
 bcc Loop
 rts
.endproc
.popseg
