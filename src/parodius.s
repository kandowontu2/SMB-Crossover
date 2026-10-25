; Expanded native Famicom Parodius component and explicit SMB adapters.
.include "parodius_native.s"
.include "parodius_bell_native.s"
.include "parodius_data.inc"
.include "parodius_art.inc"
.include "parodius_contact_data.inc"
.include "parodius_adapter.s"
.include "parodius_render.s"
.include "parodius_death_art.inc"
.include "parodius_death.s"
.include "parodius_fast_render.s"
.include "parodius_bells.s"
.pushseg
.segment "PARODIUS_CHR"
.incbin "chr/characters/parodius.chr"
.popseg
