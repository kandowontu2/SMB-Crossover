; ROM-owned CHR publication request. Both full cache headers must authenticate.
; Odd tile IDs select PPU $1000: windows4..7. Window7 shares metadata page517;
; only pairs117..127 reference its art tail. Native NMI publishes the request.
.export ShChr
.segment "SHINOBI_RESIDENT"
ShChr:
 php
 pha
 txa
 pha
 tya
 pha
 jsr ShCheckCode
 bcc ShChrNo
 ldx #3
ShChrLoop:
 lda ShChrLow,x
 sta CurrentCHRBank+4,x
 lda ShChrUpper,x
 sta X5ChrMode+4,x
 dex
 bpl ShChrLoop
 lda #0
 sta SsChrActive
 lda #1
 sta X5WideChrActive
 sta ReloadCHRBank
 tsx
 lda $0104,x
 ora #1
 bne ShChrFlags
ShChrNo:
 tsx
 lda $0104,x
 and #$fe
ShChrFlags:
 sta $0104,x
 pla
 tay
 pla
 tax
 pla
 plp
 rts
ShChrLow: .byte <503,<504,<505,<517
ShChrUpper: .byte $80|>503,$80|>504,$80|>505,$80|>517
