; Source gap between SunnyArtEnd and RdArtStart, physical94 B25F..B300.
; Called through the newly factored Mike pose tail with real FarCallCommon.
.setcpu "6502"
.segment "HOT94"
JayHot94:
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
 stx $7da1
 stx $5116
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
 lda #<PrivateUpdate
 sta $016c
 lda #>PrivateUpdate
 sta $016d
 lda #3
 jsr $015a
 pla
 jsr $80c2
 bcc Legacy
 pla
 tay
 pla
 tax
 pla
 plp
 rts
RejectMapped:
 pla
 jsr $80c2
Legacy:
 pla
 tay
 pla
 tax
 pla
 plp
 sta $016a
 lda #$cb
 sta $016c
 lda #$a2
 sta $016d
 lda #$e0
 jmp $015a
Cookie:
 .byte CookieBytes
