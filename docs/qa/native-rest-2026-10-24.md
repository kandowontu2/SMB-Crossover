# Native food, copy abilities and route continuation

The complete roster and every-powerup goal remains active. The adopted private
checkpoint is `build/checkpoints/native-rest-py/candidate.nes`, SHA256
`70480630828a92839938b18b3e4f73acd8f9255879b2174df00f41c2e6cf98c9`.
Its source ZIP SHA256 is
`7a5ad21d2099018a01d3ca4b97c55634076cb9f250710268092fbd6dfeb1f72f`.
The receipt is `build/verification/native-rest-py/proof.json`.
`finalize_py_once.py` succeeded and must never be rerun.

Evidence and all large captures remain outside the workspace in
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py`.
Public ROMs and the NU player guide were preserved. Immediately after adoption
the workspace occupied 29,987,692,508 bytes, below the user's 30 GB cap.

## Three reproduced defects

Kirby's copied Red Cheep wave started downwards. From a ground shot at Y196,
its first updates moved it into the floor and consumed it before the nearby
enemy was hit. Two direction immediates now start the same eight-update wave
phase upwards. Speed, lifetime, instruction addresses and cycle costs stay
unchanged. The negative trace and actual physical frames are retained in
`kirby-wave-diagnosis-v1`; the corrected native attack passes.

Chip and Dale always wrote scene power status zero after healing, so the next
ordinary block could never naturally reveal a flower. Their real mushroom and
flower receipts now set the next appearance from the collected actor's type.
Health and scene appearance remain separate. The existing heal/cap/SFX return
contract is preserved. A ten-byte helper adds 22 CPU cycles once per health
pickup, never to ordinary movement or attacks. The parent negative is retained
in `chip-natural-flower-parent-v1`.

Tall copied-enemy HUD icons covered Kirby's coin counter. The existing icon
now occupies the empty left margin beside his name. Only its two coordinate
operands changed: no additional sprites, graphics or CPU work were introduced.
The old and current physical-frame sheets retain the overlap and correction.
This checks placement; it is not a new source-color certification of the icons.

The four source changes are `src/kirby_weapons.s`, `src/kirby_draw.s`,
`src/chip_dale_health.s` and `src/chip_dale_dispatch.s`. Relative to PX, exactly
19 ROM bytes change in PRG banks 74 and 79. All 54,005 previous qualified symbols
keep their values; one helper label is added. CHR, levels, RAM layout, jump and
collision code remain byte-identical.

## Native checks on the adopted ROM

All fourteen Kirby copy families pass in Easy and Hard: real inhale/swallow,
controller attack or passive behavior, Select discard, world-star recovery,
re-swallow and natural drop expiry. Combat checks use actual enemy defeat,
guard contact or cloud hover as appropriate. Starting copied inventory is not
injected. Source-family actors and visible/logical arenas are explicitly staged;
this is not proof that every family naturally appears in 1-1.

Eight food cases pass for Kirby, Meta Knight, Chip and Dale in both modes,
covering 44 native actors. These require real head bumps, full emergence,
collection receipts, health caps, healing SFX, star contact/expiry and 1-Up lives.
Chip/Dale's first mushroom, subsequent flower, capped mushroom and next flower
now arise without seeded scene power status. Only the final injured-flower
case seeds health to one. Mature actors are brought to the player after 110
ticks to isolate physical collection. Player X and active block columns must
remain exactly 112 through the head-bump window. Meta never gains copied
equipment or flight from food.

All 37 identities pass cold selection, alternate persistence, lives/level
entry, ordinary movement and interrupt ownership. These are entry tests, not
37 complete level clears.

The same exact ROM also passes Zelda II's linked numeric/pause arithmetic:
3,584 level/defer combinations and 17,920 cancellation boundaries, with all
24 prices authenticated against the original USA cartridge. Real spell uses,
enemy-earned EXP/drop restoration and the full native UI remain separate gates.

## Static and physical evidence

The wave-only predecessor executes 46,080 assembled motion-span cases with
exact original cycle costs. The combined predecessor executes 5,040 actual
collection cases with identical live registers/flags, health, sound and other
RAM except the intended next-food status. The adopted ROM differs from that
combined predecessor in exactly two HUD coordinate operands. These static
receipts retain their true parent hashes; they are not relabeled current runs.

Six current direct component streams retain 22,893 actual PPU frames losslessly:
both copy suites and Chip/Dale's four food suites. Every saved PNG is checked
against the physical screen buffer, with complete frame IDs, input/state and
hardware-audio traces. Human review covers 112 selected copy moments and 96
food moments. It is sampled review, not an exhaustive human inspection of
22,893 frames or source-perfect SFX proof.

The first copy stream passed emulation and conversion but its final host
read-all digest failed on the large raw file. A retained streaming recovery
independently verifies the raw/gzip identity and every PNG/index. Its original
raw file remains. Subsequent captures use streaming digests. No gameplay
assertions or input streams were changed to resolve this host failure.

The complete 1,217-file source ZIP independently rebuilds the adopted ROM.
Ordinary flag-off MMC3 and MMC5 builds retain their preceding hashes:
`d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb` and
`f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833`.

## Additional parent evidence and ongoing routes

Six PX CV3 routes are now independently qualified, with 31,577 actual PPU
frames, exact saved inputs/traces and the original strict motion/CHR/split,
code/stack/NMI/IRQ guards. The six sampled overview sheets were inspected.
These are PX evidence, not new PY route clears.

On PX, all eighteen Parodius integration/pickup/bell cases pass, including 90
actual hardware source-pixel pose comparisons. Both Vic gear cases and all
four Meta physical/move cases pass. Their explicitly staged actors, purchased
bar positions and component scope remain declared in the original receipts.

`known-routes-v3/progress.json` records fresh adopted-ROM 1-1 discoveries using
65 previously proven identity/mode controllers. Old proofs select controls
only. These discoveries still need independent current-hash replays and visual
review. Nine older unsuccessful controller pairs and shortcuts remain separate.

The first new Mega Man Easy attempt fell into the second staircase gap after
jumping from a lower step. A controller-only stair-top landing and new held-A
edge clears zero-death in 5,114 frames. The original failed attempt remains.
No physics, terrain, position, health or equipment write was added. Its strict
independent replay is tracked in `megaman-ledge-replay-v1`.

Remaining work includes the unfinished roster routes and shortcuts, remaining
native item uses/passives/refills/expiry/SFX, visual and palette polish, source
music, performance, MMC3 and guide consistency. Existing heavy attack lag has
not been represented as constant 60 Hz. The overall goal is not complete.


## Current roster continuation

The adopted hash now has zero-death cold-menu 1-1 clears for all 37 identities,
covering 71 of 74 identity/difficulty pairs. Complete selected-discovery bindings
are in the external `current-37-bindings-v1.json`; the root snapshot is
`build/verification/native-rest-py/roster-progress-v1.json`. The selected 37
runs total 186,070 controller frames. Original unsuccessful attempts and failed
aggregate reports remain; successful individual runs are explicitly validated.
Mario Hard, Bass Easy and Dale Easy still need successful current controls.

Corrections were confined to read-only controller policies: land before a gap,
brake earlier for horizontal inertia, take off later, use native crouch combat,
consider visible enemies in both directions, and hold Bass's automatic buster.
No additional ROM, position, terrain, health or equipment change was made.

Mega Man Easy independently qualifies with 4,914 complete physical PPU frames.
Bass Hard qualifies with 7,095. Bass's raw movement rejection is retained;
the original read-only native guard verifies the temporary origin and the
scoped guarded review passes. Bill Easy follows the same explicit sequence
inside the running 35-identity replay batch. Strict independent qualification
and sampled human review are still incomplete for the full roster.

The 35-case independent physical replay batch is running externally in
`current-roster-direct-v1`. Its frozen helper streams large file digests to
avoid the prior host read-all failure. Native inputs, pixels, frame bounds,
scroll/world/CHR assertions and raw-rejection behavior are unchanged. The
root drivers remain pinned. Inspect its progress receipt before launching any
additional native worker; use at most two total.

Human review so far includes current Mario Easy, Luigi Easy, Mega Man Easy
and Bass Hard overview sheets. A suspicious apparent far-right column was
traced to adjacent contact-sheet panels. Mario's individual frame 1814 has
only sky in the disputed strip, and its PPU/map tiles match. The retained
501-frame read-only snapshot replay leaves the original inputs, state and
CPU cycles exactly unchanged. No game defect or repair is claimed from that
false lead.
