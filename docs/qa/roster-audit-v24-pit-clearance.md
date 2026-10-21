# Pit crouch clearance, v24 candidate

V22 passed its 623 regression case slots, but Pit's subsequent full six-stage
controller replay exposed a separate physical overlap. This candidate remains
provisional until the broader regression suite and current-ROM replays pass.

## Actual replay finding

`build/roster-through-2-2/pit-v22-full-audit-6-v0-mmc3` clears through 2-2,
but its automated review correctly flags six consecutive 16-pixel shifts in
1-4. Pit moves from X1567 to1663 at Y65..67, with no directional input and a
stationary camera. This is a rejected final route despite reaching the endpoint.

The read-only probe in `build/roster-through-2-2/pit-v22-snap-probe` records
the actual `STA Player_X_Position` at fixed-bank CPU address $EA4A. Its caller
is the upper-left side collision, with R0=2; this is not the deep-foot selector.
Before the first shift, the crouched adder at Local_eb70 changes to the standing
adder at33 when Down is released. Both feet are below the ceiling and empty,
while the newly exposed standing head and upper side probe lie in ceiling
metatile $62. The left clamp then advances a player whose X ends in $f by a
whole tile repeatedly. The bounded screenshots show the traversal directly.

## Correction

Pit retains his short body after Down is released until the newly exposed
standing head band is clear. `PitStandClearance` checks both horizontal edges
at two heights, excludes coordinates outside terrain, and restores the world
position after probing. One byte records the retained crouch and resets with
the ordinary area/life state. The no-Down/no-retained-crouch path skips the
bank call.

While a roof retains the short body, releasing Down permits ordinary directional
movement so Pit can leave the space. Deliberately holding Down preserves the
stationary crouch. Arrow attacks and subsequent jumps remain available.

V23 is rejected: it prevented the airborne expansion but trapped a grounded Pit
under a low roof because the ordinary crouch path stopped horizontal movement.
Its partial broader suite was stopped; no final recording used that candidate.
V24 adds the required movement out of that retained pose. Native Mario/Luigi
dispatch is unchanged. The retired expanded Luigi launch helper moves to a cold
bank to make room; playable Luigi still uses Mario's native engine.

CHR bytes are identical to v22 for each mapper. SRAM still ends at $7FB9;
the new byte occupies existing alignment space. V24 code ends: EXPANDED $BFB8,
EXPANDED_EX $BF09, SAMUS $B27A, FIXED $F2EF.

## Evidence and current limits

`tests/pit-crouch-clearance.lua` independently compares the actual short/full
body boxes with authored roof geometry, rather than reproducing the helper's
four probe equations. Its 48 cases cover ground/air releases, mirrored facings,
page seams, stationary/moving input, prompt open-space standing, deliberate
Down stopping, arrows, and later jumps. Both v22 negative runs reproduce the
16-pixel displacement at case1/age4. V24 passes all48 cases on both mappers.

- Fixture SHA-256: `a22b5c4be76f85c5de62cccb04e034a95765adefb213f9a3c4f52c559e647e89`
- Results: `build/checkpoint-tests/pit-crouch-clearance-v2-v22-v24/summary.json`
- Frozen ROMs: `build/checkpoints/roster-audit-v24/manifest.json`
- MMC3: `36dad7ac1bcdd9f87e80345fb767e99d46d042115c229366bca668d598337214`
- MMC5: `2e216d5e7d69467c529ed109d4f42d5853a73a215f2c4e5eb49dcba0ac03912a`

The full 625-slot diagnostic run finished with 624 passes and one failure:
Link water movement on MMC5. The Link fixture was changed during this run to
the newly audited 2.02 immediate-speed contract, while this frozen ROM still
contains the older accelerated movement. This mixed-fixture run is diagnostic
evidence, not acceptance. Future full runs bind before/after fixture hashes and
fail if any fixture changes during verification. Final videos remain held.
Earlier v22 videos and controller proofs remain historical evidence; they do
not substitute for final recordings on the next accepted ROM.
