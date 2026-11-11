.setcpu "6502"

.segment "HOT94"
JayHot:
 php
 pha
 txa
 pha
 tya
 pha
 lda $6002
 cmp #16
 bne Legacy
 lda $730b
 and #$60
 cmp #$20
 bne Legacy
 lda $7da1
 pha
 ldx #3
HeaderBank:
 txa
 jsr $80c2
 ldy #15
HeaderByte:
 lda $dfe0,y
 cmp Cookie,y
 bne RejectMapped
 dey
 bpl HeaderByte
 dex
 cpx #1
 bne HeaderBank
 ; FarCallCommon saves caller A-bank above its JSR return address.
 ; Five local pushes make that saved byte the eighth stack byte here.
 tsx
 ldy $0108,x
 ldx #>PrivateMux
 stx $016d
 lda #3
 sta $016c
 jsr $015a
RestoreMap:
 pla
 jsr $80c2
 bcc Legacy
RestoreRegisters:
 pla
 tay
 pla
 tax
 pla
 plp
 rts
RejectMapped:
 clc
 bcc RestoreMap
Legacy:
 ; The draw callback returns to the original JnDraw HUD tail. Failed
 ; movement still calls the original movement leaf. None of the paths
 ; to this label have changed the incoming SafecallA immediate.
 tsx
 lda $0107,x
 cmp #$e2
 beq RestoreRegisters
 pla
 tay
 pla
 tax
 pla
 plp
 lda #$cb
 sta $016c
 lda #$a2
 sta $016d
 lda #$e0
 jmp $015a
Cookie:
 .byte CookieBytes

.segment "DRAW_CALL"
DrawCall:
 php
 pha
 lda $730b
 and #$60
 cmp #$20
 bne DrawCallReturn
 ; Reserve exactly the same body bytes that the native roster OAM
 ; path will allocate after this worker returns. C97 is still mapped.
 lda $6b06
 sta $03
 lda $6b07
 sta $04
 beq BodyLengthReady
 ldy #0
 lda ($03),y
BodyLengthReady:
 sta $016a
 lda #<JayHot
 sta $016c
 lda #>JayHot
 sta $016d
 lda #$de
 jsr $015a
DrawCallReturn:
 pla
 plp

.segment "SCOPE"
DrawPrivate:
 pha
 lda $c033
 beq RejectDraw
 lda FrameCounter
 cmp $c034
 bne RejectDraw
 lda OperMode
 cmp #1
 bne RejectDraw
 lda OperModeTask
 cmp #3
 bne RejectDraw
 lda GamePauseStatus
 lsr a
 bcs RejectDraw
 lda FamilyMainCommit
 lsr a
 bcc RejectDraw
 lda SwimmingFlag
 ora WorldNumber
 ora LevelNumber
 ora ScreenLeft_PageLoc
 ora ScreenLeft_X_Pos
 ora Player_PageLoc
 bne RejectDraw
 pla
 jmp InitBudget
RejectDraw:
 pla
 sec
 rts

.segment "MUX"
PrivateMux:
 cpy #$e2
 beq DrawPrivate
 ; Preserve the existing movement ingress after using Y for the route.
 ldx #1
 ldy #$ff
 sec
 ora #0
 jmp PrivateUpdate

InitBudget:
 sta BodyBytes
 lda NmiDisable
 bpl DrawReturn
 lda BodyBytes
 and #3
 bne DrawReturn
 lda OamOffset
 and #3
 bne DrawReturn
 lda #252
 sec
 sbc BodyBytes
 bcc DrawReturn
 sta DrawLimit
 jsr DrawStock
DrawReturn:
 sec
 rts
