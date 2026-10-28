.if ::ENABLE_MMC5_EXPANDED
; Two 1-1 tier0 accommodations, genuine native platform25 engine.
; Owner81/82 intentionally selects native YMovingPlatform (not helper sine).
; HpCount remains0. Existing authored34-record cache/data are untouched.
.pushseg
.segment "CROSSOVER_HELPERS"
.assert * = $b134,lderror,"Expected exact00597 helper end"
.res 12,$ff
CmPlatformTwoStart:
.proc CmPlatformWeapons
 farcall CmWeapons
 ; Keep the complete original weapon return ABI/scratch and caller flags.
 php
 pha
 lda HpSupport
 cmp #$ce
 beq Manage
 lda CmTier
 ora WorldNumber
 ora LevelNumber
 bne RestoreA
 lda AreaType
 cmp #1
 bne RestoreA
 lda AreaAddrsLOffset
 cmp #5
 bne RestoreA
 lda ScreenLeft_PageLoc
 cmp #2
 beq Manage
 cmp #3
 beq Manage
 cmp #7
 beq Manage
 cmp #8
 bne RestoreA
Manage:
 phx
 phy
 .repeat 8,I
  lda R0+I
  pha
 .endrepeat
 lda ObjectOffset
 pha
 jsr CmPlatformTick
 pla
 sta ObjectOffset
 .repeat 8,I
  pla
  sta R0+7-I
 .endrepeat
 ply
 plx
RestoreA:
 pla
 plp
 rts
.endproc
.proc CmPlatformTick
 lda SelectedCharacter
 jne Done
 lda MarioVariant
 cmp #4
 jne Done
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda GamePauseStatus
 and #1
 jne Done
 lda TimerControl
 jne Done
 lda WorldNumber
 ora LevelNumber
 jne Outside
 jsr HpCurrentArea
 cmp #$25
 jne Outside
 ; The real area loader clears/configures this slab after clearing actors.
 lda HpValid
 jeq Done
 lda HpCount
 jne Done                       ; never borrow an authored/permanent cell
 lda HpArea
 cmp #$25
 jne Done
 lda HpCharacter
 jne Done
 lda HpKey
 jne Done
 lda HpMode
 cmp CrossoverBehaviorVersion
 jne Done
 lda #$ce
 sta HpSupport                  ; owner of cells0/1, not a global RAM claim
 lda #1
 sta HpLoop
Loop:
 ldx HpLoop
 lda CentersLo,x
 sta HpXLo,x
 lda CentersHi,x
 sta HpXHi,x
 jsr CmPlatformFind
 bcc Missing
 ; Do not delete a real supporting actor on the pickup update. Retirement
 ; happens only after native collision has reported no player on this actor.
 lda PlatformCollisionFlag,y
 bpl Next
 lda CmTier
 bne Retire
 jsr HpInSourceMargin
 bne Next
Retire:
 jsr CmPlatformRelease
 jmp Next
Missing:
 lda #0
 sta HpActorSlot,x              ; stale pointer never licenses actor erasure
 lda CmTier
 bne Next
 jsr HpInSourceMargin
 beq Next
 jsr CmPlatformSpawn
Next:
 dec HpLoop
 bpl Loop
 lda HpActorSlot
 ora HpActorSlot+1
 bne Done
 lda #0
 sta HpSupport
Done:rts
Outside:
 lda HpSupport
 cmp #$ce
 jne Done
 lda #1
 sta HpLoop
ReleaseLoop:
 ldx HpLoop
 jsr CmPlatformRelease
 dec HpLoop
 bpl ReleaseLoop
 lda #0
 sta HpSupport
 rts
CentersLo:.byte <888,<2216
CentersHi:.byte >888,>2216
.endproc
; X=cache0/1, C1/Yactor only for the reciprocal live primary tag.
.proc CmPlatformFind
 lda HpActorSlot,x
 beq No
 cmp #7
 bcs No
 tay
 dey
 txa
 clc
 adc #$81
 cmp HpActorOwner,y
 bne No
 lda Enemy_Flag,y
 cmp #1
 bne No
 lda Enemy_ID,y
 cmp #$25
 bne No
 lda Enemy_State,y
 cmp #$40
 bne No
 sec
 rts
No:clc
 rts
.endproc
.proc CmPlatformRelease
 stx HpSlot
 jsr CmPlatformFind
 bcc Forget
 tya
 tax
 jsr EraseEnemyObject
Forget:
 ldx HpSlot
 lda HpActorSlot,x
 jeq Done
 cmp #7
 bcs Slot
 tay
 dey
 txa
 clc
 adc #$81
 cmp HpActorOwner,y
 bne Slot
 lda #0
 sta HpActorOwner,y
Slot:lda #0
 sta HpActorSlot,x
Done:rts
.endproc
.proc CmPlatformSpawn
 stx HpSlot
 ldy #5
Free:lda Enemy_Flag,y
 beq Found
 dey
 bpl Free
 rts                            ; native actors win every capacity conflict
Found:
 ; Reject a stale cache alias before issuing a new reciprocal ownership tag.
 tya
 tax
 stx ObjectOffset
 ldy HpSlot
 tya
 clc
 adc #$81
 sta HpActorOwner,x
 txa
 clc
 adc #1
 sta HpActorSlot,y
 lda #$25
 sta Enemy_ID,x
 lda #1
 sta Enemy_Flag,x
 sta Enemy_Y_HighPos,x
 lda #0
 sta Enemy_State,x
 lda HpXLo,y
 sec
 sbc #16                       ; native32px girder, exact left edge
 sta Enemy_X_Position,x
 lda HpXHi,y
 sbc #0
 sta Enemy_PageLoc,x
 lda #208
 sta Enemy_Y_Position,x
 farcall InitEnemyObject
 ldx ObjectOffset
 lda #5                        ; same32px bbox and girder in Easy/Hard
 sta Enemy_BoundBoxCtrl,x
 lda #$40                      ;8px helper top, native movement owner>=4
 sta Enemy_State,x
 lda #$ff
 sta PlatformCollisionFlag,x
 rts
.endproc
CmPlatformTwoEnd:
.assert * <= $b600,lderror,"Two native supports exceed proposed26:B140..B5FF"
.popseg
.endif
