# Added-roster World 1-1 review

Five playthrough assignments cover the 18 added identities: Proto Man, Darkwing
Duck and Zelda II Link; Kirby, Chip and Dale; Grant, Sypha and Alucard; Little
Mac, Mike Jones and SMB3 Mario/Luigi; Vic Viper and the four turtles. The desktop
permits three child agents to execute concurrently, so two assignments followed
the first completed assignments.

Each route starts at reset, selects the character through the actual menu,
traverses the surface route of World 1-1, reaches the level end, and regains
movement control in World 1-2. Saved controller inputs are replayed separately.
No cheats, position injection, emulator state edits or forced level transitions
are used to establish a route clear. Isolated CPU tests and seeded ability
fixtures are separate evidence.

The final combined ROM is SHA256
`2b0a3b7ee1581bc011b8df1f7e1683020a7fa3f90f580e142c070f7f3e3d75ba`.
All 18 identities pass, totaling 82,167 video frames with zero deaths and at
least 25 frames of restored control in 1-2. The frozen checkpoint is
`build/checkpoints/full-roster-nd`.

## Repairs found during the runs

- Refresh the Easy/Hard body-contact cache for Chip/Dale, Kirby, Little Mac,
  Mike Jones, SMB3 Mario/Luigi and the turtles. Ground characters can perform
  their intended Easy-mode stomps. Vic Viper explicitly clears the foot-stomp
  cache and retains its ship shield/contact policy in both modes.
- Bound added HUD and palette commands by the actual 84-byte display queue.
  The earlier limits allowed writes into the adjacent level-update queue.
  Checks cover every offset and include reproductions of the old overflow.
- Space Darkwing's health/gas display and Chip/Dale's health display. Give the
  CV3 companions a compact health/heart/weapon display, with a dirty cache that
  is invalidated on actual level transitions. Move the authentic Gradius power
  bar down one row so it remains inside television overscan.
- Use native side probes during Little Mac's flagpole/castle exit sequence.
  His gameplay body probe had prevented the original exit state from advancing.
- Let Vic Viper's native post-flagpole walk scroll enough to leave the base of
  the pole, then restore the lock. Ordinary ship gameplay and the flag slide
  retain their existing camera rules.
- Separate turtle head and side samples using the original standing, rolling
  and crouching body shapes. An off-center head sample mistook pipe/stair sides
  for a ceiling, displaced the turtle downward and could push it into terrain.
- Repack SMB3 world items/effects into stable world sprite palettes. Their
  prior palette writer recolored native Koopas. Original item silhouettes,
  placement, flips and all body graphics are retained; no CHR pages are added.

## Selection and lives screens

The expanded menu uses a three-row gray portrait grid, one colored highlighted
preview, a single highlighted name and plain controller instructions. The
cursor and divider have dedicated tiles. Character identities and navigation
order remain the same.

The shared front-end renderer now snapshots native pose pointers and retains
the graphics bank chosen by a dynamic portrait. The former path replaced
Proto Man's and Zelda II Link's art bank with their legacy character's bank.
Proto Man's regular palette updates also convert his base colors, including on
the lives screen. Tall lives portraits and Raphael's raised sai are positioned
clear of the WORLD text and preview boundary. All 32 selected identities have
native selection/lives captures for visual review.

## Bass's missing arm

The original Crossover body and separate arm clips are composed for the idle,
horizontal-fire and airborne-fire poses. Walking and diagonal-fire pixels are
preserved. The same correction is applied to the Pharaoh body variants. The
new ordinary poses need at most seven body sprites on a scanline with outlines
off; the earlier greedy composition needed nine and could hide its own arm.
Graphics are repacked inside their assigned banks. Original hurt art and the
private walking bank remain unchanged.

The standard MMC3 and smaller MMC5 builds receive the Bass artwork correction;
the added-roster changes remain in the full-roster MMC5 build.

## Evidence and limits

The combined-build matrix, ROM hashes, source manifest and retained capture
locations are bound by the final checkpoint manifest. Per-frame native records
include graphics-bank publication, OAM, scrolling and contact telemetry.
Visual review uses whole-route contact sheets and consecutive frames around
suspect events. Lossless frame streams are retained locally or in verified
external archives to respect the 30 GB workspace cap.

Twelve original input recordings passed the final combined ROM. Six needed
fresh controller recordings after lag changed which game updates received
brief button presses. Active-entry states and physics matched; the original
failed attempts are retained. Fresh Alucard, Sypha, Darkwing, Zelda II Link and
Mike routes were independently replayed. Kirby retains his entire old input
prefix and adds a normal jump at the pole base. All six new input streams and
per-frame traces match their independent replay confirmations exactly. No ROM
changes were made during this retiming step.

The final ROM also passes all 32 cold identity/menu/lives checks, 14 focused
ability suites, 30 native spring/contact arenas, both outline guard fixtures
and 768 compiled Proto Man palette-queue cases. Its 64 selection/lives PNGs
are byte-identical to the complete, visually reviewed menu capture set.

These are Easy-mode surface-route clears and focused behavior checks. They do
not certify every weapon, every upgrade, every sound effect, Hard-mode full
routes, shortcut-pipe routes, all campaign levels or physical cartridges.
Posting-video production remains deferred as requested.
