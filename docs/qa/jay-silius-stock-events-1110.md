# Jay McCray stock gun and scripted contact

The test parent is `b031802c7bc4f4e9596683e66f2f53c124b3a3ac155b80bbec03c5965b8e4e65`.
Applying the existing resident Jay link in memory gives
`fedcc6eef6d7b6634842872634feee5e3da57517b0c43fd86c07439ac9466454`.
The source recipe verifies the DK Jr. four-pipe change before applying the
3,307 disjoint Jay changes. The original donor is Journey to Silius (USA),
SHA-256 `12f5c5e413a2aa5bff75b5077e4477497d7e49aa432560c2e8c3fd3cc71910cc`.

## Original behavior

The 334-byte binding uses RAM3 `$B000..<$B14E` and has SHA-256
`1909dffc4da48b29bf6ab2558566578ce5c2a7698a45f15f2b27ee1667464533`.
The frozen movement import at `$B000` jumps to `$B006`. The three event
callers use `$B003`, which jumps to `$B0E2`. The stock projectile records
use C2 `$C080..<$C0B0`. The primary hurt timer and four saved-actor fields
use `$C0B0..<$C0B5`. These fields start zero through the original compact
worker's first-page initialization.

| Service | Exact donor code used |
|---|---|
| Stock input | Bank 6 `$81D2..<$81EA` cooldown and selector, row 0 `$844E..<$8480` |
| Shot creation | Bank 6 `$A387..<$A39C` three slots, `$8E39..<$8EA7` original position and stance tables |
| Controller and dispatch | Fixed bank 7 `$C86E..<$C878` new-button calculation, row 0 ABI of `$CD36..<$CD4C` |
| Hurt event | Fixed bank 7 `$EA06..<$EA6E` primary and saved actor gates, HP subtraction and source sound |

The stock gun uses a new B press and checks slots `$F0`, `$E0`, `$D0` in
that order. A successful press sets a four-update cooldown and sound
request `$12`. The source sets horizontal speed to four pixels per update
with the original facing sign. The original X spawn offset is 12 pixels
in the facing direction. Y is one pixel up or eleven pixels down on the
grounded crouch path. A full pool and held B produce no new projectile.

The paired checker executes 768 stock cases and 768 hurt cases on the
actual donor and relocated instructions. It compares AXYP/SP, all linked
actor fields, all three projectile records, and foreign host state. Seven
non-stock values safely decline in the proposed bridge. Eight directed
cases execute the original scripted position caller through `$B003`.
Accepted cases deduct 16 HP and select sound `$23`. Blocked damage retains
the caller's `$24` sound and leaves HP intact. Reached event instructions
pass 46 actual NMI and 46 IRQ cuts.

## Resident cold and controller

Appending the binding to the movement stream would need 2,331 bytes in the
existing codec, 283 more than the two-page carrier. The existing Jay art
page 216 has a source-owned blank tail at offsets 640 through 1023. Its
2,048 actual `JnSetPose` calls use eight body records and physical tiles
0 through 31. The finite audit retains 88 selector domains, 49 exact
current tables, four native mapper mirrors, the current Zelda alias and
the separately qualified Final Fantasy writer rebind. The native weapon
reader with a `$D8` table row selects page 217. The full first 640 bytes of
Jay art remain exact.

The resident result is
`3a33b18029329f54dcc52c62f3a3563caffc59608c9c802680e117ea6f4bb6d2`.
Its full cookie is `a71020049c0d4ea4a38ff2855a80ac86`. The actual compact
worker reads the existing pages 331 and 332 and a third row, page 216, to
C2 `$D800`. The 2,044-byte movement stream calls the 40-byte shim at
C2 `$DBCE`. It copies and verifies the 334 binding bytes from `$DA80` into
A3 `$B000`. The caller commits both full headers after readback. The
151-byte cold resident fits its existing 162-byte extent. The tail uses
374 of 384 bytes. The new carrier's only edit envelopes are PRG65, PRG94,
and CHR216, 331 and 332. It preserves the DK Jr. and Sonic payloads.

Cold load takes 6,150 PPU reads and verified warm load takes zero additional
reads. All 32 individual header-byte faults reload. Seven directed C2 and
A3 transfer faults leave both headers invalid. The reached shim passes
16 actual forced-blank NMI cuts while executing with IRQ masked.

The real title-to-Jay CPU controller opens 1-1 and runs 44 ordinary Main
updates with the naturally loaded bindings and no post-cold state writes.
B rising edges are 4, 14, 24 and 34. The first three create source
projectiles and the fourth meets a full pool. Jay ends at X40/Y176 with
both lives and zero Mike shots. Reached stock instructions pass 84 actual
NMI and 84 IRQ cuts. The earlier detached RAM case repeats these same
controller results with attachment after the genuine two-page cold load.

Projectile flight, tile and enemy impacts, display, host audio and injury
publication, the donor's hurt countdown, and the five alternate weapons
remain open. The source shot records therefore remain occupied in this
fixture. The scripted contact controls are directed CPU cases. This work
creates no ROM, Mesen run, capture, or generated build file.

Run the bounded source checks from the workspace.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/jay-silius-stock-events-1110 --max-files 1 --timeout 600 -- python -B tools/audit/check_jay_silius_stock_events_1110.py
python -B tools/audit/run_bounded_build_v1.py --output build/jay-silius-stock-carrier-1110 --max-files 1 --timeout 600 -- python -B tools/audit/check_jay_silius_stock_carrier_1110.py
```

- Binding source SHA-256 `e6b1fcf1ff10c786b7091b894db61c8193d7603ea4c5ea13eeb1d6709ad607e1`.
- Binding checker SHA-256 `b6b3388c625ab2e627165991f7e45e56af3ffd7cb4092aa432eb1b92fc34e279`.
- Copy source SHA-256 `9439259e94ddd72c8f3a61f77e22732a2bed313eb4a264240445f3da56677fe6`.
- Carrier checker SHA-256 `50024a46601b5eb563abb6cfd5d5574d63f545f70e64123cef6126fb08288a8b`.
