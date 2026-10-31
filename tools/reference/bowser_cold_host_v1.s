; All ROM-only callbacks fit already granted six A-only Bowser islands.
.setcpu "6502"
.macpack longbranch
.include "common.inc"
.import FmAlts,SmPosePtr,SmChrBank,CurrentCHRBank,ObjectMetasprite,X5SetPhysicalChr
.import BwPortrait1Right,BwPortrait3Right,BwLoad,BwConstruct,BwRetire
.import S2InitScreenPrepare,FwMuxMenuResolve,DrawMetasprite,WriteGameText,BwColors
.export BwScene,BwMenuResolve,BwColdPrepare,BwColdDraw,BwStatusName

.segment "BW_ROM_COPY"
BwMenuResolve:
 BwFar BwRetire,jsr
 BwFar FwMuxMenuResolve,jmp

.segment "BW_ROM_PREVIEW"
BwColdPrepare:
 lda FmAlts
 and #8
 lsr
 lsr
 tay
 lda BwColdPtrs,y
 sta SmPosePtr
 lda BwColdPtrs+1,y
 sta SmPosePtr+1
 tya
 lsr
 eor #1
 clc
 adc #<824
 ldx #3
 ldy #0
 BwFar X5SetPhysicalChr,jsr
 lda CurrentCHRBank
 sta SmChrBank
 lda #.lobyte(.bank(BwPortrait1Right)|$80)
 sta CurrentBankC
 sta $5116
 lda #$e9
 sta ObjectMetasprite
 rts
; Stored pointers intentionally address the genuine C-view of this ROM data.
BwColdPtrs:.word BwPortrait3Right+$2000,BwPortrait1Right+$2000
BwColdDraw:
 php
 pha
 lda #.lobyte(.bank(BwPortrait1Right)|$80)
 sta CurrentBankC
 sta $5116
 pla
 plp
 BwFar DrawMetasprite,jmp
.assert *<=$b600,lderror,"A83 ROM portrait budget"

.segment "BW_ROM_AUX"
BwScene:
 BwFar S2InitScreenPrepare,jsr
 php
 pha
 txa
 pha
 tya
 pha
 lda SelectedCharacter
 cmp #27
 bne BwSceneDone
 BwFar BwLoad,jsr
 bcc BwSceneDone
 lda #<BwConstruct
 sta FarcallJmpTarget_SMC+1
 lda #>BwConstruct
 sta FarcallJmpTarget_SMC+2
 lda #3
 jsr FarCallCommon
BwSceneDone:
 pla
 tay
 pla
 tax
 pla
 plp
 rts
; Original native text must finish FIRST. Only its actual lives A1/Y30
; continuation appends the body packet; unused flame P2 remains native.
BwStatusName:
 cmp #1
 bne BwStatusNative
 cpy #30
 bne BwStatusNative
 BwFar WriteGameText,jsr
 php
 pha
 txa
 pha
 tya
 pha
 BwFar BwColors,jsr
 pla
 tay
 pla
 tax
 pla
 plp
 rts
BwStatusNative:
 BwFar WriteGameText,jmp
.assert *<=$b400,lderror,"A88 scene/status budget"
