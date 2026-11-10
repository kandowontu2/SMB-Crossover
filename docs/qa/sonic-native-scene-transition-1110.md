# Sonic native flag, castle and entrance

Sonic clears 1-1 and reaches active underground 1-2 with two lives in the
controller-only CPU replay. The repaired route uses 1,404 original Sonic
frames and 17 jump requests. It uses the authored terrain throughout.

On the predecessor, Sonic touched the flag and began the native castle walk.
The original motor stopped as intended. The public feet probe still consulted
its frozen airborne flag and suppressed native floor metatile `$54`. A direct
CPU comparison confirmed the failure at engine 5 with native Y176, source
Y131 and source flags `$0c`. The old service returned A0 and the native probe
returned A`$54`. The full route entered native death at X3215/Y243.

The new four service targets delegate head, side and feet reads to native
collision outside engine 8. Bounds decline through carry so the existing
native caller uses its native fallback. Engine 8 continues through the
qualified source effects. The cached head wrapper preserves the incoming
processor flags. This uses exactly 50 bytes of the approved executable
metadata range `$D2E9` through `$D31A` on CHR page 328. It uses no new RAM.
The prior 139-byte cold startup and the complete original motor retain their
exact bytes. The update changes 71 bytes across page 328 and its fixed cookie
at file offset 1034472. The new cookie is `a72b01c0f80210577f684adf9ea78ed5`.

| Replay phase | Native engine | World X | Native Y | CPU epoch |
| --- | ---: | ---: | ---: | ---: |
| Active 1-1 | 8 | 40 | 176 | 167 |
| Flag | 4 | 3161 | 131 | 1571 |
| Castle walk | 5 | 3161 | 158 | 1633 |
| Automatic 1-2 entrance | 7 | 40 | 176 | 2392 |
| Active underground 1-2 | 8 | 44 | 48 | 2768 |

The CPU receipt recorded 87 native flag collision entries, one original
constructor before the new area, no injury or death calls, maximum logical
camera movement of 3 pixels and minimum SP 184. The pre-portrait source
composition was `050b9896dd86a887cc695b2050a6e341b602244e48024c92cad0b4cf568e24b9`.
The independently composed d76 plus portrait and scene image replayed the
same route at `498130a62b4a80b49bfb9ee8602d2afb2254f4e8368b5879d2dd2bfcd42fa319`.

The source API `check_sonic_native_scene_1110.combined()` returns the image,
common program, packet and receipt in RAM. On the frozen public source
parent `7de72fb7d315cd78288790e84ff0ff988e9f62906470edeb43a8ccf3104bf2ef`
it produces `9e4d1bb5bc50fd019ac95dd6435b698f556f530bf7418a88fd216ae5c1cda14e`.
`proposal(raw, aligned)` applies the scene delta to a composed parent after
checking the existing page, all eight kernel carriers and the fixed cookie.

Cold loading checks the full 1 KiB metadata readback and commits both headers
after validation. A cold load takes 18,386 PPU reads, 397,199 CPU cycles and
minimum SP 187. Warm admission takes zero reads. The old cookie causes a
new cold load. Twelve injected faults cover both endpoints of each new leaf
and the four retargeted rows. Each fault leaves both headers invalid. The
shared mailbox retains its initial bytes. The first mailbox fixture wrongly
expected zero and was corrected to compare the actual saved preimage.

Twenty-four scripted-scene ABI pairs match the native behavior and eight
ordinary pairs match the frozen source effects. Every new instruction is
reached. Seventy-five real lag NMIs, 75 foreground scanline IRQs and one nested
scanline IRQ restore the live foreground and return state. The independent
public rebind covers 66 ordinary getters, 2,048 header/flag negatives, 192
scripted native getter pairs, 16 bounds fallbacks and owner/cold lifecycle.

The earlier root Mesen opening used the pre-scene current image
`e7a30825f992d9a28c813ee7eb2571e6836b8f75c6579234f7f7a66106a6d896`.
Receipt `e745a7dccf3d213eaeafcbf713645e32346c4618ec69968ae2754c9fe2f77e95`
recorded 81 original frames, one constructor and 162 feet calls. The script
observed 506 physical frames, 162 gameplay frames and 81 gameplay frames
without a completed Main update. The new opening controller changes only the
cookie literal. The separate full-stage controller samples real terrain and
enemy positions, waits for Sonic's jump-ready bit, and holds A for 20 logical
updates. Both Lua controllers passed API mocks. Physical replay of the scene
and the full route is a separate queue step.

| Source | SHA256 |
| --- | --- |
| `tools/reference/sonic_sms_native_scene_1110.py` | `a43c8e12dc743428ef87ae255a245aed13a4acd203777f257ce2b0c29102f5c6` |
| `tools/audit/check_sonic_native_scene_1110.py` | `da9ad101bd2aa40e0103fe473e4c9cb831e4a1c1c778646f6caf0e8564390b63` |
| `tools/audit/qualify_sonic_native_scene_1110.py` | `32137430db9234eb7d78034df93b82e07d1764ba80e12e242f24d071b77eacef` |
| `tools/audit/check_sonic_native_route_1110.py` | `d5f9c4fa7e94d7579acfbc0b6999cdf9fdb156aaae8ae23e1af5e23d121f12fc` |
| `tools/audit/check_sonic_scene_public_rebind_1110.py` | `11fab24a8e76d85e0668d52609ad9fc5a503092f7c2135a488c095def75b442b` |
| `tools/audit/check_sonic_scene_stdout_source_1110.py` | `95dd6191519d96596d141f9bc5281d28f72483ec60b0e35811579c90bbcba8b6` |
| `tools/playthroughs/sonic_original_motion_stdout_1110_v2.lua` | `052a4f436c6b2a697b6e79c35b14bd006842b89a53ae56a9430fb25c0e404ba8` |
| `tools/playthroughs/sonic_original_full_stage_stdout_1110.lua` | `2c2ee3f821affcff8c8748a35918fd7c9531760332a3e6d0b5d392f4154fa4ee` |

All checks ran through the bounded runner with a one-file maximum and used
zero output files. This proof covers the 1-1 route and its entrance into 1-2.
Earned pickup routes, original ring/combat behavior, full source artwork and
source audio still need separate gameplay qualification.
