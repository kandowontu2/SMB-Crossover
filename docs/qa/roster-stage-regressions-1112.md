# Current nightly stage regressions — November 12

Installed ROM: `8fc57b8b4268a47f8a906af8b5813834bbf76ca7376d1d12767d510708da9582`.
All runs use ordinary controller input from reset, no emulated-state writes,
no capture files, and the root's serial Mesen queue.

## Kirby

Natural Green Koopa inhale, Down swallow, green-shell enemy defeat and full
1-1 to active 1-2 passed in 6,296 physical frames, HP5 and both lives. This
is not an injury-free route or proof of every copy ability.

- Receipt: `f9cd55629692af89d070d14133872f6f13a3f4abe723b30084fe481c7ea39410`
- Script: `21006897ae2bf02861dd16620a4e7fc7e4bdd6cc19c932d05a192b3f92e35ad5`
- Recipe: `compose_metal_kirby_1112.py --mode green-route --rom C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes`

## WWF

The retained successful historical controllers were adapted to the current
menu and stdout-only reporting. The first Hogan run lost a life at X802:
after stomping one Goomba, it descended beside the second without an aerial
attack. An active-frame actor trace established this contact sequence. Adding
the normal aerial punch input and settling walking before grounded punches
resolved the route. No ROM behavior was changed to accommodate the test.

Hogan passed full non-shortcut 1-1 to active 1-2 in 11,586 physical frames,
4,628 active updates, both lives, 13 native defeat calls and 70 native helper
carry calls. The route uses the existing 48-pixel horizontal platform at
initial left X1376, center X1400, top Y208 in 1-1. No helpers were added or moved.

- Receipt: `4d155edb6fdc3b4e21f06b75f18e13b87bb6314eb16f5839efd34a4e3bd889ad`
- Script: `ac519316de6d0edd5dcf9d56a511689799ed4288bedb900d96c8d6447409b204`
- Recipe: `replay_wwf_stage_current_1112.py --role 0`
- Diagnostic failed receipt: `55fb3730b3d5d8f3d2c5b3011e95653c1ed70118e8293f4dced92f49db261d85`

Ted DiBiase also passed with both lives: 10,962 physical frames, 4,273 active
updates, 13 native defeats and 64 helper carries.

- Receipt: `1c5a87bd9feed272c334c6ec9064b217e2fa4d004c8d9a4104adc762ce0a7dda`
- Script: `7f6d33b494d4208687761700ced29247aa7513e366e662a48715c8fc9a78e09e`

Bam Bam Bigelow passed with both lives: 11,102 physical frames, 4,319 active
updates, 13 native defeats and 62 helper carries.

- Receipt: `414164cc3e8e205f98ef0263f16b7df616e13d82a7086d2affc112fd95f39dfa`
- Script: `b917b9f13d67790205d007ca3e68992d0df4272ec5cd0eae1067981838e9d8eb`

Honky Tonk Man passed with both lives: 11,491 physical frames, 4,529 active
updates, 14 native defeats and 63 helper carries. His route uses Down+B for
grounded combat, which the existing adapter maps to the original game's B
attack. The plain-B attempt stalled in source action15 and lost to the
Goomba descending near X1194; that ordinary punch interaction remains a
separate review item, not a proved game defect or a fix delivered here.

- Receipt: `034df89bb8d19e046e520040ac6b25e09cb21c6489c1cd5bff078e11f8a81987`
- Script: `f37ee607eb092a92842a9fb590751c31e9b450173c0ea6209d23851ec29373fe`
- Plain-B contact trace: `3e17b75371097b859a58d5f0e4602b2d41b05751dc026f1ac09fc4fc38a528dd`

Randy Savage passed with both lives: 11,249 physical frames, 4,387 active
updates, 13 native defeats and 64 helper carries.

- Receipt: `8ff221552b109d2e0b2e4d29ced14856b6d0b5072ce7d5c2b60ee933eec255e4`
- Script: `11e8703b766614f1165c2c5e7d121a95830dd057d2389cf8b284c84d6f005480`

Andre the Giant passed with both lives: 11,568 physical frames, 4,555 active
updates, 13 native defeats and 65 helper carries.

- Receipt: `852a4d29843b1ad3b8303b8c97e74d69d174d63029795f759c7ef284a417220e`
- Script: `aa992ced24cdd2d90b75e9d332716b48e4311aed1830ebdf10342b79ebf41616`

All six WWF identities now have a full-route pass on this exact nightly.
This stage replay does
not establish natural flower/Star/1UP collection, full original WWF gear,
all-enemy defeat, visual review of every frame, or both difficulty modes.

Build inventory after these runs: 3,123,066,778 bytes and 19,998 files, within
the existing 5 GB / 20,000-file cap. Root reuses one Lua output; no videos,
screenshots, per-frame dumps, or additional ROM copies were produced.
