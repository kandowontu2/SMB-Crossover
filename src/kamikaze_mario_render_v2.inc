; Complete source poses, native Mario physics. Reuses inactive Samus record
; pointer and the native Mario16B OAM reservation. No new RAM or service flag.
.pushseg
.segment "KAMIKAZE_CORE"
KmCoreStart:
.proc KmGraphics
 lda MarioVariant
 cmp #4
 beq Celeste
 farcall PlayerGfxHandler::KmNativeGraphics
 lda MarioVariant
 cmp #3
 bne Done
 ldx ObjectMetasprite
 beq Done
 jmp KmSelect
Celeste:farcall CmHostGraphics,jmp
Done:rts
.endproc
.proc KmSelect
 lda KmFrameMap,x
 tax
 lda KmPages,x
 sta SmChrBank
 sta PlayerChrBank
 sta CurrentCHRBank
 lda PlayerFacingDir
 cmp #2
 beq Left
 lda KmRLo,x
 sta SmPosePtr
 lda KmRHi,x
 bne High
Left:lda KmLLo,x
 sta SmPosePtr
 lda KmLHi,x
High:sta SmPosePtr+1
 lda #$84
 sta X5ChrMode
 lda #1
 sta X5WideChrActive
 sta ReloadCHRBank
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 BankPRGC #62
 rts
.endproc
.proc KmPortrait
 php
 pha
 phx
 phy
 lda SelectedCharacter
 bne Foreign
 lda MarioVariant
 cmp #3
 bne Foreign
 ldx ObjectMetasprite
 jsr KmSelect
 farcall HpPrepareNativePointers
 ply
 plx
 pla
 plp
 ldx #METASPRITE_SAMUS_BODY
 farcall DrawMetasprite,jmp
Foreign:ply
 plx
 pla
 plp
 farcall CmHostPortraitRender,jmp
.endproc
.include "kamikaze_mario_source_art_v2.inc"
KmCoreEnd:
.assert * <= $c000,lderror,"Kamikaze complete source poses exceed62B690 gap"
.popseg
