.setcpu "6502"

SelectedCharacter = $6002
SafecallA = $016a
NativeReload = $a7f2
DkDescriptorData = $a7dc

.segment "EMPTY"
.export GfEmptyService
GfEmptyService:
    lda SelectedCharacter
    eor #42                     ; Preserve incoming C, I, V and D.
    .byte $d0, <(NativeReload-(*+1))
    lda SafecallA               ; The original RAM farcall loads A/N/Z here.
    clc
    rts
    .assert *-GfEmptyService=12,error,"Exactly the relocated descriptor-copy span"

.segment "COLD_COPY"
.export DkCopyDescriptor
DkCopyDescriptor:
    ldy #7
:
    lda DkDescriptorData,y
    sta $dfe0,y
    dey
    bpl :-
    rts
