; EXPERIMENTAL source selected31 scheduler, always authenticated through ROM.
; Native world draws FIRST in shared59B. Public6 is also injury status: only
; authenticated earlyDraw's bit7 phase token admits one late pass; otherwise
; retain the original unavailable C0 callback and all originalAXY/PexceptC.
.setcpu "6502"
.import CfState,CfCallA,CfTarget,CfTargetBank,CfNativeP1Mask
.import SprObject_SprAttrib,ObjectMetasprite,Sprite_Data,CurrentBankC
.import SmFreezePalettePacket,SmFreezePalettePending,SmFreezeLastBlue,SmFreezeTurn
.import SmFreezePaletteControl,AreaType
.export CfP1SavedAttributes,CfP1NativeC,CfP1EarlyTag,CfP1LateEntry,CfP1Heartbeat,CfP1Acquire
.export CfP1Late,CfP1Packet,CfP1PacketGate,CfP1ModuleEnd
CfP1Tag=CfState+$02df
CfP1Temp=CfState+$02f7
CfP1Visible=CfState+$02fa
CfP1Choice=CfState+$02fb
.macro P1_SAVE
 php
 pha
 txa
 pha
 tya
 pha
.endmacro
.macro P1_RESTORE
 pla
 tay
 pla
 tax
 pla
 plp
.endmacro
.segment "CF_P1_STATE"
CfP1SavedAttributes:.res 24
CfP1NativeC:.res 1

.segment "CF_P1_TAG"
CfP1EarlyTag:
 ldx #23
Actor:
 lda SprObject_SprAttrib,x
 sta CfP1SavedAttributes,x
 cpx #0
 beq NextActor
 lda ObjectMetasprite,x
 beq NextActor
 cmp #145
 bcs NextActor
 tay
 lda CfNativeP1Mask,y
 sta CfP1Temp
 lda SprObject_SprAttrib,x
 and #3
 tay
 lda Bits,y
 and CfP1Temp
 beq NextActor
 lda SprObject_SprAttrib,x
 ora #$10
 sta SprObject_SprAttrib,x
NextActor:
 dex
 bpl Actor
 lda CfP1Tag
 ora #$80                   ; phase token AFTER every authenticated snapshot
 sta CfP1Tag
 rts
Bits:.byte 1,2,4,8

.segment "CF_P1_LATE"
CfP1LateEntry:
 php
 pha
 lda CfP1Tag
 bmi Late
 pla
 plp
 clc                        ; actual injury-status6 stays original no-op
 rts
Late:
 lda #0
 sta CfP1Tag                ; consume once, before any palette producer
 pla
 plp
 P1_SAVE
 ldx #23
:lda CfP1SavedAttributes,x
 sta SprObject_SprAttrib,x
 dex
 bpl :-
 jsr CfP1Late
 P1_RESTORE
 rts

CfP1Late:
 lda #0
 sta CfP1Visible
 ldx #0
Scan:
 lda Sprite_Data,x
 cmp #240
 bcs Next
 lda Sprite_Data+2,x
 and #$18
 cmp #8
 beq Shot
 cmp #16
 bne Next
 lda #2
 bne AddVisible
Shot:lda #1
AddVisible:
 ora CfP1Visible
 sta CfP1Visible
Next:
 inx
 inx
 inx
 inx
 bne Scan
 lda #0
 sta CfP1Choice
 lda CfP1Visible
 cmp #3
 beq Both
 and #1
 beq PaintStart
 lda #1
 bne SetChoice
Both:
 lda SmFreezeTurn
 eor #1
 and #1
 sta SmFreezeTurn
SetChoice:sta CfP1Choice
PaintStart:
 ldx #0
Paint:
 lda Sprite_Data+2,x
 and #$18
 cmp #8
 beq LoanPart
 cmp #16
 bne ClearTag
 lda CfP1Choice
 bne Hide
 beq ClearTag
LoanPart:
 lda CfP1Choice
 bne ClearTag
Hide:lda #248
 sta Sprite_Data,x
ClearTag:
 lda Sprite_Data+2,x
 and #$e7
 sta Sprite_Data+2,x
 inx
 inx
 inx
 inx
 bne Paint
 jmp CfP1PacketGate

.segment "CF_P1_PACKET"
CfP1Packet:
 lda #0
 sta SmFreezePalettePending
 lda #$3f
 sta SmFreezePalettePacket
 lda #$15
 sta SmFreezePalettePacket+1
 lda #3
 sta SmFreezePalettePacket+2
 lda #0
 sta SmFreezePalettePacket+6
 lda CfP1Choice
 bne ShotColors
 ldx SmFreezePaletteControl
 cpx #1
 bcc Area
 cpx #5
 bcc NativeColors
 cpx #8
 bne Area
 ldx #2
 bne NativeColors
Area:
 ldx AreaType
 cpx #4
 bcc :+
 ldx #1
:inx
NativeColors:
 lda Color1-1,x
 sta SmFreezePalettePacket+3
 lda Color2-1,x
 sta SmFreezePalettePacket+4
 lda Color3-1,x
 sta SmFreezePalettePacket+5
 lda #$c0
 bne Commit
ShotColors:
 lda #$20
 sta SmFreezePalettePacket+3
 lda #$38
 sta SmFreezePalettePacket+4
 lda #$16
 sta SmFreezePalettePacket+5
 lda #$80
Commit:
 pha
 lda CfP1Choice
 ora #$c0
 sta SmFreezeLastBlue
 pla
 sta SmFreezePalettePending ; COMPLETE OAM/packet +owner BEFORE validity LAST
 rts
Color1:.byte $10,$1a,$1c,$1c
Color2:.byte $30,$30,$36,$36
Color3:.byte $27,$27,$17,$17

.segment "CF_P1_HEARTBEAT"
CfP1Heartbeat:
 php
 pha
 lda SmFreezeLastBlue
 cmp #$c1
 bne Done
 lda #0
 sta SmFreezePalettePending
 lda SmFreezePalettePacket
 cmp #$3f
 bne Done
 lda SmFreezePalettePacket+1
 cmp #$15
 bne Done
 lda SmFreezePalettePacket+2
 cmp #3
 bne Done
 lda SmFreezePalettePacket+3
 cmp #$20
 bne Done
 lda SmFreezePalettePacket+4
 cmp #$38
 bne Done
 lda SmFreezePalettePacket+5
 cmp #$16
 bne Done
 lda SmFreezePalettePacket+6
 bne Done
 lda #$80
 sta SmFreezePalettePending
Done:
 pla
 plp
 rts

.segment "CF_P1_ACQUIRE"
CfP1Acquire:
 lda #0
 sta SmFreezePalettePending
 sta SmFreezeLastBlue
 sta SmFreezeTurn
 sta CfP1Choice
 jmp CfP1PacketGate

.segment "CF_P1_GATE"
CfP1PacketGate:
 php
 pha
 lda #<CfP1Packet
 sta CfTarget
 lda #>CfP1Packet
 sta CfTarget+1
 lda #.lobyte(.bank(CfP1Packet))
 sta CfTargetBank
 pla
 plp
 jmp CfCallA
CfP1ModuleEnd:
