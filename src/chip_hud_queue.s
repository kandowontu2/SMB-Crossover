; Foreground-only, same existing CD_LOGIC bank. No persistent cache/RAM.
; Empty and whole-singleton queues retain fast paths. For longer queues,
; suppress only if the last possibly overlapping complete command is an
; identical current HP packet. Never mutate or remove an existing command.
; A known first HP record seeds the scan without parsing it again.
; All nametable mirrors are treated as potential aliases. Unsupported native
; repeat/vertical/zero256/high aliases or malformed data append conservatively.
.pushseg
.segment "CD_LOGIC"
.proc CdQueueHud
 cpx #0
 bne Nonempty
Append:
 lda #$20
 sta VRAM_Buffer1,x
 lda #$4b ; Keep HP and its count together in the white HUD attribute.
 sta VRAM_Buffer1+1,x
 lda #4
 sta VRAM_Buffer1+2,x
 lda #$24
 sta VRAM_Buffer1+3,x
 lda CdHudText
 sta VRAM_Buffer1+4,x
 lda CdHudText+1
 sta VRAM_Buffer1+5,x
 lda CdHealth
 sta VRAM_Buffer1+6,x
 txa
 clc
 adc #7
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 rts
Nonempty:
 cpx #7
 jcc Append
 lda VRAM_Buffer1
 cmp #$20
 bne UnknownFirst
 lda VRAM_Buffer1+1
 cmp #$4b
 bne UnknownFirst
 lda VRAM_Buffer1+2
 cmp #4
 bne UnknownFirst
 lda VRAM_Buffer1+3
 cmp #$24
 bne UnknownFirst
 lda VRAM_Buffer1+4
 cmp CdHudText
 bne UnknownFirst
 lda VRAM_Buffer1+5
 cmp CdHudText+1
 bne UnknownFirst
 lda VRAM_Buffer1+6
 cmp CdHealth
 bne UnknownFirst
 cpx #7
 bne KnownPrefix
 lda VRAM_Buffer1+7
 jne Append
 jmp Suppress
KnownPrefix:
 tya
 pha
 ldx #7
 ldy #1
 jmp Scan
UnknownFirst:
 cpx #7
 jeq Append
 tya
 pha
 ldx #0
 ldy #0
Scan:
 cpx VRAM_Buffer1_Offset
 jeq AtEnd
 jcs Fallback
 txa
 clc
 adc #3
 cmp VRAM_Buffer1_Offset
 jcs Fallback ; header and at least one data byte must fit.
 lda VRAM_Buffer1,x
 cmp #$20
 jcc Fallback
 cmp #$40
 jcs Fallback
 lda VRAM_Buffer1+2,x
 jeq Fallback ; native zero means256, never an empty command.
 and #$c0
 jne Fallback ; retain all repeat/vertical/high-flag packet semantics.
 txa
 clc
 adc VRAM_Buffer1+2,x
 adc #3
 cmp VRAM_Buffer1_Offset
 bcc Bounded
 jne Fallback
Bounded:
 pha ; next complete command index; only scratch is the real CPU stack.
 lda VRAM_Buffer1,x
 and #3
 bne Next
 lda VRAM_Buffer1+1,x
 cmp #$4f
 bcs Next
 clc
 adc VRAM_Buffer1+2,x ; exclusive end; low start<=78 and count<=63.
 cmp #$4c
 bcc Next
 ldy #0 ; any possible mirrored or partial overlap invalidates the prior match.
 lda VRAM_Buffer1,x
 cmp #$20
 bne Next
 lda VRAM_Buffer1+1,x
 cmp #$4b
 bne Next
 lda VRAM_Buffer1+2,x
 cmp #4
 bne Next
 lda VRAM_Buffer1+3,x
 cmp #$24
 bne Next
 lda VRAM_Buffer1+4,x
 cmp CdHudText
 bne Next
 lda VRAM_Buffer1+5,x
 cmp CdHudText+1
 bne Next
 lda VRAM_Buffer1+6,x
 cmp CdHealth
 bne Next
 ldy #1
Next:
 pla
 tax
 jmp Scan
AtEnd:
 lda VRAM_Buffer1,x
 bne Fallback
Finished:
 tya
 tax
 pla
 tay
 txa
 beq RestoreAppend
 jmp Suppress
Fallback:
 ldy #0
 jmp Finished
RestoreAppend:
 ldx VRAM_Buffer1_Offset
 jmp Append
Suppress:
 ldx VRAM_Buffer1_Offset
 lda #0
 clc
 clv ; original bounded offset+7 always clears V.
 rts
.endproc
.popseg

; X5InventoryInit already cleared all four profile pages. Initialize the
; selected Chip/Dale constructor before any visible entrance HUD is queued.
; The original variant-restoration loop follows and retains its caller ABI.
.pushseg
.segment "X5_PROFILES"
.proc CdNewGameProfiles
 jsr X5ProfilesNewGame
 lda SelectedCharacter
 cmp #14
 bne Done
 lda #3
 sta CdHealth
 lda #$a5
 sta CdMagic
Done:rts
.endproc
.popseg
