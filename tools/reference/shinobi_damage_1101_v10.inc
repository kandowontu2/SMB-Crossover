; Native injury ownership. Donor D6E9/D762 gates and D771 health semantics.
; Hit reaction uses the original DA1B initializer via authenticated private row36.
; Death bit is published here; native death/life handoff remains a separate service.
.export ShInjury
.segment "SHINOBI_RESIDENT"
ShInjury:
 php
 pha
 txa
 pha
 tya
 pha
 .repeat 8,I
 lda R0+I
 pha
 .endrepeat
 lda CurrentBankC
 pha
 jsr ShCheckCode
 bcc ShInjuryReject
 lda #2
 sta CurrentBankC
 sta $5116
 lda $c800
 cmp #$a7
 bne ShInjuryReject
 lda $c413
 cmp #$0a
 beq ShInjuryHandled
 cmp #$10
 beq ShInjuryHandled
 lda $c460
 and #2
 bne ShInjuryHandled
 lda $c54c
 ora $c54d
 bne ShInjuryHandled
 lda $c038
 and #2
 bne ShInjuryHandled
 ; Source counter6 means seven hits. Do not turn zero into an early death.
 dec $c539
 bpl ShInjuryAlive
 lda #0
 sta $c539
 lda $c038
 and #1
 bne ShInjuryAlive
 lda $c038
 ora #2
 sta $c038
 jmp ShInjuryHandled
ShInjuryAlive:
 ShRomFar ShInjuryVeneer,193
ShInjuryHandled:
 tsx
 lda $010d,x
 ora #1
 bne ShInjuryFlags
ShInjuryReject:
 tsx
 lda $010d,x
 and #$fe
ShInjuryFlags:
 sta $010d,x
 pla
 sta CurrentBankC
 sta $5116
 .repeat 8,I
 pla
 sta R0+7-I
 .endrepeat
 pla
 tay
 pla
 tax
 pla
 plp
 rts
ShInjuryVeneer=ShServiceVeneers+108
