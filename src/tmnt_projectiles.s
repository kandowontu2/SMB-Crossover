; Three original concurrent secondary actors; four private physical drop actors.
.pushseg
.segment "TMNT_COMBAT"
.proc TnAllWeapons
 jsr TnWeapons                 ; Existing primary implementation remains exact.
 lda TimerControl
 jne Done
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda MmDeathFlag
 jne Done
 lda TnUpdateTick
 jeq Done
 lda TnTickValid
 beq Tick
 lda FrameCounter
 cmp TnTickFrame
 jeq Done
Tick:lda #1
 sta TnTickValid
 lda FrameCounter
 sta TnTickFrame
 ldx #5
Receipts:
 lda Enemy_Flag,x
 beq Clear
 lda Enemy_State,x
 and #$20
 bne NextReceipt
 lda Enemy_ID,x
 cmp #Goomba
 bne Clear
 lda Enemy_State,x
 cmp #2
 bcs NextReceipt
Clear:lda #0
 sta TnDropReceipt,x
NextReceipt:dex
 bpl Receipts
 ldx #2
Shots:stx TnSlot
 lda TnShotKind,x
 beq Next
 jsr TnUpdateShot
 ldx TnSlot
 lda TnShotKind,x
 beq Next
 jsr TnShotEnemies
Next:ldx TnSlot
 dex
 bpl Shots
 jsr TnUpdateDrops
Done:rts
.endproc
.proc TnUpdateShot
 inc TnShotAge,x
 jsr TnAdvanceShotAnimation
 lda TnShotKind,x
 cmp #3
 bne Integrate
 ; Original $FD9F signed40/256 drag reverses the boomerang smoothly.
 lda TnShotFace,x
 cmp #2
 beq DragLeft
 sec
 lda TnShotVXLo,x
 sbc #40
 sta TnShotVXLo,x
 lda TnShotVX,x
 sbc #0
 sta TnShotVX,x
 jmp Catch
DragLeft:clc
 lda TnShotVXLo,x
 adc #40
 sta TnShotVXLo,x
 lda TnShotVX,x
 adc #0
 sta TnShotVX,x
Catch:
 lda TnShotAge,x
 cmp #11
 bcc Integrate
 lda TnShotX,x
 sta TnTempX
 lda TnShotPage,x
 sta TnTempPage
 lda TnShotY,x
 sta TnTempY
 lda #11
 sta TnRadiusX
 lda #23
 sta TnRadiusY
 jsr TnNearPlayer
 bcc Integrate
 ldx TnSlot
 lda #0
 sta TnShotKind,x
 farcall TnRestoreBoomerang
 rts
Integrate:
 clc
 lda TnShotFrac,x
 adc TnShotVXLo,x
 sta TnShotFrac,x
 lda TnShotX,x
 adc TnShotVX,x
 sta TnShotX,x
 lda #0
 ldy TnShotVX,x
 bpl Sign
 lda #$ff
Sign:adc TnShotPage,x
 sta TnShotPage,x
 clc
 lda TnShotY,x
 adc TnShotVY,x
 sta TnShotY,x
 cmp #32
 jcc Kill
 cmp #240
 jcs Kill
 ; Host-camera clipping is a scene adaptation to SMB's viewport.
 sec
 lda TnShotX,x
 sbc ScreenLeft_X_Pos
 sta TnTemp
 lda TnShotPage,x
 sbc ScreenLeft_PageLoc
 jne Kill
 lda TnTemp
 cmp #7
 jcc Kill
 cmp #246
 jcs Kill
 lda TnShotKind,x
 cmp #3
 beq Done
Terrain:
 lda TnShotX,x
 sta TnQueryX
 lda TnShotPage,x
 sta TnQueryPage
 lda TnShotY,x
 jsr TnReadCell
 tay
 lda MTileAttribute,y
 and #MTILE_SOLID|MTILE_CLIMB
 cmp #MTILE_SOLID
 beq Kill
Done:rts
Kill:ldx TnSlot
 lda #0
 sta TnShotKind,x
 rts
.endproc
; Original bank6 $8010 animation semantics: FE resets phase while retaining
; the last pose for this update. Initial timer3, subsequent duration2.
.proc TnAdvanceShotAnimation
 dec TnShotTimer,x
 bne Fetch
 lda #2
 sta TnShotTimer,x
 inc TnShotPhase,x
Fetch:
 lda TnShotKind,x
 cmp #4
 beq Kiai
 ldy TnShotPhase,x
 cpy #4
 bcs Restart
 cmp #3
 beq Boom
 tya
 clc
 adc #73
 bne Store
Boom:lda BoomPoses,y
 bne Store
Kiai:lda TnShotPhase,x
 bne Restart
 lda #72
Store:sta TnShotAnim,x
 rts
Restart:lda #0
 sta TnShotPhase,x
 rts
BoomPoses:.byte 60,61,63,62
.endproc
.proc TnShotEnemies
 ldx TnSlot
 lda TnShotX,x
 sta TnWeaponX
 lda TnShotPage,x
 sta TnWeaponPage
 lda TnShotY,x
 sta TnWeaponY
 ; Actual native secondary collision radii from PRG6 tables.
 lda TnShotKind,x
 sec
 sbc #1
 tay
 lda SecondaryRadiusX,y
 sta TnRadiusX
 lda SecondaryRadiusY,y
 sta TnRadiusY
 ; Source $9978 uses current selection/equipment even for in-flight actors.
 ; Last-ammo fallback and Select can therefore change an old shot's damage.
 ldy TnVariant
 lda TnGearSelected
 beq DamageIndex
 ldx TnVariant
 lda TnEquipment,x
 clc
 adc #3
 tay
DamageIndex:
 ldx TnVariant
 lda TnHealth,x
 cmp #64
 tya
 rol
 eor #1
 tay
 lda ContextDamage,y
 sta TnDamageNow
 ldx #5
Enemy:stx TnSavedSlot
 jsr TnEnemyEligible
 bcc Next
 lda TnEnemyHurt,x
 bne Next
 jsr TnOverlap
 bcc Next
 lda #24
 sta TnEnemyHurt,x
 lda #12
 sta MmEnemyFlash,x
 lda #Sfx_EnemySmack
 sta Square1SoundQueue
 lda TnEnemyHP,x
 sec
 sbc TnDamageNow
 bcc Defeat
 beq Defeat
 sta TnEnemyHP,x
 jmp Next
Defeat:
 lda ObjectOffset
 pha
 stx ObjectOffset
 lda Enemy_ID,x
 cmp #Bowser
 bne Ordinary
 lda #0
 sta TnDropCounter               ; mapped native boss defeat clears source counter
 lda #1
 sta BowserHitPoints
 stx R1
 jsr HandleEnemyFBallCol
 jmp Restore
Ordinary:jsr ShellOrBlockDefeat
Restore:pla
 sta ObjectOffset
 ldx TnSlot
 lda TnShotKind,x
 cmp #3
 bcs Next
 ; Original single/triple shuriken actors are consumed on a target kill;
 ; returning boomerangs and piercing Kiai actors continue.
 lda #0
 sta TnShotKind,x
 rts
Next:ldx TnSavedSlot
 dex
 bpl Enemy
 rts
ContextDamage:.byte 7,10,9,9,7,12,15,16,18,20,14,17,16,16,29,32
SecondaryRadiusX:.byte 4,4,5,6
SecondaryRadiusY:.byte 4,4,6,18
.endproc
; Input world point TnTempX/Page/Y. Inclusive radii implement native strict tests.
.proc TnNearPlayer
 lda Player_Y_HighPos
 cmp #1
 bne No
 clc
 lda Player_X_Position
 adc #8
 sta TnWeaponX
 lda Player_PageLoc
 adc #0
 sta TnWeaponPage
 sec
 lda TnTempX
 sbc TnWeaponX
 sta TnTemp
 lda TnTempPage
 sbc TnWeaponPage
 sta TnTemp2
 clc
 lda TnTemp
 adc TnRadiusX
 sta TnTemp
 lda TnTemp2
 adc #0
 bne No
 lda TnRadiusX
 asl
 cmp TnTemp
 bcc No
 lda Player_Y_Position
 clc
 adc #8
 sta TnWeaponY
 sec
 lda TnTempY
 sbc TnWeaponY
 clc
 adc TnRadiusY
 sta TnTemp
 lda TnRadiusY
 asl
 cmp TnTemp
 bcc No
 sec
 rts
No:clc
 rts
.endproc
.proc TnUpdateDrops
 ldx #3
Loop:stx TnSlot
 lda TnDropKind,x
 beq Next
 dec TnDropTimer,x
 beq Kill
 lda TnDropX,x
 sta TnTempX
 lda TnDropPage,x
 sta TnTempPage
 lda TnDropY,x
 sta TnTempY
 jsr TnDropOverlap
 bcc Next
 ldx TnSlot
 lda TnDropKind,x
 farcall TnGiveEquipment
Kill:ldx TnSlot
 lda #0
 sta TnDropKind,x
Next:ldx TnSlot
 dex
 bpl Loop
 rts
.endproc
; Native item bounds: centerX+-4, [anchorY-12,anchorY-2].
; Native player stand/roll/crouch source bounds match TnBoundingBoxGate.
.proc TnDropOverlap
 lda Player_Y_HighPos
 cmp #1
 bne No
 clc
 lda Player_X_Position
 adc #8
 sta TnWeaponX
 lda Player_PageLoc
 adc #0
 sta TnWeaponPage
 sec
 lda TnTempX
 sbc TnWeaponX
 sta TnTemp
 lda TnTempPage
 sbc TnWeaponPage
 sta TnTemp2
 clc
 lda TnTemp
 adc #9
 sta TnTemp
 lda TnTemp2
 adc #0
 bne No
 lda TnTemp
 cmp #18
 bcs No
 lda #$f8
 ldx #24
 ldy TnSeq
 cpy #$87
 bne Crouch
 lda #2
 ldx #14
 bne Store
Crouch:ldy RgCrouch
 beq Store
 lda #5
 ldx #27
Store:clc
 adc Player_Y_Position
 sta TnTemp
 lda TnTempY
 sec
 sbc #2
 cmp TnTemp
 bcc No
 txa
 clc
 adc Player_Y_Position
 sta TnTemp
 lda TnTempY
 sec
 sbc #12
 cmp TnTemp
 bcs No
 sec
 rts
No:clc
 rts
.endproc
.proc TnReadCell
 cmp #32
 bcc Empty
 cmp #240
 bcs Empty
 and #$f0
 sec
 sbc #32
 sta R2
 lda TnQueryPage
 and #1
 asl
 asl
 asl
 asl
 sta R0
 lda TnQueryX
 lsr
 lsr
 lsr
 lsr
 ora R0
 jsr GetBlockBufferAddr
 ldy R2
 lda (R6),y
 rts
Empty:lda #0
 rts
.endproc
.segment "TMNT_CORE"
.proc TnRestoreBoomerang
 ldx TnVariant
 lda TnEquipment,x
 bne Existing
 lda #3
 sta TnEquipment,x
 lda #1
 sta TnGearSelected
Existing:lda TnEquipment,x
 cmp #3
 bne Done
 inc TnAmmo,x                ; source $FDFE: refund one returned actor.
Done:rts
.endproc
.popseg
