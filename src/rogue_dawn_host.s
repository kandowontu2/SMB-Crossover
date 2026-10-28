; Independent host helpers only; shared routing/complete services remain pending.
; ROOT approved A95 A600..BFFF, but this is not a playable integration.
; SelectedCharacter=rawSamus2 AND RdVariant=1, with no temporary ID changes.
.include "rogue_dawn_state.inc"
.pushseg
.segment "ROGUE_DAWN_HOST"
.export RdHostEnabled,RdHostInput,RdHostTickBefore,RdHostTickAfter
.export RdHostContextB
.proc RdHostEnabled
 lda SelectedCharacter
 cmp #2
 bne No
 lda RdVariant
 cmp #1
 bne No
 sec
 rts
No:clc
 rts
.endproc

; One call per admitted ACTIVE Main, not per endFrame/poll/render. Gameplay
; source3/5/7/9/11:B028..B03C sets16=12 (its old repeat store is NOPed).
.proc RdHostInput
 jsr RdHostEnabled
 bcc Done
 lda SavedJoypadBits
 eor RdHeld
 and SavedJoypadBits
 sta RdFresh
 sta RdRepeat
 lda SavedJoypadBits
 sta RdHeld
 sec
Done:rts
.endproc
.proc RdHostTickBefore
 jsr RdHostEnabled
 bcc Done
 lda RdMorphCooldown
 beq Done
 dec RdMorphCooldown            ; genuine sourceC266 owns2A before the update
Done:rts
.endproc
.proc RdHostTickAfter
 jsr RdHostEnabled
 bcc Done
 inc RdClock                    ; genuine sourceC0C5 follows completed update
Done:rts
.endproc

; ROOT-approved SMB adaptation B: virtual ORIGINAL8x8 pre-draw cursor0.
; Table bytes are authenticated original decoder returnX per REAL pose.
; Not host OAM, not constant36, not full original enemy/projectile ordering.
; Output X; Cset admitted/Cclear unsupported. A/P scratch, Y preserved.
; Call AFTER authentic current pose/radius selection. Does not render or tick.
.proc RdHostContextB
 jsr RdHostEnabled
 bcc Fail
 lda RdSourceAltPalette
 bne Fail
 lda RdFacing
 cmp #2
 bcs Fail
 lda RdAnimFrame
 cmp #$f7
 beq Empty
 cmp #106
 bcs Fail
 tax
 lda RdHostBodyOnlyReturnX,x
 cmp #$ff
 beq Fail
 tax
 sec
 rts
Empty:ldx #0                    ; actual source F7 return; no emitted parts
 sec
 rts
Fail:ldx #0
 clc
 rts
.endproc
.include "rogue_dawn_host_context.inc"
.popseg
