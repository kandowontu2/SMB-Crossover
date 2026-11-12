# Steve Hermann throw carrier

The audit pins the installed lift build `235de3ed2487cd3f93c695e1eb2ceec55c172cede3cb6d98c5309afbc7cfbe38` and layers the throw carrier on the qualified pose fixture `4bbc4011db1648eef85cd7d591255e85d4d0d691bb68e5073545be04cc5d4dd2`. The combined fixture is `b29210a30d7d7b16cbd3937e0bce6ceb6aacab2ac2c22739b9c553e685f00317` with cookie `a710200a0f0115156b4bc9163cd50ad2`.

## Storage and binding

| Region | Qualified use |
| --- | --- |
| Raw2 `$D800–DA4D` | 590 relocated throw code bytes. `$DA4E–DA7F` leaves 50 bytes in the same prefix. |
| Raw2 `$CD00–CD7E` | The 127-byte cold loader with both pose and throw rows. |
| Raw2 `$CD80–CDBF` | The 64-byte direction table. `$CDC0–CDFF` leaves 64 bytes in the same loaded row. |
| Raw2 `$C969–C97F` | 23 bytes after the lift fields, already zeroed and verified by the existing state initializer. |
| Physical CHR306 | Full 1 KiB row carrying the new `$D800–DA7F` prefix and an exact copy of the existing `$DA80–DBFF` suffix. |

The existing common decoder returns before the new loader copies and reads back CHR306 to `$D800–DBFF`. It uses the existing verified row transfer. The duplicate 384-byte suffix preserves the live punch and draw code, and physical CHR220 retains its art and code bytes. The common owner commits both cookies after successful readback. The pose row still finishes at `$CE00–CFFF`, and the Laserbot and lift rows still occupy `$D000–D7FF`. Raw3 matches the pose parent outside the cookie.

Roll's pool 4 and 5 slot 6 requests move from blank CHR306 to byte-identical blank CHR304. PRG79 `$B06F–B074` at file offset `$9F07F` changes from `18 69 02 A2 01 EA` to `C9 31 90 02 69 01`. The preceding physical setter preserves X at 1, allowing the replacement to use the same span. The compiled publisher still requests the original pages for pools 0–3. The six pools and four incoming processor statuses produced 24 matching publisher comparisons, including 72 byte-identical requested page pairs.

| Exact preimage | SHA-256 |
| --- | --- |
| Loaded raw2 `$D800–DA7F`, equal to physical CHR220's first 640 bytes | `70df09cf8f2218661222f42ef4224a610238aa5ba2fa77239ae9b88e23296fa7` |
| Loaded raw2 `$DA80–DBFF`, equal to physical CHR220's final 384 bytes | `e0c86b96c1843e29e8ceb5ba6f043b445c00e0b14deb066a5b93e75d663d6c7f` |
| Loaded raw2 `$CD80–CDFF`, 128 bytes of `$EA` | `e9052613918860901206e1ff27591636df1d731e5740246e59941e562878730b` |
| Loaded raw2 `$C969–C97F`, 23 zero bytes | `015275e61fa0d0751c1d9f45541c7804c895404455470710ade3786f282f2da0` |
| Physical CHR304 and CHR306 before the edit, each 1,024 zero bytes | `5f70bf18a086007016e948b04aed3b82103a36bea41755b6cddfaf10ace3c6ef` |

The standalone audit exposes `mount(image, info, code, data, pose=True, extra_edits=...)`. `detached(donor)` demonstrates relocating the existing throw assembly into the two regions. The loader addition lives in `tools/reference/steve_shatterhand_throw_cold_1111.inc`. The audit leaves the shared pose and late-loader source files unchanged.

## State fields

The proposed bindings below fit within the qualified zeroed range. The detached core can reuse the existing companion position, facing, age, orbit vector, and lift robot animation fields.

| Address | Proposed binding |
| --- | --- |
| `$C969–C96C` | `SteveThrowSelector`, `SteveThrowTimer`, `SteveThrowSpeed`, `SteveThrowAux` |
| `$C96D–C96F` | `SteveThrowAim`, `SteveThrowAnimAux`, `SteveThrowSound` |
| `$C970–C973` | `SteveThrowCameraX` and `SteveThrowCameraY`, two bytes each |
| `$C974–C976` | `SteveThrowQuadrant`, `SteveThrowContact`, `SteveThrowHealth` |
| `$C977–C97F` | Nine bytes left in the qualified state range |

Cold initialization zeroed all 23 bytes. A warm call kept a state canary and performed zero additional PPU reads. The live bridge still owns reset and retirement within an already-authenticated scene.

## CPU verification

The warm-footprint probe instrumented CPU bus reads and writes only when raw bank 2 was mapped into the `$C000` window. It classified access as warm only when both complete cookies matched. On the exact installed build, Mike, Jay, and Steve each entered active gameplay and ran 80 input updates. The existing Steve route earned three Alpha tokens and completed the lift with 21 upward steps. Jay completed the native 1-1 flagpole and castle sequence and earned the 1-2 machinegun with five matched DMA cells. These routes made zero warm reads or writes to `$D800–DA7F`, `$CD80–CDFF`, and `$C969–C97F`. The Steve lift made 595 warm reads at `$D756–D776`, confirming that span remains live. This is route coverage rather than a claim about every possible stage or state.

The carrier fixture passed 58 forced-blank lag-NMI instruction cuts. Five injected readback faults at `$D800`, `$DA7F`, `$DA80`, `$DBFF`, and `$CD80` left both cookies invalid. The new row adds 2,050 cold PPU reads to the pose fixture. The authenticated direction probe executed at its relocated `$D800`-region entry, read the `$CD80` table, and returned the expected angle 8. The relocated source also passed 529 direction comparisons, 12 launch cases, and eight contact updates. Paired Mike, Jay, and Steve openings entered gameplay at update 167 and matched application state, OAM, CHR latches, and VRAM over 80 subsequent input updates each.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-throw-carrier-1111 --max-files 1 --timeout 150 -- python -B tools/audit/check_steve_shatterhand_throw_carrier_1111.py --openings
```

The separate installed warm-footprint probe was an in-memory stdin script that used the existing opening, lift, and earned-machinegun controller routes.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-throw-hot-footprint-1111 --max-files 1 --timeout 240 -- python -B -
```

Both probes exited zero and generated zero files. The combined fixture has no live throw caller, player recoil, enemy integration, or renderer binding. Its verification is at the CPU and mapper-model level. Live integration and Mesen qualification remain open.

## Rebased onto the delivered original lift poses

`--live-pose --openings` now starts from exact installed `80e6aa3e32574f38b23fa6da6ab3c94bbe7b5ae11b29339b32b11a624fe6f1ed`.
The carrier first passed unchanged detached bindings on this baseline, then
was linked to the actual companion/lift RAM fields and loaded `PlayLiftBot`
and `CompanionVector` entries. The throw pose aliases the lift robot pose,
not the separate ordinary robot pose. The live clock uses a zero-page
instruction, reducing the code to 589 bytes (51 bytes remain in its prefix).

Live-bound fixture: `cc2d58533b243b91f80b63e48c854ffd34522eae22965b2286c7136d76ab9918`.
Cookie: `a810200a46aeefca7af128162f32a340`.

The CPU audit passed 58 interrupt cuts, five readback-failure cases, all24
Roll publisher cases, exact preservation of the 384-byte punch/draw suffix,
and 80 paired opening updates each for Mike, Jay and Steve. The detached
donor comparisons still pass 529 directions,12 launch cases and8 contacts.
The actual loaded live-bound core was then called directly: direction8,
ground launch timer3, speed$60 in Q4, original launch sound request$0C,
and an outbound update from X$2200 to$2260 with robot pose$015E published
by the existing animation decoder. These direct calls are fixture tests,
not controller-driven gameplay. No outputs were generated.

The test fixture explicitly clears the earlier warm-state canary before the
launch test and passes A=5 through the CPU call helper's argument. The helper
resets A, so assigning cpu.a beforehand is insufficient.

The public nightly is unchanged. Input admission, player recoil, native
enemy receipts, actor retirement and complete throw rendering remain to be
connected. See [the source-grounded integration plan](steve-throw-live-integration-1111.md).
