; Alex / Ryan: authentic NES pixels and brawler actions, SMB scene adapter.
; Public entries require exact SelectedCharacter=21 admission by root dispatch.
; A=jump, B=punch, Down+B=kick, airborne B=flying kick, Up+B=grab,
; a second fresh B while carrying throws. Double-tap left/right runs.
.include "river_city_state.inc"
.include "river_city_core_host_v8.inc"
.include "river_city_wall_prepass_v2.inc"
.include "river_city_combat.s"
.include "river_city_shared_palette_host_v8.inc"
.include "river_city_shared_palette_art.inc"
.pushseg
.segment "RIVER_CITY_CHR"
.incbin "chr/characters/river-city-shared-palette.chr",0,8192
.segment "RIVER_CITY_EXTRA_CHR"
.incbin "chr/characters/river-city-shared-palette.chr",8192,3072
.popseg
