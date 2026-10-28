; Separate Sunny profile, supplied Super Sunny World RC1 artwork.
; Mario-family gameplay is the requested port foundation, not Sunny's original
; executable. ROOT must admit ID23 before every legacy player/table route.
.include "sunny_state.inc"
.pushseg
.segment "SUNNY_CORE"
SunnyCoreBegin:

.proc SunnyIsActive
 lda SelectedCharacter
 cmp #CHARACTER_SUNNY
 beq Yes
 clc
 rts
Yes:sec
 rts
.endproc

; Global constructor touches ONLY Sunny's own persistent8B. It is safe while
; another selected profile owns the active ExRAM overlay.
.proc SunnyGlobalInit
 lda #0
 ldx #7
Loop:sta SunnyForm,x
 dex
 bpl Loop
 rts
.endproc

; Loader-owned scene key. AreaPointer may already contain a future bonus-pipe
; destination while the present scene remains loaded.
.proc SunnySceneKey
 lda AreaType
 asl
 asl
 asl
 asl
 asl
 ora AreaAddrsLOffset
 rts
.endproc

.proc SunnyEnsure
 jsr SunnyIsActive
 bcc Done
 lda SunnyReady
 cmp #$53
 bne NewLife
 lda NumberofLives
 sec
 sbc SunnyLife
 bmi NewLife                 ; real INC, including FF->00, preserves form
 lda NumberofLives
 sta SunnyLife
 jsr SunnySceneKey
 cmp SunnyArea
 bne Area
 lda WorldNumber
 cmp SunnyWorld
 beq Done
 bne Area
NewLife:
 lda #0
 sta SunnyForm
 sta SunnyFuture
 lda #$53
 sta SunnyReady
Area:
 jsr SunnyAreaReset
Done:rts
.endproc

; Fresh selection/area adapter: initialize a never-used identity first, then
; restore its own persistent form into the native Mario fields.
.proc SunnyReset
 jsr SunnyEnsure
 jmp SunnyAreaReset
.endproc

; Explicit owner guard precedes all writes to the shared active overlay.
.proc SunnyAreaReset
 jsr SunnyIsActive
 bcc Done
 lda #0
 ldx #$7f
Loop:sta $5c00,x
 dex
 bpl Loop
 lda NumberofLives
 sta SunnyLife
 jsr SunnySceneKey
 sta SunnyArea
 lda WorldNumber
 sta SunnyWorld
 lda #$ff
 sta SunnyPalette
 sta SunnyLastForm
 lda SunnyForm
 cmp #3
 bcc Valid
 lda #0
 sta SunnyForm
Valid:
 sta PlayerStatus
 cmp #1
 lda #0
 rol
 eor #1
 sta PlayerSize
Done:rts
.endproc

; Call only at a completed native form boundary. A changing growth/shrink
; display is not a new earned persistent form.
.proc SunnyCaptureForm
 jsr SunnyIsActive
 bcc Done
 lda GuestPowerupActive
 ora PlayerChangeSizeFlag
 bne Done
 lda PlayerStatus
 cmp #3
 bcs Done
 sta SunnyForm
Done:rts
.endproc

; A=actual visible form, clamped0..2. This never indexes legacy ID arrays.
.proc SunnyVisualForm
 lda GuestPowerupActive
 beq Native
 lda GuestPowerupDisplay
 jmp Clamp
Native:lda PlayerStatus
Clamp:cmp #3
 bcc Done
 lda #0
Done:rts
.endproc

; Genuine ordinary SMB movement leaf. ROOT may instead select current
; source-Mario motion after closing its owner0-specific shared gates. Neither
; this wrapper nor any other Sunny leaf ever rewrites SelectedCharacter.
.proc SunnyNativeMovement
 php
 pha
 phx
 phy
 jsr SunnyIsActive
 bcc Inactive
 jsr SunnyEnsure
 jsr SunnyCaptureForm
 inc SunnyClock
 lda SunnyClock
 cmp #120
 bcc Ready
 lda #0
 sta SunnyClock
Ready:
 ply
 plx
 pla
 plp
 farcall CrossoverVanillaMovement,jmp
Inactive:
 ply
 plx
 pla
 plp
 rts
.endproc

; Tail replacement for the native fireball/bubble branch in OBJECT, not a
; regular NrWeapons child (that caller would run the bubble tail twice).
; Uses real native two-shot allocation/physics/collision/SFX unchanged.
.proc SunnyNativeWeaponTail
 lda PlayerStatus
 cmp #2
 bcc Bubbles
 farcall ProcFireball_Bubble::CheckAttackButton,jmp
Bubbles:
 farcall ProcFireball_Bubble::ProcAirBubbles,jmp
.endproc
.proc SunnyWeapons
 ; No banked custom weapon subsystem; OBJECT owns the genuine native tail.
 rts
.endproc

; The existing source-Mario freeze preserves the requested inherited forms
; without consulting a twelve-owner inventory. Caller owns physical actor
; erase/1000points/SFX, then invokes this exactly once. Stars/1Ups return C0.
.proc SunnyBeginPickup
 lda PowerUpType,x
 cmp #2
 bcs Native
 farcall MarioSourceBeginPowerup
 sec
 rts
Native:clc
 rts
.endproc
.proc SunnyInjuryStart
 farcall MarioSourceInjuryStart,jmp
.endproc
.proc SunnyPowerupUpdate
 farcall MarioSourcePowerupUpdate
 jmp SunnyCaptureForm
.endproc
.proc SunnyNativeDeath
 farcall NativePlayerDeath,jmp
.endproc
.proc SunnyHead
 jmp BlockBufferColli_Head
.endproc
.proc SunnySide
 jmp BlockBufferColli_Side
.endproc
.proc SunnyUi
 lda InvHudActive
 beq Done
 lda #0
 sta InvHudActive
 inc ReloadCHRBank
Done:rts
.endproc
.proc SunnyFullPower
 jsr SunnyEnsure
 lda #2
 sta SunnyForm
 sta PlayerStatus
 lda #0
 sta PlayerSize
 lda #$ff
 sta SunnyPalette
 rts
.endproc
.proc SunnyStatusName
 cmp #0
 bne Done
 phy
 ldy #6
Loop:lda Name,y
 sta VRAM_Buffer1+11,y
 dey
 bpl Loop
 ply
 lda #0
Done:rts
Name:.byte "SUNNY  "
.endproc

; Native-Mario compatible collision/stomp admission. A=raw ID on entry for
; Adder/Box. Carry clear requests the actual PlayerSize/crouch terrain rows.
.proc SunnyAdder
 clc
 rts
.endproc
.proc SunnyBox
 rts
.endproc
.proc SunnyBody
 pha
 lda AreaType
 sta GuestBodyStompAllowed
 lda #0
 sta GuestBodyNoStomp
 pla
 clc
 rts
.endproc
.proc SunnyInjuryStatus
 lda PlayerStatus
 tax
 rts
.endproc
.proc SunnyVisible
 lda GuestHurtKind
 beq Native
 lda GuestHurtVisible
 cmp #1
 rts
Native:
 lda InjuryTimer
 beq Yes
 lda FrameCounter
 lsr
 bcs No
Yes:sec
 rts
No:clc
 rts
.endproc
.proc SunnyDeathStart
 jsr SunnyIsActive
 bcc Done
 lda #0
 sta SunnyForm
 lda #$ff
 sta SunnyPalette
Done:rts
.endproc

; Small native Sunny pose. ROOT calls this for a front-end portrait, separate
; from the active form renderer. It does not invent a different face asset.
.proc SunnyPortrait
 jsr SunnyEnsure
 ldx #SUNNY_POSE_PORTRAIT
 jsr SunnySetPose
 jsr SunnyDraw
 jmp SunnyForcePalette
.endproc

.proc SunnyGraphics
 jsr SunnyEnsure
 lda Player_Rel_XPos
 sta Player_Pos_ForScroll
 lda MmDeathFlag
 beq Live
 lda MmDeathPit
 bne Hide
 ldx #SUNNY_POSE_DEATH
 bne Set
Live:
 lda CrouchingFlag
 beq Climb
 ldx #SUNNY_POSE_CROUCH
 bne Set
Climb:
 lda Player_State
 cmp #3
 bne Water
 lda PlayerAnimCtrl
 and #1
 clc
 adc #SUNNY_POSE_CLIMB0
 tax
 bne Set
Water:
 lda SwimmingFlag
 beq Air
 lda Player_State
 beq Ground
 lda PlayerAnimCtrl
 cmp #3
 bcc Swim
 lda #0
Swim:clc
 adc #SUNNY_POSE_SWIM0
 tax
 bne Set
Air:
 lda Player_State
 beq Ground
 ldx #SUNNY_POSE_JUMP
 lda Player_Y_Speed
 bmi Set
 inx
 bne Set
Ground:
 ldx #SUNNY_POSE_IDLE
 lda Player_X_Speed
 beq Set
 lda Player_MovingDir
 cmp PlayerFacingDir
 beq Walk
 ldx #SUNNY_POSE_SKID
 bne Set
Walk:
 lda PlayerAnimCtrl
 cmp #3
 bcc WalkFrame
 lda #0
WalkFrame:clc
 adc #SUNNY_POSE_WALK0
 tax
Set:
 lda PlayerStatus
 cmp #2
 bne Pose
 lda FireballThrowingTimer
 beq Pose
 ldx #SUNNY_POSE_THROW
Pose:jmp SunnySetPose
Hide:lda #0
 sta ObjectMetasprite
 rts
.endproc

; X=semantic0..16. Preserve incoming X/Y; publish actual C94 record pointer.
; Explicit SunnyFrame/SunnyPose are owned active-state outputs. ABI returns
; A=METASPRITE_SAMUS_BODY, C from facing CMP2, V/D/I from palette tail.
.proc SunnySetPose
 phx
 phy
 cpx #SUNNY_POSE_COUNT
 bcc Valid
 ldx #SUNNY_POSE_IDLE
Valid:stx SunnyPose
 jsr SunnyQueuePalette
 php
 BankPRGC #94
 ldx SunnyPose
 cpx #SUNNY_POSE_PORTRAIT
 beq Small
 jsr SunnyVisualForm
 beq Small
 lda SunnySemanticBig,x
 jmp Frame
Small:
 lda SunnySemanticSmall,x
Frame:
 jsr SunnySelectAnimation
 sta SunnyFrame
 tax
 lda PlayerFacingDir
 cmp #2
 beq Left
 lda SunnyRLo,x
 sta SmPosePtr
 lda SunnyRHi,x
 jmp Pointer
Left:
 lda SunnyLLo,x
 sta SmPosePtr
 lda SunnyLHi,x
Pointer:sta SmPosePtr+1
 lda SunnyChrLow,x
 sta SmChrBank
 lda Player_SprAttrib
 and #$fc
 sta Player_SprAttrib
 plp
 ply
 plx
 lda PlayerFacingDir
 cmp #2
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 rts
.endproc

; Animate the genuine source idle20-update six-step sequence and the native
; two-frame crouch (small15 / large30). Other semantic categories retain the
; actual Mario-family animation selection. X is private and restored by the
; enclosing SetPose; no input, movement or attack clock is changed.
.proc SunnySelectAnimation
 sta SunnyTemp
 cpx #SUNNY_POSE_IDLE
 bne Crouch
 lda SunnyClock
 ldx #0
IdleLoop:
 cmp #20
 bcc IdleSlot
 sbc #20
 inx
 bne IdleLoop
IdleSlot:
 lda IdleSequence,x
 clc
 adc SunnyTemp
 rts
Crouch:
 cpx #SUNNY_POSE_CROUCH
 bne Original
 lda SunnyTemp
 cmp #33
 lda #15
 bcc Step
 lda #30
Step:sta SunnyAnimationStep
 lda SunnyClock
 ldx #0
CrouchLoop:
 cmp SunnyAnimationStep
 bcc CrouchSlot
 sbc SunnyAnimationStep
 inx
 bne CrouchLoop
CrouchSlot:
 txa
 and #1
 clc
 adc SunnyTemp
 rts
Original:
 lda SunnyTemp
 rts
IdleSequence:.byte 0,0,1,2,2,1
.endproc

.proc SunnyGraphicsBank
 BankPRGC #94
 rts
.endproc
.proc SunnyDraw
 BankPRGC #94
 lda SmChrBank
 ldx #>SUNNY_FIRST_CHR
 ldy #0
 farcall X5SetPhysicalChr,jmp
.endproc
.proc SunnyForcePalette
 lda #$ff
 sta SunnyPalette
 jmp SunnyQueuePalette
.endproc
.proc SunnyColors
 jmp SunnyForcePalette
.endproc
.proc SunnyQueuePalette
 lda StarInvincibleTimer
 ora GuestPowerupActive
 beq Normal
 lda #$ff
 sta SunnyPalette
 rts
Normal:
 jsr SunnyVisualForm
 cmp #2
 lda #0
 rol
 cmp SunnyPalette
 beq Done
 pha
 ldx VRAM_Buffer1_Offset
 cpx #78
 bcs Declined
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$11
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 lda #4
 sta VRAM_Buffer1+3,x
 lda #$26
 ldy PlayerStatus
 cpy #2
 bcc Color
 lda #$2a
Color:sta VRAM_Buffer1+4,x
 lda #$36
 sta VRAM_Buffer1+5,x
 txa
 clc
 adc #6
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 pla
 sta SunnyPalette
 rts
Declined:pla
Done:rts
.endproc
SunnyCoreEnd:
.assert SunnyCoreEnd-SunnyCoreBegin<=$0e00,error,"Reserved Sunny A81 B200..BFFF overflow"
.popseg
.include "sunny_art.inc"
.pushseg
.segment "SUNNY_CHR"
.incbin "chr/characters/sunny.chr"
.popseg
