; Expanded MMC5 only. Authored original sprites, distinct original-game profile.
.include "darkwing_core.s"
.include "darkwing_weapons.s"
.include "darkwing_pickups.s"
.include "darkwing_recovery.s"
.include "darkwing_art.inc"
.pushseg
.segment "DARKWING_CHR"
.incbin "chr/characters/darkwing.chr"
; The live legacy route is RlLegacyDrawDispatch through Z2DrawGuard.
; Its former, unreferenced DwDrawGuard allocation now holds the Roll
; interior-render admission; all other draws retain NativeGoombaRender.
.popseg
