; MEASUREMENT ONLY, no physical interval granted/adopted by this proposal.
; Actual selected31 shared late SFC target may be rebound to this pure ROM
; worker. It restores a complete native P1 prequeue packet before the real
; B020/service6 ROM guard, and NEVER reads/executes a guest bank itself.
; Keep Turn: clearing it every frame would permanently starve native P1.
.setcpu "6502"
.import SmFreezeLastBlue,SmFreezePalettePending,FarCallCommon
.import SafecallA_SMC,FarcallJmpTarget_SMC,BtServiceVeneers,FwMuxNativeSelect
.export CfP1NativeRestore,CfP1NativeRestoreEnd
.segment "CF_P1_ROM_RESTORE_PROPOSAL"
.macro CF_FAR target,tail
 sta SafecallA_SMC+1
 lda #<target
 sta FarcallJmpTarget_SMC+1
 lda #>target
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(target)|$80)
 .if .xmatch({tail},{jmp})
 jmp FarCallCommon
 .else
 jsr FarCallCommon
 .endif
.endmacro
CfP1NativeRestore:
 php
 pha
 txa
 pha
 tya
 pha
 lda SmFreezeLastBlue
 and #$fe
 cmp #$c0
 bne Restore
 lda #0
 sta SmFreezePalettePending     ; invalidate before any packet/owner overwrite
 lda #$c0
 sta SmFreezeLastBlue           ; native owner, completed packet publishes LAST
 .ifdef SAME_PHYSICAL_93
 jsr FwMuxNativeSelect          ; genuine pure native packet path, no State/OAM
 .else
 CF_FAR FwMuxNativeSelect,jsr
 .endif
Restore:
 pla
 tay
 pla
 tax
 pla
 plp
 ; Preserve original callback input. The actual 36-row service6 ROM guard
 ; authenticates the complete CF cookie/class BEFORE every first A2 opcode.
 CF_FAR BtServiceVeneers+18,jmp
CfP1NativeRestoreEnd:
