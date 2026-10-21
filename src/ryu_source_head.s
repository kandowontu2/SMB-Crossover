; PRIVATE UNAPPLIED source head admission. No new persistent state.
; The broad rejection uses every audited unrotated Ryu HRect's envelope.
; Exact positive response is deliberately narrower; qualifications in contract.
.pushseg
.segment "ROSTER"
RyuSourceHeadStart:
.proc RyuSourceHeadGate
  ; Resident caller has already run the ORIGINAL native head query. The
  ; farcall restores its tile A and preserves query C/V; RP_Save snapshots
  ; all original query registers, flags and thirteen scratch bytes.
  RP_Save
  lda R3                         ; RP_Save's load/push macros clobber A.
  bne :+
    farcall RyuCornerHeadGate
    jmp Native
  :
  sta RgTemp3                    ; actual queried metatile, before scratch use.
  cpy #51
  beq Profile
  cpy #58
  beq Profile
  cpy #65
  jne Native
Profile:
  lda GameEngineSubroutine
  cmp #8
  jne Native
  lda Player_State
  cmp #3
  jcs Native                     ; vine/pipe/flag dispatch remains separate.
  lda GuestHurtTicks
  jne Native                     ; nonInteractive is a separate source gate.
  lda Player_Y_HighPos
  cmp #1
  jne Native
  lda Player_Y_Position
  cmp #224
  jcs Native                     ; no 8-bit PY+32 or terrain row wrapping.
  lda R2
  cmp #$d0
  jcs Native                     ; valid rows0..12 only.
  lda Player_PageLoc
  cmp #$ff
  bne Family
  lda Player_X_Position
  cmp #241
  jcs Native                     ; source body's right endpoint must not wrap.
Family:
  ldy RgTemp3
  lda MTileAttribute,y
  and #MTILE_SOLID | MTILE_CLIMB
  cmp #MTILE_SOLID
  jne Native
  ; Coins/pole/vine, axe and real SpringObj have distinct source dispatch.
  ; $23 is a transient native bumped-block hole, not an authored Ground.
  cpy #$23
  jeq Native
  cpy #$66
  jeq Native
  cpy #$67
  jeq Native
  cpy #$c2
  jeq Native
  cpy #$c3
  jeq Native
  cpy #$c5
  jeq Native
  lda R2
  clc
  adc #$30
  sta RgTempY                    ; queried cell bottom = (R2+32)+16.
  lda Player_Y_Position
  clc
  adc #5                         ; envelope27: current top PY+5.
  cmp RgTempY
  jcc EnvelopeBottom
  jne Handled
  lda MmYFraction
  ora MmYFraction+1
  jne Handled                    ; equality only when all Q16 fractions zero.
EnvelopeBottom:
  lda R2
  clc
  adc #$20
  sta RgTemp2                    ; cell top.
  lda Player_Y_Position
  clc
  adc #32                        ; every audited source pose ends at the foot.
  cmp RgTemp2
  jcc Handled
  ; Head X adder8 lies strictly inside both source horizontal endpoints
  ; PX+1.25..PX+14.75 for every native/Q16 fraction, so no X test is lost.

  ; Exact current25 response: source ordinary rising ground-jump/air body.
  ; Retained attack/throw cache transitions remain separate unfinished work.
  ; A spring can launch while source ST_ATTACK retains its ground27 frame.
  lda Player_State
  cmp #1
  jne Native
  lda XgJumpUsed
  jeq Native
  lda RgCrouch
  ora CrouchingFlag
  ora RgAttack
  ora MmUnderwater
  ora SwimmingFlag
  ora XgWall
  ora XgWallLock
  ora RyPlatformSlot
  ora AvSlash
  ora RyWallResolved
  jne Native
  lda AreaType
  jeq Native                     ; water profile/cache ordering not guessed.
  lda MmVY+2
  jpl Native
  cmp Player_Y_Speed
  jne Native
  cmp #$fb
  jcc Native
  bne Speed
  lda MmVY+1
  cmp #$80                       ; no stronger launch than ordinary -4.5.
  jcc Native
Speed:
  ; abs(qVX)<=101035 ($018AAB), the established normal source cap.
  lda MmVX+2
  bpl Positive
  sec
  lda #0
  sbc MmVX
  sta R0
  lda #0
  sbc MmVX+1
  sta R1
  lda #0
  sbc MmVX+2
  jmp XHigh
Positive:
  lda MmVX
  sta R0
  lda MmVX+1
  sta R1
  lda MmVX+2
XHigh:
  cmp #1
  bcc Current25
  jne Native
  lda R1
  cmp #$8a
  bcc Current25
  jne Native
  lda R0
  cmp #$ac
  jcs Native
Current25:
  lda Player_Y_Position
  clc
  adc #7
  cmp RgTempY
  bcc Previous
  jne Handled
  lda MmYFraction
  ora MmYFraction+1
  jne Handled
Previous:
  ; Only direct-below source axes proven without a pose cache are admitted.
  ; No stale RyWallOld* reads: previousQ=currentQ-integrated qV, valid only
  ; for the guarded no-wall/no-platform/no-hurt ordinary integration path.
  sec
  lda MmYFraction
  sbc MmVY
  sta R0
  lda MmYFraction+1
  sbc MmVY+1
  sta R1
  lda Player_Y_Position
  sbc MmVY+2
  ; Snapshot is from the actual pre-integration source-shaped ordinary
  ; body. Require its previousY to equal currentQ-integratedV exactly;
  ; retained/incoherent histories keep the original conservative27 path.
  tay                            ; keep reconstructed previous integerY.
  lda RyWallSupported
  beq Prior27
  lda RyWallOldHeight
  cmp #25
  bne Prior27
  lda RyWallWasGround
  cmp #1
  bne Prior27
  cpy RyWallOldY
  bne Prior27
  lda R0
  cmp RyWallOldYFine
  bne Prior27
  lda R1
  cmp RyWallOldYFrac
  bne Prior27
  ; Do not mistake unsigned16 worldwrap for a real adjacent-page step.
  ; Lastworldpage sourcefidelity remains a qualified nativefallback.
  lda RyWallOldPage
  cmp #$ff
  beq Prior27
  ; Source hWidth13.5: integer delta[-5,+5], arbitraryQ16 fractions,
  ; implies actual delta strictly within(-6,+6). HeadpointPX+8 is then
  ; strictly inside cached sourceX bounds oldPX+1.25..oldPX+14.75.
  ; Signed16 subtraction handles real adjacent-page seams too.
  lda Player_X_Position
  sec
  sbc RyWallOldX
  sta RgTemp2                    ; old celltop scratch is no longer used.
  lda Player_PageLoc
  sbc RyWallOldPage
  beq PriorPositiveX
  cmp #$ff
  bne Prior27
  lda RgTemp2
  cmp #$fb
  bcc Prior27
  bcs Prior25
PriorPositiveX:
  lda RgTemp2
  cmp #6
  bcs Prior27
Prior25:
  tya
  clc
  adc #7                         ; actual cached previous25 top.
  jmp PriorTopReady
Prior27:
  tya
  clc
  adc #5                         ; unchanged conservative fallback.
PriorTopReady:
  cmp RgTempY
  jcc Native
  ; qVX cap and head X adder8 put this same tile point STRICTLY inside
  ; previous source X bounds for every fraction; exact numeric proof pinned.
  ldy RgTemp3
  lda MTileAttribute,y
  and #MTILE_BUMP
  bne Resolve
  lda BlockBounceTimer
  jne Native                     ; native/source block lifecycle not guessed.
Resolve:
  lda RgTempY
  sec
  sbc #7
  pha                            ; source canonical Y survives native effects.
  ldy RgTemp3
  lda MTileAttribute,y
  and #MTILE_BUMP
  bne NoBlockEffects
  lda RgTemp3
  jsr PlayerHeadCollision        ; resident original block effects, exactly once.
NoBlockEffects:
  pla
  sta Player_Y_Position
  lda #0
  sta MmYFraction
  sta MmYFraction+1
  sta MmVY+2
  sta Player_Y_Speed
  lda #$55
  sta MmVY
  lda #$d5
  sta MmVY+1                     ; 100Flash px/s /120 = Q16 $00D555.
  lda #Sfx_Bump
  ora Square1SoundQueue
  sta Square1SoundQueue
  jsr RyuPlatformBox
Handled:
  RP_Restore
  lda #0                         ; return no second native head response.
  rts
Native:
  RP_Restore                     ; original tile/query flags/scratch exactly.
  rts
.endproc
RyuSourceHeadEnd:
.assert RyuSourceHeadEnd-RyuSourceHeadStart <= 832, error, "Head helper exceeds private ROSTER budget"
.popseg
