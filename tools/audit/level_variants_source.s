; Authored Crossover level differences, using the retained revision2 audit.
; Easy = pinned hosted six-character1.x; Hard = authenticated2.02.
; Keep original NES coordinates. This is not a replacement castle-maze engine.
.pushseg
.segment "LEVEL_VARIANTS_BRIDGE"
; AreaParserCore discards incoming A and reloads BlockBufferColumnPos after us.
.proc CrossoverLevelColumnBridge
  lda #<CrossoverLevelColumn
  SMC_StoreLowByte FarcallJmpTarget,a
  lda #>CrossoverLevelColumn
  SMC_StoreHighByte FarcallJmpTarget,a
.if ::MAPPER_MMC5
  lda #.bank(CrossoverLevelColumn) | MMC5_PRG_ROM
.else
  lda #.bank(CrossoverLevelColumn)
.endif
  jmp FarCallCommon
  .assert *-CrossoverLevelColumnBridge=15,error,"Retain the17-byte LEVEL tail"
.endproc

.segment "LEVEL_VARIANTS"
.proc CrossoverLevelColumn
  farcall ProcessAreaData
  lda AreaPointer
  cmp #$40                    ;1-2
  beq Scan
  cmp #$41                    ;4-2
  beq Scan
  cmp #$31                    ;5-2
  beq Scan
  cmp #$23                    ;6-2
  beq Scan
  cmp #$27                    ;2-3 /7-3
  beq Scan
  cmp #$20                    ;3-3
  beq Scan
  cmp #$2c                    ;4-3
  beq Scan
  cmp #$61                    ;4-4
  bne Done
Scan:
  ldx #CrossoverCellCount-1
Loop:
  lda AreaPointer
  cmp CellArea,x
  bne Next
  lda WorldNumber
  cmp CellWorld,x
  bne Next
  lda CurrentPageLoc
  cmp CellPage,x
  bne Next
  lda CurrentColumnPos
  cmp CellColumn,x
  bne Next
  lda CellMask,x
  beq Version
  ldy SelectedCharacter
  cpy #CHARACTER_COUNT
  bcs Next
  and CrossoverCharacterHelperMask,y
  beq Next
Version:
  lda CrossoverBehaviorVersion
  beq Easy
  lda CellHard,x
  jmp Store
Easy:
  lda CellEasy,x
Store:
  cmp #$ff                    ;FF is absent in this behavior version.
  beq Next
  ldy CellRow,x
  sta MetatileBuffer,y
Next:
  dex
  bpl Loop
Done:
  rts
.endproc

; Shared mask contract:1H,2V. Luigi and Bass have neither source helper family.
; Pit/Rygar H and Scrooge H+V are the user-approved conservative custom policy.
CrossoverCharacterHelperMask:
  .byte 0,3,1,3,3,1,1,1,0,0,1,2,3

.proc CrossoverLevelEnemyInit
  php
  pha
  lda AreaPointer
  cmp #$01                    ; Shared2-2 /7-2 water stream.
  bne Ground
  lda WorldNumber
  cmp #World2
  beq WaterOffset
  cmp #World7
  bne Native
WaterOffset:
  lda EnemyDataOffset
  cmp #23                     ; Native Blooper column71,row8 is not authored.
  beq Omit
  bne Native
Ground:
  cmp #$23                    ;6-2
  bne Native
  lda WorldNumber
  cmp #World6
  bne Native
  lda EnemyDataOffset
  cmp #14                     ; Native upper Goomba column68,row3 is absent.
  bne Native
Omit:
  pla
  plp
  lda #0
  sta Enemy_Flag,x
  sta EnemyObjectPageSel
  inc EnemyDataOffset         ; Consume only this admitted two-byte actor.
  inc EnemyDataOffset
  rts
Native:
  pla
  plp                         ; CheckpointEnemyID uses incoming carry at its Y adder.
  farcall CheckpointEnemyID
  php
  pha
  lda AreaPointer
  cmp #$62
  bne Done
  lda WorldNumber
  cmp #World2
  beq Castle2
  cmp #World5
  bne Done
  lda Enemy_ID,x
  cmp #$2b
  beq Rise5
  cmp #$2c
  bne Done
  lda #64                     ;5-4 right: falling at64/192.
  sta Enemy_Y_Position,x
  lda #192
  bne Second
Rise5:
  lda #96                     ;5-4 left: rising at96/224.
  sta Enemy_Y_Position,x
  lda #224
  bne Second
Castle2:
  lda Enemy_ID,x
  cmp #$2b
  beq Reverse
  cmp #$2c
  bne Done
Reverse:
  eor #7                      ;2-4 duplicate constructor properties: first wins.
  sta Enemy_ID,x              ; Left falls; right rises in both pinned versions.
  lda #96
  sta Enemy_Y_Position,x
  lda #192
Second:
  sta Enemy_State,x           ; Small lifts otherwise do not use these fields.
  lda #0
  sta Enemy_X_Speed,x         ; Second platform Q8 fraction.
  sta Enemy_YMoveForceFractional,x
  sta Enemy_Y_MoveForce,x ; Shared three-update rational55px/s cadence.
Done:
  pla
  plp
  rts
.endproc

.proc CrossoverLevelGroupInit
  php
  pha
  lda NumberofGroupEnemies
  cmp #1                     ; Omit the second/final member, not the whole group.
  bne Native
  lda AreaPointer
  cmp #$25
  bne World6Group
  lda WorldNumber
  cmp #World1
  bne Native
  lda CrossoverBehaviorVersion
  beq Native
  lda EnemyDataOffset
  cmp #23                    ;2.02 removes source1-1(128,12),shiftRight.
  beq Omit
  bne Native
World6Group:
  cmp #$23
  bne Native
  lda WorldNumber
  cmp #World6
  bne Native
  lda EnemyDataOffset
  cmp #32                    ;6-2 later grouped Goomba at nominalcolumn170.5.
  bne Native
Omit:
  pla
  plp
  lda #0
  sta Enemy_Flag,x            ; HandleGroupEnemies still consumes the record once.
  rts
Native:
  pla
  plp
  farcall CheckpointEnemyID,jmp
.endproc

.proc CrossoverLevelCoinBrick
  tya
  pha
  lda CrossoverBehaviorVersion
  beq Ordinary
  ldx #CrossoverCoinCellCount-1
Loop:
  lda AreaPointer
  cmp CoinCellArea,x
  bne Next
  lda WorldNumber
  cmp CoinCellWorld,x
  bne Next
  lda R2
  cmp CoinCellRow,x
  bne Next
  lda R6
  cmp CoinCellBufferLo,x
  bne Next
  lda R7
  cmp CoinCellBufferHi,x
  bne Next
  lda Player_PageLoc
  cmp CoinCellPage,x
  beq Single
  ; A head/projectile center can probe across one page boundary. Resolve the
  ; actual contacted cell using its block-buffer column and the center edge.
  lda CoinCellColumn,x
  beq PreviousPage
  cmp #15
  bne Next
  lda Player_X_Position
  cmp #32
  bcs Next
  lda Player_PageLoc
  sec
  sbc #1
  cmp CoinCellPage,x
  beq Single
  bne Next
PreviousPage:
  lda Player_X_Position
  cmp #224
  bcc Next
  lda Player_PageLoc
  clc
  adc #1
  cmp CoinCellPage,x
  beq Single
Next:
  dex
  bpl Loop
Ordinary:
  pla
  tay
  ldx SprDataOffset_Ctrl
  lda SelectedCharacter
  beq Mario
  farcall MegaManCoinBrick,jmp
Mario:
  lda BrickCoinTimerFlag      ; Preserve native Mario's original multi-coin rule.
  bne Running
  lda #$0b
  sta BrickCoinTimer
  inc BrickCoinTimerFlag
Running:
  lda BrickCoinTimer
  bne Keep
  ldy #$c4
Keep:
  tya
  rts
Single:
  pla
  tay
  ldx SprDataOffset_Ctrl
  lda #$c4                    ; The ordinary bounce emits one coin, then empties.
  rts
.endproc

.proc CrossoverLiftMove
  lda AreaPointer
  cmp #$62
  jne Native
  lda WorldNumber
  cmp #World2
  beq Source
  cmp #World5
  jne Native
Source:
  lda TimerControl
  jne Done
  lda Enemy_OffscreenBits
  and #15
  cmp #15                     ; Source platforms do not tick before visibility.
  jeq Done
  ldy Enemy_Y_MoveForce,x
  lda LiftStep,y
  sta R0
  iny
  cpy #3
  bcc Counter
  ldy #0
Counter:
  tya
  sta Enemy_Y_MoveForce,x
  lda Enemy_ID,x
  cmp #$2b
  jeq Rise
  lda Enemy_YMoveForceFractional,x
  clc
  adc R0
  sta Enemy_YMoveForceFractional,x
  lda Enemy_Y_Position,x
  adc #0
  cmp #240
  bcc Fall1Store
  bne Fall1Reset
  lda Enemy_YMoveForceFractional,x
  beq Fall1End
Fall1Reset:
  lda PlatformCollisionFlag,x
  cmp #2
  bne Fall1Release
  lda #0
  sta PlatformCollisionFlag,x
Fall1Release:
  lda #0
  sta Enemy_YMoveForceFractional,x
  lda #64
  bne Fall1Store
Fall1End:
  lda #240
Fall1Store:
  sta Enemy_Y_Position,x
  lda Enemy_X_Speed,x
  clc
  adc R0
  sta Enemy_X_Speed,x
  lda Enemy_State,x
  adc #0
  cmp #240
  bcc Fall2Store
  bne Fall2Reset
  lda Enemy_X_Speed,x
  beq Fall2End
Fall2Reset:
  lda PlatformCollisionFlag,x
  cmp #1
  bne Fall2Release
  lda #0
  sta PlatformCollisionFlag,x
Fall2Release:
  lda #0
  sta Enemy_X_Speed,x
  lda #64
  bne Fall2Store
Fall2End:
  lda #240
Fall2Store:
  sta Enemy_State,x
  rts
Rise:
  lda Enemy_YMoveForceFractional,x
  sec
  sbc R0
  sta Enemy_YMoveForceFractional,x
  lda Enemy_Y_Position,x
  sbc #0
  cmp #64
  bcs Rise1Store
  lda PlatformCollisionFlag,x
  cmp #2
  bne Rise1Release
  lda #0
  sta PlatformCollisionFlag,x
Rise1Release:
  lda #0
  sta Enemy_YMoveForceFractional,x
  lda #240
Rise1Store:
  sta Enemy_Y_Position,x
  lda Enemy_X_Speed,x
  sec
  sbc R0
  sta Enemy_X_Speed,x
  lda Enemy_State,x
  sbc #0
  cmp #64
  bcs Rise2Store
  lda PlatformCollisionFlag,x
  cmp #1
  bne Rise2Release
  lda #0
  sta PlatformCollisionFlag,x
Rise2Release:
  lda #0
  sta Enemy_X_Speed,x
  lda #240
Rise2Store:
  sta Enemy_State,x
Done:
  rts
Native:
  farcall MoveLiftPlatforms,jmp
LiftStep:
  .byte 235,235,234            ; Sum704Q8 units/3 =55NESpx/s at60Hz.
.endproc

;@@CELL_TABLES@@

.segment "LEVEL_LIFT_BRIDGE"
.proc CrossoverLiftMoveBridge
  farcall CrossoverLiftMove
  rts
.endproc

.proc CrossoverLiftSecondY
  pha
  lda AreaPointer
  cmp #$62
  bne Native
  lda WorldNumber
  cmp #World2
  beq Source
  cmp #World5
  bne Native
Source:
  pla
  ldx ObjectOffset            ; DrawSmallPlatform's incoming X is an old Y value.
  sec
  sbc Enemy_Y_Position,x
  clc
  adc Enemy_State,x
  rts
Native:
  pla
  clc
  adc #$80
  rts
.endproc

.proc CrossoverLiftPlayerY
  cpy #1
  beq Second
  clc
  adc #0
  rts
Second:
  jmp CrossoverLiftSecondY
.endproc
.popseg
