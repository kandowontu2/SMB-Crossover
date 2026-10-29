; Independent SMB host services, not shared admission or native integration.
; Pinned host Sunny55e87482 / source d97e4858; source Rogue1.21 9271411a.
; Approved A95 A600..BFFF. Include the FROZEN helpers in the same segment.
; All character-state public entries gate raw2/variant1 before overlay reads.
; The cell query is private to admitted callbacks; its inputs are not host ZP.
; No inventory owner/MP/health aliases and no temporary character swaps.
.include "rogue_dawn_state.inc"
RdHostService=$5c79
RdHostEntryA=$5fb7
.assert RdPlayerUpdating=$5c17,error,"same immutable component constant"
.assert RdMorphCooldown=$5c1b,error,"same immutable component constant"
.assert RdHurtClock=$5c1c,error,"same immutable component constant"
.assert RdHurtDirection=$5c1d,error,"same immutable component constant"
.assert RdContactFlags=$5c1e,error,"same immutable component constant"
.assert RdHurtBlink=$5c1f,error,"same immutable component constant"
.assert RdDoorMove=$5c7e,error,"same immutable component constant"
.assert RdSourceAltPalette=$5c7d,error,"same immutable component constant"
.assert RdWeaponSpawnDX=$5c3e,error,"same immutable component constant"
.assert RdWeaponSpawnDY=$5c3f,error,"same immutable component constant"
; Existing SOURCE arithmetic/Wave metadata temporaries. Geometry saves/restores
; all6 on its real stack. Host NMI can overwrite global R0..R3, never these.
; Unmorph Stage->Offset->Commit is one declared live private-context chain;
; weapon producers reinitialize their metadata before use (finite controls).
Rh2=$5c31
Rh3=$5c32
Rh4=$5c33
Rh5=$5c35
Rh6=$5c36
Rh7=$5c37

; Target bank124 is entered only by the REAL resident farcall owner. Its A95
; caller must not change $5115 while executing in A95. C94 remains ART/bridge.
.macro RdHsLeaf Target
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #($80|124)
 jsr FarCallCommon
.endmacro
.pushseg
.segment "ROGUE_DAWN_HOST"
.export RdHostDispatch,RdHsImportPosition,RdHsExportPosition
.export RdHsNewSession,RdHsNewLife,RdHsEnterScene,RdHsDamage,RdHsGrantType
.export RdHsRewardForRaw,RdHsPrepareActor,RdHsCollectActor,RdHsDropContact
.export RdHsActorEligible,RdHsActorContact,RdHsClockBefore,RdHsClockAfter
.export RdHsServicesStart,RdHsServicesEnd
RdHsServicesStart:

; Input AXYP is delivered unmodified to the selected real callback body.
; No jump-vector pointer in NMI-clobbered R0/R1 or additional shared SMC.
.proc RdHostDispatch
 php
 pha
 jsr RdHostEnabled
 jcc Foreign
.macro Case Id,Target
 lda RdHostService
 cmp #Id
 bne :+
 pla
 plp
 jmp Target
:
.endmacro
 Case 12,RdHsGeometry
 Case 9,RdHsGeometry
 Case 10,RdHsGeometry
 Case 11,RdHsGeometry
 Case 14,RdHsGeometry
 Case 15,RdHsGeometry
 Case 16,RdHsGeometry
 Case 17,RdHsGeometry
 Case 6,RdHsSupport
 Case 5,RdHsEnvironment
 Case 18,RdHsRelativeX
 Case 19,RdHsRelativeY
 Case 3,RdLifeDraw
 Case 21,RdHsStage
 Case 13,RdHsOffset
 Case 0,RdHsCommit
 Case 20,RdWxSpawn
 Case 8,RdHsHealth
 Case 7,RdHsLowHealth
 Case 2,RdHsNoDoor
 Case 1,RdHsNoDoor
 Case 4,RdHsNoDoor
Foreign:
 pla
 plp
 clc
 rts
.endproc

; Save6 existing private SOURCE temporaries plus incoming registers/P.
; No global ZP borrowed. Conservative choice, not a shared NMI repair: initial
; apparent R2/R3 clobber was an UNINITIALIZED audio fixture (preserved proof).
.macro RdHsSave
 php
 pha
 txa
 pha
 tya
 pha
 lda Rh2
 pha
 lda Rh3
 pha
 lda Rh4
 pha
 lda Rh5
 pha
 lda Rh6
 pha
 lda Rh7
 pha
.endmacro
; Preserve carry while restoring scratch. Each callback changes only C unless
; its explicit native-output ABI below says otherwise. Dead stack is measured.
.proc RdHsRestoreC
 pla
 sta Rh7
 pla
 sta Rh6
 pla
 sta Rh5
 pla
 sta Rh4
 pla
 sta Rh3
 pla
 sta Rh2
 bcs Yes
 pla
 tay
 pla
 tax
 pla
 plp
 clc
 rts
Yes:
 pla
 tay
 pla
 tax
 pla
 plp
 sec
 rts
.endproc

; REAL SMB two-page Block_Buffer ABI. Rh2=full world page,Rh3=visible Y,
; Rh4=low world X,Rh5=axis0up/1down/2left/3right. A=raw tile,Cset SOLID.
; Coins/axe/climb aren't solid; native invisible blocks are head-only.
; The native column table is in F127 and no indirect pointer can be raced.
; Missing loaded horizontal page is blocked, not a stale parity-page read.
; Top/bottom outside32..239 is empty: pits must fall, never wrap to buffer RAM.
.proc RdHsReadCell
 lda Player_Y_HighPos
 cmp #1
 bne Empty
 lda Rh3
 cmp #32
 bcc Empty
 cmp #240
 bcs Empty
 lda Rh2
 cmp ScreenLeft_PageLoc
 bcc Outside
 cmp ScreenRight_PageLoc
 beq Loaded
 bcs Outside
Loaded:
 lda Rh4
 lsr
 lsr
 lsr
 lsr
 sta Rh7
 lda Rh3
 and #$f0
 sec
 sbc #32
 clc
 adc Rh7
 tay
 lda Rh2
 and #1
 beq Page0
 lda Block_Buffer_2,y
 jmp Attribute
Page0:
 lda Block_Buffer_1,y
Attribute:
 sta Rh7
 cmp #$5f                    ; invisible coin/1up: no standing/side collision
 beq Invisible
 cmp #$60
 beq Invisible
 cmp #$c2                    ; native coin transaction is a separate host owner
 beq Empty
 cmp #$c3                    ; coin and axe interaction owned by real host path
 beq Empty
 cmp #$c5
 beq Empty
 tay
 lda MTileAttribute,y
 and #MTILE_SOLID|MTILE_CLIMB
 cmp #MTILE_SOLID
 beq Solid
 lda Rh7
 clc
 rts
Solid:
 lda Rh7
 sec
 rts
Invisible:
 lda Rh5
 bne Empty
 lda Rh7
 sec
 rts
Outside:
 lda #0
 sec
 rts
Empty:
 lda #0
 clc
 rts
.endproc

; A95 geometry implements all8 pixel/probe services. No coordinate separation
; warp: blocked pixel commits NOTHING; first solid sample wins. Sample current
; leading edge+one at transverse -radius/0/+radius. Authenticated body radii
; <=16 make this cover every intersecting16px cell, including page boundaries.
.proc RdHsGeometry
 RdHsSave
 lda RdHostService
 tax
 lda Axis,x
 sta Rh5                      ; 0up,1down,2left,3right
 lda #0
 sta Rh6                      ; three transverse samples, first-hit ordering
Sample:
 lda RdRoomHi
 sta Rh2
 lda RdY
 sta Rh3
 lda RdX
 sta Rh4
 lda Rh5
 cmp #2
 jcs Horizontal
 and #1
 bne Down
 lda Rh3
 sec
 sbc RdRadiusY
 sec
 sbc #1
 sta Rh3
 jmp TransverseX
; Original E4A3/E7AD tests CURRENT aligned bottom, before the next pixel.
; Testing bottom+1 prevents the final alignment pixel and repeatedly rearms
; gravity before the source running handler can reach its jump/idle checks.
Down:
 lda Rh3
 clc
 adc RdRadiusY
 sta Rh3
TransverseX:
 lda Rh6
 cmp #1
 jeq Check
 bcs XPlus
 lda Rh4
 sec
 sbc RdRadiusX
 sta Rh4
 lda Rh2
 sbc #0
 sta Rh2
 jmp Check
XPlus:
 lda Rh4
 clc
 adc RdRadiusX
 sta Rh4
 lda Rh2
 adc #0
 sta Rh2
 jmp Check
Horizontal:
 and #1
 bne Right
 lda RdRadiusX
 clc
 adc #1
 sta Rh7
 lda Rh4
 sec
 sbc Rh7
 sta Rh4
 lda Rh2
 sbc #0
 sta Rh2
 jmp TransverseY
Right:
 lda RdRadiusX
 clc
 adc #1
 sta Rh7
 lda Rh4
 clc
 adc Rh7
 sta Rh4
 lda Rh2
 adc #0
 sta Rh2
TransverseY:
 lda Rh6
 cmp #1
 beq Check
 bcs YPlus
 lda Rh3
 sec
 sbc RdRadiusY
 sta Rh3
 jmp Check
YPlus:
 lda Rh3
 clc
 adc RdRadiusY
 sta Rh3
Check:
 jsr RdHsReadCell
 bcs Blocked
 inc Rh6
 lda Rh6
 cmp #3
 jne Sample
 lda Rh5
 cmp #1
 bne TileClear
; Geometry already owns the complete saved caller/private scratch image.
; Reconstruct its only live scratch axis from immutable service9/14.
; LDA/TAX/LDA/STA preserve the query carry, with NO extra stack byte.
 jsr RdHsSupportQuery
 lda RdHostService
 tax
 lda Axis,x
 sta Rh5
 bcs Blocked
TileClear:
 lda RdHostService
 cmp #14
 bcs Clear                    ; probe cannot commit player movement
 lda Rh5
 beq MoveUp
 cmp #1
 beq MoveDown
 cmp #2
 beq MoveLeft
 inc RdX
 bne Clear
 inc RdRoomHi
 jmp Clear
MoveLeft:
 lda RdX
 bne :+
 dec RdRoomHi
:
 dec RdX
 jmp Clear
MoveUp:
 lda RdY
 bne :+
 dec Player_Y_HighPos           ; center-high context during this player phase
:
 dec RdY
 inc RdJumpDistance
 jmp Clear
MoveDown:
 inc RdY
 bne :+
 inc Player_Y_HighPos
:
 dec RdJumpDistance
Clear:
 sec
 jmp RdHsRestoreC
Blocked:
 lda RdHostService
 cmp #14
 bcs ProbeBlocked
 lda #0
 sta RdDoorMove
ProbeBlocked:
 clc
 jmp RdHsRestoreC
Axis:
 .byte $ff,$ff,$ff,$ff,$ff,$ff,$ff,$ff,$ff,1,2,3,0,$ff,1,2,3,0
.endproc

; No stale PlatformCollisionFlag accepted. True support requires an actual
; active native platform actor and CURRENT authenticated bbox touching feet.
; Existing platform/carry owner must still run its real frame after the player.
.proc RdHsSupport
 RdHsSave
.endproc
; Only true source service6 enters the saved public callback. Geometry
; service9/14 calls this private worker under its enclosing complete save.
.proc RdHsSupportQuery
 lda #0
 sta RdElevator
 sta RdFrozenSupport
 ldx #4
Loop:
 lda Enemy_Flag,x
 jeq Next
 jmi Next
 lda Enemy_ID,x
 cmp #$24
 jcc Next
 cmp #$2d
 jcs Next
 lda Enemy_State,x
 jmi Next
 lda Enemy_Y_HighPos,x
 cmp #1
 jne Next
 lda Enemy_BoundBoxCtrl,x
 asl
 asl
 tay
 lda Enemy_Y_Position,x
 clc
 adc BoundBoxCtrlData+1,y
 sta Rh2
 lda RdY
 clc
 adc RdRadiusY
 clc
 adc #1
 sec
 sbc Rh2
 cmp #2
 bcs Next
 ; Actual native bounding-box offsets, not hardcoded32/16 sprite widths.
 lda Enemy_X_Position,x
 clc
 adc BoundBoxCtrlData,y
 sta Rh2
 lda Enemy_PageLoc,x
 adc #0
 sta Rh3
 lda Enemy_X_Position,x
 clc
 adc BoundBoxCtrlData+2,y
 sta Rh4
 lda Enemy_PageLoc,x
 adc #0
 sta Rh5
 lda RdX
 clc
 adc RdRadiusX
 sta Rh6
 lda RdRoomHi
 adc #0
 cmp Rh3
 bcc Next
 bne CheckRight
 lda Rh6
 cmp Rh2
 bcc Next
CheckRight:
 lda RdX
 sec
 sbc RdRadiusX
 sta Rh6
 lda RdRoomHi
 sbc #0
 cmp Rh5
 bcc Found
 bne Next
 lda Rh4
 cmp Rh6
 bcc Next
Found:
 lda #1
 sta RdFrozenSupport
 sec
 bcs Return
Next:
 dex
 jpl Loop
 clc
Return:
 lda RdHostService
 eor #6                     ; LDA/EOR/BEQ preserve the query carry.
 beq Public
 rts
Public:jmp RdHsRestoreC
.endproc

.proc RdHsEnvironment
 php
 pha
 lda AreaType
 beq Water
 lda #$80
 bne Store
Water:
 lda #0
Store:
 sta RdEnvironment
 pla
 plp
 rts
.endproc
.proc RdHsRelativeX
 lda RdX
 sec
 sbc ScreenLeft_X_Pos
 rts
.endproc
.proc RdHsRelativeY
 lda RdY
 sec
 sbc #0                       ; SMB fixed vertical viewport, source SBC ABI
 rts
.endproc

; Stage across actual unmorph caller only: X0 (D101->D10A->D10D). Native
; Rh4/Rh5/Rh6/Rh7 are LIVE across these three callbacks, never shared ZP.
; No fake roomRAM. Full highY is kept in existing host
; Player_Y_HighPos during the center-coordinate phase, exported exactly once.
.proc RdHsStage
 cpx #0
 bne No
 lda RdRoomHi
 sta Rh6
 lda Player_Y_HighPos
 sta Rh7
 lda RdY
 sta Rh5
 lda RdX
 sta Rh4
 sec
 rts
No:clc
 rts
.endproc
.proc RdHsOffset
 cpx #0
 bne No
 lda Rh4
 clc
 adc RdWeaponSpawnDX
 sta Rh4
 lda #0
 bit RdWeaponSpawnDX
 bpl :+
 lda #$ff
:
 adc Rh6
 sta Rh6
 lda Rh5
 clc
 adc RdWeaponSpawnDY
 sta Rh5
 lda #0
 bit RdWeaponSpawnDY
 bpl :+
 lda #$ff
:
 adc Rh7
 sta Rh7
 sec
 rts
No:clc
 rts
.endproc
.proc RdHsCommit
 cpx #0
 bne No
 lda Rh4
 sta RdX
 lda Rh5
 sta RdY
 lda Rh7
 sta Player_Y_HighPos
 lda Rh6
 sta RdRoomHi
 and #1                       ; original commit final A/NZ, page is NOT masked
 sec
 rts
No:clc
 rts
.endproc
.proc RdHsSpawn
 cpy #$d0
 beq Yes
 cpy #$e0
 beq Yes
 cpy #$f0
 bne No
Yes:
 tya
 tax
 lda RdX
 clc
 adc RdWeaponSpawnDX
 sta $5b7e,x
 lda #0
 bit RdWeaponSpawnDX
 bpl :+
 lda #$ff
:
 adc RdRoomHi
 sta $5b7c,x
 lda RdY
 clc
 adc RdWeaponSpawnDY
 sta $5b7d,x
 lda $5b7c,x
 and #1                       ; native output only; full host page retained
 sec
 rts
No:clc
 rts
.endproc

; Actual native record/radius selection and approved virtual source8x8 cursor.
; Host player DrawAll remains a separate renderer hook; this is not a fake OAM
; publication. A/Y/flags are dead after this control tail; X context is live at
; the following same-update Stand/Aim D0CD path (after actual drawing).
.proc RdHsDraw
 ; Same authenticated selection/bytes as frozen RdRenderPlayer, but publish
 ; pointer bytes directly to SmPosePtr. Never hold a live pointer in R0/R1
 ; across a real host NMI; its still-unintegrated rawSamus audio can clobber it.
 lda RdSourceAltPalette
 bne Empty
 ldx RdAnimFrame
 cpx #106
 bcs Empty
 lda RdFacing
 cmp #2
 bcs Empty
 lda RdFacing
 beq Right
 lda RdBodyIndex1,x
 jmp Record
Right:
 lda RdBodyIndex0,x
Record:
 cmp #$ff
 beq Empty
 tay
 lda RdBodyRadiusY,x
 sta RdRadiusY
 lda RdBodyRadiusX,x
 sta RdRadiusX
 lda RdArtRecordLo,y
 sta SmPosePtr
 lda RdArtRecordHi,y
 sta SmPosePtr+1
 lda RdArtRecordPage,y
 clc
 adc #<RD_FIRST_CHR
 sta SmChrBank
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 jmp RdHostContextB
Empty:
 lda #<RdArtEmpty
 sta SmPosePtr
 lda #>RdArtEmpty
 sta SmPosePtr+1
 lda #0
 sta ObjectMetasprite
 jmp RdHostContextB
.endproc
.proc RdHsHealth
 sta RdHit                     ; source area3:B11C, caller passes actual0
 rts                           ; room-specific6996=E4 hazard is not fabricated
.endproc
.proc RdHsLowHealth
 clc                           ; explicit OPEN original06C4 counter/audio owner
 rts                           ; no generic SMB sound substituted/acknowledged
.endproc
.proc RdHsNoDoor
 clc                           ; source5/9 need an admitted actual SMB transition
 rts                           ; NEVER silently treat a source room as walking
.endproc

; Explicit lifecycle hooks: shared caller must identify real session/life/area
; transitions. No AreaPointer snapshot or spare hidden life counter is used.
.proc RdHsNewSession
 jsr RdHostEnabled
 bcc No
 lda #0
 ldx #5
ClearPersistent:
 sta RdGear,x
 dex
 bpl ClearPersistent
 lda #$99
 sta RdHealthLo
 lda #9
 sta RdHealthHi
 jmp RdHsEnterScene
No:rts
.endproc
.proc RdHsEnterScene
 jsr RdHostEnabled
 bcc No
 lda #0
 ldx #$7f
ClearActive:
 sta RdAction,x
 dex
 bpl ClearActive
 lda #15
 sta RdRadiusY
 lda #4
 sta RdRadiusX
 lda #8
 sta RdAnimFrame
 lda #7
 sta RdAnimIndex
 sta RdAnimReset
 lda #9
 sta $5c18                     ; real source walk cadence state
 lda SavedJoypadBits
 sta RdHeld                    ; no fabricated fresh edge on a scene transition
 lda #$80
 sta RdEnvironment
 jsr RdHsImportPosition
No:rts
.endproc
.proc RdHsNewLife
 jsr RdHostEnabled
 bcc No
 lda RdTanks
 asl
 asl
 asl
 asl
 ora #9
 sta RdHealthHi
 lda #$99
 sta RdHealthLo
 jmp RdHsEnterScene            ; approved SMB adaptation; gear/ammo retained
No:rts
.endproc
.proc RdHsImportPosition
 jsr RdHostEnabled
 bcc No
 lda Player_X_Position
 clc
 adc #8
 sta RdX
 lda Player_PageLoc
 adc #0
 sta RdRoomHi
 lda Player_Y_Position
 clc
 adc #16
 sta RdY
 lda Player_Y_HighPos
 adc #0
 sta Player_Y_HighPos           ; temporary CENTER-high, export exactly once
 sec
No:rts
.endproc
.proc RdHsExportPosition
 jsr RdHostEnabled
 bcc No
 lda RdX
 sec
 sbc #8
 sec
 sbc Player_X_Position
 sta Player_X_Scroll            ; actual committed signed pixel delta, not VX
 lda RdX
 sec
 sbc #8
 sta Player_X_Position
 lda RdRoomHi
 sbc #0
 sta Player_PageLoc
 lda RdY
 sec
 sbc #16
 sta Player_Y_Position
 lda Player_Y_HighPos
 sbc #0
 sta Player_Y_HighPos
 lda RdVY
 sta Player_Y_Speed
 lda RdVX
 sta Player_X_Speed
 bpl Speed
 eor #$ff
 clc
 adc #1
Speed:
 sta Player_XSpeedAbsolute
 lda #0
 ldx RdGravity
 beq State
 lda #1
State:
 sta Player_State               ; real source support/gravity, never pose guess
 lda RdFacing
 clc
 adc #1                       ; native host1right/2left
 sta PlayerFacingDir
 sec
No:rts
.endproc
.proc RdHsClockBefore
 jsr RdHostTickBefore
 bcc No
 jsr RdHostInput
No:rts
.endproc
.proc RdHsClockAfter
 jmp RdHostTickAfter
.endproc

; Approved resource SELECTOR ONLY. A raw0/1 -> actual Rogue item8/9/0..7.
; No gear/resource commit, actor erase, automatic collection or RNG mutation.
.proc RdHsRewardForRaw
 pha
 jsr RdHostEnabled
 bcc No
 pla
 cmp #0
 beq Tank
 cmp #1
 bne Fail
 lda RdMaxMissiles
 beq Missile
 ldx #0
 lda #1
Loop:
 and RdGear
 beq Gear
 inx
 lda Bits,x
 bne Loop
Missile:lda #9
 sec
 rts
Gear:txa
 sec
 rts
Tank:lda #8
 sec
 rts
No:pla
Fail:clc
 rts
Bits:.byte 1,2,4,8,16,32,64,128,0
.endproc

; Prepare AFTER genuine original actor construction. D0..D9 distinct typed
; records; caller supplies raw PowerUpType from its actual slot, never base0.
.proc RdHsPrepareActor
 jsr RdHostEnabled
 bcc No
 cpx #6
 bcs No
 lda Enemy_ID,x
 cmp #$2e
 bne No
 txa
 pha
 lda PowerUpType,x
 jsr RdHsRewardForRaw
 bcc RestoreNo
 ora #$d0
 tay
 pla
 tax
 tya
 sta InvPickup,x
 lda #2
 sta InvPickupOwner,x
 sec
 rts
RestoreNo:pla
 tax
No:clc
 rts
.endproc
; Genuine collection caller must have established physical player contact.
; This gate independently rejects hidden/emerging/wrong-owner/stale actors.
; Erasure/floating points happen ONCE at that original caller after Cset.
.proc RdHsCollectActor
 jsr RdHostEnabled
 bcc No
 cpx #6
 bcs No
 lda Enemy_Flag,x
 beq No
 bmi No
 lda Enemy_ID,x
 cmp #$2e
 bne No
 lda Enemy_State,x
 bpl No
 lda InvPickupOwner,x
 cmp #2
 bne No
 lda InvPickup,x
 sec
 sbc #$d0
 cmp #10
 bcs No
 txa
 pha
 lda InvPickup,x
 and #$0f
 jsr RdHsGrantType
 pla
 tax
 sec
 rts
No:clc
 rts
.endproc

; Source item61:A667/A684/A68D: authentic gear bits, Tank cap6/full refill,
; Missile Tank saturating current/max+5. Input typed0..9; no native room74.
.proc RdHsGrantType
 pha
 jsr RdHostEnabled
 bcc Foreign
 pla
 cmp #10
 bcs No
 cmp #8
 beq Energy
 bcs Missile
 tax
 lda Bits,x
 ora RdGear
 sta RdGear
 jmp Announce
Energy:
 lda RdTanks
 cmp #6
 beq Full
 inc RdTanks
Full:
 lda RdTanks
 asl
 asl
 asl
 asl
 ora #9
 sta RdHealthHi
 lda #$99
 sta RdHealthLo
 jmp Announce
Missile:
 lda #5
 RdHsLeaf RD_LEAF_ADD_MISSILE_TANK
Announce:
 lda #$40
 ora RdSfx+4
 sta RdSfx+4                    ; real source CBF9/CBFF index4 MUSIC request only
 sec
 rts
Foreign:pla
No:clc
 rts
Bits:.byte 1,2,4,8,16,32,64,128
.endproc

; Typed ACTUAL earned small drops only: A0 energy+5,A1 missile+5. Caller owns
; real collision/erase, no universal RNG/drop-rate or original room-map claim.
.proc RdHsDropContact
 pha
 jsr RdHostEnabled
 bcc Foreign
 pla
 cmp #0
 beq Health
 cmp #1
 bne No
 lda RdMissiles
 clc
 adc #5
 bcs Clamp
 cmp RdMaxMissiles
 bcc Missile
Clamp:lda RdMaxMissiles
Missile:sta RdMissiles
 lda #$80
 ora RdSfx+1
 sta RdSfx+1
 sec
 rts
Health:
 lda #$50                     ; source63:F4A9 +5 in native low BCD image
 sta Rh6
 lda #0
 sta Rh7
 jsr RdHsAddBCD
 lda #$40
 ora RdSfx+1
 sta RdSfx+1
 sec
 rts
Foreign:pla
No:clc
 rts
.endproc

; Real SMB actor eligibility, not a fake Rogue source enemy record. X0..4,
; active ordinary actor IDs0..14, no marked-dead/high-bit duplicate/turtle shell
; state20. Contact must be established externally with full page/radii. Output
; Cset means eligible, not damaged. Frozen source weapon art/physics stays own.
.proc RdHsActorEligible
 jsr RdHostEnabled
 bcc No
 cpx #5
 bcs No
 lda Enemy_Flag,x
 beq No
 bmi No
 lda Enemy_ID,x
 cmp #$15
 bcs No
 lda Enemy_State,x
 and #$20
 bne No
 sec
 rts
No:clc
 rts
.endproc
; A typed effect bitfield is delivered to the ORIGINAL actor damage owner by
; future shared hook. This entry ONLY validates actual active actor and source
; projectile record; it must never write Enemy_State/RAM HP to invent defeat.
; Y D0/E0/F0; Cset accepted; A=typed effect code ($04beam/$40missile/$80bomb)
; plus$10 Ice. These are API codes, NOT counterfeit source040C enemy flags.
.proc RdHsActorContact
 jsr RdHsActorEligible
 bcc No
 cpy #$d0
 beq Slot
 cpy #$e0
 beq Slot
 cpy #$f0
 bne No
Slot:
 lda $5b70,y
 beq No
 cmp #10
 beq Bomb
 cmp #11
 beq Missile
 cmp #3
 beq Ice
 cmp #1
 beq Beam
 cmp #2
 bne No
 beq Beam
Ice:
 lda #$14
 sec
 rts
Beam:lda #4
 sec
 rts
Missile:lda #$40
 sec
 rts
Bomb:lda #$80
 sec
 rts
No:clc
 rts
.endproc

; Source arithmetic appended below by verified recipe, generated from actual
; source62:C3DA..C42B/CEAC..CED9/CEF9..CF2D. Rh6/Rh7 are native damage/change
; BCD values, and Rh2/Rh3/Rh4 replace source01/02/03 transient nibble scratch.
.include "rogue_dawn_host_services_bcd.inc"
RdHsServicesEnd:
.assert RdHsServicesEnd-RdHsServicesStart+219 <= 6656,error,"Host plus frozen helper allocation"
.popseg
