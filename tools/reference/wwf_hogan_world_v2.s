; Selected C2 world-facing callbacks. No original ring fences or CPU opponent.
.setcpu "6502"
.macpack longbranch
.import WfState,WfProxyValid,WpDir,WpOldX,WpOldPage,WpOldY,WpOldYHi,WpOldJump
.import WfPointX,WfPointPage,WfPointY,WfPointYHi,BlockBufferAddr,MTileAttribute
.import Player_Y_Position,Player_Y_HighPos
.importzp R0,R1,R2,R3,R4,R5,R6,R7
.export WfEnv_WfCbAI,WfEnv_WfCbRingClamp,WfEnv_WfCbRingBounds
.export WfEnv_WfCbAudio09,WfEnv_WfCbAudio0F,WfEnv_WfCbAudio12
.export WfRenderBuffer,WfPreviousInput,WfPosePage,WfPoseIndex,WfPoseWidth,WfCellCount
.export WfWorldWall,WfCueClass,WfCueValue,WfCuePending,WfRenderFace,WfCellOffset
.export WfOwnerPlayer,WfOwnerLife
.segment "WF_RUNTIME_STATE"
WfRenderBuffer:.res 64
WfPreviousInput:.res 1
WfPosePage:.res 1
WfPoseIndex:.res 1
WfPoseWidth:.res 1
WfCellCount:.res 1
WfCellOffset:.res 1
WfRenderFace:.res 1
WfWorldWall:.res 1
WfCueClass:.res 1
WfCueValue:.res 1
WfCuePending:.res 1
WfWorldDelta:.res 1
WfOwnerPlayer:.res 1
WfOwnerLife:.res 1

.segment "WF_WORLD_CALLBACKS"
; The selected actor driver always calls AF4D with X0/Y0. Native SMB
; enemies retain their own AI. If a proxy-intent query is explicitly made,
; marshal its actual native direction rather than advancing another VM.
WfEnv_WfCbAI:
 cpx #1
 bne AIEnd
 lda WfProxyValid
 beq AIEnd
 lda WpDir
 and #3
 sta WfState+$0f
 lda #0
 sta WfState+$10
AIEnd:rts

; The original ring's slanted X fence is inappropriate in an SMB level.
; Probe the real parsed native side tiles at the proposed source delta.
; Native PlayerBGCollision still owns support, head/block, coin and pipe
; progression after export. No level cells or ring-depth values are edited.
WfEnv_WfCbRingClamp:
 cpx #0
 jne ClampEnd
 txa
 pha
 tya
 pha
 lda #0
 sta WfWorldWall
 lda WfState+$2c
 sec
 sbc #128
 sta WfWorldDelta
 beq ClampRestore
 clc
 adc WpOldX
 sta WfPointX
 lda #0
 ldy WfWorldDelta
 bpl :+
 lda #$ff
:
 adc WpOldPage
 sta WfPointPage
 lda WfWorldDelta
 bmi LeftEdge
 lda WfPointX
 clc
 adc #15
 sta WfPointX
 bcc LeftEdge
 inc WfPointPage
LeftEdge:
 lda WfState+$30
 sec
 sbc WpOldJump
 sta WfWorldDelta
 clc
 adc WpOldY
 sta WfPointY
 lda #0
 ldy WfWorldDelta
 bpl :+
 lda #$ff
:
 adc WpOldYHi
 sta WfPointYHi
 lda WfPointY
 clc
 adc #8
 sta WfPointY
 bcc :+
 inc WfPointYHi
:
 jsr WfWorldSolid
 bcs Blocked
 lda WfPointY
 clc
 adc #16
 sta WfPointY
 bcc :+
 inc WfPointYHi
:
 jsr WfWorldSolid
 bcc ClampRestore
Blocked:
 lda #128
 sta WfState+$2c
 lda #1
 sta WfWorldWall
ClampRestore:
 pla
 tay
 pla
 tax
ClampEnd:rts

WfWorldSolid:
 lda WfPointYHi
 cmp #1
 bne Air
 lda WfPointY
 cmp #32
 bcc Air
 cmp #240
 bcs Air
 and #$f0
 sec
 sbc #32
 pha
 lda WfPointPage
 and #1
 tay
 lda BlockBufferAddr+2,y
 sta R7
 lda WfPointX
 lsr
 lsr
 lsr
 lsr
 clc
 adc BlockBufferAddr,y
 sta R6
 pla
 tay
 lda (R6),y
 tay
 lda MTileAttribute,y
 and #3
 cmp #1
 beq Solid
Air:clc
 rts
Solid:sec
 rts

; World eligibility, not ring-depth/rope coordinates. Pit/death viewport
; cannot offer contact actions; ordinary supported SMB space can.
WfEnv_WfCbRingBounds:
 lda #0
 sta WfState+$7f
 lda Player_Y_HighPos
 cmp #1
 bne Outside
 lda Player_Y_Position
 cmp #240
 bcc BoundsEnd
Outside:dec WfState+$7f
BoundsEnd:rts

; Retain genuine source class/value commands for a later audio consumer.
; No stock tune, prerecorded cue or donor-address oracle executes here.
WfEnv_WfCbAudio09:lda #9
 bne QueueCue
WfEnv_WfCbAudio0F:lda #15
 bne QueueCue
WfEnv_WfCbAudio12:lda #18
QueueCue:
 sta WfCueClass
 lda WfState+$06
 sta WfCueValue
 inc WfCuePending
 rts
.export WfWorldCallbacksEnd
WfWorldCallbacksEnd:
