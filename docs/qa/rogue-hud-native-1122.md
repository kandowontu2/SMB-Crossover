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

Missile and Bomb impacts on enemies and breakable bricks remain to be tested,
along with the remaining upgrades and the full sound and performance review.

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
