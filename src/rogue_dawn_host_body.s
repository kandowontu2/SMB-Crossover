; PRIVATE successor to frozen e4b788/d52 motion unit. No menu/native admission.
; Source collision radii are unchanged. Native box bottom is the actual source
; leading-foot plane center+radius+1, used by SMB's platform contact consumer.
; Only sprite window0/palette0 belongs to this BODY unit. World/enemy/effect
; windows1..11 and palette1..3 are never published from Rogue's source image.
.pushseg
.segment "ROGUE_DAWN_HOST"
.export RdBodyStart,RdBodyEnd,RdBodySelectBox,RdBodyBox,RdBodyBoxOwn
.export RdBodyGraphics,RdBodyDynamicPrg,RdBodyColors,RdBodyQueuePalette
.export RdBodyPositionPlatform,RdBodyNewSession,RdBodyNewLife,RdBodyEnterScene
RdBodyStart:

; Trampoline deliberately omits incomingA save: the actual old selector's
; first instruction is LDA SelectedCharacter. Only returned Y is then live.
.proc RdBodySelectBox
 php
 pha
 jsr RdHostEnabled
 bcc Foreign
 pla
 plp
 ldy #1                         ; ignored by the exact source box below
 rts
Foreign:pla
 plp
 jmp MegaManCollisionBox         ; genuine LOW126 owner, not an A-window alias
.endproc

.proc RdBodyBox
 php
 pha
 jsr RdHostEnabled
 bcc Foreign
 pla
 plp
 jmp RdBodyBoxOwn
Foreign:pla
 plp
 farcall LmBoundingBoxGate,jmp
.endproc

; Actual PlayerCtrl scroll may clamp the host coordinate. Synchronize the
; source center to that committed clamp; no separation warp or pose guess.
.proc RdBodyBoxOwn
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sta Player_Rel_XPos
 lda Player_Y_Position
 sta Player_Rel_YPos
 lda Player_X_Position
 clc
 adc #8
 sta RdX
 lda Player_PageLoc
 adc #0
 sta RdRoomHi
 lda Player_Y_Position
 clc
 adc #16
 sta RdY
 lda Player_Rel_XPos
 clc
 adc #8
 sec
 sbc RdRadiusX
 sta BoundingBox_UL_XPos
 lda Player_Rel_XPos
 clc
 adc #8
 clc
 adc RdRadiusX
 sta BoundingBox_LR_Corner
 lda Player_Y_Position
 clc
 adc #16
 sec
 sbc RdRadiusY
 sta BoundingBox_UL_YPos
 lda Player_Y_Position
 clc
 adc #16
 clc
 adc RdRadiusY
 clc
 adc #1                        ; same leading-foot plane as RdHsSupport
 sta BoundingBox_LR_Corner+1
 ldx #0
 ldy #0
 rts
.endproc

; Same real platform ordinate/actor slot as the frozen transaction owner.
; Standing15 keeps native-32; Morph8 keeps its real feet with native-25.
.proc RdBodyPositionPlatform
 php
 pha
 jsr RdHostEnabled
 bcc Foreign
 lda GameEngineSubroutine
 cmp #11
 beq Skip
 lda Enemy_Y_HighPos,x
 cmp #1
 bne Skip
 pla
 sec
 sbc RdRadiusY
 sec
 sbc #1
 sta RdY
 lda Enemy_Y_HighPos,x
 sbc #0
 sta Player_Y_HighPos           ; temporary center-high, then export origin
 lda RdY
 sec
 sbc #16
 sta Player_Y_Position
 lda Player_Y_HighPos
 sbc #0
 sta Player_Y_HighPos
 lda Player_X_Position
 clc
 adc #8
 sta RdX
 lda Player_PageLoc
 adc #0
 sta RdRoomHi
 lda #0
 sta Player_Y_Speed
 sta Player_Y_MoveForce
 sta RdVY
 sta RdGravity
 lda #1
 sta RdFrozenSupport
 pha
 txa
 pha
 tya
 pha
 jsr RdBodyBoxOwn
 pla
 tay
 pla
 tax
 pla
 plp
 rts
Skip:pla
 plp
 rts
Foreign:pla
 plp
 jmp RdTxPositionPlatform
.endproc

; No action/animation advance here. The authentic ControlStep has already
; selected the current frame. The first-record owner repairs C94 again after
; the unchanged resident graphics selector intentionally maps legacy raw2.
.proc RdBodyGraphics
 php
 pha
 jsr RdHostEnabled
 bcc Foreign
 pla
 plp
 farcall RdRenderPlayer
 jsr RdBodyPublishChr
 lda RdColorRequest
 beq NoPalette
 jsr RdBodyQueuePalette
NoPalette:
 lda Player_Rel_XPos
 sta Player_Pos_ForScroll
 rts
Foreign:pla
 plp
 farcall SamusGraphics,jmp
.endproc

.proc RdBodyPublishChr
 lda SmChrBank
 cmp CurrentCHRBank
 bne Changed
 lda X5ChrMode
 cmp #($80|>RD_FIRST_CHR)
 beq Active
Changed:
 lda SmChrBank
 sta CurrentCHRBank
 lda #($80|>RD_FIRST_CHR)
 sta X5ChrMode
 lda #1
 sta ReloadCHRBank
Active:lda #1
 sta X5WideChrActive
 rts
.endproc

; Only body palette0's THREE nonuniversal colors. The original source palette
; routine decides actual suit/missile colors; no area backdrop/holes reset.
; Accepted complete6B queue packet -> clear existing source color request.
; Busy queues retain it. No new cache, pending byte or per-frame forced packet.
.proc RdBodyQueuePalette
 farcall RdRenderPalettePointer
 ldx VRAM_Buffer1_Offset
 cpx #78
 bcs Busy
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$11
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 ldy #1
Copy:lda (R0),y
 sta VRAM_Buffer1+3,x
 inx
 iny
 cpy #4
 bne Copy
 txa
 clc
 adc #3
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 sta RdColorRequest
 sec
 rts
Busy:clc
 rts
.endproc

.proc RdBodyColors
 php
 pha
 jsr RdHostEnabled
 bcc Foreign
 pla
 plp
 lda #1
 sta RdColorRequest
 jmp RdBodyQueuePalette
Foreign:pla
 plp
 farcall X5GetPlayerColors,jmp
.endproc

; Public lifecycle APIs, NOT auto-detection by AreaPointer or invisible state.
; Actual shared callers must call the appropriate one before exposing Rogue.
; Life/scene persistence policy is the approved explicit SMB adaptation.
.proc RdBodyNewSession
 jsr RdHsNewSession
 jmp RdBodyLifecycleDirty
.endproc
.proc RdBodyNewLife
 jsr RdHsNewLife
 jmp RdBodyLifecycleDirty
.endproc
.proc RdBodyEnterScene
 jsr RdHsEnterScene
 jmp RdBodyLifecycleDirty
.endproc
.proc RdBodyLifecycleDirty
 jsr RdHostEnabled
 bcc Done
 jsr RdTxMovementBegin
 lda #1
 sta RdColorRequest
Done:rts
.endproc

; Only the indirect PLAYER path reaches this service. Old world path remains
; CPY0/BNE/JMP wholly in the original44B bank4 shim. A/NZ/C are dead at the
; sole continuation LDA SprObject_X_Position,Y / SEC. X/Y/V/D/I stay exact.
.proc RdBodyDynamicPrg
 php
 pha
 jsr RdHostEnabled
 bcc Foreign
 pla
 plp
 BankPRGC #94
 rts
Foreign:pla
 plp
 jmp RdBodyLegacyDynamicPrg
.endproc
; Genuine old leaf copied by the sparse recipe into this same A95 segment.
.include "legacy-player-prg.s"
RdBodyEnd:
.assert RdBodyStart=$b5d2,error,"Frozen motion unit end"
.assert * <= $c000,error,"Approved A95 body capacity"
.popseg
