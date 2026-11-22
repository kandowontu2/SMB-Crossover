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

## Toad and Peach collect the Star

The first Toad attempt scrolled past the Star block. Another attempt hit the
adjacent brick. The verified route kept the existing enemy jump, braked in
the air and lined up below the block at X1616/Y144. Toad hit tile `$57` at
X1610, backed away while the Star rose, then jumped past the approaching
Koopa and chased the Star on its next bounce.

On installed `32eaf178`, the native collector removed the mature Star,
started invincibility and its music cue, and awarded 1,000 points. Toad kept
Small form and two lives and completed 25 more movement updates. The
replay took 1,852 physical frames and created no captures.

- Receipt `7f2a742f7612e1787024d4112e50920442af2a044bbb13dcb82c8f10cef648e4`
- Controller `34408cd6bda28a550c1dee903d6ade1bbdd6ac8b1999b89ea87979eeee759f2c`

Peach used the same block and caught the Star farther right at X1843.
The game removed the Star, queued its music and awarded 1,000 points.
Peach kept Super form, two lives and an active Star for 25 more movement
updates. The installed replay took 1,948 physical frames and created no
captures.

- Receipt `2937bf320ee1354d58d24e7c76b93c56a70b341a87c54bec35de2a383ab2ba77`
- Controller `9972c690c16976644f0236bab00774eb77938b79fae6691f4b3d75befc509724`

The natural Mushroom and randomly selected suit upgrades still need their
own acquisition checks for both characters.
