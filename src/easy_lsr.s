; Private original-source Link/Simon gates. Mode0=Easy,1=Hard.
; No SRAM aliases/new persistent fields. Roster movement is in TITLE; helpers
; occupy space vacated in ROSTER by its separately audited farcall-only move.
.pushseg
.segment "ROSTER"
.proc EasyRosterSpecial
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne Axe
  lda #5
  farcall RosterWeapons::FindType
  bcs Done
  farcall RosterWeapons::SpawnBoomerang
  jmp Pose
Axe:
  farcall RosterWeapons::CountShots
  lda PlayerStatus
  cmp RgCount                 ; status0..2 permits1..3 already-live projectiles.
  bcc Done
  lda #6
  sta AvPending
Pose:
  lda #1
  sta RgAttackKind
  farcall RosterWeapons::StartAttack
Done:
  rts
.endproc

; Entry A=original damage,Y=type. Every foreign kind returns literal A.
; A-only result; preserves X/Y and has no RAM/scratch writes.
.segment "GUEST"
.proc EasyLsrDamage
  pha
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  beq Link
  cmp #CHARACTER_SIMON
  bne Original
  cpy #22
  beq Axe
  lda CrossoverBehaviorVersion
  bne Original
  cpy #19
  beq D34
  cpy #20
  beq D50
  cpy #21
  beq D80
  bne Original
Axe:
  lda CrossoverBehaviorVersion
  beq Original                ; Original table60 is the Easy axe damage.
  pla
  lda #75                     ; Hard2.02 source axe damage.
  rts
Link:
  lda CrossoverBehaviorVersion
  bne Original
  cpy #14
  beq D34
  cpy #23
  beq D34
  cpy #15
  beq D50
  cpy #24
  beq D50
  cpy #16
  beq D75
  cpy #25
  beq D75
Original:
  pla
  rts
D34: pla
  lda #34
  rts
D50: pla
  lda #50
  rts
D75: pla
  lda #75
  rts
D80: pla
  lda #80
  rts
.endproc
.segment "ROSTER"

.proc EasyWhipEligible
  lda CrossoverBehaviorVersion
  bne No
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  beq Link
  cmp #CHARACTER_SIMON
  bne No
  lda MmBulletType
  cmp #19
  bcc No
  cmp #22
  bcs No
  sec
  rts
Link:
 .if ::ENABLE_MMC5_EXPANDED
  jsr Z2LegacyEasyProbeType
 .else
  lda MmBulletType
 .endif
  cmp #14
  bcc No
  cmp #17
  bcc Yes
  cmp #23
  bcc No
  cmp #26
  bcs No
Yes: sec
  rts
No: clc
  rts
.endproc

; Exact source old active whip endpoints for an INTEGER native target box.
; ceil(min)/floor(max) is equivalent to comparing the Q16 attack interval to
; that target's integer endpoints. Native enemy proxy geometry stays native.
; MmBillEdge* is unused by Simon; Bill never enters this admission.
.proc EasyWhipPrepare
  jsr EasyWhipEligible
  jcc Done
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne Whip
  farcall EasyLinkRectPrepare
  rts
Whip:
  phx
  phy
  ldx PlayerStatus
  lda PlayerFacingDir
  cmp #1
  bne Left
  lda #16
  ldy MmXFraction+1
  cpy #$80
  bcc RightMin
  bne RightExtra
  ldy MmXFraction
  beq RightMin
RightExtra:
  lda #17                     ; ceil(PX+15.5+fraction).
RightMin:
  ldy #0
  jsr StoreX
  lda RightMax,x              ; floor(PX+44/57/69+fraction).
  ldy #1
  jsr StoreX
  jmp Vertical
Left:
  lda LeftMin,x               ; ceil(PX-28/-41/-53+fraction).
  ldy MmXFraction
  bne LeftExtra
  ldy MmXFraction+1
  beq LeftReady
LeftExtra:
  clc
  adc #1
LeftReady:
  ldy #0
  jsr StoreX
  lda #0                      ; floor(PX+.5+fraction).
  ldy MmXFraction+1
  cpy #$80
  bcc LeftMax
  lda #1
LeftMax:
  ldy #1
  jsr StoreX
Vertical:
  lda RgCrouch
  beq Stand
  txa
  clc
  adc #3
  tax
Stand:
  lda Top,x
  sta MmBillEdgeY
  lda MmYFraction+1
  cmp TopHi,x
  bcc Bottom
  bne TopInc
  lda MmYFraction
  cmp TopLo,x
  bcc Bottom
TopInc:
  inc MmBillEdgeY
Bottom:
  lda BottomOffset,x
  sta MmBillEdgeY+1
  cpx #2                      ; Stand flame lower endpoint is an integer.
  beq TranslateY
  lda MmYFraction+1
  cmp BotHi,x
  bcc TranslateY
  bne BottomInc
  lda MmYFraction
  cmp BotLo,x
  bcc TranslateY
BottomInc:
  inc MmBillEdgeY+1
TranslateY:
  lda MmBillEdgeY
  clc
  adc Player_Y_Position
  sta MmBillEdgeY
  lda MmBillEdgeY+1
  clc
  adc Player_Y_Position
  sta MmBillEdgeY+1
  ply
  plx
Done:
  rts
StoreX:
  sta RgTemp3
  clc
  adc Player_X_Position
  sta MmBillEdgeX,y
  lda #0
  bit RgTemp3
  bpl Positive
  lda #$ff
Positive:
  adc Player_PageLoc
  sta MmBillEdgePage,y
  rts
RightMax: .byte 44,57,69
LeftMin: .byte <(-28),<(-41),<(-53)
Top: .byte 10,11,11,17,18,18
BottomOffset: .byte 16,17,18,23,24,24
TopLo: .byte $67,$01,$01,$67,$01,$67
TopHi: .byte $06,$80,$00,$06,$80,$06
BotLo: .byte $67,$00,0,$67,$00,$67
BotHi: .byte $06,$80,0,$06,$80,$06
.endproc

.proc EasyWhipEnvelope
  jsr EasyWhipEligible
  bcc Done
  lda MmBillEdgeX
  sec
  sbc ScreenLeft_X_Pos
  sta BoundingBox_UL_Corner+28
  lda MmBillEdgeX+1
  sec
  sbc ScreenLeft_X_Pos
  sta BoundingBox_LR_Corner+28
  lda MmBillEdgeY
  sta BoundingBox_UL_Corner+29
  lda MmBillEdgeY+1
  sta BoundingBox_LR_Corner+29
Done: rts
.endproc

.proc EasyWhipProbe
  jsr EasyWhipEligible
  bcc Done
  phy
  lda MmProbeIndex
  and #1
  eor #1
  tay
  lda MmProbeIndex
  cmp #4
  bcs Middle
  lda MmBillEdgeX,y
  sta MmProbeX
  lda MmBillEdgePage,y
  sta MmProbePage
  jmp Vertical
Middle:
  sec
  lda MmBillEdgeX+1
  sbc MmBillEdgeX
  lsr
  clc
  adc MmBillEdgeX
  sta MmProbeX
  lda MmBillEdgePage
  adc #0
  sta MmProbePage
  lda MmProbeIndex
  cmp #8
  bcc Vertical
  and #1
  bne Minus16
  clc
  lda MmProbeX
  adc #16
  sta MmProbeX
  lda MmProbePage
  adc #0
  sta MmProbePage
  jmp Vertical
Minus16:
  sec
  lda MmProbeX
  sbc #16
  sta MmProbeX
  lda MmProbePage
  sbc #0
  sta MmProbePage
Vertical:
  lda MmProbeIndex
  and #2
  lsr
  tay
  lda MmBillEdgeY,y
  sta MmProbeY
  ply
Done: rts
.endproc

; Entry A=native RadiusX. Only Easy chain needs the additional middle probes.
.proc EasyWhipProbeRadius
  pha
  lda SelectedCharacter
  cmp #CHARACTER_SIMON
  bne Original
  jsr EasyWhipEligible
  bcc Original
  lda PlayerStatus
  beq Original
  pla
  lda #22
  rts
Original: pla
  rts
.endproc
 .if ::ENABLE_MMC5_EXPANDED
; Link-only entry. Valid variant0/1: preserve original type/C for classic,
; return type0 for ZeldaII so its real sword point is never replaced by a
; legacy whip rectangle. X/Y/RAM unchanged; original caller does CMP#14.
.proc Z2LegacyEasyProbeType
  lda Z2Variant
  eor #1
  lsr a
  bcc Done
  lda MmBulletType
Done:rts
.endproc
 .endif
.popseg
