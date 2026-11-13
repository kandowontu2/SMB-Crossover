# Private Prince cache fix: native checks and entry defect

Public Downloads remains62ba7f54. Private candidate
`209abc2fd6144d59720e54352ed6f9f7384e2fa9ede0fbb1fb37f9e02d385008`
restores the original pre-animation X save. It changes24 existing decoded
runtime bytes, preserves the other two decoded streams, and reverses exactly
to public62. No helper, normal movement constant or native level data changes.
Source/funding/cold/IRQ/fault proofs are in `prince-earned-sword-combat-1113.md`
and root's independent `prince-original-position-cache-1113.md`.

## Actual Mesen

The exact read-only combat controller848c67e3 requires runner `variant=3`.
The first native invocation mistakenly used default0 and stopped after the
first pipe at2617 frames; its7b381e9f receipt is only first-pipe evidence.
It was not accepted as a sword-combat pass.

With variant3, the same exact controller passes7849 physical frames and3511
source commits. The actual mushroom then mature flower grants the sword at
frame6717,X1260/Y112. Original action62 parry and58 attack lead to actual
guardHP1→0 at original8725, source proxy export, native call kind1 and
bank254:9AF8, all at commit3499. Native slot0 becomes defeated state34 with
score1. HP4/lives2/Star0 remain. After12 more updates a second real opponent
is acquired asUID129/action55; this is one verified fight, not a full sword
route. Receipt:
`702af2eb8687109b455c36058b6891c72a3001a4942feb45f04bb1f94b8d1900`.

The existing full nonshortcut1-1 controller also passes on209abc: native
flagpole, castle and final gap, active1-2 at16295 physical frames with both
lives. It ends at X40/Y48,HP5, before the entry drop completes. Controller
`a1513cbe9a25bf1b56b1c2c0cb1e7dc2d4e53ad5cf32798de34db8e9abce3357`,
receipt`d58fb0867068c7f7f5a6bed6c7694279bede83427e3995a67b8c4f939972f06b`.
This proves the1-1 clear; it does not prove safe1-2 gameplay or full-stage
sword use.

Unselected Steve's unchanged controller3c477bf9 passes the actual private209
ROM through all eight1-1 obstacles and into grounded1-2,6175 physical frames,
X40/Y176,HP4/lives2. Receipt:
`d248b723fb57d6ef025d6502ea4c5d3204d5cbc8bf5b1cdf6ac483564dee2a36`.

Root also compares the actual menu/Select/renderer/NMI CPU results before and
after209: all101 portrait, silhouette, identity and state rows are exactly
unchanged, digest`f58ec905102307ca87d9c302248fa7da9c44cd5550df154323e67024da245db7`.
No extra sheet is generated. This is not a fresh physical raster audit.

## Stronger entry check exposed an existing defect

The new3dbbf79a controller continues with neutral input after active1-2,
requiring grounded Y176 and120 physical frames. On209 it catches sourceHP0
at frame16391/commit7025,X48/Y176,action53/mode255. The wrapper initially
threw the full receipt before printing its digest; the terminal failure was
observed and retained, and the wrapper now prints compact metadata first.

The exact same route and entry check on public62 produces the same source
failure: initial1-2 frame16293,X40/Y48,HP5; terminal16389/commit7025,X48/Y176,
HP0/action53/mode255. Public baseline controller
`72cf8939d7eec83b2e7ed859ffe0e0876b57eca3cf5ed1e2a8ab26844cf47444`,
receipt`60a582a76742591d672e64c3ba64a0361c5f02895c6387aef27314ef33698577`.
Thus the entry death is preexisting, not introduced by the cache save. It
remains an open gameplay defect. Original fall-counter/health writes and the
native entrance handoff are under investigation; no fall immunity or physics
change has been applied.

Private209 is not installed or published at this checkpoint. The strict
native runner is `tools/audit/check_prince_draw_cache_native_1113.py`; its
extended `stage` case intentionally remains failing until the entry defect is
resolved. The independent trace generator is
`tools/audit/replay_prince_entry_trace_1113.py`.

All native runs use the shared Mesen queue, existing capture watchdog, zero
capture files and the two-file `build/metal-flower-native-1112` output root.
Only candidate.nes and controller.lua are reused; no backup or video was made.
The full roster/powerup goal remains incomplete.

## Native fall-counter cause

The public62 trace generatorf2a20ff6 reproduces the same failure with receipt
`6f766a3728a0a2fc3279eac4818d3b19c6b55658b79c0ba8faaac8a9e67d88fd`.
After the live1-2 handoff, source fall-counterC6C6 increments0→7 at commits
7001/7005/7009/7013/7017/7021/7025, native Y96/107/118/132/146/160/175.
The RMW bus includes unchanged old-value writes. At the landing in commit7025,
healthC6CF is deliberately drained5→4→3→2→1→0, X0, before action53 starts.
The exact decoded live writers are raw3:A03B `EEC6C6` and raw3:A342 `9DCFC6`.
Mesen reports next-PC A03E/A345 inside write callbacks; the trace's `pc` and
`instruction` fields must be interpreted accordingly. Earlier engine0 records
include cold staging/clearing and are not valid actor-state snapshots.

The helper independently reaches the actual normal underground entrance
(AreaType2/header1/Alt0,engine7/X40/Y48,HP5,lives2,counter0). A clone of that
genuine state calls unchanged AutoControlPlayer(0), with no engine, position
or health seeds. Native gravity and BG collision land atY176/state0 after34
calls; source health/counter/phase stay5/0/0. The real profile uses32-pixel
feet. This is a direct native ABI fixture, not a mounted fix; source receipt
`590f5502f11aa444cfca21a04f33abb8c69e2080c7c532bdc633e3d5384e7083`.
A scoped transport that defers the ordinary entrance handoff is now being
developed. Normal controllable Prince fall physics remain unchanged.
