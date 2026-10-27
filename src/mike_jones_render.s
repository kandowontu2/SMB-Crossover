; Fixed two1KB source art pages. Native enemy sprite windows2/3 stay unchanged.
.pushseg
.segment "MIKE_COMBAT"
.proc JnDraw
 BankPRGC #.bank(JnArtStart)
 lda #<(JN_FIRST_CHR+2)
 ldx #>(JN_FIRST_CHR+2)
 farcall X5SetSpecialChr
 lda #<(JN_FIRST_CHR+3)
 ldx #>(JN_FIRST_CHR+3)
 ldy #5
 farcall X5SetPhysicalChr
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda MmDeathFlag
 jne Done
 inc JnDrawFirst
 lda JnDrawFirst
 cmp #6
 bcc :+
 lda #0
 sta JnDrawFirst
:tax
 lda #6
 sta JnTemp2
Shots:
 stx JnSavedY
 lda JnShotKind,x
 jeq Next
 tay
 dey
 lda JnShotVX,x
 jne VelocityFacing
 lda PlayerFacingDir
 cmp #2
 jeq LeftFacing
 jmp FacingReady
VelocityFacing:
 jpl FacingReady
LeftFacing:
 tya
 clc
 adc #13
 tay
FacingReady:
 lda JnShotAge,x
 and #4
 jeq PhaseReady
 tya
 clc
 adc #26
 tay
PhaseReady:
 jmp JnBatSelectRecord
 .res 7,$ea
::JnBatRecordSelected:
 lda JnShotX,x
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda JnShotPage,x
 sbc ScreenLeft_PageLoc
 sta R5
 lda JnShotY,x
 sta R6
 jsr Draw
Next:
 dec JnTemp2
 jeq Items
 ldx JnSavedY
 inx
 cpx #6
 jcc Shots
 ldx #0
 jeq Shots
Items:
 ldx #5
World:
 stx JnSavedY
 jsr JnPrivatePickup
 jcc NextWorld
 lda Enemy_State,x
 jmi Visible
 cmp #2
 jcc NextWorld
Visible:
 lda #0
 sta EnemyMetasprite,x
 lda InvPickup,x
 and #$7f
 cmp #1
 jne NativeItem
 lda #<JnBigHeart
 sta R0
 lda #>JnBigHeart
 jmp ItemPtr
NativeItem:
 tay
 lda JnItemLo,y
 sta R0
 lda JnItemHi,y
ItemPtr:sta R1
 lda Enemy_X_Position,x
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda Enemy_PageLoc,x
 sbc ScreenLeft_PageLoc
 sta R5
 lda Enemy_Y_Position,x
 clc
 adc #8
 sta R6
 jsr Draw
NextWorld:ldx JnSavedY
 dex
 jpl World
 ldx #3
Drops:
 stx JnSavedY
 lda JnDropKind,x
 jeq NextDrop
 cmp #1
 jne Star
 lda #<JnHeart
 sta R0
 lda #>JnHeart
 jmp DropPtr
Star:lda #<JnStar
 sta R0
 lda #>JnStar
DropPtr:sta R1
 lda JnDropX,x
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda JnDropPage,x
 sbc ScreenLeft_PageLoc
 sta R5
 lda JnDropY,x
 sta R6
 jsr Draw
NextDrop:ldx JnSavedY
 dex
 jpl Drops
 jsr JnHud
Done:rts
Draw:
 lda #1
 sta R7
 lda #0
 sta R3
 farcall MetaspriteRenderLoop
 rts
.endproc
.proc JnHud
 lda JnUiDirty
 jeq Done
 lda VRAM_Buffer1_Offset
 jne Done
 lda #$20
 sta VRAM_Buffer1
 lda #$22
 sta VRAM_Buffer1+1
 lda #22
 sta VRAM_Buffer1+2
 ldx #21
Copy:lda Template,x
 sta VRAM_Buffer1+3,x
 dex
 jpl Copy
 lda JnHealth
 lsr
 jsr Decimal
 stx VRAM_Buffer1+6
 sta VRAM_Buffer1+7
 lda JnHealth
 and #1
 beq :+
 lda #5
:sta VRAM_Buffer1+9
 lda JnMaxHearts
 jsr Decimal
 stx VRAM_Buffer1+14
 sta VRAM_Buffer1+15
 lda JnSelected
 jeq Primary
 clc
 adc #3
 jmp Weapon
Primary:lda JnTier
Weapon:
 tax
 lda NameLo,x
 sta R0
 lda NameHi,x
 sta R1
 ldy #0
Name:lda (R0),y
 sta VRAM_Buffer1+17,y
 iny
 cpy #5
 jcc Name
 lda JnSelected
 jeq Infinite
 tax
 lda JnAmmo-1,x
 jsr Decimal
 stx VRAM_Buffer1+23
 sta VRAM_Buffer1+24
 jmp Finish
Infinite:lda #$28
 sta VRAM_Buffer1+23
 sta VRAM_Buffer1+24
Finish:
 lda #25
 sta VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1+25
 sta JnUiDirty
Done:rts
Decimal:
 ldx #0
Loop:cmp #10
 jcc End
 sec
 sbc #10
 inx
 jne Loop
End:rts
Template:.byte "HP 00.0 MAX00 YOYO  --"
NameLo:.byte <Empty,<Yoyo,<SStar,<Nova,<Bat,<Sling,<Fire,<Mirror,<Cross,<Bola,<Spikes,<Ball,<Laser,<Mega
NameHi:.byte >Empty,>Yoyo,>SStar,>Nova,>Bat,>Sling,>Fire,>Mirror,>Cross,>Bola,>Spikes,>Ball,>Laser,>Mega
Empty:.byte "     "
Yoyo:.byte "YOYO "
SStar:.byte "SSTAR"
Nova:.byte "NOVA "
Bat:.byte "BAT  "
Sling:.byte "SLING"
Fire:.byte "FIRE "
Mirror:.byte "MIROR"
Cross:.byte "CROSS"
Bola:.byte "BOLA "
Spikes:.byte "SPIKE"
Ball:.byte "BALL "
Laser:.byte "LASER"
Mega:.byte "MEGA "
.endproc

; Authenticated source interpreter:8 windup,8 damaging,3 recovery motion,
; 11 recovery hold; clear on tick30. ShotAge1 corresponds to source tick0.
; SMB reach/terrain and body-relative coordinates remain existing adaptations.
.proc JnBatBeginAttack
 lda #1
 sta JnAttack
 lda #0
 sta JnHitMask
 php
 pha
 lda JnWeapon
 cmp #4
 bne Normal
 pla
 plp
 jsr JnRelease
 jmp JnWeapons::Active
Normal:
 pla
 plp
 jmp JnWeapons::Active
.endproc
.proc JnBatReleaseIfDue
 php
 pha
 lda JnWeapon
 cmp #4
 beq AlreadyVisible
 pla
 plp
 jmp JnRelease
AlreadyVisible:
 pla
 plp
 rts
.endproc
.proc JnBatAttackLimit
 lda JnWeapon
 cmp #4
 bne Normal
 lda JnAttack
 cmp #33
 jmp JnBatAttackLimitContinue
Normal:
 lda JnAttack
 cmp #19
 jmp JnBatAttackLimitContinue
.endproc
.proc JnBatContactIfActive
 php
 pha
 lda JnShotKind,x
 cmp #4
 bne Normal
 lda JnShotAge,x
 cmp #9
 bcc Inactive
 cmp #17
 bcs Inactive
Normal:
 pla
 plp
 jmp JnShotEnemies
Inactive:
 pla
 plp
 rts
.endproc
.proc JnBatSelectRecord
 php
 lda JnShotKind,x
 cmp #4
 bne Legacy
 lda JnShotAge,x
 beq Legacy
 cmp #31
 bcs Legacy
 tya
 pha
 lda JnShotAge,x
 sec
 sbc #1
 tay
 lda JnShotVX,x
 bne Velocity
 lda PlayerFacingDir
 cmp #2
 beq Left
 bne Lookup
Velocity:
 bpl Lookup
Left:
 tya
 clc
 adc #30
 tay
Lookup:
 lda JnBatRecordLo,y
 sta R0
 lda JnBatRecordHi,y
 sta R1
 pla
 tay
 plp
 lda R1
 jmp JnBatRecordSelected
Legacy:
 plp
 lda JnShotAllLo,y
 sta R0
 lda JnShotAllHi,y
 sta R1
 jmp JnBatRecordSelected
.endproc

.popseg
