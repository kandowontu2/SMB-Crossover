# Rogue Dawn HUD restored in 1-2

The November 22 MMC5 nightly redraws Rogue Dawn's energy and missile display
after the native area loader clears the status bar. The fix marks her HUD for
redraw when the scene changes. It changes 10 bytes in her existing lifecycle
routine. The rest of the parent ROM is byte identical, including the helper
platforms and the code for other characters.

The [normal controller replay](../../tools/audit/run_rogue_hud_scene_native_1122.py)
earns the energy and missile tanks, clears 1-1, enters 1-2, earns the Bomb,
and verifies its placement, fuse, explosion, terrain calls and expiry. At the
first active 1-2 update, the game queues the HUD row for the PPU. The row
reads `E191 M005` at the end of the replay. The test counted two redraws in
236 eligible calls, with 234 calls skipping an unchanged display.

| Mesen check | Physical frames | Receipt SHA-256 |
| --- | ---: | --- |
| HUD and Bomb, private candidate and installed Downloads copy | 7,621 | `6b34c16be2fda760e5957b5b5acda09f38288329fd5a99ce06a99c05f75f90eb` |
| Earned missile motion and offscreen expiry, private candidate | 3,236 | `16c3b55c81ca396c54b4a2d845cc9459b398667304ead1738fd9113c6b84366f` |
| 1-1 clear and 25 grounded updates in 1-2, private candidate | 6,795 | `f420e2a8da91962bd9906cbd79f4e5fe927c3ceb3c5f64c09da90c8af8ed9458` |

The installed 2,097,168-byte ROM matches the private candidate exactly.
SHA-256 `79fd089f80b06038e68b968d2ff80d09caba72a133735b3fef6bb86ffa3ed2df`.
The Downloads sidecar checks passed before and after installation, and the
Downloads replay matched the private HUD and Bomb receipt exactly. The run
reused the existing two-file test slot and created zero capture files.

The remaining upgrades and the full sound and performance review still need
playtests.

### Bomb hit on a 1-2 coin block

The [Bomb block replay](../../tools/audit/run_rogue_bomb_block_native_1122.py)
earned the Bomb through ordinary play on the installed `a6d91e36` nightly.
Rogue Dawn rolled along the top of the block row and placed a Bomb at
X186/Y140. Its downward explosion point at X186/Y156 activated the authored
question block at X176/Y144. The native block state changed from `$C0` to
`$C4`, the coin count rose from one to two, and the score rose by 20.

The Bomb expired normally. Another 25 gameplay updates passed with the
same health, energy tank and five missiles. The test used controller input
and read-only observers and created zero capture files. Receipt
`6f8ad6f3e869b378c5562ccd4af32cb6cc651992028e9cee9d7cbd2927107d48`.

### Earned High Jump in 1-2

The `--high-jump` replay continued from the verified coin-block Bomb. Rogue
Dawn rolled under the low ceiling, stood up, and walked under the hanging
bricks. She jumped up from the open pocket to the right of the upgrade brick
at X1104/Y128 and placed a Bomb above it. Its downward explosion activated
the brick and revealed the typed High Jump pickup. The normal reward routine
granted it, changed gear from `$01` to `$03`, and awarded 1,000 points.

Rogue Dawn then returned to the floor and jumped using normal controller
input. The source jump began with the same vertical velocity and used
gravity `$12`, compared with `$18` on the dry jump before the pickup. She
rose 111 pixels from Y177 to Y66 and landed back at Y177. The replay
continued for 25 updates after landing with the upgrade, one tank, and
five missiles. Receipt
`affa692dc427deaa9994ba53730feb83f60bb45468ec8fce740f6d5e146ed196`.

### Earned Wall Jump and ordinary brick break in 1-2

On the installed `a6d91e36` nightly, the `--wall-jump` route crosses the
long gap using the existing descending lift at world X2236. A Bomb above
the authored brick at X2400/Y128 reveals Wall Jump. The normal reward
routine collects the item and changes gear from `$03` to `$07`.

A second Bomb breaks the ordinary brick at X2384/Y128 and opens a gap on
the left side of the used upgrade brick. Rogue Dawn jumps into that gap,
releases A, and presses A again while holding Right against the wall. The
native jump routine sets upward velocity to `$FC` and gravity to `$12`.
She lands on the floor at X2387/Y177 with one energy tank and five missiles.
The replay passes 25 further game updates with the same health, lives and
gear. Receipt
`750a60f2b404fd7c219ddd704ae5b5ccbfcff95da0aadf4b7f41d380f0537f26`.
Controller SHA-256 is
`097bc20c658398f969e4b95d607bb40f3d4881cea6bb06d9c1e2e2766fdffcac`.

The `--wall-jump-left` replay collected the same upgrade, rose in the open
pocket to the right of the brick, then pressed A again while holding Left
against it at X2412/Y131. The native branch used upward velocity `$FC` and
gravity `$12`. Rogue Dawn landed at X2412/Y177 and kept the same health,
energy tank, and five missiles through another 25 game updates. Receipt
`6eb3cf24a12ccf59a3efee099c9e12389726336757867124a1ced9f34352a1bf`.
Controller SHA-256 is
`1f8406cf1693e2dac5e7e2108b72090b4bc0ff5d76c266dfb9d1fefc133baa7a`.

### Bomb damage against a live Goomba

The Mesen replay on installed `32eaf178` earned the Bomb in normal play
and repeated the coin-block check. A first approach jumped over the
Goomba's floor pocket. The passing run landed on the step at X433/Y129
and rolled into the pocket to plant a Bomb.

The explosion at X466/Y199 struck the Goomba at X467/Y184. The enemy's
health went from two to one and it flashed on contact. Rogue Dawn
retreated, the Bomb expired, and 26 further movement updates passed
with the same health, two lives, one tank and five missiles.
The replay created no capture files.

- Receipt `4424558cb7423761d9b00fc9fa8beddd46f58862ed9dc780d16d2238ae227ce7`
- Controller `de6461b64045d59eb1d525f83d788d7144e9ed6db82a684060a281fd417e58a9`

### Missile damage against a live Goomba

On installed `32eaf178`, Rogue Dawn earned the Missile through ordinary
play and used it in 1-2. She fired from the floor as a Goomba fell from
the ledge. The missile reached X1120/Y187 while the Goomba was at
X1122/Y171. The actual collision lowered the Goomba from two HP to one
and it flashed on the hit.

The missile played its normal impact and expired. The replay observed
26 further gameplay returns after expiry with two lives, the same
health as at the start of the encounter, and four of the five missiles
remaining. The run took 9,069 physical frames and created no captures.

- Receipt `c60c4b6aa9dd3004254b4a8870212a46df74b05bee05de26038f3a451d98ab03`
- Controller `5b608700704e84387e772e6272b6f77d40884585980c68c0505e49040e9d6ba4`

### Route to the Screw Attack upgrade

The controller-only diagnostic reached High Jump and crossed the first
long gap of 1-2 from the Downloads nightly `59e1a591`. Rogue Dawn jumped
from X1275/Y177 and reached Y69 near X1326. The later approach fell at
X1940/Y241 on update 7,148, before the descending lift at X2236. The
replay stopped when the fall cleared her health. The next attempt needs
a different approach to the gap at X1940.

A linked CPU replay reached the descending lift after landing from the
earned High Jump. Its jump from X2196/Y113 aimed for the lift at X2236/Y128
and missed. Those two replays establish separate points where the controls
need adjustment. The Screw Attack pickup and its hit are still open.

The [controller runner](../../tools/audit/run_rogue_screw_native_1122.py)
uses the existing two-file test slot and launches the Downloads ROM. Both
tests produced zero capture files.

- Native receipt `f01321f9eaf48649693ab925c8e664c0e3a8e9f5de605269f29ae2f05b19b72c`
- Controller `9ae88510c8f72f34d5d3127d9159237459c9e4cc28999d6cc18e7eef1dbc3f94`
- Linked CPU receipt `bdd24e44267d78100a028127b0a731a920ef53944c2a0d767be5fe16eb153355`

The latest replay on the same Downloads nightly passed both gaps and
boarded the moving lift at X2253/Y145. A separate jump carried Rogue Dawn
off the lift to the far bank at X2320. She earned Wall Jump from its
authored block and kept full health and two lives.

The run then stopped outside the side pipe to 1-3. Rogue Dawn reached
X2643/Y129 with Right held and stayed there. The loaded pipe mouth showed
the expected upper `$1C` and lower `$1F` tiles. Pipe entry and the Screw
Attack acquisition remain open. This run wrote zero captures.

- Native receipt `6ecd83de61ba39f89b02eb7b5c3057376f7da26e6ea596fd770da3d6afec3a7f`
- Controller `08c7ad7fe505a05e8d3969cd992c1604c273db972d25f2411e96d66b747eb311`

The linked CPU reproduced the stall with the actual `$1C` and `$1F` side
contacts. Rogue Dawn's movement used its own terrain resolver and omitted
the native pipe entry. The source repair sends that contact to the existing
native pipe routine while preserving Rogue Dawn's movement. Standing and
Morph Ball both entered with the normal timer, sprite priority and sound
cue. Controls for blocked contacts, flagpoles and other characters passed.
The source check also covered cold startup and reached interrupt points.
Source receipt `c8f6387e5b636edc366a62343549bee19b5732e8933418635dc8cd6f0cf7997e`.

The private build `28708fa9` then carried the same playthrough through
the side pipe and into the outside part of 1-2. Rogue Dawn reached
X2872/Y144 with Wall Jump, full health and two lives. The controller
kept holding Right because the level number was still 1-2, and stopped
at the outside staircase at X2899/Y161. The next replay must recognize
the exterior area and jump the stairs before attempting Screw Attack.
No captures were written. Native receipt
`5c2839af7fdadb24c7717835db704cac29598b2457e799866a2191c3b91e9266`.

The replay now reads the loaded area type and terrain offset. This lets
the same controller switch from the underground approach to the usual
overworld movement when the pipe exits. The first exterior-only run
reached X2896/Y87 during the staircase jump after 25 completed game
updates. Health, Wall Jump and both lives carried through. Its final
check still expected the live pickup variables to be set after they had
been cleared for Screw Attack. The exterior-only check now uses the
recorded Wall Jump pickup. The full route still checks the live Screw
Attack pickup. The old check is reproducible with
`--historical-exterior-finish-diagnostic`, receipt
`eb29b2b4ef1a216da912f57c634346755c040fcefbcfbfbdeec0518e0fd510b9`.

The corrected controller passed in private Mesen with the same movement
and all 25 game loop, control step, dispatch and movement returns. It
ran 12,770 video frames and wrote zero captures. The verified receipt is
`a1b28f926ba78c15ea3eb365352b4d36281eb4e37658b79bbcc3d93ff37cb3fe`.

The same Mesen controller passed from the installed Downloads ROM and
matched that receipt exactly. Rogue Dawn entered the exterior at
X2872/Y144 and reached X2896/Y87 during the staircase jump. All
25 updates preserved her health, gear, five missiles and two lives.
The installed ROM and the test slot matched byte for byte. The patch
guard passed before and after replacement. No backup or captures were
created. The exact installed ROM is
`28708fa9a4e7dd88f1aaa72653b7d5a6ba0fb3c6d5abf544a526b09d333a884c`.

The longer linked replay passed the stairs and castle, then entered
1-3 at X40/Y176 with full health, Wall Jump and two lives. Its first
jump over the tree platforms launched at about X238 and overshot the
first landing. Rogue Dawn fell at X381 before reaching Screw Attack.
The next controller needs to land on the tree from X288 to X351, with
its top at Y192, before jumping again. The longer route still needs a
full Mesen run. Its linked receipt is
`ca490d003777f2e67c99a35abcca7bc47b61a401ca47712d27c3ea78e2e60d65`.

### The first two trees in 1-3

The revised route brakes over the first tree before jumping toward the
lower left section of the second. On the Downloads nightly `28708fa9`,
Mesen reached 1-3 at X40/Y176 and landed at X313/Y161 and X393/Y113.
The original collision routine stopped descent at canopy tops Y192
and Y144. The replay then completed 25 game updates on the second
tree with full health, the earned upgrades, five missiles and two
lives. The linked CPU replay also passed both landings. Screw Attack
still needs to be collected and used against an enemy.

- Mesen receipt `0d4839b87be509c8f8ff3a68a01e7985076cfa9dc0da7775ecd87249b58ca36e`, 14,522 video frames, zero captures.
- Linked receipt `29f15e14403b2f963094008a22002add44cdd340b0fcad9796d2aaa70d63c4e0`.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 600 -- python -B tools/audit/run_rogue_screw_trees_native_1123.py --run --trees-only
```

The longer linked run reached X730/Y33 with full health and both
lives. Its next jump overshot the lower tree from X800 to X863 and
fell short of the later ledge. The next replay needs to land on the
lower tree at Y208 before jumping toward the Screw Attack block at
X944. Linked receipt
`57febf4c8a178d31e659e983d0039abe3e39c84ec5389e7f2377f24ec8b06224`.

### The Screw Attack pickup in 1-3

The linked replay landed on the lower tree at X824/Y177 and reached
the power block at X944/Y129. Rogue Dawn placed a Bomb on the block,
collected the exposed Screw Attack and earned 1,000 points from the
native score writer. She kept full health, five missiles and both
lives for at least 25 further game updates. Linked receipt
`40f44a0b9c4dce7c00116cad8e973357a13df40cdd82a5d0e946caa8161fa8f5`.

The first Mesen run reached its 240-second wall limit without a final
receipt. The retry added progress markers to the same gameplay inputs
and passed from the Downloads ROM in 15,675 video frames. Rogue Dawn
collected Screw Attack at X945/Y129. She kept full health, five
missiles and two lives across at least 25 further completed updates.
The score rose from 9,140 to 10,140. The replay wrote zero captures.
Using Screw Attack against a live enemy still needs a playtest.

Mesen receipt
`90f7d82af3b3dcb39b9859048cd06c0d0f989b1b71d5f9573cdca48d65519863`.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 600 -- python -B tools/audit/run_rogue_screw_acquisition_progress_1123.py --run
```

## Screw Attack against a live Goomba

On `28708fa9`, the linked engine replay earned Screw Attack from its
ordinary block and continued to the next tree canopy. A fresh Right+A
wall jump activated the spin while Rogue Dawn was rising. The spin hit
a live Goomba at X1212/Y72, reduced its HP from two to zero, and put it
in the native defeat state. Rogue Dawn landed on the canopy at
X1245/Y65 and continued for 25 updates with full health, gear, ammo and
two lives.

The linked replay began from the compiled roster menu and used ordinary
input throughout. The same controller passed in Mesen from the title
screen on the Downloads nightly. The Screw hit reduced the Goomba's HP
from two to zero and awarded 100 points. Rogue Dawn landed at X1247/Y65,
then returned through all four observed gameplay routines 25 more times.
She kept full health, five missiles, one tank and both lives. The Mesen
run took 16,285 video frames and wrote zero captures.

- Linked receipt `7b4538313200ee9c6cddab3385ec2951f87d098e70ddeb0d1372560d0b3b5c9a`.
- Mesen receipt `593ea5bae1ff07f5fd6da877bc86550132e8d4745a293729747bd77896e6c436`.
- Controller SHA-256 `8ed50b13523a50c72cf1991665b4532632cf71d232ed9a31cfc4084c044ec303`.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 600 -- python -B tools/audit/run_rogue_screw_combat_native_1123.py --run
```

### Spring Ball physics on the November 26 nightly

Spring Ball follows Screw Attack in Rogue Dawn's upgrade order. With the first four gear bits set, the next normal Flower block yields item D4. The castle in 1-4 has a power block at world X480, top Y96.

On nightly `83b38793`, 960 paired CPU cases ran the Spring Ball routine from the installed cartridge and from the original Rogue Dawn 1.21 cartridge. The comparison covered fresh, held and released A, ordinary and frozen-platform support, dry and reduced gravity, and gear combinations with and without High Jump. The two routines agreed on vertical speed, gravity and the sound request in every case. These checks supplied the downward terrain result. Natural acquisition and a bounce in the level still need a controller replay.
