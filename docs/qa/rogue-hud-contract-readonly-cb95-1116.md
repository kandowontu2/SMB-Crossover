# Rogue HUD contract and passive observer — 2026-11-16

Root's private cb95 two-picture missile replay was functionally positive and showed a moving missile. Root noticed E191/M005 while actual resources were HealthLo19h/HealthHi19h and missiles4/max5. This note does not declare a HUD defect or alter the qualified missile/full source/native claims.

`src/rogue_dawn_host_ui_v1.s::RdUiHud` formats energy as `(HealthHi>>4, HealthHi&15, HealthLo>>4)`. Thus raw bytes `[25,25]` decimal = Lo19h/Hi19h correctly produce **E191**; the fractional low nibble is omitted. M decodes **current RdMissiles**, not capacity, into three decimal digits. Current4 should eventually display M004.

The late writer admits only actual Rogue gameplay and an empty/safe native queue, palette and parser context. Pause, disabled screen, TimerControl, either queue offset/payload, address control, pending CHR/palette/growth/Star, area parser and ScrollThirtyTwo≥32 can defer it. It compares missiles against InvHudAmmo on every eligible call. Cache acknowledgement follows the complete14B command/terminator/offset commit.

`RdUiEarly::Retract` verifies its sole complete14B cache-matching packet before clearing only VRAM_Buffer1[0]/Offset and setting **InvDirty=1**. It preserves the health/ammo cache. `RdUiHud` tests InvDirty before comparing cached values. Therefore a retracted cache4 alone cannot suppress retry while PPU still shows5. Actual guard/caller/NMI cadence remains to be measured; no indefinite-progress claim is made from static code.

Separate passive facade, frozen for root:

- `tools/audit/replay_rogue_missile_cb95_hud_observer_1116.py`, SHA `995e0f3071bd5c1ccbeaeaa14e1b1b3ba097c87f78dc5462315b89c2fa454031`.
- API `controller(rawcb95)`, `metadata(rawcb95)`; Lua `39f017917d328687b9f9c03af016ea8ad1ab3492cdd9701764251b8648833f41`.
- Exact observer removal restores qualified core missile Lua `614b87d9365dcd07268084e47824874a4055b9b1b90d70459efe4ccf18a303d3`. Controls, all functional assertions and the actual expiry/+25 endpoint remain exact.
- `hud_diagnostic` adds aggregate actual Early/Hud/eligible calls and guard reasons, at most4 first causal packet/retraction/ammo-cache witnesses, terminal resource/cache/guard fields,15 queue bytes and11 actual `nesPpuDebug` nametable bytes2023..202D. Zero PNGs, no per-frame dumps or game writes.

Final bounded metadata73111 PASS: compile/exact restoration plus executed no-game-CPU mock registration22 exec addresses/14 write addresses/two events. `build/rogue-hud-observer-source-1116` remains absent, zero generated files. This is not a source/full route rerun or PPU rendering claim. Earlier metadata77824 was intentionally discarded because the Python registration gate was added while it was running; no native pin relies on that process. Root alone will execute the final frozen observer against actual hardware/PPU state.
