; PRIVATE live cue / source06C4 successor. No scheduler hooks.
; Private original Rogue Dawn audio source unit. No scheduling/mixer hooks.
; All public APIs are consumer-exclusive and preserve AXYP. They are not an
; atomic foreground/NMI publication protocol. Init is required on identity entry.
.include "live-driver-imports.inc"
.macpack longbranch
RdaState=RgAudioRam
RdaZpState=RgAudioRam+$100
RdaSavedC=RgAudioRam+$113
RdaReadValue=RgAudioRam+$114
RdaFrameControl=RgAudioRam+$115
RdaDac=RgAudioRam+$116
RdaPtr=$e8

.macro RdaPublic
 php
 pha
 txa
 pha
 tya
 pha
 lda SelectedCharacter
 cmp #2
 jne RdaPublicReturn
 lda RdVariant
 cmp #1
 jne RdaPublicReturn
.endmacro

.segment "ROGUE_AUDIO_ADAPTER_A62"
.export RdaAudioInit
.export RdaAdapterStart,RdaAdapterEnd,RdaState,RdaZpState,RdaFrameControl,RdaDac
RdaAdapterStart:
; Put the shared public return nearby to keep each identity branch in range.
RdaPublicReturn:
 pla
 tay
 pla
 tax
 pla
 plp
 rts
.proc RdaAudioInit
 RdaPublic
 lda #0
 tax
Clear:
 sta RdaState,x
 sta RdaState+$100,x
 inx
 bne Clear
 ldx #5
LiveClear:
 sta RdSfx,x
 dex
 bpl LiveClear
 lda #3
 sta RdaZpState             ; actual source1E gameplay mode
 lda #$1d
 sta RdaZpState+3           ; explicit original LFSR seed2F
 lda #1
 sta RdSfx                  ; exact live source silence/init priority
 sta RdaState+$2c           ; original repeating music flag
 lda #15
 sta GuestNativeEnable     ; buffered only: source has no DMC
 jmp RdaPublicReturn
.endproc
.proc RdaBorrow
 ldx #18
Loop:
 ldy ZpAddresses,x
 lda $0000,y
 sta RgAudioCpuZp,x
 lda RdaZpState,x
 sta $0000,y
 dex
 bpl Loop
 rts
.endproc
.proc RdaRelease
 ldx #18
Loop:
 ldy ZpAddresses,x
 lda $0000,y
 sta RdaZpState,x
 lda RgAudioCpuZp,x
 sta $0000,y
 dex
 bpl Loop
 rts
.endproc
ZpAddresses:.byte $1e,$23,$2e,$2f,$79,$e0,$e1,$e2,$e3,$e4,$e5,$e6,$e7,$e8,$e9,$ea,$eb,$ec,$ed

.macro RdaReadSave
 php
 pla
 sta RdaSavedC
 stx RdsRngDelta
 sty RdsDacDue
.endmacro
; Every replaced absolute ROM load is authenticated by its exact JSR return
; PC. The source operand table distinguishes raw data from relocated code.
; Actual four source LDA absolute,Y sites, all immutable80xx operands.
; IncomingA andNZ are overwritten by originalLDA. C/V/D/I survive the
; constant-offset LDA and are captured before any address arithmetic.
.proc RdaRead8002Y
 lda #$02
 bne RdaReadFixedCommon
.endproc
.proc RdaRead8003Y
 lda #$03
 bne RdaReadFixedCommon
.endproc
.proc RdaRead801AY
 lda #$1a
 bne RdaReadFixedCommon
.endproc
.proc RdaRead804CY
 lda #$4c
 bne RdaReadFixedCommon
.endproc
RdaReadFixedCommon:
 sta RdaPtr
 RdaReadSave
 tya
 clc
 adc RdaPtr
 sta RdaPtr
 lda #$80
 adc #0
 sta RdaPtr+1
 jsr RdaReadRomValue
 jmp RdaReadReturn
.macro RdaIndirectReader name,pointer
.proc name
 RdaReadSave
 tya
 clc
 adc pointer
 sta RdaPtr
 lda pointer+1
 adc #0
 sta RdaPtr+1
 jsr RdaReadRomValue
 jmp RdaReadReturn
.endproc
.endmacro
RdaIndirectReader RdaReadE6Y,$e6
RdaIndirectReader RdaReadECY,$ec
RdaReadReturn:
 ldx RdsRngDelta
 ldy RdsDacDue
 lda RdaSavedC
 pha
 plp
 lda RdaReadValue           ; original LDA changes NZ, preserves CV/DI
 rts
; Compound source instruction replacements retain every original upper PC.
.proc RdaLoadVolume
 jsr RdaReadECY
 sta $ea
 rts
.endproc
.proc RdaAdvanceNote
 ldy RdaState+$38,x
 inc RdaState+$38,x
 jmp RdaReadE6Y
.endproc
.proc RdaLoadNoteY
 jsr RdaReadE6Y
 tay
 rts
.endproc
.include "rogue_dawn_audio_upper_map_v4.inc"

; Actual source3:B189/B199 foreground counter semantics. The C94 source
; bridge supplies real service7 (health) /8 (low). No audio-private RAM/ZP
; is accessed by this foreground routine. Public return preserves AXYP.
.export RdaLowHealth,RdaLowHealthEnd,RdLowHpCounter
RdLowHpCounter=RdSfx+2
.proc RdaLowHealth
 RdaPublic
 lda RdHostService
 cmp #8
 beq Low
 cmp #7
 bne Done
 tsx
 lda $0103,x
 sta RdHit                  ; genuine original Health callback inputA0
 lda RdHealthHi
 beq Done
 cmp #2
 bcs Reset
 lda RdHealthLo
 cmp #$70
 bcc Done
Reset:
 lda #0
 sta RdLowHpCounter
 jmp Done
Low:
 lda RdLowHpCounter
 and #$3c
 cmp #$3c
 bcc Decrement
 lda #8
 ora RdSfx+3                ; literal sourceCBF3 X3 OR/STA interruption semantics
 sta RdSfx+3
Decrement:
 dec RdLowHpCounter
Done:
 jmp RdaPublicReturn
.endproc
RdaLowHealthEnd:
.include "rogue_dawn_audio_scheduler_hooks_v5.s"
RdaAdapterEnd:
.assert RdaAdapterEnd-RdaAdapterStart<=$2d9,lderror,"Rogue audio adapter exceeds root BD27..BFFF lease"

.segment "ROGUE_AUDIO_DRIVER_C97"
.export RdaDriverStart,RdaUpperStart,RdaUpperEnd,RdaReadRom,RdaOriginalRng
RdaDriverStart:
; Called only by the A62 wrappers with A62 currently mapped. Leave the actual
; software A-bank shadow and hardware together, including each temporary map.
.proc RdaReadRom
 jsr RdaReadRomValue
 lda RdaReadValue
 rts
.endproc
.proc RdaReadRomValue
 lda RdaPtr+1
 cmp #$a0
 bcs Upper
 lda $23
 asl a
 asl a
 asl a
 asl a
 asl a
 clc
 adc RdaPtr+1
 sec
 sbc #$80
 tax
 lda RdaLowerHighTable,x
 sta RdaPtr+1
 lda RdaLowerBankTable,x
MapRead:
 sta CurrentBank
 sta $5115
 ldy #0
 lda (RdaPtr),y
 sta RdaReadValue
 lda #$be
 sta CurrentBank
 sta $5115
 rts
Upper:
 ; This is the separately preserved ORIGINAL data view. Some authored volume
 ; reads intentionally address bytes that are also instructions in source49.
 sec
 sbc #$a0
 tax
 lda RdaUpperRawHighTable,x
 sta RdaPtr+1
 lda RdaUpperRawBankTable,x
 jmp MapRead
.endproc
.include "rogue_dawn_audio_rng_v4.inc"
.res $77-(*-RdaDriverStart),$ff
RdaUpperStart:
.include "rogue_dawn_audio_reader_native_v6.inc"
RdaUpperEnd:
.assert RdaUpperStart-RdaDriverStart=$77,lderror,"Original A480 source remains at C480"
.assert RdaUpperEnd-RdaUpperStart=$1b80,lderror,"Complete original upper span retained"
