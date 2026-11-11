# Sonic and Super Sonic MMC5 nightly

Highlight Mr. Gimmick in row 4, column 2. Three Select presses show
**SONIC**. Four show **SUPER SONIC**. A fifth returns to Mr. Gimmick.
The other choices in the cycle are Bub and Bob. The compiled roster
test confirms Start and A for all 101 names and preserves the previous
100 rows.

Both forms use their standing sprites from *Sonic the Hedgehog
Improvement*, Vol. 2 1.7. Normal Sonic uses CHR224 and the blue palette.
Super Sonic uses CHR226 and the gold palette. The four body cells
appear on the character-select screen, the lives screen and during
play. Both forms retain the existing Master System motor, ring
collection, ring-loss response and native mushroom progression.
Additional poses and distinct Super Sonic mechanics remain open.
[Sprite sheet](https://www.spriters-resource.com/nes/sonicthehedgehogimprovement/asset/504880/)

## Physical Mesen checks

Each route starts at the title screen and uses controller input only.
Both forms took the native 1-1 flag, walked into the castle and entered
active underground 1-2 with both lives. The Sonic replay lasted 5,089
physical frames and matched 2,980 body frames in hardware OAM. Super
Sonic took 5,114 frames and matched 2,984. Separate runs verified five
ring pickups, loss on live Goomba contact, the displayed ring HUD and
recovery. The mushroom routes collected the authored item, completed
all 60 growth updates and recovered from ring loss at the powered tier.
No helper platforms or level data were added.

| Form | Replay | Receipt SHA-256 |
| --- | --- | --- |
| Sonic | Menu and lives portraits | `45048ee287136395659d62583701f69fff8fa432d5a31d244616ccf55f26b627` |
| Sonic | 1-1 to active 1-2 | `efcf0d862663c551918f62276507e73de5b99d1e9fb7c440ada6f837cd4cdee7` |
| Sonic | Rings and damage | `e7d99c07f0937c4b6de598bb427ccc81323d07fd104480b19806aa1241862b74` |
| Sonic | Earned mushroom | `4946618eaa39c6572c90fc899f1639ed10752fb8632571f22eeed032fc493f85` |
| Super Sonic | Menu and lives portraits | `e18c98ee94428b25b68e6c90e0a088fdf8eb40c1d2059635ab1830ef53557a60` |
| Super Sonic | 1-1 to active 1-2 | `ae4816c16c20f09bc170d593d8b2005f76d11bd3bebdef226b720c05cc74a20c` |
| Super Sonic | Rings and damage | `c4ae5790c3b81bdd341d487a95716720e3f18d3b261eaee882dada77d5b2d8aa` |
| Super Sonic | Earned mushroom | `6f7a4777f247198e6f3a1c70ad6e5386b706e3067e103b23e7e1a2986179d12d` |

## Cartridge binding

- MMC5 ROM `c4568faf4f472d4d6c3915c9b4258d5c04d6dcbb562b3e5602a5d580bb3046a2`
- Current IPS `ff95f659cb60da74c888f34197a7a186c6868a26909052546b3fda9575b9e9bd`
- Stage route source `2c2ee3f821affcff8c8748a35918fd7c9531760332a3e6d0b5d392f4154fa4ee`
- Parent MMC5 ROM `2d7fb6e63ea55f2d0eb9ef3af4efc467233da013dc70e295952a4adcdd14ecdb`

The recipe inverts to the exact parent in RAM. The release patch
reconstructs the tested ROM from clean headered Super Mario Bros. (World).
All eight candidate receipts matched when repeated from the Downloads
launch path. The automatic patch guard found no matching sidecar before
or after installation. The installer replaced the ROM directly with no
backup file.

The selector retains `$5FFE` across native profile initialization.
Five CPU canary cases cover the full ExRAM window. A separate Rogue Dawn
audio check binds all 25 relocated direct and indexed readers plus the
224 indirect bank entries. Their compiled read and code domains leave
the new menu-name helper at `$DEED–$DF18` available.
