; PRIVATE f467 successor: native SMB backdrop + authentic source body colors.
; Internal only: actual RdBodyColors/Graphics/LifeGraphics already prove raw2/Rd1.
; No new RAM. Original source palette0 universal entry is never published.
; Requires ROOT approval for the existing A121 item-tail subdivision BF00..BF6F.
.import RdRenderPalettePointer,FarCallCommon
.import SafecallA_SMC,FarcallJmpTarget_SMC
.import VRAM_Buffer1,VRAM_Buffer1_Offset,BackgroundColorCtrl,AreaType
.import RdColorRequest
.importzp R0
.export RdBackdropQueue,RdBackdropStart,RdBackdropEnd
.segment "ROGUE_DAWN_HOST_AUX"
.res 2,$ff ; exact previous qualified segment ended BEFE; never infer from FF alone
RdBackdropStart:
.assert RdBackdropStart=$bf00,lderror,"Exact item descriptor predecessor changed"
.proc RdBackdropQueue
 sta SafecallA_SMC+1
 lda #<RdRenderPalettePointer
 sta FarcallJmpTarget_SMC+1
 lda #>RdRenderPalettePointer
 sta FarcallJmpTarget_SMC+2
 lda #<(.bank(RdRenderPalettePointer)|$80)
 jsr FarCallCommon
 ldx VRAM_Buffer1_Offset
 cpx #77                      ; native 84-byte region: complete7B packet+null
 bcs Busy
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$10
 sta VRAM_Buffer1+1,x
 lda #4
 sta VRAM_Buffer1+2,x
 ldy BackgroundColorCtrl
 bne Color
 ldy AreaType
Color:
 lda NativeBackgroundColors,y
 sta VRAM_Buffer1+3,x
 ldy #1
Copy:
 lda (R0),y                  ; actual source suit/missile three opaque roles
 sta VRAM_Buffer1+4,x
 inx
 iny
 cpy #4
 bne Copy
 txa
 clc
 adc #4
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 sta RdColorRequest           ; ACK only after the complete successful command
 sec
 rts
Busy:
 clc
 rts
; Exact native X5LegacyGetPlayerColors/BackgroundColors, validated by builder.
NativeBackgroundColors:.byte $22,$22,$0f,$0f,$0f,$22,$0f,$0f
.endproc
RdBackdropEnd:
.assert RdBackdropEnd<=$bf70,lderror,"Approved narrow palette tail exceeded"
