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

## Follow-up: return flight and remaining defect

`--return-flight` now releases B after the enemy hit, waits60 physical frames,
then presses B for6 frames. The earlier20-frame delay produced no second shot;
that timeout was controller timing, not evidence of broken return physics.

The second naturally earned shell starts X619 at age1, moves right at3px/update,
then returns left at3px/update and reaches Kirby at X600. Health6/lives2 remain.
It expires at frame1874. Receipt
`02acc9f7fd773cdd41a1e2de3d88d85c2b5f1c822e76ece460a112ccc1679033`,
controller `c14d7413ac5f34415527747dfb6fcecdd5bc92f2e0662ad2e949e69c1fa8da4c`.

**Remaining defect:** after reaching Kirby, it oscillates X598/X601 at ages68..89
instead of retiring on return. The replay's `passed` means travel/return/expiry
were observed; it does not certify this visual behavior as acceptable. The return
observer must be tightened when catch retirement is implemented. No fix delivered.
# Explicit catch regression on the November12 nightly

## Delivery

The catch candidate below is now installed directly in Downloads, with no
backup. The Downloads launch repeated the strict catch replay with exact
receipt `0ba2031f64825b6188e67ecd7d6f849c70c365af5ba0e5072f61b3001e9128f6`.
Patch guards passed before/after, and IPS reconstruction equals the tested
installed bytes. IPS SHA256:
`55381d7bfb47beb05d00863d072e04b365be48b97ae731e16b03ceb02608f86d`,
2,099,506 bytes. All source/control/contact/interrupt/lifecycle checks passed;
root independently repeated243 TTL comparisons and three mixed-slot cleanups.
The older candidate-pending text below describes the pre-delivery checkpoint.

The private catch candidate
`f228e61399432c1a205b8f5ac6dad13d990515f9c2e2f5024bcd5ce443c76653`
passes the same strict controller in actual Mesen. Receipt
`0ba2031f64825b6188e67ecd7d6f849c70c365af5ba0e5072f61b3001e9128f6`.
After the natural enemy acquisition and first-shot defeat, the second shell
returns X613→610→607→604→601 at ages63..67 and retires at frame1852;
Kirby retains copy3, HP6 and both lives. The baseline instead oscillates until
age89. This candidate is not installed yet; remaining CPU regression gates
must pass before delivery.

`replay_kirby_red_current_1112.py --expect-catch` now distinguishes an actual
catch from eventual shot expiry: the returned shell must retire within two
updates of reaching three pixels from Kirby, before the89-update expiry edge.
The currentc5ce8c nightly correctly fails this new check with
`return-shell-not-caught`, receipt
`7ab8497b5bb817a63db45352519bec7d44b651e3a409b553c8385ddcbc6372b8`,
controller `c76e0e3236aa81a845d47c06a81605072d9f1930f7a4a26f8ab0464a862190c1`.
The natural first red-shell shot still defeats the real red Koopa; Kirby
retains copy3, HP6 and both lives. This is a reproducible negative regression
for the pending catch fix, not a new ROM change or a passing catch claim.

