# Sonic ring pickups and damage

Sonic, the third Select alternate on Mr. Gimmick’s slot, collects five rings in
the opening stretch of World 1-1. Mesen confirmed the count rising from `00`
through `05`, the pickup sparkle, and the thrown ring after a Goomba hit. The
hit spends the rings and applies the original knockback and stun. Sonic
recovers on the ground and keeps both lives.

The five pickups occurred at X197, X212, X230, X245 and X260. The hit at
X317/Y176 occurred at source tick 120. The thrown ring activated at tick 128
and expired at tick 208 after 81 source updates. Sonic regained control at
tick 156 and advanced again by tick 178. The native replay checked the ring,
sparkle and thrown ring against 116, 60 and 90 rendered pixels respectively.
It matched 412 hardware OAM publications to their source draw and checked 121
completed sprite allocations, including 85 with both guest and world sprites.

An early replay exposed a block-buffer write when the native reservation
read the zero-page byte behind Sonic’s empty pose pointer. That added a
misaligned byte count and eventually rotated an OAM write across `$02FF`.
The allocator now skips the empty pose and aligns the rotation to a full
four-byte sprite slot. The CPU check compares 512 valid pose cases, 64 empty
pose cases and all 256 rotation inputs. A separate cadence check caught the
thrown ring disappearing when NES drawing sampled the donor’s hidden ticks.
The renderer alternates on eligible draw calls and uses the donor’s six art
poses. The source object continues using its original motion, timer and expiry.

Another Mesen run collected an authored mushroom, finished all 60 growth
updates, lost five rings, and recovered with the mushroom upgrade and two
lives. A separate controller run cleared 1-1 and entered active underground
1-2 with both lives. The full stage still recorded 2,162 of 4,888 gameplay
frames without a completed Main update. The five ring placements belong to
1-1. Later placements and further powerup checks remain open.

All 100 named menu entries retained their previous Start and A admission.
The Donkey Kong Jr. regression repeated all four pipe crossings and the first
gap with both lives, reaching X1136/Y176.

All three Sonic replays reproduced the same gameplay results from the exact
Downloads path. The automatic patch check passed before and after the direct
replacement. The visual test sent three PNGs through stdout and retained no
capture or backup files.

- Parent ROM SHA-256 `b031802c7bc4f4e9596683e66f2f53c124b3a3ac155b80bbec03c5965b8e4e65`
- Candidate ROM SHA-256 `36e9a6a8b2f8dfb79447c8d9e74633245dd412ede0a408d075e3df2db01b85ca`
- Reconstructed IPS SHA-256 `9ebf6513327e71f80b1a33326c6831be22b045dfb97d01692da06e655f69411c`
- Sonic owner cookie `a72b018c2e04635376b3ef263b330c8f`
- Ring replay Lua SHA-256 `628832f25a2e9ed7975b5523904ad91731be130df35f11c488cb327ddb8f1e37`
- Ring replay gameplay SHA-256 `aac201ce41ac6813019c3ba7f6c743ba0f99e098272d6c823a76024e58535d2b`
- Mushroom replay gameplay SHA-256 `b778e53418a779c17f1c362eb730a3e7f87fe903f60b5495e1c9a1a9aedbafa7`
- Full-stage replay gameplay SHA-256 `49fec282e56af7bb399c47e4a85da0d8e31fef52dcd694ae130d3d342a9169a5`
- Donkey Kong Jr. replay receipt SHA-256 `91423d245b6557774ac86f9d7e87d409fc87f19ad44168738f1537deb7020ae0`
