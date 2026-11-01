; Original FF27/8BCF capsule eligibility, not a selectable admission.
; Negative original projectile types80/81 in source slots1..3 only.
; Original enemy/GravityFire metadata is deliberately outside this component.
.export MsNativeObjectsReady,MsNativeShotTileQuery,MsNativeAnimationMask,MsObjectsHostEnd
.import MsObjectUnsupported
MsDonorMapperSelect=$c818
MsDonorMapperData=$c819
MsNativeObjectsReady:
 php
 pha
 txa
 pha
 lda MsState+$717
 bmi BadObject ; GravityFire can create unsupportedslot1 later in actor step
 ldx #23
CheckObject:
 lda MsState+$510,x
 beq NextObject
 cpx #4
 bcs BadObject
 lda MsState+$528,x
 cmp #$80
 beq CheckObjectFlags
 cmp #$81
 bne BadObject
CheckObjectFlags:
 lda MsState+$600,x
 cmp #$0a
 bne BadObject
 lda MsState+$6a8,x
 bmi BadObject
NextObject:
 dex
 bne CheckObject
 tsx
 lda $0103,x
 ora #1
 bne ObjectResult
BadObject:
 tsx
 lda $0103,x
 and #$fe
ObjectResult:
 sta $0103,x
 pla
 tax
 pla
 plp
 rts

; The original shot collision code tests separate normal/upgraded bits08/10.
; Native fully solid terrain admits both contact masks; actor FF1E remainsE0.
; Bit02/04 donor hazard flags remain clear. X retained, Y=0, A/P volatile.
MsNativeShotTileQuery:
 jsr MsNativeTileQuery
 lda MsTileFlags
 beq :+
 ora #$18
 sta MsTileFlags
:rts

; Original rendererF2EA..F2F7 reads byte(state+5) from original actor metadata.
; Keep that exact source animation mask even before native OAM integration.
; Call after actor step (renderer ordering), and for the first ctor pose.
; All AXYP retained; no source/host pointer or PPU accesses.
MsNativeAnimationMask:
 php
 pha
 txa
 pha
 lda MsState+$4e0
 cmp #8
 bcs :+
 tax
 lda MsActorAnimationMasks,x
 sta MsState+$5a0
:pla
 tax
 pla
 plp
 rts
MsObjectsHostEnd:
