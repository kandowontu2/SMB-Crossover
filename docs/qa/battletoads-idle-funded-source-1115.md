# Funded Battletoads idle source image, November 15

This is source-model qualification only. Root owns the native queue and all
physical candidate, Downloads and delivery actions. No ROM, capture, build tree
or receipt file is emitted by these gates.

The exact parent is installed `7a80f0f37e316436be0825bbd6fd9d372af6b0b7741f84ea87356282033d9b79`.
The source image is `a90cf06bdad6778a5b01927af5bfe175fcf5dd391f52d4f8877ce622628bdde9`.
Root's source-only lease is
`allocations/battletoads-idle-funded-source-1115.json`, SHA256
`676a61814f6571eada48a51f3ac350702e45d7248eb7a90817354d554e8f00d0`.
It grants nine envelopes totaling 556 bytes, with 535 actual changes. All other
7a80 bytes remain exact, including the Gimmick 191-byte correction, Prince
packet, prior BT cache/cookie/full BtCheck, score table and earlier fixes.

The frozen proposal remains `research_battletoads_idle_funding_1115.py`, SHA256
`c43361c1d8e0e9c2f88748686170f5b73a012df83f4fc3ee2927e82a5d3d6c47`.
Its framed old/new arrays pin is
`295e9408740ad58b4a36ccd558b0a72806cebf14461d3a88cc34f0317c6adb9a`.
The companion frozen funding QA remains unchanged. The new composer is
`compose_battletoads_idle_funded_1115.py`; `proposal(parent)` returns bytes and
ownership metadata in memory. `inverse(image)` restores exact inline 556-byte
source preimages, checks the complete 7a80 hash, and validates the proposal
roundtrip without reading mutable Downloads. `load_current_image()` accepts only
exact installed 7a80.

The accepted source contract allows only residual farcall operand differences
at `$0162/$016C/$016D` at the native getter return. Their owning callers publish
fresh arguments before use; snapshot tails transport them opaquely. Main
boundaries still require complete SMC equality. After actual BtRetire the native
getters intentionally return Y0/C1 instead of the old rejected Y91/C0. This does
not authorize private code with an invalid cache or a blanket RAM/fault mask.

Run the new checker through the bounded runner, for example:

```
python -B tools/audit/run_bounded_build_v1.py --output build/battletoads-remaining-idle-1114 --max-files 1 --timeout 600 -- python -B tools/audit/check_battletoads_idle_funded_1115.py strict
```

The same absent output root is reused; every invocation has zero generated
files. Modes are `strict`, `foreign`, `units`, `constructors`, `profile`,
`profile-short`, `lifecycle`, `interrupts`, `rash`, `zitz`, and `metadata`.

Terminal gates so far:

| Gate/session | Actual scope | Receipt |
| --- | --- | --- |
| identity 77413 | 9 exact spans,556 owned/535 changed, whole source image pin | candidate pin above |
| strict 20989 | portable inverse/roundtrip with Downloads reads forbidden;20 wrong/dirty rejections; ordinary Lua compilation | `e90382d97cdb54df8fad2f7d6b7c1989f224cf62166eb61155f806060001bbb7` |
| foreign 29709 | 39,160 mounted public-selector endpoint pairs;all256 owners/36 services/four status corners, raw33 getter cases separately reserved; exact AXYP/SP/live RAM/physical RAM/maps/SMC,minSP219 | `95d2efc3dbe6f0a7b94e98ade49c393c203be760235c2c073d8cb09f0e44c827` |
| units 47966 | 512 complete Adder and512 complete Box calls;all128 validP/fourXY;exact AXYP/SP/RAM/maps/VRAM except only0162/C/D;983/978 cycle savings,minSP181 | `7cec03a9570115c4e2691f21cfe3fe11fc603a22990b1cfadf2e2df97a5a2f70` |
| constructors 52920 | 768 actual Gimmick/DK/Rash menu/fullFarCall continuations;all128 validP/twoXY;exact AXYP/SP/live RAM/SMC/physical RAM/VRAM/maps,minSP152 | `e86050454e1b338ce27ea561ec1a2234fa9724332d384ad13444efab2d092994` |
| mounted profile 18140 | 48 idle and32 Right;one actual GameLoop entry/return per iteration;Main RAM/SMC/VRAM/maps exact;AudioUpdate once/Main,minSP192 | `b3ac8e201568bd48d08f61ce48ead65ca7da6fa76ede6c52e8360c5b0683ab52` |
| lifecycle 71542 | actualcold/walk8/pauseedge/64paused/resumeedge/resume8;actualBtRetire;34 native getter admissions and68 private/NoOp invalid-cache rejection parity cases;owning DeathStart+8Main engine11/lives2 parity | `d59bb3707de6b486860091ee4a6f04c0e8409b3051955673b474e6bdcff1087e` |
| Rash full route 57244 | ordinary frozen Luae470;4003 actualMain entries=returns;2863 BTsteps/58 next;flag2805/castle2868/entrance3406+25 grounded1-2;HP43/lives2 | `8ea7948cd8ba8096f7023d2ded7fb13d5fb37eb4dfdc48244acd7fe2acdc4a1c` |

The actual mounted profile saves exactly1966 source cycles on every sampled
Main: idle27528.0625→25562.0625 and Right27788.5625→25822.5625. Each Main still
calls AudioUpdate once. Private BtRouter entries fall7→5 and BtCheck calls5→3
because the two admitted native getters execute no private code. Full BtCheck
bytes and the remaining calls are unchanged. No active actors were present;
HP47/lives2/power0/Star0 retained, idle40/176 and Right83/176. This is source CPU
cost evidence; regular NMI cost and real physical controller reads require
separate native measurement. Literal-read lag is still open.

Harness negatives are retained as test evidence: profile 27148 compared all48
idle Main state boundaries successfully, then incorrectly required private
router/check call counts to stay unchanged. Profile95305 investigated the
replacement count assertion. Units8296 stopped at a missing `SP` receipt key:
`N.invoke` itself asserts SP224 but omits it from its compact result. The checker
now explicitly uses that guaranteed SP for its comparator. These are not game
defect findings or terminal qualification receipts.

Profile86890 showed the expected call counts and1966 saved cycles on two idle
updates, then exposed a second harness error: the guard entry counter included
all BT services instead of only12/13. Profile18140 uses the corrected filter.
ISR86053 initially assumed no physical RAM changes, and ISR94371 identified
initial-menu busy-NMI CHR publication from zero latches to native world pages.
ISR29478 exposed that these globally observed constructor CPUs included legacy
F11 metadata-generation menus, not only mounted candidate execution: resuming
an old B8BF snapshot against the relocated candidate produced a BRK. ISR90420
filters exact owning raw object identity and records each actual caller's
endpoint instead of guessing it. The earlier ISR jobs are harness negatives,
not candidate ISR qualification. Native handler effects must match the exact
unmodified-parent oracle, not be discarded or masked.

Rash's source controller receipt is
`de765e6a5d1b79a780680e2f4ae01e3bf873c9a0581c3798adf23500628c78c3`.
Its source-only terminal is40/176/high1/native0/engine8/HP43/lives2/power0/Star0.
The scheduler's4002 frame labels are model callbacks, not physical Mesen frames.
No source timing or HP outcome is transferred to a native run.

The root-only replay API is `replay_battletoads_idle_funded_1115.controller(image,
key)` (`rash`/`zitz`) and `.cadence_reads(image)`. It preserves the frozen ordinary
route/read-observer body and replaces only the pinned configuration. LF Lua pins:

| Controller | SHA256 |
| --- | --- |
| Rash full1-1/25 grounded1-2 | `e470fcbcd639fe09318d87f502ca0e6a9926ab828f4efa215a0c0584c495b46a` |
| Zitz full1-1/25 grounded1-2 | `c7d217eafbf91a673864dc89e36dcd9b9d40a319c4fac7671082f67fa6b82220` |
| literal4016/4017 reads, idle48/Right32 | `bbee821d0038d4074b36747ce743636b2fc643e946f25dd659538294e131963e` |

Actual mounted reached ISR and the Zitz source full route remain pending.
No native speed, cadence, zero-lag,
natural-death/respawn or delivery claim is made.
