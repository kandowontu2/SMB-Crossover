; Private source component. A3 executable and C2 state/metadata are proposals,
; not grants. Caller must authenticate/load/map them before any RAM opcode.
; R0..R3=$03..$06 are foreground pointers; native NMI$00..$02 are untouched.
ShReady=$c800
ShPrevious=$c801
ShLastEpoch=$c802
ShHaveEpoch=$c803
ShQueryTile=$c804
ShQueryClass=$c805
ShRenderSlot=$c806
ShNextDescriptor=$c807
ShOldX=$c809
ShOldY=$c80b
ShTemp=$c80d
ShEvent=$c80e
ShDrawPhase=$c80f
ShDrawBits=$c810
ShMirrorPacket=$c880          ; granted transient descriptor[C880,C900)

.segment "SHINOBI_KERNEL"
; Preserve original NULL-timer behavior after moving the animator headers.
; Initial NULL timer reads original$00 = original header low byte. Subsequent
; frame0/1 reads see the NULL pointer just written to source$00/$01 = zero.
ShReadInitialTimer:
 lda ShScratch+2
 ora ShScratch+3
 bne ShInitialHasData
 ldy ShState+$0300,x
 lda ShOriginalHeaderLo,y
 ldy #0
 rts
ShInitialHasData:
 lda (ShScratch+2),y
 rts
ShReadNextTimer:
 lda ShScratch
 ora ShScratch+1
 bne ShNextHasData
 lda #0
 rts
ShNextHasData:
 lda (ShScratch),y
 rts

; Original D1BC..D2F2 point geometry calls this SMB-specific final lookup.
; Input: source four-byte viewport X/Y at R0..R3. X actor remains intact.
; Return source class1 for native solid/non-climb,0 empty,FF outside plane.
; Native metatile is retained for the future native head/effect transaction.
ShNativeQuery:
 txa
 pha
 lda ShScratch+3
 bne ShQueryOutside
 lda ShScratch+2
 cmp #32
 bcc ShQueryOutside
 cmp #240
 bcs ShQueryOutside
 sec
 sbc #32
 sta ShState+$0009
 and #$f0
 sta ShState+$0004
 lsr
 and #$f0
 sta ShState+$0005
 lda ShScratch
 clc
 adc ScreenLeft_X_Pos
 sta ShState+$0006
 sta ShState+$000a
 lda ShScratch+1
 adc ScreenLeft_PageLoc
 and #1
 beq ShQueryFirstBuffer
 lda #<Block_Buffer_2
 bne ShQueryBuffer
ShQueryFirstBuffer:
 lda #<Block_Buffer_1
ShQueryBuffer:
 sta R6
 lda #>Block_Buffer_1
 sta R7
 lda ShState+$0006
 lsr
 lsr
 lsr
 lsr
 clc
 adc R6
 sta R6
 ldy ShState+$0004
 lda (R6),y
 sta ShQueryTile
 tax
 lda ShNativeTileAttributes,x
 and #3                     ; MTILE_SOLID|MTILE_CLIMB
 cmp #1                     ; climbing is not a solid wall/floor here
 beq ShQuerySolid
 lda #0
 beq ShQueryReturn
ShQuerySolid:
 lda #1
 sta ShState+$0007
 sta ShState+$0008
 bne ShQueryReturn
ShQueryOutside:
 lda #$ff
ShQueryReturn:
 sta ShQueryClass
 pla
 tax
 lda ShQueryClass
 rts

; Original source renderer is8x8. This typed replacement selects a packed,
; raster-verified8x16 descriptor for the exact source pose/frame/facing.
; Native MetaspriteRenderLoop owns its actual OAM allocator and clipping.
ShNativeDrawObject:
 stx ShRenderSlot
 lda ShDrawPhase
 bne ShDrawNow
 lda ShRenderMasks,x
 ora ShDrawBits
 sta ShDrawBits
 rts
ShDrawNow:
 lda ShState+$0460,x
 and #1
 bne ShDrawDone
 ldy ShState+$0300,x
 lda ShNativePoseOrdinal,y
 cmp #$ff
 beq ShDrawDone
 tay
 lda ShNativeFrameBase,y
 clc
 adc ShState+$030b,x
 asl
 asl
 tay
 lda ShNativeFramePointers,y
 sta R0
 lda ShNativeFramePointers+1,y
 sta R1
 lda ShNativeFramePointers+2,y
 sta ShNextDescriptor
 lda ShNativeFramePointers+3,y
 sta ShNextDescriptor+1
 jsr ShDrawPacket
 lda ShNextDescriptor+1
 beq ShDrawDone
 lda ShNextDescriptor
 sta R0
 lda ShNextDescriptor+1
 sta R1
 jsr ShDrawPacket
ShDrawDone:
 ldx ShRenderSlot
 rts
ShDrawPacket:
 ldx ShRenderSlot
 lda ShState+$0363,x
 and #4
 beq ShPacketReady
 ; Original left-facing OAM is an exact priority-preserving mirror of each
 ; right-facing packet: x'=256-x-8. Normal native descriptor,<=124 bytes.
 ldy #0
 lda (R0),y
 sta ShMirrorPacket
 tay
 beq ShPacketMirrored
ShMirrorPart:
 lda (R0),y                ; descriptor dx
 eor #$ff
 clc
 adc #$f9                  ; -dx-8
 sta ShMirrorPacket,y
 dey
 lda (R0),y                ; descriptor dy
 sta ShMirrorPacket,y
 dey
 lda (R0),y                ; original attr, mirror the8px cell
 eor #$40
 sta ShMirrorPacket,y
 dey
 lda (R0),y                ; unchanged8x16 tile pair
 sta ShMirrorPacket,y
 dey
 bne ShMirrorPart
ShPacketMirrored:
 lda #<ShMirrorPacket
 sta R0
 lda #>ShMirrorPacket
 sta R1
ShPacketReady:
 ldx ShRenderSlot
 lda ShState+$0379,x
 sta R4
 lda ShState+$0384,x
 sta R5
 lda ShState+$038f,x
 sta R6
 lda ShState+$039a,x
 clc
 adc #1                     ; original viewport0 -> native generic Ypage1
 sta R7
 lda Player_SprAttrib
 and #$20
 sta R3
 sta SafecallA_SMC+1
 lda #<MetaspriteRenderLoop
 sta FarcallJmpTarget_SMC+1
 lda #>MetaspriteRenderLoop
 sta FarcallJmpTarget_SMC+2
 lda #Bank_MetaspriteRenderLoop
 jsr FarCallCommon
 ldx ShRenderSlot
 rts

; World/scene/enemy/audio leaves remain typed unresolved services. The private
; CPU oracle intercepts them explicitly; none is an admitted native no-op.
ShNativeEvent:
 sta ShEvent
 rts

.macro ShSave
 php
 pha
 txa
 pha
 tya
 pha
 .repeat 8,I
 lda R0+I
 pha
 .endrepeat
.endmacro
.macro ShRestore
 .repeat 8,I
 pla
 sta R7-I
 .endrepeat
 pla
 tay
 pla
 tax
 pla
 plp
.endmacro
.export ShHostConstruct,ShHostMovement,ShHostDraw,ShSourceFrame
; Cold authenticated loader must have copied metadata before this entry.
ShHostConstruct:
 clc                         ; rejected constructor returnsC0 via savedP
 ShSave
 lda OperMode
 cmp #1
 jne ShConstructReturn
 lda DisableScreenFlag
 jeq ShConstructReturn
 lda Mirror_PPUMASK
 and #$18
 jne ShConstructReturn
 lda NmiDisable
 jpl ShConstructReturn
 lda FamilyMainCommit
 and #1
 jeq ShConstructReturn
 lda #0
 sta ShReady               ; invalidate old actor before any construction
 sta R0
 lda #$c0
 sta R1
 ldx #8
 ldy #0
ShClearPage:
 lda #0
ShClearByte:
 sta (R0),y
 iny
 bne ShClearByte
 inc R1
 dex
 bne ShClearPage
 lda #0
 sta ShPrevious
 sta ShHaveEpoch
 sta ShDrawPhase
 sta ShDrawBits
 lda #$ff
 ldx #4
ShClearInventory:
 sta ShState+$0738,x
 dex
 bpl ShClearInventory
 lda #6                     ; actual pinned original intro539/53A
 sta ShState+$0539
 sta ShState+$053a
 lda #$90
 sta ShState+$002d
 jsr ShImportPosition
 lda PlayerFacingDir
 cmp #2
 bne ShInitFacing
 lda #4
 sta ShState+$0363
ShInitFacing:
 ldx #0
 jsr Sh_83AB
 lda #$a7
 sta ShReady                ; final context publication, not auth cookie
 tsx
 lda $010c,x                ; common public restore; sourceCtor never ownsP
 ora #1
 sta $010c,x
ShConstructReturn:
 ShRestore
 rts

ShImportPosition:
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sta ShState+$0379
 lda Player_PageLoc
 sbc ScreenLeft_PageLoc
 sta ShState+$0384
 lda ShState+$0379
 clc
 adc #8
 sta ShState+$0379
 bcc ShImportY
 inc ShState+$0384
ShImportY:
 lda Player_Y_Position
 clc
 adc #32
 sta ShState+$038f
 lda Player_Y_HighPos
 adc #0
 sec
 sbc #1
 sta ShState+$039a
 rts

ShHostMovement:
 ShSave
 lda ShReady
 cmp #$a7
 jne ShMoveDone
 lda OperMode
 cmp #1
 jne ShMoveDone
 lda GameEngineSubroutine
 cmp #8
 jne ShMoveDone
 lda GamePauseStatus
 and #1
 jne ShMoveDone
 lda ShHaveEpoch
 beq ShMoveAccepted
 lda FrameCounter
 cmp ShLastEpoch
 jeq ShMoveDone
ShMoveAccepted:
 inc ShState+$0553         ; genuine9AA0 accepted source Main phase
 lda FrameCounter
 sta ShLastEpoch
 lda #1
 sta ShHaveEpoch
 lda #0
 sta ShDrawBits
 lda Player_X_Position
 sta ShOldX
 lda Player_PageLoc
 sta ShOldX+1
 lda Player_Y_Position
 sta ShOldY
 lda Player_Y_HighPos
 sta ShOldY+1
 jsr ShImportPosition
 lda SavedJoypadBits
 and #15
 tax
 lda ShReverseNibble,x
 asl
 asl
 asl
 asl
 sta ShState+$0031
 lda SavedJoypadBits
 lsr
 lsr
 lsr
 lsr
 tax
 lda ShReverseNibble,x
 ora ShState+$0031
 sta ShState+$0031
 eor ShPrevious
 and ShState+$0031
 sta ShState+$003a
 lda ShState+$0031
 sta ShPrevious
 ldx #0
 jsr ShSourceFrame
 ldx #0
 jsr Sh_A196
 jsr Sh_C9DA                ; genuine four-slot motion; draw is deferred
 ldx #0
 jsr Sh_A154                ; genuine9B60 post-contact magic/hurt countdown
 lda ShState+$0379
 sec
 sbc #8
 sta R4
 lda ShState+$0384
 sbc #0
 sta R5
 lda R4
 clc
 adc ScreenLeft_X_Pos
 sta Player_X_Position
 lda R5
 adc ScreenLeft_PageLoc
 sta Player_PageLoc
 lda Player_X_Position
 sec
 sbc ShOldX
 sta Player_X_Scroll
 asl
 asl
 asl
 asl
 sta Player_X_Speed
 lda ShState+$038f
 sec
 sbc #32
 sta Player_Y_Position
 lda ShState+$039a
 sbc #0
 clc
 adc #1
 sta Player_Y_HighPos
 lda Player_Y_Position
 sec
 sbc ShOldY
 sta Player_Y_Speed
 lda ShState+$03fd
 and #12
 beq ShOnFloor
 lda #1
ShOnFloor:
 sta Player_State
 lda #1
 sta PlayerSize
 lda #0
 sta CrouchingFlag
 lda ShState+$0413
 cmp #5
 bne ShFacing
 lda #4
 sta CrouchingFlag
ShFacing:
 lda #1
 ldx ShState+$0363
 txa
 and #4
 beq ShFaceRight
 lda #2
 bne ShStoreFace
ShFaceRight:
 lda #1
ShStoreFace:
 sta PlayerFacingDir
ShMoveDone:
 ShRestore
 sec
 rts

ShSourceFrame:
 lda ShState+$0413
 cmp #19
 bcs ShBadState
 asl
 tay
 lda ShActorRoots,y
 sta ShState+$017b
 lda ShActorRoots+1,y
 sta ShState+$017c
 jmp (ShState+$017b)
ShBadState:
 rts

ShHostDraw:
 ShSave
 lda ShReady
 cmp #$a7
 bne ShDrawReturn
 lda #1
 sta ShDrawPhase
 ldx #0
 jsr ShNativeDrawObject
 ldx #1
ShDrawSlots:
 lda ShRenderMasks,x
 and ShDrawBits
 beq ShDrawNextSlot
 jsr ShNativeDrawObject
ShDrawNextSlot:
 inx
 cpx #5
 bne ShDrawSlots
 lda #0
 sta ShDrawPhase
ShDrawReturn:
 ShRestore
 sec
 rts
ShRenderMasks:.byte 1,2,4,8,16
ShReverseNibble:.byte 0,8,4,12,2,10,6,14,1,9,5,13,3,11,7,15
