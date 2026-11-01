# Karnov rendering and projectile motion — private progress

Karnov is still COMING SOON in the installed 85-character nightly. This component
adds real body/shot rendering and original actor-to-weapon updates. It is not a
native stage clear, combat/upgrade completion, or release admission.

The 7441-byte kernel includes all 64 original facing/pose packets,
kept in their native OAM priority order. Five CHR pages remain sufficient: seven
original projectile patterns occupy verified unused pairs in body page 3.
Even projectile tiles use P0 window 3; world windows 4..7 are preserved.
The 1345-byte pose metadata is copied to conditional C2/D000, so native farcalls
can read it while A3 is unmapped. Hurt blinking keeps the actual source CHR page.

Original single/double/triple/boomerang updates run after the source actor.
Existing shots rebase before spawning at a new camera, and drawing accounts for
the native scroll that occurs after movement. Left-edge underflow never wraps a
projectile to the right. Palette commands write only 3F11..13, preserving the
NES universal background color at mirrored 3F00/10.

Evidence: 256 exact original body contexts, 768 shot contexts, 24 OAM capacity/
rotation cases, 644 coherent actor/projectile comparisons, 840 native block-query
comparisons, 420 native camera updates, and 434 real host
interrupt cuts. Two executions of the real normal-NMI palette writer verify
default/injured sprite colors and an unchanged universal background color.

Draw cost in these CPU fixtures ranges from 1901 to
5376 cycles. That is not a whole-game 60Hz claim.
sprite-preview.png is one bounded CPU-rendered pixel preview, not native footage.

The ZIP lists exact source/assets and compact receipts; it contains no ROM,
object/debug images, video or capture forest. Existing game linker objects and
the original donor are retained external inputs, not recursively archived here.
