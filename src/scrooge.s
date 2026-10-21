; Scrooge is a native DuckTales addition; he is not a Crossover 2.02 character.
.pushseg
.segment "SAMUS"
.proc ScroogeHeadProbe
  jsr BlockBufferColli_Head
  beq Done
  cmp #$c2                       ; Collectible coins do not stop a rising head.
  beq Done
  cmp #$c3
  beq Done
  pha
  phy
  ldy Player_Y_Speed
  bpl Restore
  ldy R3                         ; PHY is TYA/PHA on6502; recover the probe tile.
  lda MTileAttribute,y
  and #MTILE_SOLID | MTILE_CLIMB
  cmp #MTILE_SOLID
  bne Restore
  ; DuckTales $D4C8 separates the crossed probe to the tile's lower edge.
  ; Canonical head Y is PlayerY+8. Keeping that point below the ceiling
  ; prevents the following native side probe (Y+9) from ejecting the body.
  ; R2/R6/R7 still describe the original block for its bounce and power-up.
  lda Player_Y_Position
  clc
  adc #8
  and #$f0
  clc
  adc #8
  sta Player_Y_Position
  and #15
  sta R4                         ; Let SMB process this resolved rising hit.
  lda #0
  sta MmYFraction
  sta MmYFraction+1
  ; Preserve the original rising Player_Y_Speed until the head parser has
  ; activated the question/brick or stopped the jump on protected terrain.
Restore:
  ply
  pla
Done:
  rts
.endproc
.segment "SRAM"
ScPogo: .res 1
ScAttack: .res 1
ScFresh: .res 1
ScPrevious: .res 1
ScEnemy: .res 1
.segment "REMAINING_AUDIO"
ScroogeMusicIntro: .incbin "audio/expanded/scrooge-intro.bin"
ScroogeMusicLoop: .incbin "audio/expanded/scrooge-loop.bin"
.segment "SPECIAL_ROSTER"
.proc ScroogeMovement
  lda SavedJoypadBits
  eor ScPrevious
  and SavedJoypadBits
  sta ScFresh
  lda SavedJoypadBits
  sta ScPrevious
  lda Player_State
  beq :+
    lda ScFresh
    and #$7f                    ; Ordinary A launch is a grounded input edge.
    sta ScFresh
  :
  lda SavedJoypadBits
  and #Down_Dir | B_Button
  cmp #Down_Dir | B_Button
  bne Cancel
  lda Player_State
  bne Pogo
  lda ScPogo
  beq Done
  jsr Bounce
Pogo:
  lda ScPogo
  bne :+
    lda #0
    sta SmBombHits             ; Each newly engaged pogo is an independent hit.
    sta ScEnemy                ; A prior cane/pogo cannot protect a new contact.
  :
  lda #1
  sta ScPogo
  rts
Cancel:
  lda #0
  sta ScPogo
  sta ScEnemy
Done:
  rts
Bounce:
  lda #1
  sta Player_State
  lda #0
  sta SmBombHits               ; A rebound begins the next pogo strike.
  sta MmVY
  sta MmVY+1
  sta MmYFraction
  sta MmYFraction+1
  ; DuckTales writes +$05a8 upward, then subtracts $0033 gravity after moving.
  ; This engine applies gravity first, so launch at -($05a8+$0033).
  lda MmUnderwater
  bne :+
    lda #$25
    sta MmVY+1
  :
  lda #$fa
  sta MmVY+2
  sta Player_Y_Speed
  lda #Sfx_BigJump
  sta Square1SoundQueue
  rts
.endproc
.proc ScroogePhysics
  lda MmUnderwater
  bne Done                      ; Preserve the existing separate water motion.
  lda #0
  sta XgGravity
  lda #$33                      ; Native DuckTales gravity, 51/256 px/update².
  sta XgGravity+1
  lda ScPogo
  beq :+
    lda #0
    sta XgRise
    rts
  :
  lda ScFresh
  and #A_Button
  beq VariableJump
  lda Player_State
  cmp #1
  bne Done
  ; Normal native launch is $04bb upward before its post-motion gravity.
  ; Initialize the subtractive fractional phase for the native 58px rise.
  lda #0
  sta MmVY
  lda #$12
  sta MmVY+1
  lda #$fb
  sta MmVY+2
  sta Player_Y_Speed
  lda #$ff
  sta MmYFraction
  sta MmYFraction+1
  lda #1
  sta XgRise                    ; Only an ordinary launch is cut by releasing A.
  rts
VariableJump:
  lda XgRise
  beq Done
  lda MmVY+2
  bpl EndRise
  lda A_B_Buttons
  and #A_Button
  bne Done
  lda #0                        ; DuckTales cancels ascent on ordinary A release.
  sta MmVY
  sta MmVY+1
  sta MmVY+2
EndRise:
  lda #0
  sta XgRise
Done:
  rts
.endproc
.proc ScroogeWeapons
  lda SavedJoypadBits
  sta RgPreviousButtons        ; Shared movement must see real A input edges.
  lda TimerControl
  bne Done
  lda GameEngineSubroutine
  cmp #8
  bne Clear
  ldx #5
Flash:
  lda MmEnemyFlash,x
  beq :+
    dec MmEnemyFlash,x
  :
  dex
  bpl Flash
  lda ScAttack
  beq Input
  dec ScAttack
  cmp #9
  bcs Done
  cmp #3
  bcc Done
  jsr Cane
  jmp Done
Input:
  lda ScPogo
  beq Swing
  lda MmVY+2
  bmi Done
  ora MmVY+1
  ora MmVY
  beq Done                    ; Native vertical contact requires actual descent.
  jsr PogoHit
  jmp Done
Swing:
  lda ScFresh
  and #B_Button
  beq Done
  lda SavedJoypadBits
  and #Down_Dir
  bne Done
  lda #12
  sta ScAttack
  lda #0
  sta SmBombHits               ; Keep one hit per enemy per cane swing.
  lda #Sfx_Fireball
  sta Square1SoundQueue
  rts
Clear:
  lda #0
  sta ScPogo
  sta ScAttack
Done:
  lda #0
  sta MmBulletType
  rts
Cane:
  ldx PlayerFacingDir
  cpx #1
  bne CaneLeft
  lda Player_X_Position
  clc
  adc #24
  sta MmBulletX
  lda Player_PageLoc
  adc #0                       ; Preserve the low-byte carry across the page.
  jmp CaneY
CaneLeft:
  lda Player_X_Position
  sec
  sbc #8
  sta MmBulletX
  lda Player_PageLoc
  sbc #0                       ; Preserve the low-byte borrow at the left seam.
CaneY:
  sta MmBulletPage
  lda Player_Y_Position
  clc
  adc #24
  sta MmBulletY
  jsr Bridge
  farcall MegaManWeapons::Blocks
  ; The cane's eight-pixel vertical band is Y+17..Y+24. Sampling only its
  ; bottom pixel traps Scrooge beneath adjacent hanging bricks. Avoid a
  ; redundant terrain call when both ends occupy the same metatile row.
  lda Player_Y_Position
  clc
  adc #17
  eor MmBulletY
  and #$f0
  beq CaneEnemy
  lda Player_Y_Position
  clc
  adc #17
  sta MmBulletY
  jsr Bridge
  farcall MegaManWeapons::Blocks
CaneEnemy:
  lda Player_Y_Position
  clc
  adc #24
  sta MmBulletY                 ; Enemy contact retains its existing probe.
  jsr Bridge
  farcall MegaManWeapons::Enemies
  rts
PogoHit:
  lda Player_Y_HighPos
  cmp #1
  jne PogoDone                ; An above-room body cannot hit bottom-room actors.
  lda Player_Y_Position
  cmp #208
  jcs PogoDone                ; Keep the foot probe/rectangle inside the playfield.
  lda Player_X_Position
  clc
  adc #8
  sta MmBulletX
  lda Player_PageLoc
  adc #0
  sta MmBulletPage
  lda Player_Y_Position
  clc
  adc #32
  sta MmBulletY
  lda SmBombHits
  sta ScEnemy
  ; A foot strike can reveal an invisible block inside the current descent.
  ; Retain both prior slot states: the native allocator may choose the other
  ; slot, so a change in its preferred-slot bit is not a reliable receipt.
  lda Block_State
  pha
  lda Block_State+1
  pha
  jsr Bridge
  farcall MegaManWeapons::Blocks
  lda SprDataOffset_Ctrl
  eor #1                     ; Native block dispatch flips after its actual slot.
  tax
  pla
  tay
  pla
  cpx #0
  beq PogoOldBlock
  tya
PogoOldBlock:
  and #15
  cmp #1
  beq PogoNoBump              ; A pre-existing bouncing block is not a new hit.
  lda Block_State,x
  cmp #$11                   ; Fresh real bump; debris/shatters use state$12.
  bne PogoNoBump
  lda Player_Y_Position
  sec
  sbc Block_Orig_YPos,x       ; Original row is tileTop-32, the foot's support Y.
  bcc PogoNoBump
  cmp #16
  bcs PogoNoBump
  lda Block_Orig_YPos,x
  sta Player_Y_Position      ; Separate vertically before the next foot parser.
  jsr ScroogeMovement::Bounce
  rts                        ; Retain the native live solid/bouncing placeholder.
PogoNoBump:
  jsr Bridge
  jsr PogoEnemies
  lda SmBombHits
  eor ScEnemy
  sta ScEnemy
  beq PogoDone
  ldx #5
PogoStruck:
  lda PogoBits,x
  and ScEnemy
  beq PogoNext
  ; Type10 marks contact before its immunity test. Only successful strikes
  ; rebound; the same protected enemy types remain immune to the cane/pogo.
  lda Enemy_ID,x
  cmp #Podoboo
  beq PogoNext
  cmp #BuzzyBeetle
  beq PogoNext
  cmp #BulletBill_FrenzyVar
  beq PogoNext
  cmp #BulletBill_CannonVar
  beq PogoNext
  jsr ScroogeMovement::Bounce
  rts
PogoNext:
  dex
  bpl PogoStruck
PogoDone:
  rts
PogoBits: .byte 1,2,4,8,16,32
PogoEnemies:
  ; DuckTales D291 uses the ordinary body center for a descending pogo,
  ; with |dx| strictly inside the summed widths and inclusive vertical touch.
  ; The shared enemy renderer's inclusive16px box therefore needs radius9
  ; horizontally and12 vertically about canonical center(+8,+20).
  lda MmBulletX
  sec
  sbc ScreenLeft_X_Pos
  sec
  sbc #9
  sta BoundingBox_UL_Corner+28
  clc
  adc #18
  sta BoundingBox_LR_Corner+28
  lda Player_Y_Position
  clc
  adc #8
  sta BoundingBox_UL_Corner+29
  clc
  adc #24
  sta BoundingBox_LR_Corner+29
  farcall MegaManWeapons::BeginEnemyLoop
  rts
Bridge:
  lda #10                       ; 100 damage; native terrain protection remains authoritative.
  sta MmBulletType
  lda PlayerFacingDir
  sta MmBulletDir
  lda #0
  sta MmSlot
  sta SmSlot                   ; Type10's shared damage path indexes this mask.
  tax
  rts
.endproc
.proc ScroogePogoContact
  ; Native DuckTales D318..D338 gives a successful descending pogo priority
  ; over body injury at the actual enemy contact. The earlier weapon pass
  ; uses visible16px shot targets; Bowser's real body begins6px higher and
  ; his rear is a duplicate. Resolve those real contacts here as well.
  phx
  phy
  lda ObjectOffset
  pha
  lda SelectedCharacter
  cmp #CHARACTER_SCROOGE
  jne Ordinary
  lda ScPogo
  jeq Ordinary
  lda Player_Y_HighPos
  cmp #1
  jne Ordinary
  lda Player_Y_Position
  cmp #208
  jcs Ordinary

  ; Retain the contacted half's actual prepared native body rectangle.
  txa
  asl
  asl
  clc
  adc #4
  tay
  lda BoundingBox_UL_Corner,y
  sta BoundingBox_UL_Corner+32
  lda BoundingBox_UL_Corner+1,y
  sta BoundingBox_UL_Corner+33
  lda BoundingBox_LR_Corner,y
  sta BoundingBox_LR_Corner+32
  lda BoundingBox_LR_Corner+1,y
  sta BoundingBox_LR_Corner+33

  ; The two Bowser halves share one health/hit receipt. Other duplicates
  ; are never eligible, and unrelated actors retain their own identity.
  lda Enemy_ID,x
  cmp #Bowser
  bne Target
  lda Enemy_Flag,x
  bpl Target
  and #$7f
  cmp #6
  jcs Ordinary
  tax
  lda Enemy_ID,x
  cmp #Bowser
  jne Ordinary
  lda Enemy_Flag,x
  jeq Ordinary
  jmi Ordinary
Target:
  stx MmEnemySlot
  lda MmVY+2
  jmi Rebounding
  ora MmVY+1
  ora MmVY
  jeq Ordinary
  lda Enemy_ID,x
  cmp #Bowser
  beq Susceptible
  cmp #$15
  jcs Ordinary
  cmp #Podoboo
  jeq Ordinary
  cmp #BuzzyBeetle
  jeq Ordinary
  cmp #BulletBill_FrenzyVar
  jeq Ordinary
  cmp #Goomba
  bne Susceptible
  lda Enemy_State,x
  cmp #2
  jcs Ordinary
Susceptible:
  lda Player_Rel_XPos
  sec
  sbc #1
  sta BoundingBox_UL_Corner+28
  clc
  adc #18
  sta BoundingBox_LR_Corner+28
  lda Player_Y_Position
  clc
  adc #8
  sta BoundingBox_UL_Corner+29
  clc
  adc #24
  sta BoundingBox_LR_Corner+29
  ldy #28
  ldx #32
  jsr SprObjectCollisionCore
  jcc Ordinary
  ldx MmEnemySlot
  stx ObjectOffset
  jsr ScroogeWeapons::Bridge
  ldx MmEnemySlot
  farcall MegaManWeapons::DamageEnemy
  lda #0
  sta MmBulletType
  ldx MmEnemySlot
  lda ScroogeWeapons::PogoBits,x
  and SmBombHits
  beq Ordinary
  ora ScEnemy
  sta ScEnemy
  jsr ScroogeMovement::Bounce
  jmp Protected
Rebounding:
  ; A surviving struck body cannot hurt us during its short hit flash.
  ; No general injury timer or protection from adjacent actors is granted.
  lda MmEnemyFlash,x
  beq Ordinary
  lda ScroogeWeapons::PogoBits,x
  and ScEnemy
  beq Ordinary
Protected:
  pla
  sta ObjectOffset
  ply
  plx
  sec
  rts
Ordinary:
  pla
  sta ObjectOffset
  ply
  plx
  clc
  rts
.endproc
.proc ScroogeGraphics
  lda GuestPowerupActive
  beq Normal
  farcall GuestPowerupPalette
  lda GuestPowerupPose
  sta RgPose
  farcall ExpandedPose
  rts
Normal:
  inc RgClock
  lda #XG_POSE_STAND
  ldx GameEngineSubroutine
  cpx #$0b
  bne :+
    lda #XG_POSE_DIE
    bne Pose
  :
  ldx ScAttack
  beq Pogo
  txa
  eor #$ff
  clc
  adc #13
  lsr
  lsr
  clc
  adc #XG_POSE_ATTACK1
  bne Pose
Pogo:
  ldx ScPogo
  beq State
  lda #XG_POSE_DASH
  bne Pose
State:
  ldx Player_State
  beq Walk
  lda #XG_POSE_JUMP
  bne Pose
Walk:
  ldx RgCrouch
  beq Moving
  lda #XG_POSE_CROUCH
  bne Pose
Moving:
  ldx Player_X_Speed
  beq Pose
  lda RgClock
  lsr
  lsr
  lsr
  and #3
  cmp #3
  bne :+
    lda #1
  :
  clc
  adc #XG_POSE_WALK1
Pose:
  sta RgPose
  farcall ExpandedPose
  rts
.endproc
.popseg
