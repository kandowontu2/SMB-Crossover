# Karnov natural Bomb route

The original collector requires four healthy ordinary powerups to reach Bomb.
The first two-pickup route changes no ROM bytes. Root has delivered the
qualified scene-motor fix as exact Downloads
`a3c5fa63872fbb3103ae57d9748fef233e8b2273e26d985aa4006b2492d81b8a`.
Its exact inverse reconstructs65ee94ca, whose Thomas-only inverse reconstructs
318a087. The natural pickup/option code and manual-platform bank remain
unchanged; the motor fix and both owner cookies are separately scoped below.

| Pickup | Physical item | Original source result |
| --- | --- | --- |
|1|Mushroom|AD79 advances single shot to double, source65 low bits1|
|2|Flower|AD79 advances double to triple, source65 low bits2|
|3|Flower|EF61 option0: Boots stockBD1, selected0, cycleC860=1|
|4|Flower|EF61 option1: Bomb stockBB1, selected1, cycleC860=2|

An injury spends a pickup on original health recovery before further shot
advancement. The route therefore requires original health bit80 to stay clear.
The four-collector CPU fixture supplies only explicitly declared native mature
item actors. It never seeds source shot level, cycle, ownership or stock. Its
actual InitScreen same-life area fixture retains shot2, Boots, stock and cycle1
before the fourth collector grants Bomb. This is source progression/scene
evidence; those actor fixtures are separate from natural gameplay evidence.

The current source level streams are present byte-for-byte in the ROM. The
planned natural blocks are **1-1 left336/top144**, **1248/144**, then
**1-2 left160/top144** and **left1104/top128**. Source stream bytes are5700,
E700, A700 and5604 respectively; the last is a brick containing the ordinary
powerup. The base jump repeatedly peaks at nativeY128 from groundY176;
its feet cannot mount the row at144. The route uses Karnov's existing user
control **Up + Select** to summon a native vertical girder before each elevated
flower. It grants no inventory and does not change jump strength or geometry.
The same helper constructor was already delivered; no new fixed placement is
added to the ROM.

The shared Lua controller uses genuine menu Left/Select/Start, native block
production, immature-to-mature item observation, actual mapped
HandlePowerUpCollision entry and its matching stack return. Items require
the native Karnov preparation tags. It fires original crouch shots to clear
ground enemies, including enemies behind the retreat. The file contains no
emulated-memory write, screenshot, state-load or file-output operation.
After four collections its default route uses actual Down+B and observes the
Bomb's fuse and explosion; that later endpoint remains unqualified below.

**Actual Mesen supplied by root:** the two-pickup prefix passes on exact
Downloads65ee in3492 physical frames /1668 committed updates, both lives,
health0 and shot2. Mushroom collection is frame1340/update500 at X401/Y176,
actual actor413/164. Flower collection is frame3491/update1668 at X1251/Y96,
actual actor1248/119. Manual helper creation is frame3246, native ID25,
**1-1 left1201, center1217, initial top208, width32**, slot0,141 actual carries.
Existing fixed pipe helpers remain **1-1 left688/center704/top208** and
**left872/center888/top208**, width32.

Root receipt:
`55c1f5d3b097377b190f836cb213ed7f31a0736dbdc9ec5d3054638dd6f45a23`.
Exact generated two-pickup controller:
`88ccc41014cea57d2e95e48833f27291f7bf566356481362c4cbbe08b6f0eba4`.
The CPU model independently passes the same controller at1787 Main/NMI
updates, natural mushroom/flower and the same initial helper position, ending
shot2/health0/lives2. CPU scheduling does not establish native cadence.

Reproduction API:
`check_karnov_natural_bomb_1113.controller(raw, stop_after=2)` returns the complete
standalone Lua string without writing a file or ROM. The checker also accepts
`--write-controller PATH` under root's bounded one-file reservation.
The qualified two-pickup source is frozen in Git commit66e595f3. The current
two-pickup binder reads that immutable Lua blob and asserts the exact88ccc410
script hash on65ee, preserving reproduction while the later route changes.

```
python -B tools/audit/run_bounded_build_v1.py --output build/karnov-natural-bomb-cpu-1113 --max-files 1 --timeout 600 -- python -B tools/audit/check_karnov_natural_bomb_1113.py
python -B tools/audit/run_bounded_build_v1.py --output build/karnov-natural-bomb-cpu-1113 --max-files 1 --timeout 600 -- python -B tools/audit/check_karnov_natural_bomb_1113.py --route --stop-after 2 --limit 2400
```

Both completed runs generate zero files. The three-pickup continuation found
a genuine same-life scene motor reset defect, repaired by the separate
`compose_karnov_scene_motor_1113.py` candidate. See
`docs/qa/karnov-scene-motor-1113.md` for exact code/cookie scope and controls.
The controller's initial underground dispatch erroneously checked water
AreaType0; its corrected dispatch uses actual underground AreaType2 and waits
neutrally for the authored entrance fall. With genuinely neutral input the
old ROM still dies after seven source updates, proving a game defect beyond
that controller correction.

**Actual Mesen supplied by root:** private scene-motor candidate
`a3c5fa63872fbb3103ae57d9748fef233e8b2273e26d985aa4006b2492d81b8a`
passes the complete natural three-pickup route in9781 physical frames /
5594 committed updates, source health0, shot2 and both lives. It clears1-1,
survives the normal1-2 entrance, spawns/matures/collects the authored flower
at160/144, then grants original Boots: cycle1/owned1/selected0. Actual
collection is frame9780 at playerX163/Y96, actorX160/Y119. The existing
Up+Select helper is created in **1-2 left112, center128, initial top208,
width32**, slot0, frame9529,143 actual carries. The same1-1 manual helper
remains left1201/center1217/initialtop208; fixed pipe helpers remain unchanged.
Root receipt:
`4d0e7e4ffbf11b56b4aad0f18d87da629804d00f7993de9499687a8fe96b90e0`.
Complete three-pickup controller:
`57763e630aeae8ea0a0792646dd200bec841410b72942b1d1cde89af96754f35`.
Its Lua source is frozen in Git commitf19ecfb5. The binder reads that immutable
blob for `stop_after=3`, independently of the continuing fourth-pickup source.
The complete CPU route also exits0 after5675 updates, same script SHA,
source shot2/health0/cycle1,1-2X162/Y97 and both lives.
Root repeated the exact same native receipt from Downloads and published
Current/Latest sole IPS57b84a6d; see `karnov-scene-delivery-1113.md`.

The first four-pickup/default0 continuation is deliberately retained as a
negative controller diagnostic. Script
`1f8a0ad07b60d2c6aeb4b8d5b39ca876cc33701edb540d06e25f7a67b9d4b36c`
on actual Downloads passes all first three pickups, then genuinely activates
earned Boots at frame9794/update5603, X163/Y112: stock1→0, ownership1→0,
source65 bit80 set. It reaches the fourth brick region healthy with both
lives, but its unnecessary lift directly below the brick carries the player
past the required underside bump. Native diagnostic helper is **1-2
left1089, center1105, initialtop208, width32**, slot3,1533 carries. Terminal
physical bound24001/update14431 is X1151/Y48, cycle1, Bomb0, no fourth birth.
Root negative receipt:
`a2d7c0656d7b98ffe70562d89ac5426e228e45fd787d6e0bfd14355ccb3fcbc9`.
CPU independently reaches the same healthy missed-bump endpoint, and the
actual1104/128 cell remains unconsumed tile5A. This is a route setup failure;
no additional ROM change is indicated. The next controller will approach the
brick on the ground and use a fresh original jump before summoning its
separate flower-collection lift.

The second default0 diagnostic removes that lift and waits below the brick.
Its actual native scriptdd3f491dd5bae9e49e443db7ef3e960ea11ea1797efb8f2cdc1b4e4116a0ae91
reaches X1097/Y176, then takes a later ground-enemy hit before a fourth birth
(source health192, both lives, frame12392/update6932). Receipt
425ade54c67c983c8034baf804bcef641cb8012e3b6c0f42255e57aedd93ea50.
CPU reproduces it. The observed block column has ordinary masonry52 at144
directly below the desired powerup5A at128. Karnov's head policy deliberately
keeps ordinary bricks intact. His already-integrated original fireballs use
KrCombatBlock and a real native MmBlockAttack proxy to shatter masonry and
activate powerup bricks. The next controller uses standing B pulses during
the jump and continues clearing incoming enemies; no ROM defect is claimed.

The jump-plus-fireball diagnostic8a9ef998d23ccec51bfc137972cf1d0886cb5bb7dce2ccbbf37a7afa1a02df3c
keeps full health and both lives in actual Mesen, but hits the480-update
fourth-bump bound with only three births (X1097/Y176). Receipt
159ab83104f48f8957d4f1bf6b9071a1bb2ca74a62cbf5ca0449e9298dfe4c2e.
CPU with the identical script does shatter the lower brick and reveal/mature
the fourth flower, then misses collection because the helper is displaced
by adjacent masonry. CPU/native timing equivalence is therefore not claimed.
The next replay adds read-only source projectile/block and native head traces
before further control changes.

The read-only follow-up controller is prepared, with unchanged controls and
script `6b90a9c2d516680b5520f42aaa06fa837de6c47290fdf17e3bf2f5cf903dc236`.
Its final receipt retains bounded native/source frame samples, actual C2
KrCombatBlock CAF0 projectile contacts and mapped native head-core BE97 calls.
Samples include actual shot worldX/Y, queried tile, source selector/jump timer,
native input/facing/DY/R4, lower/upper target cells, active projectile records
and minimum jumpY. Root has not run this follow-up: its native capture guard
currently rejects new runs because C: free space is below the existing25GB
floor. The published nightly and qualified three-pickup replay remain intact.
No source/game defect beyond the delivered scene reset is asserted from the
CPU/native fourth-pickup divergence. No CPU process or generated output remains
active for this source task.

Fourth natural flower/Bomb acquisition and use remain pending. Ladder, Clapper,
Glasses, Swimming Mask and Shield remain required integrations, along with the
broader original equipment/audio and roster obligations.
# November 13 native fourth-block follow-up

The prepared6b90 trace was subsequently run on installed parenta3. It ends
at the fourth-block bound, full health/both lives, with minY176: no jump is
ever admitted. Receipt
`414ac792099408aa81dfaba93f0f009af2f4406093e372a43370290df5928a3c`.
The input callback could be polled repeatedly in one logical epoch: setting
lastPulse in the first poll consumed the intended one-poll A press. This is
a replay defect, not a new ROM movement defect.

Holding A for six logical updates corrects admission. At the original
X1097, the small head now bumps the masonry atY144 and stops at nativeY151;
the upward fireball passes the target column too late. Held-A controller
`cb1a3c342be6522fd3def1363c0d314822a25254c07860b674e6c79a45738524`,
receipt `64b745a0ca2b32ec9cb2e911aec45c8fcac168e1cefcba20426cee17e7f8554d`.

Firing from16 pixels farther left, X1081, puts the original upper fireball
through the lower brick at1104/Y144. Its permanent tile becomes0, then a
new under-block jump atX1103/Y134 hits native5A and reveals the fourth
flower. Controller
`b054d7540053f288f01d012299b29e646e08255aa98cc9220da1a5f613019481`,
receipt `a1da4978e0ec913305b7e00e791f35b0e54c7526a6856ccdf914b092b851ac62`.
The generic flower-lift setup remains unsuccessful: physical bound24001,
X1103/Y176, full health/both lives, three collected items, Bomb not earned.
Minimum observedY134. No new fixed helper or gameplay byte changed. The
next step is to inspect the actual fourth-flower/lift terrain and camera,
rather than claim acquisition from the head-reveal proof.

Frozen stop-after2/3 recipes still reproduce their original controllers;
the existing qualified3-pickup controller remains57763. After the Quick-only
nightly4641 delivery, the audit explicitly authenticates that image through
`compose_quick_climb_material_1113.inverse` to exacta3 before its established
Karnov ownership checks. This does not claim a repeated native4th-item test
on4641. No captures or extra build files were produced.

# Natural Bomb acquisition and use verified on4641

Current Downloads4641 now passes a complete controller-only sequence:
natural mushroom→double shot, flower→triple shot,1-2 flower→Boots, next
flower→Bomb. The original Boots are activated and consumed. The fourth
flower emerges, matures at1104/Y103, and is collected at nativeX1116/Y90,
granting cycle2/owned2/stock1/option1. Down+B consumes the stock, the armed
and explosion phases are observed, and the bomb retires to0 normally.
Terminal12756physical/7112updates: full source health0, both lives, shot2,
cycle2, stock0, bomb0. No game bytes changed.

Frozen controller SHA256:
`dc93477b7397473a57af3660b1bd6bc993541da645bced10b50b4c6f061f3bcf`

Actual Downloads Mesen receipt SHA256:
`edfa6bfe7aa2f1c2d9ccc7b56f60bfc5558ab42a88ab82b499819efcbf48f141`

The new fourth-flower approach is based on a read-only actual native terrain
probe, receipt `d353722063dea877262879282c7b9ce33f4e8ab5b1da8a0cc2bc187cb52baaa9`,
controller `94fa3b0c0247745c8aca83f6674c86a21da8cddf8c5b2bba936ecce33a19523d`.
At camera986, west column1072 has masonry80..144, while1136 is clear.
Approaching with the existing summoned vertical girder from the east avoids
that masonry. Its actual1-2 placement is **left1127/center1143/initialtop208,
width32**. The two earlier manual girders remain1-1 at1201/1217/208 and
1-2 at112/128/208. Inventory records them as controller-created actors.

The previous east-approach run had already collected the Bomb and reached
explosion130 but was falsely stopped by the ordinary240-frame travel-stall
observer while waiting stationary. That observer now applies only before
the fourth pickup. Receipt22325f46 remains a negative observer result, not
a frozen Bomb. The successful run has zero native bomb/enemy contacts;
it proves natural acquisition/use/retirement, not a new enemy-damage case.
Native prepared-enemy Bomb damage has its separate older fixture evidence.
Star/1UP and remaining original equipment/audio still need qualification.

