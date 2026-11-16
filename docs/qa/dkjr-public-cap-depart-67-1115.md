# DK Jr. first-pipe fall cause and ordinary cap departure

The current67 first-pipe failure is an original landing injury after a
58-pixel drop, with the original24-pixel limit. A new controller waits near
the helper's right edge until actual pipe-cap grounding, then walks right.
That narrow first-pipe component passes the actual67 CPU source model.
Native qualification is pending. No game, helper, terrain or fall-limit change
is proposed.

## Actual native cause

Root80300 replayed unchanged43b5 controls with the passive2ad observer.
Diagnostic completed with original gameplay **false**, receipt
`3b87a46813d934605ff0db14c84a86afcc22bcad3a7724774f1be4c8173007f7`.
The first pending source5 store is RAM3:A8DD, SP194/P65, Main1135/frame2804,
player450/144, source/prior4, originalY159/origin101/limit24.
Querykind3/body[80,159,97,174] has real pipe supports
[79,176,94,191] and[95,176,110,191], with no walls. The departed416 helper
is at top79, rising, passenger255. This is the existing authored first pipe,
not a newly fabricated floor or a reported nonexistent wall.

Last actual carry was Main1102/X449/Y86/sourceY101, origin105, helperTop118,
VY254, passenger5. First source1→4 was Main1105/X450/Y86, before the original
state-entry code republished the origin from originalY101. The resulting
landing at159 is58 below that origin. The earlier first support loss at
Main1065/X440/Y140/sourceY155 was during the original cross jump, with held129;
it is not the later terminal landing.

`check_dkjr_public_low_depart_67_1115.fall_code(raw67)` authenticates these
actual serialized instructions, without executing a modified routine:

| Current RAM3 PC | Original label | Relevant behavior |
|---|---|---|
|A8CE|DA22|Calls A8E1; nonzero selects A8DB|
|A8DB|DA2F|Loads5|
|A8DD|DA31|Stores5 toC06B|
|A8E1|DA34|Reads originalY, subtracts origin if not upward, compares limit|
|A8F0|DA40|BCS selects result1 when drop≥limit|

The only three literal original origin stores in the authenticated8160-byte
program are A26C, A275 and A9AA. Each derives directly from originalY: the
two original source-state entry paths and the original detach/jump path.
No private floor repair is present. The exact original comparison gives
`159−101=58≥24`, so the recorded A5 follows its intended branch.
These observations support an ordinary fatal-drop diagnosis; they do not
justify bypassing fall injury or changing collision geometry.

## Retained first wait-policy negative and measured gate

`replay_dkjr_public_low_depart_67_1115.py`, SHA256
`2c9d042fadfac88d0ddd6d0deda65f9a44d307e73c3f51044d8b65e638d09176`,
Lua `f3e772cb69a17803efb3b772f60d4806744c22fc90973309d50d011860f3dd8e`,
tried one ordinary first-pipe wait at X446. Its low-departure condition required
simultaneous grounded state, the existing exact carry witness and a descending
helper top154..160. All other pipe controls and game bytes stayed unchanged.

Source11022 was a bounded **input negative**, receipt
`b69ba1292f37a2b80e977bc2eb7c6b8060d55c133a1c215ccde40c2f12505a21`.
It remained alive at446 after2800 updates, with no source5 writer, but no
departure occurred. This controller is retained unchanged, rather than
presented as a functional route.

The short, separate source13480 window explains the admission miss, receipt
`820353d70cee2e4368ab283d556cc8752509fdb6061a913c41dc0c91f2862406`.
At descending tops154/155/157, the player was X446, source4/native2, with feet
152/154/156: one or two pixels above the moving platform. The strict existing
carry witness remained from Main785. Requiring all the low-departure conditions
together therefore did not qualify at these actual source observations.
The diagnostic retained only three specific condition-window witnesses.
It changed neither ordinary controls nor any game state to obtain them.

## Source-qualified cap-departure successor

New factory `tools/audit/replay_dkjr_public_cap_depart_67_1115.py`:

- SHA256 `d4a14cf6d92f5c561ac3025369d67d7e1d5c056e07315044818d2e054b6f534c`.
- API `controller(raw67)`, strict exact current input/public packet.
- Native Lua SHA256
  `5c65a62251a0613e0c072087cc81f94716426e037c3ae9618d59e3415ddd9ffa`.

It preserves the X446 wait and adds a distinct ordinary departure: player at
least446, source1/native0, nativeY144/sourceY159, helperTop≥180. The player is
then grounded on the known pipe cap while the helper is at least four pixels
below his feet176. It walks right with A released. This does not manufacture
a native passenger or suppress a fall; ordinary game collision must supply
those grounded states. Other pipes, hazards and the old full-route assertions
remain unchanged. Reversing the declared first-rise text replacement recovers
the exact old43b5 controller.

Source83910 passes the first-pipe component on actual67, receipt
`797517f36288880aa233fba369483740032435982df829334bcead80605c5aaf`.
Departure is Main974 at446/144, source1/native0/sourceY159, helperTop180,
origin155/limit24. It reaches510/111/lives2 at1193 source updates with no
source5 writer. The inherited `predicted_drop` event field is `cap−helperTop`;
its value−4 identifies the below-feet helper at this static-cap departure,
not a negative actual fall. The live game makes the landing decision.

`check_dkjr_public_cap_depart_67_1115.py` reuses the same authenticated cold and
first-pipe component checker, with the new controller explicitly rebound in
memory. Source-only endpoint instrumentation stops at X510; native factory
still retains the old full route and active1-2 endpoint. This is **first-pipe
source qualification**, not source/native full1-1 or25-grounded1-2 evidence.
Source component Lua is
`22a3abebdb2d9ee69aaa35e567bc3d49c7822d7e76740fbf2e89ef9a80d9c745`.

Root's next native run may use the frozen controller with
`SMB_DKJR_FAST_ROUTE=1`, variant0 and exact67 ROM environment. It can report
the first-pipe result and any later route result separately. No helper-native
launch, private ROM composition or nightly change is authorized from this lane.

Every producer used its exact absent bounded root, max-files1/600 seconds,
and generated zero files. Roots: `build/dkjr-public-low-depart-67-1115`,
`build/dkjr-public-depart-window-67-1115`, `build/dkjr-public-cap-depart-67-1115`.
No actor/player/item/health/terrain seeds, copied ROMs, captures or patch assets
were used. The thirteen helpers remain exactly those in
[dkjr-current-recovery-67-1115.md](dkjr-current-recovery-67-1115.md).
