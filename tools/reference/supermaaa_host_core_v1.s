; Private host translation of jroweboy neckyboi 47273511. No new physics.
.macpack longbranch
.feature force_range
.include "inc/common.inc"
.include "inc/charmap.inc"
MaaaLength=$5c7f
.export MaaaLength,MaaTimer,MaaStomp,MaaReservation,MaaFresh,MaaLifePrefix
.export MaaBox,MaaHead,MaaAfterBG,MaaFireInit,MaaQueueName,MaaBodyDraw,MaaDrawNeck
__IMPORTS__
.macro MaaCall Target,Bank,Tail
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #Bank|$80
 .if Tail
 jmp FarCallCommon
 .else
 jsr FarCallCommon
 .endif
.endmacro
.segment "MAAA_CORE"
MaaCoreStart:
.proc MaaFresh
 MaaCall NrFreshGameInit,124,0
 php
 pha
 jsr MaaOwner
 bne Done
 lda #0
 sta MaaaLength
Done:pla
 plp
 rts
.endproc
.proc MaaLifePrefix
 inc DisableScreenFlag
 lda #0
 sta Sprite0HitDetectFlag
 lda #$80
 sta EventMusicQueue
 dec NumberofLives
 php
 pha
 jsr MaaOwner
 bne Done
 lda #0
 sta MaaaLength
Done:pla
 plp
 ; The immediate BPL consumes DEC's N. Both following paths overwrite A.
 lda NumberofLives
 rts
.endproc
.proc MaaBox
 MaaCall LmBoundingBoxGate,93,0
 php
 pha
 jsr MaaOwner
 bne Done
 lda BoundingBox_UL_YPos
 cmp #$f0
 bcs Done
 sec
 sbc MaaaLength
 bcs Store
 lda #1
Store:sta BoundingBox_UL_YPos
Done:pla
 plp
 rts
.endproc
.proc MaaHead
 php
 pha
 jsr MaaOwner
 bne Legacy
 pla
 plp
 lda Player_Y_Position
 pha
 clc
 adc BlockBuffer_Y_Adder,y
 sec
 sbc MaaaLength
 bcc Empty
 cmp #$20
 bcc Empty
 lda Player_Y_Position
 sec
 sbc MaaaLength
 sta Player_Y_Position
 jsr BlockBufferColli_Head
 ; Preserve the actual query's A/P; X is the genuine player offset0.
 php
 ldy Local_eb
 pla
 sta R5
 pla
 sta Player_Y_Position
 lda R5
 pha
 lda R3
 plp
 rts
Empty:pla
 lda #0
 rts
Legacy:pla
 plp
 ; Exact original BillBGHeadConsumer dispatcher, including its flags.
 php
 pha
 lda SelectedCharacter
 cmp #3
 beq Bill
 pla
 plp
 jmp BillHeadConsumer
Bill:pla
 plp
 jmp BillBGEmptyEnvelope
.endproc
.proc MaaAfterBG
 jsr PlayerBGCollision
 php
 pha
 phx
 phy
 jsr MaaOwner
 bne Done
 jsr MaaCoins
Done:ply
 plx
 pla
 plp
 rts
.endproc
.proc MaaCoins
 lda DisableCollisionDet
 bne Done
 lda GameEngineSubroutine
 cmp #4
 bcc Done
 cmp #11
 beq Done
 lda Player_Y_HighPos
 cmp #1
 bne Done
 lda MaaaLength
 clc
 adc #8
 lsr
 lsr
 lsr
 lsr
 beq Done
 sta R0
 lda MaaaLength
 and #15
 sta R1
 eor #$ff
 clc
 adc Player_Y_Position
 cmp #$20
 bcc Done
 lda #0                    ; Original first left query uses cleared temp.
Pair:ldx #6
 jsr Query
 jsr Credit
 lda R1
 ldx #9
 jsr Query
 jsr Credit
 lda R1
 clc
 adc #16
 sta R1
 dec R0
 beq Done
 lda Player_Y_Position
 sec
 sbc R1
 sec
 sbc #1
 cmp #$20
 bcc Done
 lda R1
 jmp Pair
Done:rts
Credit:
 cmp #$c2
 beq Coin
 cmp #$c3
 bne Done
Coin:
 ; Keep a physical coin when the optional extra producer cannot fit.
 ; Each real native erase/credit is executed once, never a remote grant.
 ldx VRAM_Buffer1_Offset
 cpx #17
 bcs Done
 lda VRAM_Buffer_AddrCtrl
 bne Done
 lda VRAM_Buffer2_Offset
 bne Done
 lda VRAM_Buffer2
 bne Done
 lda #Sfx_CoinGrab
 sta Square2SoundQueue
 lda R0
 pha
 lda R1
 pha
 jsr HandleCoinMetatile
 pla
 sta R1
 pla
 sta R0
 rts
Query:
 ; Original narrow neck X6/9 and exact native block-buffer addressing.
 pha
 txa
 clc
 adc Player_X_Position
 sta R5
 lda Player_PageLoc
 adc #0
 and #1
 lsr
 ora R5
 ror
 lsr
 lsr
 lsr
 jsr GetBlockBufferAddr
 pla
 sta R4
 lda Player_Y_Position
 sec
 sbc R4
 bcc Blank
 cmp #$20
 bcc Blank
 and #$f0
 sec
 sbc #$20
 sta R2
 tay
 lda (R6),y
 rts
Blank:lda #0
 rts
.endproc
.proc MaaFireInit
 ; Caller enters with the genuine ASL-derived carry from Fireball_State.
 lda Player_X_Position
 adc #4
 sta Fireball_X_Position,x
 lda Player_PageLoc
 adc #0
 sta Fireball_PageLoc,x
 lda Player_Y_Position
 sta Fireball_Y_Position,x
 php
 pha
 jsr MaaOwner
 bne Foreign
 pla
 plp
 sec
 sbc MaaaLength
 bcc Rejected
 sta Fireball_Y_Position,x
 jmp High
Foreign:pla
 plp
 lda SelectedCharacter
 cmp #1
 bne High
 lda Fireball_Y_Position,x
 clc
 adc #16
 sta Fireball_Y_Position,x
High:lda #1
 sta Fireball_Y_HighPos,x
 sec
 rts
Rejected:clc
 rts
.endproc
.proc MaaQueueName
 jsr GbPitQueueName
 php
 pha
 phx
 phy
 jsr MaaOwner
 bne Done
 ldx VRAM_Buffer1_Offset
 ldy #15
Copy:dex
 lda Name,y
 sta VRAM_Buffer1,x
 dey
 bpl Copy
Done:ply
 plx
 pla
 plp
 rts
Name:.byte " SUPERMAAA MARIO"
.endproc
__TIMER__
__STOMP__
__RESERVATION__
MaaCoreEnd:
.assert *<=$b9a8,lderror,"Approved Maaa CORE cap808B"
.segment "MAAA_ART"
MaaArtStart:
.proc MaaBodyDraw
 lda CurrentOAMOffset
 cmp #232
 jcs Rejected
 lda ObjectMetasprite
 tay
 lda MaaFrameMap,y
 sta M0
 tay
 lda MaaPages,y
 sta CurrentCHRBank
 sta SmChrBank
 lda #$83
 sta X5ChrMode
 lda #1
 sta X5WideChrActive
 sta ReloadCHRBank
 lda MaaHeads,y
 sta R2
 tya
 asl
 sta R0
 asl
 clc
 adc R0
 ldx #>MaaTiles
 bcc :+
 inx
:
 clc
 adc #<MaaTiles
 bcc :+
 inx
:
 sta R0
 stx R1
 lda PlayerFacingDir
 cmp #1
 beq AttrReady
 lda R3
 ora #$40
 sta R3
AttrReady:
 lda #0
 sta M1
 ldx CurrentOAMOffset
Part:
 ldy #0
 lda (R0),y
 inc R0
 bne :+
 inc R1
:
 cmp #$ff
 beq Hide
 pha
 and #$3f
 sta Sprite_Tilenumber,x
 pla
 and #$40
 eor R3
 and #$f3
 sta Sprite_Attributes,x
 lda M1
 and #1
 ldy PlayerFacingDir
 cpy #1
 beq Col
 eor #1
Col:asl
 asl
 asl
 clc
 adc R4
 sta Sprite_X_Position,x
 lda R5
 adc #0
 bne Hide
 lda R7
 cmp #1
 bne Hide
 lda M1
 cmp #2
 bcs Torso
 lda R2
 clc
 adc R6
 bcs Hide
 ldy CrossoverMenuState
 bne VisibleY
 ldy OperMode_Task
 cpy #3
 bne VisibleY
 sec
 sbc MaaaLength
 bcc Hide
 jmp VisibleY
Torso:cmp #4
 bcs Bottom
 lda R2
 clc
 adc #8
 bcc AddBase
Bottom:lda #24
AddBase:clc
 adc R6
 bcs Hide
VisibleY:cmp #$f8
 bcc StoreY
Hide:lda #$f8
StoreY:sta Sprite_Y_Position,x
 inx
 inx
 inx
 inx
 inc M1
 lda M1
 cmp #6
 jcc Part
 stx CurrentOAMOffset
Rejected:clc
 rts
.endproc
.proc MaaDrawNeck
 php
 pha
 phx
 phy
 lda CrossoverMenuState
 jne Done
 lda OperMode_Task
 cmp #3
 jne Done
 lda MaaaLength
 jeq Done
 lsr
 lsr
 lsr
 clc
 adc #1
 sta R2
 lda ObjectMetasprite
 tay
 lda MaaFrameMap,y
 tay
 sty M0
 lda Player_Y_HighPos
 cmp #1
 jne Done
 lda MaaHeads,y
 clc
 adc Player_Y_Position
 jcs Done
 cmp #$f0
 jcs Done
 clc
 adc #1
 sta R0
 lda #4
 cpy #4
 bcs NeckX
 lda PlayerFacingDir
 lsr
 asl
 asl
 sta R1
 tya
 adc R1
 tay
 lda MaaXOffsets,y
NeckX:clc
 adc Player_Rel_XPos
 bcs Done
 sta R1
 lda Player_SprAttrib
 ldy PlayerFacingDir
 cpy #1
 beq Attr
 ora #$40
Attr:sta R3
 ldx #24
Next:lda Sprite_Y_Position,x
 cmp #$f8
 bcc Skip
 ldy M0
 lda MaaPages,y
 sec
 sbc #<813
 tay
 lda R2
 cmp #2
 bcc Single
 lda R0
 cmp #8
 bcc Single
 sec
 sbc #8
 sta Sprite_Y_Position,x
 lda MaaNeckRepeat,y
 sta Sprite_Tilenumber,x
 lda #2
 bne Used
Single:lda R0
 sta Sprite_Y_Position,x
 lda MaaNeckOdd,y
 sta Sprite_Tilenumber,x
 lda #1
Used:sta R4
 lda R1
 sta Sprite_X_Position,x
 lda R3
 and #$f3
 sta Sprite_Attributes,x
 lda R2
 sec
 sbc R4
 sta R2
 beq Done
 lda R4
 asl
 asl
 asl
 sta R4
 lda R0
 sec
 sbc R4
 bcc Done
 sta R0
Skip:inx
 inx
 inx
 inx
 bne Next
Done:ply
 plx
 pla
 plp
 rts
.endproc
MaaXOffsets:.byte 3,4,3,6,5,4,5,2
__ART_DATA__
MaaArtEnd:
.assert *<=$df20,lderror,"Approved Maaa ART cap1024B"
.segment "MAAA_CHR"
.incbin "__CHR__"
