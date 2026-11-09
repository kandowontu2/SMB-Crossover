; Skip Tank admission for other owners and preserve the mapper call ABI.
.setcpu "6502"

SelectedCharacter = $6002
SafecallA = $016a
FarTarget = $016c
SafereturnA = $0179
FarCall = $015a

.macro Dispatch target, bank, opcode
    lda #<target
    sta FarTarget
    lda #>target
    sta FarTarget+1
    lda #bank
    opcode FarCall
.endmacro

.segment "CONTACT"
Contact:
    php
    pha
    lda SelectedCharacter
    bne Native
    ; FarCall already loaded SafecallA. The Tank predicate is a leaf.
    Dispatch $bfb0, $9c, jsr
    bcc Native
    pla
    plp
    sta SafecallA
    Dispatch $b60b, $02, jmp
Native:
    ; The bypass must publish the same rejected A as the real predicate.
    ; Lag audio can copy this operand to its private save area.
    sta SafereturnA
    pla
    plp
    Dispatch $ad52, $bf, jmp
.assert * = $afd6, lderror, "Tank Fresh begins at its original AFD6 entry"
