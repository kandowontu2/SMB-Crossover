.pushseg
.segment "TMNT_CORE"
.proc TnDrawEquipment
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda MmDeathFlag
 jne Done
 ; Same publication stores/order as X5SetSpecialChr, without a bank trip.
 lda #.lobyte(628)
 sta SsChrPhysical
 lda #.hibyte(628)
 sta X5SpecialChrUpper
 lda #1
 sta SsChrActive
 sta X5WideChrActive
 sta ReloadCHRBank
 BankPRGC #.bank(TnWorldArtStart)
 ; Inactive slots cannot produce source sprites. Retain the old ammo HUD
 ; path and its final scratch slot even when there is nothing to scan.
 lda TnGearSelected
 ora TnShotKind
 ora TnShotKind+1
 ora TnShotKind+2
 ora TnDropKind
 ora TnDropKind+1
 ora TnDropKind+2
 ora TnDropKind+3
 ora TnPickupStamp
 ora TnPickupStamp+1
 ora TnPickupStamp+2
 ora TnPickupStamp+3
 ora TnPickupStamp+4
 ora TnPickupStamp+5
 bne RenderActors
 lda #0
 sta TnDrawSlot
 ldx #$ff
 jmp Ammo
RenderActors:
 ldx #2
Shot:stx TnDrawSlot
 lda TnShotKind,x
 jeq NextShot
 lda TnShotAnim,x
 jeq NextShot
ShotPointer:
 ldy TnShotFace,x
 jsr TnWorldPointer
 ldx TnDrawSlot
 lda TnShotX,x
 sta R4
 lda TnShotPage,x
 sta R5
 jsr TnWorldScreenX
 lda TnShotY,x
 sta R6
 lda #1
 sta R7
 lda #0
 sta R3
 jsr TnWorldDraw
NextShot:
.if ::MAPPER_MMC5
 jmp ::TnSkipEmptyEquipmentScans
 .res 3,$ea
.else
 ldx TnDrawSlot
 dex
 jpl Shot
.endif
::TnEquipmentScansResume:
 ldx #3
Drop:stx TnDrawSlot
 lda TnDropKind,x
 beq NextDrop
 clc
 adc #79
 ldy #1
 jsr TnWorldPointer
 ldx TnDrawSlot
 lda TnDropX,x
 sta R4
 lda TnDropPage,x
 sta R5
 jsr TnWorldScreenX
 lda TnDropY,x
 sta R6
 lda #1
 sta R7
 lda #0
 sta R3
 jsr TnWorldDraw
NextDrop:ldx TnDrawSlot
 dex
 bpl Drop
 ldx #5
Pickup:stx TnDrawSlot
 lda Enemy_Flag,x
 beq NextPickup
 jsr TnPrivatePickup
 bcc NextPickup
 lda Enemy_State,x
 bmi Visible
 cmp #2
 bcc NextPickup
Visible:
 lda #83
 ldy #1
 jsr TnWorldPointer
 ldx TnDrawSlot
 lda Enemy_X_Position,x
 clc
 adc #8
 sta R4
 lda Enemy_PageLoc,x
 adc #0
 sta R5
 jsr TnWorldScreenX
 lda Enemy_Y_Position,x
 clc
 adc #16
 sta R6
 lda Enemy_Y_HighPos,x
 adc #0
 sta R7
 lda Enemy_SprAttrib,x
 and #$20
 sta R3
 jsr TnWorldDraw
NextPickup:ldx TnDrawSlot
 dex
 bpl Pickup
::TnEquipmentIconResume:
 ; An icon and three background digits are visible only while secondary is active.
 ; Existing four health sprites + at most four icon parts fit eight HUD sprites.
 lda TnGearSelected
 beq Ammo
 ldx TnVariant
 lda TnEquipment,x
 beq Ammo
 clc
 adc #79
 ldy #1
 jsr TnWorldPointer
 lda #128
 sta R4
 lda #0
 sta R5
 sta R3
 lda #23
 sta R6
 lda #1
 sta R7
 jsr TnWorldDraw
Ammo:jsr TnAmmoHud
Done:rts
.endproc
.proc TnWorldPointer
 tax
 cpy #2
 beq Left
 lda TnWorldRLo,x
 sta R0
 lda TnWorldRHi,x
 sta R1
 rts
Left:lda TnWorldLLo,x
 sta R0
 lda TnWorldLHi,x
 sta R1
 rts
.endproc
.proc TnWorldScreenX
 sec
 lda R4
 sbc ScreenLeft_X_Pos
 sta R4
 lda R5
 sbc ScreenLeft_PageLoc
 sta R5
 rts
.endproc
.proc TnWorldDraw
 ; Keep every pre-existing linked address stable; skip the unused call padding.
CallStart:
 jsr TnFastWorldRender
 jmp CallEnd
 .res 12,$ea
CallEnd:
 .assert CallEnd-CallStart=18,error,"Preserve original farcall footprint"
 BankPRGC #.bank(TnWorldArtStart)
 rts
.endproc
.proc TnAmmoHud
 lda #0
 sta TnTemp
 sta TnTemp2
 lda TnGearSelected
 beq Compare
 ldx TnVariant
 lda TnEquipment,x
 beq Compare
 lda #1
 sta TnTemp
 lda TnAmmo,x
 sta TnTemp2
Compare:
 lda TnTemp
 cmp TnHudSelected
 bne Dirty
 lda TnTemp2
 cmp TnHudAmmo
 beq Done
Dirty:
 ldx VRAM_Buffer1_Offset
 cpx #78                      ;6-byte append + terminator in native84-byte queue.
 bcs Done
 lda #$20
 sta VRAM_Buffer1,x
 lda #$31                     ;top empty HUD row8, cols17/18 (above WORLD).
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 lda #$24
 sta VRAM_Buffer1+3,x
 sta VRAM_Buffer1+4,x
 sta VRAM_Buffer1+5,x
 lda TnTemp
 beq Commit
 lda #0
 sta TnTempX
 sta TnTempY
 lda TnTemp2
Hundreds:cmp #100
 bcc Divide
 sec
 sbc #100
 inc TnTempX
 bne Hundreds
Divide:cmp #10
 bcc Digits
 sec
 sbc #10
 inc TnTempY
 bne Divide
Digits:
 sta VRAM_Buffer1+5,x
 lda TnTempY
 sta VRAM_Buffer1+4,x
 lda TnTempX
 bne StoreHundreds
 lda #$24
StoreHundreds:sta VRAM_Buffer1+3,x
Commit:
 txa
 clc
 adc #6
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 lda TnTemp
 sta TnHudSelected
 lda TnTemp2
 sta TnHudAmmo
Done:rts
.endproc
.popseg
