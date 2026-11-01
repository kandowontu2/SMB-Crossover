; Original Karnov actor/weapons in conditional RAM3, state in conditional C2.
; Not a gameplay admission. Every unimplemented service explicitly rejects.
.setcpu "6502"
.macpack longbranch
.define KrDispatch KrInlineDispatch
.importzp R0
.export KrState,KrPointer,KrSourceFrame,KrSourceWeapons,KrCacheServices
.export KrKernelEnd,KrTerrainResult,KrSoundEvent,KrSceneEvent
KrState=$c000
KrPointer=R0                 ; actual foreground scratch; never NmiR0..2
KrTerrainResult=$c800
KrSoundEvent=$c801
KrSceneEvent=$c802
KrSaved0=$c7fe
KrSaved1=$c7ff
KrExternal_C1C7=KrSceneCallback
KrExternal_C81D=KrSoundCallback
KrExternal_C3D8=KrTerrainCallback
KrExternal_C2B7=Kr_C2B7
.segment "KR_KERNEL"
KrCacheServices:
.repeat 36
 jmp KrReject
.endrepeat
KrReject:clc
 rts
KrDispatch:
 .include "portable_dispatch.inc"
 .include "portable_actor.inc"
 .include "portable_weapon.inc"
 .include "portable_clear.inc"
; Same source leaf contracts as isolated component. Callback events are a
; declared boundary for later native SMB terrain/audio/scene adaptation.
KrTerrainCallback:
 lda KrTerrainResult
 rts
KrSoundCallback:
 sta KrSoundEvent
 rts
KrSceneCallback:
 sta KrSceneEvent
 rts
.macro SourceCall Target
 lda KrPointer
 sta KrSaved0
 lda KrPointer+1
 sta KrSaved1
 jsr Target
 php
 pha
 lda KrSaved0
 sta KrPointer
 lda KrSaved1
 sta KrPointer+1
 pla
 plp
 rts
.endmacro
KrSourceFrame:SourceCall Kr_F28D
KrSourceWeapons:SourceCall Kr_AAB2
KrKernelEnd:
.assert KrKernelEnd<=$bfe0,lderror,"Karnov kernel exceeds conditional RAM3"
.res $1fe0-(*-KrCacheServices),$ff
.incbin "kr-cookie.bin"
.res 16,$ff
