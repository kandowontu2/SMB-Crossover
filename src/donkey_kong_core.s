; Original DK is an NPC. Playable input/SMB movement/tier rules are authored;
; barrel1px motion, six-update roll animation and original graphics are sourced.
; Component only: no menu/shared/native admission is claimed by this file.
.include "donkey_kong_state.inc"
.macro DkGate
 .local Own
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_DONKEY_KONG
 beq Own
 pla
 plp
 rts
Own:
 pla
 plp
.endmacro
.pushseg
.segment "DONKEY_KONG_CORE"
DkCoreStart:

; Exact owner gate precedes every overlay access. Fresh activation uses this
; explicit constructor even if the foreign overlay happens to contain44.
.proc DkConstruct
 DkGate
 lda #0
 ldx #$7f
Clear:
 sta $5c00,x
 dex
 bpl Clear
 lda #$44
 sta DkReady
 lda NumberofLives
 sta DkLife
 lda AreaAddrsLOffset
 sta DkArea
 lda WorldNumber
 sta DkWorld
 lda #$ff
 sta DkPaletteAck
 lda #0
 sta PlayerStatus
 sta PlayerSize                 ;DK's visual/collision never shrinks.
 rts
.endproc

; Real loaded-scene loader calls this; AreaPointer may already be a future
; bonus-pipe destination. Retain earned tier across scenes and extra lives.
.proc DkEnterScene
 DkGate
 lda DkTier
 pha
 jsr DkConstruct
 pla
 cmp #3
 bcc Restore
 lda #0
Restore:
 sta DkTier
 sta PlayerStatus
 rts
.endproc
.proc DkEnsure
 DkGate
 lda DkReady
 cmp #$44
 bne Fresh
 lda NumberofLives
 sec
 sbc DkLife
 bmi Fresh
 lda NumberofLives
 sta DkLife
 lda AreaAddrsLOffset
 cmp DkArea
 bne Scene
 lda WorldNumber
 cmp DkWorld
 beq Done
Scene:
 jmp DkEnterScene
Fresh:
 jmp DkConstruct
Done:
 rts
.endproc

; A=physical native Mushroom0/Flower1. The host still owns actual emergence,
; collection, erase,1000points,pickup sound and transform freeze exactly once.
; Native Star/1Up return Cclear untouched; no automatic grants.
.proc DkGrant
 DkGate
 cmp #2
 bcs Native
 pha
 txa
 pha
 jsr DkEnsure
 pla
 tax
 pla
 cmp #1
 beq Flower
 lda DkTier
 cmp #2
 bcs Store
 clc
 adc #1
 bne Store
Flower:
 lda #2
Store:
 sta DkTier
 sta PlayerStatus
 lda #0
 sta PlayerSize
 sec
 rts
Native:
 clc
 rts
.endproc
.proc DkFullPower
 DkGate
 jsr DkEnsure
 lda #2
 sta DkTier
 sta PlayerStatus
 lda #0
 sta PlayerSize
 rts
.endproc

; Every actual active Main calls this once at the movement admission point.
; It consumes only genuine SavedJoypadBits. Down+B selects the earned vertical
; barrel at tier2. A uses the real native Mario jump; no extra jump is invented.
.proc DkMovement
 DkGate
 jsr DkEnsure
 lda GameEngineSubroutine
 cmp #8
 bne Native
 jsr DkClock
Native:
 lda #0
 sta PlayerSize
 sta CrouchingFlag              ;no original DK crouching pose.
 farcall CrossoverVanillaMovement,jmp
.endproc
.proc DkClock
 lda SavedJoypadBits
 eor DkPrevious
 and SavedJoypadBits
 sta DkFresh
 lda SavedJoypadBits
 sta DkPrevious
 lda Player_X_Speed
 beq Idle
 inc DkWalkDelay
 lda DkWalkDelay
 cmp #6
 bcc Attack
 lda #0
 sta DkWalkDelay
 lda DkWalk
 eor #1
 sta DkWalk
 jmp Attack
Idle:
 lda #0
 sta DkWalkDelay
 sta DkWalk
Attack:
 lda DkAttack
 beq Start
 inc DkAge
 lda DkAge
 cmp #16
 bne Expire
 lda #1
 sta DkSpawn
Expire:
 lda DkAge
 cmp #24
 bcc Done
 lda #0
 sta DkAttack
 sta DkSpawn
 rts
Start:
 lda DkFresh
 and #$40
 beq Done
 lda #1
 sta DkAttack
 lda DkTier
 cmp #2
 bne Begin
 lda SavedJoypadBits
 and #4
 beq Begin
 inc DkAttack
Begin:
 lda #0
 sta DkAge
 sta DkSpawn
Done:
 rts
.endproc

; Native collision adaptation: preserve source NPC42x32 physical bounds
; within its48x32 canvas. Signed horizontal offsets need sign extension at
; the actual host bounding-box consumer; a14px legacy box is insufficient.
.proc DkBounds
 DkGate
 lda #$f3                      ;left -13 from native Player_X_Position.
 sta R0
 lda #0
 sta R1
 lda #29
 sta R2
 lda #32
 sta R3
 rts
.endproc

; Actual successful spawn. Cset/X=record offset. A full pool preserves the
; pending event until the current throw expires; it never replaces a live shot.
.proc DkSpawnBarrel
 DkGate
 lda DkSpawn
 jeq No
 lda DkTier
 clc
 adc #1
 sta DkTemp
 ldx #0
Find:
 lda DkShots,x
 beq Free
 dec DkTemp
 beq No
 txa
 clc
 adc #12
 tax
 bne Find
Free:
 lda DkAttack
 sta DkShots,x
 cmp #2
 lda #1                       ;source horizontal toss starts tile84.
 bcc Frame
 lda #4
Frame:
 sta DkShots+1,x
 lda #0
 sta DkShots+2,x
 sta DkShots+8,x
 sta DkShots+9,x
 sta DkShots+10,x
 sta DkShots+11,x
 sta DkSpawn
 lda #240
 sta DkShots+3,x
 lda PlayerFacingDir
 sta DkShots+7,x
 cmp #2
 beq Left
 lda Player_X_Position
 clc
 adc #24
 sta DkShots+4,x
 lda Player_PageLoc
 adc #0
 jmp Page
Left:
 lda Player_X_Position
 sec
 sbc #24
 sta DkShots+4,x
 lda Player_PageLoc
 sbc #0
Page:
 sta DkShots+5,x
 lda Player_Y_Position
 clc
 adc #16
 sta DkShots+6,x
 sec
 rts
No:
 clc
 rts
.endproc

; X=0/12/24, DkQuery=REAL current SMB terrain classification.
; Source DB34 horizontal1px, DBEE roll four frames every6 updates.
; Source DC69 off-edge drop1px and horizontal only when new Y is odd.
; Vertical straight drop uses1px without the original room-specific ladder/
; platform tables. Landing in SMB hands off to rolling in its launch direction.
.proc DkBarrelStep
 DkGate
 lda DkShots,x
 jeq Done
 dec DkShots+3,x
 jeq Retire
 lda DkShots,x
 cmp #2
 beq Vertical
 lda DkQuery
 and #1
 bne OnFloor
 lda #1
 sta DkShots+9,x
 inc DkShots+6,x
 lda DkShots+6,x
 and #1
 beq Animate
 bne Horizontal
OnFloor:
 lda #0
 sta DkShots+9,x
Horizontal:
 lda DkQuery
 and #2
 beq Move
 lda DkShots+7,x
 eor #3
 sta DkShots+7,x             ;authored SMB wall response.
Move:
 lda DkShots+7,x
 cmp #2
 beq MoveLeft
 inc DkShots+4,x
 bne Animate
 inc DkShots+5,x
 jmp Animate
MoveLeft:
 lda DkShots+4,x
 bne LowLeft
 dec DkShots+5,x
LowLeft:
 dec DkShots+4,x
Animate:
 inc DkShots+2,x
 lda DkShots+2,x
 cmp #6
 bcc End
 lda #0
 sta DkShots+2,x
 lda DkShots+7,x
 cmp #2
 beq RollLeft
 lda DkShots+1,x
 sec
 sbc #1
 jmp RollFrame
RollLeft:
 lda DkShots+1,x
 clc
 adc #1
RollFrame:
 and #3
 sta DkShots+1,x
End:
 lda DkShots+6,x
 cmp #240
 bcs Retire
Done:
 rts
Vertical:
 lda DkQuery
 and #1
 beq Fall
 lda #1
 sta DkShots,x
 lda #0
 sta DkShots+1,x
 jmp Horizontal
Fall:
 inc DkShots+6,x
 lda DkShots+1,x
 eor #1
 sta DkShots+1,x
 jmp End
Retire:
 lda #0
 sta DkShots,x
 rts
.endproc
DkCoreEnd:
.popseg
