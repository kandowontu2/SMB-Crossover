# Remaining DMC fixed-prefix differences on delivered12397

Read-only inventory of exact Downloads SHA256
`12397b1c2557834f6a2b7e23c9915d5dc40c6cabff7a6ee844c1adebf6564c52`.
Scope is physical PRG119/120/125 versus127, offsets0..4415 inclusive
(`E000..F13F`,4416 bytes), ending before the first SMB2 sample atF140.
This does not alter or broaden the verified
[12397 delivery](smb2-postbg-delivery-1113.md). No game bytes, source
recipes, allocations or frozen observers change; no broad copy is proposed.

| Bank | Differing bytes / contiguous ranges | Prefix SHA256 |
| --- | --- | --- |
|119,120 (identical)|46 /7 each|`1273ae272ff77db116df97be12689720163fefa9c81692d2add0d165cb3df7bc`|
|125|42 /5|`47d5a24fadc6d3da0057b7d6967a3267cf2e5773ac674fb6728fad3af63fc7b6`|
|127 (reference)|0|`b189d5e7b4fbfe62cf5c52b6d77af3d3af95a8ab05fb6946ade4e65ad0d5bff3`|

The closed head/feet/side `E45B..E499` and post-BG `E5CC..E5FC`
windows are byte-identical in all four banks. There are no other differing
prefix bytes beyond the ranges below. Addresses are inclusive CPU ranges;
file offset is `16 +8192*bank +(CPU &8191)`.

“Stale” identifies a known later implementation not reflected in an alias;
it does not assert a newly reproduced gameplay failure. No remaining
difference is proved intentionally necessary in the current nightly.
Some audio padding is intentional within its coherent **older** layout;
the reason for retaining that layout in current aliases is unproven.

| Banks | Differing range | Alias → canonical bytes/meaning | Owner and classification |
| --- | --- | --- | --- |
|119,120|E037|`DE → F5`: cold farcall target `CF:BDDE → CF:BDF5`|`GuestGameRoutinesBridge` / `HuGokuGameCold`: **stale obsolete address**. Current BDDE is a store inside `HuLateUiDirect`, not a game-cold entry. BDF5 is current `HuGameColdDispatch`. Highest-value remaining address investigation.|
|119,120,125|E0D6|`2A → 7B`: reservation target `C2:B92A → C2:B97B`|`PlayerOAMReservation`: **stale valid legacy target**. B92A remains `MaaReservation`. B97B is `MtReservationV5`, which adds24-byte reservation for raw0/MarioVariant7/**PlayerStatus2** and otherwise tails B92A. No new bad instruction entry is implied.|
|119,120,125|E710..E715|sixEA → `8D45014C3EEB`|`GiantReturnDraw`: **stale missing executable extension**. Canonical publishes CurrentBank and jumps EB3E (`STA5115/RTS`); aliases retain old NOP padding before `MegaManCheckPit`. A genuine Giant caller exists, but its execution while one of these aliases is active was not established here.|
|119,120|F062|`BF → E0`: AudioUpdate's A-map bank|**Older valid audio forwarding; current intent uncertain.** Canonical maps96 for WWF/Hogan `WfAudioProbe`; aliases map63 directly. Interpret with the next row.|
|119,120|F067..F06E|`00B6` + sixEA → `B9BC20ECA44CCEF0`|`AudioUpdate`: old `JMP B600` versus `JMP BCB9`, followed by absent finish worker. B600 is still valid `GmFamilyNmiGate`, so this is **not an obsolete target**. Canonical adds the Hogan probe and shared quiet-mix finish worker. Wrapper/worker synchronization policy is **uncertain**, not grounds for copying this range alone.|
|125|F069..F06E|sixEA → `20ECA44CCEF0`|Missing quiet-mix finish worker `JSR A4EC / JMP F0CE`. Its absence is **internally consistent with the older GuestMix below**; no direct caller targets the old padding. Stale optimization companion, not an independently dangling call.|
|119,120,125|F0B6..F0CD|older unconditional tick/finish sequence → quiet-effect guard and new finish-bank branch|`GuestMix`: **stale optimization layout with valid old callees**. Canonical skips the bank7 tick only when7FA6/7FA7/7FA9 are all zero, then uses the fixed worker. Old code still calls valid87:BFB4 and9D:A4EC. No new effect/cadence defect is measured here.|
|119,120,125|F0D3..F0D7|fiveEA → `8D1551D091`|Canonical `PublishMixerBank`: `STA5115 / BNE F069`. **Intentional padding in the older layout; present retention uncertain.** Old GuestMix already finishes through the unchanged F0CE..F0D2 restore/RTS and never needs this continuation. Coupled with the preceding two rows.|

## Current callers and source anchors

- **Cold game gate:** current native126:83A1 (`GameCoreRoutine`) calls
  E02B. `GuestHurtKind`6F1C OR `CheatInvincible`7FFB must be nonzero to
  reach E033 and its changed E037 operand; otherwise E045 takes the regular
  native GameRoutines route. `src/guest_injury.s:7` owns the bridge.
  The retained live input `build/karnov-host-resource-base-1101-v1/union.s`
  was read in place, SHA256
  `fa55d0b6aa95afb111261b6c2634b4054bf0439b59ef14332f7de742f0bcbbe2`.
  Its `HuGameColdDispatch` preserves PHP/PHA and routes Dragon Power,
  Rogue and foreign cheat/injury paths; `HuLateUiDirect` instead owns the
  late palette/UI tail. Current79:BDDE is `STA016C` inside that UI tail,
  followed by AA/BF SMC setup and two PLA, whereas79:BDF5 starts PHP/PHA.
  The stale destination is statically conclusive; no fresh DMC+gate trigger
  or new failure is claimed.

- **Reservation:** actual E0D2 callers are native4:A145
  `ClearReservedPlayer`,4:B826 `LegacyReservation` (JMP), and9:BCB6
  `NativeRareVictoryModeCore`. The public owner is
  `src/metasprite_engine.s:276`; the current replacement is
  `tools/reference/mario_tank_graft_1101_v5.inc:9` and its source-owned
  pointer rebind is in `prepare_mario_tank_candidate_1101_v5.py`.
  Current66:B97B bytes explicitly check6002=0,730A=7 and075B=2;
  075B is **PlayerStatus**, not engine000F. Variant7 is Mario the Tank,
  independently identified by its current candidate/menu source. The shim
  returns A24 for his fire form; all others tail still-valid B92A. Runtime
  exposure with an active alias is unqualified, and no full ABI test is
  implied by menu identity alone.

- **Giant return:** the current native90:B889 is the actual `JMP E710`,
  preceded by `8DA17D8D1651A9BF48A9FA48A984`. This matches
  `GiantTailFinish`/`GiantReturnDraw` in
  `tools/reference/mega_giant_mario_late_draw_1110.s`; the six-byte owner
  span is recorded in `check_mega_giant_f33_1110.py`. Old retained labels
  call this page Rogue audio, so that nearest old label is not used as its
  ownership proof. No active-alias Giant crossing is rerun or claimed.

- **Audio prefix:** actual NMI callers are E375 and E3FA in each fixed
  copy (lag/regular paths in `src/reset.s`), plus native5:B85B
  `SoundTestAudioTick`. The installed target96:BCB9 is `WfAudioProbe`,
  anchored in `tools/reference/wwf_roster_native_support_v1.s:67` and its
  explicit AudioUpdate rebind in `join_wwf_roster_bounded_v1.py`.
  Its owner gate is Hogan raw29/default family; a foreign probe restores
  context then reaches the same valid63:B600 `GmFamilyNmiGate`. Thus the
  older119/120 route bypasses the probe, rather than entering removed code.
  Whether preserving that bypass during old-owner retirement is deliberate
  needs its own contract study, not an address-only repair.

- **Quiet-mix group:** actual F091/F09B/F0A5/F0AF jumps reach F0B2;
  source ownership is `src/music_drivers/audio.s` and
  `tools/reference/guest_audio_quiet_tick_1110.s`. The producer/checker is
  `check_guest_audio_quiet_tick_1110.py`; it intentionally preserves the
  external F0CE..F0D2 return used by63:B52A. Canonical F0D6's relative BNE
  reaches F069; F0CB's BNE reaches F0D3. There are no native literal
  JSR/JMP callers of F069 or F0D3. Neither absence is an independent proof
  that the padding is free. These three ranges belong to one layout change.

The next concrete address question is the gated E037 cold dispatch.
Tank's valid legacy fallback, Giant's alias-domain reachability and the
coherent audio differences are separate lower-confidence investigations.
No broad synchronization, code allocation or performance claim follows.
Only byte/symbol/source inspections ran under the existing empty bounded
root `build/prince-pickup-reach-1112 --max-files 1`; outputs0, no extraction,
ROM writes, Mesen, captures or changes to the user-dirty progress JSON.
