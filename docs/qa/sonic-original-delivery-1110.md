# Sonic’s original movement in the MMC5 nightly

Highlight **Mr. Gimmick** in row 4, column 2 and press **Select** three times.
The cycle is Mr. Gimmick, Bub, Bob, Sonic. The tested candidate has SHA-256
`d2542ff3c9f78ac26eb7e19d64a7708711bc766515f634b05952bab1be9103f0`.
The Downloads ROM was replaced directly. All three tests below repeated with
identical receipts in the Downloads launch context. Both automatic patch
guards found no same-name patches. The 2,099,510-byte IPS has SHA-256
`0584f89085f4470ecd97fd306d9a761ab4bb350d6fdf7caf58ab191e97524405`.
Its clean-base reconstruction equals the tested Downloads ROM.

Sonic uses the original Master System movement and jump state, including its
grounded jump latch, acceleration and rolling collision shape. The port reads
the native SMB terrain and publishes native position, collision and scroll
state. At the flag and castle, scripted SMB scenes use their own collision
rules so Sonic can complete the stage and enter the next one.

The menu and lives screen share the original standing art in the existing
four-cell renderer. Mesen confirmed page 224, all four expected OAM cells and
sprite colors `16 12 30` on the menu at X120/Y160 and lives card at X96/Y88.
An intermediate candidate had the correct tiles but inherited Bub and Bob’s
`2C 23 30` palette. The native GetPlayerColors entry now queues Sonic’s colors
before the private gameplay module loads. It uses the uncalled vanilla palette
body at PRG3 `B4BE..<B50E`, writes only the sprite palette, and preserves other
owners and the native queue limit. The portrait uses 47 bytes of the previously
retired PRG9 demo tail `BC77..<BCAA`, directly after the 35-byte public reject
helper. The incoming A contract is bound to the sole intermediate portrait
caller. CPU tests cover 100 unchanged selector states, 200 Start/A confirmations,
and eight palette queue capacity cases.

## Mesen verification

Each test starts from the title and uses controller input. The test runner
checks the original movement and renderer callbacks in physical mapped memory.

| Replay | Evidence | Receipt SHA-256 |
| --- | --- | --- |
| Portraits | Four original art cells, CHR page 224 and correct palette on menu and lives card | `650eddee8a9a5fef6bfd05d51c36ea99d0abc0f945de5a8dae3118f0a2c23717` |
| Opening | X200/Y176, camera X88, both lives, 81 original updates and one constructor | `bb782212c48763783d77a94c6df80d6471117aa4ec0111330371a3110373b1da` |
| Full 1-1 | Native flag, castle walk, next-stage entrance, active underground 1-2 with both lives | `0185f0fc9a35557ace4d6f843a62d33e41dd4bb7032645c1bdd96693241e5496` |

The full run reached the flag at X3161 on frame 3,325, started the castle walk
on frame 3,420 and entered active underground 1-2 on frame 5,042. It used
1,423 original movement updates and 17 jump requests, with zero helper platforms.
The full receipt records 5,043 physical frames, 2,991 completed Main calls and
2,023 gameplay frames without a completed Main call. The opening records 81
such frames out of 162. The current standing canvas, original animation set,
rings and other pickup rules, original audio, shortcut route and lag work remain
unfinished.

Controller SHA-256 bindings:

- Portraits `b2f4d172657a4a10930c93330595e3dad52af66c9fccda9e62675b4761bc860d`.
- Opening `052a4f436c6b2a697b6e79c35b14bd006842b89a53ae56a9430fb25c0e404ba8`.
- Full stage `2c2ee3f821affcff8c8748a35918fd7c9531760332a3e6d0b5d392f4154fa4ee`.

## Source and scope

The exact final CPU build also reaches active underground 1-2 with both lives
after 1,404 original updates and 17 jump requests. The d76 rebase retains the
Excitebike, Thomas and WWF changes with disjoint byte writers. The original
Sonic overlay changes 9,634 bytes and the menu changes 153. The scene derivative
changes 71 bytes, including its complete source cookie
`a72b01c0f80210577f684adf9ea78ed5`. The Zelda II CHR alias and Prince’s reserved
page are retained. Details are in the [scene qualification](sonic-native-scene-transition-1110.md)
and [public admission report](sonic-public-admission-1110.md).

No helper actors or coordinates changed. The existing positions for the rest
of the roster are recorded in the [helper inventory](helper-platform-inventory-1101.md).
The candidate reused the single 2,097,168-byte task ROM slot. Mesen receipts
stayed in memory and no captures or backup copies were generated.
