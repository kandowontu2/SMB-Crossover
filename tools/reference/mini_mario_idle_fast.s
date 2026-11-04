.setcpu "6502"
.export MiniTry, MiniChecked
.import MiniFullCheck, MiniAuthorized

.segment "TRY"
MiniTry:
 ; Keep the existing B08C..B0FD target. The new ROM bank has a copy of
 ; those veneer entry addresses, with each entry leading to the same test.
 lda #$d5
 jsr $015a
 jmp MiniChecked

.segment "CHECKED"
MiniChecked:
 .byte $90, <($a75e-($a7d5+2))
 .byte $b0, <($a763-($a7d5+4))
 .assert MiniFullCheck=$a75e, lderror, "Mini full check moved"
 .assert MiniAuthorized=$a763, lderror, "Mini authenticated path moved"

CurrentBankC = $7da1
MiniValidatedEpoch = $c3f0
FrameCounter = $0e

.segment "BANK_ENTRY"
 .repeat 38
  jmp CheckMini
 .endrepeat

.segment "BANK_GATE"
CheckMini:
 lda CurrentBankC
 pha
 lda #2
 jsr MapC
 lda FrameCounter
 beq Miss
 cmp MiniValidatedEpoch
 bne Miss
 jsr LiveHeader
 bcc Miss
 jmp CheckCodeHeader
Miss:
 clc
 jmp RestoreC

.segment "BANK_CODE_HEADER"
CheckCodeHeader:
 lda #3
 jsr MapC
 jsr LiveHeader
 jmp RestoreC

.segment "BANK_UTIL"
LiveHeader:
 lda $dfe0
 cmp #$a7
 bne Invalid
 lda $dfe1
 cmp #41
 beq HeaderResult
Invalid:
 clc
HeaderResult:
 rts
RestoreC:
 pla
MapC:
 sta CurrentBankC
 sta $5116
 rts

; Native new-roster side ingress, before the shared family router.
; All foreign callers resume after the displaced STA with original A/P.
.segment "SIDE_GATE"
.export MiniSideGate
MiniSideGate:
 sta $016a
 php
 lda $6002
 cmp #41
 beq MiniSide
 jmp SideForeign
MiniSide:
 plp
 jsr $958b
 php
 ldx $0f
 cpx #8
 bne KeepTile
 and #$fe
 cmp #$c2
 beq KeepTile
 ldx $06
 lda $ef36,x
 and #3
 cmp #1
 bne KeepTile
 lda #0
 beq RestoreResult
KeepTile:
 lda $06
RestoreResult:
 jmp SideReturn

.segment "SIDE_RETURN"
SideReturn:
 ldx #0
 plp
 ora #0
 rts
SideForeign:
 lda $016a
 plp
 jmp $aadc

; GmNrRare has already matched its linked caller and retained the
; original X in Y. Three Mini services are immutable ABI constants.
.segment "RARE_GUARD"
MiniRareGuard:
 lda $6002
 cmp #41
 beq IsMiniRare
 jmp RareForeign
IsMiniRare:
 jmp ClassifyRare

.segment "RARE_FOREIGN"
RareForeign:
 txa
 asl a
 asl a
 jmp $a509

.segment "RARE_CLASS"
ClassifyRare:
 lda RareResultY,x
 beq NotConstant
 jmp RareConstant
NotConstant:
 jmp RareForeign

.segment "RARE_TABLE"
RareResultY:
 ; Visible (index 9) preserves Y. Adder and box type return 2 and 1.
 .byte 0,0,0,0,0,0,0,0,0,$ff,0,0,2,1,0

.segment "RARE_CONSTANT"
RareConstant:
 tax
 pla
 pla
 cpx #$ff
 bne OverrideY
 jmp PreserveY
OverrideY:
 pla
 txa
 jmp RareFinish

.segment "RARE_FINISH"
PreserveY:
 pla
RareFinish:
 pha
 tya
 tax
 pla
 tay
 plp
 lda $016a
 sec
 rts
