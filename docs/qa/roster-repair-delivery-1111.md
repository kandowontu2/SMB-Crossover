# Roster flicker, Giant startup, and Prince footing

## Mini Mario and the roster

The installed predecessor `e6b152e2` drops the full roster heading at
physical frame 301 when the eighth Mario Select press displays Mini
Mario. The heading returns truncated at 266 lit pixels versus 405
before selection, and it stays truncated through subsequent navigation.
The delayed NMI restores background CHR and PPUMASK during visible
scanlines 34–40.

Mini’s owner-specific palette write assumed the final three bytes of
the VRAM queue were colors. The compact queue puts the palette first
and the cursor last. The old code overwrote the cursor address, length
and value, turning the cursor command into a 22-byte nametable write
across the heading. The fix checks
the actual compacted palette shape and modifies its two changed colors.
The third color already matches Mini. The queue length, cursor, Mini
name, and CHR968 sprite remain intact. The standalone CPU check
exercises all 65,536 page and length values.

The full Mesen menu sweep uses the current compiled slot and alternate
routes, 135 actual Select and D-pad transitions. The combined candidate
keeps the heading pixel-identical, with no transient anomaly in the
sampled preview, grid or name regions and no visible-scanline writes
to the monitored PPU mask and background CHR registers. The sweep uses
no screenshots or per-frame files.

- Predecessor receipt `65b3ee0ce4baaced6eccc0800ad4fd22fd63feeb596fe0c4675d31bfe613f097`
- Combined receipt `e844ad71ed50db8043aa719d4711f154f5215054a8c5bda12af7ca61f1bba46a`
- Controller SHA-256 `2c3c9c267a0e94950183031d8e85bd54dcdb55d0f71d61cb732e56c14904190a`

## Mega Giant Mario

The prior cold worker read the wrong CHR rows when Giant passed its
legacy descriptor. The corrected descriptor loads rows 214 and 212.
In the combined candidate, Giant draws with the intended 46 sprite
parts and clears 1-1, reaching X40/Y48 in active 1-2 with both lives.
The route reaches the flag at frame 2321 and 1-2 at frame 3512.
[Root cause and standalone checks](giant-cold-descriptor-repair-1111.md)

- Combined receipt `108b755260e4b3e0548e178e644f19404f3c6b995e1d9ef7617783b1d22507cc`

## Prince of Persia

Prince reaches a real foothold on the exposed question block after
the ordinary brick pair. He holds X1731/Y112 through 20 neutral
updates, then a separate replay jumps past the two live Goombas and
reaches grounded X1853/Y176. Both runs retain 4 HP and both lives.
The full stage remains open. [Geometry and CPU checks](prince-question-ledge-1111.md)

- Combined neutral receipt `c34792eacb57239a84d592599dad376f7f19fe7be5b62060c691c700376d74db`
- Combined Goomba receipt `d429efa0d32b51e92d841fad95d9ec1bcb32c1904ce9a9ced3a096590ff5bf22`

## ROM binding

- ROM SHA-256 `677aad54c55f829d9e7b2aab9e2b1f4eddebcd3c6e6532eeddd9f2ce4e1a26ab`
- IPS SHA-256 `0c7c0b82a204bcd53a42e9e84abc1575fee7791a6867a06158de17aa83fa06ae`

The three independently composed changes have no overlapping bytes.
Prince changes 11,809 packed bytes, Giant five descriptor bytes and
Mini 31 menu code bytes. The recipe reconstructs the predecessor in
memory and regenerates the exact combined image.

All four Mesen receipts above repeated byte for byte from the installed
Downloads ROM. The patch guard found no automatic sidecars before or
after replacement. No backup ROM was created.

[Candidate replay](../../tools/audit/replay_roster_repair_1111.py) ·
[Delivery recipe](../../tools/audit/deliver_roster_repair_1111.py)
