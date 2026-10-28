; Private successor to frozen services9dc533. Actual SMB transaction owners,
; not shared admission, native evidence, or an original Metroid room adapter.
; Include AFTER unchanged services (renamed RdHsFrozenDispatch) and helpers.
; All public entries gate rawSamus2/RdVariant1 BEFORE any overlay read.
.pushseg
.segment "ROGUE_DAWN_HOST"
.macro RdTxFar Target,Bank
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #($80|Bank)
 jsr FarCallCommon
.endmacro
.export RdHostDispatch,RdTxHead,RdTxAfterMovement,RdTxPositionPlatform,RdTxPrepareActor
.export RdTxStart,RdTxEnd
RdTxStart:

; The immutable bridge's actual slots are Health=7, LowHealth=8. The v1
; service dispatcher reversed these two names; preserve that packet, fix here.
.proc RdHostDispatch
 php
 pha
 jsr RdHostEnabled
 bcc Foreign
 lda RdHostService
 cmp #7
 beq Health
 cmp #8
 beq Low
 cmp #12
 beq Up
 pla
 plp
 jmp RdHsFrozenDispatch
Health:pla
 plp
 jmp RdHsHealth
Low:pla
 plp
 jmp RdHsLowHealth
Up:pla
 plp
 jsr RdHsFrozenDispatch
 bcs Done
 ; Only the real MOVE-UP callback can bump. ProbeUp never has side effects.
 jsr RdTxHead
 clc                         ; blocked source pixel remains blocked
Done:rts
Foreign:pla
 plp
 clc
 rts
.endproc

; Real native constructor hook, not collection. Never descend the unrelated
; guest inventory/actor-producer chain with this typed identity. Incoming AXY/P
; survive the hook; no reward/resource state changes until actual collection.
.proc RdTxPrepareActor
 php
 pha
 txa
 pha
 tya
 pha
 jsr RdHostEnabled
 bcc Done
 cpx #6
 bcs Done
 lda Enemy_ID,x
 cmp #$2e
 bne Done
 lda #2
 sta InvPickupOwner,x
 lda #$fc
 sta InvPickup,x
 lda #0
 sta InvRisePhase,x
 sta InvPickupSaveLo,x
 sta InvPickupSaveHi,x
 jsr RdHsPrepareActor
Done:pla
 tay
 pla
 tax
 pla
 plp
 rts
.endproc

; Keep v1's tile/attribute semantics, but do not mistake a retained Rh7 for a
; new tile when v1 rejects an unloaded page before reading the block buffer.
.proc RdTxLoadedCell
 lda Rh3
 cmp #32
 bcc Empty
 cmp #240
 bcs Empty
 lda Rh2
 cmp ScreenLeft_PageLoc
 bcc Empty
 cmp ScreenRight_PageLoc
 beq Read
 bcs Empty
Read:jmp RdHsReadCell
Empty:lda #0
 sta Rh7
 clc
 rts
.endproc

; Native low/fixed-bank transactions use real R0..R7. Preserve the complete
; interrupted foreground scratch image around those genuine callees. Active
; Main owns NmiDisable=FF; this is not a new shared scratch/NMI convention.
.macro RdTxSaveNative
 lda R0
 pha
 lda R1
 pha
 lda R2
 pha
 lda R3
 pha
 lda R4
 pha
 lda R5
 pha
 lda R6
 pha
 lda R7
 pha
.endmacro
.macro RdTxRestoreNative
 pla
 sta R7
 pla
 sta R6
 pla
 sta R5
 pla
 sta R4
 pla
 sta R3
 pla
 sta R2
 pla
 sta R1
 pla
 sta R0
.endmacro

; Rh2=world page, Rh3=screen Y, Rh4=world low X. Actual native pointer+row,
; not a fabricated metatile address or stale PlayerBG scratch. Public callers
; own six saved private temporaries. Rh7 holds the actual current metatile.
.proc RdTxNativeCell
 lda Rh3
 and #$f0
 sec
 sbc #32
 sta R2
 lda Rh4
 lsr
 lsr
 lsr
 lsr
 sta R6
 lda Rh2
 and #1
 asl
 asl
 asl
 asl
 ora R6
 jsr GetBlockBufferAddr
 ldy R2
 lda (R6),y
 sta Rh7
 rts
.endproc

; Preserve the source blocked pixel and native first-solid sample order.
; Only an upward leading pixel CROSSING a tile bottom can bump it. Hitting a
; pipe side halfway up a cell must never trigger head separation/displacement.
.proc RdTxHead
 jsr RdHostEnabled
 jcc No
 RdHsSave
 RdTxSaveNative
 lda Player_Y_HighPos
 cmp #1
 jne Done
 lda RdY
 sec
 sbc RdRadiusY
 sec
 sbc #1
 sta Rh3
 and #15
 cmp #15
 jne Done
 lda Rh3
 cmp #32
 jcc Done
 cmp #240
 jcs Done
 lda #0
 sta Rh6
 sta Rh5                     ; actual UP tile classification
Loop:
 lda RdRoomHi
 sta Rh2
 lda RdX
 sta Rh4
 lda Rh6
 cmp #1
 beq Check
 bcs Right
 lda Rh4
 sec
 sbc RdRadiusX
 sta Rh4
 lda Rh2
 sbc #0
 sta Rh2
 jmp Check
Right:lda Rh4
 clc
 adc RdRadiusX
 sta Rh4
 lda Rh2
 adc #0
 sta Rh2
Check:jsr RdTxLoadedCell
 bcs Solid
 inc Rh6
 lda Rh6
 cmp #3
 bne Loop
 jmp Done
Solid:
 ; Same native exclusions: water, active bounce, noninteractive hurt, bump
 ; solids/vines. Real PlayerHeadCollision handles bricks/questions/invisibles.
 lda AreaType
 jeq Done
 lda BlockBounceTimer
 jne Done
 lda RdHurtClock
 jne Done
 ldy Rh7
 lda MTileAttribute,y
 and #MTILE_BUMP|MTILE_CLIMB
 jne Done
 jsr RdTxNativeCell
 jsr PlayerHeadCollision
Done:
 RdTxRestoreNative
 sec
 jmp RdHsRestoreC
No:clc
 rts
.endproc

; Call ONCE after real ControlStep+Export, before native scrolling/enemies.
; Collect at most one genuine native coin per Main, then test the real SMB
; down-pipe pair. No source Door/Elevator/Metroid room RAM is synthesized.
.proc RdTxAfterMovement
 jsr RdHostEnabled
 jcc No
 RdHsSave
 RdTxSaveNative
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda Player_Y_HighPos
 cmp #1
 jne Done
 lda #0
 sta Rh6
CoinLoop:
 lda RdRoomHi
 sta Rh2
 lda RdX
 sta Rh4
 lda RdY
 sta Rh3
 lda Rh6
 cmp #3
 bcc Upper
 cmp #6
 bcc Middle
 lda Rh3
 clc
 adc RdRadiusY
 sta Rh3
 jmp Across
Upper:lda Rh3
 sec
 sbc RdRadiusY
 sta Rh3
Middle:
Across:lda Rh6
 ; repeated subtraction keeps the exact nine probes without new state/RAM
 cmp #6
 bcc :+
 sec
 sbc #6
:cmp #3
 bcc :+
 sec
 sbc #3
:cmp #1
 beq CoinCheck
 bcs CoinRight
 lda Rh4
 sec
 sbc RdRadiusX
 sta Rh4
 lda Rh2
 sbc #0
 sta Rh2
 jmp CoinCheck
CoinRight:lda Rh4
 clc
 adc RdRadiusX
 sta Rh4
 lda Rh2
 adc #0
 sta Rh2
CoinCheck:
 lda Rh3
 cmp #32
 bcc Next
 cmp #240
 bcs Next
 lda #1
 sta Rh5
 jsr RdTxLoadedCell       ; validates current loaded page, retains raw tile
 lda Rh7
 cmp #$c2
 beq Coin
 cmp #$c3
 beq Coin
Next:inc Rh6
 lda Rh6
 cmp #9
 jne CoinLoop
 jmp Pipe
Coin:jsr RdTxNativeCell
 jsr HandleCoinMetatile   ; real buffer erase/VRAM/score/coin-life transaction
Pipe:
 lda RdHeld
 and #4
 jeq Done
 ; Actual current source foot ordinate, not Mario's standing size heuristic.
 lda RdY
 clc
 adc RdRadiusY
 clc
 adc #1
 sta Rh3
 cmp #32
 jcc Done
 cmp #240
 jcs Done
 lda RdX
 sec
 sbc RdRadiusX
 sta Rh4
 lda RdRoomHi
 sbc #0
 sta Rh2
 jsr RdTxLoadedCell
 lda Rh7
 cmp #$10
 jne Done
 lda #$10
 sta R1
 lda RdX
 clc
 adc RdRadiusX
 sta Rh4
 lda RdRoomHi
 adc #0
 sta Rh2
 jsr RdTxLoadedCell
 lda Rh7
 cmp #$11
 jne Done
 sta R0
 jsr HandlePipeEntry      ; actual Down gate, engine3/timer/warp native owner
Done:RdTxRestoreNative
 sec
 jmp RdHsRestoreC
No:clc
 rts
.endproc

; Replaces ONLY existing Z2PositionOnPlatform farcall in a private object.s.
; Actual callers provide A=resolved first/second/balance platform ordinate,
; X=real actor slot; HPlat already committed the actual signed X carry.
; Native actor collision pass remains the attachment authority.
.proc RdTxPositionPlatform
 php
 pha
 jsr RdHostEnabled
 bcs Own
 pla
 plp
 RdTxFar Z2PositionOnPlatform,71
 rts
Own:
 lda GameEngineSubroutine
 cmp #$0b
 beq Skip
 lda Enemy_Y_HighPos,x
 cmp #1
 bne Skip
 pla
 sec
 sbc #32
 sta Player_Y_Position
 lda #1
 sbc #0
 sta Player_Y_HighPos
 lda Player_Y_Position
 clc
 adc #16
 sta RdY
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
 plp
 rts
Skip:pla
 plp
 rts
.endproc
RdTxEnd:
.assert RdTxEnd <= $c000,error,"Approved A95 host end"
.popseg
