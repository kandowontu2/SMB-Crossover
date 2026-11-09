; Preserve the original Tank body-contact lease and native fallback.
.setcpu "6502"

SelectedCharacter = $6002
SafecallA = $016a
FarTarget = $016c
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
    ; The actual FarCall entry has already loaded A from SafecallA.
    Dispatch $bfb0, $9c, jsr
    bcc Native
    pla
    plp
    sta SafecallA
    Dispatch $b60b, $02, jmp
Native:
    pla
    plp
    sta SafecallA
    Dispatch $ad52, $bf, jmp
.assert * = $afd6, lderror, "Tank Fresh begins at its original AFD6 entry"
