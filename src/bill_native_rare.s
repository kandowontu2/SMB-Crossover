.pushseg
.segment "SRAM"
BillNativeReturnP: .res 1
BillNativeReturnA: .res 1
BillNativeReturnSelector: .res 1
.assert BillNativeReturnSelector=$7ff6,error,"Append explicit original output selector"
.assert BillNativeReturnP=$7ff4,error,"Append rare-call P after exact old Bill cache"
.assert * <= $8000,error,"Rare-call result exceeds SRAM"
.popseg
; Private V layout only: existing rare native procedures moved byte-for-byte
; except necessary bank/local target bindings. Resident public ABI wrappers
; preserve all input/output registers/flags; no-Down pipe return stays resident.
.pushseg
.segment "BILL_BODY_COLD"
BillNativeRareStart:
.pushseg
.segment "OBJECT_EX"
.proc NativeRareRunGameOver
  jsr NativeRareRunGameOverCore
  jsr BillNativeCaptureP
.if ::MAPPER_MMC3
  ; Public entry SP=s. Selector push ->s-1; JSR common ->s-3;
  ; bank push ->s-4; target JSR ->s-6; one X-save ->s-7.
  ; Thus original selector is at $0107,X; actual stack oracle guards it.
  txa
  pha
  tsx
  lda $0107,x
  sta BillNativeReturnSelector
  pla
  tax
  lda BillNativeReturnSelector
.else
  lda #0
  sta BillNativeReturnSelector
.endif
  rts
.endproc
.proc NativeRareRunGameOverCore

  lda #$00              ;reenable screen
  sta DisableScreenFlag
  lda SavedJoypad1Bits  ;check controller for start pressed
  and #Start_Button
  bne TerminateGame
  lda ScreenTimer       ;if not pressed, wait for
  bne GameIsOn          ;screen timer to expire
TerminateGame:
  lda #Silence          ;silence music
  sta EventMusicQueue
  jsr TransposePlayers  ;check if other player can keep
  bcc ContinueGame      ;going, and do so if possible
  lda WorldNumber       ;otherwise put world number of current
  sta ContinueWorld     ;player into secret continue function variable
  lda #$00
  sta OperMode_Task     ;reset all modes to title screen and
  sta ScreenTimer       ;leave
  sta OperMode
  rts

ContinueGame:
  jsr LoadAreaPointer       ;update level pointer with
  lda #$01                  ;actual world and area numbers, then
  sta PlayerSize            ;reset player's size, status, and
  inc FetchNewGameTimerFlag ;set game timer flag to reload
  lda #$00                  ;game timer from header
  sta TimerControl          ;also set flag for timers to count again
  sta PlayerStatus
  sta GameEngineSubroutine  ;reset task for game core
  sta OperMode_Task         ;set modes and leave
  lda #$01                  ;if in game over mode, switch back to
  sta OperMode              ;game mode, because game is still on
GameIsOn:
  rts
.endproc
.popseg

.proc NativeRareGameMenuRoutine
  jsr NativeRareGameMenuRoutineCore
  jsr BillNativeCaptureP
.if ::MAPPER_MMC3
  ; Original compiled far/endfar always selects 7|PRG_FIXED_8, literally.
  lda #7 | PRG_FIXED_8
.else
  lda #0
.endif
  sta BillNativeReturnSelector
  rts
.endproc
.proc NativeRareGameMenuRoutineCore
.if ::ENABLE_CROSSOVER
  farcall CrossoverMenuInput
  cmp #0
  beq ExitMenu
  jmp ChkContinue
.else

  ldy #$00
  lda SavedJoypad1Bits        ;check to see if either player pressed
  ora SavedJoypad2Bits        ;only the start button (either joypad)
  cmp #Start_Button
  beq StartGame
  cmp #A_Button+Start_Button  ;check to see if A + start was pressed
  bne ChkSelect               ;if not, branch to check select button
StartGame:
  jmp ChkContinue             ;if either start or A + start, execute here
ChkSelect:
  cmp #Select_Button          ;check to see if the select button was pressed
  beq SelectBLogic            ;if so, branch reset demo timer
  ldx DemoTimer               ;otherwise check demo timer
  bne ChkWorldSel             ;if demo timer not expired, branch to check world selection
  sta SelectTimer             ;set controller bits here if running demo
  jsr DemoEngine              ;run through the demo actions
  bcs ResetTitle              ;if carry flag set, demo over, thus branch
  jmp RunDemo                 ;otherwise, run game engine for demo
ChkWorldSel:
  ldx WorldSelectEnableFlag   ;check to see if world selection has been enabled
  beq NullJoypad
  cmp #B_Button               ;if so, check to see if the B button was pressed
  bne NullJoypad
  iny                         ;if so, increment Y and execute same code as select
SelectBLogic:
  lda DemoTimer               ;if select or B pressed, check demo timer one last time
  beq ResetTitle              ;if demo timer expired, branch to reset title screen mode
  lda #$18                    ;otherwise reset demo timer
  sta DemoTimer
  lda SelectTimer             ;check select/B button timer
  bne NullJoypad              ;if not expired, branch
  lda #$10                    ;otherwise reset select button timer
  sta SelectTimer
  cpy #$01                    ;was the B button pressed earlier?  if so, branch
  beq IncWorldSel             ;note this will not be run if world selection is disabled
  lda NumberOfPlayers         ;if no, must have been the select button, therefore
  eor #%00000001              ;change number of players and draw icon accordingly
  sta NumberOfPlayers
  farcall DrawMushroomIcon
  jmp NullJoypad
IncWorldSel:
  ldx WorldSelectNumber       ;increment world select number
  inx
  txa
  and #%00000111              ;mask out higher bits
  sta WorldSelectNumber       ;store as current world select number
  jsr GoContinue
UpdateShroom:
  lda WSelectBufferTemplate,x ;write template for world select in vram buffer
  sta VRAM_Buffer1-1,x        ;do this until all bytes are written
  inx
  cpx #$06
  bmi UpdateShroom
  ldy WorldNumber             ;get world number from variable and increment for
  iny                         ;proper display, and put in blank byte before
  sty VRAM_Buffer1+3          ;null terminator
NullJoypad:
  lda #$00                    ;clear joypad bits for player 1
  sta SavedJoypad1Bits
RunDemo:
  jsr GameCoreRoutine         ;run game engine
  lda GameEngineSubroutine    ;check to see if we're running lose life routine
  cmp #$06
  bne ExitMenu                ;if not, do not do all the resetting below
ResetTitle:
  lda #$00                    ;reset game modes, disable
  sta OperMode                ;sprite 0 check and disable
  sta OperMode_Task           ;screen output
  sta Sprite0HitDetectFlag
  inc DisableScreenFlag
  rts
.endif
ChkContinue:
.if ::ENABLE_CROSSOVER
  ; Start/A was confirmed in the dedicated select screen.
.else
  ldy DemoTimer               ;if timer for demo has expired, reset modes
  beq ResetTitle
.endif
  asl                         ;check to see if A button was also pushed
  bcc StartWorld1             ;if not, don't load continue function's world number
  lda ContinueWorld           ;load previously saved world number for secret
  jsr GoContinue              ;continue function when pressing A + start
StartWorld1:
  jsr LoadAreaPointer
  inc Hidden1UpFlag           ;set 1-up box flag for both players
  inc OffScr_Hidden1UpFlag
  inc FetchNewGameTimerFlag   ;set fetch new game timer flag
  inc OperMode                ;set next game mode
  lda WorldSelectEnableFlag   ;if world select flag is on, then primary
  sta PrimaryHardMode         ;hard mode must be on as well
  lda #$00
  sta OperMode_Task           ;set game mode here, and clear demo timer
  sta DemoTimer
  ldx #6 + 6 + 2 + 2 - 1      ; for each of the scores
  lda #$00
InitScores:
  sta ScoreAndCoinDisplay,x   ;clear player scores and coin displays
  dex
  bpl InitScores
ExitMenu:
  rts
GoContinue:
  sta WorldNumber             ;start both players at the first area
  sta OffScr_WorldNumber      ;of the previously saved world number
  ldx #$00                    ;note that on power-up using this function
  stx AreaNumber              ;will make no difference
  stx OffScr_AreaNumber   
  rts
.endproc

.proc NativeRareDemoEngine
  jsr NativeRareDemoEngineCore
  jsr BillNativeCaptureP
.if ::MAPPER_MMC3
  ; Public entry SP=s. Selector push ->s-1; JSR common ->s-3;
  ; bank push ->s-4; target JSR ->s-6; one X-save ->s-7.
  ; Thus original selector is at $0107,X; actual stack oracle guards it.
  txa
  pha
  tsx
  lda $0107,x
  sta BillNativeReturnSelector
  pla
  tax
  lda BillNativeReturnSelector
.else
  lda #0
  sta BillNativeReturnSelector
.endif
  rts
.endproc
.proc NativeRareDemoEngineCore
  ldx DemoAction         ;load current demo action
  lda DemoActionTimer    ;load current action timer
  bne DoAction           ;if timer still counting down, skip
  inx
  inc DemoAction         ;if expired, increment action, X, and
  sec                    ;set carry by default for demo over
  lda DemoTimingData-1,x ;get next timer
  sta DemoActionTimer    ;store as current timer
  beq DemoOver           ;if timer already at zero, skip
DoAction:
  lda DemoActionData-1,x ;get and perform action (current or next)
  sta SavedJoypad1Bits
  dec DemoActionTimer    ;decrement action timer
  clc                    ;clear carry if demo still going
DemoOver:
  rts

DemoActionData:
      .byte $01, $80, $02, $81, $41, $80, $01
      .byte $42, $c2, $02, $80, $41, $c1, $41, $c1
      .byte $01, $c1, $01, $02, $80, $00

DemoTimingData:
      .byte $9b, $10, $18, $05, $2c, $20, $24
      .byte $15, $5a, $10, $20, $28, $30, $20, $10
      .byte $80, $20, $30, $30, $01, $ff, $00
.endproc

.proc NativeRareVictoryMode
  jsr NativeRareVictoryModeCore
  jsr BillNativeCaptureP
.if ::MAPPER_MMC3
  ; Original compiled far/endfar always selects 7|PRG_FIXED_8, literally.
  lda #7 | PRG_FIXED_8
.else
  lda #0
.endif
  sta BillNativeReturnSelector
  rts
.endproc
.proc NativeRareVictoryModeCore

  ; lda #0
  ; sta PlayerOAMOffset
  jsr PlayerOAMReservation
  sta CurrentOAMOffset
  
  jsr VictoryModeSubroutines  ;run victory mode subroutines
  lda OperMode_Task           ;get current task of victory mode
  beq AutoPlayer              ;if on bridge collapse, skip enemy processing
  ldx #$00
  stx ObjectOffset            ;otherwise reset enemy object offset 
  ; TODO Consolidate farcall 
  farcall EnemiesAndLoopsCore     ;and run enemy code
AutoPlayer:
  jsr RelativePlayerPosition  ;get player's relative coordinates
  farcall PlayerGfxHandler    ;draw the player, then leave
  
  farcall SamusFreezeDrawAll, jmp

.endproc

.proc NativeRarePlayerVictoryWalk
  jsr NativeRarePlayerVictoryWalkCore
  jsr BillNativeCaptureP
.if ::MAPPER_MMC3
  ; Original compiled far/endfar always selects 7|PRG_FIXED_8, literally.
  lda #7 | PRG_FIXED_8
.else
  lda #0
.endif
  sta BillNativeReturnSelector
  rts
.endproc
.proc NativeRarePlayerVictoryWalkCore
  ldy #$00                ;set value here to not walk player by default
  sty VictoryWalkControl
  lda Player_PageLoc      ;get player's page location
  cmp DestinationPageLoc  ;compare with destination page location
  bne PerformWalk         ;if page locations don't match, branch
  lda Player_X_Position   ;otherwise get player's horizontal position
  cmp #$60                ;compare with preset horizontal position
  bcs DontWalk            ;if still on other page, branch ahead
PerformWalk:
  inc VictoryWalkControl  ;otherwise increment value and Y
  iny                     ;note Y will be used to walk the player
DontWalk:
  tya                     ;put contents of Y in A and
  sta SavedJoypadBits
.if ::ENABLE_CROSSOVER
  farcall GuestVictoryControl
.else
  farcall PlayerCtrlRoutine   ;use A to move player to the right or not
.endif
  lda ScreenLeft_PageLoc  ;check page location of left side of screen
  cmp DestinationPageLoc  ;against set value here
  beq ExitVWalk           ;branch if equal to change modes if necessary
  lda ScrollFractional
  clc                     ;do fixed point math on fractional part of scroll
  adc #$80        
  sta ScrollFractional    ;save fractional movement amount
  lda #$01                ;set 1 pixel per frame
  adc #$00                ;add carry from previous addition
  tay                     ;use as scroll amount
  farcall ScrollScreen        ;do sub to scroll the screen
  jsr UpdScrollVar        ;do another sub to update screen and scroll variables
  inc VictoryWalkControl  ;increment value to stay in this routine
ExitVWalk:
  lda VictoryWalkControl  ;load value set here
  ; jroweboy: Change from vanilla: just inc and rts here instead
  ; beq IncModeTask_A       ;if zero, branch to change modes
  ; rts                     ;otherwise leave
  bne DontIncModeTask
    inc OperMode_Task
DontIncModeTask:
  rts
.endproc

.pushseg
.segment "OBJECT_EX"
.proc NativeRarePrintVictoryMessages
  jsr NativeRarePrintVictoryMessagesCore
  jsr BillNativeCaptureP
.if ::MAPPER_MMC3
  ; Public entry SP=s. Selector push ->s-1; JSR common ->s-3;
  ; bank push ->s-4; target JSR ->s-6; one X-save ->s-7.
  ; Thus original selector is at $0107,X; actual stack oracle guards it.
  txa
  pha
  tsx
  lda $0107,x
  sta BillNativeReturnSelector
  pla
  tax
  lda BillNativeReturnSelector
.else
  lda #0
  sta BillNativeReturnSelector
.endif
  rts
.endproc
.proc NativeRarePrintVictoryMessagesCore
  lda SecondaryMsgCounter   ;load secondary message counter
  bne IncMsgCounter         ;if set, branch to increment message counters
  lda PrimaryMsgCounter     ;otherwise load primary message counter
  beq ThankPlayer           ;if set to zero, branch to print first message
  ldy WorldNumber           ;check world number
  cpy #World8
  bne MRetainerMsg          ;if not at world 8, skip to next part
  cmp #$03                  ;check primary message counter again
  bcc IncMsgCounter         ;if not at 3 yet (world 8 only), branch to increment
  sbc #$01                  ;otherwise subtract one
  jmp ThankPlayer           ;and skip to next part
MRetainerMsg:
  cmp #$02                  ;check primary message counter
  bcc IncMsgCounter         ;if not at 2 yet (world 1-7 only), branch
ThankPlayer:
  tay                       ;put primary message counter into Y
  bne SecondPartMsg         ;if counter nonzero, skip this part, do not print first message
  lda CurrentPlayer         ;otherwise get player currently on the screen
  beq EvalForMusic          ;if mario, branch
  iny                       ;otherwise increment Y once for luigi and
  bne EvalForMusic          ;do an unconditional branch to the same place
SecondPartMsg:
  iny                       ;increment Y to do world 8's message
  lda WorldNumber
  cmp #World8               ;check world number
  beq EvalForMusic          ;if at world 8, branch to next part
  dey                       ;otherwise decrement Y for world 1-7's message
  cpy #$04                  ;if counter at 4 (world 1-7 only)
  bcs SetEndTimer           ;branch to set victory end timer
  cpy #$03                  ;if counter at 3 (world 1-7 only)
  bcs IncMsgCounter         ;branch to keep counting
EvalForMusic:
  cpy #$03                  ;if counter not yet at 3 (world 8 only), branch
  bne PrintMsg              ;to print message only (note world 1-7 will only
  lda #VictoryMusic         ;reach this code if counter = 0, and will always branch)
  sta EventMusicQueue       ;otherwise load victory music first (world 8 only)
PrintMsg:
  tya                       ;put primary message counter in A
  clc                       ;add $0c or 12 to counter thus giving an appropriate value,
  adc #$0c                  ;($0c-$0d = first), ($0e = world 1-7's), ($0f-$12 = world 8's)
  sta VRAM_Buffer_AddrCtrl  ;write message counter to vram address controller
IncMsgCounter:
  lda SecondaryMsgCounter
  clc
  adc #$04                      ;add four to secondary message counter
  sta SecondaryMsgCounter
  lda PrimaryMsgCounter
  adc #$00                      ;add carry to primary message counter
  sta PrimaryMsgCounter
  cmp #$07                      ;check primary counter one more time
SetEndTimer:
  bcc ExitMsgs                  ;if not reached value yet, branch to leave
  lda #$06
  sta WorldEndTimer             ;otherwise set world end timer
IncModeTask_A:
  inc OperMode_Task             ;move onto next task in mode
ExitMsgs:
  rts                           ;leave
.endproc
.popseg

.pushseg
.segment "OBJECT_EX"
.proc NativeRarePlayerEndWorld
  jsr NativeRarePlayerEndWorldCore
  jsr BillNativeCaptureP
.if ::MAPPER_MMC3
  ; Public entry SP=s. Selector push ->s-1; JSR common ->s-3;
  ; bank push ->s-4; target JSR ->s-6; one X-save ->s-7.
  ; Thus original selector is at $0107,X; actual stack oracle guards it.
  txa
  pha
  tsx
  lda $0107,x
  sta BillNativeReturnSelector
  pla
  tax
  lda BillNativeReturnSelector
.else
  lda #0
  sta BillNativeReturnSelector
.endif
  rts
.endproc
.proc NativeRarePlayerEndWorldCore

  lda WorldEndTimer          ;check to see if world end timer expired
  bne EndExitOne             ;branch to leave if not
  ldy WorldNumber            ;check world number
  cpy #World8                ;if on world 8, player is done with game, 
  bcs EndChkBButton          ;thus branch to read controller
  lda #$00
  sta AreaNumber             ;otherwise initialize area number used as offset
  sta LevelNumber            ;and level number control to start at area 1
  sta OperMode_Task          ;initialize secondary mode of operation
  ; jroweboy added:
  ; disable the screen since loading a new area pointer will change CHR banks
  inc DisableScreenFlag
  inc WorldNumber            ;increment world number to move onto the next world
  jsr LoadAreaPointer        ;get area address offset for the next area
  inc FetchNewGameTimerFlag  ;set flag to load game timer from header
  lda #MODE_GAMEPLAY
  sta OperMode               ;set mode of operation to game mode
EndExitOne:
  rts                        ;and leave
EndChkBButton:
  lda SavedJoypad1Bits
  ora SavedJoypad2Bits       ;check to see if B button was pressed on
  and #B_Button              ;either controller
  beq EndExitTwo             ;branch to leave if not
  lda #$01                   ;otherwise set world selection flag
  sta WorldSelectEnableFlag
  lda #$ff                   ;remove onscreen player's lives
  sta NumberofLives
  jsr NativeRareRunGameOverCore::TerminateGame          ;do sub to continue other player or end game
EndExitTwo:
  rts                        ;leave
.endproc
.popseg

.proc NativeRarePrintStatusBarNumbers
  jsr NativeRarePrintStatusBarNumbersCore
  jsr BillNativeCaptureP
.if ::MAPPER_MMC3
  ; Public entry SP=s. Selector push ->s-1; JSR common ->s-3;
  ; bank push ->s-4; target JSR ->s-6; one X-save ->s-7.
  ; Thus original selector is at $0107,X; actual stack oracle guards it.
  txa
  pha
  tsx
  lda $0107,x
  sta BillNativeReturnSelector
  pla
  tax
  lda BillNativeReturnSelector
.else
  lda #0
  sta BillNativeReturnSelector
.endif
  rts
.endproc
.proc NativeRarePrintStatusBarNumbersCore
  sta R0             ;store player-specific offset
  jsr OutputNumbers  ;use first nybble to print the coin display
  lda R0             ;move high nybble to low
  lsr                ;and print to score display
  lsr
  lsr
  lsr
OutputNumbers:
  clc                      ;add 1 to low nybble
  adc #$01
  and #%00001111           ;mask out high nybble
  cmp #$06
  bcs ExitOutputN
  pha                      ;save incremented value to stack for now and
    asl                      ;shift to left and use as offset
    tay
    ldx VRAM_Buffer1_Offset  ;get current buffer pointer
    lda #$20                 ;put at top of screen by default
    cpy #$00                 ;are we writing top score on title screen?
    bne SetupNums
    lda #$22                 ;if so, put further down on the screen
SetupNums:
    sta VRAM_Buffer1,x
    lda StatusBarData,y      ;write low vram address and length of thing
    sta VRAM_Buffer1+1,x     ;we're printing to the buffer
    lda StatusBarData+1,y
    sta VRAM_Buffer1+2,x
    sta R3                   ;save length byte in counter
    stx R2                   ;and buffer pointer elsewhere for now
  pla                      ;pull original incremented value from stack
  tax
  lda StatusBarOffset,x    ;load offset to value we want to write
  sec
  sbc StatusBarData+1,y    ;subtract from length byte we read before
  tay                      ;use value as offset to display digits
  ldx R2 
DigitPLoop:
  lda DisplayDigits,y      ;write digits to the buffer
  sta VRAM_Buffer1+3,x    
  inx
  iny
  dec R3                   ;do this until all the digits are written
  bne DigitPLoop
  lda #$00                 ;put null terminator at end
  sta VRAM_Buffer1+3,x
  inx                      ;increment buffer pointer by 3
  inx
  inx
  stx VRAM_Buffer1_Offset  ;store it in case we want to use it again
ExitOutputN:
  rts
  

;-------------------------------------------------------------------------------------
;$00 - used to store status bar nybbles
;$02 - used as temp vram offset
;$03 - used to store length of status bar number

;status bar name table offset and length data
StatusBarData:
  .byte $f0, $06 ; top score display on title screen
  .byte $62, $06 ; player score
  .byte $62, $06
  .byte $6d, $02 ; coin tally
  .byte $6d, $02
  .byte $7a, $03 ; game timer

StatusBarOffset:
  .byte TopScoreDisplay + TopScoreLastIndex - DisplayDigits + 1
  .byte Player1ScoreDisplay + PlayerScoreLastIndex - DisplayDigits + 1
  .byte Player2ScoreDisplay + PlayerScoreLastIndex - DisplayDigits + 1
  .byte Player1CoinDisplay + PlayerCoinLastIndex - DisplayDigits + 1
  .byte Player2CoinDisplay + PlayerCoinLastIndex - DisplayDigits + 1
  .byte GameTimerDisplay + GameTimerLastIndex - DisplayDigits + 1
.endproc

.proc NativeRareTransposePlayers
  jsr NativeRareTransposePlayersCore
  jsr BillNativeCaptureP
.if ::MAPPER_MMC3
  ; Public entry SP=s. Selector push ->s-1; JSR common ->s-3;
  ; bank push ->s-4; target JSR ->s-6; one X-save ->s-7.
  ; Thus original selector is at $0107,X; actual stack oracle guards it.
  txa
  pha
  tsx
  lda $0107,x
  sta BillNativeReturnSelector
  pla
  tax
  lda BillNativeReturnSelector
.else
  lda #0
  sta BillNativeReturnSelector
.endif
  rts
.endproc
.proc NativeRareTransposePlayersCore
  sec                       ;set carry flag by default to end game
  lda NumberOfPlayers       ;if only a 1 player game, leave
  beq ExTrans
  lda OffScr_NumberofLives  ;does offscreen player have any lives left?
  bmi ExTrans               ;branch if not
  lda CurrentPlayer         ;invert bit to update
  eor #%00000001            ;which player is on the screen
  sta CurrentPlayer
  ldx #$06
TransLoop:
  lda OnscreenPlayerInfo,x    ;transpose the information
  pha                         ;of the onscreen player
    lda OffscreenPlayerInfo,x   ;with that of the offscreen player
    sta OnscreenPlayerInfo,x
  pla
  sta OffscreenPlayerInfo,x
  dex
  bpl TransLoop
  clc            ;clear carry flag to get game going
ExTrans:
  rts
.endproc

.pushseg
.segment "GUEST"
.proc NativeRareGetAreaMusic
  jsr NativeRareGetAreaMusicCore
  jsr BillNativeCaptureP
.if ::MAPPER_MMC3
  ; Public entry SP=s. Selector push ->s-1; JSR common ->s-3;
  ; bank push ->s-4; target JSR ->s-6; one X-save ->s-7.
  ; Thus original selector is at $0107,X; actual stack oracle guards it.
  txa
  pha
  tsx
  lda $0107,x
  sta BillNativeReturnSelector
  pla
  tax
  lda BillNativeReturnSelector
.else
  lda #0
  sta BillNativeReturnSelector
.endif
  rts
.endproc
.proc NativeRareGetAreaMusicCore
  lda OperMode           ;if in title screen mode, leave
  beq ExitGetM
  lda AltEntranceControl ;check for specific alternate mode of entry
  cmp #$02               ;if found, branch without checking starting position
  beq ChkAreaType        ;from area object data header
  ldy #$05               ;select music for pipe intro scene by default
  lda PlayerEntranceCtrl ;check value from level header for certain values
  cmp #$06
  beq StoreMusic         ;load music for pipe intro scene if header
  cmp #$07               ;start position either value $06 or $07
  beq StoreMusic
ChkAreaType:
  ldy AreaType           ;load area type as offset for music bit
  lda CloudTypeOverride
  beq StoreMusic         ;check for cloud type override
  ldy #$04               ;select music for cloud type level if found
StoreMusic:
  lda MusicSelectData,y  ;otherwise select appropriate music for level type
  sta AreaMusicQueue     ;store in queue and leave
ExitGetM:
  rts
.endproc
.popseg

.proc NativeRareHandlePipeEntry
  jsr NativeRareHandlePipeEntryCore
  jsr BillNativeCaptureP
.if ::MAPPER_MMC3
  ; Exactly the original down/foot/warp branch performs the mapped read.
  ; These source input fields are unchanged by the completed core.
  lda Up_Down_Buttons
  and #4
  beq CallerSelector
  lda R0
  cmp #$11
  bne CallerSelector
  lda R1
  cmp #$10
  bne CallerSelector
  lda WarpZoneControl
  beq CallerSelector
  lda #7 | PRG_FIXED_8
  sta BillNativeReturnSelector
  rts
CallerSelector:
  txa
  pha
  tsx
  lda $0107,x
  sta BillNativeReturnSelector
  pla
  tax
  lda BillNativeReturnSelector
.else
  lda #0
  sta BillNativeReturnSelector
.endif
  rts
.endproc
.proc NativeRareHandlePipeEntryCore
  lda Up_Down_Buttons       ;check saved controller bits from earlier
  and #%00000100            ;for pressing down
  beq RTSOpCode               ;if not pressing down, branch to leave
  lda R0
  cmp #$11                  ;check right foot metatile for warp pipe right metatile
  bne RTSOpCode               ;branch to leave if not found
  lda R1
  cmp #$10                  ;check left foot metatile for warp pipe left metatile
  bne RTSOpCode               ;branch to leave if not found
  lda #$30
  sta ChangeAreaTimer       ;set timer for change of area
  lda #$03
  sta GameEngineSubroutine  ;set to run vertical pipe entry routine on next frame
  lda #Sfx_PipeDown_Injury
  sta Square1SoundQueue     ;load pipedown/injury sound
  ; lda #1
  ; jsr SetupPipeTransitionOverlay
  ; lda Player_X_Position
  ; sec
  ; sbc ScreenLeft_X_Pos
  ; sta PipeXPosition
  ; lda Player_Y_Position
  ; clc
  ; adc #32
  ; sta PipeYPosition
  lda #%00100000
  sta Player_SprAttrib      ;set background priority bit in player's attributes
  lda WarpZoneControl       ;check warp zone control
  beq ExPipeE               ;branch to leave if none found
  and #%00000011            ;mask out all but 2 LSB
  asl
  asl                       ;multiply by four
  tax                       ;save as offset to warp zone numbers (starts at left pipe)
  lda Player_X_Position     ;get player's horizontal position
RTSOpCode = * + 1
  cmp #$60      
  bcc GetWNum               ;if player at left, not near middle, use offset and skip ahead
  inx                       ;otherwise increment for middle pipe
  cmp #$a0      
  bcc GetWNum               ;if player at middle, but not too far right, use offset and skip
  inx                       ;otherwise increment for last pipe
GetWNum:
  ; TODO stop being bad and using a far call for this one thing
  jsr BillNativeReadWarp     ; original mapped-data read stays resident.
  dey                       ;decrement for use as world number
  sty WorldNumber           ;store as world number and offset
  ldx WorldAddrOffsets,y    ;get offset to where this world's area offsets are
  lda AreaAddrOffsets,x     ;get area offset based on world offset
  sta AreaPointer           ;store area offset here to be used to change areas
  lda #Silence
  sta EventMusicQueue       ;silence music
  lda #$00
  sta EntrancePage          ;initialize starting page number
  sta AreaNumber            ;initialize area number used for area address offset
  sta LevelNumber           ;initialize level number used for world display
  sta AltEntranceControl    ;initialize mode of entry
  ; inc Hidden1UpFlag         ;set flag for hidden 1-up blocks
  inc FetchNewGameTimerFlag ;set flag to load new game timer
ExPipeE:
  rts                       ;leave!!!
.endproc

.proc NativeRarePlayerHeadCollision
  jsr NativeRarePlayerHeadCollisionCore
  jsr BillNativeCaptureP
.if ::MAPPER_MMC3
  ; Original compiled far/endfar always selects 7|PRG_FIXED_8, literally.
  lda #7 | PRG_FIXED_8
.else
  lda #0
.endif
  sta BillNativeReturnSelector
  rts
.endproc
.proc NativeRarePlayerHeadCollisionCore
  pha                      ;store metatile number to stack
    lda #$11                 ;load unbreakable block object state by default
    ldx SprDataOffset_Ctrl   ;load offset control bit here
    ldy PlayerSize           ;check player's size
.if ::ENABLE_CROSSOVER
    jsr CrossoverBlockSize
    tya
    beq GuestBigBlock
      lda #$11
      bne GuestBlockState
GuestBigBlock:
    lda #$12
GuestBlockState:
.else
    bne :+
      lda #$12
:
.endif
    sta Block_State,x        ;store into block object buffer
    farcall DestroyBlockMetatile ;store blank metatile in vram buffer to write to name table
    ldx SprDataOffset_Ctrl   ;load offset control bit
    lda R2                   ;get vertical high nybble offset used in block buffer routine
    sta Block_Orig_YPos,x    ;set as vertical coordinate for block object
    tay
    lda R6                   ;get low byte of block buffer address used in same routine
    sta Block_BBuf_Low,x     ;save as offset here to be used later
    lda (R6),y              ;get contents of block buffer at old address at $06, $07
    jsr BlockBumpedChk       ;do a sub to check which block player bumped head on
    sta R0                   ;store metatile here
    ldy PlayerSize           ;check player's size
.if ::ENABLE_CROSSOVER
    jsr CrossoverBlockSize
    tya
    beq GuestBlockTileReady
    lda R0
GuestBlockTileReady:
.else
    bne :+
      tya
:
.endif

    bcc PutMTileB            ;if no match was found in previous sub, skip ahead
      ldy #$11                 ;otherwise load unbreakable state into block object buffer
      sty Block_State,x        ;note this applies to both player sizes
      lda #$c4                 ;load empty block metatile into A for now
      ldy R0                   ;get metatile from before
      cpy #$58                 ;is it brick with coins (with line)?
      beq StartBTmr            ;if so, branch
        cpy #$5d                 ;is it brick with coins (without line)?
        bne PutMTileB            ;if not, branch ahead to store empty block metatile
StartBTmr:
.if ::ENABLE_CROSSOVER
      lda SelectedCharacter
      beq NativeCoinTimer
      farcall MegaManCoinBrick
      jmp PutMTileB
NativeCoinTimer:
.endif
      lda BrickCoinTimerFlag   ;check brick coin timer flag
      bne :+             ;if set, timer expired or counting down, thus branch
        lda #$0b
        sta BrickCoinTimer       ;if not set, set brick coin timer
        inc BrickCoinTimerFlag   ;and set flag linked to it
:  
      lda BrickCoinTimer       ;check brick coin timer
      bne :+             ;if not yet expired, branch to use current metatile
        ldy #$c4                 ;otherwise use empty block metatile
:  
      tya                      ;put metatile into A
PutMTileB:
    sta Block_Metatile,x     ;store whatever metatile be appropriate here
    jsr SophiaHeadBlockOrigin ;same native initialization, then exact source-head cell
    ldy R2                   ;get vertical high nybble offset
    lda #$23
    sta (R6),y               ;write blank metatile $23 to block buffer
    lda #$10
    sta BlockBounceTimer     ;set block bounce timer
  pla                      ;pull original metatile from stack
  sta R5                   ;and save here
.if ::ENABLE_CROSSOVER
  lda SelectedCharacter
  beq NativeBlockY
  ; Guest head probes do not share Mario's tall/small offsets. The saved
  ; buffer row is authoritative for the bounce and its emerging power-up.
  lda Block_Orig_YPos,x
  clc
  adc #$20
  sta Block_Y_Position,x
  jmp BlockYReady
NativeBlockY:
.endif
  ldy #$00                 ;set default offset
  lda CrouchingFlag        ;is player crouching?
  bne SmallBP              ;if so, branch to increment offset
    lda PlayerSize           ;is player big?
    beq BigBP                ;if so, branch to use default offset
SmallBP:
    iny                      ;increment for small or big and crouching
BigBP:
  lda Player_Y_Position    ;get player's vertical coordinate
  clc
  adc BlockYPosAdderData,y ;add value determined by size
  and #$f0                 ;mask out low nybble to get 16-pixel correspondence
  sta Block_Y_Position,x   ;save as vertical coordinate for block object
BlockYReady:
  ldy Block_State,x        ;get block object state
  cpy #$11
  beq :+                   ;if set to value loaded for unbreakable, branch
    jsr BrickShatter         ;execute code for breakable brick
    jmp InvOBit              ;skip subroutine to do last part of code here
:   
  jsr BumpBlock            ;execute code for unbreakable brick or question block
InvOBit:
  lda SprDataOffset_Ctrl   ;invert control bit used by block objects
  eor #$01                 ;and floatey numbers
  sta SprDataOffset_Ctrl
  rts                      ;leave!


;--------------------------------

.endproc
.pushseg
.segment "OBJECT_EX"
NativeRareContinueGame:
  jsr NativeRareRunGameOverCore::ContinueGame
  jsr BillNativeCaptureP
.if ::MAPPER_MMC3
  ; Public entry SP=s. Selector push ->s-1; JSR common ->s-3;
  ; bank push ->s-4; target JSR ->s-6; one X-save ->s-7.
  ; Thus original selector is at $0107,X; actual stack oracle guards it.
  txa
  pha
  tsx
  lda $0107,x
  sta BillNativeReturnSelector
  pla
  tax
  lda BillNativeReturnSelector
.else
  lda #0
  sta BillNativeReturnSelector
.endif
  rts
.popseg
BillNativeRareEnd:
.assert BillNativeRareEnd-BillSourceBodyStart <= 1679,error,"Bill/native layout exceeds old MM2 audio tail"
.popseg
.pushseg
.segment "LOWCODE"
.proc BillNativeReadWarp
  far RENDER
  ldy WarpZoneNumbers,x
  endfar
  rts
.endproc
.popseg

.pushseg
.if ::MAPPER_MMC3
.segment "SAMUS_CROUCH_BODY"
.else
.segment "LOWCODE"
.endif
BillNativeCaptureP:
  sta BillNativeReturnA
  php
  pla
  sta BillNativeReturnP
  lda BillNativeReturnA
  rts
BillNativeRestoreP:
  lda BillNativeReturnP
  pha
  lda BillNativeReturnA
  plp
  rts
.popseg

.pushseg
.if ::MAPPER_MMC3
.segment "SAMUS_CROUCH_BODY"
.else
.segment "LOWCODE"
.endif
BillRareCallCommon:
.if ::MAPPER_MMC3
  ; Retain the target bank in the existing self-modified operand; no third
  ; RAM cell or global pending-shadow state. Each nested caller owns its
  ; original selector on the real stack until its corresponding return.
  SMC_StoreValue NextBank, a
  lda BankShadow
  pha
  SMC_LoadValue NextBank, a
.endif
  jsr FarCallCommon
.if ::MAPPER_MMC3
  pla ; release this invocation's input selector
  lda BillNativeReturnSelector
  sta BankShadow
  sta BANK_SELECT
.endif
  jmp BillNativeRestoreP
.popseg

; Append in the existing bank9 tail. Only an admitted ordinary Sophia head
; collision overrides Mario's center-derived block position. Projectile
; callers already publish their own contacted cell and remain unchanged.
.pushseg
.segment "BILL_BODY_COLD"
.proc SophiaHeadBlockOrigin
  ; Other characters tail-call the native initializer: the caller reloads A
  ; and flags, and this keeps their common bump timing close to the original.
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  jne InitBlock_XY_Pos
  jsr InitBlock_XY_Pos
  php
  pha
  lda MmBlockAttack
  bne Done
  bit SmCeilingHit
  bpl Done
  lda RgTempX
  and #$f0
  sta Block_X_Position,x
  lda RgTempPage
  sta Block_PageLoc,x
  sta Block_PageLoc2,x
Done:
  pla
  plp
  rts
.endproc
.popseg
