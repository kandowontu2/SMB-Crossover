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
generated outputs were used. This native pass covers Mario collect only;
other variants and throw/hit successors are not inferred from it.

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
