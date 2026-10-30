; Genuine native queue composition for FF body colors. No new state.
; Existing FfPaletteAck is touched only after the full RAM3 owner cookie passes.
.setcpu "6502"
.macpack longbranch
.import SelectedCharacter,CurrentBankC,FarCallCommon,SafecallA_SMC,FarcallJmpTarget_SMC
.import FwCheck,QueueMegaManFacePalette,QueueGuestWeaponPalette
.import FfPaletteAck,FfVariant,StarInvincibleTimer,GuestPowerupActive,GuestLegacyHurt,GuestPowerupAge
.import BackgroundColorCtrl,AreaType,VRAM_Buffer1_Offset,VRAM_Buffer1
.importzp FrameCounter,R0
.export FwForceColors,FwPaletteTick,FwSvcWorldPalette,FfHostPaletteC,FfPalettePhaseC,FfQueueBodyC
.export FfHostPaletteAStart,FfHostPaletteAEnd,FfHostPaletteCStart,FfHostPaletteCEnd
.export FwSvcWorldPaletteEnd

.macro FP_FAR target
 sta SafecallA_SMC+1
 lda #<target
 sta FarcallJmpTarget_SMC+1
 lda #>target
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(target)|$80)
 jsr FarCallCommon
.endmacro

.segment "FF_PALETTE_BRIDGE"
FfHostPaletteAStart:
.proc FwForceColors
 php
 pha
 txa
 pha
 tya
 pha
 lda #1
 bne FwPaletteCommon
.endproc
.proc FwPaletteTick
 php
 pha
 txa
 pha
 tya
 pha
 lda #0
 ; fall through, with the same saved caller stack.
.endproc
FwPaletteCommon:
 pha
 lda SelectedCharacter
 cmp #22
 bne FwPaletteForeign
 pla
 jsr FwCheck
 bcc FwPaletteCold
 cmp #1
 beq FwPaletteInvalidate
 lda FfPaletteAck
 cmp #$ff
 beq FwPaletteForcePending
 lda #0
 beq FwPaletteHaveMode
FwPaletteInvalidate:
 lda #$ff
 sta FfPaletteAck
FwPaletteForcePending:
 lda #1
 bne FwPaletteHaveMode
FwPaletteCold:
 asl                          ; authenticated mode0/1 becomes cold0/2.
 beq FwPaletteRestore
FwPaletteHaveMode:
 pha
 cmp #0
 beq FwPaletteMapC
 ldx VRAM_Buffer1_Offset
 cpx #65                      ;6B face+6B weapon+7B body+terminator <=84B.
 bcs FwPaletteForeign
 ; Genuine area palette3 and native powerup palette2 stay authoritative.
 FP_FAR QueueMegaManFacePalette
 FP_FAR QueueGuestWeaponPalette
FwPaletteMapC:
 pla
 tay
 lda CurrentBankC
 pha
 lda #.lobyte(.bank(FfHostPaletteC)|$80)
 sta CurrentBankC
 sta $5116
 tya
 jsr FfHostPaletteC
 pla
 sta CurrentBankC
 sta $5116
 jmp FwPaletteRestore
FwPaletteForeign:
 pla
FwPaletteRestore:
 pla
 tay
 pla
 tax
 pla
 plp
 rts
FfHostPaletteAEnd:

; Identical compiled14B native area donor body, in the existing18B own tail.
; The actual FF row32 previously supplied no donor Y to the face helper.
.segment "FF_WORLD_PALETTE_BRIDGE"
.proc FwSvcWorldPalette
 lda AreaType
 asl
 sta R0
 asl
 clc
 adc R0
 adc #6
 tay
 rts
.endproc
FwSvcWorldPaletteEnd:

.segment "FF_HOST_PALETTE_C"
FfHostPaletteCStart:
; A0=ready cached tick, A1=ready force, A2=cold force without ACK access.
.proc FfHostPaletteC
 pha
 jsr FfPalettePhaseC
 bcc Bad
 tax
 pla
 cmp #2
 beq Cold
 cmp #1
 beq Queue
 txa
 cmp FfPaletteAck
 beq No
Queue:
 txa
 pha
 jsr FfQueueBodyC
 pla
 bcc Done
 sta FfPaletteAck             ; only a successfully queued complete packet.
Done:rts
Cold:txa
 jmp FfQueueBodyC
Bad:pla
No:clc
 rts
.endproc

; Two authenticated class rows plus the existing guest star/upgrade colors.
; Source tier changes do not change class colors. Injury has no rainbow.
.proc FfPalettePhaseC
 lda FfVariant
 cmp #4
 bcs No
 lda GuestPowerupActive
 beq Star
 lda GuestLegacyHurt
 cmp #1
 beq Base
 lda GuestPowerupAge
 ldx #0
Divide:
 cmp #6
 bcc Phase
 sbc #6
 inx
 bne Divide
Phase:txa
ColorPhase:
 and #3
 beq Base
 clc
 adc #1
 sec
 rts
Star:
 lda StarInvincibleTimer
 beq Base
 lda FrameCounter
 lsr
 lsr
 jmp ColorPhase
Base:
 lda FfVariant
 lsr
 sec
 rts
No:clc
 rts
.endproc

; One7B packet plus terminator, bounded by the actual84B native queue.
; Writing3F10 also restores the area's universal backdrop on lives cards.
.proc FfQueueBodyC
 cmp #5
 bcs No
 asl
 asl
 tay
 ldx VRAM_Buffer1_Offset
 cpx #77
 bcs No
 tya
 pha
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$10
 sta VRAM_Buffer1+1,x
 lda #4
 sta VRAM_Buffer1+2,x
 lda BackgroundColorCtrl
 bne Background
 lda AreaType
Background:
 cmp #8
 bcc ValidBackground
 lda #2
ValidBackground:
 tay
 lda Backgrounds,y
 sta VRAM_Buffer1+3,x
 pla
 tay
 lda Colors+1,y
 sta VRAM_Buffer1+4,x
 lda Colors+2,y
 sta VRAM_Buffer1+5,x
 lda Colors+3,y
 sta VRAM_Buffer1+6,x
 txa
 clc
 adc #7
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 sec
 rts
No:clc
 rts
Backgrounds:.byte $22,$22,$0f,$0f,$0f,$22,$0f,$0f
; Class rows match original FfPaletteRed/Blue. Rows2..4 match the existing
; guest star palette. Phase0 returns to the authenticated body class.
Colors:
 .byte $0f,$16,$30,$36
 .byte $0f,$28,$18,$21
 .byte $0f,$1a,$27,$30
 .byte $0f,$16,$27,$30
 .byte $0f,$0f,$24,$30
.endproc
FfHostPaletteCEnd:

; Existing native DrawAll behavior relocated into the remaining owned A62
; palette alignment. Do not latch freeze state after DrawAll: preserve its
; genuine entry decision and genuine final returned AXY/P on both paths.
.import DrawAllMetasprites,SmFreezeRenderState,SamusFreezeRenderFinish
.export FwNativeDrawAll,FwNativeDrawAllEnd
.segment "FF_NATIVE_DRAW_BRIDGE"
.proc FwNativeDrawAll
 lda SmFreezeRenderState
 beq Native
 FP_FAR DrawAllMetasprites
 sta SafecallA_SMC+1
 lda #<SamusFreezeRenderFinish
 sta FarcallJmpTarget_SMC+1
 lda #>SamusFreezeRenderFinish
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(SamusFreezeRenderFinish)|$80)
 jmp FarCallCommon
Native:
 sta SafecallA_SMC+1
 lda #<DrawAllMetasprites
 sta FarcallJmpTarget_SMC+1
 lda #>DrawAllMetasprites
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(DrawAllMetasprites)|$80)
 jmp FarCallCommon
.endproc
FwNativeDrawAllEnd:
