# Simon air jump and empty special-pool work

Accepted component checkpoint with known roster defects. Staged validation
covers all761 current-ROM slots. The initial41d full run passed759 and failed
two MMC5 Water Shield CPU budgets. After correction, all378 MMC5 slots ran
again on41e;383 passing MMC3/baseline slots remain bound to byte-identical
ROMs and current-CRC raw logs. Fixtures stayed unchanged in both batches.
This is not a single all-passing full run. The roster goal and final recordings
remain incomplete. Summary: `summary-roster-audit-v41-provisional-e.json`.

- MMC3 SHA256 `a26efdc525def83287a82bb78bbe70deba5d77417408be64c446f21033378366`.
- MMC5 SHA256 `c83a24fa60df0660e9a7ea171fcefd008d47d2a74363c8098f3579e6540fbedd`.

## Runtime changes

Simon now rearms his unused air jump while grounded. Pinned2.02
`Simon.checkState` grants `canDoubleJump` on ground before its attack branch;
walking off support must retain that opportunity. The seven-byte change in
`src/roster.s` leaves other characters' ground state unchanged. Separate
Simon/Ryu collision-profile and attack-phase corrections remain pending.

On MMC5, Mega Man and Bass skip shared special-weapon physics/draw loops only
when all ten shared shot types are zero. Input, clocks, inventory, palette,
pickup and CHR publication remain. Exhausted-loop scratch is reproduced.
Any nonzero type takes the existing loop; highest slots are checked first
to return promptly for usual live allocations. MMC3 remains byte identical
to41a/41d. Native audio and resident banks remain unchanged from40.

## Independent controls and retained failures

`simon-walkoff-v40-component-b/negative-summary.json` freezes an actual40
negative on both mappers. Its authored1-1 ledge is not terrain-edited;
player/environment setup is explicitly seeded and is not a route proof.
Twelve cases cover dry/water walk-off, whip cancellation, armed/unarmed air
jumps, exhaustion and real landing controls. Water is an environment override,
not2-2 traversal. All twelve cases pass unchanged on each41e mapper:
`simon-walkoff-v41e-positive/report.json`.

`special-empty-v41a-v41e-mmc5.json` checks1624 whole compiled CPU cases through
SpecialWeapons/SpecialDrawShots. A/X/Y/allP/SP, C000 physical bank and every RAM
byte below8000 match41a; only discarded stack/farcall target scratch is
excluded. Empty live input/clocks/inventory, occupied-slot fallback, rotating
starts and publication transitions are covered. Empty physics saves up to274
cycles; empty drawing up to294. Occupied checks add up to83/72 in these
controls, with usual highest-slot allocations cheaper. These are CPU units,
not PPU, interrupt or traversal proof.

41b exceeded MMC3 bank capacity at link time.41c changed the overflow flag;
41d fixed that with DEX but its unconditional ten-slot check raised Water
Shield expansion maxima to6127/6128, exceeding the unchanged6100 budget.
All negatives and the failed full summary remain.41e restores expansion
maxima6089/6090 and averages5534/5535. Both characters deliver100/100 orbit
DMA frames with zero orbit lag, and60/62 expansion DMA frames. No flag
comparison or performance budget changed.

## Walking results and setup qualification

The first40c-to41d comparison retains196 Bass integer-X/fraction differences
in scenes6/16. A read-only probe proves mismatched pre-seed startup:
40c previousRight0/step0;41d previousRight1/step6. Staging held Right can execute
a foreground step before setup. The v40 arena initialized Mega Man's separate
edge/timer but omitted Bass's corresponding state. That negative remains.

The separate v41 arena initializes XgBassStep0, RgPreviousButtons to held input
and XgFresh0 on both ROMs. All20 scenes,60 updates and204 fields remain; no
field/tolerance is excluded.40c-to41e matches all2400 MM/Bass updates. Five
other characters retain the original arena:6000 updates match, with identical
physical-frame/draw counts in all100 scenes. Samus's four-Goomba walking stays
60 draws/60 updates. See `plain-walking-v40c-v41e-bass-aligned-comparison.json`
and `plain-walking-v40c-v41e-other-comparison.json`.

Default outlines-off four-Goomba walking:

| Character |40c draws/physical frames|41e draws/physical frames|
|---|---:|---:|
|Mega Man|30/60|35/60|
|Bass|37/59|44/60|

Several six-Goomba scenes finish sooner. Two small counterexamples remain:
MM two-Goomba outlines-off walking loses one draw (60 to59, same60 frames);
Bass's row above takes one extra measured physical frame. No per-scene
zero-regression claim is made. A repeated live-music Bass supplement has1200
more matching updates/204 fields: total frames1200 to1199, draws881 to1053;
no repeat loses draws. Repeat20 still has a59-to60-frame boundary example,
with42 to50 draws. See `plain-walking-v40c-v41e-bass-repeated-comparison.json`.

These9600 paired updates are seeded components, not controller playthroughs.
Dense-scene lag, hardware sprite limits and four inherited38 regressions
against37 remain qualified.

## Rebuild and remaining work

The401-file41e archive rebuilds both ROMs byte identically from fresh extraction
with separately supplied compiler/Python/Pillow. SHA256:
`6c7144c1f5aa4776b997426b1aeb2f899ef91de9cd0ce919e0972a9d97eacfd8`.
Receipt: `build/checkpoint-tests/source-v41e-rebuild-smoke/report.json`.
The manifest binds the archived README and its later documentation-only update.

Outlines remain off by default with a gold option row. Samus's ordinary jump
does not stomp under2.02; Screw Attack supplies aerial contact damage.
Ryu wall/vine primary attacks remain independently negative on40/41. A passive
Sophia38d route traced normal NMI consuming a partially published timer command
during catch-up; current-build reproduction/fix is next. Bill Flare source
disagreements are being bound separately. Geometry, every weapon and upgrade,
final-hash routes, videos and final visual QA remain unfinished.
