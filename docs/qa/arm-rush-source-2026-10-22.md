# Super Arm, Rush and Mega Man audio

Both main mapper builds now include the prepared Super Arm payment correction,
Rush input/energy rules, Rush spring landing sound and native Mega Man audio
optimization. These changes were composed onto the actual Rygar world-palette
GA source; newer cheats, HUD, terrain publication, score, cannon, firebar,
Sophia and Water Shield changes remain present. Checkpoint:
`build/checkpoints/weapons-source-go/manifest.json`.

In the extracted Crossover 2.02 source, Super Arm checks its eight-unit energy
requirement before lifting, lifts and carries for free, and pays at the actual
throw. Switching weapons or taking damage before throwing costs nothing. A
throw without enough energy leaves the held brick intact. Star power makes
the action free. The former port charged at lift time. Both Mega Man and Bass
now use the source payment timing. Terrain, collision and art are otherwise
unchanged by this correction.

Rush requires at least four energy units, or Star power, to summon; summoning
costs nothing. Pressing attack while Rush already exists fires the ordinary
buster, respecting the shared three-projectile limit and active charged shot.
A successful spring spends twelve units, clamps insufficient remaining energy
to zero, and sets the source jump-release and vertical-friction flags. The
spring now requests the source Land effect in Hard Mega Man mode. Its six
encoded register-image frames match the retained native source capture's
audible updates, including pulse/noise timer retriggers and release back to
continuing music. Pause, shared world sounds, character changes and higher
priority injury effects retain their ownership rules. This does not claim
sample-perfect waveform or subframe source write timing.

The audio optimization removes redundant MM3 zero-page transfers and restores
only the active music engine's CPU snapshot range, while still executing every
music/effect update. The new Land state occupies 52 previously unused bytes
inside the existing reserved audio slab; the slab and all old RAM addresses
stay fixed. Every old nonempty public code address remains fixed; only the
zero-length DPCM end marker moves within its original physical bank. Header,
CHR and both rebuilt baseline ROMs remain byte-identical. No OAM or CHR parts
are added. The special roster bank retains 76 MMC3 / 82 MMC5 free bytes.

Validation on the actual combined candidate, reproduced byte-for-byte by both
main builds:

- Four mapper/baseline builds pass. `weapons-current-gf` records the exact
  seven-file additive overlay and unchanged original source catalog.
- `weapons-mechanics-gi` passes 34 fresh native groups: eight Arm cases for
  each of two characters on each mapper, and fifteen Rush cases per mapper.
  Its 250 captured foreground callers independently reexecute against the
  compiled ROM with exact registers, all 10,240 RAM bytes, stack, ordered
  writes, mapper state and the source payment/projectile/jump oracles.
- `weapons-land-gg` passes twelve native audio/lifecycle groups and independently
  reexecutes 516 complete AudioUpdate calls with their attained interrupts.
  It compares source effect images, retriggers, release and ownership rules.
- `weapons-regressions-gh` passes 24 unchanged focused mapper checks for menu,
  score, terrain, cannons, firebars, flagpole, combat, overloaded projectiles,
  Rush, block rewards and native music/effects. `weapons-broad-gn` also passes
  the broad Bass fixture on both mappers. Only its two old Arm payment
  expectations change, exactly matching the separately source-backed successor;
  the old fixture and all other assertions remain retained.
- `weapons-audio-cost-gk` compares matched quiet full audio calls. MMC3 saves
  474 cycles for MM3 song-start samples and 322 for MM2 samples; MMC5 costs 42
  additional cycles for the landing-sound hooks. Checked registers, ports,
  mapper state and live RAM match. Any popped stack differences are individually
  traced. These are local call costs, not a whole-game lag-solved claim.
- `root-rygar-weapon-gm-7-v0-mmc3` replays the complete fixed ordinary-controller
  route on the new ROM, clearing through 2-2 with zero deaths and actual control
  in 2-3. It is a replay proof, not a new recording.

The first private builder stopped on an overly broad host text anchor before
assembly; that attempt remains in `weapons-current-ge`. The corrected GF builder
uses complete-line boundaries. All native captures and negative evidence remain.

The retained old Bass movie controller tape is not a current proof. Fresh GA
and GF replays both die at frame 2251 in 1-1, with every captured trace, OAM,
CHR, scrolling, input and audio-event CSV byte-identical. This is an unchanged
route-transfer failure, not a newly introduced weapon regression. Bass's
current route is being retimed. His shared world/face palette conflict remains
open, as do the complete roster, every-weapon fidelity, performance and final
recording requirements. The full goal remains active.

The additional current-GO route transfer audit (`roster-current-gu`) also tests
the twelve other legacy tapes. None transfers as a zero-death clear: eleven
stop in 1-1 and Luigi loses a life in 1-2. These are current Easy/MMC3 fixed-input
transfer results, not proof that a character cannot finish a level. The earlier
all-green/fourteen-movie claims in README are now explicitly tied to their older
checkpoint. New source-guided Bass inputs clear 1-1; independently cold-boot
verified GQ, GS and GV branches reach 1-2 X2673/Y96 with the mushroom retained.
This is partial route progress, not a full clear or final recording. The exit
pipe needs an approach beneath its upper lip.

The source also contains code/icons for Magma Bazooka and additional Rush forms,
but MegaMan.as and Bass.as exclude them from their 2.02 obtainable-upgrade arrays.
Their mere presence in the shared weapon definitions is not evidence that an
additional obtainable weapon is missing from this port.
