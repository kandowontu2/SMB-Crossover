; Private linked leaves. No public/native row or physical allocation is changed.
.segment "BB_HOST"
.export BbNativeInput,BbNativeIn,BbNativeOut,BbNativeTile23,BbNativeTile84
.export BbNativeDraw,BbNativeBoxes,BbNativeEnemyAdmission,BbNativeEnd
.export BbNativeProxiesIn,BbNativeProxyPosition,BbNativeProxyRestore
.export BbNativeCeiling,BbNativeDeath
.export BbNativeActorBirth
.export BbNativeProxyCapture,BbNativeObserve,BbNativeBodyContact,BbNativeContactBox
.export BbNativeProxiesOut,BbNativeContacts
.export BbNativeInit,BbNativeRetire
.export BbNativeFresh
.export BbNativeSound,BbNativeEnemyDraw,BbNativeNoop
.export BbNativeTileId,BbNativePair
BbNativeNoop=BbReject+1
.segment "BB_SOUND_HOLE"
; Preserve the original FA81 source-state/AXYP contract. Native audio mapping
; remains a separate cosmetic adapter; this stores the original source event.
BbNativeSound:
 sta $c00f
 tya
 clc
 rts
.segment "BB_HOST"
; The original enemy routine asks its renderer to surround the native victim
; with its actual source-grown bubble pair. Preserve the source import ABI.
BbNativeEnemyDraw:
 php
 pha
 lda $c002,x
 and #16
 beq BbNativeEnemyDrawDone
 lda $c002,x
 and #1
 beq BbNativeEnemyDrawPalette
 lda #3
BbNativeEnemyDrawPalette:
 sta $c102,y
 sta $c106,y
 lda #$26
 sta $c101,y
 lda #$28
 sta $c105,y
BbNativeEnemyDrawDone:
 pla
 plp
 rts

; Real fresh/scene service ABI: no normalized A/X is assumed. Preserve source
; state on a warm same-life scene. Source/native death requests a new-life
; constructor; its source200-update grace remains original behavior.
BbNativeFresh:
 lda $c307
 tax
 bne BbNativeFreshInit
 lda $c304
 cmp #$a7
 beq BbNativeFreshDone
BbNativeFreshInit:
 lda FmGroups
 asl
 lda #0
 rol
 jmp BbNativeInit
BbNativeFreshDone:
 sec
 rts

; A=identity0/1, X=0scene/1newlife. The caller must already own/authenticate
; exclusive RAM2/3. Publish ready only after private state is complete.
BbNativeInit:
 cmp #2
 jcs BbNativeNo
 pha
 txa
 pha
 lda #0
 ldx #0
:
 sta $c000,x
 sta $c100,x
 sta $c200,x
 sta $c300,x
 inx
 bne :-
 pla
 sta $c3ce
 pla
 sta $c300
 jsr BbNativeActor
 lda NumberofLives
 clc
 adc #1
 sta $c000,x
 clc
 adc #4
 sta $c208
 cmp #46
 bcs BbNativeInitMinTimer
 lda #47
 sec
 sbc $c208
 bcs BbNativeInitTimer
BbNativeInitMinTimer:
 lda #2
BbNativeInitTimer:
 sta $c20a
 lda #40
 sta $c292
 lda #1
 sta $c261
 lda #255
 sta $c254
 lda #2
 sta $c25d
 jsr BbSourceInit
 jsr BbSourceSprites
 jsr BbNativeIn
 jsr BbNativeActor
 lda $c3ce
 beq :+
 lda #200
 sta $c011,x
:
 lda $c000,x
 sta $c308
 lda #0
 ldx $c300
 bne :+
 lda #3
:
 ldx PlayerFacingDir
 cpx #1
 bne :+
 ora #64
:
 sta $c102,y
 sta $c106,y
 lda ScreenLeft_X_Pos
 sta $c305
 lda ScreenLeft_PageLoc
 sta $c306
 lda #$a7
 sta $c304
 sec
 rts

.segment "BB_ACTOR_HOLE"
BbNativeActor:
 ldx #$2e
 ldy #0
 lda $c300
 beq :+
 ldx #$42
 ldy #8
:
 rts
.segment "BB_HOST"

BbNativeInput:
 lda $c304
 cmp #$a7
 jne BbNativeNo
 lda $c307
 jne BbNativeNo
 lda OperMode
 cmp #1
 jne BbNativeNo
 lda GameEngineSubroutine
 cmp #8
 jne BbNativeNo
 lda GamePauseStatus
 and #1
 jne BbNativeNo
 lda $c303
 beq :+
 lda FrameCounter
 cmp $c302
 jeq BbNativeNo
:
 lda FrameCounter
 sta $c302
 lda #1
 sta $c303
 jsr BbNativeActor
 ldy #$f5
 lda $c300
 beq :+
 iny
:
 lda SavedJoypadBits
 eor $c301
 and SavedJoypadBits
 sta $c000,y
 lda SavedJoypadBits
 sta $c002,y
 sta $c301
 jsr BbInput
 sec
 rts
BbNativeNo:
 clc
 rts

BbNativeIn:
 jsr BbNativeActor
 lda Player_X_Position
 sta $c309
 sec
 sbc ScreenLeft_X_Pos
 clc
 adc #16
 sta $c103,y
 sta $c30d
 clc
 adc #8
 sta $c107,y
 lda Player_PageLoc
 sta $c30a
 lda Player_Y_Position
 sta $c30b
 clc
 adc #16
 sta $c100,y
 sta $c104,y
 sta $c30e
 lda Player_Y_HighPos
 sta $c30c
 rts

BbNativeOut:
 jsr BbNativeActor
 lda $c103,y
 sec
 sbc $c30d
 sta Player_X_Scroll
 sta $c30f
 asl
 asl
 asl
 asl
 sta Player_X_Speed
 lda $c30f
 ldx #0
 cmp #128
 bcc :+
 dex
:
 clc
 adc $c309
 sta Player_X_Position
 txa
 adc $c30a
 sta Player_PageLoc
 lda $c100,y
 sec
 sbc $c30e
 sta Player_Y_Speed
 ldx #0
 cmp #128
 bcc :+
 dex
:
 clc
 adc $c30b
 sta Player_Y_Position
 txa
 adc $c30c
 sta Player_Y_HighPos
 jsr BbNativeActor
 lda $c003,x
 beq :+
 lda #1
:
 sta Player_State
 lda $c102,y
 and #64
 beq BbNativeFaceLeft
 lda #1
 bne BbNativeFaceReady
BbNativeFaceLeft:
 lda #2
BbNativeFaceReady:
 sta PlayerFacingDir
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sta Player_Pos_ForScroll
 rts

BbNativeTile23:
 lda $c023
 sta $c3d0
 lda $c024
 jmp BbNativeTile
BbNativeTile84:
 lda $c084
 sta $c3d0
 lda $c085
BbNativeTile:
 sta $c3d1
 php
 txa
 pha
 tya
 pha
 lda R6
 pha
 lda R7
 pha
 lda $c3d1
 sec
 sbc #5
 cmp #3
 bcs BbNativeAir
 asl
 asl
 asl
 asl
 asl
 asl
 sta $c3d2
 lda $c3d0
 and #$e0
 lsr
 lsr
 clc
 adc $c3d2
 and #$f0
 tay                       ; source tile row8 -> native metatile row16.
 lda $c3d0
 and #31
 asl
 asl
 asl
 sec
 sbc #16
 sta $c3d0
 lda #0
 sbc #0
 sta $c3d1
 lda $c3d0
 clc
 adc ScreenLeft_X_Pos
 sta $c3d0
 lda $c3d1
 adc ScreenLeft_PageLoc
 cmp #$ff
 beq BbNativeAir
 and #1
 beq :+
 lda #<Block_Buffer_2
 jmp BbNativeBuffer
:
 lda #<Block_Buffer_1
BbNativeBuffer:
 sta R6
 lda #>Block_Buffer_1
 sta R7
 lda $c3d0
 lsr
 lsr
 lsr
 lsr
 clc
 adc R6
 sta R6
 lda (R6),y
 sta $c3d3
 tax
 lda MTileAttribute,x
 and #3
 cmp #1
 bne BbNativeAir
 lda #0
 beq BbNativeQueryReturn
BbNativeAir:
 lda #1
BbNativeQueryReturn:
 sta $c3d4
 pla
 sta R7
 pla
 sta R6
 pla
 tay
 pla
 tax
 plp
 lda $c3d4
 rts

.segment "BB_BOX_HOLE"
BbNativeBoxes:
 jsr BbNativeActor
 lda $c103,y
 sec
 sbc #16
 sta $c3b0
 sta $c3b4
 clc
 adc #15
 sta $c3b2
 sec
 sbc #7
 sta $c3b6
 lda $c100,y
 sta $c3b1
 sta $c3b5
 clc
 adc #15
 sta $c3b3
 sec
 sbc #7
 sta $c3b7
 sec
 rts
.segment "BB_HOST"

BbNativeEnemyAdmission:
 txa
 pha
 asl
 asl
 clc
 adc #$68
 tax
 lda $c000,x
 beq BbNativeEnemyNo
 lda $c002,x
 and #16
 beq BbNativeEnemyNo
 pla
 tax
 sec
 rts
BbNativeEnemyNo:
 pla
 tax
 clc
 rts

BbNativeProxyIndices:
 stx $c3c0
 txa
 asl
 asl
 clc
 adc #$68
 sta $c3c1
 txa
 asl
 asl
 asl
 clc
 adc #$10
 sta $c3c2
 rts

; Required owner-gated native actor-birth ingress, including same-ID reuse.
; CheckpointEnemyID is the actual native slot initialization boundary.
BbNativeActorBirth:
 cpx #6
 jcs BbNativeNo
 lda $c304
 cmp #$a7
 jne BbNativeNo
 txa
 pha
 asl
 tax
 inc $c310,x
 bne :+
 inc $c311,x
:
 pla
 tax
 txa
 asl
 asl
 clc
 adc #$68
 tay
 lda #0
 sta $c000,y
 sta $c002,y
 txa
 asl
 asl
 asl
 asl
 tay
 lda #0
 sta $c320,y
 sec
 rts

BbNativeProxyCapture:
 cpx #6
 jcs BbNativeNo
 jsr BbNativeProxyIndices
 ldx $c3c1
 lda $c000,x
 jeq BbNativeProxyNo
 lda $c002,x
 and #16
 jeq BbNativeProxyNo
 ldx $c3c0
 lda Enemy_Flag,x
 jeq BbNativeProxyNo
 jmi BbNativeProxyNo
 lda Enemy_State,x
 and #32
 jne BbNativeProxyNo
 txa
 asl
 asl
 asl
 asl
 tay
 lda #0
 sta $c320,y
 lda Enemy_ID,x
 sta $c321,y
 lda Enemy_Flag,x
 sta $c322,y
 lda Enemy_State,x
 sta $c325,y
 lda Enemy_X_Speed,x
 sta $c326,y
 lda Enemy_Y_Speed,x
 sta $c327,y
 lda Enemy_MovingDir,x
 sta $c328,y
 lda EnemyIntervalTimer,x
 sta $c329,y
 txa
 asl
 tax
 lda $c310,x
 sta $c323,y
 lda $c311,x
 sta $c324,y
 ldx $c3c0
 lda #1
 sta $c320,y                 ; Publish only after all association fields.
 sec
 rts

BbNativeObserve:
 ldx #0
BbNativeObserveNext:
 jsr BbNativeValidateProxy
 bcs BbNativeObserveValid
 ldy $c3c5
 lda $c320,y
 beq BbNativeObserveValid
 lda #0
 sta $c320,y
 txa
 asl
 asl
 clc
 adc #$68
 tay
 lda #0
 sta $c000,y
BbNativeObserveValid:
 inx
 cpx #6
 bne BbNativeObserveNext
 rts

BbNativeProxiesIn:
 ldx #0
BbNativeProxyNext:
 jsr BbNativeProxyIndices
 lda Enemy_Flag,x
 jeq BbNativeProxyEmpty
 jmi BbNativeProxyEmpty
 lda Enemy_ID,x
 cmp #$15
 jcs BbNativeProxyEmpty
 cmp #$0c
 jeq BbNativeProxyEmpty
 cmp #$14
 jeq BbNativeProxyEmpty
 lda Enemy_State,x
 and #32
 jne BbNativeProxyEmpty
 lda Enemy_Y_HighPos,x
 cmp #1
 jne BbNativeProxyEmpty
 ldx $c3c1
 lda $c000,x
 beq BbNativeProxyVisible
 lda $c002,x
 and #16
 jne BbNativeProxyFinish
BbNativeProxyVisible:
 ldx $c3c0
 lda Enemy_X_Position,x
 sec
 sbc ScreenLeft_X_Pos
 sta $c3c3
 lda Enemy_PageLoc,x
 sbc ScreenLeft_PageLoc
 sta $c3c4
 lda $c3c3
 clc
 adc #16
 sta $c3c3
 lda $c3c4
 adc #0
 jne BbNativeProxyEmpty
 lda $c3c3
 cmp #240
 jcs BbNativeProxyEmpty
 lda Enemy_Y_Position,x
 clc
 adc #8
 jcs BbNativeProxyEmpty
 cmp #224
 jcs BbNativeProxyEmpty
 ldy $c3c2
 sta $c100,y
 sta $c104,y
 lda $c3c3
 sta $c103,y
 clc
 adc #8
 sta $c107,y
 lda #0
 sta $c101,y
 sta $c105,y
 sta $c102,y
 sta $c106,y
 ldx $c3c1
 sta $c001,x
 sta $c002,x
 sta $c003,x
 lda #1
 sta $c000,x
 bne BbNativeProxyFinish
BbNativeProxyEmpty:
 ldx $c3c1
 lda #0
 sta $c000,x
BbNativeProxyFinish:
 ldx $c3c0
 inx
 cpx #6
 jne BbNativeProxyNext
 rts

; Association record16B: active,id,flag,generation16,state,xspeed,yspeed,
; direction,interval. Current generation16 lives atC310+slot*2.
BbNativeValidateProxy:
 cpx #6
 bcs BbNativeInvalidProxy
 stx $c3c0
 txa
 asl
 asl
 asl
 asl
 tay
 sty $c3c5
 lda $c320,y
 beq BbNativeInvalidProxy
 lda Enemy_Flag,x
 beq BbNativeInvalidProxy
 cmp $c322,y
 bne BbNativeInvalidProxy
 lda Enemy_ID,x
 cmp $c321,y
 bne BbNativeInvalidProxy
 lda Enemy_State,x
 and #32
 bne BbNativeInvalidProxy
 txa
 asl
 tay
 lda $c310,y
 sta $c3c6
 lda $c311,y
 ldy $c3c5
 cmp $c324,y
 bne BbNativeInvalidProxy
 lda $c3c6
 cmp $c323,y
 bne BbNativeInvalidProxy
 sec
 rts
BbNativeInvalidProxy:
 clc
 rts

BbNativeProxyPosition:
 jsr BbNativeValidateProxy
 bcc BbNativeProxyNo
 jsr BbNativeProxyIndices
 ldy $c3c2
 lda $c103,y
 sec
 sbc #16
 sta $c3c3
 lda #0
 sbc #0
 sta $c3c4
 lda $c3c3
 clc
 adc ScreenLeft_X_Pos
 sta Enemy_X_Position,x
 lda $c3c4
 adc ScreenLeft_PageLoc
 sta Enemy_PageLoc,x
 lda $c100,y
 sec
 sbc #8
 sta Enemy_Y_Position,x
 lda #1
 sta Enemy_Y_HighPos,x
 lda #0
 sta Enemy_X_Speed,x
 sta Enemy_Y_Speed,x
 sec
 rts
BbNativeProxyNo:
 clc
 rts

BbNativeProxyRestore:
 jsr BbNativeValidateProxy
 bcc BbNativeProxyNo
 lda $c325,y
 sta Enemy_State,x
 lda $c326,y
 sta Enemy_X_Speed,x
 lda $c327,y
 sta Enemy_Y_Speed,x
 lda $c328,y
 sta Enemy_MovingDir,x
 lda $c329,y
 sta EnemyIntervalTimer,x
 lda #0
 sta $c320,y
 sec
 rts

BbNativeProxiesOut:
 ldx #0
BbNativeProxyOutNext:
 jsr BbNativeProxyIndices
 ldx $c3c1
 lda $c000,x
 jeq BbNativeProxyOutDone
 lda $c002,x
 and #16
 beq BbNativeProxyOutExisting
 ldx $c3c0
 txa
 asl
 asl
 asl
 asl
 tay
 lda $c320,y
 bne BbNativeProxyOutExisting
 jsr BbNativeProxyCapture
 bcc BbNativeProxyOutClear
BbNativeProxyOutExisting:
 ldx $c3c0
 txa
 asl
 asl
 asl
 asl
 tay
 lda $c320,y
 beq BbNativeProxyOutDone
 jsr BbNativeProxyPosition
 bcc BbNativeProxyOutClear
 ldx $c3c1
 lda $c002,x
 and #8
 bne BbNativeProxyOutPop
 lda $c002,x
 and #16
 bne BbNativeProxyOutDone
 ldx $c3c0
 jsr BbNativeProxyRestore
 jmp BbNativeProxyOutClear
BbNativeProxyOutPop:
 ldx $c3c0
 stx $c3ed
 stx ObjectOffset
 lda #<ShellOrBlockDefeat
 sta $c3ea
 lda #>ShellOrBlockDefeat
 sta $c3eb
 lda #Bank_ShellOrBlockDefeat
 sta $c3ec
 jsr BbNativeCallService
BbNativeProxyOutClear:
 ldx $c3c0
 txa
 asl
 asl
 asl
 asl
 tay
 lda #0
 sta $c320,y
 jsr BbNativeProxyIndices
 ldx $c3c1
 lda #0
 sta $c000,x
BbNativeProxyOutDone:
 ldx $c3c0
 inx
 cpx #6
 jne BbNativeProxyOutNext
 rts

.segment "BB_BOX_HOLE"
BbNativeContactBox:
 jsr BbNativeBoxes
 ldx #3
:
 lda $c3b4,x
 sta BoundingBox_UL_Corner,x
 dex
 bpl :-
 sec
 rts
.segment "BB_HOST"

; Owner-specific contact replacement. A trapped enemy never enters native
; stomp/injury policy. Other contacts use original9px axis-distance hurt.
BbNativeBodyContact:
 lda $c304
 cmp #$a7
 jne BbNativeNo
 cpx #6
 jcs BbNativeNo
 stx $c3c0
 lda Enemy_Flag,x
 jeq BbNativeNo
 jmi BbNativeNo
 lda Enemy_ID,x
 cmp #$14
 jeq BbNativeNo              ; Powerups retain the native collection path.
 lda Enemy_State,x
 and #32
 jne BbNativeBodyDone
 jsr BbNativeEnemyAdmission
 jcs BbNativeBodyDone
 lda Player_Y_HighPos
 cmp Enemy_Y_HighPos,x
 jne BbNativeBodyDone
 lda Player_X_Position
 sec
 sbc Enemy_X_Position,x
 sta $c3c3
 lda Player_PageLoc
 sbc Enemy_PageLoc,x
 beq BbNativeBodyPositiveX
 cmp #255
 jne BbNativeBodyDone
 lda $c3c3
 cmp #248
 jcc BbNativeBodyDone
 bcs BbNativeBodyNearX
BbNativeBodyPositiveX:
 lda $c3c3
 cmp #9
 jcs BbNativeBodyDone
BbNativeBodyNearX:
 jsr BbNativeActor
 lda $c011,x
 jne BbNativeBodyDone
 lda $c003,x
 jmi BbNativeBodyDone
 lda $c100,y
 sta $c021
 lda $c103,y
 sta $c022
 ldx $c3c0
 lda Enemy_Y_Position,x
 clc
 adc #8
 sta $c140
 lda Enemy_X_Position,x
 sec
 sbc ScreenLeft_X_Pos
 clc
 adc #16
 sta $c143
 ldy #$40                   ; Seventh source enemy/OAM slot is scratch only.
 lda #9
 jsr BbOriginal_C43E
 bcs BbNativeBodyDone
 lda $c300
 beq :+
 jsr BbHurtBob
 jmp BbNativeBodyDone
:
 jsr BbHurtBub
BbNativeBodyDone:
 ldx $c3c0
 sec
 rts

.segment "BB_BOX_HOLE"
BbNativeContacts:
 ldx #0
:
 jsr BbNativeBodyContact
 inx
 cpx #6
 bne :-
 rts
.segment "BB_HOST"

BbNativeRetire:
 ldx #0
BbNativeRetireNext:
 jsr BbNativeProxyRestore    ; Invalid/reused slots receive no native writes.
 ldx $c3c0
 txa
 asl
 asl
 asl
 asl
 tay
 lda #0
 sta $c320,y
 jsr BbNativeProxyIndices
 ldx $c3c1
 lda #0
 sta $c000,x
 ldx $c3c0
 inx
 cpx #6
 bne BbNativeRetireNext
 ldx #$88
 lda #0
:
 sta $c000,x
 inx
 inx
 inx
 inx
 cpx #$c4
 bne :-
 sta $c304
 sta $c303
 sec
 rts

; Preserve the source43px rise unless the actual native metatile is solid.
; Sweep every crossed head pixel; source terrain remains its own8px grid.
BbNativeCeiling:
 lda Player_Y_HighPos
 cmp #1
 jne BbNativeNo
 cmp $c30c
 jne BbNativeNo
 lda $c30b
 cmp #224
 jcs BbNativeNo
 lda Player_Y_Position
 cmp $c30b
 jcs BbNativeNo
 clc
 adc #15
 sta $c3c9
 lda $c30b
 clc
 adc #15
 sta $c3c8
 lda R6
 pha
 lda R7
 pha
BbNativeCeilingSweep:
 ldy $c3c8
 lda #1
 jsr BbNativeSolid
 beq BbNativeCeilingHit
 ldy $c3c8
 lda #14
 jsr BbNativeSolid
 beq BbNativeCeilingHit
 dec $c3c8
 lda $c3c8
 cmp $c3c9
 bne BbNativeCeilingSweep
 lda #0
 beq BbNativeCeilingDone
BbNativeCeilingHit:
 lda $c3c8
 and #$f0
 sta Player_Y_Position       ; block bottom minus visible head offset16.
 jsr BbNativeActor
 lda #2
 sta $c003,x
 lda #0
 sta $c004,x
 lda #1
BbNativeCeilingDone:
 sta $c3cd
 pla
 sta R7
 pla
 sta R6
 lsr $c3cd                  ; C1 only if the head sweep hit a solid tile.
 rts

; A=horizontal inset1/14, Y=native head pixel. Result0solid/1air.
BbNativeSolid:
 sty $c3ca
 clc
 adc Player_X_Position
 sta $c3cb
 lda Player_PageLoc
 adc #0
 and #1
 beq :+
 lda #<Block_Buffer_2
 jmp BbNativeSolidBuffer
:
 lda #<Block_Buffer_1
BbNativeSolidBuffer:
 sta R6
 lda #>Block_Buffer_1
 sta R7
 lda $c3cb
 lsr
 lsr
 lsr
 lsr
 clc
 adc R6
 sta R6
 lda $c3ca
 sec
 sbc #32
 cmp #208
 bcs BbNativeSolidAir
 and #$f0
 tay
 lda (R6),y
 tax
 lda MTileAttribute,x
 and #3
 cmp #1
 bne BbNativeSolidAir
 lda #0
 rts
BbNativeSolidAir:
 lda #1
 rts

; Native death occurs once after the source injury animation loses a life,
; or before the source engine's screen-wrap can turn a native pit into sky.
BbNativeDeath:
 lda $c307
 jne BbNativeNo
 jsr BbNativeActor
 lda $c000,x
 cmp $c308
 bcc BbNativeKill
 sta $c308
 lda Player_Y_HighPos
 cmp #1
 bne BbNativePitHigh
 lda Player_Y_Position
 cmp #240
 jcc BbNativeNo
 bcs BbNativeKill
BbNativePitHigh:
 cmp #2
 jcc BbNativeNo
BbNativeKill:
 lda #1
 sta $c307
 lda #<KillPlayer
 sta $c3ea
 lda #>KillPlayer
 sta $c3eb
 lda #Bank_KillPlayer
 sta $c3ec
 lda #0
 sta $c3ed
 jsr BbNativeCallService
 sec
 rts

BbNativeCallService:
 ldx #0
:
 lda R0,x
 pha
 inx
 cpx #8
 bne :-
 ldx #0
:
 ldy BbNativeSmcOffsets,x
 lda $0100,y
 pha
 inx
 cpx #5
 bne :-
 lda $c3ed
 sta R1
 lda $c3ea
 sta FarcallJmpTarget_SMC+1
 lda $c3eb
 sta FarcallJmpTarget_SMC+2
 ldx $c3ed
 lda $c3ec
 jsr FarCallCommon
 ldx #4
:
 pla
 ldy BbNativeSmcOffsets,x
 sta $0100,y
 dex
 bpl :-
 ldx #7
:
 pla
 sta R0,x
 dex
 bpl :-
 sec
 rts

BbNativeDraw:
 php
 pha
 txa
 pha
 tya
 pha
 ldx #0
BbNativeSave:
 lda R0,x
 pha
 inx
 cpx #8
 bne BbNativeSave
 ldx #0
BbNativeSaveSmc:
 ldy BbNativeSmcOffsets,x
 lda $0100,y
 pha
 inx
 cpx #5
 bne BbNativeSaveSmc
 lda #0
 sta $c3cf
 lda $c304
 cmp #$a7
 jne BbNativeDrawRestore
 lda CurrentOAMOffset
 and #3
 jne BbNativeDrawRestore
 lda GuestOamRotationActive
 beq :+
 lda RgOamRotation
 and #3
 jne BbNativeDrawRestore
:
 jsr BbNativeShiftCamera
 jsr BbNativeIn
 jsr BbNativeActor
 lda $c000,x
 beq BbNativeDrawBubbles
 jsr BbNativePair
BbNativeDrawBubbles:
 ldx #$68
 ldy #$10
BbNativeDrawLoop:
 cpx #$88
 bcs BbNativeDrawActive
 lda $c002,x
 and #16
 beq BbNativeDrawAdvance
BbNativeDrawActive:
 lda $c000,x
 beq :+
 txa
 pha
 tya
 pha
 jsr BbNativePair
 pla
 tay
 pla
 tax
:
BbNativeDrawAdvance:
 inx
 inx
 inx
 inx
 tya
 clc
 adc #8
 tay
 cpx #$80
 bne :+
 ldx #$88
 ldy #$88
:
 cpx #$c4
 bne BbNativeDrawLoop
 lda #0
 sta ObjectMetasprite
 lda #<ObjectMetasprite
 sta SmPosePtr
 lda #>ObjectMetasprite
 sta SmPosePtr+1
 inc $c3cf
BbNativeDrawRestore:
 ldx #4
:
 pla
 ldy BbNativeSmcOffsets,x
 sta $0100,y
 dex
 bpl :-
 ldx #7
:
 pla
 sta R0,x
 dex
 bpl :-
 lda $c3cf
 beq BbNativeDrawRejected
 pla
 tay
 pla
 tax
 pla
 plp
 sec
 rts
BbNativeDrawRejected:
 pla
 tay
 pla
 tax
 pla
 plp
 clc
 rts

BbNativePair:
 lda $c100,y
 cmp #240
 bcs BbNativePairDone
 sta R6
 lda #1
 sta R7
 lda $c103,y
 sec
 sbc #16
 sta R4
 lda #0
 sbc #0
 sta R5
 lda $c101,y
 jsr BbNativeTileId
 bcc BbNativePairDone
 sta $c3e5
 lda $c105,y
 jsr BbNativeTileId
 bcc BbNativePairDone
 sta $c3e1
 lda $c102,y
 sta $c3e6
 lda $c106,y
 sta $c3e2
 lda $c104,y
 sec
 sbc $c100,y
 sta $c3e3
 lda $c107,y
 sec
 sbc $c103,y
 sta $c3e4
 lda #0
 sta $c3e7
 sta $c3e8
 sta R3
 lda #8
 sta $c3e0
 lda #<$c3e0
 sta R0
 lda #>$c3e0
 sta R1
 lda #<MetaspriteRenderLoop
 sta FarcallJmpTarget_SMC+1
 lda #>MetaspriteRenderLoop
 sta FarcallJmpTarget_SMC+2
 lda #0
 sta SafecallA_SMC+1
 lda #Bank_MetaspriteRenderLoop
 jsr FarCallCommon
BbNativePairDone:
 rts
BbNativeTileId:
 cmp #$27
 bne :+
 lda #$31
 sec
 rts
:
 cmp #$30
 bcs BbNativeTileBad
 lsr
 bcs BbNativeTileBad
 asl
 ora #1
 sec
 rts
BbNativeTileBad:
 clc
 rts
BbNativeSmcOffsets:
 .byte <(NextBank_SMC+1),<(SafecallA_SMC+1),<(FarcallJmpTarget_SMC+1),<(FarcallJmpTarget_SMC+2),<(SafereturnA_SMC+1)
.include "bubble_bobble_native_frame_1101_v3.inc"
BbNativeEnd:
