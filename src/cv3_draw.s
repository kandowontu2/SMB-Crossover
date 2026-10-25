.pushseg
.segment "CV3_COMBAT"
.proc Cv3DrawDispatch
 lda SelectedCharacter
 cmp #CHARACTER_KIRBY
 bcc Check
 farcall VvDrawDispatch,jmp
Check:
 farcall Cv3IsActive
 bcs Native
 farcall RosterDrawShots,jmp
Native:jmp Cv3DrawShots
.endproc
.proc Cv3DrawShots
 lda Cv3Variant
 cmp #3
 jeq AlucardArt
 BankPRGC #83
 jmp ArtReady
AlucardArt:
 BankPRGC #85
ArtReady:
 lda Cv3Variant
 asl
 clc
 adc #<516
 ldx #>518
 farcall X5SetSpecialChr
 lda Cv3Variant
 asl
 clc
 adc #<517
 ldx #>519
 ldy #5
 farcall X5SetPhysicalChr
 lda GameEngineSubroutine
 cmp #8
 jne Body
 lda MmDeathFlag
 jne Body
 inc Cv3DrawFirst
 lda Cv3DrawFirst
 and #3
 tax
 lda #4
 sta Cv3Temp3
Loop:
 stx Cv3Slot
 lda Cv3ShotType,x
 jeq Next
 jsr ProjectilePointer
 lda Cv3ShotX,x
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda Cv3ShotPage,x
 sbc ScreenLeft_PageLoc
 sta R5
 lda Cv3ShotY,x
 sta R6
 jsr Draw
Next:
 ldx Cv3Slot
 inx
 txa
 and #3
 tax
 dec Cv3Temp3
 jne Loop
 lda Cv3Variant
 cmp #2
 jne Rewards
 lda Cv3AttackKind
 cmp #1
 jne Rewards
 lda Cv3AttackAge
 cmp #15
 jcs Rewards
 cmp #3
 jcc Rewards
 lda #<Cv3W2P10R
 sta R0
 lda #>Cv3W2P10R
 sta R1
 lda Cv3AttackAge
 cmp #10
 jcs StaffFacing
 lda #<Cv3W2P11R
 sta R0
 lda #>Cv3W2P11R
 sta R1
StaffFacing:
 lda PlayerFacingDir
 cmp #2
 jne StaffPosition
 lda #<Cv3W2P10L
 sta R0
 lda #>Cv3W2P10L
 sta R1
 lda Cv3AttackAge
 cmp #10
 jcs StaffPosition
 lda #<Cv3W2P11L
 sta R0
 lda #>Cv3W2P11L
 sta R1
StaffPosition:
 lda Player_X_Position
 clc
 adc #8
 sta R4
 lda Player_PageLoc
 adc #0
 sta R5
 lda R4
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda R5
 sbc ScreenLeft_PageLoc
 sta R5
 lda Player_Y_Position
 clc
 adc #16
 sta R6
 lda Cv3AttackCrouch
 beq :+
 lda R6
 clc
 adc #8
 sta R6
: jsr Draw
Rewards:
 ldx #5
World:
 stx Cv3HitSlot
 lda Enemy_Flag,x
 jeq WorldNext
 lda Enemy_ID,x
 cmp #PowerUpObject
 jne WorldNext
 lda Cv3PickupVariant,x
 cmp Cv3Variant
 jne WorldNext
 lda InvPickupOwner,x
 cmp #CHARACTER_SIMON
 jne WorldNext
 lda InvPickup,x
 cmp #$d1
 jcc WorldNext
 cmp #$d5
 jcs WorldNext
 sec
 sbc #$d0
 sta Cv3Temp
 lda Cv3Variant
 cmp #2
 jeq SyphaReward
 cmp #3
 jeq AlucardReward
 lda Cv3Temp
 cmp #1
 jeq DaggerReward
 cmp #3
 jeq StopwatchReward
 lda #<Cv3W1P23R
 sta R0
 lda #>Cv3W1P23R
 jne RewardPointer
StopwatchReward:
 lda #<Cv3W1P40R
 sta R0
 lda #>Cv3W1P40R
 jne RewardPointer
DaggerReward:
 lda #<Cv3W1P27R
 sta R0
 lda #>Cv3W1P27R
 jne RewardPointer
SyphaReward:
 lda Cv3Temp
 cmp #1
 jeq FlameReward
 cmp #2
 jeq IceReward
 lda #<Cv3W2P27R
 sta R0
 lda #>Cv3W2P27R
 jne RewardPointer
IceReward:
 lda #<Cv3W2P23R
 sta R0
 lda #>Cv3W2P23R
 jne RewardPointer
FlameReward:
 lda #<Cv3W2P1FR
 sta R0
 lda #>Cv3W2P1FR
 jne RewardPointer
AlucardReward:
 lda #<Cv3W3P22R
 sta R0
 lda #>Cv3W3P22R
RewardPointer:sta R1
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
 jsr Draw
WorldNext:ldx Cv3HitSlot
 dex
 jpl World
 ldx #1
Drops:
 stx Cv3HitSlot
 lda Cv3DropType,x
 jeq DropNext
 lda Cv3Variant
 cmp #1
 jeq GrantHeart
 cmp #2
 jeq SyphaHeart
 lda #<Cv3W3P07R
 sta R0
 lda #>Cv3W3P07R
 jne HeartPointer
GrantHeart:
 lda #<Cv3W1P07R
 sta R0
 lda #>Cv3W1P07R
 jne HeartPointer
SyphaHeart:
 lda #<Cv3W2P07R
 sta R0
 lda #>Cv3W2P07R
HeartPointer:sta R1
 lda Cv3DropX,x
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda Cv3DropPage,x
 sbc ScreenLeft_PageLoc
 sta R5
 lda Cv3DropY,x
 sta R6
 jsr Draw
DropNext:ldx Cv3HitSlot
 dex
 jpl Drops
 jsr Hud
Body:
 lda Cv3Variant
 cmp #3
 jeq AlucardBody
 BankPRGC #83
 jmp Publish
AlucardBody:
 BankPRGC #85
Publish:
 lda SmChrBank
 ldx Cv3BodyChrUpper
 ldy #0
 farcall X5SetPhysicalChr
 rts
Draw:
 lda #1
 sta R7
 lda #0
 sta R3
 farcall MetaspriteRenderLoop
 rts
ProjectilePointer:
 lda Cv3ShotType,x
 cmp #2
 jeq AxePointer
 cmp #3
 jeq FlamePointer
 cmp #4
 jeq IcePointer
 lda Cv3ShotAge,x
 lsr
 lsr
 lsr
 and #1
 sta Cv3Temp2
 lda Cv3ShotType,x
 sec
 sbc #1
 asl
 clc
 adc Cv3Temp2
 tay
 lda Cv3ShotFlags,x
 cmp #2
 jeq Left
 lda RightLo,y
 sta R0
 lda RightHi,y
 sta R1
 rts
Left:
 lda LeftLo,y
 sta R0
 lda LeftHi,y
 sta R1
 rts
IcePointer:
 lda Cv3ShotAge,x
IceModulo:
 cmp #24
 jcc IcePhase
 sbc #24
 jmp IceModulo
IcePhase:
 tay
 lda AxeFrames,y
 tay
 lda IceRightLo,y
 sta R0
 lda IceRightHi,y
 sta R1
 rts
FlamePointer:
 lda Cv3ShotSpec,x
 sec
 sbc #30
 tay
 lda Cv3ShotFlags,x
 cmp #2
 jeq FlameLeft
 lda FlameRightLo,y
 sta R0
 lda FlameRightHi,y
 sta R1
 rts
FlameLeft:
 lda FlameLeftLo,y
 sta R0
 lda FlameLeftHi,y
 sta R1
 rts
AxePointer:
 lda Cv3ShotAge,x
AxeModulo:
 cmp #24
 jcc AxePhase
 sbc #24
 jmp AxeModulo
AxePhase:
 tay
 lda AxeFrames,y
 tay
 lda Cv3ShotFlags,x
 cmp #2
 jeq AxeLeft
 lda AxeRightLo,y
 sta R0
 lda AxeRightHi,y
 sta R1
 rts
AxeLeft:
 lda AxeLeftLo,y
 sta R0
 lda AxeLeftHi,y
 sta R1
 rts
IceRightLo:.byte <Cv3W2P23R,<Cv3W2P24R,<Cv3W2P25R,<Cv3W2P26R
IceRightHi:.byte >Cv3W2P23R,>Cv3W2P24R,>Cv3W2P25R,>Cv3W2P26R
FlameRightLo:.byte <Cv3W2P1ER,<Cv3W2P1FR,<Cv3W2P20R,<Cv3W2P21R,<Cv3W2P22R,<Cv3W2P22R,<Cv3W2P22R,<Cv3W2P22R,<Cv3W2P22R,<Cv3W2P22R,<Cv3W2P22R,<Cv3W2P22R,<Cv3W2P22R,<Cv3W2P2BR
FlameRightHi:.byte >Cv3W2P1ER,>Cv3W2P1FR,>Cv3W2P20R,>Cv3W2P21R,>Cv3W2P22R,>Cv3W2P22R,>Cv3W2P22R,>Cv3W2P22R,>Cv3W2P22R,>Cv3W2P22R,>Cv3W2P22R,>Cv3W2P22R,>Cv3W2P22R,>Cv3W2P2BR
FlameLeftLo:.byte <Cv3W2P1EL,<Cv3W2P1FL,<Cv3W2P20L,<Cv3W2P21L,<Cv3W2P22L,<Cv3W2P22L,<Cv3W2P22L,<Cv3W2P22L,<Cv3W2P22L,<Cv3W2P22L,<Cv3W2P22L,<Cv3W2P22L,<Cv3W2P22L,<Cv3W2P2BL
FlameLeftHi:.byte >Cv3W2P1EL,>Cv3W2P1FL,>Cv3W2P20L,>Cv3W2P21L,>Cv3W2P22L,>Cv3W2P22L,>Cv3W2P22L,>Cv3W2P22L,>Cv3W2P22L,>Cv3W2P22L,>Cv3W2P22L,>Cv3W2P22L,>Cv3W2P22L,>Cv3W2P2BL
AxeFrames:.byte 0,0,0,0,0,0,1,1,1,1,1,1,2,2,2,2,2,2,3,3,3,3,3,3
AxeRightLo:.byte <Cv3W1P23R,<Cv3W1P24R,<Cv3W1P25R,<Cv3W1P26R
AxeRightHi:.byte >Cv3W1P23R,>Cv3W1P24R,>Cv3W1P25R,>Cv3W1P26R
AxeLeftLo:.byte <Cv3W1P23L,<Cv3W1P24L,<Cv3W1P25L,<Cv3W1P26L
AxeLeftHi:.byte >Cv3W1P23L,>Cv3W1P24L,>Cv3W1P25L,>Cv3W1P26L
RightLo:.byte <Cv3W1P27R,<Cv3W1P27R,<Cv3W1P23R,<Cv3W1P24R,<Cv3W2P1FR,<Cv3W2P20R,<Cv3W2P23R,<Cv3W2P24R,<Cv3W2P27R,<Cv3W2P28R,<Cv3W3P20R,<Cv3W3P20R
RightHi:.byte >Cv3W1P27R,>Cv3W1P27R,>Cv3W1P23R,>Cv3W1P24R,>Cv3W2P1FR,>Cv3W2P20R,>Cv3W2P23R,>Cv3W2P24R,>Cv3W2P27R,>Cv3W2P28R,>Cv3W3P20R,>Cv3W3P20R
LeftLo:.byte <Cv3W1P27L,<Cv3W1P27L,<Cv3W1P23L,<Cv3W1P24L,<Cv3W2P1FL,<Cv3W2P20L,<Cv3W2P23L,<Cv3W2P24L,<Cv3W2P27L,<Cv3W2P28L,<Cv3W3P20L,<Cv3W3P20L
LeftHi:.byte >Cv3W1P27L,>Cv3W1P27L,>Cv3W1P23L,>Cv3W1P24L,>Cv3W2P1FL,>Cv3W2P20L,>Cv3W2P23L,>Cv3W2P24L,>Cv3W2P27L,>Cv3W2P28L,>Cv3W3P20L,>Cv3W3P20L
Hud:
 lda FrameCounter
 and #15
 jne HudDone
 lda Cv3Variant
 cmp #3
 jeq HudAlucard
 sec
 sbc #1
 asl
 asl
 sta Cv3Temp
 ldy Cv3Variant
 dey
 lda Cv3Subweapon,y
 and #3
 clc
 adc Cv3Temp
 jmp HudComputed
HudAlucard:
 lda Cv3Power+2
 cmp #3
 bcc :+
 lda #2
:
 clc
 adc #8
HudComputed:
 sta Cv3Temp
 cmp Cv3HudWeapon
 jne HudDirty
 lda Cv3Variant
 cmp Cv3HudVariant
 jne HudDirty
 ldy Cv3Variant
 dey
 lda Cv3Health,y
 cmp Cv3HudHealth
 jne HudDirty
 lda Cv3Hearts,y
 cmp Cv3HudHearts
 jeq HudDone
HudDirty:
 ldx VRAM_Buffer1_Offset
 cpx #(84-(3+19)) ; 19 status tiles, 3 header bytes and the terminator.
 jcs HudDone
 lda #$20
 sta VRAM_Buffer1,x
 lda #$23 ; Free top HUD row, above the original name/score/world/time.
 sta VRAM_Buffer1+1,x
 lda #19
 sta VRAM_Buffer1+2,x
 .repeat 19,I
 lda HudTemplate+I
 sta VRAM_Buffer1+3+I,x
 .endrepeat
 ldy Cv3Variant
 dey
 lda Cv3Health,y
 lsr
 lsr
 jsr Decimal
 sta VRAM_Buffer1+6,x
 tya
 sta VRAM_Buffer1+5,x
 ldy Cv3Variant
 dey
 lda Cv3Hearts,y
 jsr Decimal
 sta VRAM_Buffer1+14,x
 tya
 sta VRAM_Buffer1+13,x
 lda Cv3Temp
 asl
 clc
 adc Cv3Temp
 asl
 tay
 .repeat 6,I
 lda HudWeapons+I,y
 sta VRAM_Buffer1+16+I,x
 .endrepeat
 txa
 clc
 adc #22
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 lda Cv3Variant
 sta Cv3HudVariant
 tay
 dey
 lda Cv3Health,y
 sta Cv3HudHealth
 lda Cv3Hearts,y
 sta Cv3HudHearts
 lda Cv3Temp
 sta Cv3HudWeapon
HudDone:rts
HudTemplate:.byte "HP00 HEART00       "
HudWeapons:
 .byte "KNIFE ","DAGGER","AXE   ","WATCH "
 .byte "STAFF ","FLAME ","ICE   ","ORBS  "
 .byte "BOLT1 ","BOLT2 ","BOLT3 "

Decimal:
 ldy #0
Tens:cmp #10
 jcc Digits
 sec
 sbc #10
 iny
 jne Tens
Digits:rts
.endproc
.popseg

