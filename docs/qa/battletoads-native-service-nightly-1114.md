# Battletoads native-service optimization

Private candidate: `ae669c7ec7536f1c912b3000597be7b3416c20f312638b2589f52fab55f0bc01`.
Parent verified nightly: `5715bb7e3c772350a2a7420ec9061eabd948964a8789e5d348c49d3cfb3c57ee`.
This note records version-scoped evidence, not whole-roster completion.

The candidate changes160 bytes inside347 funded bytes: public router224,
head/side prefix25, shared side service94, and four prefix operands. Complete
BT8192-byte code/data, cookie, full BtCheck, score correction, graphics,
physics, level data, helpers and every other byte remain exact. The intended
fault-contract change is explicit: raw33 native terrain queries use the real
native query even with invalid private cache; private services still reject.

The old source-only lease is unchanged. Root's private candidate lease is
`allocations/battletoads-native-service-candidate-1114.json`, SHA256
197cfe60a47f505ad818eb01a84d51cf3d4ed46f19c679cc62840d15553adae5.
Initial candidate runner55363 stopped before any output write or Mesen launch
because a hand-copied old-router preimage contained two extra JMP entries.
The corrected receipt stores exactly36 repeated entries plus its suffix,
validates the frozen preimage hash/length, and roundtrips the exact parent.
The candidate bytes never changed; the malformed c011 draft is superseded.

Root's independent source profile28386 reproduces the frozen model exactly:
48idle mean36604.0625 to27528.0625 cycles,32Right36864.5625 to27788.5625,
9076 saved in every Main, complete game/physicalRAM/OAM/VRAM/maps/SMC parity.
Opcode ABI, damaged cache, interrupts, both full source routes, declared
executable ingress and lifecycle parity are in the frozen model/ingress QA.
The explicit DeathStart component staysengine11/lives2 for360 Main in both
inputs; that is not natural death/respawn evidence.

## Native baseline

Root97226, actual Downloads571, terminal PASS. Lua
f06aa6a24d9d6e135931b56bb350acbbdb66952e29e82fd209ee93ececc04236;
receipt be7def6b7e6dde1922a06761c542ffac7764b1e0b23026002808248119933441.

| Phase | Completed Main | Physical frames | NmiSkipped delta |
| --- | ---: | ---: | ---: |
| Neutral idle | 48 | 72 | 48 |
| Right | 32 | 48 | 32 |

Both phases have zero active actors, HP47/lives2/power0/Star0/Y176. Idle stays
X40/camera0; Right endsX81. The inherited controller label says optimized
because it is shared with the upcoming candidate observation; this result's
actual authenticated ROM is571. No new candidate cadence, stage or installed
improvement is claimed by this baseline.

The only active output is the existing two-file flag slot. No captures,
videos, logs, states, patches, backup ROMs or releases are created. Other
project Mesen sessions remain untouched. Candidate native gates and any
Downloads delivery must be recorded below before claiming installation.

## Native candidate

Root5301 terminal PASS on privateae66. Lua
479809a4e16588a7ae78c89b1ef004437fcf8130d4183463118469297e5b00e7;
receipt0e7f05b9257771ae95459d624c87b509fa020760ce3bfb0a5e3cdd7c62734988.
Idle48Main/48physical/NmiSkipped24; Right32/32/16. Same zero actors, HP47,
lives2/X81/Y176. This is an **average** of one update per physical frame,
not yet proof of zero missed controller-read frames: the engine can perform
one immediate catch-up. A targeted read/per-frame histogram observer follows.

Root14089 terminal full Rash PASS onae66. Lua
b178e16d40681ffa08e4fc24f7fcd3c6df247a4aa490544e0efd400b368c8a80;
receipt a57a3339a6c5e42e777f9b1b0368e3a6c27ba35d5fce71417afca1ec13d63652.
4,359Main entries=returns/5,152physical,2,799actualBTsteps/58in1-2,
HP35/lives2, flag3012/frame3761,castle3075/3827,entrance3762/4529,then25
living grounded1-2 at40/176/high1/native0/engine8/area2/power0/Star0.
The input body is identical to the previously qualified route. Parent571's
preserved full receipt used6,464physical for the same4,359Main and HP35.
Zitz and actual Downloads delivery remain pending at this checkpoint.

The finer native observer13017 confirms remaining lag. Lua
404f3208118e9061fe242b20954ea0c61b5b16473f32f65eafc139d79f612854;
receipt46bb457dc547b0660cb80a68d2895c993c9570a6c23b4544389cbf363f1bfb0a.
After excluding the initial partial frame, idle47physical frames have23
missed4016/4017-read frames and Main histogram0:24/2:23. Walking32frames
have16 missed-read frames and histogram0:16/2:16. These are real read
callbacks, not just the native NmiSkipped counter. The faster average is
therefore a catch-up pattern; this candidate is a partial performance gain,
not smooth60Hz or zero-lag admission. The remaining idle/walk overrun stays
open for the next optimization. No game or input policy changed for this
observer.

Root19284 terminal full Zitz PASS onae66. Lua
a93c56ff35f877a2c14a8229b59a4fe89709ff81abadddd114f9efc4d996d15d;
receipt581e7f685679393638d9b5e54f1ace1815dee83d3b609e4128d820bbac2219e8.
4,380Main entries=returns/5,173physical,2,799BTsteps/58in1-2, HP35/lives2,
Selectcycle1/variant32. Flag3033/frame3782,castle3096/3848,entrance3783/4550,
then25 living grounded1-2 at40/176/high1/native0/engine8/area2/power0/Star0.
Parent's preserved route used6,485physical for the same4,380Main/HP35.
Both native stage routes and the literal-read observation now qualify a
partial performance delivery. The unresolved skipped-read frames are an
explicit limitation, not a blocked whole-goal or zero-lag completion claim.

## Downloads delivery

Root72436 TERMINAL PASS after source push85bd96b3. Replaced
`C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes` directly with
the exact testedae66 image,2,097,168bytes, no backup. CLI patch guards before
and after are clear, with no same-name IPS/BPS/UPS. Actual Downloads Mesen
launches for the read observer, Rash full1-1 and Zitz full1-1 reproduce all
three private Lua/receipt hashes, counters and endpoints exactly. No rollback
was needed. The literal idle/walking missed-read limitation remains identical
and open in the installed build.

Final shared storage preflight: build2,873,625,401bytes/19,996files, below
5GB/20,000. Latest capture preflight workspace~6.428GB, below70GB. All new
source output roots remain absent; only the existing two-file flag slot was
reused (ae66 candidate/a93cZitz Lua). No screenshots, videos, logs, state
dumps, backups, patch assets or releases were produced. Other Mesen sessions
were left untouched. Existing helper placements are unchanged.
