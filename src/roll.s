; Mobile-sheet Roll alternate. Platform physics are the installed Crossover
; MegaMan integrator; buster/auto-charge/energy and health are independent.
.pushseg
.segment "SRAM"
RlOutlineBypass:.res 1            ; The final free byte of the existing8KiB.
.export RlOutlineBypass
.popseg
.include "roll_state.inc"
.include "roll_core.s"
.include "roll_motion.inc"
.include "roll_dispatch.s"
.include "roll_shot_bank.inc"
.include "roll_render.s"
.include "roll_fast_render.s"
.include "roll_empty_space.s"
.include "roll_weapons.s"
.include "roll_drop_fade.s"
.include "roll_art.inc"
.pushseg
.segment "ROLL_CHR_MAIN"
.incbin "chr/characters/roll.chr",0,16384
.segment "ROLL_CHR_DW"
.incbin "chr/characters/roll.chr",16384,4096
.segment "ROLL_CHR_Z2"
.incbin "chr/characters/roll.chr",20480,4096
.popseg
