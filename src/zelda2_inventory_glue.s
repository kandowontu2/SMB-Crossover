.pushseg
.segment "Z2_LOGIC"
.proc Z2InventoryLegacyClassicGate
 pha
 jsr Z2IsActive
 bcc Original
 pla
 sec ; Makes originalLink's InventoryHasRaw/Spend reject all old items.
 rts
Original:pla
 jmp Z2OriginalInventoryLegacyClassic
.endproc
.proc Z2InventorySupportedGate
 pha
 jsr Z2IsActive
 bcc Original
 pla
 sec ; Reuse physical private pickup rise/clipped collision, not old equipment.
 rts
Original:pla
 jmp Z2OriginalInventorySupported
.endproc
.proc Z2InventoryHurtGate
 jsr Z2IsActive
 bcc Original
 lda #0
 rts
Original:jmp Z2OriginalInventoryHurt
.endproc
.proc Z2InventoryDeathGate
 jsr Z2IsActive
 bcs Native
 farcall InventoryDeath,jmp
Native:
 lda #0
 ldx #127
ClearTransient:
 sta Z2TransientBegin,x
 dex
 bpl ClearTransient
 lda NumberofLives
 beq FinalLife
 jmp Z2NewLife
FinalLife:jmp Z2GameOver
.endproc
.proc Z2ResetAreaGate
 farcall MegaManResetArea
 lda #0
 ldx #127
Clear:sta Z2TransientBegin,x
 dex
 bpl Clear
 jsr Z2AreaReset
 lda #0
 sta Z2PanelActive
 sta Z2PanelPending
 sta Z2HudCacheValid
 lda SavedJoypadBits
 sta Z2PreviousButtons
 lda SavedJoypad1Bits
 sta Z2UiPrevious
 rts
.endproc
.proc Z2RemainingWeaponsGate
 jsr Z2IsActive
 bcc Original
 rts
Original:farcall RemainingWeapons,jmp
.endproc
.popseg
