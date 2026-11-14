# Separate bounded Flower throw acknowledgement — November 13

New source: `replay_smb2_flower_ack_followup_1113.py`. This preserves all frozen
52f/045/f78/f6a factories and their exact source/native positives and negatives.
Only ordinary controller decisions and read-only evidence change. No ROM,
actor, item, health, maturity, ability or timer field is granted or written.

Root's actual Downloads12397 Mario throw passes with frozen Lua
`7ffacac34ae161daaf08f45da5691ef8df55f1fa0d35d973d544279f2ac22f52`,
receipt `c3a8a37f2837e91cb7bca7a09d6bb24a69e3a70b798eeb81afb7ace09202b168`:
912 physical/571 Main, pull509/carry540/throw541, vegetable at349/107 VX48/VY26,
reserve2 and30 resumed updates. This establishes Mario's original earned throw.

The batch stops on Luigi's frozen62338c4a controller, receipt
`0d96d023493b5cba482790c56bb95a7dba4f7c9256dc826f3313d93e136e6df2`:
2963 physical/2600 Main,332/112, health31/lives2. Pull654/carry685 succeed with
reserve2. It enters throw685, requests B for one update, then remains holding1
without a throw; later sampled Held/Fresh remain0. A lost controller/source
sampling pulse is the hypothesis, not a proved game throw defect.

The new throw derivative changes only that input phase: while still holding,
request B until the source Held bit acknowledges it, release on acknowledgement,
and require progress within12 controller updates. If an acknowledged throw is
refused, a release/repress may occur within that same finite budget; a missing
real projectile still fails the original assertions. A current-ROM-bound,
read-only callback at the original `S2N8E05` BIT Fresh records actual fresh B
while an object is held. The original collector, reserve, throw, health and
resumed-play assertions remain mandatory.

For hit scope, the base is the separate frozenf6a neutral-aim controller. Its
demonstrated odd-family gap65 miss is addressed by waiting until gap<=40 before
the low arc. This reuses the older odd-family controller's maximum shot range;
it changes no projectile or enemy physics. Source fresh-B acknowledgement and
actual native projectile/defeat evidence are still required.

Priority source checks pass Luigi throw, Mario hit and Luigi hit on exact12397,
under1500 logical Main/NMI iterations with original2600/180 route/flight bounds.
Factory SHA256 is frozen at
`8846c50a316355f4198471b2cf3d3e62db4b7086c251d88761864d1520f0abc4`.

| Variant/scope | Logical / returned Main | Lua SHA256 |
|---|---|---|
|Luigi1 throw|741 /740|`38246a00fa6eda0749bb05c791a6ad13b1a9c48f233dd105157a2190d27547d3`|
|Mario0 hit|808 /807|`2bb321529317c4ac0afe3a36e9a1d94cb8c25bce657e09ec0e0db346f6bc722c`|
|Luigi1 hit|1065 /1064|`ed1d738b3cf1d5cf5795904f82b9cae6ee55de66d3b350b168ba2e02d95c37ce`|

All three observe Fresh64/Held64/Holding1 at the real original BIT Fresh, then
a real throw with reserve2, health31/lives2 and30 resumed updates. Hit0 and hit1
also reach native Goomba state0→34. A null `throw_input_ack` is legitimate when
the action finishes immediately: the BIT hook's `throw_fresh` and actual
projectile prove consumption without a separate still-held acknowledgement.
Remaining source cases are run independently. Root90336 subsequently passed
all three exact texts on actual Downloads: Luigi throw1080 physical/717 Main,
Mario hit1210/817 and Luigi hit1445/1044, each with original BIT Fresh64 while
holding, real throw, reserve2, healthy31/both lives and30 resumed updates.
Both hit routes defeat an actual native Goomba0→34. The full native receipts
belong to root's `smb2-flower-native-1113.md`; these passes do not establish
the other six native hit routes. The helper creates no ROM/capture/receipt
files and leaves GitHub releases empty.

All eight Ack throw source routes now pass independently, each with an actual
fresh-B hook and retained original assertions. Every returned-Main count is
one below the logical iteration count shown; all cases finish below1500, with
2600/180 global/flight bounds and the additional12-update acknowledgement cap.

| Variant | Logical iterations | Ack throw Lua SHA256 |
|---:|---:|---|
|0|566|`7a9e5fd8f944dedbe6dbc2203b9fb5f22edf036fa04a63f53b0fba1661a854e4`|
|1|741|`38246a00fa6eda0749bb05c791a6ad13b1a9c48f233dd105157a2190d27547d3`|
|2|555|`0a4aeba4c2a19196e2623640d3f06603a66ba90038171b4910b2142a89f776fd`|
|3|615|`320e2601cc4d6aa2a243b08d863c77fa462bee272a31cf62a81c953bcdc45a59`|
|4|566|`27cdf4183a7359c04220198030648f7320a2c3e88350f5051b32a00639425cdf`|
|5|615|`9a02d304975cf14902ca1bb3792194ab50cbf0c81a271856ebe9bef7d043720b`|
|6|555|`66e78b5518eea19be8b033660bff9a0ab80d3d6ba0e4f9430771c9f1b243e09b`|
|7|601|`aa3fd5a1c8e1f8131d59485571405c04bf1bb4070bc0aac2fc62a1c855b7669a`|

All eight Ack hit source routes also pass, with the same1500/2600/180/12 limits
and returned-Main counts one lower. Every case records original Fresh64 while
holding, real projectile contact and native Goomba0→34, health31/lives2,
reserve2 and30 resumed updates. No older source positive is substituted.

| Variant | Logical iterations | Ack hit Lua SHA256 |
|---:|---:|---|
|0|808|`2bb321529317c4ac0afe3a36e9a1d94cb8c25bce657e09ec0e0db346f6bc722c`|
|1|1065|`ed1d738b3cf1d5cf5795904f82b9cae6ee55de66d3b350b168ba2e02d95c37ce`|
|2|795|`bb1f00408d14907100e235d602b412c43c3ac3486ee397c827970f7277324a35`|
|3|945|`863106674c24900f19c900a846029516b9f1f0e1a776019124efcdd5bb11c44f`|
|4|808|`3bfe5a902b9680ab162c560da4630d3e341b637fd3db54078ac8d915d4882fa2`|
|5|945|`bf770d7587319f7d29c127dc7e221b427dec5039e1f7233b984b0053a55a12e2`|
|6|795|`9bcc1c29770391765916aff4d7cfd0cd5de92a07020fc887ea8ea03706c7f644`|
|7|935|`137652d896d9bf43137d23f92a545c0dce132605be9d9d2e7d87a22bcaada039`|

The root-only runner now offers `--ack-followup` for throw/hit, independently
of the preserved default and `--followup` paths. A successful Ack native result
must additionally contain the actual original BIT Fresh64/Holding1 evidence.
Metadata compile/dispatch/isolation checks passed before the new selector was
handed to root: b6/a463 unchanged, priority3824/2bb3 exact, strict unknown-ROM
rejection and correct selector/conflict behavior. Path writers/mkdir, Popen
and native entry were blocked. The helper never launches its native branch.
