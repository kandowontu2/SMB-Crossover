; Original manual quantities and single-adaptor ownership. SMB block contents,
; 48-update block emergence, enemy drop rate/flight and water are explicit port
; adaptations; no claim that the original game contains SMB question blocks.
.pushseg
.segment "DARKWING_CORE"
.proc DwInventoryInit
  farcall X5InventoryInit
  lda #0
  ldx #8
:
  sta DwHealth,x
  dex
  bpl :-
  lda #4
  sta DwHealth
  rts
.endproc
.proc DwPreparePickup
  DwGate InventoryPreparePickup
Duck:
  lda #0
  sta InvRisePhase,x
  lda #$fc
  sta InvPickup,x
  lda PowerUpType,x
  cmp #2
  bcs Done
  lda #CHARACTER_SCROOGE
  sta InvPickupOwner,x
  ; Native mushroom blocks become full health until an adaptor has been
  ; acquired. Afterwards each block's world column deterministically selects
  ; one of the three original adaptor icons. Re-hitting a reloaded block has
  ; the same content; ownership never indexes the twelve-family inventory.
  lda DwAdaptor
  beq Health
  lda Enemy_X_Position,x
  lsr
  lsr
  lsr
  lsr
  clc
  adc Enemy_PageLoc,x
Reduce:
  cmp #3
  bcc Adaptor
  sec
  sbc #3
  jmp Reduce
Adaptor:
  tay
  lda Icons,y
  bne Publish
Health:
  lda DwHealth
  cmp #4
  bcc Aid
  lda #$26                    ; explicit SMB first-upgrade Arrow adaptation
  bne Publish
Aid:
  lda #$23
Publish:
  sta InvPickup,x
  lda #1
  sta PowerUpType,x
Done:
  rts
Icons:.byte $27,$28,$26         ; Heavy, Thunder, Arrow
.endproc
.proc DwPrivatePickup
  DwGate InventoryPrivatePickup
Duck:
  lda Enemy_ID,x
  cmp #PowerUpObject
  bne No
  lda InvPickupOwner,x
  cmp #CHARACTER_SCROOGE
  bne No
  lda InvPickup,x
  cmp #$22
  bcc No
  cmp #$29
  bcs No
  sec
  rts
No:
  clc
  rts
.endproc
.proc DwPickupCollision
  jsr DwPrivatePickup
  bcc Allowed
  lda Enemy_State,x
  bmi Allowed
  cmp #2
  bcc Hidden
  txa
  asl
  asl
  tay
  lda Enemy_Y_Position,x
  clc
  adc #8
  sta EnemyBoundingBoxCoord+1,y
  lda Enemy_Y_Position,x
  clc
  adc Enemy_State,x
  adc #6
  sta EnemyBoundingBoxCoord+3,y
Allowed:
  sec
  rts
Hidden:
  clc
  rts
.endproc
.proc DwRisePickup
  jsr DwPrivatePickup
  bcc Native
  lda TimerControl
  bne Handled
  inc InvRisePhase,x
  lda InvRisePhase,x
  cmp #3
  bcc Handled
  lda #0
  sta InvRisePhase,x
  dec Enemy_Y_Position,x
  inc Enemy_State,x
  lda Enemy_State,x
  cmp #17
  bcc Handled
  lda #$80
  sta Enemy_State,x
  lda #0
  sta Enemy_SprAttrib,x
  sta Enemy_X_Speed,x
Handled:
  sec
Native:
  rts
.endproc
.proc DwCollectPickup
  DwGate InventoryCollect
  ; Native HandlePowerUpCollision erases the actor BEFORE this hook. Its
  ; proven powerup callsite owns collection; use the immutable reveal stamp,
  ; while drawing/private admission still requires a live PowerUpObject ID.
  lda InvPickupOwner,x
  cmp #CHARACTER_SCROOGE
  bne Native
  lda InvPickup,x
  cmp #$22
  bcc Native
  cmp #$29
  bcs Native
Duck:
  phx
  lda InvPickup,x
  jsr DwGiveItem
  plx
  sec
  rts
Native:
  clc
  rts
.endproc
.proc DwGiveItem
  cmp #$22
  bne Full
  lda DwHealth
  cmp #4
  bcs Sound
  inc DwHealth
  bne Sound
Full:
  cmp #$23
  bne Gas
  lda #4
  sta DwHealth
  bne Sound
Gas:
  cmp #$24
  beq Ten
  cmp #$25
  bne Adaptor
  lda #1
  bne Add
Adaptor:
  cmp #$26
  bcc Sound
  cmp #$29
  bcs Sound
  sec
  sbc #$26
  tax
  lda Kinds,x
  sta DwAdaptor                ; replacing one carried adaptor is intentional
Ten:
  lda #10
Add:
  clc
  adc DwGas
  cmp #100
  bcc :+
  lda #99
:
  sta DwGas
Sound:
  lda #Sfx_PowerUpGrab
  sta Square2SoundQueue
  rts
Kinds:.byte 2,1,3
.endproc
.proc DwCanDrop
  DwGate RemainingCanDrop
  sec
  rts
.endproc
.proc DwDropMade
  DwGate RemainingDropMade
  lda PseudoRandomBitReg+2
  and #7
  tay
  lda Icons,y
  sta AvDropItem,x
  rts
Icons:.byte $25,$25,$25,$24,$22,$22,$22,$23
.endproc
.proc DwRefill
  DwGate RemainingRefill
  lda AvRefillItem
  jmp DwGiveItem
.endproc
.proc DwDrawPickups
  ldx #5
World:
  stx InvDrawSlot
  lda Enemy_Flag,x
  beq Next
  jsr DwPrivatePickup
  bcc Next
  lda Enemy_State,x
  bmi Visible
  cmp #2
  bcc Next
Visible:
  lda #0
  sta EnemyMetasprite,x
  lda InvPickup,x
  tay
  lda DwWeaponBase,y
  tay
  lda DwWeaponRLo,y
  sta R0
  lda DwWeaponRHi,y
  sta R1
  lda Enemy_X_Position,x
  clc
  adc #8
  sta R4
  lda Enemy_PageLoc,x
  adc #0
  sta R5
  lda R4
  sec
  sbc ScreenLeft_X_Pos
  sta R4
  lda R5
  sbc ScreenLeft_PageLoc
  sta R5
  lda Enemy_Y_Position,x
  clc
  adc #8
  sta R6
  lda Enemy_Y_HighPos,x
  adc #0
  sta R7
  lda #0
  sta R3
  farcall MetaspriteRenderLoop
Next:
  ldx InvDrawSlot
  dex
  bpl World
  ldx #3
Drops:
  stx InvDrawSlot
  lda InvDropKind,x
  beq NextDrop
  lda InvDropAgeHi,x
  beq DropVisible
  lda InvDropAge,x
  and #4
  bne NextDrop
DropVisible:
  lda AvDropItem,x
  tay
  lda DwWeaponBase,y
  tay
  lda DwWeaponRLo,y
  sta R0
  lda DwWeaponRHi,y
  sta R1
  lda InvDropX,x
  sec
  sbc ScreenLeft_X_Pos
  sta R4
  lda InvDropPage,x
  sbc ScreenLeft_PageLoc
  sta R5
  lda InvDropY,x
  sta R6
  lda #1
  sta R7
  lda #0
  sta R3
  farcall MetaspriteRenderLoop
NextDrop:
  ldx InvDrawSlot
  dex
  bpl Drops
  jmp DwHud
.endproc
.proc DwHud
  lda FrameCounter
  and #15
  bne Done
  ldx VRAM_Buffer1_Offset
  cpx #$49 ;11B spaced status plus terminator fits84B queue
  bcs Done
  lda #$20
  sta VRAM_Buffer1,x
  lda #$49
  sta VRAM_Buffer1+1,x
  lda #8
  sta VRAM_Buffer1+2,x
  lda #'H'
  sta VRAM_Buffer1+3,x
  lda DwHealth
  sta VRAM_Buffer1+4,x
  lda #$24
  sta VRAM_Buffer1+5,x
  sta VRAM_Buffer1+9,x
  lda #'G'
  sta VRAM_Buffer1+6,x
  lda DwGas
  ldy #0
Tens:
  cmp #10
  bcc Digits
  sec
  sbc #10
  iny
  bne Tens
Digits:
  sta VRAM_Buffer1+8,x
  tya
  sta VRAM_Buffer1+7,x
  lda DwMode
  and #1
  beq Mode
  lda DwAdaptor
  beq Mode
  tay
  lda Letters,y
Mode:
  bne Put
  lda #'N'
Put:
  sta VRAM_Buffer1+10,x
  txa
  clc
  adc #11
  sta VRAM_Buffer1_Offset
  tax
  lda #0
  sta VRAM_Buffer1,x
Done:
  rts
Letters:.byte 'N','H','A','T'
.endproc
.popseg
