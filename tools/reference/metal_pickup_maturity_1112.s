; HuMature admits overlap only after the native actor finishes rising.
; The outer Ms12Common frame restores AXYP except this returned carry.
.setcpu "6502"
.segment "MATURE"
    jmp MsMetalMaturity
.segment "BRIDGE_TAIL"
    pla
    sta CurrentBankC
    sta $5116
    rts
MsMetalMaturity:
    lda Enemy_State,x
    asl a
    rts
