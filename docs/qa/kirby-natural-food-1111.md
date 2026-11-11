# Kirby's earned mushroom and Fire Flower in World 1-1

The MMC5 nightly with SHA-256
`409d5a2e3b8ca1fdf6fa4512cac399310c44c1837b88b9f7d2a1e5bde858d280`
passed both native food pickups in one controller run. The same checker
passes on the Prince footing build `ac262446` and the installed Steve
movement build `e6b152e2`. The CPU model executes
the reset vector, title, roster, area parser, native Main and normal NMI. It
uses five directional menu presses to select Easy Kirby, raw 13, variant 0,
then confirms with Start. Active World 1-1 begins at X40/Y176 with 6 HP and
two lives.

| Food | Authored block | Native block bump | First mature actor observation | Native collection | HP |
| --- | --- | ---: | ---: | --- | --- |
| Mushroom, type 0 | X336/Y144 | 644 | 712, X336/Y119 | 784, player X405/Y154, actor X409/Y151 | 5 → 6 |
| Fire Flower, type 1 | X1248/Y144 | 1906 | 1972, X1248/Y119 | 2073, player X1235/Y103, actor X1248/Y119 | 4 → 6 |

The first authored Goomba takes one HP at player X286/Y176 on tick 487.
Two further authored Goombas hit at X844/Y176 and X830/Y176 on ticks 1224
and 1444, after the mushroom restores 6 HP. These later contacts leave
Kirby at 4 HP for the flower's two-point heal.

Both block bumps construct the original `$2E` enemy actor in slot 5 at
Y136. The model observes state 1 immediately after each bump and state 128
at maturity. Native contact enters `KbHealPickup` with the actual actor
type. Collection erases the actor, sets the native 1,000-point floaty
control to 6, queues sound `$20`, and starts the 24-update heal effect.
The food appearance bit changes 0 → 1 → 0, which selects the type at
the second block. Kirby keeps both lives throughout.

The replay supplies controller input and schedules interrupts at the native
idle boundary. Both cheat flags remain zero and all damage, actors, terrain,
positions, and pickups come from the cartridge. The PPU and controller are
modeled, so this receipt covers logical updates. It has no physical-frame,
visual, audio-output, or full-stage measurement. No gameplay code or helper
platforms changed.

Run the [bounded stdout-only checker](../../tools/audit/check_kirby_natural_food_1111.py)
against the pinned ROM. It creates zero generated files.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/kirby-natural-food-1111 --max-files 1 --timeout 150 -- python -B tools/audit/check_kirby_natural_food_1111.py
```

Canonical JSON line SHA-256 on `409d5a2e`
`f38d1d122f3ba57a2ff0b9f8ef939ae5886e1cf61b0e009102b49f054db2d315`.
On `ac262446`
`680abca80a817488b2d31d8eb7c1ab8f30bacf336bbe004666bb44acca9d2455`.
On installed `e6b152e2`
`e03ca798290491ca9a0b153f9cce33966785dd7d0c4b9b90c46dc9beaa4d0a65`.

## Installed Mesen replay

On `e6b152e2`, an input-only run from title verifies both native foods
through 2,410 physical frames and 1,811 active gameplay updates. Kirby
keeps both lives. The mature mushroom uses the original metasprite
`$41` with attributes 0. The mature flower uses the distinct `$40`
metasprite and the sample captures palette 2 during the native cycle.

| Food | Birth frame | Mature render frame | Collection frame | HP |
| --- | ---: | ---: | ---: | --- |
| Mushroom | 692 | 780 | 883 | 5 → 6 |
| Fire Flower | 2175 | 2270 | 2409 | 4 → 6 |

Both pickups erase the mature actor and start the 24-update heal animation.
The game reaches these states through the authored blocks and Goombas.
The [physical replay](../../tools/audit/replay_kirby_food_native_1111.py)
verifies the metasprite selections. The CPU replay independently checks
the score and sound request. The physical run writes no captures.

- Mesen receipt SHA-256 `d2287de0c8c20778352ce45e8860d13c97b2c4627edeece7796088343c8d0829`
- Assembled controller SHA-256 `4967d394f295505fec5928c40021bc93d23970c676635e5942b231d665bb8ddb`

Two separate native regressions on the same installed bytes also pass.
The close inhale takes the first Goomba at X287 with full health and
both lives. The green-shell route reaches the 1-1 flagpole at frame 4973
and active 1-2 at frame 6084, with green copy, 5 HP and both lives.
Their respective receipts are
`08c15ed394ece63cf841cb7fbae0fcd88df9c431fbaea44ade9f2faf8c7e73b8` and
`54fe1a5fbf2b810d8d339c8c61aa0c98fc1c3c0d8c57e04471a3a0ce47339656`.
