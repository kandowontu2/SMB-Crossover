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

Suit acquisition and suit-specific moves are checked separately below.

## Raccoon flight and runway combat

SMB3 Toad collected the Raccoon upgrade from the regular 1-1 upgrade
block on the installed `59e1a591` nightly. He used the tail to defeat
seven enemies on the runway and earned a full P-meter by running. A
fresh A press started the native 128-update flight timer. After the
timer expired, he held a controlled one-pixel descent for 22 updates,
landed on the stairs at X2085/Y48 and completed 25 more movement updates
with the suit and two lives. The run took 3,290 video frames and wrote
zero captures. Receipt
`d8c1e7c573a6df36095021e11edc2cdade4db835ce71c7b9206583855e6ddf1c`.

SMB3 Peach also passed. She defeated seven enemies with her tail, filled
the P-meter, flew and slowed her descent for 11 observed one-pixel steps
after her usual float had ended. She landed with the suit and two lives
and made 25 complete grounded updates. The grounded tail timer stayed
idle at 12, as in SMB3 Rev 1. Her next normal jump cleared the timer to
zero, started a new timer at 16, and lowered it to 15 when she released A.
She landed again and completed 25 more grounded updates. The Downloads
replay took 3,289 video frames and wrote zero captures. Receipt
`926ad7f96f925d7fc06abe330e7113fd086772a9e8f98ec0f862a32db63dd7e0`.

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

## Moves with an earned suit

Toad and Peach each collected the five suits from normal 1-1 blocks in
Downloads nightly `59e1a591`, then used the move for that suit. Fire launched
and bounced a fireball. Raccoon's tail swipe reached both hit phases and
expired. Right triggered the Frog suit's land hop. Down+B entered Tanooki's
stone pose, and releasing the controls completed the exit. Both effects ran
for 24 updates. The Hammer suit threw a hammer in its native arc.

Each run retained the form and both lives for 25 further movement updates and
created no captures. Separate CPU fixtures verified fireball and hammer hits
and a stone contact defeat. Projectile, tail and stone contact in regular
play, Raccoon flight and Frog swimming still need playtests.

| Character | Suit action | Physical frames | Mesen receipt SHA-256 | Controller SHA-256 |
| --- | --- | ---: | --- | --- |
| Toad | Fire | 1,606 | `7a0f8dedb392a4a8cddd2940f75ce0e9a1b77c5a5e60495c7decf46d44f9af13` | `90f5ba5b1b81ae5c4fe09fbdab4f3da77bbcafb466911232cd7923b618d8ba41` |
| Toad | Tanooki | 1,668 | `93a895cfd093baf2d77b04edf57b495c9ee1fa25ecd2aa1470ca63a1d0659204` | `5401be988ec22124080387d71ed01a52e51b716b6ca64300286ca4168846e1d5` |
| Peach | Fire | 1,558 | `5e87aa650cc90ed6fd56732dd771c42eb3f320118f1b04c4b53aac0566e79ac4` | `eed7dd8cd6f946f2edca2c4fa89e6bc675cd607fccc8c1cda12882d5bab02afe` |
| Peach | Tanooki | 1,628 | `db163390d1b7b234d1397a756668a95a47d0b4eed700fe33ef01fea8c530e38d` | `a33ceb67b4de3212c08e3c531f3f2613c12b7c6291eeab7fa7aa014a24ab8bc9` |
| Toad | Raccoon | 1,631 | `fb0296010e94c220b06b54f91293aa6d8c86d626333f1e6c7f9af1be048bc324` | `894d6e606349fa5acc17b05d490a715346a8a59a30fe639b7017ada8d90f99da` |
| Toad | Frog | 1,631 | `3bfaf2cda790f06b60dcfd254ad0e78adaa44c7daaff58178a9df0ad62f3abf7` | `72ae7e6ccc2478f779787fffd9bbb2e1c1be67a7d2eeb455d1e25fe45f36e08d` |
| Toad | Hammer | 1,618 | `acf8a0c7dad79ef3fb2be3ea76daae9ca10ea3be6a48dd5fdec4b01259012bf8` | `32ee98bf041339d59e904c6e4cadefaf192aecac3d0f7c69a9672461781a784d` |
| Peach | Raccoon | 1,599 | `b33983e90f4adcfb5f1a9281f2d32402d3b23ccee9cb12c1b12317d8198f5854` | `55deedf4f50d6f29d03273a3296e855d43e6c84ad6a0fad4945ce117f0c829fa` |
| Peach | Frog | 1,587 | `fa8e13404c4c09766c5382c6a21286668a170be0b1bb932258a11691428baed2` | `b260234e5f10a616b94269d6344e499fb981ed98102473d30064a50fc02cbd6e` |
| Peach | Hammer | 1,572 | `7d78e07ac86323592115da9fd55c7c13f2c3621008049a9698bf394f409c9859` | `0ca39d32c583da065d0ce2f77d094d17ff54c10d2683c59edbd4d6889681d7db` |

## Frog Suit through 2-1 and into 2-2

On the `28708fa9` ROM, the linked engine replay earned the Mushroom and
Frog Suit from normal 2-1 blocks at X256 and X848. Toad and Peach
crossed the three gaps, reached the spring, cleared the flag and castle,
and entered 2-2 with the suit and two lives. Each completed 428 native
swimming updates across 17 input segments. The last 25 were neutral,
ending at X113/Y113 with both velocities zero.

| Character | Linked replay final epoch | Controller SHA-256 |
| --- | ---: | --- |
| Toad | 5,400 | `7dade7aa336dd716e38bbf9b59512c4d665cf5ed5f9004612cf1111b011be71a` |
| Peach | 5,404 | `e462ba074f0e85fefe950ec91dbca22dbf3ef15550a7a2c69d7463b644761004` |

Toad's first continuous Mesen run from Downloads collected both items.
During the landing at X1607/Y176, a live Goomba at X1616/Y184 hit him.
The Frog Suit reverted to Super form after the hit. The run stopped before
the first water entrance, at video frame 2,738. The Mesen receipt is
`0099b5bc05f8238c3412e0ed3936a2692d6b91daea0c6a6f8cc1b37a069e63a4`.
The approach needs a separate enemy check before the landing. The linked
results establish the swimming behavior with the earned suit. The full
route in Mesen remains open for both characters. The runs wrote zero captures.

The revised approach cleared a live Goomba using the ledge at X1472–1535
in the linked replay. It also climbed the empty pipe at X2016 and passed
all 17 swimming segments with the Frog Suit and both lives. The linked
receipt is `abe768d732d498dd5a8af77a751d49489c9106f9feb631bd66f367b547980c4b`.
In Mesen, the same approach fell below that ledge before landing. Toad
reached X1513/Y242 at video frame 2,745, with the last 12 inputs neutral.
The next approach needs to reach the ledge from above before braking.
Mesen receipt `67ffe7d39573ab9af4b280c99ff968cdd4f989789d0af5e737964dd65ef57ad8`.
Both runs used controller
`d83e3b288d7f82be3644c8cb77cd3141231681a756f5f46069ea2e985a481b30`.

The next linked replay reached 2-2 and passed the 17 swim segments again,
receipt `3747ba40e04fe70c03ed662410e8b7d6fac59764c62a978a789ceae340a9a063`.
In Mesen, Toad crossed under the ledge and got back onto solid ground.
He started the pipe jump at X1605/Y176. The Piranha Plant above the pipe
hit him at X1646/Y109 before he could land. This run reached video frame
2,988. Mesen receipt
`8246a27de0a5ddf4e89bed9316630025a84ceeb01601f27dfa68c0a9e3ebbc3d`.
The next physical replay needs to time the pipe jump against the plant's
observed movement.

With that timing, Toad waited for the first plant to retract at Y144
before jumping, landed on the pipe and crossed the gap. He also cleared
the next two plants and kept Frog and both lives. The replay stopped at
X2065/Y176 after missing the next tall pipe. The input had waited for that
plant to retract at Y128, but the character landed short of the cap.
The next replay needs to retry the climb from solid ground.
Mesen receipt `98403523f23da445c57de898fc8804629c041b81c04e6c9a716edec36a767601`.
The matching linked replay completed the swim with receipt
`267c39963d0ae91bbdfeedb924fdd0d1b94cd9184723378872dc31f0ce538335`.

To reproduce the recorded linked route, choose `toad3` or `peach3`.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb3-frog-source-1123 --max-files 1 --timeout 600 -- python -B tools/audit/replay_smb3_frog_water_1123.py --pipe-nightly --frozen-pipe-approach --cpu-full --form toad3
```

## Mario and Luigi's standard pickups

Each brother collected all four standard powerups in the November 22
Downloads nightly `59e1a591`, starting through the normal character menu.
Each Mushroom and Fire Flower emerged from its authored block and finished
its grant and appearance changes. The hidden 1-UP at X1024 awarded the third
life after the native delay. Each Star from X1616 activated invincibility,
queued Star music and awarded 1,000 points. Every check included 25 further
movement updates. The replays made no captures.

| Character | Pickup | Physical frames | Mesen receipt SHA-256 | Controller SHA-256 |
| --- | --- | ---: | --- | --- |
| Mario | Mushroom and Fire Flower | 1,579 | `24e3975a0a0eb38361dc910eb66353029069433a34734455662f50b4b0b8bdc5` | `5bc49482e5853b2e05b2012783939b6c8a8b7fcd859442c753a7719197ecc7b3` |
| Mario | Hidden 1-UP | 1,355 | `6c3f7250f75f68182eedccd3b8ee39610a63aac5f94fb535971362bb8e05cbd6` | `bf6d0fc47203688e553494afa1ae1d60aab1063e28646d0c3e6f07480c4de364` |
| Mario | Star | 1,852 | `17629660e18be6839a3b42b7f4a3aca5e788901dee936effe3b4c275e5c9012c` | `53bf3530e4fb7b63ff27ce9510398bdcf177145c92cce905cdd8e45dff531944` |
| Luigi | Mushroom and Fire Flower | 1,579 | `16393e23fcadcd32340e5d6a074766fa3ffe21f14eba1563bfab9c2ec6c2013b` | `63d258c0218c04e0a89db2a78c2d33b22e7fe21c39acd59541031bbb3bab6044` |
| Luigi | Hidden 1-UP | 1,355 | `36219824377f71b7d14e19ddaf98df65ee97ecab599c02686110c7c77a48623e` | `990b507f68006df372be87e4de84e0821cbd92b700a27f47d05c09b891106403` |
| Luigi | Star | 1,849 | `0f0b3aa87cf6675c376a993510938fb27ed3298468d3bc553ab629d303d91774` | `c7a35fa5fbc00e9b9ec8f1423704da36b8b950f8dc10d69afb5dacacef128f84` |
## Frog high pipe follow-up on the November 22 nightly

The linked Toad replay on `14b0b4c2` waited on the solid lower pipe at
X2029/Y128 until the tall pipe's Piranha Plant retracted. It jumped past
the cap, cleared the upper pipe at X2114/Y96 and landed at X2140/Y176.
It went on to clear 2-1 and complete all 17 swim segments in 2-2, with Frog
power and both lives through 25 neutral updates. Linked receipt
`67c0204c2f1544780f48ea2890ef312df2921c3c78b152ece36eab81d0513d90`.

The first Downloads Mesen replay crossed the same pipes and reached the same
landing. A sliding Koopa shell approached from behind and hit Toad just
after landing, removing Frog at X2140/Y176. Receipt
`9be752dce7ea200e59493992752eda6f6a17e83edee9580edbb35eca9a1ddac0`.

The passing Downloads Mesen replay landed farther right at X2178/Y176,
ran into the pit jump from X2193 and landed at X2349/Y176. An observer
tracked 25 consecutive grounded updates on the bank as Toad continued
toward the third pit. He passed that pit, reached the flag and castle,
and completed 429 swim returns across 17 exercises in 2-2. He had Frog
and both lives after 25 final neutral returns. The replay used 6,773 video
frames and saved zero captures. Peach's physical swim replay remains open.

Mesen receipt
`2085d40dfd78b3cdcce0284f6f471ac3eaaf409cecf4e2d18e90175c7595f222`.
Controller SHA-256
`9deb4173121e8f778657664a32f3445aee313aa63f4b8468f34a724a7c9287db`.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 330 -- python -B tools/audit/replay_smb3_frog_water_1123.py --combined-nightly --shell-runout --run --form toad3
```
