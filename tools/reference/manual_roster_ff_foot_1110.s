; Explicit retirement of unused FwSide26B ROM62 gate. Live FF side service14
; targets FwSvcSide/FwHostSide. FOOT_ORIGINAL reassembles the exact old gate.
.setcpu "6502"
.export FfManualFootQuery,FfManualFootQueryEnd
FootBBoxBottom=$065b
FootNativeLargePlatform=$b453
FootTarget=$016c
FootFarCall=$015a

.segment "FF_ROSTER_FOOT"
FfManualFootQuery:
.ifdef FOOT_ORIGINAL
    php
    jsr $aa2d                 ; original FwCheck
    .byte $b0,3               ; genuine long BCC to FwGateUnavailable
    jmp $ac0a
    plp
    sta $016a
    lda #<$ae90               ; original FfSide in authenticated RAM3
    sta FootTarget
    lda #>$ae90
    sta FootTarget+1
    jmp $ac0d                 ; original FwCallEnter
.else
    ; Only the native manual-H selected22 gate calls here, after rejecting
    ; bottom255. Inclusive stock platform tests need the half-open32px foot.
    inc FootBBoxBottom
    lda #<FootNativeLargePlatform
    sta FootTarget
    lda #>FootNativeLargePlatform
    sta FootTarget+1
    lda #$80
    jsr FootFarCall
    dec FootBBoxBottom        ; ordinary FF collision rectangle byte-exact.
    rts
.endif
FfManualFootQueryEnd:
