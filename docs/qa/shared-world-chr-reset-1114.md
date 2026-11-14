# Granted common logical CHR reset: source qualification

Root's exact29-byte grant is
`allocations/shared-world-chr-reset-1114.json`, SHA256
`76b4de7eefd18406d81bce95875e4cf30cd1383be05b625f7817efdfba25eda9`.
It permits in-memory composition and source tests only. Root owns candidate
placement, Mesen, cleanup and delivery. This helper creates no ROM, capture,
patch asset, installer, release, or generated build file.

Owning parent421:
`421379021e775e6e03357c0aa11d4cab04008452f94bc9e8938f0662cc0c979f`.
Source-qualified common-only candidate82ec:
`82ec0446873b28af458e7686fec87938feaf798a0a893b44e4dccfd071ccfd63`.
There are28 actual changed bytes inside the granted29-byte envelope. It is
not native-qualified or installed at this checkpoint.

The original corruption and all three root native421 observations are in
`shared-world-sprite-audit-1114.md` (checkpoint4946f8a8). The common change fixes
stale direct modes on logical/native world windows. It **does not** fix active
Prince/DK ownership of native Mushroom window1. Their Mushroom conflict remains
an explicit negative for subsequent private work, with no granted CHR repack.

## Composition and independent inverse

`compose_shared_world_chr_reset_1114.proposal(raw421)` authenticates the frozen
grant and measurement tool599a6213, applies only the declared legacy29-byte
delta, then uses `current_smb2_hidden_input_1114` as the sole owner of retaining
all176 current fixes. All453 complete hidden/cheat envelope bytes are exact;
every byte outside the component changes is exact. No new RAM/CHR/storage,
helper or extra stack is used.

`inverse(raw82ec)` authenticates the exact candidate, restores the exact29-byte
source preimage, verifies parent421 and the typed proposal roundtrip. It never
depends on the mutable nightly. Tests forbid live Downloads rereads and all
file/Mesen writes after the initial input snapshot. Truncated inputs, dirty
owned/unowned/hidden/cheat bytes, wrong forward parents and parent421 presented
as a candidate are rejected.

The explicit `load_current_image()` boundary accepts only exact421 (compose)
or exact82ec (strict inverse/roundtrip). Both boundary states are exercised
with in-memory read fixtures, exactly one boundary read each, zero fixture
files. Frozen421/fa66/default APIs are unchanged.

## Fit and legal caller behavior

PRG126:$8A63..$8A80 / file1034867..1034896 is the frozen29-byte span. Its23-byte
body plus6 owned NOPs clear modes11..1, restore logical windows7..1 from the
existing immutable native table, and restore original exitX26. Mode0, its
current private page, wide flag, special/HUD upper state and all private
code/cache bytes remain exact. The following original
`INC ReloadCHRBank / LDA AreaType / RTS` is unchanged.

The isolated4096-case proof covers all256 input flags, all4 legal area types
and4 RAM/register patterns. A/X/Y/P/SP and all other RAM match original.
Including the original suffix, cycles58→242 (+184 only on an actual area-CHR
change), extra stack0. The grant and measurement contain exact old/new bytes
and hashes; the six NOPs are not available to another component.

Actual source ingress proves two public entries, rather than assuming every
caller enters the longer prefix:

| Actual entry/caller | Taken case | Live result |
| --- | --- | --- |
| LoadAreaPointer$8A30, PRG9:$BC1D | Cold Start | Changed ground mapping; A1/X26/Y1, mode0 unchanged |
| LoadAreaPointer$8A30, PRG1:$A5C5 | Next-level overworld | Unchanged area: original X0 and all modes retained |
| LoadAreaPointer$8A30, PRG1:$A5C5 | Underground1-2 | Changed mapping: A2/X26/Y2, mode0 unchanged |
| GetAreaType$8A41, PRG2:$A003 | Secret-pipe intermediate A37 | Unchanged mapping: X255/modes retained |
| GetAreaType$8A41, PRG2:$A003 | Secret room A194($C2) | Changed mapping: A2/X26/Y2, mode0 unchanged |

All observed actual callers have NmiDisable255. Changed calls clear exactly
modes1..11; unchanged calls do not enter the new body. Private0=$83 remains
intact through both next-level and same-level pipe constructors and their
ordinary standing/walking pose updates. Full private/cache RAM hashes match
before and after each native area call. The isolated all-RAM proof also
preserves every cache byte for arbitrary prior mode0 and wide/special/HUD state;
the repair never relies on a same-pose renderer republishing private0.

## Ordinary source pipeline receipts

All are original CPU/Main/NMI/controller paths with actual compiled UI and
constructors. They are source scheduling evidence, not physical-cadence,
raster, audible-output or native acceptance.

* Hogan, ordinary Goomba plus natural Mushroom:550 Main,
  receipt `aced2aa9159d581986498d8600042520424871563ad4157c7f9a6029ddb40f7f`.
  Goomba banks `[634,16,17,18,19,20,21,21]`; mature Mushroom banks
  `[446,16,17,18,19,20,21,21]`. Actor/control coordinates are unchanged, lives2.
* Toad Select2, complete nonshortcut1-1 and25 living grounded1-2:2974 Main,
  receipt `89d5ce7cfb926a69c92e25987090c42243929950704b47235095ecca957f6545`.
  Terminal40/176, world0/level1/area2, private mode0=$83, lives2/power0/Star0.
* Separate Toad same-level secret-pipe route:752 Main,
  receipt `139639e956b3ddd4f11bacb7401faa3348bc0ec75c26296c973168c5928a7061`.
  The actual authored fourth pipe896..928 leads to25 grounded coin-room
  updates, terminal24/176, world0/level0/area2, lives2/power0/Star0. This is a
  deliberate shortcut case, not an additional full1-1 receipt.

The secret-pipe control's preliminary source-only negatives used encoded-area
assumptions and then an incorrect1792 waypoint. Those controls followed the
ordinary stage or parked on flat ground; they establish no game/geometry
defect. The final control uses the already verified AreaAddrsLOffset5 and the
source-confirmed fourth pipe896..928. On reaching it, a tracer negative exposed
the legitimate direct GetAreaType entry; the final caller census includes it.

## Genuine interrupt and publication gates

The real cold contaminated-preview call was captured before the new body,
including its live CPU, stack, private caches, mapper and scalar state. Every
one of71 dynamic instruction boundaries, covering all17 new PCs, was replayed
with the actual native IRQ and NMI vectors. Three distinct legal variants pass:

| Actual cold variant | IRQ cuts | NMI cuts | Negative-NMI publication behavior |
| --- | ---: | ---: | --- |
| Hogan/raw29 guest | 71 | 71 | Retains committed CHR; no BankSwitch/Publish calls |
| Plain Mario/raw0 | 71 | 71 | 71 BankSwitchCHR and71 X5PublishChr calls; complete valid mapping exact |
| Toad/raw0 private skin | 71 | 71 | Retains committed CHR; no BankSwitch/Publish calls |

Total426 ISR cuts, no IRQ artificially unmasked, minimumSP201. Registers,
private code/cache RAM, mapper maps, transport SMC, R0..R7, mode0 and all
wide/special/HUD state survive. NmiDisable stays255 at every cut; NmiSkipped
advances only by the original one NMI count. Native Mario's original allowed
publication is validated against the complete current logical/direct mapping;
private variants retain hardware CHR. No partial invalid mapping is published.

The first native0 checker assumed all raw0 variants publish on a lag NMI. The
private-skin Toad run disproved that checker assumption; actual function-entry
counts distinguish it from plain Mario. No ROM issue is inferred from that
negative.

Only the negative NMI arm is reachable **inside** this body: actual callers
enter with NmiDisable255, the new instructions never modify it, and real IRQ
cuts preserve it. A regular-NMI arm forced into a busy frame would be a poisoned
fixture. Regular post-update NMI/CHR publication is exercised by the ordinary
Hogan route, full1-1→1-2 and secret-pipe paths via the established scheduler.
This scope does not claim arbitrary synthetic NMI states or hardware cadence.

## Frozen root replay APIs

`replay_shared_world_chr_reset_1114.controller(raw82ec, key)` is an explicit new
adapter. It independently inverts to421 for frozen bindings, then changes only
the new candidate pin, actual changed-bank hash and private observation label.
The frozen421 factory/template remain byte-identical.

Factory SHA256:
`0fb4e745e0ec7e47a27f43d3f8b7015e8fbc80f87225fec08751d20f444424c0`.

| Key/API | Frozen LF Lua SHA256 |
| --- | --- |
| hogan | `829f3f2529c241af8a2fe2ce3d8cf453624646a0f91a6d88480b5d91978b4165` |
| prince | `9a1ff092dffa136092394d11f562b5341445b3751700b1ee5aebff5e6275432a` |
| donkey_kong | `dca5f9ffaf8e808f2d4e535ab907879562246479e710f3c527d6c7d2870af45b` |
| stage_controller(raw82ec, 'toad') | `a42266b5ba49dc7aa07f59431f7fee93b2fac638407728daebc2b3bec2720161` |

Each image run remains two in-memory PNGs, each<=65536B; all controls are
ordinary. Source checks qualify the common reset for Root's next native gate.
Root must verify Hogan/Goomba/Mushroom improvement and appropriate transitions
before delivery. Prince/DK private Mushroom failure is still expected and must
not be relabeled as success. No native candidate has been run by this helper.

## Root18493 native private82ec results

Root ran the frozen APIs against private82ec, retaining actual Downloads421.
Hogan's two images now visibly show the correct Goomba and Mushroom. Receipt
`b1388d1a1d4f5f38ddb34a82a11a56b013df0bc62cae94fb63896a9005057e05`:
1490 physical/908 Main, exactly the old corrupted421 run's counts and actor
coordinates. Both shots select `[446,16,17,18,19,20,21,21]`; actual A2/A4 page17
and7C/7E page16 bytes match native patterns exactly. Private0 mode and full
state are unchanged. PNGs2701/3131 bytes, in memory only:
`07affc626261432af5b003c6a03e1b1dc4396b0f6b2bb4facfccf5f2ff55f3a1` /
`a177ef68d0ed895ba76727c8e88bea39fe0fbd5e5f3f4941145139b20fe91722`.

The frozen Toad full-stage adapter passes native3221 physical/3204 Main
entries=returns, flag1967/castle2030/entrance2607 and25 grounded1-2 updates.
Terminal40/176/high1/native0/lives2/power0/Star0/variant5/CHRmode131. Receipt
`cd0e705ddb11054cd9bdc92d4170616b42437fe550c7338edbb6a4e5abc701f1`.
Counts match the earlier421 native positive. No generated files/capture files,
patch guard violations, or Downloads change occurred during this private run.

## Root60180 family coverage and Root38527 delivered verification

Root60180 completed all seven remaining ordinary image observations on exact
private82ec. Every case retained two lives and used two PNGs in memory, with no
actor/powerup seeds or generated files. The five remaining WWF choices all
published Goomba page17 and Mushroom page16 with exact native pattern bytes and
palettes3/2. Together with Hogan above, all six WWF choices pass this graphics
scope.

| Choice | Physical/Main | Frozen LF Lua SHA256 | Native receipt SHA256 |
| --- | --- | --- | --- |
| DiBiase | 1521/935 | `73f0db48c513520094c7a13189f0c841a22d71f9c2e24ac511ca38a65fa1ea9a` | `8a48e452778b97ba835e6bd011102ec9aa46c85d15eac68ee58f7b680187845f` |
| Bigelow | 1513/921 | `eedfe2fe67f6e532167c9030aae9033e0cc4c2b5334c01fa9b0015c9abefd3e6` | `f9d50b466a2f14ee74a04e76718df0e485cb2f4c6ce96e27610f21ed7e87bb9b` |
| Honky Tonk | 1527/946 | `81f4afeb98770a4ae4c98e38f3944c733ddbc7c63baaa9a78445181f38e2aebc` | `7a78b1697a72da2dcf5e53fb5eacd4e86eebc931b7dccc468f2b2bff7eb386c4` |
| Savage | 1544/965 | `c4a04cab88803df9465df2b346bea705b2001fa41a7be81f26d364736deb2eac` | `32198dc0ed34e09d25e8302c2a2bca45dea97687438e69f9b538f88c95f1b235` |
| Andre | 1536/963 | `26aca0d675e0594535cc98e9d359f83e2c239c1abfb3f0597d236616759aef69` | `d4f29e1418ebe11eae8df40894d37a24108e072d7e183fd0362aabded58b3b82` |

Prince9a1f remained1640 physical/889 Main, receipt
`b7cf1884fcefd212856c5e9af39c11b86ab793ef821fec891928ffbd41abdbb0`.
Its Goomba now uses correct page17, while its Mushroom still uses private383:
the incorrect Mushroom PNG remains exactly
`595e13dbdc682834d4d7ae252f32418efbae1a19ca26d1257dfd8bdbe9256f55`.
Donkey Kong dca5 remained721/666, receipt
`c2f2c59605408ada7a64e14dcaca041853e587f2c37cf8f626a52c4e9c243661`.
Its Goomba is corrected to17, while its Mushroom remains blank under823, with
the same PNG `80d7a864a79b1607b65d3bff2c9e780399cf2a44b8145f2b683a4e656d7e55aa`.
These two private slot1 conflicts are observed negatives, still open.

Root directly replaced Downloads with exact tested82ec. Installer6590's
terminal output was unavailable, so Root38527 deliberately repeated actual
Downloads verification idempotently, starting from already82ec. Both frozen
Hogan829f and Toad a422 tests pass again with the identical counts, receipts and
PNG hashes recorded above. Pre/post patch guards are clear, no same-name
sidecar or output file exists, and installed bytes equal the tested82ec pin.
This closes delivery of the common reset only; no private Prince/DK fix is
included or claimed.

All producers use bounded `build/shared-world-sprite-audit-1114`, max-files1,
timeout<=600. The directory never exists: zero generated bytes/files. All
recorded producer results are terminal; no success is inferred from a missing
process. No user file, frozen grant, frozen legacy factory or game source was
edited. The source-only composer/checker/replay wrapper and this QA are the
owned successor files.
