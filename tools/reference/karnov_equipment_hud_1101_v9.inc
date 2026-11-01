; Foreground-only Karnov equipment HUD proposal. Authenticated C2 required.
; No new ROM/CHR/cache lease is granted by this include. Import KrHudCache6B,
; KrHudPhysicalLow/High and native HUD globals at the owning link.
; Consumes A/X/Y/P; returns A0,C1 for an owned gameplay UI call, C0 otherwise.
; No borrowed ZP, R0..R7, map writes, SMC, OAM or direct PPU writes.
.export KrHudTick,KrHudCancel,KrHudEnd
.export KrHudDataStart,KrHudDataEnd
KrHudOwner=$e9
KrHudTick:
 lda SelectedCharacter
 cmp #34
 jne KrHudDecline
 lda OperMode
 cmp #1
 jne KrHudHide
 lda OperMode_Task
 cmp #3
 jne KrHudHide
 lda GameEngineSubroutine
 cmp #8
 jne KrHudHide
 lda DisableScreenFlag
 jne KrHudDecline
 lda NmiDisable
 jpl KrHudDecline              ; never publish a partial foreground packet
 ldx #0
 lda KrState+$8e
 beq KrHudCheckOwned
 inx
 cmp #3
 beq KrHudCheckOwned
 inx
 cmp #7
 bne KrHudNormal
KrHudCheckOwned:
 lda KrState+$8f
 and KrHudMasks,x
 bne KrHudHaveIndex
KrHudNormal:ldx #3
KrHudHaveIndex:
 ldy KrHudStocks,x
 lda KrState,y
 cpx #3
 bne :+
 lda #0
:cpx KrHudCache
 bne KrHudDirty
 cmp KrHudCache+1
 bne KrHudDirty
 lda KrState+$e8
 and #$80
 cmp KrHudCache+2
 bne KrHudDirty
 lda InvHudActive
 cmp #KrHudOwner
 jeq KrHudHandled
KrHudDirty:
 lda VRAM_Buffer1_Offset
 jne KrHudHandled
 lda VRAM_Buffer1
 jne KrHudHandled
 lda VRAM_Buffer_AddrCtrl
 jne KrHudHandled              ; defer without losing source/cached changes
 stx KrHudCache+3
 ldy KrHudStocks,x
 lda KrState,y
 cpx #3
 bne :+
 lda #0
:sta KrHudCache+4
 lda KrState+$e8
 and #$80
 sta KrHudCache+5
 ldx #35
KrHudCopy:
 lda KrHudPacket,x
 sta VRAM_Buffer1,x
 dex
 bpl KrHudCopy
 ldx KrHudCache+3
 lda KrHudNameOffsets,x
 tay
 ldx #0
KrHudName:
 lda KrHudNames,y
 sta VRAM_Buffer1+3,x
 iny
 inx
 cpx #9
 bne KrHudName
 lda KrHudCache+4
 beq KrHudIcon
 lsr
 lsr
 lsr
 lsr
 sta VRAM_Buffer1+13
 lda KrHudCache+4
 and #15
 sta VRAM_Buffer1+14
KrHudIcon:
 ldx KrHudCache+3
 cpx #3
 beq KrHudLease
 lda KrHudTiles,x
 sta VRAM_Buffer1+28
 clc
 adc #1
 sta VRAM_Buffer1+29
 adc #1
 sta VRAM_Buffer1+33
 adc #1
 sta VRAM_Buffer1+34
 lda KrHudCache+5
 beq KrHudLease
 ldy #6
KrHudHint:
 lda KrHudDownB,y
 sta VRAM_Buffer1+18,y
 dey
 bpl KrHudHint
KrHudLease:
 lda InvHudActive
 cmp #KrHudOwner
 beq KrHudCacheCommit
 lda #KrHudPhysicalLow
 sta InvHudPhysical
 lda #KrHudPhysicalHigh
 sta X5HudChrUpper
 lda #1
 sta X5WideChrActive
 sta ReloadCHRBank
 lda #KrHudOwner
 sta InvHudActive
KrHudCacheCommit:
 ldx #2
KrHudSave:
 lda KrHudCache+3,x
 sta KrHudCache,x
 dex
 bpl KrHudSave
 lda #35
 sta VRAM_Buffer1_Offset
KrHudHandled:
 lda #0
 sec
 rts
KrHudHide:
 jsr KrHudCancel
KrHudDecline:
 lda #0
 clc
 rts
; Also callable from the existing ROM-owned retirement/scene path. No C2
; opcode may be called after retirement; place an equivalent ROM leaf if needed.
KrHudCancel:
 lda InvHudActive
 cmp #KrHudOwner
 bne KrHudCancelDone
 lda #0
 sta InvHudActive
 lda #1
 sta ReloadCHRBank
KrHudCancelDone:rts
KrHudMasks:.byte 1,8,$80
KrHudStocks:.byte $bd,$be,$bf,0
KrHudTiles:.byte $30,$34,$38
KrHudNameOffsets:.byte 0,9,18,27
KrHudDataStart:
KrHudNames:.byte "BOOTS    BOOMERANGWINGS    FIRE     "
KrHudDownB:.byte "DOWN",$3c,"B "
; Same four native literal commands as existing inventory HUD, with only
; one additional name cell: full BOOMERANG +space+two source BCD digits.
KrHudPacket:
 .byte $20,$23,12,"            "
 .byte $20,$4a,7,"SELECT "
 .byte $20,$37,2,$24,$24
 .byte $20,$57,2,$24,$24
 .byte 0
KrHudDataEnd:
KrHudEnd:
