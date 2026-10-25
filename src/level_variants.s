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
  jsr HpGetCharacterMask
  and CellMask,x
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

; Shared gate implementation is HpGetCharacterMask. New roster helper masks
; are an explicitly approved port accommodation, not Crossover source parity.

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

CrossoverCellCount=38
CrossoverCoinCellCount=16
CellArea:
  .byte $40,$41,$31,$31,$31,$23,$23,$23,$23,$23,$23,$23,$23,$23,$23,$23,$27,$27,$27,$27,$27,$27,$27,$27,$41,$61,$20,$20,$2c,$2c,$2c,$2c,$2c,$2c,$2c,$2c,$2c,$2c
CellWorld:
  .byte $00,$03,$04,$04,$04,$05,$05,$05,$05,$05,$05,$05,$05,$05,$05,$05,$01,$01,$01,$01,$01,$01,$01,$01,$03,$03,$02,$02,$03,$03,$03,$03,$03,$03,$03,$03,$03,$03
CellPage:
  .byte $0a,$0b,$09,$09,$09,$07,$07,$07,$07,$07,$07,$07,$07,$07,$07,$07,$04,$04,$04,$04,$04,$04,$04,$04,$08,$06,$02,$02,$01,$01,$02,$01,$01,$01,$01,$01,$01,$01
CellColumn:
  .byte $05,$0a,$03,$04,$05,$01,$03,$07,$08,$09,$0a,$0b,$0c,$0d,$0e,$0f,$08,$08,$09,$09,$0a,$0a,$0b,$0b,$00,$00,$02,$03,$0e,$0f,$00,$0f,$0f,$0f,$0f,$0f,$0f,$0f
CellRow:
  .byte $08,$08,$07,$07,$07,$07,$03,$03,$03,$03,$03,$03,$03,$03,$03,$03,$03,$04,$02,$03,$02,$03,$03,$04,$00,$08,$0c,$0c,$05,$05,$05,$06,$07,$08,$09,$0a,$0b,$0c
CellEasy:
  .byte $6f,$6f,$6e,$6e,$6e,$6e,$6e,$6e,$6e,$6e,$6e,$6e,$6e,$6e,$6e,$6e,$00,$c2,$00,$c2,$00,$c2,$00,$c2,$00,$ff,$ff,$ff,$19,$1a,$1b,$4f,$50,$50,$50,$50,$50,$50
CellHard:
  .byte $5d,$5d,$58,$58,$58,$58,$58,$58,$58,$58,$58,$58,$58,$58,$58,$58,$00,$c2,$00,$c2,$00,$c2,$00,$c2,$00,$00,$19,$1b,$19,$1a,$1b,$4f,$50,$50,$50,$50,$50,$50
CellMask:
  .byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$01,$01,$02,$02,$02,$02,$02,$02,$02,$02,$02,$02
CoinCellArea:
  .byte $40,$41,$31,$31,$31,$23,$23,$23,$23,$23,$23,$23,$23,$23,$23,$23
CoinCellWorld:
  .byte $00,$03,$04,$04,$04,$05,$05,$05,$05,$05,$05,$05,$05,$05,$05,$05
CoinCellPage:
  .byte $0a,$0b,$09,$09,$09,$07,$07,$07,$07,$07,$07,$07,$07,$07,$07,$07
CoinCellColumn:
  .byte $05,$0a,$03,$04,$05,$01,$03,$07,$08,$09,$0a,$0b,$0c,$0d,$0e,$0f
CoinCellRow:
  .byte $80,$80,$70,$70,$70,$70,$30,$30,$30,$30,$30,$30,$30,$30,$30,$30
CoinCellBufferLo:
  .byte $05,$da,$d3,$d4,$d5,$d1,$d3,$d7,$d8,$d9,$da,$db,$dc,$dd,$de,$df
CoinCellBufferHi:
  .byte $03,$03,$03,$03,$03,$03,$03,$03,$03,$03,$03,$03,$03,$03,$03,$03

.popseg

.pushseg
.segment "LEVEL_VARIANTS"
.proc CrossoverDrawSmallPlatform
      ;  ldy Enemy_SprDataOffset,x   ;get OAM data offset
    AllocSpr 6
       lda #PLATFORM_GIRDER        ;load tile number for small platforms
       iny                         ;increment offset for tile numbers
       farcall DumpSixSpr              ;dump tile number into all six sprites
       iny                         ;increment offset for attributes
       lda #$02                    ;load palette controls
       farcall DumpSixSpr              ;dump attributes into all six sprites
       dey                         ;decrement for original offset
       dey
       lda Enemy_Rel_XPos          ;get relative horizontal coordinate
       sta Sprite_X_Position,y
       sta Sprite_X_Position+12,y  ;dump as X coordinate into first and fourth sprites
       clc
       adc #$08                    ;add eight pixels
       sta Sprite_X_Position+4,y   ;dump into second and fifth sprites
       sta Sprite_X_Position+16,y
       clc
       adc #$08                    ;add eight more pixels
       sta Sprite_X_Position+8,y   ;dump into third and sixth sprites
       sta Sprite_X_Position+20,y
       lda Enemy_Y_Position,x      ;get vertical coordinate
       tax
       pha                         ;save to stack
       cpx #$20                    ;if vertical coordinate below status bar,
       bcs TopSP                   ;do not mess with it
       lda #$f8                    ;otherwise move first three sprites offscreen
TopSP: farcall DumpThreeSpr            ;dump vertical coordinate into Y coordinates
       pla                         ;pull from stack
       farcall CrossoverLiftSecondY
       tax
       cpx #$20                    ;if below status bar (taking wrap into account)
       bcs BotSP                   ;then do not change altered coordinate
       lda #$f8                    ;otherwise move last three sprites offscreen
BotSP: sta Sprite_Y_Position+12,y  ;dump vertical coordinate + 128 pixels
       sta Sprite_Y_Position+16,y  ;into Y coordinates
       sta Sprite_Y_Position+20,y
       lda Enemy_OffscreenBits     ;get offscreen bits
       pha                         ;save to stack
       and #%00001000              ;check d3
       beq SOfs
       lda #$f8                    ;if d3 was set, move first and
       sta Sprite_Y_Position,y     ;fourth sprites offscreen
       sta Sprite_Y_Position+12,y
SOfs:  pla                         ;move out and back into stack
       pha
       and #%00000100              ;check d2
       beq SOfs2
       lda #$f8                    ;if d2 was set, move second and
       sta Sprite_Y_Position+4,y   ;fifth sprites offscreen
       sta Sprite_Y_Position+16,y
SOfs2: pla                         ;get from stack
       and #%00000010              ;check d1
       beq ExSPl
       lda #$f8                    ;if d1 was set, move third and
       sta Sprite_Y_Position+8,y   ;sixth sprites offscreen
       sta Sprite_Y_Position+20,y
ExSPl: ldx ObjectOffset            ;get enemy object offset and leave
       rts

.endproc
.assert *<=$a800,error,"Authored level code must preserve helper cold space atA800"
.popseg
