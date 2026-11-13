# Prince first pickup: input diagnostic

Current Downloads ROM: `464c8f1af0401ba7d5393e331833af5bdd68882c536dfc3c77534b71508213c0`.
Controller-only Mesen, no state injection or captures. The bounded runner reused
`build/prince-first-pickup-1112/controller.lua` (one file).

The approach evades the first Goomba, runs to X400, turns left and settles at
X333/Y176 with HP5 and two lives. Up and A are distinct original actions:

- Up enters action14, poses67 onward. Native Y stays near176 instead of rising.
  Receipt `4d63a6d80c055bc07500ab28c9d29292a7602afa77135389d84187a3dc402c67`.
- A enters action3, poses16 onward, moves left to the camera boundary X305,
  and returns to action0. Sampled Y reaches174, not the block overhead.
  Receipt `d05acc71d7dbade1f856cf22c98ba9db839e5bcfcdaf1f6e4004df53a7603fc7`;
  script `f298396036f78e044189f43323e681c7498dfbe9e823f48987565917e0e71be7`.

Neither attempt spawns the item. Global minimum Y161 belongs to the earlier
Goomba evade and must not be described as the standing jump apex. The diagnostic
exits1 intentionally when no item spawns; this is not a passing pickup test.

Next: inspect the source coordinate/terrain bridge during original jump pose
updates, including camera-boundary clipping. Establish whether this is a native
vertical publication error, source terrain response, or incorrect approach
before changing gameplay. These results do not prove a missing block-bump call.
Prince's earlier full1-1 clear remains separate evidence. No ROM changes made.

## Source-coordinate follow-up

Physical write callbacks narrow the A-button case: C611 receives only two writes
during the entire attempt, 128→122 at PC $A251 (phase145/pose24), then122→128
at PC $A25C (phase149/pose25). Origin stays77/high0 throughout. Thus the trace
does not show a large source jump being erased by a repeated host Y write.
Investigate original action3 pose commands/projection before changing floor
clamping. The current callback watches CPU C611 only when mapped to RAM2;
it is not proof against writes through another alias.

Receipt `3a967dcf6a500b533749476677db82b0cbb756f367d6cc4dd2293a420894d4d3`;
script `051560564983fb76f52fb3820710b37d0eb84f2559c81937310211c07b73ebbf`.
All100 update samples are retained in the in-memory receipt; stdout displays
only changes in source Y, origin, projection delta or action. No captures added.

## Original ROM comparison resolves the shallow-hop question

`check_prince_original_jump_commands_1112.py` executes actual original ROM
SetAction and AdvanceActor instructions, using the retained original RAM seed.
The ROM is SHA-pinned by the existing donor oracle. Bounded execution passed:
standing action3 has Y128 except pose25/Y122, then returns128 at pose26.
Running action4 reaches114. Action14 animation commands alone leave Y128.
This exactly explains the observed standing-hop source writes; do not increase
its height as a supposed porting fix. Action14 also needs its terrain/climb
context assessed separately. This check does not execute terrain or projection.

Initial checker attempts omitted the actor-slot register at AdvanceActor entry;
those failed the execution bound and were harness failures, not game failures.
The corrected call explicitly supplies X0, matching the original slot0 ABI.
No output files were generated. Next investigate reachable block interaction
with intended climb/reach controls rather than retuning authentic action3.

## Correct approach reaches the block row

The controller now supports bounded runout position, an explicit turn followed
by idle before a fresh Up press, and a configurable hold. Up+Right directly
from the left-facing idle merely turns and runs; it is not the climb recipe.
Turning first at the old position gives X342, too far beneath the row, and
action14 still fails to climb (receipt e0f339bc8e6b533d65cf40b4fa8e494c2bea07fe8d8a6f957a07a8952f7daebd).

With `--runout-x 360 --face-right --jump-mask 8 --hold-updates 80`, the real
controller settles X303. Up admits action8, then action10 at age52, with actual
surface144. Projection becomes negative during the climb; native Y reaches113
at age94. HP5/two lives remain intact. This confirms the projection handles
large upward movement in the actual native scene. No item spawns during this
100-update observation, and the final pose146 is still climbing; that is not
a completed pickup or completed climb assertion.

Receipt `1049972968656323fa66a6bc38743f20ebd23b36e6d9236185a564a1a18869cc`;
script `11dee6f0f93d97d25625079df3a07d6d967322dcd6f4ee69d58a0c4a61ca266f`.
Continue this controller to settled top support, then inspect the existing
block activation paths without adding a non-original jump-height change.

## Settled top support confirmed

Extending that same controller with `--observe-updates 180` completes the
climb: age112 returns action0/pose15; terminal X307/Y112, ground0, mode0,
HP5/two lives at physical frame2014. Native support is the row at Y144.
No item appears and sword remains0. Receipt
`1a2eb712409343f829f1fd26f85d573f549f5e65932300b951a93679070684b1`, script
`acddc1bd565d21d937fdf82867fc691da22f462a32ec8ef72f51e5a5bce53b48`.

Source inspection: ordinary native head activation requires negative
Player_Y_Speed, head-cell collision and low-nibble>=4 in PlayerBGCollision.
Climbing beside the row is not itself evidence of a head collision. The next
test must exercise an actual activation path rather than treating successful
ledge traversal as a failed head-bump. No gameplay edits or captures.

## B at the climbed edge

The same controller with `--top-b` presses B during updates120..139 after
the settled climb. It does not release an item: Prince drops from the edge,
returns to ground Y176/X314, HP5/two lives, sword0. This is not evidence for
an unarmed block attack. Receipt
`21dbe685850e50ec73064b68b09afb59d6725f5306b0536f860e70cd1a9d1a6f`, script
`cfcfb27de527dffea57e52888407917b51ef173a9e7894303bdd6571805aeb01`.
The prior neutral supported position X307 is at the left edge, not centered
over the powerup block. Future action tests must first move onto the row.

Existing pickup source maps mushroom to a capped five-HP heal and flower to
sword1/action91. Historical strike qualification explicitly seeds sword2;
neither it nor the staged pickup tests establish natural acquisition or a
usable unarmed activation path. Keep that gap explicit.

## Walking off the settled climb exposes support gap

`--top-walk --observe-updates 280` holds Right during ages120..147, then B
during220..239. Prince falls before the B window: source action1 at phase228
aligns rawY65→63→65, then action7 falls at phase229. Terminal X335/Y176,
HP5/two lives, no item. Receipt
`224631d8d80532b7fa86f30e92866d0bfad68263515fb57a947b6df72270de49`, script
`fa4e69881a25d1e788b437545de6f9b6c9225018280b8a9cfc01b0879a66bdcb`.

Relevant actual source: `prince_exposed_brick_idle_1111.s` admits ordinary
brick51/57 only when action0; coin-brick58 is also admitted while moving.
Its logical-sole fallback remains careful-step-only. This is a concrete next
investigation: trace the failing support call and its exact native tile and
sole geometry before broadening admission. Do not claim a fixed bug or infer
the tile solely from appearance. No ROM edits made.

## Exact rejection and private candidate

Current-ROM Mesen trace confirms at age125/action1/mode255 that D720 returns
tile51, queryX320/queryY144, nativeY112/ground0, both source soles145. D739
rejects solely because action is nonzero. Same tile/geometry passed at age121
with action0. Receipt b7041664c30722134dc51df2881c750479cfaae5bcdd4a68915ec8dbdc933429.

`--test-moving-support` rebuilds the authenticated Prince packet in a private
candidate, replacing only D736..D73A's `LDA action / BNE Empty` with five NOPs.
Earlier action0/1/42-mode admission, grounded/sole checks, actual native solid
tile classification and empty-above checks remain. This also affects ordinary
brick57 and questionC0, which require regression coverage before delivery.

Actual Mesen replay now remains atop the row and ends X383/Y112, action0,
HP5/two lives, versus original X335/Y176. Receipt
e378a07972cc2b41a3204f03b4611a6e0998c6d1f98a3cf40f2cf32710034719.
The pickup assertion still fails because no item was released. This is a
successful movement observation, not a passing pickup or delivery gate.
Candidate and Lua are the two bounded files in build/prince-first-pickup-1112.
Next: negative support/interrupt/full-stage regressions and natural pickup;
do not install this private candidate yet.

## Full-route regression blocks delivery

Candidate SHA `6d0346164b7099f8e75cdbe22a9e9f1fd5f4f673116fd1dcb48a3cee620734c2`
fails the existing controller at X1888/Y176, HP0, late-finish-climb,
physical frame9412. Receipt c057a8dd9d7ae71aa5343234cfa097d734d8435d6bcff846de8e924efd9197a4.
The same controller on installed464c8 passes into1-2 with both lives,
physical frame16598; receipt e94382dd32df70ec9325ec0548688664bcb8faecc0150b1f1a529c9305e52058.
Thus candidate is NOT qualified for delivery. Investigate the first route
divergence near the later brick/Goomba section before deciding whether this
is altered controller timing or incorrect newly admitted support.

The replay formatter previously raised on Lua's empty jumps table (decoded
as `{}`); fixed that reporting path so the actual failure is visible.
Storage guard initially blocked reservation; one retry incorrectly budgeted
one file despite the retained candidate and was terminated by the guard.
Removed the byte-identical delivered Steve candidate from its old build folder
after hash comparison with Downloads. Its source and installed ROM remain.
Current Prince folder has only candidate plus regenerated controller; no captures.

## Candidate full-stage pass with corrected controller retreat

The failed old controller starts retreat atX1913 while still atY113 because
walking support now works. It turns right again atX1902, beyond the isolated
brick1888, and Up cannot grab it. The optional `--adaptive-retreat` continues
original careful left steps until at least9px left of the previously observed
climb-cap X. This is controller-only and uses actual prior geometry, no actor
or HP writes. It stops left at1863 and turns to1872, then climbs successfully.

Unchanged candidate6d0346 passes full1-1 into active1-2 with both lives at
frame16355. Receipt a3c15de76676ba9ebdf3ffdbc84049ef953b70d14015285e31e05251c0fd773c,
script a115265b9c2a3cc12fbf792a3460e01c5ce67264e2829dc901dfe5ee37ce33d0.
The old-controller negative remains valid evidence of a controller assumption,
not proof that the candidate cannot clear the stage. CPU boundary/interrupt
checks and Downloads delivery remain pending. Natural pickups still unresolved.

## Powerup reveal progression audit on delivered6d0346

`check_prince_powerup_progression_1112.py` cold-loads current Prince and invokes
the genuine native PwrUpJmp for slot5/type0 with controlled PlayerStatus0/1/2.
Actual revealed types are0/1/1 respectively. Test passed with zero files.
This proves the native reveal selector's dependency on PlayerStatus, not a
natural pickup or default-status claim. Existing Prince pickup source heals
mushrooms without a PlayerStatus store. Next exercise its actual linked mature
pickup and re-reveal to determine whether a progression bridge is missing.
No gameplay edit in this diagnostic.

## Mature pickup confirms the progression gap

Expanded CPU test invokes genuine HuFullBox and PowerUpObjHandler for an
explicitly staged mature mushroom overlapping Prince (HP4/status0). It heals
HP4→5 and erases the item, but PlayerStatus remains0. A subsequent genuine
PwrUpJmp reveals type0 again. This confirms a missing progression update in
the current linked path; it does not prove natural head/block activation.
Initial test fixture omitted ScreenRight_X_Pos255 and therefore clipped the
item's bounding box toFFFFFFFF. Correcting the viewport made the real native
collision/collector execute; no pickup result was injected.

Next implement a bounded progression bridge after accepted mushroom collection,
preserving the capped health heal and requiring a separately collected flower
for the original sword effect. Locate the actual current cold-loaded collector;
historical C7B5 and staging-C65F assumptions are stale for this packet.
