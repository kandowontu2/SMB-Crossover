; Source-owned forced-blank loader, executing retained C70 ROM while
; RAM2 is writable through A. Existing global RAM0/protection are untouched.
.import __ARTHUR_CACHE_EXEC_LOAD__,__ARTHUR_CACHE_EXEC_SIZE__
.export ArCacheLoad,ArCacheCheckpoint,ArCacheStreamBegin,ArCacheStreamDone
.segment "ARTHUR_ART_TAIL"
.proc ArCacheLoad
 lda SelectedCharacter
 cmp #32
 jne Rejected
 lda DisableScreenFlag
 jeq Rejected
 lda Mirror_PPUMASK
 and #$18
 jne Rejected
 lda NmiDisable
 jpl Rejected
 php
 sei
 lda R0
 pha
 lda R1
 pha
 lda ArHostOldPage
 pha
 lda ArHostReady
 pha
 lda #0
 sta ArHostReady             ; NMI clock cannot consume partial source scratch
 jsr ArCachePublishCheckpoint
::ArCacheCheckpoint:
 lda Mirror_PPUCTRL
 and #$fb
 sta $2000
 lda CurrentBank
 pha
 lda #2                      ; destination selectedRAM2, genuine raw tag
 sta CurrentBank
 sta $5115
 lda #0
 sta $bfe0                   ; shared valid byte cleared BEFORE any overwrite
 lda #3
 sta $5130
 lda #113                    ; source-granted physical881
 sta $5120
 sta $5128
 lda #114
 sta $5121
 sta $5129
 lda #115
 sta $5122
 sta $512a
::ArCacheStreamBegin:
 lda #0
 sta ArHostOldPage           ; construction mode0..2, restored before ready
 sta ArDrawIndex             ; source key0..73
 sta ArLayoutPtr
 lda #$a0
 sta ArLayoutPtr+1
 lda #$bc
 sta ArDrawPtr
 lda #$a1
 sta ArDrawPtr+1
LoadKey:
 lda ArDrawIndex
 clc
 adc #172
 ldx #0
 jsr SeekInput
 lda $2007
 cmp #255
 jeq EmptyKey
 sta ArDrawRecord
 lda ArLayoutPtr
 sta R0
 lda ArLayoutPtr+1
 sta R1
 ldy #0
 lda ArDrawPtr
 sta (R0),y
 cmp (R0),y
 jne VerifyFail
 iny
 lda ArDrawPtr+1
 clc
 adc #$20                    ; stored pointers target future C2, not load A2
 sta (R0),y
 cmp (R0),y
 jne VerifyFail
 lda ArDrawRecord
 and #127
 ldx ArHostOldPage
 beq MasterReady
 clc
 adc #43
MasterReady:
 asl
 ldx #0
 jsr SeekInput
 lda $2007
 sta ArDrawHeader
 lda $2007
 tax
 lda ArDrawHeader
 jsr SeekInput
 lda ArDrawPtr
 sta R0
 lda ArDrawPtr+1
 sta R1
 ldy #0
 lda $2007
 cmp #1
 jcc VerifyFail
 cmp #12
 jcs VerifyFail
 sta ArDrawCount
 sta (R0),y
 cmp (R0),y
 jne VerifyFail
 iny
 lda $2007
 cmp #15
 beq CommonOnly
 cmp #9
 jcs VerifyFail
 clc
 adc #100
 bne StorePage
CommonOnly:lda #255
StorePage:
 sta (R0),y
 cmp (R0),y
 jne VerifyFail
 iny
CopyPart:
 lda $2007
 sta (R0),y
 cmp (R0),y
 jne VerifyFail
 iny
 lda $2007
 sta (R0),y
 cmp (R0),y
 jne VerifyFail
 iny
 lda $2007
 bit ArDrawRecord
 bpl FacingReady
 eor #64
FacingReady:
 ldx ArHostOldPage
 cpx #2
 bne PaletteReady
 sta ArDrawAttr
 and #3
 cmp #1
 bne OriginalPalette
 lda ArDrawAttr
 ora #2
 bne PaletteReady
OriginalPalette:lda ArDrawAttr
PaletteReady:
 sta (R0),y
 cmp (R0),y
 jne VerifyFail
 iny
 lda $2007
 bit ArDrawRecord
 bpl XReady
 eor #255
 sec
 sbc #7
XReady:
 sta (R0),y
 cmp (R0),y
 jne VerifyFail
 iny
 dec ArDrawCount
 jne CopyPart
 tya
 clc
 adc ArDrawPtr
 sta ArDrawPtr
 bcc AdvanceKey
 inc ArDrawPtr+1
 jmp AdvanceKey
EmptyKey:
 lda ArLayoutPtr
 sta R0
 lda ArLayoutPtr+1
 sta R1
 ldy #0
 lda #0
 sta (R0),y
 cmp (R0),y
 jne VerifyFail
 iny
 sta (R0),y
 cmp (R0),y
 jne VerifyFail
AdvanceKey:
 lda ArLayoutPtr
 clc
 adc #2
 sta ArLayoutPtr
 bcc :+
 inc ArLayoutPtr+1
:
 inc ArDrawIndex
 lda ArDrawIndex
 cmp #74
 jne LoadKey
 lda #0
 sta ArDrawIndex
 inc ArHostOldPage
 lda ArHostOldPage
 cmp #3
 jne LoadKey
 lda ArDrawPtr
 cmp #$f2
 bne VerifyFail
 lda ArDrawPtr+1
 cmp #$b7
 bne VerifyFail
 ; Exact linker-relocated executable bytes follow the canonical input.
 lda #.lobyte(__ARTHUR_CACHE_EXEC_LOAD__-$dc400)
 ldx #.hibyte(__ARTHUR_CACHE_EXEC_LOAD__-$dc400)
 jsr SeekInput
 lda #0
 sta R0
 lda #$b8
 sta R1
 lda #.lobyte(__ARTHUR_CACHE_EXEC_SIZE__)
 sta ArDrawCount
 lda #.hibyte(__ARTHUR_CACHE_EXEC_SIZE__)
 sta ArDrawPart
 ldy #0
CopyCode:
 lda $2007
 sta (R0),y
 cmp (R0),y
 bne VerifyFail
 iny
 bne :+
 inc R1
:
 lda ArDrawCount
 bne :+
 dec ArDrawPart
:
 dec ArDrawCount
 lda ArDrawCount
 ora ArDrawPart
 bne CopyCode
 ldy #15
Cookie:
 lda Signature,y
 sta $bfe0,y
 cmp $bfe0,y
 bne VerifyFail
 dey
 bne Cookie
 lda #$a7
 sta $bfe0                   ; publish validity LAST, after every readback
 cmp $bfe0
 bne VerifyFail
 lda #1
 bne Cleanup
VerifyFail:
 lda #0
 sta $bfe0
Cleanup:
 sta ArDrawHeader            ; verification result, not an admission flag
::ArCacheStreamDone:
 pla
 sta CurrentBank
 sta $5115
 jsr ArCachePublishCheckpoint
 lda Mirror_PPUCTRL
 sta $2000
 bit $2002
 lda #0
 sta $2005
 sta $2005                  ; exact native forced-blank scroll/latch contract
 pla
 sta ArTemp                 ; saved scene readiness, restored after pointers
 pla
 sta ArHostOldPage
 pla
 sta R1
 pla
 sta R0
 lda ArDrawHeader
 beq NotReady
 lda ArTemp
 sta ArHostReady
 plp
 sec
 rts
NotReady:
 lda #0
 sta ArHostReady
 plp
Rejected:clc
 rts
SeekInput:
 bit $2002
 stx $2006
 sta $2006
 lda $2007                  ; genuine buffered-read dummy
 rts
Signature:
 .repeat 16,I
 .byte .ident(.concat("AR_CACHE_SIG",.string(I)))
 .endrepeat
.endproc

.proc ArCachePublishCheckpoint
 ; Source publication defines/restores a completed native latch checkpoint.
 ; No software CHR/cache state or global WRAM protection changes.
 lda CurrentBank
 pha
 lda #$be
 sta CurrentBank
 sta $5115
 jsr X5PublishChr
 pla
 sta CurrentBank
 sta $5115
 rts
.endproc
