# Steve Hermann’s original movement in the MMC5 nightly

Highlight Mike Jones and press Select twice for Steve. His walking
acceleration, reversal, crouch and variable-height jump now use the
Shatterhand movement routine. The crossover still supplies level terrain,
camera, damage, enemies and scene transitions. B retains his original
punch timing and fist graphics.

From title, the Mesen replay selects Steve, checks that holding B creates
one punch, defeats the real first Goomba with a fresh B press and checks
the native score at the defeat. It observes 12 matching fist cells across
OAM DMA. Steve crouches for six sampled frames, hits the first pipe at
X433/Y176, and stops with native X speed and scroll both zero. The
following update imports that correction before accelerating again.
Right+A then crosses the pipe with an apex at Y107, lands at X488/Y176
in 52 movement updates, and retains both lives. The replay observes 537
authenticated movement projections.

The candidate and installed Downloads ROM produced the same Steve receipt.
The installed Prince neutral-brick replay also passed, matching the prior
gameplay receipt after substituting the ROM digest. Its exact installed
receipt is `95ba14daa42ec2062f46b24ca94b4fc9ecd64cd4eab784ec80b19575d9b7e78b`.
The patch guard found no same-name sidecars before or after installation.
The nightly was replaced without creating a backup.

The [CPU and donor checks](steve-shatterhand-move-live-1111.md) qualify
467 actual Main updates, both punch directions, native collision, foreign
Mike/Jay behavior, 32 bad header fallbacks, five nonwalking fallbacks
and interrupt cuts. Steve’s port still uses the existing body renderer.
The full stage, armor and companions remain open.

- ROM SHA-256 `e6b152e26b43449115a7ff21903ae756346052e55dbdd94d8751e8c3a0951f23`
- IPS SHA-256 `e866c1260204115be1de66474d44fcb8ae19e98ee6ea165409e92d88589f19ca`
- Mesen receipt SHA-256 `cfca6b729fb654f4e30de0020b09aef64e3be3250fe5ad90513268c499ab35d5`
- Replay tail SHA-256 `33731436eb8e721ee2a022e6fbe14438965a2eb9525c7485ad8e0459591cc851`
- Assembled controller SHA-256 `36b59dc6064fde3b93c6029966ab10f84e6003a3a69d67451c7a55c9c707862c`

[Physical replay](../../tools/audit/replay_steve_move_native_1111.py) ·
[Delivery recipe](../../tools/audit/deliver_steve_move_1111.py)
