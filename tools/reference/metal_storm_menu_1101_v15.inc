.macro MetalFar Target,Bank
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #($80|Bank)
 jsr FarCallCommon
.endmacro
.segment "RESOLVE"
.export Ms15Resolve
Ms15Resolve:
 php
 pha
 txa
 pha
 tya
 pha
 ; Authenticate both complete Metal headers before retiring either one.
 MetalFar Ms8Auth,25
 bcc Restore
 MetalFar Ms12RetireHeaders,94
Restore:
 pla
 tay
 pla
 tax
 pla
 plp
 jsr KrMenuResolve
 php
 lda CrossoverMenuIndex
 cmp #11
 bne Done
 lda FmAlts
 and #2
 beq Done
 lda #35
 sta SelectedCharacter
Done:
 plp
 lda SelectedCharacter
 rts
.assert *-Ms15Resolve<=114,error,"Bank29 pre-veneer padding capacity"

.segment "START"
.export Ms15StartFlags
Ms15StartFlags:
 jsr FmStartRetireFlags
 php
 pha
 lda SelectedCharacter
 cmp #34
 beq Karnov
 cmp #35
 bne StartDone
 lda #2
 bne Store
Karnov:
 lda #1
Store:
 ora FmAlts
 sta FmAlts
StartDone:
 pla
 plp
 rts
.assert *-Ms15StartFlags<=31,error,"Bank29 post-veneer padding capacity"
