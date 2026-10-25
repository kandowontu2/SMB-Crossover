.include "tmnt_native_motion.s"
.include "tmnt_animation.inc"
.include "tmnt_core.s"
.include "tmnt_equipment.s"
.include "tmnt_projectiles.s"
.include "tmnt_equipment_draw.s"
.include "tmnt_draw.s"
.include "tmnt_combat.s"
.include "tmnt_dispatch.s"
.include "tmnt_art.inc"
.include "tmnt_secondary_art.inc"
.include "tmnt_fast_render.s"
.include "tmnt_health_render.s"
.include "tmnt_primary_render.s"
.export TnMovement,TnGraphics,TnPortrait,TnAreaReset,TnEnsure,TnWeapons,TnDraw
.export TnTrySecondary,TnGiveEquipment,TnAllWeapons,TnDrawEquipment,TnEnemyDropDispatch
.export TnPreparePickupDispatch,TnPrivatePickupDispatch,TnRisePickupDispatch,TnPickupCollisionDispatch,TnCollectEquipment
.export TnQueuePalette,TnInjuryStatus,TnInjuryStart,TnHeal,TnDeath
.export TnMovementDispatch,TnGraphicsDispatch,TnPortraitDispatch,TnDeathDispatch
.export TnWeaponsDispatch,TnDrawDispatch,TnSpecialDrawDispatch,TnPickupDispatch
.export TnInjuryStatusDispatch,TnInjuryStartDispatch,TnBodyDispatch,TnResetDispatch
.export TnAdderDispatch,TnBoxDispatch,TnHeadDispatch,TnBoundingBoxGate,TnVisibleDispatch
.pushseg
.segment "TMNT_CHR"
.incbin "chr/characters/tmnt.chr"
.popseg

.include "tmnt_hud_world.s"

.include "tmnt_probe_gates.s"

.include "tmnt_middle_probe.s"

.include "tmnt_head_ceiling.inc"
