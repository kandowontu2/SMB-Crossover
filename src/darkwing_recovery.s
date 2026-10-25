; Explicit SMB acquisition/recovery adaptation approved by parent/user.
; The original Duck game does not contain these SMB powerblocks or caches.
; Unmodified50px jump and original Arrow toolkit remain the traversal method.
DwCacheCooldown=$5e80
DwCacheArea=$5e81
DwCacheWorld=$5e82
DwCacheLife=$5e83
DwCachePending=$5e84
DwCacheDirection=$5e85
.export DwCacheCooldown,DwCachePending
.pushseg
.segment "DARKWING_CORE"
.proc DwRecovery
  lda TimerControl
  jne Done
  lda GameEngineSubroutine
  cmp #8
  jne Done
  lda AreaPointer
  cmp DwCacheArea
  bne Reset
  lda WorldNumber
  cmp DwCacheWorld
  bne Reset
  lda NumberofLives
  cmp DwCacheLife
  beq Clock
Reset:
  lda AreaPointer
  sta DwCacheArea
  lda WorldNumber
  sta DwCacheWorld
  lda NumberofLives
  sta DwCacheLife
  lda #0
  sta DwCacheCooldown
  sta DwCachePending
Clock:
  lda DwCacheCooldown
  beq Need
  dec DwCacheCooldown
Need:
  lda DwAdaptor
  cmp #2
  bne Check
  lda DwGas
  cmp #3
  jcs Cancel
Check:
  lda Player_State
  jne Cancel
  lda Player_X_Speed
  jne Cancel
  lda RgBillBurstDelay
  jne Cancel
  lda SavedJoypadBits
  and #3
  cmp #1
  beq Direction
  cmp #2
  jne Cancel
Direction:
  sta DwCacheDirection
  lda #32                      ; center+24 ahead of a right-facing player
  ldy DwCacheDirection
  cpy #1
  beq Probe
  lda #$f0                    ; center-24 ahead when facing left
Probe:
  ldy #0
  cmp #$80
  bcc :+
  dey
:
  clc
  adc Player_X_Position
  sta RgTempX
  tya
  adc Player_PageLoc
  sta RgTempPage
  lda Player_Y_Position
  sec
  sbc #20                     ;52px above feet: only pipes taller than50px
  sta RgTempY
  farcall ExpandedMapCell
  bcc Cancel
  cmp #$10                    ; typed native vertical pipe caps/shafts only
  bcc Cancel
  cmp #$16
  bcs Cancel
  lda #1
  sta DwCachePending
  lda DwCacheCooldown
  bne Done
  ldx #5
Visible:
  lda Enemy_Flag,x
  beq Next
  lda Enemy_ID,x
  cmp #PowerUpObject
  bne Next
  lda InvPickupOwner,x
  cmp #CHARACTER_SCROOGE
  bne Next
  lda InvPickup,x
  cmp #$26
  beq Done                    ; at most one visible/pending recovery icon
Next:
  dex
  bpl Visible
  ldx #5
Free:
  lda Enemy_Flag,x
  beq Spawn
  dex
  bpl Free
  rts                         ; capacity pressure never deletes another actor
Cancel:
  lda #0
  sta DwCachePending
Done:
  rts
Spawn:
  lda #$e8                    ; world pickup center24px behind the character
  ldy DwCacheDirection
  cpy #1
  beq XPos
  lda #24
XPos:
  ldy #0
  cmp #$80
  bcc :+
  dey
:
  clc
  adc Player_X_Position
  sta Enemy_X_Position,x
  tya
  adc Player_PageLoc
  sta Enemy_PageLoc,x
  lda Player_Y_Position
  clc
  adc #8
  sta Enemy_Y_Position,x
  lda Player_Y_HighPos
  adc #0
  sta Enemy_Y_HighPos,x
  lda #PowerUpObject
  sta Enemy_ID,x
  lda #1
  sta Enemy_Flag,x
  sta PowerUpType,x
  sta Enemy_MovingDir,x
  lda #$80
  sta Enemy_State,x
  lda #3
  sta Enemy_BoundBoxCtrl,x
  lda #CHARACTER_SCROOGE
  sta InvPickupOwner,x
  lda #$26
  sta InvPickup,x
  lda #0
  sta InvRisePhase,x
  sta Enemy_CollisionBits,x
  sta EnemyMetasprite,x
  sta Enemy_SprAttrib,x
  sta Enemy_X_Speed,x
  sta Enemy_Y_Speed,x
  sta Enemy_Y_MoveForce,x
  sta DwCachePending
  lda #120
  sta DwCacheCooldown
  rts
.endproc
.popseg
