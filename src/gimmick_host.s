; Authenticated source integration plus explicit SMB terrain/coordinate adapter.
.pushseg
.segment "GIMMICK_MOVE"
.proc GmIntegrate
 ; Native movement-class jump table31:F65C. The host supplies only actual
 ; ordinary empty1/solid2 classes; original3..7 arithmetic remains callable.
 lda GmRam035A,x
 and #7
 asl
 tay
 lda Table,y
 sta R0
 lda Table+1,y
 sta R1
 jsr Jump
 jmp GmResolveTerrain
Jump:jmp (R0)
Table:.word GmN31_F6F3,GmN31_F6F3,GmN31_F689,GmN31_F670
 .word GmN31_F67E,GmN31_F6CD,GmN31_F6DB,GmN31_F6A5
.endproc
.proc GmSpawnEffectBody
 ; Native type1/type2 B4 producer. Seven owned noninteractive effects.
 ; Packed X16/Y12/age4 preserves every renderer-consumed source bit; full
 ; source Y high nibble is not rendered. Newly born index is a Main-local
 ; witness so age0 can receive its genuine first update after allocation.
 lda GmClock
 and #1
 bne Odd
 ldy #0
Find:lda GmEffects+3,y
 and #$f0
 beq Found
 tya
 clc
 adc #4
 tay
 cpy #28
 bne Find
 ldy #9
 lda #1
 cpy #9
 rts
Found:sty GmSpawnIndex
 lda GmClock
 lsr
 and #7
 tax
 lda GmRam009B
 clc
 adc EffectYLo,x
 sta GmEffects+2,y
 lda GmRam00A5
 adc EffectYHi,x
 and #$0f
 sta GmEffects+3,y
 lda GmRam00AF
 clc
 adc EffectXLo,x
 sta GmEffects,y
 lda GmRam00B9
 adc EffectXHi,x
 sta GmEffects+1,y
 php
 tya
 lsr
 lsr
 clc
 adc #2
 tay
 plp
 lda #0
Odd:rts
EffectYLo:.byte $70,$c0,$20,$80,$a0,$f0,$90,$30
EffectYHi:.byte $ff,$fe,$fe,$ff,$fe,$ff,$ff,$fe
EffectXLo:.byte $90,$90,$c0,$b0,$60,$50,$20,$c0
EffectXHi:.byte 0,$ff,0,$ff,0,0,$ff,$ff
.endproc
.proc GmEffectsTick
 ldx #0
Next:lda GmEffects+3,x
 and #$f0
 bne Age
 cpx GmSpawnIndex
 bne Skip
Age:lda GmEffects+3,x
 clc
 adc #$10
 sta GmEffects+3,x
 and #$f0
 beq Skip
 ; Native16:89FF cull, with the same disclosed SMB240-row and long-world
 ; camera projection as star retirement. Zero-velocity B4s do not collide.
 lda GmEffects+3,x
 and #15
 beq Cull
 cmp #15
 bcs Cull
 lda ScreenLeft_X_Pos
 .repeat 4
 lsr
 .endrepeat
 sta GmTemp
 lda ScreenLeft_PageLoc
 .repeat 4
 asl
 .endrepeat
 ora GmTemp
 sta GmTemp
 lda GmEffects+1,x
 sec
 sbc GmTemp
 cmp #$13
 bpl Cull
 cmp #$fc
 bpl Skip
Cull:lda GmEffects+3,x
 and #15
 sta GmEffects+3,x
Skip:txa
 clc
 adc #4
 tax
 cpx #28
 bne Next
 lda #$ff
 sta GmSpawnIndex
 rts
.endproc
.proc GmReadPoint
 ; X is0hero/1star, source16.4 point; sourceY=feet. Real SMB block memory.
 ; Input source fractional point in R2/R3(X),R4/R5(Y); outputs Ametatile,
 ; carry solid. No synthetic original room RAM, no repeated movement.
 ; R2/R3 are PIXEL X low/page by this boundary; caller did source conversion.
 lda R2
 .repeat 4
 lsr
 .endrepeat
 sta R0
 lda R3
 and #1
 .repeat 4
 asl
 .endrepeat
 ora R0
 sta R0
 jsr GetBlockBufferAddr
 lda R5
 bne Empty                    ; Outside active host vertical page.
 lda R4
 cmp #32
 bcc Empty
 cmp #240
 bcs Empty
 and #$f0
 sec
 sbc #32
 tay
 lda (R6),y
 sta GmTemp
 beq Empty
 cmp #$23
 beq Empty
 cmp #$26
 beq Empty
 cmp #$c2
 beq Empty
 cmp #$c3
 beq Empty
 cmp #$5f
 beq Empty
 cmp #$60
 beq Empty
 tay
 lda MTileAttribute,y
 and #MTILE_SOLID
 beq Empty
 lda GmTemp
 sec
 rts
Empty:lda #0
 clc
 rts
.endproc
.proc GmPointPixels
 ; Convert current source X16/Y16 at slotX into full world pixel coordinates.
 lda GmRam00AE,x
 sta R2
 lda GmRam00B8,x
 sta R3
 lda GmRam009A,x
 sta R4
 lda GmRam00A4,x
 sta R5
 .repeat 4
 lsr R3
 ror R2
 lsr R5
 ror R4
 .endrepeat
 rts
.endproc
.proc GmResolveTerrain
 ; Genuine 1/16 motion is complete before host tile collision. A floor/ceiling
 ; clamps fractional Y and clears only native vertical speed; side clamps X.
 ; Point geometry is native hero halfwidth3,height14; star uses launch tables.
 ; Player terrain is the genuine native coin/brick/pipe/platform consumer,
 ; using GmAdder/Head/Foot/Side and followed by GmSync. Do not clear source
 ; upward speed before that real head-bump consumer can see it. Star owns
 ; this actual block-map bounce callback; it is not generic player physics.
 cpx #0
 bne Star
 lda #0
 sta GmRam036E
 lda #1
 sta GmRam035A
 rts
Star:stx GmTickSlot
 lda #0
 sta GmRam036E,x
 lda GmRam00C2,x
 bmi Up
 jsr GmPointPixels
 jsr GmReadPoint
 bcc Sides
 ldx GmTickSlot
 lda R4
 and #$f0
 sta R4
 lda #0
 sta GmRam009A,x
 lda R4
 .repeat 4
 asl
 .endrepeat
 sta GmRam009A,x
 lda R4
 .repeat 4
 lsr
 .endrepeat
 sta GmRam00A4,x
 lda #0
 sta GmRam00C2,x
 lda #$80
 sta GmRam036E,x
 lda #2
 sta GmRam035A,x
 bne Sides
Up:jsr GmPointPixels
 lda R4
 sec
 sbc #14
 sta R4
 lda R5
 sbc #0
 sta R5
 jsr GmReadPoint
 bcc Sides
 ldx GmTickSlot
 lda GmOldY
 sta GmRam009A,x
 lda GmOldY+1
 sta GmRam00A4,x
 lda #0
 sta GmRam00C2,x
Sides:
 ldx GmTickSlot
 lda GmRam036E,x
 bmi ClassDone
 lda #1
 sta GmRam035A,x
ClassDone:
 lda #0
 cpx #0
 beq :+
 sta GmRam0379
:lda GmRam00CC,x
 beq Done
 jsr GmPointPixels
 lda R4
 sec
 sbc #7
 sta R4
 lda R5
 sbc #0
 sta R5
 lda GmRam00CC,x
 bmi Left
 lda R2
 clc
 adc #3
 sta R2
 bcc Probe
 inc R3
 bne Probe
Left:lda R2
 sec
 sbc #3
 sta R2
 bcs Probe
 dec R3
Probe:jsr GmReadPoint
 bcc Done
 ldx GmTickSlot
 lda GmOldX
 sta GmRam00AE,x
 lda GmOldX+1
 sta GmRam00B8,x
 lda #0
 sta GmRam00CC,x
 cpx #0
 beq Done
 lda #$80
 sta GmRam0379
Done:ldx GmTickSlot
 rts
.endproc
.export GmIntegrate,GmSpawnEffectBody,GmEffectsTick,GmResolveTerrain
.proc GmMovement
 ; Root's wrapper skips generic physics, calls this once, retains native
 ; BG/coins/pipes/platforms with Gm probes, then calls GmAfterTerrain once.
 ; Camera remains genuine/once. No source clock is advanced from either.
 php
 pha
 lda #0
 beq GmFrameCommon
.endproc
.proc GmAfterTerrain
 php
 pha
 lda #1
 ; fall through to shared wrapper, preserving entry A and P above phase.
.endproc
GmFrameCommon:
 pha                          ; phase0 before native BG, phase1 after it.
 txa
 pha
 tya
 pha
 lda SelectedCharacter
 cmp #CHARACTER_GIMMICK
 jne GmFrameDone
 GmSaveScratch
 GmFar GmEnsure,75
 lda GamePauseStatus
 and #1
 bne GmFrameRestore
 lda GameEngineSubroutine
 cmp #8
 bne GmFrameRestore
 lda TimerControl
 bne GmFrameRestore
 tsx
 lda $0111,x                  ;14 saved scratch +Y/X +phase, real stack.
 bne Late
 jsr GmImport
 GmFar GmN30_8000,24
 jsr GmExport
 jmp GmFrameRestore
Late:
 jsr GmSync
 jsr GmRideStar
 jsr GmExportMotion
 lda #$ff
 sta GmSpawnIndex
 GmFar GmKernelStar,24
 jsr GmEffectsTick
GmFrameRestore:GmRestoreScratch
GmFrameDone:pla
 tay
 pla
 tax
 pla
 pla                          ; discard phase, then restore original entryA.
 plp
 rts
.proc GmImport
 ; Native source X=center, Y=feet. SMB actor X/Y remain its 16x32 anchor.
 lda Player_X_Position
 clc
 adc #8
 sta R0
 lda Player_PageLoc
 adc #0
 sta R1
 lda R0
 .repeat 4
 asl
 .endrepeat
 sta R2
 lda GmRam00AE
 and #15
 ora R2
 sta GmRam00AE
 lda R0
 .repeat 4
 lsr
 .endrepeat
 sta R2
 lda R1
 .repeat 4
 asl
 .endrepeat
 ora R2
 sta GmRam00B8
 lda Player_Y_Position
 clc
 adc #32
 sta R0
 lda Player_Y_HighPos
 adc #$ff
 sta R1
 lda R0
 .repeat 4
 asl
 .endrepeat
 sta R2
 lda GmRam009A
 and #15
 ora R2
 sta GmRam009A
 lda R0
 .repeat 4
 lsr
 .endrepeat
 sta R2
 lda R1
 .repeat 4
 asl
 .endrepeat
 ora R2
 sta GmRam00A4
 rts
.endproc
.proc GmExport
 ldx #0
 jsr GmPointPixels
 lda R2
 sec
 sbc #8
 sta R0
 sec
 sbc Player_X_Position
 sta Player_X_Scroll
 lda R0
 sta Player_X_Position
 lda R2
 cmp #8
 lda R3
 sbc #0
 sta Player_PageLoc
 lda R4
 sec
 sbc #32
 sta Player_Y_Position
 lda R5
 sbc #0
 clc
 adc #1
 sta Player_Y_HighPos
::GmExportMotion:
 lda GmRam00CC
 sta Player_X_Speed
 bpl Positive
 eor #$ff
 clc
 adc #1
Positive:sta Player_XSpeedAbsolute
 lda GmRam00C2
 cmp #$80
 ror
 .repeat 3
 cmp #$80
 ror
 .endrepeat
 sta Player_Y_Speed
 lda #0
 sta PlayerSize
 sta PlayerStatus
 lda GmRam036E
 bmi Ground
 lda #1
 ldx GmRam00C2
 bmi State
 lda #2
 bne State
Ground:lda #0
State:sta Player_State
 lda #1
 ldx GmRam030A
 bne Facing
 lda #2
Facing:sta PlayerFacingDir
 rts
.endproc
.proc GmRideStar
 ; Exact31:FF13 support geometry for actual slot1; only native D7bit40
 ; supports. No invented X carry: original30:8369 applies extra friction.
 lda GmRam00C2
 bmi No
 lda GmRam00D7
 and #$40
 beq No
 lda GmRam009B
 sec
 sbc GmRam0315
 sta R0
 lda GmRam00A5
 sbc GmRam031F
 sta R1
 lda GmRam009A
 sec
 sbc R0
 sta R2
 lda GmRam00A4
 sbc R1
 bne No
 lda R2
 bmi No
 lda GmRam00AE
 sec
 sbc GmRam00AF
 sta R2
 lda GmRam00B8
 sbc GmRam00B9
 sta R3
 lda GmRam0329
 clc
 adc #$30                    ; Genuine initialized hero halfwidth3px.
 sta R4
 lda GmRam0333
 adc #0
 sta R5
 lda R3
 bmi Left
 lda R2
 cmp R4
 lda R3
 sbc R5
 bmi Yes
No:rts
Left:lda R2
 clc
 adc R4
 lda R3
 adc R5
 bmi No
Yes:
 ; Original8369..8387 does NOT snap Y. FF13 accepts up to127fraction
 ; penetration, then applies only friction/VY0/ground80. Keep that real arc.
 lda GmRam00CC
 bmi Negative
 sec
 sbc #1
 bpl Speed
 jmp Zero
Negative:clc
 adc #1
 bmi Speed
Zero:lda #0
Speed:sta GmRam00CC
 lda #0
 sta GmRam00C2
 lda #$80
 sta GmRam036E
 rts
.endproc
.export GmMovement,GmAfterTerrain,GmImport,GmExport,GmExportMotion,GmRideStar
.proc GmRetireStar
 ; Original29:84FD..8522 retirement consumer, with explicit SMB viewport
 ; adaptation:240px bottom and world camera-relative range[-48,288), rather
 ; than original room-local signed X. No retirement of source scripted states.
 lda GmRam0091
 bmi Done
 lda GmRam00A5
 and #15
 cmp #15
 bcs Retire
 ldx #1
 jsr GmPointPixels
 lda R2
 sec
 sbc ScreenLeft_X_Pos
 sta R2
 lda R3
 sbc ScreenLeft_PageLoc
 beq Done
 cmp #$ff
 beq Left
 cmp #1
 bne Retire
 lda R2
 cmp #32
 bcc Done
 bcs Retire
Left:lda R2
 cmp #$d0
 bcs Done
Retire:lda #0
 sta GmRam0091
 sta GmRam00D7
 sta GmRam0351
Done:rts
.endproc
.export GmRetireStar
.proc GmSync
 ; After genuine native BG/coin/pipe/platform consumers, synchronize their
 ; clamp/carry receipts back into source positions; never integrate twice.
 lda SelectedCharacter
 cmp #CHARACTER_GIMMICK
 bne Done
 jsr GmImport
 lda Player_X_Speed
 sta GmRam00CC
 lda Player_State
 beq Land
 lda #0
 sta GmRam036E
 lda Player_Y_Speed
 bmi Done
 lda GmRam00C2
 bpl Done
 lda #0                       ; Real head consumer accepted ceiling clamp.
 sta GmRam00C2
 beq Done
Land:lda #$80
 sta GmRam036E
 lda #2
 sta GmRam035A
 lda #0
 sta GmRam00C2
 lda GmRam009A
 and #$f0
 sta GmRam009A
Done:rts
.endproc
.proc GmAdder
 ; Use existing native base0 while own probes supply all7 exact geometry
 ; points; root must intercept ALL head/feet/sides for raw26, not just head.
 ldy #0
 sec
 rts
.endproc
.segment "GIMMICK_CORE"
.proc GmHead
 lda #0
 jmp GmBodyProbe
.endproc
.proc GmFoot
 iny
 lda #0
 jmp GmBodyProbe
.endproc
.proc GmSide
 lda #1
 ; fall through
.endproc
.proc GmBodyProbe
 ; Literal BlockBufferCollision return contract: A/Z=actual raw metatile,
 ; R2 native row,R3 tile,R4 original actor-coordinate low nibble,R5 probeX,
 ; R6/7 actual block pointer,Y same probe index,X0. R0/1 remain live unchanged.
 pha
 lda SelectedCharacter
 cmp #CHARACTER_GIMMICK
 beq Owned
 pla
 clc
 rts
Owned:
 tya
 pha
 lda Player_X_Position
 clc
 adc XAdd,y
 sta R5
 lda Player_PageLoc
 adc #0
 and #1
 tay
 lda #>Block_Buffer_1
 sta R7
 lda R5
 .repeat 4
 lsr
 .endrepeat
 clc
 adc BlockBufferAddr,y
 sta R6
 pla
 tay
 lda Player_Y_Position
 clc
 adc YAdd,y
 and #$f0
 sec
 sbc #32
 sta R2
 sty GmTemp2
 tay
 lda (R6),y
 sta R3
 ldy GmTemp2
 pla
 bne Horizontal
 lda Player_Y_Position
 jmp Fraction
Horizontal:lda Player_X_Position
Fraction:and #15
 sta R4
 ldx #0
 lda R3
 rts
XAdd:.byte 8,5,11,5,5,11,11
YAdd:.byte 18,32,32,22,30,22,30
.endproc
.segment "GIMMICK_MOVE"
.proc GmBox
 ; Host contact body matches actual terrain extent3px/14px, rooted at feet.
 ; Original source asymmetric contact-side test must still own GmInjury.
 lda SelectedCharacter
 cmp #CHARACTER_GIMMICK
 bne Done
 lda Player_Rel_XPos
 clc
 adc #5
 sta BoundingBox_UL_Corner
 clc
 adc #6
 sta BoundingBox_LR_Corner
 lda Player_Y_Position
 clc
 adc #18
 sta BoundingBox_UL_Corner+1
 clc
 adc #14
 sta BoundingBox_LR_Corner+1
Done:
 rts
.endproc
.proc GmHealth
 lda SelectedCharacter
 cmp #CHARACTER_GIMMICK
 bne No
 lda GmRam0346
 ldx GmRam002B
 sec
 rts
No:clc
 rts
.endproc
.proc GmDeathStart
 lda SelectedCharacter
 cmp #CHARACTER_GIMMICK
 bne Done
 lda #$d0
 sta GmRam0090
 lda #$15
 sta GmRam0300
 ; Native SMB death/life/pipe transition is an explicit host adaptation.
 jmp KillPlayer
Done:rts
.endproc
.proc GmFullPower
 ; Existing user cheat endpoint only, never the new-game constructor or a
 ; native test fixture. No source claim that Ice/Gimmick offered this cheat.
 lda SelectedCharacter
 cmp #CHARACTER_GIMMICK
 bne Done
 GmFar GmEnsure,75
 bcc Done
 lda #4
 sta GmRam002B
 sta GmRam0346
 lda #2
 sta GmRam0036
 sta GmRam0038
 lda #3
 sta GmRam0037
 sta GmRam0039
Done:
 rts
.endproc
.proc GmWeapons
 ; Collision only: source star tick ALREADY ran exactly once in Movement.
 ; Existing NPC damage consumer maps one original HP to100 host HP, including
 ; host immunity/flash/score behavior. It does not substitute projectile motion.
 php
 pha
 txa
 pha
 tya
 pha
 lda SelectedCharacter
 cmp #CHARACTER_GIMMICK
 jne Done
 lda GmRam0091
 cmp #1
 beq Active
 cmp #$d0
 jne Done
 lda GmRam0351
 cmp #2
 jne Done
Active:GmSaveScratch
 .repeat 8,I
 lda BoundingBox_UL_Corner+28+I
 pha
 .endrepeat
 .repeat 6,I
 .if I=0
 lda MmSlot
 .elseif I=1
 lda MmEnemySlot
 .elseif I=2
 lda SmSlot
 .elseif I=3
 lda SmBombHits
 .elseif I=4
 lda MmBulletType
 .else
 lda ObjectOffset
 .endif
 pha
 .endrepeat
 ldx #1
 GmFar GmScreenPoint,24
 ; Convert native star extents from16.4 to pixel radii.
 lda GmRam0329
 .repeat 4
 lsr
 .endrepeat
 sta R0
 lda GmRam0333
 .repeat 4
 asl
 .endrepeat
 ora R0
 sta R0
 lda GmRam0315
 .repeat 4
 lsr
 .endrepeat
 sta R1
 lda GmRam031F
 .repeat 4
 asl
 .endrepeat
 ora R1
 sta R1
 lda R4
 sec
 sbc R0
 sta R2
 lda R5
 sbc #0
 beq LeftVisible
 cmp #$ff
 jne Restore
 lda #0
 sta R2
LeftVisible:lda R2
 sta BoundingBox_UL_Corner+28
 lda R4
 clc
 adc R0
 sta R2
 lda R5
 adc #0
 beq RightVisible
 cmp #1
 jne Restore
 lda #$ff
 sta R2
RightVisible:lda R2
 sta BoundingBox_LR_Corner+28
 lda R6
 sec
 sbc R1
 sta BoundingBox_UL_Corner+29
 lda R6
 sta BoundingBox_LR_Corner+29
 lda #0
 sta MmSlot
 sta SmSlot
 sta SmBombHits
 lda #10                      ; Genuine native100damage, piercing consumer.
 sta MmBulletType
 GmFar BeginEnemyLoop,8
 lda SmBombHits
 beq Restore
 lda GmRam0351
 cmp #2
 bne Restore
 lda GmRam0091
 cmp #1
 bne Restore
 lda #$d0                     ; Exact source ApplyStarHitAndReward transition.
 sta GmRam0091
 lda #0
 sta GmRam038D
Restore:
 pla
 sta ObjectOffset
 pla
 sta MmBulletType
 pla
 sta SmBombHits
 pla
 sta SmSlot
 pla
 sta MmEnemySlot
 pla
 sta MmSlot
 .repeat 8,I
 pla
 sta BoundingBox_UL_Corner+35-I
 .endrepeat
 GmRestoreScratch
Done:pla
 tay
 pla
 tax
 pla
 plp
 rts
.endproc
.export GmSync,GmAdder,GmHead,GmFoot,GmSide,GmBodyProbe,GmBox,GmHealth,GmDeathStart,GmFullPower
.export GmWeapons
.popseg
