# Root controller discovery handoff

## Current v32 diagnostic progress

Samus clears 1-1 and normal 1-2 using ordinary inputs in
`root-samus-v32-b-2-v0-mmc3`, entering 1-3 at frame10046. The old generic
enemy policy prioritized elevated Goombas over closer floor threats; the new
owned policy ranks same-height enemies first. This changes the discovery
controller only.

Three same-ROM branches independently match fresh power-on inputs, endpoint,
frames and all10,240RAMbytes: `root-samus32-blocks-a` reaches X1360/Y176 in
1-1, `root-samus32-13-high-a` reaches X860/Y176 in 1-3, and
`root-samus32-13-koopa-a` reaches X1407/Y96 in 1-3 at poll11218. Their exact
input/ROM hashes are in `build/verification/root-samus32-controller-progress.json`.
The next branch `root-samus32-13-next-koopa-a` independently verifies
X1848/Y112 at poll11584. Its continuation clears 1-3 and enters the castle at
frame12722, then genuinely collects the castle mushroom at frame13068.
Generic navigation jumps from its raised used block too early and falls in
the first pit.

`root-samus32-14-first-pit-a` deliberately retains a rejected search root:
poll13080 was still engine9 during the real pickup transition. The corrected
root at13128 is controllable. Its bounded search `...first-pit-b` exhausted
its time limit. A trial reaches X505/Y128 on the ordinary lower floor, but
that later trial was not exported before timeout. The actual exported best
branch independently cold-boots with all10,240RAMbytes exact at poll13144,
X487/Y64/power1. Only that verified `best` root is reusable for matching-ROM
discovery; the lower-floor trial is not a reusable proof.
The short retreat policy `root_samus32_castle_floor.lua` instead contacts the
firebar and is a negative controller candidate, not a demonstrated ROM bug.

The new policies contain no emulated memory/register writes. These are v32
diagnostics, not accepted current-ROM full audits or final recordings.

## V24 complete Samus candidate

`build/roster-through-2-2/root-samus-v24-final-exit-a-2-v0-mmc3/inputs.csv`
is a complete ordinary-controller discovery from power-on through active2-3,
frame25473/poll25472, with no deaths. Stage entries are1-1@541,
1-2@5650,1-3@10482,1-4@13496,2-1@16642,2-2@21201,2-3@25449.
Input SHA-256: `ae054197a94c4f83da1bec72acbc552a6e03dd4b50713b1be11109a6e0990d76`.
The far-water branch through frame24082 was independently verified from a
fresh power-on against all10,240 RAM bytes; the final exit is a controller
policy tail. This fast discovery has not passed the full frame/audio audit.
It is not final acceptance: the new source audit found the shared native
enemy-stomp shortcut incorrectly applies to guests, and that fix can require
retiming earlier encounters. Preserve this candidate and replay on the next
coherent source checkpoint. No Samus video is accepted yet.

## Current frozen v22

Accepted ROM: `build/checkpoints/roster-audit-v22/smb-crossover-mmc3.nes`,
SHA-256 `2ec13bcac6c9c60a37096b0b5e2377c771c345b54325dd26c602c8cfc059debf`.
The current Samus prefix is
`build/roster-through-2-2/search/root-samus-v22-14-bowser-a/winning-inputs.csv`:
poll/frame15773, 1-4 x2245/Y84, airborne, power0. It crosses Bowser after
clearing the first three stages. This branch independently matches a fresh
power-on replay's exact controller polls, target and all 10,240 RAM bytes.
It uses no emulated writes or state loads during verification. No final
six-stage replay or recording is accepted for Samus yet.

The controller-only `root_samus_13_low_cap.lua` wrapper stops before the 1-3
64-pixel ledge, jumps vertically to its real top, then crosses. The subsequent
moving-platform and castle firebar branches are ordinary controller streams.
They establish route feasibility and do not replace full graphics/audio review.

## Historical v12 geometry

No complete six-stage clear is accepted for Samus/Bill/Lance yet. All following
branch winners were independently cold-boot checked against exact input polls,
frames, endpoint and all 10,240 RAM bytes. They are v12 geometry, not final-ROM
proofs; v13's now-superseded costly head helper alters lag timing early.

Paths below are under build/roster-through-2-2/search, use winning-inputs.csv:

- Samus: root-samus-v12-14-midbars-a, poll14725, castle x1980/Y128. Tail
  root-samus-v12-fast-j reaches Bowser x2153 and lands on its head. It jumps
  too early from2064; next branch should wait for Bowser or improve takeoff.
- Bill: root-bill-v12-13-lifts-a, poll12023, 1-3 x1681/Y80. Tail
  root-bill-v12-g clears1-3, enterscastle13351, dies13948. Continuecastle.
- Lance: root-lance-v12-12-first-lift-a, poll9642, 1-2 x2340/Y96. Tail
  root-lance-v12-e clears1-2 normally, enters1-3 at12418, dies12965 on high-cap
  Goomba x625. Use grounded edge fire or a short branch there.

Owned controller-only policy tools/playthroughs/root_samus_contra.lua now
selects forward enemies first, avoiding a stale rear threat suppressing the
next Piranha. For Bill/Lance its first-powerup approach takes over at240 before
the ordinary route jumps atop the block row; this genuinely collects the first
mushroom. Samus/Bill/Lance explicit weapon/upgrade arenas cover broader inventory
items separately and must not be described as controller-collected inventory.

The policy reads Bowser flame ID$15 directly and jumps ahead of floor-height
flames. This passed the first Samus castle flame, but final Bowser timing remains.
All discovery outputs use --discovery-fast and are not accepted final audits.
Final full replay/recording must use the frozen ROM and full audit, without state
loads or emulated memory/register changes. Opaque verified-root reuse is limited
to matching-ROM discovery and still requires independent cold-boot verification.
