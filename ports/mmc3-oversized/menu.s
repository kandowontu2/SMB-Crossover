; Selection uses a resident 66-page portrait atlas, loaded once while the menu
; is being built. No family upload, forced blank, or live CHR write occurs when
; moving the cursor or cycling alternates. Full gameplay art loads on confirm.
; Audio scratch belongs to Contra/Link when those portraits are highlighted.
; Use an invalid gameplay profile value ($80+portrait) instead of that scratch.
M3MenuPortrait=M3CacheProfile
.export M3MenuPortrait,M3MenuSelect,M3MenuDrawPreview,M3MenuLoad
.pushseg
.segment "M3_MENU"
.proc M3MenuLoad
 lda CurrentBankC
 pha
 BankPRGC #.bank(M3MenuLoadCore)
 jsr M3MenuLoadCore
 pla
 BankPRGC a
 rts
.endproc
.proc M3MenuSelect
 ldx CrossoverMenuIndex
 lda BaseIdentity,x
 cpx #0
 bne NotMario
 clc
 adc MarioVariant
 jmp Chosen
NotMario:cpx #1
 bne NotMega
 clc
 adc ProtoVariant
 jmp Chosen
NotMega:cpx #3
 bne NotBill
 clc
 adc BillVariant
 jmp Chosen
NotBill:cpx #4
 bne NotLink
 clc
 adc Z2Variant
 jmp Chosen
NotLink:cpx #5
 bne NotSimon
 clc
 adc Cv3Variant
 jmp Chosen
NotSimon:cpx #8
 bne NotScrooge
 clc
 adc DarkwingVariant
 jmp Chosen
NotScrooge:cpx #12
 bne NotKirby
 ldx KbVariant
 beq Chosen
 lda #32
 bne Chosen
NotKirby:cpx #13
 bne NotChip
 clc
 adc CdVariant
 jmp Chosen
NotChip:cpx #16
 bne NotM3
 clc
 adc M3Variant
 jmp Chosen
NotM3:cpx #18
 bne Chosen
 clc
 adc TnVariant
Chosen:
 ldx PlayerOutlinesOff
 bne Off
 clc
 adc #33
Off:
 tay
 ora #$80
 sta M3MenuPortrait
 tya
 clc
 adc #52
 sta PlayerChrBank
 lda #$80
 sta X5ChrMode
 lda #1
 sta X5WideChrActive
 sta ReloadCHRBank
 lda #0
 sta SsChrActive
 sta InvHudActive
 ; The palette follows the exact captured source pose. Four separate packets
 ; skip $3F10/$14/$18/$1C, which alias universal background color entries.
 lda M3MenuPortrait
 and #$7f
 tay
 lda M3MenuRecordLo,y
 sta R0
 lda M3MenuRecordHi,y
 sta R1
 ldy #0
 lda (R0),y
 asl
 asl
 clc
 adc #1
 tay
 ldx VRAM_Buffer1_Offset
 lda #$11
 sta R2
Palette:
 iny
 lda #$3f
 sta VRAM_Buffer1,x
 lda R2
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 lda (R0),y
 sta VRAM_Buffer1+3,x
 iny
 lda (R0),y
 sta VRAM_Buffer1+4,x
 iny
 lda (R0),y
 sta VRAM_Buffer1+5,x
 iny
 txa
 clc
 adc #6
 tax
 lda R2
 clc
 adc #4
 sta R2
 cmp #$21
 bcc Palette
 lda #0
 sta VRAM_Buffer1,x
 stx VRAM_Buffer1_Offset
 rts
BaseIdentity:.byte 0,2,4,5,7,9,13,14,15,17,18,19,20,21,23,24,25,27,28
.endproc
.proc M3MenuDrawPreview
 ; Complete a private OAM image before NMI publishes the matching CHR page.
 ldx #0
 lda #$f8
Hide:sta Sprite_Y_Position,x
 inx
 inx
 inx
 inx
 bne Hide
 lda M3MenuPortrait
 and #$7f
 tay
 lda M3MenuRecordLo,y
 sta R0
 lda M3MenuRecordHi,y
 sta R1
 ldy #0
 lda (R0),y
 sta R2
 ldx #0
Copy:
 iny
 lda (R0),y
 sta Sprite_Y_Position,x
 inx
 iny
 lda (R0),y
 sta Sprite_Y_Position,x
 inx
 iny
 lda (R0),y
 sta Sprite_Y_Position,x
 inx
 iny
 lda (R0),y
 sta Sprite_Y_Position,x
 inx
 dec R2
 bne Copy
 txa
 ora #$80                    ; Queue the hint on the next idle menu frame.
 sta CurrentOAMOffset
 lda #120
 sta Player_X_Position
 lda #152
 sta Player_Y_Position
 rts
.endproc
.popseg
.include "mmc3_menu_art.inc"

.pushseg
.segment "M3_CACHE"
.proc M3MenuLoadCore
 jsr M3Blank
 lda #0
 sta M3Pending
 lda #$ff                    ; Force complete family restore on confirmation.
 sta M3CacheProfile
 lda #<756
 sta $0200
 lda #>756
 sta $0201
 lda #52
 sta $0202
 lda #66
 sta $0203
Loop:
 jsr M3UploadPage
 inc $0200
 bne :+
 inc $0201
:inc $0202
 dec $0203
 bne Loop
 jmp M3Unblank
.endproc
.popseg
