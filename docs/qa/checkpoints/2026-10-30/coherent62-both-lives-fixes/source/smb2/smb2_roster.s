; Private raw25 component. ROOT owns shared dispatcher/linker integration.
.include "smb2_roster_state.inc"
.pushseg
.segment "PARODIUS_BELLS"
 .res 9,$ff                     ; existing1591B owner endsA637, appendA640.
S2ComponentStart:
.assert S2ComponentStart=$a640,lderror,"SMB2 CORE actual append start"
.popseg
.include "smb2_roster_native.inc"
.include "smb2_roster_core.s"
.include "smb2_roster_terrain.s"
.include "smb2_roster_objects.s"
.include "smb2_roster_render.s"
.pushseg
.segment "PARODIUS_BELLS"
S2ComponentEnd:
.assert S2ComponentEnd<=$c000,lderror,"SMB2 CORE must fit approved118 tail"
.segment "CD_GFX"
 ; Existing source-owned CD16..<CE00 alignment padding, never Rogue D600.
 .export S2PortraitDrawC
S2PortraitDrawC:
 ; The actual X5PortraitRender has already preserved the C80 art context and
 ; native pointer snapshot. Common ingress saved sourceA, originalY/P, liveX.
 lda #<DrawMetasprite
 sta FarcallJmpTarget_SMC+1
 lda #>DrawMetasprite
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(DrawMetasprite)|$80)
 jmp FarCallCommon
 .assert .bank(DrawMetasprite)=4,lderror,"Actual native renderer bank"
 .assert *=$cd25,lderror,"Exactly15B inside already-owned S2 sourcepadding"
.proc S2TextStatusC
S2LivesOwnStart:
 ; Near-called only with genuine C80 mapped by the source A74 wrapper.
 ; Y carries priorC, originalY is on the CPU stack below our JSR+PHY.
 phy
 txa                           ; wrapper X retains original sourceA.
 cmp #0
 beq S2TextName
 cmp #1
 jne S2TextDone
 tsx
 lda $0104,x
 cmp #30
 bne S2TextRejectLives
 ; Native WriteGameText has completed its30B lives commands. Its remaining
 ; number patches address only bytes12/23/25, below this appended palette.
 ldx #3
S2TextSaveScratch:
 lda R0,x
 pha
 dex
 bpl S2TextSaveScratch
 lda BackgroundColorCtrl
 pha
 lda #2
 sta BackgroundColorCtrl
 lda #30
 sta VRAM_Buffer1_Offset
 lda #$ff
 sta S2PaletteAck
 ; Preserve the caller-owned five actually mutable SFC operands.
 lda NextBank_SMC+1
 pha
 lda SafecallA_SMC+1
 pha
 lda FarcallJmpTarget_SMC+1
 pha
 lda FarcallJmpTarget_SMC+2
 pha
 lda SafereturnA_SMC+1
 pha
 farcall S2MainPalette
 pla
 sta SafereturnA_SMC+1
 pla
 sta FarcallJmpTarget_SMC+2
 pla
 sta FarcallJmpTarget_SMC+1
 pla
 sta SafecallA_SMC+1
 pla
 sta NextBank_SMC+1
 pla
 sta BackgroundColorCtrl
 ldx #0
S2TextRestoreScratch:
 pla
 sta R0,x
 inx
 cpx #4
 bne S2TextRestoreScratch
S2TextRejectLives:
 lda #1
 bne S2TextDone
S2TextName:
 ; Match original A0 child-call/SFC output exactly. Old PHY set its sourceA
 ; to originalY, found below this helper JSR+saved priorC.
 tsx
 lda $0104,x
 farcall S2GraphicsBank
 ldx #11
 lda #7
 sta R0
 jsr S2MenuCopyC
 ply
 ldy #80|$80                   ; original successful A0 status leaves C80.
 lda #0
 rts
S2TextDone:
 ply                           ; other inputs retain genuine priorC.
 rts
 .assert *-S2LivesOwnStart<=219,error,"Existing C80 source padding only"
 .res 219-(*-S2LivesOwnStart),$ff
.endproc
S2ArtAppend:
.assert S2ArtAppend=$ce00,lderror,"SMB2 ART actual append start"
.popseg
.include "smb2_roster_art.inc"
