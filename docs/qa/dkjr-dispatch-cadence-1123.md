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

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/dkjr-sonic-combined-dispatch-1123 --max-files 1 --timeout 600 -- python -B tools/audit/check_dkjr_sonic_dispatch_1123.py --interrupts
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 360 -- python -B tools/audit/run_dkjr_dispatch_native_1123.py --combined --run
```
