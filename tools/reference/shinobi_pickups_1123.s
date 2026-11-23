; Loaded into the runs of identical values in the two Shinobi pose tables.
; The lookup workers return the original values for those runs.
ShHealth = $c539
ShMaxHealth = $c53a
ShFoodUpdate = $c752
ShWeapon = $c042
ShHeaderTable = $d125
ShPoseTable = $d185

.segment "SHINOBI_HEADER_GAP"
.export ShPickup
ShPickup:
    lda PowerUpType,x
    cmp #2
    bcs ShStockPickup
    lsr                         ; Flower leaves kind bit in carry.
    lda Enemy_State,x
    bpl PickupDone
    bcs ShFlowerPickup
    ; Shinobi's food item refills the original health and refreshes its HUD.
    lda ShMaxHealth
    sta ShHealth
    lda #1
    sta ShFoodUpdate
    sta PlayerStatus            ; The next authored upgrade block gives a Flower.
    jmp ShFoodAndFlowerEffect
PickupDone:
    clc
    rts

ShStockPickup:
    ; The native Star/1-UP collector begins by erasing the item. It ignores A.
    lda #<MarioSourcePowerupCollision
    sta FarcallJmpTarget_SMC+1
    lda #>MarioSourcePowerupCollision
    sta FarcallJmpTarget_SMC+2
    lda #Bank_MarioSourcePowerupCollision
    jmp FarCallCommon

.segment "SHINOBI_HEADER_HELP"
.export ShReadHeaderLow
ShReadHeaderLow:
    jsr ShReadPoseOrdinal
    bmi ShHeaderDefault
    lda ShHeaderTable,y
    rts
ShHeaderDefault:
    lda #$8c
    rts

.segment "SHINOBI_POSE_GAP"
.export ShReadPoseOrdinal
ShReadPoseOrdinal:
    php
    cpy #$0a
    bcc ShPoseRead
    cpy #$39
    bcc ShPoseInvalid
    cpy #$3e
    bcc ShPoseRead
    cpy #$4a
    bcc ShPoseInvalid
ShPoseRead:
    plp
    lda ShPoseTable,y
    rts
ShPoseInvalid:
    plp
    lda #$ff
    rts

ShFlowerPickup:
    ; The source weapon item increments the descriptor through tier three.
    lda ShWeapon
    and #$0f
    cmp #3
    bcc ShIncreaseWeapon
ShFoodAndFlowerEffect:
    jsr EraseEnemyObject
    lda #6
    jsr SetupFloateyNumber
    sec
    jmp ShFoodSound

.segment "SHINOBI_POSE_HELP"
ShFoodSound:
    lda #$20
    sta Square2SoundQueue
    rts
ShIncreaseWeapon:
    inc ShWeapon
    jmp ShFoodAndFlowerEffect

.segment "SHINOBI_CAMERA_ITEMS"
.export ShMature
; ShHostMovement sets carry before selecting the facing value.
    sta PlayerFacingDir
    lda Player_X_Position
    sbc ScreenLeft_X_Pos
    sta Player_Pos_ForScroll
    rts
ShMature:
    lda Enemy_State,x
    asl
    rts
