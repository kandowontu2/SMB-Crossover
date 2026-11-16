# Shared draw/audio attribution and detached BT draw route — November 15

Status: **detached proposal; no optimized ROM image or mounted overlay**. Root
owns native tests, candidate files, staging, delivery and cleanup. This packet
changes no gameplay, validation, audio, sprite data or installed ROM bytes.

## Inputs and measured scope

The cost inspection used genuine compiled Rash cold entry on exact `7fb328a6dcf6b50fd000e81eced4fd4b7390bedec56085d33130434003cc76d0`,
four warm updates, four idle updates and four Right updates. It supplied only
ordinary controls; there were no health, enemy, terrain, position or ability
seeds. Source cycles are attribution, not a physical-frame or controller-lag
claim. Root's actual-native result is recorded separately in
[battletoads-attribution-native-1115.md](battletoads-attribution-native-1115.md).
That native result has 985 balanced named entries/returns, not the separate
source observer's 1,120 callbacks. The native DrawAll mean exclusive cycles
were 7,463.83 idle and 7,459.35 walking; 7,448/7,449 were minimum wall costs.
Nested draw/graphics/render costs must not be summed.

The detached plan owns exact current input
`67e3b8e7d4b01ea549fe9dc15c09b5a0b5f7085ee396d672a9c963d24287d0b5`.
Its strict reference API calls the direct 72-byte inverse in
`compose_bub_selected_star_palette_prince_1115.py` (SHA256
`79699547d00efeb3e90d2fb321d0a9195f02b7e1e91965759a5f6c888df9aeaa`)
to exact 7fb for bindings only. It proves that all 226 draw bytes and all bytes
outside those declared 72 palette/cookie bytes are unchanged. The old source
cost receipts remain 7fb evidence. A later frozen 7fb-only funding inspection
correctly refused 67 before extracting or executing anything; that is a typed
input rejection, not a game failure.

## Concrete attribution

`inspect_shared_draw_audio_costs_1115.py` source profile 40422 passed with
receipt `6dd8a2c53b7c9798b6bea7509d1e48d821bbe6f51129b14c5f80ac38cf19dba7`.
Byte/call inspection 76918 passed with receipt
`c57ae37b42b370abef93cd4748da0ff3bf6cca8a36951c252ee77cc13fb3fdfd`.
There is one explicitly accounted nonlocal NrResolve stack unwind at
PRG124:A1A8→A1CC per render; it is not represented as a balanced child return.

| Source scope | Idle / Right cycles | Relevant inclusion |
|---|---:|---|
| DrawAllMetasprites | 7,471.75 / 7,470.5 mean | Entire draw scope |
| KbDrawDispatch | about 4,154 | ThShared → NrDraw → HuDraw → public BT draw |
| NrDraw | about 3,909 | HuDraw about 3,583; public BT draw about 3,402 |
| Native MetaspriteRenderLoop | about 1,330 | Actual native sprite renderer |
| RlSpecialDrawDispatch | about 1,022 | Later chain is not declared redundant |
| AudioUpdate | 3,051 / 2,988.75 mean | Actual music/mixer/retirement paths |
| ExpandedAudioUpdate | 1,338.75–1,399.5 | Includes real expanded byte decoding |
| GuestAudioFinish | 776–777.5 | Not proposed for removal |

The concrete candidate route skips the redundant Nr/Hu dispatch wrappers for
selected raw33 while reaching the same public BT boundary, which still checks
the complete cache header and executes the full BT draw. The measured old
wrapper gap is about 507 cycles per render. The new frontend costs eight more
cycles for raw33, giving an estimated net 499-cycle saving per render pending
actual mounted public-path proof. The same frontend adds **eight cycles per
render for default foreign owners**, including all six WWF choices. This is an
explicit tradeoff, not a global speedup claim. No audio optimization is proposed.

## Exact 118-byte detached descriptor

The sole proposed envelope is file `[545972,546090)`, physical PRG66,
CPU `[B4A4,B51A)`. Public entry B4A4 stays fixed. Its old SHA256 is
`0991df9191ae7b3cf47a4c520515e5f91598d0004e4c57d80bebd09067fdd22e`;
new SHA256 is
`dd8cd717d8bb2f8e97a768e2b346d488060fd80d3d7bf56924cd460ca7a6b869`.
There are 106 changed bytes: 89 instruction bytes, 27 table bytes and two
retained old suffix bytes. All nine relative branches stay within the 89-byte
instruction body. The descriptor API emits the complete old/new hex and labels.

Old rows 1 and 2 are identical `CF:A8F0`. Raw14 is classified to row1, freeing
row2 for selected raw33 only: **D7:B026**. All other eight descriptors retain
their exact targets. Bass raw9's zero/nonzero variant branch and Link raw10's
`FmAlts & $44 == $40` special case remain intact. New tables are B4FD/B506/B50F;
their three indexed readers are B4DF/B4E5/B4EB and use base-minus-12 operands.
No new RAM, CHR, code padding or art resource is requested.

All 108 following bytes `[B51A,B586)` are live and remain byte-for-byte fixed,
SHA256 `0d651d53d3e24002ce7592c7a7a99081f5869329f48cf6c5ef77699a650d5a40`.
This includes ThShared's JMP B4A4 at B549, the HotPlayerGraphics trampoline
at B55E (entered from B3C2), and the Mini helper at B57A (entered from B494).
The unrelated Kb 50-byte gate is also fixed, SHA256
`3c5e692f1c65a9f2a5e3ecdc4abfce6a0eee9a25a78b6b33e20aacf9f749ea37`:
its 18-byte dispatch, 25-byte live ThKbNativeFallback and later seven bytes
are not spare storage. Independent ingress/table/alias review is owned by
`dk_handoff_lag_1114`, separately from this plan.

Root independently verified the descriptor as 94926. Local descriptor 70060
passed, receipt
`de360d6f8d5c44636e50a94fb183a144362f50579bc0f6c11939f962e3fb1e5a`.

## Detached primitive qualification

Flat classifier 64035 terminated with exit 0 and receipt
`26f2e7eb8f4f4966395397789766b9db489b590335b7febb13d240d702db72c5`.
It executed 233,472 old/new cases in separate flat arrays at real B4A4 using
RP2A03 `NesMPU`, including incoming D=1 with NES binary arithmetic:

- 131,072: all 256 selected values × all 256 FmAlts × zero/nonzero roll branch.
- 32,768: all 256 selected values × all 128 hardware statuses with U=1.
- 65,536: all 256 selected values × all 256 input A values.
- 4,096: register/status corner cases.

At the unchanged FarCall+3 boundary 015D, AXYP/SP, SafeA, CVID publication and
four stack bytes match exactly, with normal PHP/PLP B/U normalization on both
versions. Minimum SP is 220. Only selected raw33's target tuple differs.
The union of noncode reads is exactly 01DD..01E0, 5FE5, 5FEB and 6002;
writes are exactly 0162, 016A, 016C, 016D and 01DD..01E0. Input/private fields
are not written. Old/new data accesses stay within their own 118-byte arrays.
This proves the classifier/frontend only. It executes no public handler,
NesBus, mapped ROM, interrupt, cold constructor or gameplay path.

Current67 target-byte inspection also terminated with exit 0, zero files:

| Preserved target | File half-open | SHA256 |
|---|---|---|
| Public BT draw veneer `JMP B08E` | 716854..716857 | `80b70a03bbecdfe1731826f5ad1cc0fc143ea0e10daf99d7c7868415e0eb08ab` |
| Full BT router, 224 bytes | 716848..717072 | `bca680209849a80d2e3901070954bba08c1805024eec17682047df941d032535` |
| Full BtCheck, 65 bytes | 765392..765457 | `8c45e152a5f3db42638cb3210b4fa14d151fa1ba42f07409f470ea2def767870` |
| BT cache, 8,192 bytes | 1989648..1997840 | `8605ac5665158653b677e7e12f44f712afb9b003c9d8a7998a632aeaedaf5c66` |
| Old NrDraw entry, 27 bytes | 1016242..1016269 | `60f069cf85b71fcdcb29d4deafbfe0528cdf41205cad58a5c70b2ab788df5965` |

## Reproduction and remaining gates

All producers used absent `build/shared-draw-audio-costs-1115`, max-files 1,
600 seconds, with aggregate stdout receipts and zero generated files. The root
was confirmed absent after terminal tests. No ROM file, image, capture, staging,
Downloads modification or native helper launch occurred.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/shared-draw-audio-costs-1115 --max-files 1 --timeout 600 -- python -B tools/audit/plan_hot_draw_bt_67e_1115.py
python -B tools/audit/run_bounded_build_v1.py --output build/shared-draw-audio-costs-1115 --max-files 1 --timeout 600 -- python -B tools/audit/check_hot_draw_bt_classifier_67e_1115.py
```

Premount scope is descriptor, flat classifier, target preimages and independent
ingress/alias census. A new explicit source lease is required before composing
or mounting an owning67 image. After that lease, required gates include real
public D7:B026 old/new return ABI and failure/cold/pause/foreign paths, actual
IRQ/busy-NMI transport, lifecycle, weighted foreign costs and ordinary routes.
Physical cadence, native qualification and delivery remain false.

Frozen source pins:

- Cost inspector: `21daaeee0ea90bcc74f86650df3fbfe152c31b88da39e7740d1439866003b86d`.
- Plan: `0bc656412e3c1a2d32bd4fea10ebb6574ceb81207d0d510a021d5536a35a197d`.
- Flat checker: `65f5256467adfe862d62b131933e2081abbcd8458c8d43b173c89c8ee3f7a221`.

After this detached qualification, root issued source-only lease
`allocations/hot-draw-bt118-source-1115.json`, SHA256
`ae2d0689d230314f1cc1adb665cf633efe6bdfbb37910e142a5a3b9fc74ddebf`,
commit `a8d26ba8`. It authorizes new in-memory composition/mounted source gates
only. This detached packet remains frozen; subsequent composition and actual
public/lifecycle qualification are recorded separately. Native, file staging
and delivery remain unauthorized by that lease.
