# Jay McCray stock bullet live draw dispatch

The source check reconstructs exact parent
`3d327d47b8127c1e76d9868191d34b8ebb1ca9ec29d6bb609ccab9c60c6cb3d8`
through the retained Sonic and DK Jr. recipes. It reproduces the
[impact and sprite image](jay-silius-stock-hit-draw-1111.md) and composes
live draw image `a2c36ff819a2f897dd58baec3df0ca3f397cac0f65133e03aa8101667a661d96`
in memory. The full cookie is `a7102007de73e237c21c140b1055419b`.
The live Downloads image had advanced and remained untouched.

## Native dispatch

The original `JnDraw` entry stays at A98 `$A91F`. Its original shots,
world items, drops and HUD keep their existing order. The 47-byte Jay
hook runs before the HUD and only admits the Jay alternate. Twelve
branch relaxations, seven source-declared NOPs and a five-byte reduction
from using the fixed `$80C2` mapper setter provide 48 bytes inside the
existing 402-byte envelope. The only displaced external entry is
`JnBatRecordSelected`, whose two real JMP operands at `$AC80` and `$AC8E`
now target `$A9A7`.

The existing A94 gate at `$B27F` checks both full 16-byte headers. The
real `FarCallCommon` stack supplies caller bank `$E0` for movement or
`$E2` for drawing. Both enter the typed A3 mux at `$B303`. A draw
rejection returns to the original HUD path. Movement rejection retains
the existing native fallback. The gate uses 128 of its 129 source-owned
bytes. It needs no extra public owner flag or mapper bypass.

The hook reads the native body length from C97 before the authenticated
map change. The private drawer budgets each 4-byte stock cell against
the space needed for that body. It uses the real `MetaspriteRenderLoop`
for clipping and rotation. The C2 guard also checks active scene,
pause, busy Main, fixed camera and the same movement epoch. The revised
CHR218 prefix still verifies the copied payload and now transfers 938
bytes. The donor art and original projectile update remain exact.

## CPU verification

A controller-only Jay selection runs 60 ordinary 1-1 Main updates with
one new B press. All 60 movement and 60 draw calls use the authenticated
private mux. The stock shot produces 50 native OAM cells and the regular
NMI performs 50 matching `$4014` DMA publications with CHR216 selected.
The first is `B7 28 00 34` at update 4, projected X56/Y191. The last is
`B7 28 00 F8` at update 53, projected X252/Y191. Both lives remain and
no Mike weapon is created.

The reached production paths pass 172 actual busy NMIs and 172 actual
scanline IRQs, including the existing mapper-shadow split repair. All 32
individual header-byte faults decline the draw without entering A3 or
calling legacy movement. Ninety-six directed capacity cases cover null
and sized body records, both facings, rotation, alignment and available
space. Six scene declines and two stale-frame declines stay empty.

Mike Jones and Steve Hermann each match 60 actual controller updates
against the previous image, including native state, OAM, VRAM and maps.
Another 312 direct native draw pairs compare all 13 existing weapon
kinds across both alternates, facings, velocity signs and selected ages.

This is CPU-model verification on exact 3d32. Physical rendering,
full-stage traversal, and the donor's alternate weapons remain open.
The source checks wrote no ROM, capture, or generated build file and ran
no Mesen.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/jay-silius-stock-draw-dispatch-1111 --max-files 1 --timeout 600 -- python -B tools/audit/check_jay_silius_stock_draw_dispatch_1111.py
```

- Source SHA-256 `82e977043bd3525857ddab654f93d652f2587da36dc84e8af3ca2e1c4bf4db93`.
- Checker SHA-256 `462e672303f1b0fd1d9e912ed2d88399409750b9fd148011a3e5be85f59e744b`.

## Released Sonic parent

`check_jay_stock_draw_sonic_rebase_1111.proposal(raw)` takes exact released
`8c1ebb1bfbe21499461c5fd65ea75b784460ac2cb81a712a9db9941aa7cec711`
bytes and returns the combined image and CPU metadata in memory. The
recipe verifies both directions of the Sonic predecessor and reproduces
the exact Jay source image above. All 4,717 Jay changes are disjoint from
the 49 Sonic changes. The combined SHA-256 is
`6cb828b3c97bd287f5fb3421e01a478319bf3615e5f2eeed8a6b7888b15c9657`.
Jay's full cookie remains `a7102007de73e237c21c140b1055419b`.

The combined image repeats 60 ordinary Main and 60 authenticated draw
updates, 50 native DMA publications with CHR216 and both lives. The
first and last stock cells again match `B7 28 00 34` and `B7 28 00 F8`.
The replay also repeats 172 busy NMIs, 172 scanline IRQs and the single
mapper-shadow split. This is the CPU proof for the combined image.

Jay is the first Select alternate of Mike Jones, row 2 column 8
(cursor slot 15). Confirm with Start. The CPU witness holds B on
ordinary updates 4 through 19, counting from update 0. Inspect stock
slot `$F0` in physical WRAM2 offsets `$A0..$AF`, actual `$4014` DMA
OAM, and the CHR216 latch after the regular NMI. The projectile retires
on update 54. Hardware testing can count completed ordinary updates
independently from elapsed video frames.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/jay-stock-draw-sonic-rebase-1111 --max-files 1 --timeout 600 -- python -B tools/audit/check_jay_stock_draw_sonic_rebase_1111.py
```

- Rebase checker SHA-256 `4cf760b308e3d27509e3ccf3b99441f6a5b5741d03a484769f0d984b01d03167`.
