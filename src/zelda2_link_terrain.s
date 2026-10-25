; Authenticated Zelda II terrain points in SMB physical coordinates.
; Crouching keeps the original full-height terrain profile. Fairy lower side
; samples are deliberately centered: the original's second left index reaches
; six pixels outside its sprite. No new persistent RAM or borrowed player pose.
.pushseg
.segment "TMNT_COMBAT"
.proc Z2HeadAdmission
 cmp #CHARACTER_LINK
 bne Legacy
 lda Z2Variant
 beq Legacy
 lda GameEngineSubroutine
 cmp #8
 bne LegacyReload
 pla
 plp
 farcall Z2TerrainHead,jmp
LegacyReload:lda SelectedCharacter
Legacy:jmp TnCv3HeadGate ; Transfer the caller's existing saved A/P unchanged.
.endproc

.segment "M3_LOGIC"
.proc Z2SideAdmission
 lda SelectedCharacter
 cmp #CHARACTER_LINK
 bne Legacy
 lda Z2Variant
 beq Legacy
 lda GameEngineSubroutine
 cmp #8
 bne Legacy
 farcall Z2TerrainSide,jmp
Legacy:jmp M3SideDispatch
.endproc

.segment "LM_CORE"
.proc LmWallGate
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_LINK
 bne Legacy
 lda Z2Variant
 beq Legacy
 lda GameEngineSubroutine
 cmp #8
 bne Legacy
 pla
 plp
 farcall Z2TerrainWall,jmp
Legacy:pla
 plp
 jmp Z2WallLegacy
.endproc

.segment "Z2_COLD"
Z2ProbeDX=Z2BodyScratch
Z2ProbeDY=Z2BodyScratch+1
Z2ProbeIndex=Z2BodyScratch+2
Z2ProbeY=Z2BodyScratch+3
Z2ProbePage=Z2BodyScratch+4
Z2ProbeTemp=Z2BodyScratch+5
Z2TerrainTargetY=Z2BodyScratch+10
Z2TerrainPreviousY=Z2BodyScratch+11

.proc Z2MovementTerrainBegin
 lda #0
 sta SmCeilingHit
 lda Player_Y_Position
 sta Z2TerrainPreviousY
 lda Player_X_Position
 sta MmOldX
 lda Player_State
 bne Air
 lda #4
 bne Contacts
Air:lda #0
Contacts:sta Z2NativeContacts
 lda Player_CollisionBits
 eor #$ff
 and #3
 ora Z2NativeContacts
 sta Z2NativeContacts
 rts
.endproc

.proc Z2HeadWithinTerrain
 lda SelectedCharacter
 cmp #CHARACTER_SOPHIA
 beq Sophia
 cmp #CHARACTER_LINK
 bne Legacy
 lda Z2Variant
 beq Legacy
 lda Z2ActiveSpells
 and #8
 clc
 adc Player_Y_Position
 cmp #32
 rts
Legacy:jmp PlayerHeadWithinTerrain
Sophia:
 lda MmYFraction+1
 asl
 lda Player_Y_Position
 adc #16
 cmp #32
 rts
.endproc

.proc Z2SourceFeetDispatch
 lda SelectedCharacter
 cmp #CHARACTER_SOPHIA
 bne Link
 farcall SophiaSourceFeet,jmp
Link:
 lda Z2Variant
 beq Legacy
 lda GameEngineSubroutine
 cmp #8
 bne Legacy
 jmp Z2TerrainFeet
Legacy:jmp BlockBufferColli_Feet
.endproc

; Read a real block-buffer cell without temporarily rewriting player X/Y.
; R0/R1 and Local_eb remain owned by PlayerBGCollision. Return its query Y.
.proc Z2TerrainRead
 lda Player_X_Position
 clc
 adc Z2ProbeDX
 sta R5
 lda Player_PageLoc
 adc #0
 sta Z2ProbePage
 and #1
 asl
 asl
 asl
 asl
 sta Z2ProbeTemp
 lda R5
 lsr
 lsr
 lsr
 lsr
 ora Z2ProbeTemp
 jsr GetBlockBufferAddr
 lda Player_Y_Position
 clc
 adc Z2ProbeDY
 bcs Empty
 sta Z2ProbeY
 cmp #32
 bcc Empty
 cmp #240
 bcs Empty
 and #$f0
 sec
 sbc #32
 sta R2
 tay
 lda (R6),y
 sta R3
Return:
 ldx #0
 ldy Z2ProbeIndex
 lda R3
 rts
Empty:
 lda #0
 sta R3
 jmp Return
.endproc

.proc Z2TerrainHead
 sty Z2ProbeIndex
 lda Z2ActiveSpells
 and #8
 sta Z2ProbeDY ; Normal head0; Fairy head8.
 ldx #4
 beq :+
 cmp #0
 beq :+
 ldx #6
:stx Z2ProbeDX
 jsr Z2TerrainRead
 bne Sampled
 lda #12
 ldx Z2ProbeDY
 beq :+
 lda #10
:sta Z2ProbeDX
 jsr Z2TerrainRead
Sampled:
 lda Player_Y_Position
 and #15
 sta R4
 lda R3
 beq Return
 ldx Player_Y_Speed
 bpl Return
 ldx R3
 lda MTileAttribute,x
 and #MTILE_SOLID|MTILE_CLIMB
 cmp #MTILE_SOLID
 bne Return
 lda R2
 clc
 adc #48 ; Actual contacted cell bottom, including the HUD offset.
 bcs Return
 sta Z2ProbeTemp
 lda Z2TerrainPreviousY
 clc
 adc Z2ProbeDY
 bcs Return
 cmp Z2ProbeTemp
 bcc Return ; Side overlap is not an upward ceiling crossing.
 lda Z2ProbeTemp
 sec
 sbc Z2ProbeDY
 sta Z2TerrainTargetY
 sta Player_Y_Position
 lda #1
 sta SmCeilingHit
 lda #4
 sta R4 ; Admit native effects despite the corrected zero-origin nibble.
Return:
 ldx #0
 ldy Z2ProbeIndex
 lda R3
 rts
.endproc

.proc Z2TerrainFeet
 iny
 sty Z2ProbeIndex
 tya
 sec
 sbc Local_eb
 tax
 lda FootX-1,x ; Only source foot indices+1/+2 enter this routine.
 sta Z2ProbeDX
 lda #32
 ldx Z2ActiveSpells
 txa
 and #8
 beq Ordinary
 lda Z2ProbeDX
 cmp #4
 beq :+
 lda #10
 bne FairyX
:lda #6
FairyX:sta Z2ProbeDX
 lda #26
 bne Offset
Ordinary:lda #32
Offset:sta Z2ProbeDY
 jsr Z2TerrainRead
 lda Z2ProbeY
 and #15
 sta R4 ; Actual foot penetration, not the sprite origin's low nibble.
 lda Z2ActiveSpells
 and #8
 beq Return
 lda Player_Y_Speed
 bmi Return
 lda R3
 beq Return
 cmp #$5f
 beq Return
 cmp #$60
 beq Return
 cmp #$c2
 beq Return
 cmp #$c3
 beq Return
 cmp #$26
 beq Return
 ldx R3
 lda MTileAttribute,x
 and #MTILE_SOLID|MTILE_CLIMB
 cmp #MTILE_SOLID
 bne Return
 lda R4
 cmp #5
 bcs Return
 lda SmCeilingHit
 ora #$80 ; Only a real Fairy floor sample may correct native floor alignment.
 sta SmCeilingHit
 lda R2
 clc
 adc #6 ; Cell top+32 minus Fairy's26px foot.
 sta Z2TerrainTargetY
Return:ldx #0
 ldy Z2ProbeIndex
 lda R3
 rts
FootX:.byte 4,12
.endproc

.proc Z2TerrainSide
 sty Z2ProbeIndex
 lda #1
 ldx R0
 cpx #1
 bne :+
 lda #15
:sta Z2ProbeDX
 tya
 cmp Local_eb
 beq Upper
 lda #26
 bne Offset
Upper:lda #6
Offset:sta Z2ProbeDY
 lda Z2ActiveSpells
 and #8
 beq Query
 lda #3
 cpx #1
 bne :+
 lda #13
:sta Z2ProbeDX
 lda Z2ProbeDY
 cmp #6
 bne LowerFairy
 lda #12
 bne FairyY
LowerFairy:lda #24
FairyY:sta Z2ProbeDY
Query:jsr Z2TerrainRead
 lda Player_X_Position
 and #15
 sta R4
 ldx #0
 ldy Z2ProbeIndex
 lda R3
 rts
.endproc

.proc Z2TerrainWall
 ; The query's exact column is authoritative, including page boundaries.
 lda R6
 sec
 sbc #<Block_Buffer_1
 and #15
 asl
 asl
 asl
 asl
 sta Z2ProbeTemp
 lda Player_PageLoc
 sta Z2ProbePage
 lda R6
 sec
 sbc #<Block_Buffer_1
 and #16
 lsr
 lsr
 lsr
 lsr
 eor Player_PageLoc
 and #1
 beq PageReady
 lda Player_X_Position
 bmi NextPage
 dec Z2ProbePage
 bne PageReady
 beq PageReady
NextPage:inc Z2ProbePage
PageReady:
 lda Z2ActiveSpells
 and #8
 beq Normal
 lda #14
 ldx R0
 cpx #1
 beq Right
 lda #13
 bne Left
Normal:lda #16
 ldx R0
 cpx #1
 beq Right
 lda #15
Left:clc
 adc Z2ProbeTemp
 sta Player_X_Position
 lda Z2ProbePage
 adc #0
 jmp Page
Right:sta Z2ProbeDX
 lda Z2ProbeTemp
 sec
 sbc Z2ProbeDX
 sta Player_X_Position
 lda Z2ProbePage
 sbc #0
Page:sta Player_PageLoc
 lda #16
 sta SideCollisionTimer
 lda R0
 eor #$ff
 and Player_CollisionBits
 sta Player_CollisionBits
 lda #0
 sta Z2NativeVX
 sta Z2NativeXFraction
 sta MmVX
 sta MmVX+1
 sta MmVX+2
 sta MmXFraction
 sta MmXFraction+1
 sta Player_X_Speed
 sta Player_X_Scroll
 sec
 rts
.endproc

.proc Z2AfterBGDispatch
 lda SelectedCharacter
 cmp #CHARACTER_SAMUS
 bne Link
 farcall SamusAfterBGCollision,jmp
Link:
 lda Z2Variant
 beq Done
 lda SmCeilingHit
 and #1
 bne Ceiling
 ; Fairy motion always exports airborne. State0 here was a real native land.
 lda Player_State
 bne Clear
 lda Z2TerrainTargetY
 sta Player_Y_Position
 jmp Stop
Ceiling:
 lda Z2TerrainTargetY
 sta Player_Y_Position
 lda #1
 sta Player_Y_Speed
 sta Z2NativeVY
Stop:lda #0
 sta Z2NativeGravityFraction
 sta MmYFraction
 sta MmYFraction+1
Clear:lda #0
 sta SmCeilingHit
Done:rts
.endproc
.popseg
