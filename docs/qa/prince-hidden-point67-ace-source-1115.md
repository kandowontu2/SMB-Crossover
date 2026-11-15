# Prince hidden body-point repair on ACE

Source-only implementation follows grant `8bf7fb86…`. The exact parent is
`aceedaf2151fdf673b489a742831a0844abbb3837e0bcba68408d3ba5c3a4cfe`.
The in-memory candidate is
`7fb328a6dcf6b50fd000e81eced4fd4b7390bedec56085d33130434003cc76d0`.
Only stream 0 [4880,4947) changes: 67 owned bytes, 61 changed. Every other
decoded byte and all physical bytes outside the existing Prince carriers
and cookie are exact, preserving all 714 carry and 52 Bub changes. Packing
is 6467/5995/1263 with 579 spare bytes; only header word 2 changes.

Initial composition receipt: `062f5ca9286eefcbd370f029fa9a3dafccfd799e47d192582bf1efe3656c5b4a`.
Physical changes total 9,907 bytes; the composer reports exact contiguous
changed spans. The inverse restores the inline 67-byte preimage and requires
the exact ACE hash. No ROM files or emulator runs are authorized in this lane.

Cold checker session 1423 initially rejected an observer ordering assumption:
first BBC1 can occur before the first PointRead. This is not a game failure.
The successor checks first publication cookies and the complete 67 bytes at
the independently reached first B310, before its SMC operand changes.
Session 40061 then rejected the checker's native-bank tag spelling: this
model encodes PRG banks 126/127 as tags 254/255, while RAM bank tags remain
unbiased. The successor checks those actual tags and the owning leaf bytes.
Neither fixture failure indicates changed gameplay.

Cold session 40077 passed, receipt
`0a91e414091121bf1df8dcdffb6ba245ddb17bee7b8f83bff79567be728d7f47`.
First B310/SP189 checks all 67 bytes before SMC, both cookies and actual
maps [254,3,2,255]. The native leaf is reached at SP186/188 and returns B33D.
All observed constructors retain 79 exact bytes. Portable inverse and four
strict unknown-input rejections pass without mutable Downloads reads.

Same-control route 68208 closes the false-wall gate, receipt
`8589381b0bb11432fc4f4cd188d7d3af725a547acafd878736bd5022e5059fe2`.
Actual hidden queries return A0/C0/classified B36D0, matching material calls
return neither kind20 nor Wall1, and the old C427 backtrack is absent.
The unchanged standing-A policy still lands without a natural 1UP birth;
that acquisition remains negative. Frozen controller Lua is `461dd1ab…`.

Initial full source 89226 stopped before Main1000; the first checker asserted
before printing the returned negative reason. Its successor prints the
compact negative before asserting, and isolates public-component clones
from the route's Lua CPU callback subclass. No full-pass claim is made.
Session 14436 recovered the exact fixture cause at source update 2: the
checker patched the budget frame module but omitted the route's separate
Game.Frames alias, leaving partial Main sampling. It failed "Previous
complete Main returned" with wrapper Main=0. The next checker patches that
actual route alias and keeps the complete-return requirement intact.

Reached point/native-leaf paired ISR session 88838 passed, receipt
`2e6c4550c4695490a7ede4ea46664d0935804aa3d1ce6cec5a2bfd640921d4ba`.
Candidate and baseline (only old 67 bytes restored) execute identical current
IRQ/busy-NMI paths and native audio/stack effects, with exact private RAM,
live caller stack, transport and maps. There is no native-RAM allowlist.
The reached scope is genuine cold plus 320 ordinary neutral/Right Main calls.

Remaining source gates: real cold/readback, same ordinary hidden approach,
head and sweep contracts, reached interrupts, full route, natural M/F/Star,
and public lifecycle components. Natural 1UP acquisition remains open.

## Completed source qualification

All required repair regression jobs are terminal with zero output files.
The entries above retain the initial fixture negatives; they are superseded
only for the corrected observer/driver scope.

| Gate | Receipt | Measured scope |
| --- | --- | --- |
| Actual cold and portable inverse | `0a91e414091121bf1df8dcdffb6ba245ddb17bee7b8f83bff79567be728d7f47` | First B310/SP189, all 67 bytes before SMC, both cookies, constructors 79 bytes, native leaf mapping and strict input rejection |
| Actual encoded transport | `eaf641e172d05f9c957ff5253e708791d3d7df214cb68d8bebbc7c13ba137091` | Every decoded byte exact: 8159/6112/1607; overlapping-stream unread margins 414/163; no array mounts |
| Same ordinary hidden approach | `8589381b0bb11432fc4f4cd188d7d3af725a547acafd878736bd5022e5059fe2` | Hidden A0/C0/B36D0, no matching Wall/kind20 or old C427 backtrack; natural 1UP policy still negative |
| Native head and sweep primitives | `00950191d1d1a3ee4f55205d5e89df0fd185f9ea3b9e99740fff0ef15bb37179` | 42 compiled head queries retain raw 5F/60; 4096 sweep pairs, including real pipe solidity and unchanged nonhidden/vine admission |
| Reached IRQ/busy-NMI | `2e6c4550c4695490a7ede4ea46664d0935804aa3d1ce6cec5a2bfd640921d4ba` | Genuine point/native-leaf cuts; exact paired effects, private RAM, transport and live stack; no masks |
| Full ordinary route and lifecycle | `c0392747b46b050e0734c485611cb033792aa112b6b0ea7e231d1c8bd9cb52c3` | 8644 Main entries=returns, no pending Main, full 1-1 and 25 living grounded returns in 1-2; terminal 40/176, HP5/lives2/native2/Sword1 |
| Natural Star | `f8bad8f45d75c0cb8b2e58804bd7188fa068faf3d3783e85d8d5c3681aae6039` | Birth3853, mature3918, physical collector3989, score credit3994, exactly 25 returned Prince updates to4019 |

The full route genuinely earns Mushroom and Flower. Its earned Flower
checkpoint is native tier2/Sword1/HP4/lives2 at1260/112. Warm32 and the
compiled ChgAreaMode component preserve the sword through 243 Main calls
and 25 active next-area calls. Explicit KillPlayer sets native tier0/engine11;
Continue and menu components also reset native tier0. The menu component
uses the declared rendering-off setup because the source peripheral lacks
physical vblank. These are public-component tests, not natural death/menu
gameplay. No upgrade or health state is seeded.

Star uses the real actor: collector C7B3/SP219 has positive4x2 overlap;
actual erase and popup6/cue32 occur, then the target timer credit changes
score2600→3600. Endpoint is actual Main return82BE/SP252, with Main and
Prince entries=returns4019,1696/176,HP4/lives2/native2/Sword1/Star33.
First BBC1/SP203 verifies both cookies and4193 static bytes; the separate
first B310 witness verifies all67 before the relocated B338 SMC operand.

The head/sweep test uses explicitly synthetic tile/position primitives and
a declared D660 tail spy. It does not claim natural vine traversal, block
birth or a 1UP collector. No helpers were added or moved. Natural 1UP,
equal-facing F090 exits, remaining abilities, audio and performance stay open.

## Frozen review interfaces

- C: `compose_prince_hidden_point67_ace_1115.py`, SHA `1fce2b546003860e31da49723c3ac185a25b5420e2ba88143434516c59a4ee27`.
- Full F: `replay_prince_hidden_point67_full_ace_1115.py`, SHA `fd0bd493ed522a2856a3f91a3300cf6ab1dc87ff91efa5ea3450e11ca2a4d371`; LF Lua `0b049ab2840bdd286f95dd9c8a88f4cfc374a5883ca43d58c01cb09f42421224`.
- Star F: `replay_prince_hidden_point67_star_ace_1115.py`, SHA `fbdd81a74f9259ff9a36bb1912d235fb300609f4e83f97597a7123c35f67b115`; LF Lua `ee13fbe7423a8e0f070e49b87d8313d45328c64672d00055dca70e5da6b4f589`.
- Same-control diagnostic F: SHA `c79c793680c362d945a4befabb46486d284f708c71e6673a63d2be158243d6d3`; LF Lua `461dd1ab6eb716e5510c6f36441425dfce36602f9b326716a2f1d7d0d0a095c9`.

Full API is `F.controller(candidate7fb3)`; Star API is
`F.controller(candidate7fb3, 'star', 8)`. Both require native variant3.
Root owns subsequent native staging and delivery. These source receipts
do not claim a native result or an installed nightly update.
