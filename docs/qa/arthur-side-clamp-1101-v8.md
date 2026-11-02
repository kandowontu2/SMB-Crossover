# Arthur source side-clamp correction

Private candidate: `build/arthur-side-clamp-1101-v8/candidate.nes`, SHA256
`8be03441c6f5503acb3d001e76fbcc1d82a0fc4967c856c2eda763eba2d09806`.
Base is installed Shinobi v30, `6f319d2039f920bc85e4a6bfe6ee3327996b42020e03c09e671142eada2a6428`.
This note initially records CPU qualification and prepared native packets;
installation and native outcomes are not implied.

The genuine first-flower controller exposed a wall displacement on the base.
`build/arthur-natural-flower-1101-v6/diagnostic/capture/displacement.csv` records
frame 984: world X305 → X289 at Y130, physical bank10 PC A2BD, R0=1,
R4=1 and R5=65 (world probe321). The flower had matured, lives remained2,
and the controller had not collected it. This is a controller-earned negative,
with a read-only first-write observer.

GNG original fixed-bank calls DF69→E9F1 and DF79→EA01 query native X±8.
Arthur's importer maps native X to host X+8, so its existing host side points
0/16 are authentic. The shared wall clamp's 1/14 geometry disagrees with those
points. At X305 its right formula gives289. Arthur's matching right separation
is `(worldX & $FFF0)-1` =303; its left separation is
`(worldX & $FFF0)+16`. Both retain 16-bit page carry/borrow.

The successor occupies exactly the existing 215-byte
`SamusStopAtWallBanked` span, physical PRG10 A290..A367 (half-open), file
82592..82807. There are196 changed bytes; every other ROM byte is identical.
No PRG/CHR/RAM allocation, helper, dispatch edit, source-probe change or new
storage is needed. `NativeGuest` remains A29D and `SamusHeadProbe` remains A367.

`tools/reference/arthur_side_clamp_1101_v8.s` is the durable owning source.
The recipe first reproduces the original installed215 bytes exactly.
Shared foreign probe arithmetic carries an intermediate through Y/stack while
retaining both SmTempX/Page outputs. Shared velocity/fraction cleanup and the
existing left-away guard fund the exact-ID32 correction. The selected-byte load
also covers Ryu's genuine `NativeGuest` entry, whose incoming A need not be an
identity. Arthur's two equality branches establish C=1 for SBC#1 and ADC#15;
the intervening LDA/AND preserve that carry.

`CPU.json` passes2432 foreign public-entry comparisons,1520 foreign
`NativeGuest` arbitrary-A comparisons,10240 Arthur16-bit/flag cases,
480 original left-guard cases,1248 non-gameplay-engine wrapper comparisons,
216 original GNG side-point cases and192 IRQ/lag-NMI cuts across96 reached
worker boundaries. Foreign application RAM, SmTempX/Page, WRAM, AXYP, live
stack, SMC and mapping contracts match. NativeGuest's actual Y=R0=side contract
is explicit. Foreign wall-call CPU changes range−2..+26 cycles; this is not an
idle/walk throughput measurement.

`callers-CPU.json` additionally passes96 comparisons through the real original
`RyuSourceSideDispatch` and192 reached NativeGuest calls, preserving Y=R0.
Those natural caller fixtures observe incoming A0; the separate direct cohort
covers A0/19/32/128/255. `candidate.json` contains the exact byte delta and
bindings. Candidate DBG procedure-local addresses are updated; external
addresses are retained. Scoped aliases are added to the inherited LBL, whose
old unscoped local names were already ambiguous across physical banks.

Reproduction uses the bounded runner and the single task root:

```powershell
python tools/audit/run_bounded_build_v1.py --output build/arthur-side-clamp-1101-v8 --resume --timeout 180 -- python -B tools/audit/prepare_arthur_side_clamp_1101_v8.py
python tools/audit/run_bounded_build_v1.py --output build/arthur-side-clamp-1101-v8 --resume --timeout 300 -- python -B tools/audit/check_arthur_side_clamp_1101_v8.py
python tools/audit/run_bounded_build_v1.py --output build/arthur-side-clamp-1101-v8 --resume --timeout 180 -- python -B tools/audit/check_arthur_side_callers_1101_v8.py
python tools/audit/run_bounded_build_v1.py --output build/arthur-side-clamp-1101-v8 --resume --timeout 180 -- python -B tools/audit/finalize_arthur_side_clamp_1101_v8.py
```

Root owns the emulator queue. The unchanged first-flower route is prepared
under `flower/`; the unchanged previously qualified full1-1 stair controller
is under `full11/`. Both are read-only/controller-only, bounded to four PNGs
per run, with no outcome seeds or helpers. This agent launched no Mesen,
installed nothing and made no Git commit.
