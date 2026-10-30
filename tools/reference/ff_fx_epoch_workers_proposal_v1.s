; UNLINKED sizing proposal. Existing mailbox/cursor aliases await explicit review.
; All scratch is borrowed native R0..R7, saved/restored on the CPU stack.
; Never mutates original FF targets/rect/bodybuffer, original source code/art.
.setcpu "6502"
.import DrawAllMetasprites,FarCallCommon,SafecallA_SMC,FarcallJmpTarget_SMC
.import SmFreezePalettePacket,SmFreezePalettePending,SmFreezeTurn,SmFreezeLastBlue
.import SmFreezePaletteControl,AreaType,RgOamPlayerStart,RgOamRotation,RgOamUsed
.import FfProjectile,Sprite_Y_Position,Sprite_Tilenumber,Sprite_Attributes
.importzp R0,R1,R2,R3,R4,R5,R6,R7,SmPosePtr
.export FfMuxNativeLate,FfMuxHeartbeat,FfMuxClassify,FfMuxPacket,FfMuxColors
.export FfMuxNativeLateEnd,FfMuxHeartbeatEnd,FfMuxClassifyEnd,FfMuxPacketEnd

.macro MP_SAVE
 php
 pha
 txa
 pha
 tya
 pha
 ldx #7
:lda R0,x
 pha
 dex
 bpl :-
.endmacro
.macro MP_RESTORE
 ldx #0
:pla
 sta R0,x
 inx
 cpx #8
 bne :-
 pla
 tay
 pla
 tax
 pla
 plp
.endmacro

.segment "FF_EPOCH_MAIN"
FfMuxNativeLate:
 ; This is the genuine original native DrawAll target, exactly once.
 sta SafecallA_SMC+1
 lda #<DrawAllMetasprites
 sta FarcallJmpTarget_SMC+1
 lda #>DrawAllMetasprites
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(DrawAllMetasprites)|$80)
 jsr FarCallCommon
 MP_SAVE
 ldy #0
 lda (SmPosePtr),y
 clc
 adc RgOamPlayerStart
 sta R2                       ; complete FF extra/body0 logical end.
 lda #0
 sta R0                       ; logical OAM byte offset.
 sta R3                       ; actual admitted visible family bitset.
 ldx RgOamRotation             ; physical OAM byte offset.
Scan:
 lda R0
 cmp RgOamUsed
 bcs Choose
 lda Sprite_Y_Position,x
 cmp #240
 bcs ScanNext
 jsr FfMuxClassify
 cmp #6
 bcs ScanNext
 tay
 lda FfMuxBits,y
 ora R3
 sta R3
ScanNext:
 inx
 inx
 inx
 inx
 lda R0
 clc
 adc #4
 sta R0
 bne Scan
Choose:
 ldx SmFreezeTurn
 cpx #6
 bcc Cursor
 ldx #0
Cursor:
 lda R3
 beq Native
Search:
 lda FfMuxBits,x
 and R3
 bne Found
 inx
 cpx #6
 bcc Search
 ldx #0
 beq Search
Native:
 ldx #0
Found:
 stx R4                       ; selected complete color family.
 inx
 cpx #6
 bcc NextCursor
 ldx #0
NextCursor:
 stx SmFreezeTurn             ; advance ONLY on completed DrawAll.
 lda #0
 sta R0
 ldx RgOamRotation
Paint:
 jsr FfMuxClassify
 cmp #6
 bcs ClearTag
 cmp R4
 bne Hide
 cmp #0
 beq ClearTag                 ; whole native mixed object keeps every palette.
 lda Sprite_Attributes,x
 and #$fc
 ora #1                       ; exact source colors in borrowed P1.
 sta Sprite_Attributes,x
 bne ClearTag
Hide:
 lda #$f8
 sta Sprite_Y_Position,x
ClearTag:
 lda Sprite_Attributes,x
 and #$ef
 sta Sprite_Attributes,x
 inx
 inx
 inx
 inx
 lda R0
 clc
 adc #4
 sta R0
 bne Paint                    ; all64 parts clear metadata before DMA.
 jsr FfMuxPacket
 MP_RESTORE
 rts
FfMuxNativeLateEnd:
.assert FfMuxNativeLateEnd-FfMuxNativeLate<=273,error,"Largest granted hole273B"

.segment "FF_EPOCH_CLASSIFY"
FfMuxClassify:
 lda R0
 cmp RgOamUsed
 bcs None
 cmp R2
 bcs World
 lda Sprite_Tilenumber,x
 and #1
 beq Body
 lda Sprite_Tilenumber,x
 lsr
 lsr
 lsr
 lsr
 lsr
 lsr
 tay
 beq None                     ; final hardware window4 is never sourceFF.
 lda FfMuxSlots,y              ; windows5/6/7 -> true slots0/12/24.
 tay
 lda FfProjectile,y
 cmp #5
 bcs None
 tay
 lda FfMuxKinds,y
 rts
Body:
 lda Sprite_Attributes,x
 and #3
 beq None                     ; body0 always retained.
 cmp #2
 bcc None                     ; no invented role1 body.
 clc
 adc #2                       ; native source sword2 ->4; ink3 ->5.
 rts
World:
 lda Sprite_Attributes,x
 and #$10
 beq None
 lda #0                       ; actual marker covers complete mixed object.
 rts
None:
 lda #$ff
 rts
FfMuxClassifyEnd:
.assert FfMuxClassifyEnd-FfMuxClassify<=119,error,"Granted119B hole"

.segment "FF_EPOCH_PACKET"
FfMuxPacket:
 lda #0
 sta SmFreezePalettePending   ; clear validity FIRST.
 lda #$3f
 sta SmFreezePalettePacket
 lda #$15
 sta SmFreezePalettePacket+1
 lda #3
 sta SmFreezePalettePacket+2
 lda #0
 sta SmFreezePalettePacket+6
 lda R4
 beq NativeColor
 sec
 sbc #1
 sta R5
 asl
 clc
 adc R5
 tay                          ; chosenFX family1..5 -> triplets0..14.
 bcc Copy                     ; bounded0..12.
NativeColor:
 ldy SmFreezePaletteControl
 cpy #1
 bcc Area
 cpy #5
 bcc HaveArea
 cpy #8
 bne Area
 ldy #2
 bne HaveArea
Area:
 ldy AreaType
 cpy #4
 bcc :+
 ldy #1
:iny
HaveArea:
 tya
 sta R5
 asl
 clc
 adc R5
 adc #12                      ; native1..4 -> triplets15..26.
 tay
Copy:
 ldx #0
:lda FfMuxColors,y
 sta SmFreezePalettePacket+3,x
 iny
 inx
 cpx #3
 bcc :-
 lda R4
 ora #$80
 sta SmFreezeLastBlue         ; complete OAM+packet, ownerfamily LAST.
 lda #$80
 sta SmFreezePalettePending   ; normal native postflush validity LAST.
 rts
FfMuxPacketEnd:
.assert FfMuxPacketEnd-FfMuxPacket<=117,error,"Granted117B hole"

.segment "FF_EPOCH_HEARTBEAT"
FfMuxHeartbeat:
 MP_SAVE
 lda SmFreezeLastBlue
 cmp #$80
 bcc Done
 cmp #$86
 bcs Done
 and #7
 sta R4
 jsr FfMuxPacket              ; reissue current epoch; NEVER advancecursor.
Done:
 MP_RESTORE
 rts
FfMuxHeartbeatEnd:

.segment "FF_EPOCH_COLORS"
FfMuxColors:
 .byte $16,$26,$30,$12,$21,$30,$18,$28,$30,$0c,$1c,$2c,$0f,$0f,$0f
 .byte $10,$30,$27,$1a,$30,$27,$1c,$36,$17,$1c,$36,$17
.segment "FF_EPOCH_TABLES"
FfMuxBits: .byte 1,2,4,8,16,32
FfMuxSlots: .byte 0,0,12,24
FfMuxKinds: .byte $ff,1,3,2,2
