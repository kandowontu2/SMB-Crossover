; Generated original native instructions with symbolicRAM retargeting.
.pushseg
.segment "Z2_COLD"
.scope Z2Native
L93B0: rts
Table_for_Link1:
.byt    $01,$FF
L93B3:
.byt    $18,$E8
L93B5:
.byt    $08,$F8
L93B7:
.byt    $08,$07,$05,$04,$03
bank0_Side_View4__walking:
 lda Z2NativeEntryTimer
 jeq L93CD
 ldy Z2NativeEntrySide
 lda L93B5,y
ASL
 sta Z2NativeVX
 jmp bank0_jump_to__143A
L93CD:
 lda Z2NativeRecoilTimer
 jne L93DC
 lda Z2AttackStage
 jeq L93DC
 lda Z2NativeAir
 jeq L93B0
L93DC:
 lda Z2NativeShield
 jeq L93E6
 ldy Z2NativeHeldLR
DEY
 jpl Links_Acceleration_Routine
L93E6:
 lda Z2NativeAir
 jne L942B
 ldy Z2NativeWalkFace
DEY
 lda Z2NativeVX
 jeq L93FA
SEC
 sbc Table_for_Link1,y
 sta Z2NativeVX
 jne L93FA
L93FA:
 jmp L9419
Links_Acceleration_Routine:
 lda Z2NativeVX
 cmp L93B3,y
 jeq L9419
CLC
 adc Table_for_Link1,y
INY
 cpy Z2NativeWalkFace
 jeq L9417
DEY
 cmp L93B3,y
 jeq L9417
CLC
 adc Table_for_Link1,y
L9417:
 sta Z2NativeVX
L9419:
 lda Z2NativeShield
 jne L942B
 jsr L942B
 lda Z2NativeContacts
 and #$04
 jeq L942A
 lda #$06
 sta Z2CachedPose
L942A:
RTS
L942B:
 lda Z2NativeContacts
 and #$03
 jeq bank0_jump_to__143A
 lda Z2NativeHeldLR
 jeq L9438
 lda #$05
L9438:
 jpl L943F
bank0_jump_to__143A:
 jsr bank0_goto__1610
 lda Z2NativeVX
L943F:
 ldy Z2NativeAir
 jne L9468
 cmp #$00
 jeq L946C
 jpl L944F
 eor #$FF
CLC
 adc #$01
L944F:
LSR
LSR
LSR
TAY
 ldx Z2NativeWalkTimer
 jne L9468
 lda L93B7,y
 sta Z2NativeWalkTimer
 inc Z2NativeWalkFrame
 lda Z2NativeWalkFrame
 cmp #$03
 jcc L9468
 stx Z2NativeWalkFrame
L9468:
 lda Z2NativeWalkFrame
 jpl L949B
L946C:
 lda #$03
 jne L949B
bank0_Table_for_Link2:
.byt    $FB,$FB,$FC,$FC
L9474:
.byt    $80,$00,$F0,$80
L9478:
.byt    $06,$06,$20
L947B:
.byt    $04,$05,$03,$04,$07,$06
L9481:
.byt    $01,$03
bank0_Sword_Slash:
 ldy Z2AttackStage
 jeq L94C2
DEY
 ldx Z2NativeAttackStand
 lda Z2AttackTimer
 jeq L949E
DEX
 jpl L9498
INY
INY
INY
INY
L9498:
 lda L947B,y
L949B:
 sta Z2CachedPose
RTS
L949E:
TYA
 cmp L9481,x
 jeq L94B6
 lda L9478,y
 sta Z2AttackTimer
 inc Z2AttackStage
INY
 cpy Z2NativeAttackStand
 jne L94C2
 jmp bank0_set_sound_of_Sword_Slash
L94B6:
 lda #$00
 sta Z2AttackStage
 lda Z2NativeAir
 jne L94C2
 sta Z2NativeVX
L94C2:
RTS
bank0_unknown15:
.byt    $00,$0E
Link_Jumping_routine:
 lda Z2NativeElevator
 jne L94C2
 lda Z2NativeContacts
 and #$04
 jne L94DA
 lda Z2NativeAir
 jne L952D
 inc Z2NativeAir
 jne L952D
L94DA:
 lda Z2NativeAir
 jeq L94F8
 ldy Z2NativeVY
 jmi L952D
 cpy #$05
 jcc L94ED
 lda #$08
 sta Z2NativeLandCrouch
L94ED:
 lda #$00
 sta Z2NativeAir
 sta Z2NativeVY
 sta Z2AttackStage
L94F8:
 lda Player_Y_Position
 and #$F0
 sta Player_Y_Position
 lda Z2NativePressedAB
 and #$80
 jeq L94C2
 ldy #$00
 sty Z2AttackStage
 sty Z2NativeLandCrouch
 lda Z2NativeVX
 adc #$13
 cmp #$26
 jcc L9516
INY
L9516:
 lda Z2NativeJumpFlag
 jne L951C
INY
INY
L951C:
 lda bank0_Table_for_Link2,y
 sta Z2NativeVY
 lda L9474,y
 sta Z2NativeGravityFraction
 lda #$02
 sta Z2NativeAir
L952D:
 ldy #$48
 lda SavedJoypadBits
 and #$80
 jeq L953C
 lda Z2NativeVY
 jpl L953C
 ldy #$30
L953C:
 sty $00
 lda #$05
 sta $02
 ldx #$00
 lda Z2NativeVY
 jpl L9569
 lda Z2NativeContacts
 and #$08
 jeq L9569
 ldy Z2NativeVY
INY
 jpl L955E
 ldy #$FF
 sty Z2NativeVY
INY
 sty Z2NativeGravityFraction
L955E:
 lda Player_Y_Position
PHA
 jsr bank7_applyGravityMotion
PLA
 sta Player_Y_Position
 jne L956C
L9569:
 jsr bank7_applyGravityMotion
L956C:
 ldy Z2NativeAir
DEY
 jeq L958C
 ldy #$06
 lda Z2Tech
 and #$04
 jeq L9582
 lda SavedJoypadBits
 and #$08
 jeq L9582
TAY
L9582:
TYA
 ldy Z2NativeVY
 jmi L958A
 lda #$02
L958A:
 sta Z2CachedPose
L958C:
 lda Z2Tech
 and #$10
 jeq L959B
 lda Z2NativeShield
 jne L959B
 lda #$09
 sta Z2CachedPose
L959B:
RTS
L959C:
 lda SavedJoypadBits
 and #$87
 jeq L95B5
 ldy Z2AttackStage
 cpy #$04
 jne L95B5
 ldy #$00
 sty Z2AttackStage
 lda Z2NativeAir
 jne L95B5
 sta Z2NativeVX
L95B5:
 lda SavedJoypadBits
 and #$0C
 sta Z2NativeHeldUD
 ldy #$00
 and #$04
 jne L95C3
INY
L95C3:
 sty a:Z2NativeShield
 lda SavedJoypadBits
 and #$03
 sta Z2NativeHeldLR
 jeq L95D1
 sta PlayerFacingDir
L95D1:
 lda Z2NativePressed
 and #$C0
 sta Z2NativePressedAB
 and #$40
 jeq L960F
bank0_Button_B_Pressed:
 lda PlayerFacingDir
 sta Z2NativeAttackFace
 lda Z2NativeAir
 jne L95ED
 lda Z2NativeRecoilTimer
 jne L95ED
 sta Z2NativeVX
L95ED:
 ldy #$01
 lda Z2AttackStage
 jeq L95FC
 cmp #$04
 jne L960F
 jsr bank0_set_sound_of_Sword_Slash
INY
L95FC:
 sty Z2AttackStage
 lda #$06
 sta Z2AttackTimer
 lda Z2NativeShield
 sta Z2NativeAttackStand
 jne L960F
bank0_set_sound_of_Sword_Slash:
 lda #$20
 sta Z2NativeSound2
L960F:
RTS
bank0_goto__1610:
 lda Z2NativeLava
 jeq L9626
 lda FrameCounter
LSR
 jcc L962D
 and #$03
 jne L9626
 ldy Z2NativeVX
 jeq L9626
 lda #$20
L9624:
L9625     = * + $0001
 sta Z2NativeSound3
L9626:
 ldx #$00
 jsr bank7_XY_Movements_Routine
 sta Player_X_Scroll
L962D:
RTS
bank7_applyGravityMotion:
 ldy #$00
 lda Z2NativeVY,x
 jpl LD1A3
DEY
LD1A3:
 sty $07
CLC
 adc Player_Y_Position,x
 sta Player_Y_Position,x
 lda Player_Y_HighPos,x
 adc $07
 sta Player_Y_HighPos,x
 lda Z2NativeGravityFraction,x
CLC
 adc $00
 sta Z2NativeGravityFraction,x
 lda Z2NativeVY,x
 adc #$00
 sta Z2NativeVY,x
 cmp $02
 jne LD1CD
 sta Z2NativeVY,x
 lda #$00
 sta Z2NativeGravityFraction,x
LD1CD:
RTS
bank7_XY_Movements_Routine:
 lda Z2NativeVX,x
ASL
ASL
ASL
ASL
 sta $01
 lda Z2NativeVX,x
LSR
LSR
LSR
LSR
 cmp #$08
 jcc LD1E2
 ora #$F0
LD1E2:
 sta $00
 ldy #$00
 cmp #$00
 jpl LD1EB
DEY
LD1EB:
 sty $02
 lda Z2NativeXFraction,x
CLC
 adc $01
 sta Z2NativeXFraction,x
 lda #$00
ROL
PHA
ROR
 lda Player_X_Position,x
 adc $00
 sta Player_X_Position,x
 lda Player_PageLoc,x
 adc $02
 sta Player_PageLoc,x
 jmp LD247
LD20A:
 lda Z2NativeVY,x
ASL
ASL
ASL
ASL
 sta $01
 lda Z2NativeVY,x
LSR
LSR
LSR
LSR
 cmp #$08
 jcc LD220
 ora #$F0
LD220:
 sta $00
 ldy #$00
 cmp #$00
 jpl LD229
DEY
LD229:
 sty $02
 lda Z2NativeGravityFraction,x
CLC
 adc $01
 sta Z2NativeGravityFraction,x
 lda #$00
ROL
PHA
ROR
 lda a:Player_Y_Position,x
 adc $00
 sta a:Player_Y_Position,x
 lda Player_Y_HighPos,x
 adc $02
 sta Player_Y_HighPos,x
LD247:
PLA
CLC
 adc $00
RTS
.endscope
.popseg
