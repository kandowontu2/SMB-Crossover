; Combined owner-limited authorization helper. Public row zero always takes
; the complete checker in bank65. The private bank85 row-zero mirror is no
; longer an entry: UTIL borrows its first three bytes; rows1..37 stay exact.
.setcpu "6502"
CurrentBankC=$7da1
SelectedCharacter=$6002
FrameCounter=$0e
SharedEpoch=$c3f0
DkEpoch=$c8ff
MapC=$80c2                    ; Existing fixed native shadow/port/RTS helper.

.segment "GATE"
CheckEpoch:
 lda CurrentBankC
 pha
 lda #2
 jsr MapC
 ldx SelectedCharacter
 jsr LiveHeader
 bcc Miss
 jsr ReadEpoch
 beq Miss
 bcc MiniGood
 jmp ReadSonicEpoch
MiniGood:
 jmp CheckCodeHeader
Miss:
 clc
 jmp RestoreC

.segment "UTIL"
ReadEpoch:
 cpx #41
 lda DkEpoch
 bcc EpochLoaded              ; Only admitted raw40 reads C8FF.
 lda SharedEpoch              ; Mini41/Sonic43 retain their existing epoch.
EpochLoaded:
 beq BadEpoch
 cmp FrameCounter
 bne BadEpoch
 cpx #43
 txa                          ; Success is nonzero; C still identifies Sonic.
 rts
BadEpoch:
 lda #0
 rts
CheckCodeHeader:
 lda #3
 jsr MapC
 jsr LiveHeader
RestoreC:
 pla
 jmp MapC

.segment "HEADER"
LiveHeader:
 lda $dfe0
 cmp #$a7
 bne Invalid
 cpx $dfe1
 beq HeaderReturn
Invalid:
 clc
HeaderReturn:
 rts
