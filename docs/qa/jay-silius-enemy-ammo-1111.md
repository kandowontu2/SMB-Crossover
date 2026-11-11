# Jay McCray enemy ammo pickup

The Journey to Silius (USA) donor is
`12f5c5e413a2aa5bff75b5077e4477497d7e49aa432560c2e8c3fd3cc71910cc`.
The detached host fixture starts from the installed MMC5 nightly
`852712c9a2afce71c45f9f2c970e1f5c7969c58d878cfa0a250d2bdb7ba93383`.

The donor controller opening defeats the enemy at update 69, transforms
its explosion into type `$22` ammo at update 93 and collects it at 124.
The item rises from 160.25 to 130.25 pixels and returns to 160.25. The
first active update uses signed Q4 velocity `$C4`, up from the initial
`$C0`, and the collection update reaches `$3C`. The 31 donor OAM cells
use 8×16 tiles `$FC` and `$FE`, with horizontal and vertical flip bits.
The 64 donor CHR bytes are copied into CHR216 bytes 672–735 for native
tiles `$2A` and `$2C`. The art SHA-256 is
`fd58ba6cdbdf0aa6ef7d1a0ceaddb6a6b467850096f30bb37dcbcbb18a3d29dc`.

The detached host cold-starts Jay and uses the native parser to place the
authored Goomba record `$6B06` in slot 4. The controller fires once. The
existing stock flight and hit code reaches the native defeat JSR at `$B2AF`
on update 11. The capture hook preserves AXYP and SP on ingress to `$9AF5`
and reads the Goomba's center before the native defeat mutates its state.
The default zero PRNG seed and captured live position and clock produce the
pending item at world X101. It becomes active at update 35, rises from Y192
to Y162, and lands on native terrain at Y200 on update 69. Right from update
68 reaches the item on update 100. The item clears, ammo rises from 0 to 16,
the donor sound request is `$18`, and Jay retains two lives. The check pairs
64 native renderer cells to their live OAM entries and following DMA with
CHR216 selected.

The worker also matches 6,144 donor roll cases, 280 lifetime ticks, 256
gravity values and 432 touch/refill cases. Another 108 original integrations
through PRG7 `$E1A4` with X6 compare signed position, velocity and airborne
state using the same 136 ordered host terrain answers, 44 of them blocking.
The genuine X6 geometry pointer is `$D046` → `$D0C8`. Its head samples are
`(-8,+4),(-8,-4)` and feet `(+8,+4),(+8,-4)` in Y/X pixels. A zero resulting
vertical velocity skips probes. A blocked head retains the airborne flag.

| Component | A3 placement | Bytes | Ingress |
| --- | --- | ---: | --- |
| Roll, lifetime, gravity and touch | `$B700..$B7BF` | 192 | `RollAmmoDrop`, `AdvanceAmmoDrop`, `AmmoGravity`, `TouchAmmoDrop` |
| Capture and item update | `$BA90..$BC7F` | 496 | `$B2AF` → `CaptureAmmoDefeat`, `$B14E` → `StepAmmoAndStock` |
| Pickup rendering | `$BC80..$BCFB` | 124 | `$B332` → `DrawAmmoAndStock` |

The update runs before stock projectile updates so the defeat frame keeps
all 24 subsequent countdown ticks. The renderer runs after stock shots and
uses their existing body-aware OAM limit. Private state uses C2 `$C0D0..$C0DA`
and `$C0E0..$C0EC`. The worker shares the existing Jay terrain query scratch
and five-byte shot metasprite buffer. The capture's room value 8 and mode
0 apply to the authenticated opening stage scope. Area entry must clear
`$C0D7` when reconstructing the actor to discard the prior area's item.

The fixture attaches the code and the camera handoff to cold-loaded RAM.
Cartridge transport, area retirement, actual Mesen display and the complete
stage route require qualification on the composed ROM. The Goomba spawn is
directed through the real parser. The controller supplies the shot and pickup.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/jay-silius-enemy-ammo-1111 --max-files 1 --timeout 600 -- python -B tools/audit/check_jay_silius_enemy_ammo_1111.py
```

The bounded run generated no files. The linked roll, host and draw SHA-256
digests are `fe4c7b02faa564f1fe87a8065fc87af3c6c818ae848aa92cb8664e63e8cfaf87`,
`2785c20a247d5c8181628319679ea1ad8f184b2c38f01c729eb77704f3cbe5f2`, and
`1ac9acee77601a5c2ee1daa9884ba95bb34137fca28257d62936db300314766a`.
