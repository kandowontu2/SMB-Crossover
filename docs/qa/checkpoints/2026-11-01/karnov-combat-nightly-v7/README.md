# Karnov projectile combat WIP

The exact0ffb1d79 candidate replaces the single Downloads nightly, without a
backup. Reopen the ROM and start fresh. Rygar -> Select -> Karnov -> A/Start.

Actual controller input crouch-fires the first Goomba, with native score and
hit sound, then collects a block-emerged mushroom and fires double shots.
A second route shoots the lone coin box, advances past that used block, then
breaks a brick with debris and shoots the mushroom question block. Its item
emerges normally. The124-transition menu sweep also passes on this exact ROM.

Collision now follows the visible bottom8px of the original8x16 projectile
tiles; standing flames naturally pass above low enemies. HoldDown+B to aim
lower. Native damage/HP, score positions, brick debris and block items retain
their existing owners. The real ten-row loader copies/readbacks all1280bytes
before paired cache validity. Actual Main and cold-loader IRQ/NMI tests retain
at least12bytes above native SMC storage. See handoff.json for precise scope.

Equipment activation, its UI/icons and original audio are not integrated.
Full levels/shortcut/all-powerup testing remains unfinished. This remains an
86-selectable WIP, not a completed Karnov implementation or new roster count.

The obsolete block-route diagnostic stopped behind the first used coin box;
the final route advances to the brick row. Earlier ground-fire diagnostics
identified the blank-half hitbox. Historical diagnostics do not qualify this
delivery. Frozen native templates have conservative legacy scope strings;
their hash-bound ready scopes and explicit counters define these tests.

Packets contain source/recipes/receipts and12 screenshots, no ROM, fulldebug,
object, video or per-frame dump. Separate component packets are explicitly
marked as integrated or pending in handoff.json.
