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
