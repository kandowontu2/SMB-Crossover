# SMB3 completed-Main controls and current native clears — November14

Input remains exact installed421379021e775e6e03357c0aa11d4cab04008452f94bc9e8938f0662cc0c979f.
No ROM, physics, actor, terrain, health, ability, cheat, helper or cosmetic change.
No installation, patch/release asset, capture or generated build file.

`replay_smb3_mainclock_full11_1114.controller(raw,key,damage_probe=False)` is a
separate successor to frozen020c83c9 controls. Frozen c8f/BF45 factories remain
byte-exact. The current native-qualified choices are explicit:

| Choice | Logical generated Lua SHA256 | Scope |
|---|---|---|
| `key='toad3', damage_probe=True` |`52d028149999b274f3640dc9e601f7ea02a7e04a90b0abdc5b8cccb50ad5d87e`|Earn power through ordinary inputs, permit a real actor injury, cross the second gap as form0, then full stage|
| `key='peach3'` |`30e533cd1d43814653dc87fa712aa92fcd3b58caafb2362e6e3d5f662a91130d`|Ordinary full route using Peach's actual hover at the final gap|

Physical input polls now apply cached buttons. Navigation decisions use only
fully returned Main snapshots, and route frame/poll clocks use completed Main
counts. Actual M3Previous supplies the held-A edge. This avoids consuming a
35-update jump hold through multiple physical polls or reading partially updated
movement state. Genuine title/roster/Select/Start remains physically driven.

Bounded second-gap trace covers takeoff, matched M3Movement returns, Main-return
decisions, native form, VX/VY, actual/previous/requested inputs and A held. It
retains at most32 first records,64 tail records and8 takeoffs, in memory/stdout.
M3Movement's real stack return is the CPU-RAM FarCallCommon stub at016E;
the typed symbol is FarcallJmpTarget_SMC+3. Return PC/SP tokens match actual
calls. An initial source observer rejected this legitimate RAM return and
stopped at2 updates; that was an observer error, not a gameplay negative.

Source Toad52d full PASS3184 Main entries=returns,1835 movement entries=returns,
1743 native steps,58 next-area movements. Real M3Injury atMain542/X697/Y176,
form1, X-register slot1/Enemy_ID6, inputRight alone; no actor or power seed.
Form0 second-gap takeoffMain896/X1346/Y176/VX40/VY252/A held; genuine grounded
far bankMain958/X1501/Y176/form0. Flag1777/castle1839/entrance2587 and25 completed
grounded1-2 updates finishX40/Y176/lives2/power0/Star0. Source receipt
`a217bb0397e98fecb0dd4eedb1127bf93da122a789719b867ee1454f270d7777`.

Source Peach30e full PASS2891 Main entries=returns,1695 movement entries=returns,
1649 native steps,58 next-area movements and92 airborne hover-ready2 samples
across the route. Flag1637/castle1699/entrance2293 and25 grounded1-2 finish at
X40/Y176/lives2/power1/Star0. Source receipt
`211112554b9dc01aea34180d5d13e01574c278afc612bd0f0aa8f081be167fdb`.
These are CPU scheduler counts, not physical video/APU timing; the source
frontend remains a menu arena without actual vblank. Native is separate.

Actual Downloads421 root95857 Toad52d terminal PASS:3752 physical frames,
3751 polls,3330 Main entries=returns,1860 mapped movement entries=returns,
1768 native steps,58 next-area movement calls,25 living grounded1-2 updates.
`damage_probe`, `post_damage` and full1-1 are true, maxX3266. The live Lua's
required injury and grounded form0 far-bank assertions pass, as do both lives.
Exact terminal nested fields and injury actor class were not retained in root's
compact native summary; do not substitute the source values above. Receipt
`ba892ced8b474e45c6337d27f6c2d2f20f6c2d652371a575f9e69f404ef46e2a`.
The logical generated text is52d028; Windows `write_text` produced CRLF file
bytes SHA256 `9d14c3ca742bc66fe84a1a9fa332e310851e76ace9809e7269b85f0ec54f429e`.
These two hashes are not claimed to be identical file bytes. An earlier native
output was lost at a context boundary; it supplies no pass/fail claim. A retry
stopped at capture preflight before launching Mesen;95857 is the retained pass.

Actual Downloads421 root33056 Peach30e terminal PASS:3777 physical/3776 polls,
3351 Main entries=returns,1881 movement entries=returns,1789 native steps,
58 next-area movements,141 airborne hover-ready2 samples across the route.
Native flagMain2115/frame2531, castle2177/2593, entrance2754/3176 precede25
grounded1-2 updates. TerminalX40/Y176/YHigh1/lives2/power0/Star0, variant3/CHR131,
maxX3267, `post_damage=true`. This differs from source's undamaged power1 path.
Receipt `37549a26d99b0625123f9606759541062c63f9ccd8919d5cdeeb73f4dc1f1f2e`.
Root writes LF bytes for this controller, so actual script file SHA256 is
exact30e533. Both native runs have clean pre/post patch guards and zero files/
images. The installed ROM remains421; no new ROM delivery is required.

Retain negatives without reopening the now-cleared identities:

- Frozen c8f source full pass versus native10309 second-pit death are recorded
  in `smb3-toad-peach-full11-1114.md`; no ROM bug was inferred.
- Initial completed-Main ordinary Toad8bddb26d source clears the second gap but
  dies at the final stair, source1370/X2467/Y241/engine11 before life decrement.
  Receipt `84e82b33c442d6af947c7350d67295190ccf6d2c57ab2565e70bd64c4e455825`.
- Already-completed source-only all-form stair adaptation21f03ec3f4f2a9d69b5ac6ac53a468a4d0252d533e2e533108cc45aad7421e5f
  passes2954 Main/full stage/power1, receipt
  `03a59db3507c886d7d0208db90828eb89c61e24f5f60d8bdea124d491fb96dca`.
  It has no native pass and receives no further work: actual post-damage52d
  already closes the required Toad clear. Genuine cold-prefix tile reads confirm
  existing cap columns2416/2432 top144, gap2448..<2480 and far cap2480 top144;
  nothing was seeded or placed. This geometry diagnostic is not separate gameplay
  qualification.

SMB3 Toad and Peach are nowC; U15 reduces to13 across these two native closures.
Natural-item collector/erase/score/sound and full powered ensembles remain
separate from this full-stage scope. All176 current fixes and exact preserved
SMB3 code/CHR ownership are checked by strict421 metadata. No helper added/moved.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb3-mainclock-source-1114 --max-files 1 --timeout 600 -- python -B tools/audit/check_smb3_mainclock_full11_1114.py --identity toad3 --damage-probe
```

Use `--identity peach3` for the qualified Peach route; `--metadata` skips gameplay.
The output root stays absent. Protected roster progress and Steve QA untouched.
