# Current-nightly cadence baseline for the corrected carry candidate

Official174fa remains installed. Root39854 runs its actual Downloads ROM
with strict compiled Lua
`b8b325ae2b49219242d2ba6481a8ea2557afae85de3f25c8f7285677f881c069`.
Native Mesen receipt **passes**:
`66235036ec9d14ad0f7a4e8b48322d4d45cfc67326e34a64a94223f71f878005`.
It observes existing behavior; it does not qualify or install a new candidate.

| Actual174fa window | Returned Main / physical frames | Frames with no4016/4017 read | Actual Main histogram |
| --- | ---: | ---: | --- |
| Idle |48 /48|23 of47 fully observed frames|0:24,2:23|
| Right |32 /32|16 of32|0:16,2:16|

The average is one Main per video frame, achieved by skipped and doubled
updates. It is **not smooth60Hz**. NmiSkipped increases24/16 respectively.
There are zero active enemies in the idle window, HP47/lives2, and the final
state is81/176.353 Main entries equal353 returns over377 total video frames.
The Lua body uses actual read callbacks at4016/4017; its separate input_polls
counter is host input application and does not establish hardware reads.

Root preserves the exact tested19,663-byte LF source as
`tools/reference/bt174fa_cadence_b8b3_1115.lua`. Its body SHA256 is
`f76943af78cedc9d38c6433ed438a2040ccc186c18c2dd6fb686a4fbde179f7e`.
The separately named fixture facade
`replay_battletoads_carry_cadence_fixture_1115.py` SHA256
`53656a3dc35669535f4db5dc20d739db154fbaee4dab020e217b17eb6d5cee25`
reuses that body with strict frozen C/F and actual hook-bank bindings.
Source13991 proves both complete texts byte-for-byte equal the original
qualified factory outputs, receipt
`e85d3796fbe9045a595fbf3315a2c43d18df72918bd668d860e103bfcd5a33c6`.
The candidate observer pin is8f88463c; no original factory is changed.
This avoids reconstructing a historical observer for subsequent comparisons.

The corrected source candidate is
`aceedaf2151fdf673b489a742831a0844abbb3837e0bcba68408d3ba5c3a4cfe`.
It remains source-only until mounted lifecycle/profile/ingress/interrupts and
both full routes close. Root will compare it with the same literal read and
Main-return observer before any speed claim or delivery decision. No physical
candidate exists at this baseline gate; source savings do not close cadence.

Both before/after patch guards and official/private bytes are unchanged.
Only the existing controller file is replaced in the two-file native slot.
No capture files, ROM copies, backups or release assets are created. The root
source fixture proof uses absent `build/battletoads-carry-root-review-1115`,
max1/600s and zero generated outputs; native root uses its existing2-file slot.

## Private corrected candidate: partial cadence gain and both routes pass

Root83713 runs exact acee in the existing private slot. All three native
checks pass; official174fa remains untouched at this gate.

| Private scope | Main / physical frames | Native receipt SHA256 |
| --- | ---: | --- |
| Literal-read cadence |353 /377 total|0412eea79a26d44a4289af63f80c43922236e8ad74e13a213e27636fa41eaad3|
| Rash full1-1 |4254 /4699|87fc83a0d6fc4b4bda4e10ca8d122632cfbb7c63612dbcdc7641299a664c2254|
| Zitz full1-1 |4338 /4801|dbf90604db93f11c509e07409a40ff9aa5ac1d03fa783f8d75ec6fc758a1d898|

The same cadence observer now records idle48 Main/48 physical, but19 missed
reads among47 complete frames (histogram0:20,1:7,2:20), compared with23 misses
on174fa. Right32/32 has15 misses (0:15,1:2,2:15), compared with16. Idle
NmiSkipped increases19; Right increases16. Zero idle actors, HP47/lives2,
Right endpoint83/176. This is a modest improvement; skipped and doubled
updates remain. It is not smooth60Hz or a closed lag defect. Do not infer
an exact stage-speed percentage from stage runs on different older ROMs.

Both ordinary full routes retain real variants0/32, flag/castle/entrance,
then25 living grounded1-2 updates at40/176/area2/engine8/state0, HP39/lives2,
power0. Main entries equal returns. No input/game/health/terrain seeds,
helpers, images or output files are introduced. The source-qualified955-byte
envelope contains714 changes; every unowned byte, all52 Bub palette bytes,
Prince/cache/code/assets and helpers are preserved.

The separate delivery decision permits this useful partial gain while keeping
the remaining cadence work open. Source push, direct Downloads replacement,
sidecar guards and all three actual Downloads repeats remain required.

## Verified actual Downloads delivery

Source push50f7968e precedes installer41682's direct no-backup replacement
with exact acee,2,097,168 bytes. The installer is terminal PASS; its own
before/after sidecar guards are clear. Root initially started verification
38059 before that installer completed. Its exact-byte precondition rejects
the still-old174fa snapshot before Mesen launches. This is retained as an
orchestration negative; no game test or ROM failure is inferred.

After confirming installer completion, root reruns the CLI guard on acee and
starts32707. All three actual Downloads replays **pass**, and each complete
receipt SHA256 and Lua SHA256 exactly matches its private83713 counterpart
above. The partial cadence counts and both full grounded1-2 endpoints are
identical. Final CLI guard is clear, and installed bytes equal the candidate.

The improvement is delivered; remaining skipped/doubled updates stay open.
No other character receipt is silently promoted to acee. Source cycle savings
and two full routes do not establish whole-roster smooth60Hz. Helpers, levels,
all52 prior Bub palette bytes and every unowned byte are preserved.
Root's queue is free after32707. The existing slot contains candidateacee and
Zitz controller93bcd70b only. Build preflight is2,873,625,401 bytes/19,996 files;
protected user files retain bd99b4ee/963a9ef0 hashes. Zero capture files,
backups or release assets are created.

## Actual ACE Main/interrupt/service attribution

Root74702 runs the frozen read-only profiler92a42eb3 with exact Lua
`2c1c0fc42610d67add057f6983d750df6ab94ee4348bf2e3e6d2bfa7a6522704`
on actual Downloads acee. Native receipt **passes**:
`07f374ae854702a6f413c098cb32d162557c0bccd13ecacebf33da7e66809c0a`.
It reproduces the same19/47 idle and15/32 walking missed reads. Every span
is acknowledged:160 geometry getters and206 Wf/206 BtCheck entries/returns,
no pending Main/ISR/getter/service. HuResolve is not reached in this window.

| Actual measured group | Idle | Right |
| --- | --- | --- |
| Representative normal Main exclusive |25,004 cycles|24,930 cycles|
| Representative catch-up Main exclusive |16,729 cycles|16,999 cycles|
| Regular NMI calls / wall range |29 /4,299..6,876|17 /4,298..6,408|
| Busy NMI calls / wall range |19 /2,740..3,403|16 /2,740..3,376|
| IRQ calls / cost |48 /120 each|32 /120 each|
| Wf acknowledged calls / exclusive cost |125 /419 each|81 /419 each|
| BtCheck acknowledged calls / exclusive cost |125 /325 each|81 /325 each|
| Geometry getter12 /13 |48 each /21 and24 cycles|32 each /21 and24 cycles|

Wf419 includes the nested BtCheck325; do not add those service costs.
The native window does not execute three checks on every catch-up Main:
206 total calls differs from the model's one-scheduled-frame-per-Main240.
No authentication is skipped by the candidate. The next attribution must
distinguish normal/render work from the shorter catch-up path rather than
treating the aggregate mean as the normal-frame budget.

Idle Main totals are1,039,532 exclusive plus63,594 interrupt cycles across48
returns; Right totals682,552 plus50,395 across32. Regular NMI exclusive totals
149,141/87,471 (wall149,621/87,831); nested IRQ is accounted separately.
These are measured sums, not a proof that every frame fits its deadline.
The actual first normal frames run into busy NMI; skipped/doubled updates
remain. A new source-only observer will attribute AudioUpdate and actual
source update/draw/collision work before another optimization proposal.

The profiler retains32 bounded representative rows in its in-memory receipt;
normal idle frame297→298 is25,004 exclusive+3,523 interrupts, followed by
16,729+120 in frame298. Right345→346 is24,930+3,496, then16,999+120. It counts
hardware entry/RTI and uses matched PC/SP returns; software RTI does not end
a hardware span. No forced regular-NMI fixtures or nested-service sum is used.
Official/private bytes and sidecar guards remain unchanged, with zero files.
