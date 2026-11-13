; Source factoring within the previously granted shared 77B router and its
; sole 3B entry. NativeKr still branches to BFAD with A=SelectedCharacter.
; The public phase caller has already saved Y/P; X remains untouched.
; Legal entering owners are35..43 and public rows0..35 (private36).
.setcpu "6502"
.segment "ROUTER_ENTRY"
MsHeadRouteEntry:
    cpy #32
    bne MsHeadRouteOrdinary
    pla
    tay
    plp
    jmp HuNativeWorldPalette
MsHeadRouteOrdinary:
    sty TargetLo
    ldy #2
    cmp #36
    jmp MsHeadRouteClassify
MsHeadRouteLow:
    .byte $88,$8c,$6d,$6d
MsHeadRouteHigh:
    .byte $aa,$b0,$bf,$ab
MsHeadRouteBank:
    .byte $c1,$c1,$a4,$ce
.segment "ROUTER_GATE"
MsHeadRouteClassify:
    bcc MsHeadRouteMetal
    beq MsHeadRouteLookup
    iny
    bne MsHeadRouteLookup
MsHeadRouteMetal:
    lda TargetLo
    eor #10
    cmp #1
    tya
    rol a
    tay
MsHeadRouteLookup:
    lda TargetLo
    asl a
    adc TargetLo
    adc MsHeadRouteLow-2,y
    sta TargetLo
    lda MsHeadRouteHigh-2,y
    sta TargetHi
    lda MsHeadRouteBank-2,y
    sta NextBank
    jmp HuCommonRestore
