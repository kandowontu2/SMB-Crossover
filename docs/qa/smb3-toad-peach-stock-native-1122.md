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

## Peach collects the Mushroom

On the installed `32eaf178` nightly, Peach hit the Mushroom block at
X336/Y136 in Easy 1-1. The Mushroom finished emerging after 48 updates,
and Peach collected it at X428. The game awarded 1,000 points and ran
the 47-update growth animation. Peach kept Super form and two lives
through 25 further movement updates.

The same run then released a Fire Flower at X1248/Y144. The replay
stopped while the bumped block was temporarily off its tile, before Peach
collected the Flower. The Mushroom checkpoint had already passed.

- Receipt `0b539309f0ead330d560717fb7a1261c2f7e8c7b32b60fe3846e0621e5f1853f`
- Controller `bab9e5a739c235ebe98cbb6dd171794c42c86cab82d2a221649f50608b7915aa`

## Both collect the Mushroom and Fire Flower

The replay now lets the second block finish bouncing before checking the
tiles that support the flower row. Both characters passed the full pickup
sequence in Easy 1-1 on installed `32eaf178`.

Both hit the Mushroom block at X336 and the upgrade block at X1248.
After the Mushroom rose from its block, they collected it, finished the
47-update growth animation and played 25 more movement updates in Super
form. They then climbed onto the row from the left and collected the Fire
Flower. The item was the Fire upgrade (D2), and each character gained
1,000 points and stayed in Fire form for another 25 movement updates.
Both ended with two lives. The runs created no captures.

| Character | Physical frames | Mesen receipt SHA-256 | Controller SHA-256 |
| --- | ---: | --- | --- |
| Toad (SMB3) | 1,526 | `b8861e5f8a1444424242d2486bbb38749d299a94c06693665d148c89b56d7a72` | `20d84622508433026bc336e6140944952a3a546d8b6f7e6f574ad97be315ef6b` |
| Peach (SMB3) | 1,484 | `18e7cede829ec2414279356da5c44ba97bf49f302787d43ed8393ea5cef05f01` | `19f336e3978969a434dc7ebfbc7441be2f3ded15359aa8f7ce392b137dc457eb` |

Fire attacks and the other suit-specific moves still need separate playtests.

## Targeting an authored suit with ordinary controller input

The suit block chooses its pickup from the game's random state when the
player hits it. The replay pauses under the block with Start. The world
stays frozen while the native random state advances. When that state will
select the requested suit, the replay resumes and jumps into the block
with Start+A. The observer verifies the actual random byte, spawned actor,
pickup collision, full 24-update transformation and 25 further movement
updates.

Peach's first replay scheduled Start between two game updates in one
physical frame. The game's input poll still held the previous input.
The observer now waits for the native pause routine to accept Start,
then uses the actual Start+A consumption and random state to qualify
the jump.

All runs below used installed `32eaf178` and the authored block at X1248.
The characters finished in the requested form with two lives. The replays
created no captures.

| Character | Suit | Spawn tag | Random byte | Physical frames | Mesen receipt SHA-256 |
| --- | --- | --- | ---: | ---: | --- |
| Toad | Raccoon | `$D3` | 16 | 1,587 | `a132e5255173da2e3bf43f635ac94447fcc182db7507096502b83fab0613f83d` |
| Toad | Frog | `$D4` | 12 | 1,593 | `9cfaf59b23c325b36808fa9ae0ebe66175095728c7cd221aa843c7b7a615b5b2` |
| Toad | Tanooki | `$D5` | 98 | 1,590 | `083979a5936e7029a2ab8057dc7b35b323f35c80f846fced37b6b4673c0494e4` |
| Toad | Hammer | `$D6` | 49 | 1,591 | `ff6cb319cf2b3d5f9210473df45102f16e39b0995fa03c3feed1ef6fecc217af` |
| Peach | Raccoon | `$D3` | 121 | 1,555 | `4152c7f39ee79b51255389fb33aae54613b4ce9e6a583a59cc70940a76b3296f` |
| Peach | Frog | `$D4` | 107 | 1,549 | `8916cbf8455960b01ac2b0064bf1eaf0b01c5553702e389f5b43a2098c8458b9` |
| Peach | Tanooki | `$D5` | 53 | 1,550 | `773b7ba76931d9df15e4b7f280830f6a9702bd2a1a49bddab25a128d93654aa6` |
| Peach | Hammer | `$D6` | 189 | 1,545 | `4d7a8535ccabee5c66dbb72ab15a39a593ea27a028c354f60a6dcf505d12d9c0` |
