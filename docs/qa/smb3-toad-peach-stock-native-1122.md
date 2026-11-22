# SMB3 Toad and Peach pickup checks

Both hidden 1-UP checks passed in Easy 1-1 on the Downloads MMC5 nightly
`a6d91e368657a0ee1458391542e98adafcec45991ebecbe4521a648513cfa4df`.
The replays use normal controller inputs and start from the real character
menu. The existing 1-1 clears for both characters remain complete.

| Character | Hidden block | Collection | End state | Physical frames |
| --- | --- | --- | --- | ---: |
| Toad (SMB3) | X1024/Y128 | After the item rolled off the ledge | Small, three lives | 1,361 |
| Peach (SMB3) | X1024/Y128 | After the item rolled off the ledge | Super, three lives | 1,253 |

Each head hit spawned a native 1-UP actor. Both replays observed full
emergence, positive overlap with the player, the original pickup dispatch,
item removal and the extra-life popup. The delayed life counter advanced from
two to three, the extra-life cue was queued, and each character completed 25
further movement updates in the same form. Neither run created captures.

| Character | Mesen receipt SHA-256 | Controller SHA-256 |
| --- | --- | --- |
| Toad (SMB3) | `4c4421cf9f58ee039013cc5c8080ef9fb24a928e33b05904b85c809120dd5598` | `fcb029c40f0740a6ca567f5a01bd496e1e3aff056720f1a1ea10d548662baa1c` |
| Peach (SMB3) | `6640811e234f69fb8f5123bfb7ed310e08b9dfb2ce4936d439b150221151cac5` | `e176cbac5341a49b17e061d2a90a6d6e355282121b6cad3875faed07b6d1337e` |

The first Toad Star route scrolled past the block at X1616 while trying to
line up. It reached the left edge clamp at X1623 and took fatal Goomba contact
before producing a Star. That replay's receipt begins `0469f38d`. The Star and
each character's natural Mushroom and suit upgrades still need their own
passing evidence.
