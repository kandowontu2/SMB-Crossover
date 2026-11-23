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

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/dkjr-sonic-combined-dispatch-1123 --max-files 1 --timeout 600 -- python -B tools/audit/check_dkjr_sonic_dispatch_1123.py --interrupts
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 360 -- python -B tools/audit/run_dkjr_dispatch_native_1123.py --combined --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 575 -- python -B tools/audit/run_dkjr_dispatch_native_1123.py --combined --full-stage --baseline --cap-trace --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 575 -- python -B tools/audit/run_dkjr_dispatch_native_1123.py --combined --full-stage --cap-trace --time-cap-approach --run
```
