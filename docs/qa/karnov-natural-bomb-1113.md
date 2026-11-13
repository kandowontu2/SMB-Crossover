# Karnov natural Bomb route

The original collector requires four healthy ordinary powerups to reach Bomb.
This work changes no ROM bytes. Current Downloads is
`65ee94ca9ac6e1b5ad44303d08f76ecbc175a88232c82ef8c32712edf150a643`.
Its Thomas-only successor is authenticated by exact inverse to318a087 and
forward roundtrip; every Karnov carrier and the manual-platform PRG bank
remain identical.

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
planned natural blocks are **1-1 left336/top144**, **1248/144**, **1744/80**,
then **1-2 left160/top144**. Source stream bytes are5700, E700, D300 and A700
respectively. The base jump repeatedly peaks at nativeY128 from groundY176;
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

```
python -B tools/audit/run_bounded_build_v1.py --output build/karnov-natural-bomb-cpu-1113 --max-files 1 --timeout 600 -- python -B tools/audit/check_karnov_natural_bomb_1113.py
python -B tools/audit/run_bounded_build_v1.py --output build/karnov-natural-bomb-cpu-1113 --max-files 1 --timeout 600 -- python -B tools/audit/check_karnov_natural_bomb_1113.py --route --stop-after 2 --limit 2400
```

Both completed runs generate zero files. The current three/four-pickup
continuation is still being qualified; neither natural Boots/Bomb acquisition
nor native1-1→1-2 equipment retention is claimed yet. Ladder, Clapper,
Glasses, Swimming Mask and Shield remain required integrations, along with the
broader original equipment/audio and roster obligations.
