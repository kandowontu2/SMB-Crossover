.pushseg
.segment "M3_LOGIC"
.macro M3Dispatch Name,Own,LegacyTarget
.proc Name
 jsr M3IsActive
 bcc Legacy
 jmp Own
Legacy:farcall LegacyTarget,jmp
.endproc
.endmacro
M3Dispatch M3MovementDispatch,M3Movement,VvMovementDispatch
M3Dispatch M3GraphicsDispatch,M3Graphics,VvGraphicsDispatch
M3Dispatch M3PortraitDispatch,M3Portrait,VvPortraitDispatch
M3Dispatch M3WeaponsDispatch,M3Weapons,VvWeaponsDispatch
M3Dispatch M3InventoryDeathDispatch,M3Death,VvDeathStartDispatch
M3Dispatch M3InjuryDispatch,M3Injury,Cv3InjuryStartGate
M3Dispatch M3NewDrawDispatch,M3DrawWorld,VvDrawDispatch
.proc M3ResetDispatch
 jsr M3IsActive
 bcc Legacy
 farcall SpecialRosterClear
 jmp M3Reset
Legacy:farcall Cv3ResetGate,jmp
.endproc
.proc M3DeathDispatch
 jsr M3IsActive
 bcc Legacy
 inc MmDeathAge
 lda MmDeathAge
 cmp #1
 bne Move
 lda MmDeathPit
 bne Move
 lda #$c0 ; Original Player_Die initial Q4 velocity -64.
 sta M3Native::Player_YVel
 lda #$fc
 sta Player_Y_Speed
 sta M3LastVY
Move:
 lda SavedJoypadBits
 pha
 lda #0
 sta SavedJoypadBits
 sta M3Fresh
 farcall M3Step
 pla
 sta SavedJoypadBits
 lda MmDeathAge
 cmp #120
 bcc Done
 lda #6
 sta GameEngineSubroutine
 lda #0
 sta TimerControl
Done:rts
Legacy:farcall VvDeathDispatch,jmp
.endproc
.proc M3InjuryStatusDispatch
 jsr M3IsActive
 bcc Legacy
 ldx M3Form
 txa
 rts
Legacy:farcall Cv3InjuryStatusGate,jmp
.endproc
.proc M3Injury
 stx M3EnemySlot
 lda M3Form
 beq Fatal
 cmp #2
 bcc Small
 lda #1
 sta M3Form
 lda #23 ; Original US higher-suit loss poof.
 sta M3Poof
 bne Protection
Small:lda #0
 sta M3Form
 lda #47 ; Original PRG0 DA4E shrink; renderer reverses GrowFrames.
 sta M3Growth
Protection:
 jsr M3ClearSuitState
 lda #113
 sta GuestInvulTicks
 lda #1
 sta InjuryTimer
 ; A genuine nonzero owner admits GuestInjuryTick on subsequent Main calls.
 ; M3ClearSuitState above already invalidated M3PaletteValid. Reuse that
 ; redundant store's space; the same17-byte tail still takes22 CPU cycles.
 lda #17
 sta GuestHurtKind
 lda #0
 sta GuestHurtTicks
 sta TimerControl
 sta PlayerChangeSizeFlag
 nop
 lda #Sfx_PipeDown_Injury
 sta Square1SoundQueue
 ldx M3EnemySlot
 sec
 rts
Fatal:jmp KillPlayer
.endproc
.proc M3VisibleDispatch
 jsr M3IsActive
 bcc Legacy
 sec ; Graphics owns source2-tick blink after advancing transformation clocks.
 rts
Legacy:farcall TnVisibleDispatch,jmp
.endproc
.proc M3BodyDispatch
 jsr M3IsActive
 bcc Legacy
 lda AreaType
 sta GuestBodyStompAllowed
 lda #0
 sta GuestBodyNoStomp
 lda M3Form
 cmp #5
 bne Ordinary
 lda M3Native::Player_Statue
 beq Ordinary
 lda Enemy_ID,x
 cmp #Podoboo
 beq Ordinary
 cmp #$15
 bcs Protected
 lda Player_Y_Speed
 bmi Protected
 jsr M3DefeatEnemy
Protected:sec
 rts
Ordinary:clc
 rts
Legacy:farcall Cv3BodyGate,jmp
.endproc
.proc M3AdderDispatch
 cmp #17
 bne Legacy
 clc
 rts
Legacy:farcall VvAdderDispatch,jmp
.endproc
.proc M3BoxDispatch
 cmp #17
 bne Legacy
 rts
Legacy:farcall VvBoxDispatch,jmp
.endproc
.proc M3SpecialDrawGate
 jsr M3IsActive
 bcc Legacy
 rts
Legacy:farcall TnSpecialDrawDispatch,jmp
.endproc
.proc M3HeadDispatch
 jsr M3IsActive
 bcc Legacy
 lda Player_X_Position
 clc
 adc #8
 sta MmProbeX
 lda Player_PageLoc
 adc #0
 sta MmProbePage
 lda #6 ; Native non-sloped upward terrain probe, not low-clearance10.
 ldy PlayerSize
 bne Short
 ldy CrouchingFlag
 beq :+
Short:lda #16
:clc
 adc Player_Y_Position
 sta MmProbeY
 jsr M3ReadPoint
 pha
 beq Sampled
 ldy Player_Y_Speed
 bpl Sampled
 tax
 lda MTileAttribute,x
 and #MTILE_SOLID|MTILE_CLIMB
 cmp #MTILE_SOLID
 bne Sampled
 ; The native consumer's4px head threshold assumes its own probe offset.
 ; Separate the actual SMB3 head before native side probes can push X.
 lda R2
 clc
 adc #48
 ldy PlayerSize
 bne SmallHead
 ldy CrouchingFlag
 bne SmallHead
 sec
 sbc #6
 jmp Separate
SmallHead:sec
 sbc #16
Separate:sta Player_Y_Position
 lda #0
 sta M3Native::Player_YVelFrac
Sampled:
 lda Player_Y_Position
 and #15
 cmp #4
 bcs HeadThreshold
 ldy Player_Y_Speed
 bpl HeadThreshold
 ldy R3
 beq HeadThreshold
 lda #4 ; Actual source contact already admitted; bypass native4px heuristic.
HeadThreshold:
 sta R4
 lda MmProbeX
 sta R5
 ldx #0
 pla
 rts
Legacy:farcall TnHeadDispatch,jmp
.endproc
.proc M3SideDispatch
 lda SelectedCharacter
 cmp #17
 beq Own
 cmp #CHARACTER_TMNT
 bne :+
 farcall TnSideDispatch,jmp
:cmp #CHARACTER_SOPHIA
 bne Native
 farcall SophiaSourceSideProbe,jmp
Native:jmp BlockBufferColli_Side
Own:
 sty M3SideY
 lda R0
 sta M3SideCounter
 tya
 cmp Local_eb
 bne Lower
 lda #14
 ldy PlayerSize
 bne SmallTop
 ldy CrouchingFlag
 beq YReady
SmallTop:lda #20
 bne YReady
Lower:lda #27
YReady:clc
 adc Player_Y_Position
 sta MmProbeY
 ldy #0
 lda PlayerSize
 ora CrouchingFlag
 beq :+
 iny
:lda M3SideCounter
 cmp #1
 beq Right
 lda LeftOffsets,y
 bne XReady
Right:lda RightOffsets,y
XReady:clc
 adc Player_X_Position
 sta MmProbeX
 lda Player_PageLoc
 adc #0
 sta MmProbePage
 jsr M3ReadPoint
 pha
 lda M3SideCounter
 sta R0
 lda MmProbeX
 sta R5
 lda Player_X_Position
 and #15
 sta R4
 ldy M3SideY
 ldx #0
 pla
 rts
LeftOffsets:.byte 1,2
RightOffsets:.byte 14,13
.endproc
.proc M3BoundingBoxGate
 php
 pha
 jsr M3IsActive
 bcs Own
 pla
 plp
 farcall VvBoundingBoxGate,jmp
Own:
 pla
 plp
 jsr BoundingBoxCore
 ldy #0
 lda M3Form
 beq Small
 lda CrouchingFlag
 bne Small
 iny
Small:
 lda Player_Rel_XPos
 clc
 adc Lefts,y
 sta BoundingBox_UL_XPos
 lda Player_Rel_XPos
 clc
 adc Rights,y
 sta BoundingBox_LR_Corner
 lda Player_Rel_YPos
 clc
 adc Tops,y
 sta BoundingBox_UL_YPos
 lda Player_Rel_YPos
 clc
 adc #30
 sta BoundingBox_LR_Corner+1
 ldx #0
 ldy #0
 rts
Lefts:.byte 4,3
Rights:.byte 12,13
Tops:.byte 17,5
.endproc
.proc M3StatusNameDispatch
 pha
 jsr M3IsActive
 bcs Own
 pla
 farcall VvStatusName,jmp
Own:pla
 cmp #0
 bne Done
 pha
 txa
 pha
 ldy #0
 ldx M3Variant
 beq :+
 ldy #7
:sty M3Scratch
 ldy #0
Loop:ldx M3Scratch
 lda Names,x
 sta VRAM_Buffer1+11,y
 inc M3Scratch
 iny
 cpy #7
 bcc Loop
 pla
 tax
 pla
Done:rts
Names:.byte "MARIO3 ","LUIGI3 "
.endproc
.popseg
