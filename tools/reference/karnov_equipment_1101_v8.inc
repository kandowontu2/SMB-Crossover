; Original Bomb/Ladder object cluster. Unallocated component, not a host grant.
; Caller maps private original state C000..C7FF and supplies the current-stage
; ROM read backend. Source OAM/background packets stay private until adapted.
.export KrEquipmentBomb,KrEquipmentBombRender,KrEquipmentBombBlast
.export KrEquipmentLadderGrow,KrEquipmentLadderRestore,KrEquipmentLadderOverlay
.export KrEquipmentLadderRetract,KrEquipmentLadderRebuild,KrEquipmentEnd
.export KrEquipmentOriginalRebase
.include "karnov-equipment-portable-v8.inc"

; Sequential with existing source actor/options wrappers. Never nest a second
; saved-pointer wrapper: C7FE/C7FF is one shared two-byte context, not a stack.
.macro KrEquipmentSourceCall Target
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
KrEquipmentBomb:KrEquipmentSourceCall Kr_AE3D
KrEquipmentBombRender:KrEquipmentSourceCall Kr_A27B
KrEquipmentBombBlast:KrEquipmentSourceCall Kr_CCFC
KrEquipmentLadderGrow:KrEquipmentSourceCall Kr_A4B6
KrEquipmentLadderRestore:KrEquipmentSourceCall Kr_A5BD
KrEquipmentLadderOverlay:KrEquipmentSourceCall Kr_B46F
; Original camera owner also shifts the private player/enemy pools. This is
; source evidence, not a host camera hook: adapting only the Bomb anchor must
; happen at the real host scroll boundary, without double-moving the actor.
KrEquipmentOriginalRebase:KrEquipmentSourceCall Kr_AF3F
KrEquipmentLadderRetract:KrEquipmentSourceCall KrEquipmentRetractCore
KrEquipmentLadderRebuild:KrEquipmentSourceCall KrEquipmentRebuildCore
KrEquipmentRetractCore:
 jsr Kr_A5BD
 jmp Kr_D700
KrEquipmentRebuildCore:
 jsr Kr_A5BD
 jmp Kr_DB00
KrEquipmentEnd:
