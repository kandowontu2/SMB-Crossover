.include "little_mac_core.s"
.include "little_mac_render.s"
.include "little_mac_terrain.s"
.include "little_mac_pickups.s"
.include "little_mac_combat.s"
.include "little_mac_art.inc"
.pushseg
.segment "LM_CHR"
.incbin "chr/characters/little-mac.chr"
.popseg
