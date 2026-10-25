.pushseg
.segment "FIXED"
.proc MegaManClimbCheck
  BillRareCall UnionMegaManClimbCheck
.endproc
.proc MegaManBounceVelocity
  php
.if ::ENABLE_MMC5_EXPANDED
  farcall X5StompDispatch
.else
  farcall MegaManBounceVelocityModes
.endif
  plp
  rts
.endproc
.proc EasyLinkFirebarBridge
  ; All paths enter only after native distance admission, before direction write.
  php
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  beq FirebarSource
  cmp #CHARACTER_SOPHIA
  bne FirebarRestore
FirebarSource:
  tsx
  cpx #$c0
  bcc FirebarDeep
.if ::MAPPER_MMC3
  lda BankShadow
  pha
.endif
  lda NextBank_SMC+1
  pha
  lda SafecallA_SMC+1
  pha
  lda FarcallJmpTarget_SMC+1
  pha
  lda FarcallJmpTarget_SMC+2
  pha
  lda SafereturnA_SMC+1
  pha
  farcall CrossoverSourceFirebarDisjoint
  pla
  sta SafereturnA_SMC+1
  pla
  sta FarcallJmpTarget_SMC+2
  pla
  sta FarcallJmpTarget_SMC+1
  pla
  sta SafecallA_SMC+1
  pla
  sta NextBank_SMC+1
.if ::MAPPER_MMC3
  pla
  sta BankShadow
  sta BANK_SELECT
.endif
  bcc FirebarRestore
  plp
  jmp NoColFB
FirebarDeep:
FirebarRestore:
  plp
FirebarNative:
  ldx #1
  lda R4
  jmp FirebarNativeDirectionCompare
.endproc
EasyLinkFirebarBridgeEnd:
.proc MegaManSpringVelocity
  php
.if ::ENABLE_MMC5_EXPANDED
  farcall X5SpringDispatch
.else
  farcall MegaManSpringVelocityModes
.endif
  plp
  rts
.endproc
; These resident bridges consume only the old unreachable 209-EA spring
; padding. The actual spring entry21 bytes and all subsequent PCs are fixed.
.proc RyuSourceBodyAfterBGBridge
  jsr MegaManSlideSmallGap
  php
  pha
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  beq Project
  cmp #CHARACTER_RYU
  bne Bill
Project:
  farcall CrossoverSourceBodyDispatch
  jmp Done
Bill:
  cmp #CHARACTER_BILL
  bne Done
  lda #2
  jsr BillHotProject
Done:
  pla
  plp
  rts
.endproc
.proc BillBodyCall
  farcall BillBodyDispatch, jmp
.endproc
.proc BillHeadDispatch
  lda SelectedCharacter
  cmp #CHARACTER_RYU
  beq Ryu
  cmp #CHARACTER_BILL
  bne :+
    jmp BillHotRawHead
    .if !::MAPPER_MMC3
    nop
    nop
    .endif ; M3 recovers four inert dispatcher bytes for the contextual union.
  :
  cmp #CHARACTER_SOPHIA
  beq Guest
  cmp #CHARACTER_SAMUS
  beq Guest
  cmp #CHARACTER_SCROOGE
  bne Native
Guest:
  farcall CrossoverGuestHeadProbe
Return:
  rts
Native:
.if ::ENABLE_MMC5_EXPANDED
  jmp KbNativeHeadBridge
Ryu:
.else
  jmp BlockBufferColli_Head
Ryu:
.endif
  jsr BlockBufferColli_Head
  .if !::MAPPER_MMC3
  nop
  nop
  .endif
  farcall RyuSourceHeadGate, jmp
.endproc

; Cached row/height getters are resident: ordinary walking and water do not
; fetch a bank merely to decode the already selected source form.
.if ::MAPPER_MMC3
.pushseg
.segment "LOWCODE"
.endif
.proc BillCachedTerrainRow
  ldy BillSourceBodyForm
  lda Rows,y
  tay
  sec
  rts
.pushseg
.segment "LOWCODE"
Rows: .byte 6,5,5
.popseg
.endproc
.if ::MAPPER_MMC3
.popseg
.endif
.if ::MAPPER_MMC3
.pushseg
.segment "LOWCODE"
.endif
.proc BillCachedWaterHeight
  ldy BillSourceBodyForm
  lda Hi,y
  pha
  lda Lo,y
  tay
  pla
  rts
Hi: .byte 31,16,15
Lo: .byte $80,$40,0
.endproc
.if ::MAPPER_MMC3
.popseg
.endif
.pushseg
.segment "LOWCODE"
.proc BillHeadConsumer
  jsr CrossoverHeadProbe         ; raw source-cell query remains independently visible.
  php
  pha
  beq Return
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bne Return
  lda Player_Y_Speed
  bpl Return
  lda #5
  jsr BillBodyCall               ; filtered requery may find a second real ceiling.
  pla
  plp
  lda R3                        ; admitted tile/pointer; preserve original C/V/D/I.
  rts
Return:
  pla
  plp                           ; foreign A/X/Y/P are byte-exact raw getter output.
  rts
.endproc
.popseg

.proc EasyLinkHeadResponseBridge
  lda SelectedCharacter
  eor #CHARACTER_LINK
  ora CrossoverBehaviorVersion
  bne NativeHead
  php
  phx
  tsx
  cpx #$c0                      ; bounded deep-stack fallback before farcall.
  bcc DeepHead
  plx
  .if ::MAPPER_MMC3
  lda BankShadow
  pha
  .endif
  lda NextBank_SMC+1
  pha
  lda SafecallA_SMC+1
  pha
  lda FarcallJmpTarget_SMC+1
  pha
  lda FarcallJmpTarget_SMC+2
  pha
  lda SafereturnA_SMC+1
  pha
  farcall EasyLinkHeadResponse
  pla
  sta SafereturnA_SMC+1
  pla
  sta FarcallJmpTarget_SMC+2
  pla
  sta FarcallJmpTarget_SMC+1
  pla
  sta SafecallA_SMC+1
  pla
  sta NextBank_SMC+1
.if ::MAPPER_MMC3
  pla
  sta BankShadow
  sta BANK_SELECT
.endif
  plp
  lda #1                        ; old NYSpd A/N/Z, exact incoming C/V.
  jmp DoFootCheck
DeepHead:
  plx
  plp
NativeHead:
  lda #1
  sta Player_Y_Speed
  jmp DoFootCheck
.endproc
EasyLinkHeadResponseBridgeEnd:

.proc MegaManVineAnchor
  jsr BillNativeCaptureP ; original routine preserves incoming full P/A.
  BillRareCall UnionMegaManVineAnchor
.endproc

.segment "PLAYER"
.proc MegaManClimbing
  lda #0
  sta PlayerSize
  sta CrouchingFlag
  sta MmSliding
  sta MmVX
  sta MmVX+1
  sta MmVX+2
  sta Player_X_Speed
  sta Player_X_Scroll
  lda SavedJoypadBits
  and #3
  sta MmVineButtons
  lda MmOnVine
  bne Existing
  lda #1
  sta MmOnVine
  lda #0
  sta MmVineExit
  sta MmClimbFrame
  sta MmClimbTimer
  jmp SaveButtons
Existing:
  lda MmVineButtons
  eor #$ff
  and MmVineLastButtons
  beq SaveButtons
    lda #1
    sta MmVineExit
SaveButtons:
  lda MmVineButtons
  sta MmVineLastButtons
  cmp #3
  jeq Vertical
  cmp #0
  jeq Vertical
  lda MmVineExit
  jeq Vertical
  lda MmVineButtons
  sta PlayerFacingDir
  cmp #1
  beq Right
  sec
  lda Player_X_Position
  sbc #9
  sta Player_X_Position
  lda Player_PageLoc
  sbc #0
  jmp ExitVine
Right:
  clc
  lda Player_X_Position
  adc #9
  sta Player_X_Position
  lda Player_PageLoc
  adc #0
ExitVine:
  sta Player_PageLoc
  lda #2
  sta Player_State
  lda #0
  sta MmVY
  sta MmVY+1
  sta MmVY+2
  sta Player_Y_Speed
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bcc :+
 .if ::ENABLE_MMC5_EXPANDED
    farcall Cv3MovementGate
 .else
    farcall RosterMovement
 .endif
    rts
  :
  cmp #CHARACTER_SAMUS
  bne :+
    farcall SamusMovement
    rts
  :
  farcall MegaManMovement, jmp
Vertical:
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  bne :+
    lda MmStepTimer
    beq StepReady
    dec MmStepTimer
StepReady:
    lda SavedJoypadBits
    and #3
    sta MmPreviousDir
  :
  lda #0
  sta MmVY
  sta MmVY+1
  sta MmVY+2
  lda SavedJoypadBits
  and #Up_Dir
  bne Up
  lda SavedJoypadBits
  and #Down_Dir
  beq Move
  lda #$55
  sta MmVY
  lda #$15
  sta MmVY+1
  lda #1
  sta MmVY+2
  bne Move
Up:
  lda #$ab
  sta MmVY
  lda #$ea
  sta MmVY+1
  lda #$fe
  sta MmVY+2
Move:
  farcall MegaManMovement::Vertical, jmp
.endproc

.segment "GUEST"
.proc MegaManPowerupCharge
  lda PlayerStatus
  cmp #1
  bne Clear
  jsr MegaManWeapons::Release
Clear:
  lda #0
  sta MmChargeFrames
  sta MmCharging
  rts
.endproc
.popseg

.pushseg
.segment "SOPHIA_BODY_COLD"
.proc MegaManSpringVelocityModes
  php
  pha
  phx                             ; The caller's X is the native spring slot.
  lda SelectedCharacter
  bne :+
    farcall MarioSourceSpring
    jmp Done
  :
  cmp #CHARACTER_SAMUS
  beq Samus
  cmp #CHARACTER_MEGAMAN
  jne OtherGuest
  lda CrossoverBehaviorVersion
  bne MegaHard
  lda #$ab
  sta MmVY
  lda #$aa
  sta MmVY+1
  lda #$fc                     ; Classic400.
  sta MmVY+2
  lda JumpspringForce
  cmp #$f4
  bne Store
  lda #$55
  sta MmVY
  lda #$d5
  sta MmVY+1
  lda #$f8                     ; Classic860.
  sta MmVY+2
  jmp Store
MegaHard:
  lda #$ab
  sta MmVY
  lda #$0a
  sta MmVY+1
  lda #$fc                       ; MegaManBase default spring power 475.
  sta MmVY+2
  lda JumpspringForce
  cmp #$f4
  bne Store
    lda #$ab
    sta MmVY
    lda #$aa
    sta MmVY+1
    lda #$f7                     ; MegaManBase boosted spring power 1000.
    sta MmVY+2
Store:
  lda MmVY+2
  sta Player_Y_Speed
  lda #1
  sta Player_State
  ldx SelectedCharacter
  cpx #CHARACTER_SOPHIA
  bne :+
    sta RgDoubleJump             ; Source SpringObj.springLaunch sets jumped.
  :
  lda #0
  sta MmJumpReleased
  sta MmFrictionYActive
Done:
  plx
  pla
  plp
  rts
Samus:
  lda #1
  sta SmSourceJumped
  lda #0
  sta MmVY
  lda #$80
  sta MmVY+1
  lda #$fd
  sta MmVY+2
  lda JumpspringForce
  cmp #$f4
  bne Store
  lda #$ab
  sta MmVY
  lda #$2a
  sta MmVY+1
  lda #$fa
  sta MmVY+2
  jmp Store
OtherGuest:
  lda SelectedCharacter
  beq Done                      ; Mario retains the chosen original engine.
  cmp #CHARACTER_LUIGI
  beq Done                      ; Luigi now uses that same native spring engine.
  cmp #CHARACTER_LINK
  bne IndexedSpring
  lda CrossoverBehaviorVersion
  bne IndexedSpring
  ; Linked1.0 Link:400/800;2.02 remains450/950 in the indexed table.
  lda #$ab
  sta MmVY
  lda #$aa
  sta MmVY+1
  lda #$fc
  sta MmVY+2
  lda JumpspringForce
  cmp #$f4
  bne LinkStore
  lda #$55
  sta MmVY
  sta MmVY+1
  lda #$f9
  sta MmVY+2
LinkStore:
  lda #0
  sta XgRise
  jmp Store
IndexedSpring:
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bne :+
    lda #$80
    sta RgDoubleJump
  :
  lda SelectedCharacter
  sec
  sbc #CHARACTER_BILL
  tax
  lda JumpspringForce
  cmp #$f4
  bne :+
    txa
    clc
    adc #10
    tax
  :
  lda SpringLo,x
  sta MmVY
  lda SpringMid,x
  sta MmVY+1
  lda SpringHi,x
  sta MmVY+2
  lda #0
  sta XgRise
  jmp Store
; Bill, Link, Simon, Pit, Rygar (adapted), Luigi, Bass, Ryu, Sophia.
SpringLo: .byte $ab,0,$55,$55,0,$55,$ab,$55,$ab,0, $55,$55,$ab,$ab,0,$ab,$ab,$ab,0,0
SpringMid:.byte $aa,$40,$d5,$d5,$80,$d5,$0a,$d5,$aa,0, $55,$15,$aa,$aa,0,$aa,$aa,$aa,$40,0
SpringHi: .byte $fc,$fc,$fb,$fb,$fa,$fb,$fc,$fb,$fc,$fa, $f9,$f8,$f7,$f7,$f5,$f7,$f7,$f7,$f8,$f4
.endproc
.popseg

.pushseg
.segment "TITLE"
.proc MegaManBounceVelocityModes
  php
  pha
  lda SelectedCharacter
  bne :+
    farcall MarioSourceBounce
    jmp Done
  :
  cmp #CHARACTER_LUIGI
  beq Done                      ; Preserve native Mario-style stomp velocity.
  cmp #CHARACTER_LINK
  bne :+
    lda #$ab                    ; Link2.02 bounce power325/120.
    sta MmVY
    lda #$4a
    sta MmVY+1
    lda #$fd
    sta MmVY+2
    sta Player_Y_Speed
    jmp Done
  :
  lda #0
  sta MmVY
  lda #$80
  sta MmVY+1
  lda #$fd                       ; 300 Flash px/sec = 2.5 NES px/frame
  sta MmVY+2
  sta Player_Y_Speed
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bne :+
    lda #$80
    sta RgDoubleJump
    bne Done
  :
  cmp #CHARACTER_SIMON
  bne Done
  lda #1
  sta RgDoubleJump
Done:
  pla
  plp
  rts
.endproc
.popseg
