# Player CHR publication repair — private checkpoint NP

The private MMC5 candidate is
`build/verification/chr-publication-np/candidate-v2.nes`, SHA256
`a21df869bdfa8d66c6a8ce3ea83b87e83e82afd0206b5f539c49703479ee3549`.
This is a graphics ownership repair, not a final roster release. The published
33-identity MMC3 menu repair and both ordinary 14-identity cartridges are unchanged.

## Reproduced problem and repair

An overloaded gameplay update can select a new animation pose and then skip
constructing sprites. Kirby, Meta Knight, the turtles and Parodius were also
changing the physical player tiles at pose-selection time. The PPU then drew
old sprite positions/tile indices with the new pose's tiles.

The existing 140-frame entry checks missed this. Longer controller runs on
checkpoint NO reproduced 38 bad graphics frames for Kirby,155 for Meta Knight,
8 for Leonardo and2 for Octopus. Those native clears failed the graphics check.
The original discovery runner did not propagate the observer failure; its
original exit/status records are retained and explicitly excluded from passing
graphics evidence. The runner now propagates that failure for discovery too.

Gameplay tile publication now happens when the corresponding sprites are
constructed. Portraits on the selector/lives screens publish explicitly.
The first candidate removed explicit publication but still failed: MMC5's
`PlayerChrBank` aliases `CurrentCHRBank+0`, so its early stores had the same
effect. Candidate v2 also removes those early alias writes. No sprite artwork,
physics, collision data, menu controls or RAM reservations changed.

The graphics return path does not promise X/Y results. Its gameplay caller
immediately enters `BlockObjMT_Updater`, which initializes X and initializes Y
before use; the victory path initializes the drawing machinery. Restoring
unneeded old far-call register side effects was not used to retime gameplay.

## Evidence

`build/verification/chr-publication-np/proof.json` binds all results to the
candidate hash and exact input/trace/fixture files.

- Nine fresh controller discoveries and independent fixed-input replays clear
  1-1 with zero deaths and restore movement in1-2: Kirby Easy, Meta Knight Hard,
  all four turtles Easy and the three Parodius alternates Easy. Each replay's
  input file exactly matches its discovery recording.
- Those independent replays contain45,412 video frames and31,667 eligible
  graphics observations with zero tile/sprite ownership mismatches. The passive
  observer checks actual hardware windows against the last constructed and
  DMA-published body image; Parodius also checks windows6/7.
- All37 identities pass fresh cold selection/movement/interrupt-ownership
  entry checks on v2. These are entry checks, not37 campaign clears.
- Meta Knight sword/block/protected-terrain/food/SFX/health/flight arenas pass.
  Turtle health, physical pickups, protection/death and all12 identity/direction
  attack arenas pass after genuine current-menu startup.
- All three Parodius component, Bell and physical pickup suites pass. Pickup
  pictures include45 actual rendered comparisons against authenticated source
  pixels and the declared palette mapping. Roll's Easy component arena passes.
- Standard MMC3/5 builds retain hashes
  `97913a42a48b1d48c0dfde61fcc6f9eb406ec325f749dc439b96af85ba3108b4`
  and `7982aed6838e7c56e15390c67b7ddc05bd3acaab7a59bd5e2d3a91eb5bf07128`.

All failures remain. V1 still fails the observer. Three old NO route recordings
die when replayed on v2; fresh v2 controller recordings independently reproduce
their death-free clears. Old turtle fixtures use an obsolete fixed menu pulse
schedule; health/attack arena setup, actions and assertions were preserved while
waiting for actual current-menu entry before starting their fixture clocks.
The unmodified old natural turtle/Kirby-food scenes also fail on NO with the
same first assertions; they are not passing current reward/campaign evidence.

## Remaining issues and scope

This check proves matching tile ownership; it does not prove complete visible
sprites or source animation fidelity. Sampled screenshots were inspected, not
every image frame manually. Global lag, first-eight-sprites scanline dropout,
dedicated audio, production oversized MMC3 integration and the final every-
identity/every-powerup campaign matrix remain open under the final gate.

Two additional visible issues were identified during this pass:

- Pentarou's normal pose164 has8 overlapping body sprites per scanline before
  projectiles are counted. With shots allocated first, much of its body drops
  out. The matching-CHR observer correctly does not certify visibility. Repack
  or allocation/flicker work is required; it is not repaired by NP.
- Parodius's HUD uses `!?` without an explicit `?` character mapping, displaying
  an unrelated tile. Its reset cell precedes the defense cell. The guide records
  the current order; a game HUD repair is still needed.

Parodius death currently falls through a Vic Viper graphics path while its
variant draw hook remains active. That separate path needs direct death-frame
verification. It is outside the engine8 observations above.
