; Skin-only Mario alternate. Native Mario animation, motion and power state
; remain authoritative. The existing CHR mode byte publishes the skin with
; the completed menu/OAM epoch. NMI never reads a live menu identity.
.if ::ENABLE_MMC5_EXPANDED
KM_FIRST_CHR=696
.import KmNmiSlot0
.export CurrentCHRBank
.pushseg
.segment "NEW_ROSTER_GATE"
; Preserve the planned compact-router9B and Rogue-constructor42B windows.
; Those source units must be included before this final aligned append.
.assert * <= $adce,lderror,"Kamikaze cycle overlaps earlier router owners"
.assert NrMovement = $a0e0,lderror,"Kamikaze padding requires audited router origin"
.res ($adce-$a0e0)-(*-NrMovement), $ff
KmCycleStart:
.proc KmNextVariant
 lda MarioVariant
 beq Luigi
 cmp #1
 beq Skin
 cmp #3
 beq Celeste
 lda #0
 rts
Luigi:lda #1
 rts
Skin:lda #3
 rts
Celeste:lda #4
 rts
.endproc
KmCycleEnd:
.assert * <= $ae00,lderror,"Kamikaze cycle overlaps Rogue auxiliary"
.segment "CELESTE_MARIO_HOST"
KmMenuStart:
.proc KmQueueName
 php
 pha
 lda SelectedCharacter
 bne Foreign
 lda MarioVariant
 cmp #3
 bne Foreign
 pla
 plp
 ; QueueSelection has already performed the ordinary mode clear. This tag
 ; translates native Mario pages16..19 only in sprite window0. No new RAM.
 lda #$84
 sta X5ChrMode
 lda #1
 sta X5WideChrActive
 sta ReloadCHRBank
 lda #<Name
 sta R2
 lda #>Name
 sta R3
 lda #0
 jmp NrQueueSelectName::NamePage
Foreign:
 pla
 plp
 jmp NrQueueSelectName
Name:.byte " KAMIKAZE MARIO "
.endproc
KmMenuEnd:
.assert * <= $c000,lderror,"Kamikaze menu helper exceeds actual81BF60 tail"
.popseg
.endif
