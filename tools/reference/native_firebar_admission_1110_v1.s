.setcpu "6502"
.export NoSpecialWorldDraw, LegacyWorldDraw, ClearFirebarSlot

EnemyID=$17
FirebarSlot=$7eb4
SafeA=$016a
FarTarget=$016c
FarCall=$015a
NativeWorldDraw=$ad01

.segment "ADMIT"
.proc NoSpecialWorldDraw
    ldx #6
Scan:
    lda EnemyID-1,x
    ; Preserve the original return carry from the last ID comparison.
    cmp #$1b
    ; The only accepted IDs are $04..$07 and $24..$27. No firebar or
    ; small lift can be in either range, regardless of its flag/state.
    and #$dc
    eor #$04
    bne Legacy
    dex
    bne Scan
    jmp ClearFirebarSlot
Legacy:
    jmp LegacyWorldDraw
.endproc

.segment "FINISH"
.proc ClearFirebarSlot
    dex
    stx FirebarSlot
    lda EnemyID                  ; FarCall's original return updates N/Z from A.
    rts
.endproc

.segment "LEGACY"
.proc LegacyWorldDraw
    ; All four shuffled slot-zero callers enter the old wrapper with A=0.
    lda #0
    sta SafeA
    lda #<NativeWorldDraw
    sta FarTarget
    lda #>NativeWorldDraw
    sta FarTarget+1
    lda #$c7
    jmp FarCall
.endproc
