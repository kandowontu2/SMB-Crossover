; Host entry: frozen native kernel/art with corrected isolated allocator.
; Dedicated Celeste Mario DELUXE kernel, source-derived from reproduced MG.
.if ::ENABLE_MMC5_EXPANDED
.include "celeste_mario_host_state.inc"
.include "celeste_mario_core_small_host.inc"
.include "celeste_mario_kernel.inc"
.include "celeste_mario_render_small_host.inc"
.pushseg
.segment "CELESTE_MARIO_CHR"
.incbin "chr/characters/celeste-mario.chr"
.popseg
.endif
