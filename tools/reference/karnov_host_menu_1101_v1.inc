; Immutable ROM29 UI callbacks. No RAM opcode is executed before a cold load.
.import HuNativeWorldPalette
.export KrMenuResolve,KrStartFlags,KrColdResolve,KrColdPrepare,KrColdDraw
.export KrColdColors,KrStatusName,KrColdPose,KrColdNoop
KrMenuResolve:
 jsr KrRetire
 farcall HuResolve
 php
 jsr KrSelected
 bcc KrMenuResolved
 lda #34
 sta SelectedCharacter
KrMenuResolved:
 plp
 lda SelectedCharacter
 rts
KrStartFlags:
 jsr FmStartRetireFlags
 php
 pha
 lda SelectedCharacter
 cmp #34
 bne KrStartDone
 lda FmAlts
 ora #1
 sta FmAlts
KrStartDone:
 pla
 plp
 rts

; Incoming real veneer offset remains in the saved SMC low operand. Returned
; C/A selects a genuine ROM callback bank; caller AXYP stays in KrDispatch's
; existing saved frame. All other services still require both full signatures.
KrColdResolve:
 jsr KrSelected
 bcc KrNotCold
 lda FarcallJmpTarget_SMC+1
 cmp #78
 bne KrFindCold
 jsr KrCheckCode            ; initialized colors use the real blue/hurt state
 bcs KrNotCold
KrFindCold:
 ldx #6
KrFindColdLoop:
 cmp KrColdOffsets,x
 beq KrFoundCold
 dex
 bpl KrFindColdLoop
KrNotCold:clc
 rts
KrFoundCold:
 lda KrColdLo,x
 sta FarcallJmpTarget_SMC+1
 lda KrColdHi,x
 sta FarcallJmpTarget_SMC+2
 lda KrColdBank,x
 sec
 rts
KrColdOffsets:.byte 9,51,54,57,78,90,96
KrColdLo:.byte <KrColdPrepare,<KrColdDraw,<FmQueueName,<KrColdNoop,<KrColdColors,<KrStatusName,<HuNativeWorldPalette
KrColdHi:.byte >KrColdPrepare,>KrColdDraw,>FmQueueName,>KrColdNoop,>KrColdColors,>KrStatusName,>HuNativeWorldPalette
KrColdBank:.byte .lobyte(.bank(KrColdPrepare)|$80),.lobyte(.bank(KrColdDraw)|$80),.lobyte(.bank(FmQueueName)|$80),.lobyte(.bank(KrColdNoop)|$80),.lobyte(.bank(KrColdColors)|$80),.lobyte(.bank(KrStatusName)|$80),.lobyte(.bank(HuNativeWorldPalette)|$80)

KrColdPrepare:
 lda #<408
 ldx #>408
 ldy #0
 farcall X5SetPhysicalChr
 lda #<408
 sta SmChrBank
 lda #<(KrColdPose+$2000)
 sta SmPosePtr
 lda #>(KrColdPose+$2000)
 sta SmPosePtr+1
 lda #157
 sta CurrentBankC
 sta $5116
 lda #$e9
 sta ObjectMetasprite
 rts
KrColdDraw:
 php
 pha
 lda #157
 sta CurrentBankC
 sta $5116
 pla
 plp
 farcall DrawMetasprite,jmp
KrColdNoop:
 clc
 rts
KrColdColors:
 php
 pha
 txa
 pha
 tya
 pha
 ldx VRAM_Buffer1_Offset
 cpx #72
 bcs KrColdColorsDone
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$10
 sta VRAM_Buffer1+1,x
 lda #4
 sta VRAM_Buffer1+2,x
 lda OperMode
 cmp #1
 bne KrColdMenuBackground
 ldy BackgroundColorCtrl
 bne KrColdBackgroundIndex
 ldy AreaType
KrColdBackgroundIndex:
 lda KrColdBackgroundColors,y
 jmp KrColdBackgroundReady
KrColdMenuBackground:
 lda #$0f
KrColdBackgroundReady:
 sta VRAM_Buffer1+3,x
 lda #$28
 sta VRAM_Buffer1+4,x
 lda #$16
 sta VRAM_Buffer1+5,x
 lda #$0f
 sta VRAM_Buffer1+6,x
 lda #0
 sta VRAM_Buffer1+7,x
 txa
 clc
 adc #7
 sta VRAM_Buffer1_Offset
KrColdColorsDone:
 pla
 tay
 pla
 tax
 pla
 plp
 sec
 rts
KrStatusName:
 cmp #0
 bne KrStatusDone
 tya
 pha
 ldy #6
KrStatusCopy:
 lda KrStatusText,y
 sta VRAM_Buffer1+11,y
 dey
 bpl KrStatusCopy
 pla
 tay
 lda #0
KrStatusDone:rts
KrStatusText:.byte "KARNOV "
KrColdBackgroundColors:.incbin "kr-native-bg.bin"
; GENERATED_IDLE_PACKET
