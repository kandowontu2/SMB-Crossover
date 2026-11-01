; Original Karnov health/death for genuine authenticated services5/6/7/8.
; Include after the existing terrain/render kernel in RAM3/C2. No host grant
; or candidate patch is made by this component. All foregroundR0..R7 remain
; unchanged; only KrSourceFrame temporarily owns/restores foregroundR0/R1.
.import MmDeathFlag,MmDeathAge,MmDeathPit,TimerControl,EventMusicQueue
.import StarInvincibleTimer,VRAM_Buffer1,VRAM_Buffer1_Offset,MTileAttribute
.export KrHealthInjury,KrHealthStatus,KrHealthDeathStart,KrHealthDeathUpdate
.export KrHealthOriginal_CB69,KrHealthOriginal_CA31,KrHealthPaletteQueue
.export KrHealthSupport,KrHealthEnd
; Two fully assigned transient bytes after the existing C834..C838 shot packet.
KrHealthRow=$c839
KrHealthDelta=$c83a
.macro KrHealthSave
 php
 pha
 txa
 pha
 tya
 pha
.endmacro
.macro KrHealthRestore
 pla
 tay
 pla
 tax
 pla
 plp
.endmacro

; Source CB69..CB8A: bit80 means the first contact hit was already spent;
; bit40 is invulnerability, with source69's128-update countdown. First hit
; queues the original blue palette command and returnsA0. Depleted returns
; the original nonzero68. Native adapter restores its complete caller ABI.
KrHealthOriginal_CB69:
 lda KrState+$68
 bmi KrHealthOriginalHurtReturn
 lda #$10
 sta KrState+$34
 lda #$1c
 sta KrState+$35
 lda #$0f
 sta KrState+$36
 lda #1
 jsr KrHealthPaletteQueue
 lda #$c0
 ora KrState+$68
 sta KrState+$68
 lda #$80
 sta KrState+$69
 lda #0
KrHealthOriginalHurtReturn:
 rts
; Actual original C2C7..C2DE ring enqueue, relocated without borrowing ZP.
KrHealthPaletteQueue:
 ldy KrState+$70f
 cpy #8
 bcs KrHealthPaletteReturn
 ldx KrState+$710
 sta KrState+$712,x
 inx
 txa
 and #7
 sta KrState+$710
 inc KrState+$70f
KrHealthPaletteReturn:rts

; Source CA31..CA4F normal-contact fatal setup. $5D bit0 is the source
; script/lock exclusion. Native forced-death start enters after that exclusion
; because host pits/timer expiration must terminate a life independently.
KrHealthOriginal_CA31:
 lda KrState+$5d
 lsr
 bcs KrHealthFatalReturn
KrHealthForcedFatal:
 lda KrState+$62
 and #$80
 ora #$19
 sta KrState+$62
 lda KrState+$64
 sec
 sbc #$20
 sta KrState+$64
 lda #2
 jsr KrSoundCallback
 lda #$1f
 jsr KrSoundCallback
KrHealthFatalReturn:rts

; Service6: source contact survivability, not native PlayerStatus. Positive
; while hurt/dead routes host injury to service5's consumed no-op; otherwise
; source68bit80 selects the real fatal host boundary. XY/R0..R7 unchanged;
; A/N/Z report0or1, incomingC/V/D/I preserved exactly.
KrHealthStatus:
 php
 lda KrState+$62
 and #31
 cmp #25
 bcs KrHealthStatusYes
 lda KrState+$68
 and #$40
 bne KrHealthStatusYes
 lda KrState+$68
 bmi KrHealthStatusNo
KrHealthStatusYes:lda #1
 bne KrHealthStatusReturn
KrHealthStatusNo:lda #0
KrHealthStatusReturn:
 plp
 ora #0
 rts

; Service5: complete callerAXYP exceptC1=handled/C0=context unavailable.
; Does not set generic GuestHurtTicks, shrink the player, reset source motion,
; consume source clock, touch a foreign inventory or borrowNMI scratch0..2.
KrHealthInjury:
 KrHealthSave
 lda KrReady
 cmp #$a7
 bne KrHealthNo
 lda KrState+$62
 and #31
 cmp #25
 bcs KrHealthYes
 lda KrState+$68
 and #$40
 bne KrHealthYes
 jsr KrHealthOriginal_CB69
 beq KrHealthPublishBlue
 jsr KrHealthOriginal_CA31
 lda KrState+$62
 and #31
 cmp #25
 bne KrHealthYes
 jsr KrHealthNativeDeath
 jmp KrHealthYes
KrHealthPublishBlue:
 ; Three opaque sprite colors only; never overwrite3F00/10 sky/backdrop.
 ldx VRAM_Buffer1_Offset
 cpx #72
 bcs KrHealthYes
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$11
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 lda #$10
 sta VRAM_Buffer1+3,x
 lda #$1c
 sta VRAM_Buffer1+4,x
 lda #$0f
 sta VRAM_Buffer1+5,x
 lda #0
 sta VRAM_Buffer1+6,x
 txa
 clc
 adc #6
 sta VRAM_Buffer1_Offset
KrHealthYes:
 KrHealthRestore
 sec
 rts
KrHealthNo:
 KrHealthRestore
 clc
 rts

; Service7: genuine forced fatal selector25, not a Mario velocity/reskin.
; The native kill caller has already setMmDeathFlag; do not use it to reject.
KrHealthDeathStart:
 KrHealthSave
 lda KrReady
 cmp #$a7
 bne KrHealthNo
 lda KrState+$62
 and #31
 cmp #25
 bcs KrHealthYes
 lda Player_Y_Position
 clc
 adc #32
 sta KrState+$64
 jsr KrHealthForcedFatal
 jsr KrHealthNativeDeath
 jmp KrHealthYes
KrHealthNativeDeath:
 lda Player_Y_Position
 sec
 sbc #32
 sta Player_Y_Position
 bcs :+
 dec Player_Y_HighPos
:
 lda #1
 sta MmDeathFlag
 sta EventMusicQueue
 lda #0
 sta MmDeathAge
 sta StarInvincibleTimer
 sta Player_X_Speed
 sta Player_X_Scroll
 lda #$ff
 sta TimerControl
 lda #$0b
 sta GameEngineSubroutine
 lda #2
 sta Player_State
 rts

; Service8: original death selectors25(fall),26(64-update rest),28(pit),29
; and original69 timer prefix run once per accepted host FrameCounter epoch.
; Existing Main movement's shared epoch prevents a second source tick on a
; same-frame fatal hit. Source callbacks stay original pending/audio requests.
KrHealthDeathUpdate:
 KrHealthSave
 lda KrReady
 cmp #$a7
 jne KrHealthNo
 lda GameEngineSubroutine
 cmp #$0b
 jne KrHealthNo
 lda GamePauseStatus
 and #1
 jne KrHealthYes
 lda KrHaveEpoch
 beq KrHealthDeathTick
 lda FrameCounter
 cmp KrLastEpoch
 jeq KrHealthYes
KrHealthDeathTick:
 lda FrameCounter
 sta KrLastEpoch
 lda #1
 sta KrHaveEpoch
 inc MmDeathAge
 lda MmDeathPit
 beq KrHealthDeathFloor
 ; Host pages below the viewport have already crossed the sourceD0 cutoff.
 lda #$1c
 sta KrState+$62
 lda #$d0
 sta KrState+$64
KrHealthDeathFloor:
 jsr KrHealthSupport
 lda KrState+$64
 sta KrHealthDelta
 jsr KrSourceFrame
 inc KrState+$e8
 lda KrState+$64
 sec
 sbc KrHealthDelta
 sta KrHealthDelta
 sta Player_Y_Speed
 clc
 adc Player_Y_Position
 sta Player_Y_Position
 lda #0
 ldx KrHealthDelta
 bpl :+
 lda #$ff
:adc Player_Y_HighPos
 sta Player_Y_HighPos
 lda KrState+$5e
 cmp #10
 bne KrHealthDeathDone
 lda #6
 sta GameEngineSubroutine
 lda #0
 sta TimerControl
KrHealthDeathDone:
 jmp KrHealthYes

; Only this dead actor's support query. Uses real host block buffers and
; fixed MTileAttribute, requiringSOLID and excludingCLIMB; no coin/axe/pipe
; effects execute. AXY private to the saved adapter; R0..R7 never touched.
KrHealthSupport:
 lda #0
 sta KrState+$8b
 lda Player_Y_HighPos
 cmp #1
 bne KrHealthSupportDone
 lda Player_Y_Position
 clc
 adc #33                    ; F98A increments sourcefoot before reading8B
 bcs KrHealthSupportDone
 cmp #32
 bcc KrHealthSupportDone
 cmp #240
 bcs KrHealthSupportDone
 and #$f0
 sec
 sbc #32
 sta KrHealthRow
 ldy #1
KrHealthSupportLoop:
 lda Player_X_Position
 clc
 adc KrHealthFootX,y
 tax
 lda Player_PageLoc
 adc #0
 and #1
 bne KrHealthSupportPage2
 txa
 lsr
 lsr
 lsr
 lsr
 ora KrHealthRow
 tax
 lda Block_Buffer_1,x
 jmp KrHealthSupportTile
KrHealthSupportPage2:
 txa
 lsr
 lsr
 lsr
 lsr
 ora KrHealthRow
 tax
 lda Block_Buffer_2,x
KrHealthSupportTile:
 cmp #$5f                    ; native ChkInvisibleMTiles foot exclusions
 beq KrHealthSupportNext
 cmp #$60
 beq KrHealthSupportNext
 tax
 lda MTileAttribute,x
 and #3
 cmp #1
 beq KrHealthSupported
KrHealthSupportNext:
 dey
 bpl KrHealthSupportLoop
KrHealthSupportDone:rts
KrHealthSupported:
 lda #2
 sta KrState+$8b
 rts
KrHealthFootX:.byte 2,13
KrHealthEnd:
