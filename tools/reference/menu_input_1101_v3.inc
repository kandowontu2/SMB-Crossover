; Same-PC front-end input proposal. No gameplay state or new SRAM allocation.
; CrossoverContinue bit0 is a deferred Select edge ONLY while menu state1.
; Native StartSelected supplies0/80; state2 consumes bit0 before confirming.
; Include once before character_select.s, then emit the macros at the exact
; funded sites documented by the bounded component receipt.

.macro MnMenuInputHook
 php
 tya
 pha
 jmp MnMenuEdges
::MnMenuInputResume:
 pla
 tay
 plp
 ldx CrossoverMenuButtons
 lda CrossoverMenuPressed
 .res 5,$ea                     ; exact original20-byte input-edge span
.endmacro

.macro MnMenuRetainHook
 .res 6,$ea                     ; replace only STA FmAlts / STA FmGroups
.endmacro

.macro MnMenuColdHook
 farcall MnMenuColdInit         ; exact original18-byte NrGlobalInit call
.endmacro

.macro MnMenuEmitEdges
.proc MnMenuEdges
 ; PHP/TYA/PHA and restoration are at the hook. Tail jumps avoid an extra
 ; helper return address and fit107 bytes of the116-byte menu padding.
 lda SavedJoypad1Bits
 ora SavedJoypad2Bits
 tax
 stx CrossoverMenuPressed
 eor CrossoverMenuButtons
 and CrossoverMenuPressed
 sta CrossoverMenuPressed
 stx CrossoverMenuButtons
 lda CrossoverMenuState
 cmp #1
 bne Ready
 lda CrossoverMenuPressed
 and #$20
 beq Done
 lda CrossoverContinue
 ora #1
 sta CrossoverContinue
 jmp Done
Ready:
 cmp #2
 bne Done
 lda CrossoverContinue
 and #1
 beq Check
 dec CrossoverContinue          ; 01/81 ->00/80; never changes continue mode
 lda CrossoverMenuPressed
 ora #$20
 sta CrossoverMenuPressed
Check:
 lda CrossoverMenuPressed
 and #$40                      ; native B/title priority remains first
 bne Done
 lda CrossoverMenuPressed
 and #$20
 beq Done
 lda CrossoverMenuPressed
 and #$90
 beq Done
 ; Use the actual native alternate consumer, including pending/readiness
 ; gates, with direction and confirmation masked. Never invent an ID.
 lda CrossoverMenuPressed
 pha
 lda #$20
 sta CrossoverMenuPressed
 jsr CrossoverMenuInput::CheckDirection
 pla
 sta CrossoverMenuPressed
Done:
 jmp MnMenuInputResume
.endproc
.assert *-MnMenuEdges=107,lderror,"Bounded107-byte PROTO_MENU padding lease"
.endmacro

.macro MnMenuEmitColdInit
.proc MnMenuColdInit
 ; BuildScreen no longer clears these bytes. Preserve the original cold
 ; default explicitly at the actual CrossoverInit consumer instead.
 lda #0
 sta FmAlts
 sta FmGroups
 farcall NrGlobalInit,jmp
.endproc
.assert *-MnMenuColdInit=26,lderror,"Exact26-byte cold reset wrapper"
.endmacro
