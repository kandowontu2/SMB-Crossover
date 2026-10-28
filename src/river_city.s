; Alex / Ryan: authentic NES pixels and brawler actions, SMB scene adapter.
; Public entries require exact SelectedCharacter=21 admission by root dispatch.
; A=jump, B=punch, Down+B=kick, airborne B=flying kick, Up+B=grab,
; a second fresh B while carrying throws. Double-tap left/right runs.
.include "river_city_state.inc"
.include "river_city_core.s"
.include "river_city_combat.s"
.include "river_city_render.s"
.include "river_city_art.inc"
.pushseg
.segment "RIVER_CITY_CHR"
.incbin "chr/characters/river-city.chr"
.popseg
