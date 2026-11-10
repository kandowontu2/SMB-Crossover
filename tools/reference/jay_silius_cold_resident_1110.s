.setcpu "6502"

.segment "COLD65"
JaySceneOrRetire:
 php
 pha
 jsr JayIdentity
 bcc LegacyRetire
 ; Descriptor bytes survive both the A65 and A123 mappings on this frame.
 txa
 pha
 ldx #6
PushDescriptor:
 lda Descriptor,x
 pha
 dex
 bpl PushDescriptor
 jsr $ae00
SceneReturn:
 pla
 pla
 pla
 pla
 pla
 pla
 pla
 bcc SceneDone
 lda $7da1
 pha
 lda #2
 jsr $80c2
 lda #0
 sta $c033
 pla
 jsr $80c2
SceneDone:
 pla
 tax
 pla
 plp
 rts
LegacyRetire:
 pla
 plp
 jmp $b026

JaySelect:
 jsr JayIdentity
 bcc LegacySelect
 ; CoCold pushes 20 bytes, then the selector's JSR pushes two more.
 ; Accept only the actual cold scene call with its staged descriptor.
 tsx
 lda $0117,x
 cmp #<(SceneReturn-1)
 bne WrongFrame
 lda $0118,x
 cmp #>(SceneReturn-1)
 bne WrongFrame
 txa
 clc
 adc #25
 sta $06
 lda #1
 sta $07
 lda #<Cookie
 sta $08
 lda #>Cookie
 sta $09
 sec
 rts
WrongFrame:
 clc
 rts
LegacySelect:
 lda $6002
 jmp $af03

JayIdentity:
 lda $6002
 cmp #16
 bne Foreign
 lda $730b
 and #$60
 cmp #$20
 beq ReturnIdentity
Foreign:
 clc
ReturnIdentity:
 rts

Descriptor:
 .byte 2,0,1,$4b,1,$4c,1
Cookie:
 .byte CookieBytes

.segment "PROTO66"
ProtoSetPose:
 lda #$de
 jsr $80c2
 lda ProtoChrLo,x
 sta $6b08
 lda $053e
 cmp #2
 beq Left
 lda ProtoRightLo,x
 sta $6b06
 lda ProtoRightHi,x
 jmp RestoreMap
Left:
 lda ProtoLeftLo,x
 sta $6b06
 lda ProtoLeftHi,x
RestoreMap:
 sta $6b07
 lda #$c1
 jsr $80c2
 lda #$e9
 sta $06e1
 rts

.segment "SUNNY94"
SunnyRightHigh:
 lda #$ce
 cpx #25
 bcc ReturnHigh
 cpx #26
 beq ReturnHigh
 lda #$cf
 rts
SunnyLeftHigh:
 lda #$cf
 cpx #11
 bcc ReturnHigh
 beq LeftD0
 cpx #15
 bcc ReturnHigh
 cpx #26
 beq ReturnHigh
 cpx #32
 bcc LeftD0
 lda #$d1
 rts
LeftD0:
 lda #$d0
ReturnHigh:
 rts
