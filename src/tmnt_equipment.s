; Original TMNT1 gear semantics; SMB block delivery is explicitly adapted.
.pushseg
.segment "TMNT_CORE"
.proc TnTrySecondary
 lda TnGearSelected
 jeq Primary
 ldx TnVariant
 lda TnEquipment,x
 jeq Empty
 cmp #5
 jcs Empty
 lda TnAmmo,x
 jeq Empty
 lda #1
 sta TnThrow
 lda #4
 sta TnNativeFlags
 lda #$82
 ldy Player_State
 bne Air
 ldy TnHeld
 tya
 and #Down_Dir
 beq Stand
 lda #$84
 bne Set
Stand:lda #$82
 bne Set
Air:lda #$86
Set:ldx #0
 jsr TnSetSequence
 lda #Sfx_Fireball
 sta Square1SoundQueue
 lda #0
 sta TnSpawned
Find:ldx #0
Free:lda TnShotKind,x
 beq Spawn
 inx
 cpx #3
 bcc Free
 jcs Spend
Spawn:
 ldy TnVariant
 lda TnEquipment,y
 sta TnShotKind,x
 lda Player_X_Position
 clc
 adc #8
 sta TnShotX,x
 lda Player_PageLoc
 adc #0
 sta TnShotPage,x
 lda Player_Y_Position
 clc
 adc #8
 sta TnShotY,x
 lda TnSeq
 cmp #$84
 bne Position
 lda TnShotY,x
 clc
 adc #12
 sta TnShotY,x
Position:
 lda PlayerFacingDir
 sta TnShotFace,x
 lda #5
 ldy PlayerFacingDir
 cpy #2
 bne Velocity
 lda #$fb
Velocity:sta TnShotVX,x
 lda #0
 sta TnShotVXLo,x
 sta TnShotFrac,x
 sta TnShotAge,x
 sta TnShotAnim,x
 sta TnShotPhase,x
 sta TnShotVY,x
 lda #3
 sta TnShotTimer,x
 lda TnShotKind,x
 cmp #2
 bne Count
 ldy TnSpawned
 lda TripleY,y
 sta TnShotVY,x
Count:inc TnSpawned
 lda TnShotKind,x
 cmp #2
 bne Spend
 lda TnSpawned
 cmp #3
 jcc Find
Spend:
 lda TnSpawned
 beq Handled
 ldx TnVariant
 dec TnAmmo,x
 bne Handled
 lda #0
 sta TnEquipment,x
 sta TnGearSelected
Handled:sec
 rts
Empty:lda #0
 sta TnGearSelected
 sta TnEquipment,x
 sta TnAmmo,x
Primary:clc
 rts
TripleY:.byte 0,$ff,1
.endproc
; A=kind1..4. Native same-kind addition20/cap99; replacement20/autoselect.
.proc TnGiveEquipment
 ldx TnVariant
 cmp TnEquipment,x
 beq Refill
 sta TnEquipment,x
 lda #1
 sta TnGearSelected
 lda #20
 bne Store
Refill:lda TnAmmo,x
 clc
 adc #20
 cmp #100
 bcc Store
 lda #99
Store:sta TnAmmo,x
 lda #Sfx_PowerUpGrab
 sta Square2SoundQueue
 rts
.endproc
; Every wrapper restores the incoming A/P before the exact non19 fallback.
.proc TnPreparePickupDispatch
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 beq Own
 pla
 plp
 farcall Cv3PreparePickupGate,jmp
Own:pla
 plp
 lda #0
 sta TnPickupStamp,x
 sta InvRisePhase,x
 lda #$fc
 sta InvPickup,x
 lda #CHARACTER_TMNT
 sta InvPickupOwner,x
 lda PowerUpType,x
 cmp #1
 bne Done
 ldy TnVariant
 lda TnHealth,y
 cmp #128
 bne Done
 lda #4
 sta TnPickupStamp,x
 lda #$b4
 sta InvPickup,x
Done:rts
.endproc
.proc TnPrivatePickup
 lda Enemy_ID,x
 cmp #PowerUpObject
 bne No
 lda InvPickupOwner,x
 cmp #CHARACTER_TMNT
 bne No
 lda InvPickup,x
 cmp #$b4
 bne No
 lda TnPickupStamp,x
 cmp #4
 bne No
 sec
 rts
No:clc
 rts
.endproc
.proc TnPrivatePickupDispatch
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 beq Own
 pla
 plp
 farcall Cv3PrivatePickupGate,jmp
Own:pla
 plp
 jmp TnPrivatePickup
.endproc
.proc TnRisePickupDispatch
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 beq Own
Legacy:pla
 plp
 farcall Cv3RisePickupGate,jmp
Own:
 jsr TnPrivatePickup
 bcc Legacy
 pla
 plp
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
Handled:sec
 rts
.endproc
.proc TnPickupCollisionDispatch
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 beq Own
Legacy:pla
 plp
 farcall DwPickupCollision,jmp
Own:
 jsr TnPrivatePickup
 bcc Legacy
 pla
 plp
 lda Enemy_State,x
 bpl Hidden
 ; This original16x16 icon is drawn from the native actor's bottom pivot.
 ; Expose the completed item only; never collect while inside the block.
 txa
 asl
 asl
 tay
 jsr TnPickupScreenBox
 .res 13,$ea ; retain the original sixteen-byte span
 lda Enemy_Y_Position,x
 clc
 adc #4
 sta EnemyBoundingBoxCoord+1,y
 clc
 adc #10
 sta EnemyBoundingBoxCoord+3,y
 sec
 rts
Hidden:clc
 rts
.endproc
.proc TnCollectEquipment
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 bne No
 jsr TnPrivatePickup
 bcc No
 lda Enemy_State,x
 bpl No
 phx
 lda #4
 jsr TnGiveEquipment
 plx
 lda #0
 sta TnPickupStamp,x
 sta InvPickup,x
 sec
 rts
No:clc
 rts
.endproc
.proc TnEnemyDropDispatch
 php
 pha
 phx
 phy
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 beq Own
 ply
 plx
 pla
 plp
 farcall JnDropDispatch,jmp
Own:
 lda Enemy_Flag,x
 beq Done
 bmi Done
 lda Enemy_State,x
 and #$20
 bne Done
 lda Enemy_ID,x
 cmp #Bowser
 bne NotBoss
 lda #0
 sta TnDropCounter
 beq Done
NotBoss:
 cmp #BulletBill_CannonVar
 beq Eligible
 cmp #$15
 bcs Done
 cmp #Podoboo
 beq Done
Eligible:
 lda TnDropReceipt,x
 bne Done
 lda #1
 sta TnDropReceipt,x
 inc TnDropCounter
 lda TnDropCounter
 cmp #25
 bne Done
 lda #0
 sta TnDropCounter
 lda PseudoRandomBitReg+1
 and #1
 bne Done
 ldy #3
Find:lda TnDropKind,y
 beq Spawn
 dey
 bpl Find
 bmi Done
Spawn:
 lda PseudoRandomBitReg+1
 lsr
 and #3
 sty TnRewardSlot
 tay
 lda Kinds,y
 ldy TnRewardSlot
 sta TnDropKind,y
 lda Enemy_X_Position,x
 clc
 adc #8
 sta TnDropX,y
 lda Enemy_PageLoc,x
 adc #0
 sta TnDropPage,y
 lda Enemy_Y_Position,x
 clc
 adc #8
 sta TnDropY,y
 lda #128
 sta TnDropTimer,y
Done:ply
 plx
 pla
 plp
 rts
Kinds:.byte 1,1,2,3
.endproc
.popseg
