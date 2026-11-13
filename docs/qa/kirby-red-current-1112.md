# Current nightly: naturally earned red shell

Actual Mesen run passed on Downloads ROM
`cebb0ae64b4e6cc92e473a239cb8fd4011d54cfd5e6814013a3afbd2de2bf7d7`.
Normal controller input selected 4-3 through the existing level-select cheat;
all other cheats stayed off. No RAM writes, injected enemies, captures or videos.

Kirby inhaled the naturally spawned Red Koopa from world X448 facing left,
captured it at frame1257, and swallowed with Down at1260. Health remained6,
lives2. The air-puff descent preserved red-shell copy3. From X597/Y160,
Kirby fired right at1718 and hit the later authored Red Koopa at1721.

The shell advanced X616,619,622 at ages1,2,3 (3pixels/update). Its rectangle
overlapped the native enemy rectangle. The actual native defeat routine ran
for the intended enemy slot3, setting defeated state34. Run ended frame1722.

- Receipt SHA256: `315012ca2e04e429f269e689494c578976c02be0e794bb5ee058e76a69c59cd0`.
- Controller SHA256: `1aca4ca510ef3e3934f347391e6b9faadda4172ecaba939c4b27a6c65a134a4f`.
- Replay: `tools/audit/replay_kirby_red_current_1112.py` through bounded runner,
  output `build/kirby-red-current-1112`, one temporary controller, no captures.

This proves acquisition and an outbound hit against a naturally spawned enemy.
It does not prove return flight: this shell was consumed on impact. Full4-3,
underwater behavior, all enemies and all copy powers remain outside this run.
No ROM change or new nightly delivery was made.
