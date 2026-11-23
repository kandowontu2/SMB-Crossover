# Donkey Kong Jr. opening performance

The installed `59e1a591` nightly runs 13 full code header checks in each
ordinary Donkey Kong Jr. update. A linked CPU trace of 16 standing and
16 walking updates found 7,449 cycles per update in those checks. Both
tests began through the normal character menu and used an empty opening
in 1-1. [Trace script](../../tools/audit/profile_dkjr_shared_dispatch_1123.py)

The `b7562774` test ROM repeats the full check at the first call of each
update and checks the live bank prefixes for the later calls in the same
update. In paired linked CPU runs, it saved 5,080 cycles per standing
and walking update. The observed native game state, bank mappings, and
PPU state stayed matched through 32 standing, 48 walking, 16 jumping,
and 26 landing updates. The saved cycles during the jump averaged
4,649 because some calls fell back to full validation. Source receipt
`1c277d93c992d52e80abaa1582dea1723f689828ba3c6ade4340eb099c892f03`.

Mesen completed the same 48 standing and 16 walking updates in 13 fewer
video frames. No enemies were active in either run. Both runs finished
at world X50/Y176 with two lives. The standing phase improved, while
walking still took about two video frames per game update.

| ROM | Video frames across both phases | Frames with no game update | Skipped NMIs | Mesen receipt SHA-256 |
| --- | ---: | ---: | ---: | --- |
| Downloads `59e1a591` | 128 | 64 | 96 | `6a4cf967e575c0b7c397666f176de4b569aa812a63d289eacc7fd95614c3b41b` |
| Private `b7562774` | 115 | 51 | 83 | `0e2678cb33ea64052c6b9ffa74b48f00df78bf6df5eef3f17690006e6258badc` |
| Private `7bcf137e` | 112 | 48 | 80 | `d553b52f69c1706c614d15bb505bab35fdca69a3ac5301d1a726f191325d2fa6` |

The Downloads nightly for this comparison was `59e1a591`. The private
clock tests used the same shared test slot. All three runs wrote zero
captures.

The first private test exposed a dispatch issue during source review.
Out-of-range service addresses could reach a candidate helper before the
range check. The `7bcf137e` revision checks the address first and always
verifies both complete headers on the first service of a game update.
All 100 out-of-range controls rejected the call before entering the fast
helper. The first service also rejected a corrupted header in either bank
despite a matching frame stamp. Paired game state still matched and the
revision saved 5,158 cycles per standing or walking update. Source receipt
`6fbb422c919d4367e0eb2719cd4a34df1c6abe1ba11f6091618434a15716f690`.

The same revision passed 626 IRQs and 626 busy NMIs injected at reached
instructions during ordinary play. The original interrupt handlers
returned with the same live stack, and each affected game update reached
the same gameplay state as its uninterrupted counterpart. The minimum
observed stack pointer was 167. Receipt
`ec9008f5eb74b2f785ee519dfd47d68679922122aa7d50979a97e0e2e20ad2be`.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_dkjr_dispatch_native_1123.py --run
```

## Combined test ROM on `28708fa9`

The next private candidate, `14b0b4c2`, combines the Donkey Kong Jr.
optimization with the Sonic dispatcher. The first call still checks
both complete headers. Later calls in the same game update check the
live bank prefixes and the owning character's update stamp. Donkey
Kong Jr. uses `$C8FF`. Sonic, Super Sonic and Mini Mario retain their
existing stamp. The verifier also checks the Rogue Dawn pipe bank.

The linked opening comparisons passed 167 cold game updates and 53
ordinary updates per character. Donkey Kong Jr. saved 5,009 CPU cycles
per grounded update and 5,010 in the airborne test. Sonic and Super
Sonic used 156 additional cycles per update. Mini Mario used eight
additional cycles. The verifier passed 1,976 native IRQ and 1,976 busy
NMI checks, plus malformed target and corrupted header tests. It also
checked foreign dispatcher inputs and the current DK address ranges
that could have reached the stamp.

- Source and interrupts receipt `86500689b1292916e43d80e457aa52bf103cebfa84815b58668032a88781384e`.
- Foreign selector receipt `e176fc89b8af30a4b8df9cb793ab4dcd0cd4c2cd8f4366fc35fd56fc6dd69491`.

Mesen ran the same 48 standing and 16 walking updates through the
normal menu. The private ROM saved eight video frames while standing.
The walking phase took 32 video frames on both ROMs. Both runs ended
at X50/Y176 with two lives, zero enemies and zero captures.

| ROM | Video frames | Frames with no game update | Skipped NMIs | Mesen receipt SHA-256 |
| --- | ---: | ---: | ---: | --- |
| Downloads `28708fa9` | 128 | 64 | 96 | `48939baa89370f98fa9231c846fdc7ee5605e20f6d018db28909b54784832856` |
| Private `14b0b4c2` | 120 | 56 | 88 | `f9fd3f2c8a605e35959bf8563534e16a9039ee9f9a606bdc2f68d6cfbf14b84c` |

The first full-stage Mesen run on `14b0b4c2` reached the top of the last
staircase at X3028/Y48 with 82 on the timer. During the wait for the
final lift it went left to X2990/Y64, where the timer expired with
both lives still recorded. The run ended after 20,076 video frames.
The trace establishes the point to inspect before the next full-stage
run. The native Sonic and Super Sonic routes also need testing on
this combined candidate.

Full-stage receipt
`9a29c99b9db5e459f3919a306f288a71bc0ab418e9668c906ab8070c510d10b3`.

## Full-stage comparison from Downloads

The first comparison on `28708fa9` stopped at the second gap because the
replay required the native movement state to be grounded while checking
for a transient native State 2. One update had State 2 and original
standing state 1, with the original body at Y191 and the native player at
X1366/Y176 over solid tile `$54`. The revised check accepts this supported
wait and still requires native State 0 before sending the jump.

With that correction, the Downloads replay reached the staircase top at
X3026/Y48 and continued to X3038/Y48. It caught the native lift at
X3038/Y41 with the lift top at Y73, then left the lift at X3067/Y160.
DK Jr. touched the flag with time remaining, entered 1-2 and completed 25
grounded movement updates at X40/Y176 with both lives. The run took 22,242
video frames and wrote zero captures.

- First comparison receipt `0f35ed56c3738347085d0821896c2ecf1520c2ebec3a1af543461b613e5c055b`.
- Passed comparison receipt `3264106dfaa17ec8c92884167cafa9fff9ce8221aeecc32737f5d729a3ea8ec0`.
- Passed controller SHA-256 `1b21ff42fb0a25bfe1ded82070efab52689897c6f65bdec44c053705dfc5044f`.

The installed route demonstrates the support and input sequence to compare
with the private candidate before delivery.

## Private final lift trace

On `14b0b4c2`, the replay reached the top at X3028/Y48 with the lift at
Y80 and already carrying DK Jr. He advanced as far as X3030, then went
back to X2990/Y64 before the timer expired. Right reached the original
input routine for all 1,989 observed updates. The lift moved downward
through the old boarding window 71 times, while the player remained short
of the X3038 position used in the passing comparison. The run ended at
video frame 20,076 and wrote zero captures.

Mesen receipt
`042335fa295b4f9e3e3d4720dd0de39a719dbd96b94d84d3c4fe01fef82e3699`.
Controller SHA-256
`1910ba1f1f864969b4ef31f1bd0526d01486c09c089ea9657fa1f40760710c0d`.

The optional timing replay approaches to X3014 on the solid stairs and
waits for the lift to rise through Y66–72 before moving Right again.
This tests the higher approach used in the passing comparison with the
existing lift at world X3040 on `14b0b4c2`.
The compiled controller SHA-256 is
`12648ca8d182e9f163fb5ad5165a2b8ce9211465f1323f7e0d0db1f034b7bfee`.

The timed Mesen run resumed walking at X3014/Y48 with the lift at Y72,
reached X3038/Y48, and boarded at lift top Y73. DK Jr. left the lift
at X3067/Y160 and reached the flagpole base with 56 on the timer. The
jump request at X3152/Y176 stalled at the base until time expired. The
run took 20,085 video frames. Receipt
`bf876f96414e6907d6c4651f3275aeb1dcda7ddbc2e689d024c3def15a1267a7`.
An earlier linked trace at the same position caught a late jump
intersecting the flagpole base before it gained height. [Earlier flagpole trace](dkjr-floor-entry-source-1114.md)

A component test on `14b0b4c2` parsed the actual flagpole terrain and
started the player on the approach. Six takeoffs between X3138 and X3148
stopped before the pole. Walking to X3152 with the camera settled at
X3072, then jumping, reached X3161/Y160 in the native flagpole slide.
The optional camera timing holds Right until that takeoff position is
available in the full replay. The compiled controller SHA-256 is
`58a101f58fdf628ae17d9cf1c1f1423c25cb22a699f07b0ddbef07821e3af441`.

The full Mesen replay with both timing changes passed on `14b0b4c2`.
DK Jr. rode the final lift, waited for the camera at X3072 and jumped
from X3152/Y176 with 55 on the timer. He cleared the flag and castle,
then completed 25 grounded original movement updates in 1-2 at
X40/Y176 with two lives. The run took 18,933 video frames and wrote
zero captures. Receipt
`0fcb4c740d491c870383e2088a0f44737e51ca4ab478f6ab0d3f6477cb0b0a04`.

## Shared character checks

Sonic and Super Sonic each defeated four Goombas with the spin, cleared
the flag and castle, and completed 25 grounded 1-2 returns on `14b0b4c2`.
Both finished at X40/Y176 with two lives. Mini Mario completed 48 standing
and 16 walking updates in 64 video frames on both ROMs. Every measured
Mini Mario frame had a controller read, with zero skipped NMIs.

| Character and run | Video frames | Mesen receipt SHA-256 |
| --- | ---: | --- |
| Sonic full 1-1 and 1-2 entrance | 5,411 | `4d48ea7af82073761a2097ab95a63ef31a7eb7768619dd3201d70f1c780e0dba` |
| Super Sonic full 1-1 and 1-2 entrance | 5,437 | `b10d8dfbba98f6dbbdc8da889ccbb43650e0dd95789bde15964564f946b18333` |
| Mini Mario opening, Downloads `28708fa9` | 64 | `208c35e9435ad956bf906f5f7fe134ccf1cf7cfb34e1bcdef2e503e534ddf078` |
| Mini Mario opening, private `14b0b4c2` | 64 | `0ea949314ac1f8c41671478b928ff2fe92bfd253f714ad1da5d4985d83cbc788` |

The installer verifies the exact 233 changed bytes through full-image
hashes and a reversible in-memory composition. It then checks the four
affected characters' opening cadence from the actual Downloads path.

## Downloads nightly

The installed MMC5 nightly is
`14b0b4c23baa1ff454d25720b0585dd45f7fa4179bbba6b7f38d68b6e0c141b5`.
The ROM in Downloads and the shared test ROM match the private candidate
byte for byte. The installer checked for automatic patches before and
after replacement and created zero backup files.

Each Downloads launch completed 48 standing and 16 walking updates with
no enemies in the opening. DK Jr. saved eight video frames over the
original 128-frame measurement, all during standing. The walking phase
still took 32 video frames for 16 updates. Mini Mario completed one game
update per video frame throughout the measured opening.

| Character | Video frames for 64 updates | Skipped NMIs | Downloads Mesen receipt SHA-256 |
| --- | ---: | ---: | --- |
| Donkey Kong Jr. | 120 | 88 | `f9fd3f2c8a605e35959bf8563534e16a9039ee9f9a606bdc2f68d6cfbf14b84c` |
| Sonic | 97 | 65 | `c9b324028ac71ef0a657d3064b2a4d2cd0722255dab138a7fb0bfb5a22d80b93` |
| Super Sonic | 97 | 65 | `0d2797452a5099c05fe59f8d3fcc105b19256f856d215abc507f26827113ee0d` |
| Mini Mario | 64 | 0 | `0ea949314ac1f8c41671478b928ff2fe92bfd253f714ad1da5d4985d83cbc788` |

The first install attempt rolled back because of a mistyped expected
receipt hash. The Downloads run reproduced the private DK Jr. and Mini
Mario receipts listed above.

## Follow-up DK Jr. terrain optimization

Offloading the Donkey Kong Jr. terrain request to its existing authenticated
entry produces candidate SHA-256
`94fa7a028ea86cc33eee50e9890e1eda05765bf6e8fd8fe82134a0388fa330db`.
It changes 78 bytes in PRG bank 33. The two changed spans occupy the existing
terrain hook and 28 padding bytes following the intact Giant Mario terrain
routine. Linked checks preserved the Giant Mario and Rogue Dawn readers,
the foreign caller results, and 442 IRQ and busy-NMI continuations. Linked
game updates saved 1,776 CPU cycles for DK Jr., cost 28 for Sonic and
Super Sonic, and measured the same for Mini Mario. Source receipt
`17642f0c193231827a3b75caa9f9ca81663be31938816488ecb751da8b1532d7`.

The private Mesen opening used 104 video frames for the same 64 game
updates, down from 120 on Downloads `14b0b4c2`. Skipped NMIs fell from
88 to 72. The 16 walking updates still took 32 video frames.
Private cadence receipt
`928876ca96c1db045f15332e6492e3a21c73b6e64630a41080d3fccdbc111e8e`.

Private full 1-1 passed the final lift. The controller then requested
Right+A from X3152/Y176 with the camera at X3072 and 54 on the timer.
DK Jr. returned to X3150/Y176 and ran out of time at the flagpole base
after 19,551 video frames. Receipt
`7b76392f38cf2730da56ec5766a23943ab0772d96b7875cbe40eb46b077d3a49`.
This run kept the candidate private while the flagpole timing was checked.

The next controller released all buttons, waited four game updates and
then used A without a direction. The actual input edge entered the original
jump state and raised DK Jr. from Y176 to Y165 at X3150 with 54 on the
timer. The 12-update observation expired during the rise. Receipt
`e3bf4b50d6e79ae2c454447c4f77cbed271469ed7274e546bb3d8d1b9e8f96a9`.
The longer observation reached X3150/Y161, then issued Right alone.
DK Jr. still returned to X3150/Y176 and timed out after 19,549 video
frames. The run confirms that the neutral jump can rise at the base.
It leaves the horizontal flagpole contact unresolved. Receipt
`914818c187977efd4f3e07c820df02e79ce600daead7ca6bc7544feb318134c2`.

The original jump reads its horizontal direction on takeoff and keeps it
until the landing. In a linked cold-opening test on `94fa7a02`, jumping
neutrally and then holding Right left DK Jr. at X43 throughout the jump.
Left, then neutral, then Right+A moved him from X43 to X58 while still
facing left. Receipt
`8d5156cb7bd70a7d22059a2164cd0035579e2aceda8f24a34ece1d01836c3e78`.
A separate linked fixture used the parsed flagpole terrain at X3150.
The forward-facing jump hit the base, and the backward-facing jump
reached the flag slide at X3161/Y160 with both lives. The native
replay waits for X3150 before turning left and taking off.

The full private Mesen replay passed with the backward-facing jump.
DK Jr. released Right and settled at X3150/Y176, turned left at
X3149, then jumped toward the pole with Right+A. He had 54 on the
timer at takeoff. He cleared the flag and castle and completed 26
grounded source movement returns at X40/Y176 in 1-2 with both lives.
The replay used 18,495 video frames and saved zero captures. Receipt
`ca794b5ef7aeff1691c16246c3f665fc594033538a873d6db9dd551924dd728a`.
Controller SHA-256
`191bcef97c3a55e3c804e366ffd1376a759d8d23b45ffe7ba86b6ef3bca1af1c`.

Sonic and Super Sonic each defeated four Goombas by spinning, cleared
1-1 and completed 25 grounded movement updates in 1-2 with both lives
on the same private candidate. Sonic used 5,415 video frames and Super
Sonic used 5,438. Mesen receipts
`b0accb408b3b0f5a462b6ae195c9555c5e520fcc0057dc45256823e9e9ff73e6` and
`467576a927314bdf8d35cbf278b001ea4883544f1d6ac64ef7a2e8d4210671a1`.

The next terrain-dispatch change could save about 2,464 more cycles per
game update by reusing the existing epoch check for the four side probes.
Even with that estimated saving, walking would remain above a frame's
CPU budget in the linked profile. This is a design estimate.

## November 23 Downloads delivery

The Downloads MMC5 nightly is now
`94fa7a028ea86cc33eee50e9890e1eda05765bf6e8fd8fe82134a0388fa330db`.
Its bytes match the private full-route candidate and the shared test ROM.
The same-name patch guard passed before and after installation. There
were zero backup files or captures.

| Character | Video frames for 64 updates | Skipped NMIs | Downloads Mesen receipt SHA-256 |
| --- | ---: | ---: | --- |
| Donkey Kong Jr. | 104 | 72 | `928876ca96c1db045f15332e6492e3a21c73b6e64630a41080d3fccdbc111e8e` |
| Sonic | 97 | 65 | `98a64094a8e0118e3315b9bb36df0fc14769070f3584464ae6911ac3480a965d` |
| Super Sonic | 97 | 65 | `845bbd1a00affb2f593ca694ea6554e5f69df852761c16d345646e2f7ea43ea2` |
| Mini Mario | 64 | 0 | `8b2c061a8d0f8fa4792da0a3ca9f768209036c616c5a52709d06d2e948dc7322` |

Each sample included 48 standing and 16 walking updates. DK Jr.'s
standing phase needed 16 fewer video frames. Walking still needed
32 video frames for 16 updates. The other three results matched the
prior nightly's cadence.

## Faster authorization for DK Jr.'s terrain probes

Private candidate `3af597a7` reuses the existing epoch check for DK Jr.'s
four side probes and calls the original terrain routine directly on a hit.
An epoch or header mismatch still enters the public validation path. The
adapter preserves X across the fast check so a rejected request returns
the caller's X. It changes 47 ROM bytes and adds no RAM.

Linked execution saved 605 cycles per side probe and 2,420 cycles per
game update for DK Jr. The sampled walking update dropped from
43,736 to 41,316 foreground cycles, with 4,369 logical NMI cycles in
both runs. The Sonic, Super Sonic and Mini Mario samples had identical
state and cycle counts. The verifier also exercised 199 native IRQ and
199 busy-NMI continuations. Linked receipt
`9f167ca529c096be372027ff95c5555b4a11d218d669f281084cecf6c3b13d6f`.

The Mesen comparison held Right for the same 16 game updates.
Both runs advanced from X40 to X50. The installed build needed 32
video frames and the candidate needed 24. The 48 standing updates
took 72 video frames in both runs. The complete opening sample fell
from 104 to 96 video frames and from 72 to 64 skipped NMIs.

Candidate Mesen receipt
`b1f4e616bd425fbc602eaf5502eb94828cd1c6a78df962a9dfce38e925198f15`.
Controller SHA-256
`f367dc94cfd375355355fdc75a3cc570b5aaed788b83e028389156b34e4c4c64`.

The full Mesen replay on those bytes cleared 1-1 in 17,631 video
frames and completed 26 grounded movement returns in 1-2 with both
lives. The final lift and backward flagpole jump both worked. Full
stage receipt `a010886cbbad8412a630c7fb505f34f6b65c71e97473f58d703a91a5b34a5aea`.

The Downloads nightly now matches `3af597a7`. The automatic patch
guards passed before and after replacement. When Mesen launched the
installed file, DK Jr. matched the private opening receipt exactly.
Sonic and Super Sonic each took 97 video frames for 64 game updates.
Mini Mario took 64 frames with zero skipped NMIs. There are no backup
ROMs from this delivery.

DK Jr.'s Mushroom still needs a passing playtest. From the first lift,
his head contacts the underside of the brick at X384 and stops the jump
without triggering a block effect. The later powerup block at X1248 is
out of reach from the floor with his existing jump. Both observations
come from linked controller replays against `94fa7a02`. Receipts
`8c174c814e35571dfad8de57490184993051140dffda1fbc2d2f4e09c55d1ba8`
and `e3211c07ae4cf0f30092ca278a861e83ddfa745c720c389fb1a224df66f80fcf`.
The next check is whether an actual underside collision can trigger the
standard block effect without changing the jump or the stage route.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/dkjr-side-forwarder-1123 --max-files 1 --timeout 600 -- python -B tools/audit/check_dkjr_public_side_forward_1123.py
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 210 -- python -B tools/audit/run_dkjr_dispatch_native_1123.py --public-side-forward --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 320 -- python -B tools/audit/run_dkjr_dispatch_native_1123.py --public-side-forward --full-stage --time-cap-approach --center-flag-takeoff --backward-flag-hop --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 570 -- python -B tools/audit/run_dkjr_dispatch_native_1123.py --public-side-forward --sonic both --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 420 -- python -B tools/audit/install_dkjr_side_forward_1123.py --install
python -B tools/audit/run_bounded_build_v1.py --output build/dkjr-side-epoch-fast-1123 --max-files 1 --timeout 600 -- python -B tools/audit/check_dkjr_side_epoch_fast_1123.py
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 240 -- python -B tools/audit/run_dkjr_dispatch_native_1123.py --fast-side-epoch --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 320 -- python -B tools/audit/run_dkjr_dispatch_native_1123.py --fast-side-epoch --full-stage --time-cap-approach --center-flag-takeoff --backward-flag-hop --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 520 -- python -B tools/audit/install_dkjr_side_epoch_fast_1123.py --install
python -B tools/audit/run_bounded_build_v1.py --output build/dkjr-sonic-combined-dispatch-1123 --max-files 1 --timeout 600 -- python -B tools/audit/check_dkjr_sonic_dispatch_1123.py --interrupts
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 360 -- python -B tools/audit/run_dkjr_dispatch_native_1123.py --combined --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 575 -- python -B tools/audit/run_dkjr_dispatch_native_1123.py --combined --full-stage --baseline --cap-trace --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 575 -- python -B tools/audit/run_dkjr_dispatch_native_1123.py --combined --full-stage --cap-trace --time-cap-approach --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 575 -- python -B tools/audit/run_dkjr_dispatch_native_1123.py --combined --full-stage --cap-trace --time-cap-approach --center-flag-takeoff --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 600 -- python -B tools/audit/run_dkjr_dispatch_native_1123.py --combined --sonic both --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 220 -- python -B tools/audit/run_dkjr_dispatch_native_1123.py --combined --mini --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 450 -- python -B tools/audit/install_dkjr_sonic_dispatch_1123.py --install
```
