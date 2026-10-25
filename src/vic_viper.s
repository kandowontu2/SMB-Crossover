.include "vic_native_motion.s"
.include "vic_art.inc"
.include "vic_adapter.s"
.include "vic_render.s"
.include "vic_dispatch.s"
.include "parodius.s"
.pushseg
.segment "VIC_CHR"
.incbin "chr/characters/vic-viper.chr"
.popseg
