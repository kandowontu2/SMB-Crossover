# Contra Force full-route controls — November 14

Four separate normal-control full1-1 controllers are prepared for exact current
`421379021e775e6e03357c0aa11d4cab04008452f94bc9e8938f0662cc0c979f`.
Strict metadata, Lua compilation and local controller components pass for each
choice. Current full controls are **grounded-v3 for Burns/Smith/Beans and the
explicit Iron far-landing successor** below. The older v1/v2 controllers and
their negatives remain frozen. Current source passes and native limits are
recorded separately below; a sibling's result does not close another choice.
Preparation is not a stage-clear receipt.

The retained f476 report at
`checkpoints/2026-10-31/ready74-cf-projectile-native-v1/manifest.json` binds
`f4767d595a25bf64355b1e2cea86be7a93046f1cf139a4d9b0544e35f9ed4182` and
four individual earned pistol defeats, native score/SFX, camera and hardware
art checks. It explicitly excludes a full-level/powerup claim. Those earlier
positives are retained; they are not transferred into new full-stage results.

## Exact interface and separate identities

The initial frozen v1 `tools/audit/replay_contra_force_full11_1114.py` exposes
`controller(raw421, key) -> Lua text` and `metadata(raw421, key) -> dict`.
It rejects unknown/dirty ROMs and preserves the frozen SMB1 route factory.
All existing factories/defaults and root's CLI remain unchanged.

The actual compiled menu has eight columns. From the initial Mario portrait,
the new controller presses Down three times and Right six times to actual
slot30/raw31, then the stated number of Select cycles. Source UI execution
verifies each name and class separately:

| Key/name | Select cycles/source class | Frozen Lua SHA256 |
| --- | --- | --- |
| `burns` / BURNS | 0 / 0 | `ef9188cdc9d95d6a9c11105ef60b08b09a14701bd21779571a272b9f44b9cce3` |
| `smith` / SMITH | 1 / 1 | `b47968a12a866ed1b37ae603f5780ebf41be66c6cdff0ab99ba9d649646cd87b` |
| `iron` / IRON | 2 / 2 | `a5134c9ff9ffbd6fadcfeb91ea3135c9ba9c759678a79832a7ccd05076161cf9` |
| `beans` / BEANS | 3 / 3 | `f22368807ec51f52fa3b3e3ec85f49548be7b4a19fff136fb7242bfda5ec6347` |

The route uses live native terrain/enemies, original crouch-fire and fresh
released/held A jumps. Iron retains its authentic immediate Down+B startup;
the others settle Down for four updates before fresh two-of-eight B pulses.
The policy makes a new decision only after a completed Main update, retaining
the same buttons through physical lag frames. No health, position, actor,
terrain, ability, gear or cheat state is seeded. It does not require natural
items, and no item acquisition is qualified by preparation.

Success requires the actual native flagpole routine, castle sequence, ordinary
entrance and25 consecutive living grounded active1-2 updates. It additionally
requires both complete C2/C3 cookies, the actual source class constructor and
the current CF movement worker, including at least25 movement calls in1-2.
Unexpected scene/shortcut, life loss, native death, prolonged combat/stall,
wrong cookie/class or changed hook bytes fail the controller. Work RAM reads
use the typed physical C2/C3 API or verified mapped worker seams, not a foreign
restored CPU-C window.

## Current/source bindings and local gates

All24,576 current carrier bytes at CHR935..958 equal the retained f476 kernel's
three complete8KB images, including its source-declared cookie tails. Combined
carrier SHA256:
`3a7d2d9a77d5accd30e7976645856118f8734fca5a84f7df7bff8946ec989f84`.
The current menu/preview, external CF guard, native scroll and collision banks
also equal the strict12397 normalized input. Complete exact421 input binding
retains all110 hidden-response and66 cheat changes.

The source checker runs each selector and verifies ordinary travel, a live
hole-triggered fresh jump decision, class-specific crouch fire and rejection
of an unauthorized underground shortcut. These are policy component fixtures,
not simulated successful physics. Each metadata arm rejects truncated input,
a dirty native-physics byte, fa66 and12397 mislabeled as421, with file-write,
Mesen and mutable-nightly reread traps.

Source bindings:

- Factory: `1505edae84d0264be23a8ba48fbce7c8ee992931eb73dee5e515b68847e64c13`.
- Checker: `6b3b3c192ddf1349e92aec6c53e49b384acc653dad024acc254e1623498bd35e`.
- New policy: `8c4435d5732048997794641ff3d2a235ce5f7de8227f76923bb86aa80622b121`.
- Frozen SMB1 factory: `e25b9510f2fbdc5ece466033ad02d8ba25abc19cf8359bb15e3bcfe669b3af61`.
- Retained f476 runtime labels: `8944961064964d2bac2d7b2ebca31fbb4ac4c2d9b555af032f7477ee16414ab2`.
- Historical CF navigation reference: `973e3c3704a0917ef899f639c168c550e8e0f274de38796c559a862f2f13a74f`.

Reproduction (replace the identity for each separate route):

```text
python -B tools/audit/run_bounded_build_v1.py --output build/contra-force-full11-source-1114 --max-files 1 --timeout 600 -- python -B tools/audit/check_contra_force_full11_1114.py --identity burns --metadata
python -B tools/audit/run_bounded_build_v1.py --output build/contra-force-full11-source-1114 --max-files 1 --timeout 600 -- python -B tools/audit/check_contra_force_full11_1114.py --identity burns
```

## Full route status

The original v1 Burns source run failed its observer at Main2/X42/Y176/lives2,
after a genuine source movement/export: receipt
`cb919f8c0963afc6feae9982f68c50690e58c9d3810ec188fa1755055694c908`.
It incorrectly expected the complete fingerprint in both C2 and C3. The actual
loader source `CfLoadVerified` publishes only C2's cookie and deliberately
leaves C3's32-byte reserved tail zero. This is an observer assumption error,
not a game/traversal failure. Commit`f5489dfd` and every v1 pin above remain
frozen, unqualified and independently reproducible.

The separate `replay_contra_force_full11_v2_1114.py` authenticates its frozen v1
parent and replaces exactly one observer statement. It requires the complete
16-byte C2 cookie and all32 source-declared zero C3-tail bytes; all existing
C3 worker/export/impact signatures remain enforced. The expected outer cookie
also equals current `CfLoaderExpectedCookie` byte-for-byte. Selector, navigation,
combat, jumps, success conditions and every other observer are identical.

Corrected API: `replay_contra_force_full11_v2_1114.controller(raw421,key)`.
Factory SHA256 `8330845efee9e4a7eb800e457f3c3c55a28590159d274b6d7d49b699500a08c4`;
checker `check_contra_force_full11_v2_1114.py` SHA256
`7814058dc0d1ec48646c2591b9a752c3c2bfe9e56afdce4553b37517e6bb9d63`.

| Key | Corrected frozen v2 Lua SHA256 |
| --- | --- |
| `burns` | `93028d0999787c6eebf6ca46b19898a6b2452d45e8c8957af4ec3d52b0c7b1e0` |
| `smith` | `e108ceacb8ddca9d86c52abda547576348b60109853497c178265a290d042c1c` |
| `iron` | `9d8e2d714bf5deec13f36b24530ac40305c773fea345167c90019b03486a5edc` |
| `beans` | `74f91e095f47813de185f003a6e12e40e3cfa9b51df533b63c248ccada073270` |

All four v2 metadata/component arms returned0/PASS. The same unmodified Burns
full controller also passed a genuine ordinary first-pipe/camera source prefix:
Main399 at X508/Y176, camera396, grounded, life2, power0 and source class0, with
the complete C2 cookie/zero C3 tail verified. No state is seeded. `--prefix`
on the v2 checker repeats this bounded read-only checkpoint; it does not claim
the unexecuted remainder of1-1. Full Burns source then advanced to Main500 at
X631/Y98 on the next pipe, alive and unpowered.

Burns full v2 source returned0/PASS:4128 Main/scheduler passes, receipt
`7eaf28881608bb9ec1d314db4016485ab5318896d3419da000d105a92f63ac5b`.
Flag was Main2745 at X3161/Y115, castle2808, next-area entrance3511; the endpoint
was X40/Y176, active underground1-2 and25 consecutive living grounded updates.
Lives2, power0 and Star0 remained. It observed2821 actual CF movement calls,
including76 in1-2, plus13 source impact calls (not a separate13-kill claim).
The complete C2 cookie, zero C3 tail and source class0 assertions passed. Burns
crossed all ordinary obstacles with its intended source jump, without a helper.

The v2 source arms also passed individually for Smith (4045 Main, receipt
`948521d35b8c6f54ee53efb72f1ef99865b602b4ec111e380bddfa5fc94bfe06`)
and Iron (4908 Main, receipt
`6cac13b8caad9030eae8c0da0b7795ca7c6d4852754840f32ed060457ac51d0a`).
These remain source results on those exact earlier controls.

V2 Beans failed its controller at Main2090/X2177/Y128, life2/power0/Star0:
receipt `f6d82fc487653e044de391907ed02985ffbe5f772cbd93754a82ba422a4d3169`.
Its recorded phase entered `stair-1-land` while falling at Main1838/X2173/Y105,
native state2, then landed a step low and never requested another jump. The
waiting phase had mistaken an airborne Y coordinate for a successful landing.

**Actual native v2 negative, root24556:** Burns93028 on actual Downloads421
stopped at16000 physical frames,7936 Main entries/7935 returns, alive with
life2/power0/Star0 at X2177/Y128 (max2179). Its complete CF cookie passed;
7601 actual movement entries and11 source impact calls were observed. Those
are not11 independently verified kills. The source endpoint was contact1,
input3, jump age0, localX118/Y144, with no1-2 progress. Native receipt:
`3e2513593c03244744d25d52931ef6cdce3b3ce0d0c14f15ed9bb92df016ea7a`.
Smith/Iron/Beans v2 were **not launched** because the batch stopped on Burns.
This agrees with the same lower-stair controller stall; no geometry, intended
jump deficit or game defect is inferred.

## Completed source ground and current full controllers

Retained host source `tools/reference/contra_force_host_runtime_v8.s`, SHA256
`50b186659b04247ec14ed4aa1f3ba31464fafd9f813b2df8de04f5fe1da0c046`, defines
the real ground semantics. `CfHostExport` maps original C4AA air bit40 to native
state1 when rising or2 when falling, otherwise0. After accepted native floor
collision, `CfHostAfterBG` clears that air bit, zeroes C4B4 jump age/fraction and
writes C4D2 contact1. Its air path writes contact0. The current full carrier
remains byte-exact to the retained kernel containing that host.

The separate `replay_contra_force_grounded_full11_1114.controller(raw421,key)`
samples physical C2 only after a complete actual Main return, tagged with the
same Main and movement count. Ground requires native state0, contact1, age0
and a clear original air bit. The stair controller now requires that actual
ground before entering its landing wait. Decision and phase clocks advance on
the actual CF movement count completed by the matching full Main return;
repeated physical polls do not advance the policy. All cookie, worker, scene,
life and success guards remain. No game instructions change.

Grounded-v3 factory SHA256:
`0d55648f367bfec47f5b272eb4eeff3efcfe86787b112a92dae7a3422c7bcd14`.
Checker `check_contra_force_grounded_full11_1114.py`:
`127a45bea18a293e2c2c679431c5de12595494fe282daa278d3c8796b4563448`.

| Choice | Frozen grounded-v3 Lua | Full source result |
| --- | --- | --- |
| Burns | `3d3c358cc5f2b8b85f89fe48f88cf93133b4b27f0b892f9a67217d23fd7db3fa` | PASS3939 Main, receipt `0df210379382a8c4f0a9d6cac31166492ea473245b3ac255d5bb0a829b431445` |
| Smith | `fc182145cb64cc1ccc26d6b4fe3bed769d22131773e1c3590953548e0c7316e5` | PASS4066 Main, receipt `bcef8a858174955146c42dafc49d23c0b6c31f68f0e927490e21c49773f0c4ed` |
| Iron | `1d90fde89b3752da52cf3d7d8e809382e961453e4c357e6770e4e71a6cf36082` | Controller negative below; explicit successor required |
| Beans | `83b164a83934bded1575b330a15173ab92a0322e294eab4a15038250de03475d` | PASS3939 Main, receipt `d6921015e6c35138028367129cb6d7c5437ae1f7e48febd3ae9f90e6e9e8910c` |

Each of those three positive source arms individually completed flag/castle/
entrance and25 consecutive living grounded1-2 updates at X40/Y176. All retained
life2/power0/Star0. Burns observed2807 actual movements (76 in1-2), Smith2938
(77) and Beans2795 (76); each had13 source impact calls without a separate
13-kill claim. Their final completed-source snapshots were contact1/input0/
age0/native state0. No helper was needed in these source routes.

Iron-v3 genuinely landed on the **far** ledge at Main2617/X2229/Y112. The generic
landing phase then steered backward toward the near peak2192, walked into the
gap and stalled at2207/Y176. Receipt
`760e7716a1679e68d1f5cf4967526af1a044a4e9029dbec3be6d016f975b995c`,
Main2894, retains life2/power0/Star0. Its ground snapshot was valid; the route
misclassified which ledge had been reached. This is separate from v2's
airborne-to-landing error, and does not establish an ability deficit.

The explicit `replay_contra_force_iron_full11_1114.controller(raw421,'iron')`
successor retains grounded-v3 and adds only: after genuine ground at Y<=112,
X>=far-15 overlaps the far ledge with the original body box's right extent15,
so continue Right instead of backing toward the near peak. The measured
2229/Y112 counterexample is a passing policy component fixture. Factory
SHA256 `67e90e1ea8cf217e47b759fc4f8ddc8cf3fae92ad744daf69a0e14321b31b296`;
Lua `41b214df5fd7a8ffd5b8f5fba048b3cb10280ecf5fb6136fddfa7ca67f225b82`;
checker `6f3bfb7978c3c2191ac2de0e3567e5e38ac068785493b975d409e8b453d0b15d`.
Its strict metadata/components pass and full source is active. Other three
grounded-v3 controllers stay unchanged. The earlier Beans-only grounded
predicate experiment (`replay_contra_force_beans_full11_1114`, Lua`ef3bff39831d008c967b0da0dd946e869798df743b1c4849be4e281a96b29b21`)
is retained as a source-only intermediate, not the current native route.

## Separate bare idle/walk clock

`replay_contra_force_clock_1114.controller(raw421,key='burns')` is independent
of stage navigation. It uses genuine compiled UI and complete CF cookie guards,
then requests idle120/Right32/Left32 **physical** frames. Each phase waits for a
full Main and original CF movement return before closing, and reports its
actual physical duration. It records physical frames, input polls, full Main
entries/returns and original movement entries/returns separately. At each
movement entry it captures the real stack return PC/SP and current return
mapping; only an execution at that exact PC/SP/mapping acknowledges completion.

Measurement never presses B/A and requires all six native actor flags and all
twelve source shot-slot flags naturally zero throughout. It erases or seeds
nothing. Factory SHA256:
`9637e055765d51948aded6f0bad44882138949393e977679baae587552911c63`;
checker `aef5023f63943cce2a7c6f8d93860129b44c4fe2776e23aad6a6b46818e6f670`.

| Choice | Frozen bare-clock Lua SHA256 | Scope so far |
| --- | --- | --- |
| Burns | `3cd35204a49659efb1a6343e57e782a5427d358b55127718ee8cd78f396e728a` | Strict metadata and source controller PASS |
| Smith | `e392d01822b80722683c3645534d9d27699eac41c21ff83383e37e1c5eb2a793` | Strict metadata only |
| Iron | `64a00b964c81830759eeb79988d5913c19864742a6e0173724fd19743bbcaad0` | Strict metadata only |
| Beans | `bd8ef108637197e4caf8a230015c8b16101c16882c7a1158f16a680523ddc20f` | Strict metadata only |

Burns source receipt
`88b5b3dafc83febb2744db488b63db778e39f4ef2b1a503a31732a9661380cd1`
passed with186 model frames/polls/full Main returns,185/185 original worker
entries/returns including one warm return. Its actual caller was C2:CA2B,
physical Work RAM offset18987, return SP212. The measured phase deltas were
120/32/32 model frames and120/32/32 full Main and worker returns. X went
40→40→79→40 at Y176; life2/power0/Star0 remained. All186 actor/shot and complete
cookie checks passed. These CPU-model counts establish no native60Hz or
optimization claim; root owns the physical measurement.

Source
execution uses the compiled cold-menu/Select/Start/parser/constructor arena and
normal controller/Main/NMI scheduling; it does not establish physical video/APU
timing or cold-title authority. Root owns those actual native checks.

The output root is `build/contra-force-full11-source-1114`, with zero generated
files and no ROM output, capture, Mesen, installation, helper placement or
historical archive restoration. Only the new factory/checker/policy and this
QA note are owned. Any genuine traversal gap must first be measured and sent
to root for existing-native-actor helper review.
