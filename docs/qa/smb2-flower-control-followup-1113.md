# Separate ordinary Flower-retreat control correction — November13

This followup owns only `replay_smb2_flower_control_followup_1113.py` and this QA.
It changes ordinary controller decisions, with no ROM, physics, actor, health,
timer, item, maturity or ability grants. The frozen52f Flower source,045 native
adapter, original b6 Mario control, all old scope hashes and their native
negative remain unchanged.

Root twice reproduced exact original Mario Lua
`b6b10f5db8387b6673efb78749b4dc093ae79b02f82f2129750f70c4c09579ce`
and receipt
`db83087aa20a8b9a0d6de8abf00f9ca5252f827a1a5900956100ce2c4107e5cd`
on actual Downloads12397. The2600-Main bound is an ordinary-control negative:
initial head alignment succeeds at328/VX0 (Main305), real C1 head occurs311 at
328/150 and Flower birth312 at336/136. It then stays in `flower-left`, with no
launch or pickup, while healthy31/both lives. Existing recent samples show:

| Main | X | VX raw/signed | Held | Requested pad |
|---:|---:|---|---:|---:|
|2160|302|234/−22|2|2|
|2220|292|254/−2|1|1|
|2280|300|22/+22|1|1|
|2340|310|2/+2|2|2|

The pattern repeats at2400/2460/2520/2580. Full-direction reversal at the target
produces a limit cycle; there is no demonstrated game pickup or motor defect.

## Narrow new controller

`controller(exact12397,variant=0,scope='collect') -> Lua text` first obtains the
strict frozen045 adapter text. It changes only the `flower-left` call from
`settle(300)` to a new ordinary neutral/predictive settling helper. Initial
`settle(328)` and every other alignment, head/charge/jump/pickup/reserve/health/SFX
assertion and the2600 bound remain byte-exact. Removing the added helper and
reversing that one call must recover the frozen text exactly.

The new helper releases horizontal input before passing the estimated stopping
point, letting original neutral friction reduce velocity. Once stopped, it
approaches with ordinary directional input again. It reuses the existing
charged-pipe controller's conservative `v(v+1)/32+1` braking estimate. This is a
controller estimate, not an invented game constant or exact friction1 model.

Actual original neutral friction is tableFD03 (±3), bound at current file969624,
and its ADC instruction at968733. The original four-bit velocity integrator
shift at969176 confirms1/16-pixel velocity units. Exact Ready85 native member
SHA256 is `c929f894f8d6f4723e6371d140c85fef76de47eb9f53bff0af6b544325f80cb0`.
The initial planning note's friction1 explanation was corrected before claiming
native qualification; no original motor byte changes.

## Source qualification and exact Lua

Mario corrected collect Lua SHA256:
`a46346af383383c95e62764298bd613e35dc455d242618a00fe64818cbbd999b`.
Parent remains exact b6 above. The unchanged actual menu/Main/NMI source runner
passes503 logical iterations/502 returnedMain: C1 head/birth, charge60 launch
301/176 at409, mature kind1 actor336/119 collected at330/96 (442), real erasure,
SFX32/popup6, reserve0→3 and60 normal resumed updates. Health31/max0/large form and
both lives remain. No gameplay state or actor field is seeded.

The current-byte binding and Lua compile/hash checks pass. The all-eight source
collect batch completed successfully: each actual menu/Main/NMI route passes
the unchanged mature Flower, reserve, health, erasure, sound and resumed-play
assertions, with no gameplay seeds. Retained logical iteration/returned-Main
counts are Mario 503/502, Luigi 678/677, Papa 492/491 and Mama 538/537. The tool
truncated the intermediate receipts; the process completed with exit code zero
after asserting every variant passed. No missing per-variant count is inferred.

Root's actual Downloads session 36868 passed with the exact a463 controller:
849 physical frames / 508 returned Main, receipt
`c7e77df63edf96365b120a665f6f2a1382b9cea8b5e16e26025c39b4a04f9b3e`.
The mature Flower at336/119 was physically collected at331/96 on Main448,
granting reserve0→3 with native erasure, sound32/popup6 and60 resumed updates.
Health31 and both lives remained. No game changes, state grants, helpers or
generated outputs were used. This receipt covers Mario collect only. Root
subsequently passed the other seven actual Downloads collect routes in batch
97422; the complete native receipt table belongs to `smb2-flower-native-1113.md`.
All eight retain the mature kind1/state128 actor, reserve0→3, health31/max0,
native erasure/SFX32/popup6,60 resumed updates and both lives. Throw/hit
successors are qualified separately below; collect does not establish them.

The separate collect controller identities are:

| Variant | Identity | Lua SHA256 |
|---:|---|---|
|0|SMB2 Mario|`a46346af383383c95e62764298bd613e35dc455d242618a00fe64818cbbd999b`|
|1|SMB2 Luigi|`fbb669ea1484a84b663d6cf513002e671a8eb6283228c2de4788f226038e13a3`|
|2|Toad|`61dbb343b8856ba62b0a14625d5c770d81bd7c8d0d013dca5db6887e72dca335`|
|3|Peach|`18c4f60706743b329590202d540ee98d94d5f8529edd571b896b088dc4e73a6f`|
|4|Imajin|`a2319877de6a8ffa168c7739c38417f03bb8c6c506e00f14f7a23bd0415ea629`|
|5|Lina|`f36c768cd15b78ebaba06d9c1da1da711a2dd4902fe6b170d878f2cd5ee0edfa`|
|6|Papa|`be7f68a1d5a3c12bf4bfede72b5392dab5ed445d645a24fe8ff4be643731063d`|
|7|Mama|`346bcaffb4e221e80220fd7a1b918aa5e6606771584b19f1a898d04bec235c52`|

A redundant all-eight metadata invocation under the shorter 180-second limit
completed variants 0–6 before the wrapper stopped it for runtime. It produced
no files. This is a metadata scheduling limit, separate from the successful
600-second all-eight CPU batch. The individual final metadata case then passed,
closing all eight compile, hash, reverse-text and motor-binding checks.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/karnov-equipment-1113 --resume --max-files 1 --timeout 180 -- python -B tools/audit/replay_smb2_flower_control_followup_1113.py --cpu --variant 0 --scope collect --limit 1500
```

Use `--variant all` under the existing600-second bounded allowance for the
source batch, or omit `--cpu` for pure metadata. Root can obtain this separate
text through `controller` and use its existing `native_case`; the default native
runner still selects the unchanged frozen controls. The root runner's optional
`--followup --variants 1,2,3,4,5,6,7 --scope collect` selects this correction for
the seven variants not covered by Mario's native pass. See the runner QA for
the guarded root-only invocation and metadata isolation checks.
No helper Mesen is launched.
No outputs, capture files, ROM copies, patches or releases are created.

## Corrected throw successors: separate source qualification

The shifted prefix was rerun from the actual menu for every throw successor on
exact12397. All eight pass independently of the old frozen52f/045 positives.
The factory remains exact SHA256
`f78b68e72ea531df1e0adae1f6e749e31c7fbe2db6d77fbe7434d2a872654153`.
Each case has a1500 logical Main/NMI iteration cap, retaining the unchanged Lua
2600-update route bound and180-update flight/contact bound. Counts below are
source model iterations and returned Main, not physical frames.

| Variant | Identity | Logical / returned Main | Corrected throw Lua SHA256 |
|---:|---|---|---|
|0|SMB2 Mario|566 /565|`7ffacac34ae161daaf08f45da5691ef8df55f1fa0d35d973d544279f2ac22f52`|
|1|SMB2 Luigi|741 /740|`62338c4a51c3451ddc670498172c58a3ce395831455d9f3b64367a2dbf3b770d`|
|2|Toad|555 /554|`abcf0d1660627c0cabea70aaca8de337b8324a46cc51bb919c58fd0755e33cab`|
|3|Peach|615 /614|`dd19eddc6fbeeac8f7e3e77f5d29556cc855e63a260f42ad1bdc4b2f4b36f9a0`|
|4|Imajin|566 /565|`c875a1333884e3761f38f8c9ac354665a788f9e2daa4d29866a63e70756d2ef8`|
|5|Lina|615 /614|`ade10b29e6ef634fa9148085125ddc21394d275d6c012702a4b0b2846f118f3d`|
|6|Papa|555 /554|`4f0785a2f0396abc1c3c47bb845e3b9d9770c72e0e3f7c96c9d0559960ec3a72`|
|7|Mama|601 /600|`42a7ccb958e7644910e6cef7298f975d805fab2f7713bd2128247d64bb152c01`|

Each CPU route reaches the actual mature authored Flower collector,
observes native erasure/SFX32/popup6 and reserve0→3, then reaches the original
supported fresh-B `S2BeginLift`. A successful pull spends exactly one reserve;
the held record is type50/$32, host255, with a live state. The next fresh-B
launch produces a live source projectile, keeps reserve2 and resumes30 normal
updates. Every endpoint is supported atY112, health31/max0/large form/lives2.
No actor, item, maturity, health, ability or timer state is seeded. These are
source qualifications; no helper native throw-only run is claimed.

Reproduce with `--cpu --variant all --scope throw --limit 1500` through the same
600-second, max-files1 bounded root. The hit successors are run separately;
throw success does not establish a native enemy hit.

## Corrected hit successors: source positives and native aiming negative

The eight hit successors also completed fresh actual-menu/Main/NMI source
routes on exact12397, with the same1500/2600/180 limits. All retain the full
Flower, reserve, pull, carry, throw, native defeat and resumed-play assertions.

| Variant | Identity | Logical / returned Main | Corrected hit Lua SHA256 |
|---:|---|---|---|
|0|SMB2 Mario|815 /814|`204e959e535f99427846fe54d729cff1b483d9e957efe510c7355b6d7a5c4c87`|
|1|SMB2 Luigi|1074 /1073|`9e2900dee8c4bc20909c5fbc8e69fe04024793dabc82c58b8d1d68a63ad1dfa5`|
|2|Toad|802 /801|`5d4f884f2aa703abf082ac2a0d03c23c4f06bf0264434e4db972a1f1179b94ef`|
|3|Peach|942 /941|`eefdfd14808e90cce995d11ed53e80202aacf6cd4aa72b24e111ef0a54f99b16`|
|4|Imajin|815 /814|`a1af6da4b097ad69187099c78e940c072ea42edb0b8df9e7897b6ce7d151cc97`|
|5|Lina|942 /941|`a8b00523fe518ee038f169f33b1d01ca5809d12b0dbe8ef189af0961e760bd17`|
|6|Papa|802 /801|`8e3b54379ad53bd4f8843aaeb045a36c4653360bf09119cf73cb6f1fb66d9246`|
|7|Mama|926 /925|`69666abd61335690a937173a5dd05cd526ebed0deca53ebddd22f6cd46556183`|

Every case reaches the real source projectile contact and native
`ShellOrBlockDefeat`: a live Goomba changes state0→34. Endpoints remain atY176,
health31/max0/large form, reserve2 and both lives, after30 normal updates from
throw. All fixtures are ordinary-controller routes with zero gameplay seeds,
outputs or Mesen runs. Reproduce using `--cpu --variant all --scope hit --limit
1500` through the same600-second bounded root.

These source results do not close physical hit qualification. Root's actual
Downloads Mario test1277 with exact204e Lua is negative, receipt
`5d9d4a6102795297b28c30fd7dc3cdf7cc0dca5203e4fed5089796c4bd5370fe`:
1184 physical/795 returned Main, player703/176, health15/lives2, stopped by the
unchanged healthy-form assertion. Flower collection448, pull509 and carry540
pass with reserve2. Travel enters aim778 at693/176/VX24; countersteering reaches
703/VX0 at791, then the face/throw phases precede contact damage795 without a
throw observer. The native target actor's exact X was not retained and is not
inferred. This is an ordinary aiming/timing failure; no game attack defect is
established. The eight collect positives and frozen source/default controls
remain valid. A separate enemy-aware hit-control factory is investigated in
`smb2-flower-hit-followup-1113.md`; this factory and its exact hashes stay frozen.
