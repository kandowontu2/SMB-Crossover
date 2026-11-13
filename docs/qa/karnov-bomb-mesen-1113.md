# Karnov Bomb emulator verification

The private composite `0935e6c22725c008d88c3d249aae7c4c8a30cf11d87e221e2ffaef544cc088ed`
combines the Thomas flower lift with the initial Karnov Bomb implementation.
The installed nightly remains `15a683321cde608cfe15447e90ef58d5295a16a1a6b607434f98df37162ac533`.

The actual controller-only stage replay cleared 1-1 into 1-2 with both
lives and no death, in 8,768 gameplay frames. Its receipt is
`51cc77887a195086c8915cbb665f72ae089086ca70553813b17e1751764baf6c`,
script `8f00e5a93e3e64ae1cb46ed1beb71fd2f095a4ea5ce7c1aff167464db542c203`.

The stock fixture enters through the actual menu, then supplies the selected
equipment, Bomb ownership bit, and one BCD stock unit by writing only source
offsets `$8E`, `$8F`, and `$BB`. Real Select and Down+B arm the Bomb. The
native update consumes the stock and advances phases 128,129,130,131,0.
Hardware OAM shows the original armed and explosion patterns. This fixture
keeps both lives. Natural acquisition of Bomb stock remains open.

- Lifecycle receipt `17a87f7b2b84403471c557560df65a918163b7e215de84776415709ef09ba9c4`
- Lifecycle script `c6670df58572ee0494e005f3a958a8ed0fb3507d778722ce6b0e0a498de96168`

The first enemy-contact fixture found a real host-coordinate error. The
Bomb sits at world X247, source Y208, and draws at native Y192. A natural
Goomba passes through X244,243,235 in the explosion phases. Its native Y184
draws Goomba tiles162/164 at OAM Y192. The adapter measures its top at
184+8=192, giving a difference of16 against the original exclusive limit16.
Thus the visible ground explosion misses the nearby Goomba. Source renderer
inspection then established the donor enemy's anchor at its bottom edge.
Its original two-cell record renders from anchorY−16 through anchorY−1.
The native Goomba renders from nativeY+8 through nativeY+23, so the equivalent
bottom anchor is nativeY+24, or208 in this case. Its horizontal anchor is
eight pixels from its native left edge. These conversions are being checked
against the original donor rectangle before updating the candidate.

- Ground-contact negative receipt `53d9ca0ed1d5f2da86a07bb9b9c2f811ebed74d9b30a0444125c4c7fca2737b1`
- Ground-contact script `a547e8262f1c4dbeb7b44eb4aa53178cb90dfa9d0f309bbc14f85023b207ad9a`

Root reuses one candidate and one Lua controller. The explicit stock fixture
reserves one capture receipt and permits zero payload files. Five capture
budget tests pass, covering ordinary success, the one-file reservation,
unexpected payload rejection, process termination on growth, and lease
exclusion. A first attempt was refused before launching because the older
capture runner reserved all64 file slots. The optional smaller reservation
now matches the fixture's output and enforces that smaller payload limit.
No screenshot or video was produced.

## Corrected and installed build

Candidate `318a087735b4204c74274b4107efbc302bc15a674a7f6f9d3bed598cea90d08d`
converts native enemy coordinates to the donor's horizontal center and bottom
anchors with offsets8 and24. It retains the original unsigned32×16 test.
Actual donor and native renderer comparisons establish those anchor offsets.
The complete CPU suite passes the original predicate, timer, rendering,
camera, lifetime, readback and interrupt checks described in
`karnov-bomb-native-1112.md`.

The same ground-contact fixture now records one native Bomb defeat at SP230.
The Goomba rises from nativeY184 to179 and163 after the hit. Stock is consumed,
all fuse/explosion phases and OAM pass, and both lives remain.

- Receipt `c912b6e0ae1f5e575152b3dd5f41d95378ec2c6769a8c0fd46e5331d8b38bde4`
- Script `da2b3d7f6901062f70b2109f327e733bf8a03935943f57fe1c2ee62bc424d0a3`

The corrected build also passes a separate controller-only full1-1 clear
into active1-2 with both lives and8,768 gameplay frames.

- Receipt `2465de711f1e543e967b95fdde2fd83c6c7ab93bbdf56e2c5f5020fbe169e6a0`
- Script `b523871d75d9fa921d5efc52cc8946f01fe0085dd79cb9781826df836a37ec12`

Downloads was overwritten directly with this build. The stock/contact
fixture repeated with the exact same receipt from that launch path. Before
and after patch guards pass with no matching sidecars. IPS reconstruction
equals the tested installed ROM, with IPS SHA256
`2588d7bde413c7464b2695a6c91ac4d47f3dcad83e63511a6d9801e886d3d1dd`.
The delivery recipe restores the exact previous parent from authenticated
existing carrier inputs, then proves forward composition and inverse.

Natural Bomb stock acquisition remains open. Ladder, Clapper, Glasses,
Mask and Shield retain their original required integration scope. No helper
locations changed in this delivery. The Thomas flower lift remains present.
