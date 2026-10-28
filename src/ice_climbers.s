; NES Ice Climber Popo/Nana. Source commitdf2c8e55..., Nintendo manual1985.
; Movement/combat/art are dedicated; Mushroom/Flower are crossover adaptations.
.include "ice_climbers_state.inc"
.include "ice_climbers_core.s"
.include "ice_climbers_render.s"
.include "ice_climbers_art.inc"
.pushseg
.segment "ICE_CLIMBERS_CHR"
.incbin "chr/characters/ice-climbers.chr"
.popseg
