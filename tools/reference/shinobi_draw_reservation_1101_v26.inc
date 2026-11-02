; Direct emitter publishes an empty native descriptor after finishing. Point
; at unbanked ObjectMetasprite[0], not C2 or A3, since farcall restores mappings
; before RosterProjectileOamReady reads SmPosePtr. No extra OAM reservation.
ShHostDraw:
 php
 pha
 txa
 pha
 tya
 pha
 .repeat 8,I
 lda R0+I
 pha
 .endrepeat
 lda ShReady
 cmp #$a7
 bne ShDrawReturn
 lda #1
 sta ShDrawPhase
 ldx #0
 jsr ShNativeDrawObject
 ldx #1
ShDrawSlots:
 lda ShRenderMasks,x
 and ShDrawBits
 beq ShDrawNextSlot
 jsr ShNativeDrawObject
ShDrawNextSlot:
 inx
 cpx #5
 bne ShDrawSlots
ShDrawReturn:
 lda #0
 sta ShDrawPhase
 sta ObjectMetasprite
 lda #<ObjectMetasprite
 sta SmPosePtr
 lda #>ObjectMetasprite
 sta SmPosePtr+1
 ; Exact saved stack order, compacted only in this leaf to fit its own span.
 ldx #7
ShRestoreDrawScratch:
 pla
 sta R0,x
 dex
 bpl ShRestoreDrawScratch
 pla
 tay
 pla
 tax
 pla
 plp
 sec
 rts
