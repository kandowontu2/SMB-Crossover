; StarTropics Mike Jones, expanded MMC5 only.
.include "mike_jones_core.s"
.include "mike_jones_motion.s"
.include "mike_jones_weapons.s"
.include "mike_jones_pickups.s"
.include "mike_jones_render.s"
.include "mike_jones_dispatch.s"
.include "mike_jones_art.inc"
.pushseg
.segment "MIKE_CHR"
.incbin "chr/characters/mike-jones.chr"
.popseg
.export JnMovement,JnEffectiveTier,JnCollectPickup,JnRelease,JnEnemyDrop,JnTrackEnemies,JnShotPhysics,JnPreparePickup,JnAreaReset,JnClearGear,JnLifeLost
.export JnReflectMagic
.export JnShotTerrain,JnReadCell
