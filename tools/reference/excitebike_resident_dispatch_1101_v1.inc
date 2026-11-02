; ROM transport for raw37. The kernel vector is deliberately all-reject until
; native host services are implemented. No pending menu admission is changed.
; Existing loader owns the complete-cookie check and the five SMC offsets.
.export ExServiceVeneers,ExDispatch,ExDispatchEnd
.segment "EX_VENEERS"
ExServiceVeneers:
.repeat 37
 jmp ExDispatch
.endrepeat

.segment "EX_DISPATCH"
ExDispatch:
 php
 pha
 txa
 pha
 tya
 pha
 lda CurrentBankC
 pha
 ldx #0
ExDispatchSaveSmc:
 ldy ExSavedSmcOffsets,x
 lda $0100,y
 pha
 inx
 cpx #5
 bne ExDispatchSaveSmc
 lda SelectedCharacter
 cmp #37
 beq ExDispatchOwn
 lda FarcallJmpTarget_SMC+1
 jmp ExForeignUi
ExDispatchOwn:
 jsr ExCheckCode
 bcc ExDispatchNo
 lda FarcallJmpTarget_SMC+2
 cmp #>ExServiceVeneers
 bne ExDispatchNo
 lda FarcallJmpTarget_SMC+1
 sec
 sbc #<ExServiceVeneers
 bcc ExDispatchNo
 cmp #111
 bcs ExDispatchNo
 ; Both tables are contained within their respective pages.
 clc
 adc #<ExCacheServices
 sta FarcallJmpTarget_SMC+1
 lda #>ExCacheServices
 sta FarcallJmpTarget_SMC+2
 lda #2
 sta CurrentBankC
 sta $5116
ExDispatchInputs:
 tsx
 lda $010a,x
 pha
 lda $0109,x
 sta SafecallA_SMC+1
 lda $0108,x
 pha
 lda $0107,x
 tay
 pla
 tax
 plp
 lda #3
 jsr FarCallCommon
 php
 pha
 txa
 pha
 tya
 pha
 tsx
 ldy #4
ExDispatchCopyResult:
 lda $0101,x
 sta $010b,x
 inx
 dey
 bne ExDispatchCopyResult
 txs
 jmp ExDispatchRestore
ExDispatchNo:
 tsx
 lda $010a,x
 and #$fe
 sta $010a,x
ExDispatchRestore:
 ldx #4
ExDispatchRestoreSmc:
 ldy ExSavedSmcOffsets,x
 pla
 sta $0100,y
 dex
 bpl ExDispatchRestoreSmc
 pla
 sta CurrentBankC
 sta $5116
 pla
 tay
 pla
 tax
 pla
 plp
 rts
; X=5 at the foreign branch, the exact terminator of SaveSmc above. Only
; actual native colors/status ingress may forward to the original ROM leaf.
ExForeignLo:.byte <ExOriginalStatus,<ExOriginalColors
ExDispatchEnd:
.assert >ExServiceVeneers=>(ExServiceVeneers+110),error,"Excitebike veneer page"
.assert >ExCacheServices=>(ExCacheServices+110),error,"Excitebike cache vector page"

.segment "EX_FOREIGN_UI"
ExForeignUi:
 cmp #<(ExServiceVeneers+78)
 beq ExForeignPick
 cmp #<(ExServiceVeneers+90)
 bne ExForeignReject
 dex
ExForeignPick:
 lda ExForeignLo-4,x
 sta FarcallJmpTarget_SMC+1
 lda ExForeignHi-4,x
 sta FarcallJmpTarget_SMC+2
 lda ExForeignBank-4,x
 sta NextBank_SMC+1
 .repeat 6                  ; Discard savedSMC5 and unchanged caller C-bank.
 pla
 .endrepeat
 pla
 tay
 pla
 tax
 pla
 plp
 pla                         ; Replace the existing FarCallCommon JSR return,
 pla                         ; as the native callback tail already does.
 jmp NextBank_SMC            ; Native tail, preserving original leafSMC outputs.
ExForeignReject:
 jmp ExDispatchNo
ExForeignHi:.byte >ExOriginalStatus,>ExOriginalColors
.segment "EX_FOREIGN_BANK"
ExForeignBank:.byte ExOriginalStatusBank,ExOriginalColorsBank
