# Contra laser renderer repair

Working checkpoint `roster-audit-v49-bill-laser-u` fixes the reported laser
alternating between laser and machine-gun graphics. It also fixes the same
duplicate submission for Flare and excludes other advanced projectile types
from the old roster renderer.

The advanced renderer already owns projectile types32 and above and their
shared CHR window. The old roster renderer subsequently iterated the same
slots and treated every Bill type except1 as a machine-gun bullet. The fix
admits only nonzero types below32 to that older renderer. It adds four bytes
to the METASPRITE bank, changes no RAM or graphics assets and leaves collision,
weapon creation and inventory logic unchanged.

`build/verification/root49-bill-laser-render-a` contains the private build,
native controls, positive tests, screenshots and regression records. On each
mapper,60 actual-controller cases cover Bill/Lance, Normal/Machine/Spread/
Laser/Flare, standing/air/prone and both directions. Each original control
reproduces the wrong legacy rendering in all24 Laser/Flare cases. Each fixed
ROM has zero such cases. Additional guarded native observations verify the
actual emitted source metadata and its mapped data bank, including visible
laser screenshots. The first Lua syntax-error run is retained separately.

All16 existing regression groups pass across MMC3/MMC5, including projectile
priority, sprite overload rotation, combat, inventory, Flare limits and4,800
Laser/Flare collision-equivalence outcomes. Ordinary hardware sprite limits
and shared graphics-window scheduling remain; this is not a universal
flicker-free claim or a full-stage recording.

The publication manifest is
`build/checkpoints/roster-audit-v49-bill-laser-u/manifest.json`, SHA256
`4e9e854ddcd78e5c4aa7231fcea81c95fe86d969eb3bab6129bef872a9ddd0d9`.
The working ROMs match the tested candidates exactly:

- MMC3: `841fd4bf378aa96c983e35f85b59e20609226d965e93acd555deeb5dd669c5b8`.
- MMC5: `4ab8d8c37aab2110b55eeea5850eba54ae0c2b2677763593d786462c673b2ced`.

Only `src/roster_weapons.s` changes in the412-file source catalog. The user's
Easy/Hard strings and seven generated-file edits remain byte-exact. The full
Easy behavior expansion is still private and incomplete; this hotfix does
not publish or certify those separate changes. The broader roster goal remains
active.
