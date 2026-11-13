; Original BA86 waits for the donor PPU queue consumer at D872. SMB owns
; the PPU and native terrain stream. FF18 remains the typed source boundary.
; Supply the already-complete acknowledgment value at this single wait.
.setcpu "6502"
.segment "ACKNOWLEDGED"
    lda #1
    nop
    nop
    nop
