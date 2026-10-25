; Original Duck USA SHA1271dce8…: bank7 CB8B..D31A/F4FD..F611,
; bank5 renderer80F2..81F7. Source uses upward-positiveQ8.8 and post-motion
; gravity. This adapter phase-translates into the installed pre-gravityQ8.16.
.pushseg
.segment "DARKWING_CORE"
.macro DwGate legacy
.local Active
  php
  pha
  jsr DwActive
  bne Active
  pla
  plp
  farcall legacy,jmp
Active:
  pla
  plp
.endmacro
.proc DwActive
  lda SelectedCharacter
  cmp #CHARACTER_SCROOGE
  bne No
  lda DarkwingVariant
  rts
No:
  lda #0
  rts
.endproc
.proc DwGlobalInit
  farcall ProtoGlobalInit
  lda #0
  sta DarkwingVariant
  ldx #8
Clear:
  sta DwHealth,x
  dex
  bpl Clear
  rts
.endproc
.proc DwScroogeMovement
  lda DarkwingVariant
  bne Duck
  farcall ScroogeMovement,jmp
Duck:
  lda SavedJoypadBits
  eor DwPrevious
  and SavedJoypadBits
  sta ScFresh
  lda SavedJoypadBits
  sta DwPrevious
  lda MmYFraction+1
  sta ScPogo                   ; exclusive pre-physics fractional phase
  lda Player_State
  sta ScEnemy                  ; previous actual support state
  lda DwHealth
  bne Alive
  lda #4
  sta DwHealth
Alive:
  lda #0
  sta GuestHurtKind
  sta ScAttack
  lda #1
  sta GuestHurtVisible
  lda RgBillBurst
  beq Done
  dec RgBillBurst
  lda #1
  sta InjuryTimer
  lda FrameCounter
  and #4
  beq Done
  lda #0
  sta GuestHurtVisible
Done:
  jmp DwRecovery
.endproc
.proc DwScroogePhysics
  lda DarkwingVariant
  bne Duck
  farcall ScroogePhysics,jmp
Duck:
  lda #0
  sta XgRise
  sta MmFrictionYActive
  sta XgGravity
  sta RgFallCap
  sta RgFallCap+1
  lda #$40
  ldx MmUnderwater
  beq :+
  lsr                           ; explicit SMB-water adaptation
:
  sta XgGravity+1
  lda #8
  sta RgFallCap+2
  jsr DwHangUpdate
  jcs Done
  lda ScEnemy
  bne Air
  lda ScPogo
  clc
  adc #$55                     ; original grounded fall/probe fractional step
  sta MmYFraction+1
  lda #0
  sta MmYFraction
  lda ScFresh
  and #A_Button
  beq Speed
  lda #0
  sta MmVY
  lda #$db                     ; -($04e5+$0040), pre-gravity phase
  sta MmVY+1
  lda #$fa
  sta MmVY+2
  lda #1
  sta Player_State
  jmp Speed
Air:
  lda A_B_Buttons
  and #A_Button
  bne Speed
  lda MmVY+2
  bpl Speed
  cmp #$fb                     ; original release cut only below5 upward
  bcc Speed
  lda #0
  sta MmVY
  lda #$15                     ; +55/256 after the normal40/256 pull
  sta MmVY+1
  lda #0
  sta MmVY+2
Speed:
  lda RgBillBurstDelay
  beq Controlled
  dec RgBillBurstDelay
  lda #0
  sta MmVX
  sta MmVX+2
  lda #$80                     ; source hurt backward half-pixel motion
  sta MmVX+1
  lda PlayerFacingDir
  cmp #1
  jne Done
  farcall MegaManMovement::NegateX
  rts
Controlled:
  lda Player_State
  bne Moving
  lda SavedJoypadBits
  and #Up_Dir|Down_Dir
  ora RgShootPose
  bne Stop
Moving:
  lda SavedJoypadBits
  and #3
  cmp #1
  beq Direction
  cmp #2
  bne Stop
Direction:
  sta PlayerFacingDir
  lda XgWalkDirection
  bne Cap
  lda #4
  sta XgWalkTick
Cap:
  lda #1
  sta XgWalkDirection
  lda #0
  sta MmVX
  lda #$80
  sta MmVX+1
  lda #1
  sta MmVX+2
  lda MmUnderwater
  beq Step
  lda #$c0
  sta MmVX+1
  lda #0
  sta MmVX+2
Step:
  lda Player_State
  bne Signed
  lda XgWalkTick
  beq Signed
  dec XgWalkTick
  lda #$48                     ; first four ground-walk updates
  sta MmVX+1
  lda #0
  sta MmVX+2
Signed:
  lda PlayerFacingDir
  cmp #2
  bne Done
  farcall MegaManMovement::NegateX
Done:
  rts
Stop:
  lda #0
  sta XgWalkDirection
  sta MmVX
  sta MmVX+1
  sta MmVX+2
  rts
.endproc
.proc DwExpandedGraphicsBank
  jsr DwActive
  beq Legacy
  BankPRGC #.bank(DarkwingArtBegin)
  rts
Legacy:
  lda SelectedCharacter
  sec
  sbc #CHARACTER_PIT
  tax
  lda Banks,x
  ora #MMC5_PRG_ROM
  BankPRGC a
  rts
Banks:.byte .bank(XgPIT0_STANDRight),.bank(XgRYGAR0_STANDRight),.bank(XgLUIGI0_STANDRight),.bank(XgBASS0_STANDRight),.bank(XgRYU0_STANDRight),.bank(XgSOPHIA0_STANDRight),.bank(XgSCROOGE_STANDRight)
.endproc
.proc DwScroogeGraphics
  lda DarkwingVariant
  bne Duck
  farcall ScroogeGraphics,jmp
Duck:
  lda #1
  ldx GameEngineSubroutine
  cpx #$0b
  bne Alive
  lda #9
  jmp Pose
Alive:
  ldx RgBillBurstDelay
  beq Normal
  lda #9
  bne Pose
Normal:
  ldx DwHang
  bpl NotHang
  lda #$0b
  ldx RgShootPose
  beq Pose
  lda #$0c
  bne Pose
NotHang:
  ldx Player_State
  beq Ground
  lda #$11
  ldx MmVY+2
  bmi AirShot
  lda #$12
AirShot:
  ldx RgShootPose
  beq AirCape
  clc
  adc #$fd
AirCape:
  ldx SavedJoypadBits
  txa
  and #Up_Dir
  beq AirNoCape
  lda #$0d
  bne Pose
AirNoCape:
  lda #$11
  ldx MmVY+2
  bmi :+
  lda #$12
:
  ldx RgShootPose
  beq Pose
  clc
  adc #$fd
  bne Pose
Ground:
  ldx RgCrouch
  beq Cape
  lda #6
  ldx RgShootPose
  beq Pose
  lda #7
  bne Pose
Cape:
  ldx SavedJoypadBits
  txa
  and #Up_Dir
  beq Walk
  lda #4
  bne Pose
Walk:
  lda #1
  ldx RgShootPose
  beq Walking
  lda #5
  bne Pose
Walking:
  ldx Player_X_Speed
  beq Pose
  lda #3
Pose:
  jsr DwAnimate
  rts
  .byte $ea,$ea ; Palette is initialized on entry, not queued every draw.
.endproc
.proc DwAnimate
  pha
  BankPRGC #.bank(DarkwingArtBegin)
  pla
  cmp DwAnim
  beq Tick
  sta DwAnim
  lda #0
  sta DwPhase
  sta DwAnimTick
Tick:
  ldx DwAnim
  lda DwAnimTick
  inc DwAnimTick
  cmp DwAnimationDelay,x
  bcc Select
  lda #0
  sta DwAnimTick
  lda DwPhase
  cmp DwAnimationLast,x
  bcc Advance
  lda #$ff
Advance:
  clc
  adc #1
  sta DwPhase
Select:
  lda DwAnimationBase,x
  clc
  adc DwPhase
  tax
  lda DwPoseBankLo,x
  sta SmChrBank
  lda PlayerFacingDir
  cmp #2
  beq Left
  lda DwPoseRLo,x
  sta SmPosePtr
  lda DwPoseRHi,x
  jmp Ready
Left:
  lda DwPoseLLo,x
  sta SmPosePtr
  lda DwPoseLHi,x
Ready:
  sta SmPosePtr+1
  lda Player_X_Position
  sec
  sbc ScreenLeft_X_Pos
  sta Player_Pos_ForScroll     ; same native camera cache as ExpandedPose
  lda #METASPRITE_SAMUS_BODY
  sta ObjectMetasprite
  rts
.endproc
.proc DwQueuePalette
  ldx VRAM_Buffer1_Offset
  cpx #$4e ;6B palette plus terminator fits84B queue
  bcs Done
  ldy #0
Copy:
  lda Palette,y
  sta VRAM_Buffer1,x
  inx
  iny
  cpy #6
  bne Copy
  stx VRAM_Buffer1_Offset
  lda #0
  sta VRAM_Buffer1,x
Done:
  rts
Palette:.byte $3f,$11,3,$13,$30,$27
.endproc
.proc DwExpandedPortrait
  jsr DwActive
  bne Duck
  farcall ExpandedPortrait,jmp
Duck:
  lda #1
  jsr DwAnimate
  jsr DwPublishBody
  jmp DwQueuePalette
.endproc
.proc DwPublishBody
  lda X5ChrMode
  cmp #$81
  bne Publish
  lda CurrentCHRBank
  cmp SmChrBank
  beq Done
Publish:
  lda SmChrBank
  ldx #1
  ldy #0
  farcall X5SetPhysicalChr
Done:
  rts
.endproc
.proc DwInjuryStatus
  jsr DwActive
  beq Legacy
  lda DwHealth
  beq Dead
  dec DwHealth
  lda DwHealth
  beq Dead
  lda #1
Dead:
  tax
  rts
Legacy:
  ldx PlayerStatus
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bne Done
  lda CrossoverBehaviorVersion
  beq Done
  ldx #0
Done:
  txa
  rts
.endproc
.proc DwInjuryStart
  jsr DwActive
  bne Duck
  farcall GuestInjuryStart,jmp
Duck:
  lda #60
  sta RgBillBurst
  lda #15
  sta RgBillBurstDelay
  lda #0
  sta GuestHurtKind
  sta RgShootPose
  sta MmVY
  sta MmVY+2
  lda #$15
  sta MmVY+1
  lda #1
  sta InjuryTimer
  sta Player_State
  lda #Sfx_PipeDown_Injury
  sta Square1SoundQueue
  lda #0
  sec
  rts
.endproc
.proc DwPlayerVisible
  jsr DwActive
  beq Legacy
  lda GuestHurtVisible
  cmp #1
  rts
Legacy:
  lda GuestHurtKind
  beq Native
  lda GuestHurtVisible
  cmp #1
  rts
Native:
  lda InjuryTimer
  beq Show
  lda FrameCounter
  lsr
  bcs Hide
Show:
  sec
  rts
Hide:
  clc
  rts
.endproc
.proc DwScroogeContact
  lda DarkwingVariant
  bne Duck
  farcall ScroogePogoContact,jmp
Duck:
  ; Explicit SMB mapping of the source front-facing projectile guard. Cape
  ; does not protect against ordinary bodies, firebars, lava, Bowser or pits.
  lda SavedJoypadBits
  and #Up_Dir
  beq No
  lda Enemy_ID,x
  cmp #BulletBill_CannonVar
  beq Projectile
  cmp #BulletBill_FrenzyVar
  bne No
Projectile:
  lda Enemy_MovingDir,x
  cmp PlayerFacingDir
  beq No
  lda Enemy_X_Position,x
  sec
  sbc Player_X_Position
  sta R0
  lda Enemy_PageLoc,x
  sbc Player_PageLoc
  ldy PlayerFacingDir
  cpy #2
  beq Left
  cmp #0
  bne No
  lda R0
  cmp #8
  bcc No
  bcs Reflect
Left:
  cmp #$ff
  bne No
  lda R0
  cmp #$f9
  bcs No
Reflect:
  lda PlayerFacingDir
  sta Enemy_MovingDir,x
  lda #0
  sec
  sbc Enemy_X_Speed,x
  sta Enemy_X_Speed,x
  sec
  rts
No:
  clc
  rts
.endproc
.proc DwHangUpdate
  lda DwHang
  bmi Holding
  beq Find
  dec DwHang                   ; release delay prevents immediate re-grabbing
  clc
  rts
Holding:
  and #15
  tax
  stx RgSlot
  lda RgShotType,x
  cmp #6
  bne Lost
  jsr DwValidateArrow
  bcc Lost
  lda ScFresh
  and #A_Button
  beq Drop
  lda Enemy_State,y
  ora #$80                    ; original bar admits a jump from underneath
  sta Enemy_State,y            ; native collision gate, native carry unchanged
  lda #8
  sta DwHang
  lda #0
  sta ScEnemy
  clc
  rts
Drop:
  lda ScFresh
  and #Down_Dir
  jeq Freeze
Lost:
  lda #8
  sta DwHang
  lda #1
  sta ScEnemy
  lda #0
  sta MmVY
  sta MmVY+2
  lda #$15
  sta MmVY+1
  clc
  rts
Find:
  lda Player_State
  jeq No
  lda SavedJoypadBits
  and #Down_Dir
  bne No
  ldx #9
Loop:
  lda RgShotType,x
  cmp #6
  bne Next
  lda SsMode,x
  bne Next
  jsr DwValidateArrow
  bcc Next
  lda Player_X_Position
  clc
  adc #8
  sta R0
  lda Player_PageLoc
  adc #0
  sta R1
  lda R0
  sec
  sbc RgShotX,x
  sta R0
  lda R1
  sbc RgShotPage,x
  sta R1
  lda R0
  clc
  adc #15
  sta R0
  lda R1
  adc #0
  bne Next
  lda R0
  cmp #31
  bcs Next
  lda Player_Y_Position
  clc
  adc #20
  sec
  sbc RgShotY,x
  cmp #12
  bcc Next
  cmp #25
  bcs Next
  txa
  ora #$80
  sta DwHang
  jmp Freeze
Next:
  dex
  bpl Loop
No:
  clc
  rts
Freeze:
  lda SavedJoypadBits
  and #3
  beq :+
  sta PlayerFacingDir
:
  lda Enemy_Y_Position,y
  sec
  sbc #3                      ; native source center is17px below the bar
  sta Player_Y_Position
  lda #0
  sta MmVX
  sta MmVX+1
  sta MmVX+2
  sta MmVY
  sta MmVY+1
  sta MmVY+2
  sta MmYFraction
  sta MmYFraction+1
  sta XgGravity
  sta XgGravity+1
  sta Player_Y_Speed
  lda #1
  sta Player_State
  sec
  rts
.endproc
.proc DwStatusName
  pha
  jsr DwActive
  bne Duck
  pla
  farcall ProtoStatusName,jmp
Duck:
  pla
  cmp #0
  bne Done
  pha
  txa
  pha
  ldy #6
Copy:
  lda Name,y
  sta VRAM_Buffer1+11,y
  dey
  bpl Copy
  pla
  tax
  pla
Done:
  rts
Name:.byte "DWING  "
.endproc
.popseg
