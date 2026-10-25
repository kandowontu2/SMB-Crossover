.include "kirby_core.s"
.include "kirby_weapons.s"
.include "kirby_dispatch.s"
.include "kirby_draw.s"
.include "kirby_legacy.s"
.include "kirby_art.inc"
.include "kirby_copy_icons.inc"
.include "meta_knight.s"
.include "meta_knight_art.inc"
.pushseg
.segment "KIRBY_CHR"
.incbin "chr/characters/kirby.chr"
.popseg

.export KbGlobalInit,KbAreaReset,KbEnsure,KbInputs,KbMovement,KbGraphics,KbPortrait,KbDeathUpdate,KbInjuryStatus,KbInjuryStart,KbHealPickup,KbFamilyForEnemy,KbWeapons,KbDrawShots,KbDropCopy,KbAbilityMove,KbBodyContact,KbHeadDispatch
.include "kirby_world_palette.s"
