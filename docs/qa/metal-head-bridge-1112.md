# Metal Storm deferred native head effect, November 12

Private, composable source work. Root owns Mesen, installation and publication.
No ROM, capture, extracted tree or other generated output is written by these
tools. The unchanged flower files remain independently reproducible.

`compose_metal_head_bridge_1112.compose(raw)` first composes the qualified
flower item0 grant, then the deferred head bridge. `transform(flower_raw)`
applies only the head stage; `transform(head_raw, True)` exactly recovers its
flower parent. Every owned preimage is checked, preserving unrelated Prince,
menu and other changes. On the installed Prince/Menu parent this yields
`83cdb2d66691ffd1ea63c71c268eb44b8ea479d848b58afbf91c94fa2cf1c4bf`;
the flower intermediate is
`8439dea15d5570e002f1de81dbd34b2602f0f5ab84e3a6d6c51316ee0c351eff`.
Both complete cache headers use `a7232cd3586ce9901f54be4a259914ac`.

The retained v42 input is
`docs/qa/checkpoints/2026-11-02/metal-reservation-v42/inputs.zip`, SHA256
`f1548d2f32972aa150939ab9b33ab829aa4f19f60013cf813031ac21888724e9`.
Its members are read in memory; there is no historical extraction. Original
BA02 and FF36 and all source movement instructions remain intact. The sole
actor instruction replacement is the original `LDA source005B` at B798,
translated AD54, replaced with a JSR that returns the same A/N/Z. Its following
original SEC/SBC restores C/V before use. This seam follows the authentic
accepted head sweep and its distance check. Feet, side and projectile queries
do not reach it. Inverted anatomical head contacts do not manufacture an
upward native ceiling event.

The event aliases C880..C887 in the existing 33-byte native packet grant
(physical RAM2 offset2176, size33 in the November 1 owning resource grant).
Fields are tag A7, native epoch, metatile, original queried Y, native buffer
column/parity, queried X low, original negative source DY, and native Y before
source displacement export. This borrows packet storage only between movement
and native head consumption. Native rendering writes packet lengths0..32;
weapon enemy iteration uses5..0/FF, so neither can forge A7. The real GameCore
calls player movement/background before weapons, enemy iteration and draw.
The accepted update clears any older tag before original actor execution.
The getter consumes a valid tag before testing scene8, same epoch, the native
contact-time Y low nibble >=4, and the exact unchanged contacted cell. A later
foot or head query cannot reuse it. Ready revocation also rejects the record;
complete C2/C3 authentication and owner35 precede any cached opcode.

Root's live trace of the previous private candidate showed authentic contact
at world336/158, tileC1, sourceDYFA, nativeY164, followed by post-export
nativeY160. Receipt
`54a418ebfe7ad55e8d781ae1da6bb76af52fa9ce61c01809e4558b9e8478514b`
proved that the packet survived intact but the post-export low-Y test failed.
Saving the contact-time native Y preserves that native guard without changing
source physics, head height or snapped positions.

Source funding stays inside existing spans:

| Span | Used/capacity | Purpose |
| --- | --- | --- |
| RAM3 BFC0..BFDF |29/32|Head capture prefix|
| RAM2 D8AF..D8FF |81/81|One-shot exact-cell getter|
| RAM2 DCD9..DCFF |39/39|Capture tail after the stable flower313B|
| RAM3 B599..B5B6 |30/30|Original save point25B plus scene predicate5B|
| PRG36 BF46..BFBF |122/122|Copy68B, pad1, head wrapper26B, unchanged Fresh26B, pad1|
| PRG79 A707..A736 |45/48|Shared owner/row selector|
| PRG79 BFAD..BFCC |32/32|Sole-entry prefix and owner tables|

The old ROM copy tail was occupied by the Fresh helper; it was never granted
as free FF. Two identical Map calls and their LDX4 instructions are factored
into one helper. The sole copy caller follows successful original Zero with
X0, allowing STX R2. Successful CMP12 already supplies C1. The unchanged Fresh
bytes move BF9A→BFA5 with their sole Work target. The real cold load observes
X0, I-set Fresh entry, exactly24600 PPU reads, and both full headers published
last. No cached opcode executes during the cold loader.

Native HuHead alone routes owner35/row10 to ROM36 BF8B, whose low byte equals
the original authenticated row10 AB8B. It changes only the target high byte
before using the full existing ROM header transport. Failure falls back to
the exact original native head getter. Success publishes R2..R7, contact DY,
tile A/N/Z, X0, original Y/I/D and native row C/V; the ordinary native
PlayerBGCollision and PlayerHeadCollision then own block, coin, ceiling,
water, hurt and bounce effects.

CPU qualification on the installed Kirby catch parent yields head image
`0aef7ced802cbec5faa839035f3bd4125fb4fc5d8bf0ad2f90a80f89368e63d6`.
The checks cover 108 exact-cell cases with single consumption, six no-event
native ABI pairs, six event rejection causes, and 32 complete-header corruptions
that fall back to the native getter. Authentic B744→B798 contact preserves
source state and AXYP. The native background path spawns actor2E, changes the
contacted cell to23, and finishes the later foot probes with native DY0.
The shared router keeps all 333 owner/row destinations apart from Metal row10.
All 44 public head owner pairs pass, including 18 real router arrivals that
prove incoming A equals the selected owner. The source matrix covers 300
physics/AXYP pairs, including 12 accepted upward events. Two other native
probes leave a pending event untouched. The lifecycle checks cover 20 accepted
epoch clears, Fresh invalidation, and 108 pre-contact versus post-export
position and velocity cases.

The suite passes 157 IRQ and 169 FF lag-NMI cuts at a minimum stack pointer
of148. Cold loading passes a further 44 lag-NMI cuts at a minimum of167, and
five actual readback corruptions return CLC before either full header is
published. An NMI between the existing Fresh shadow write and its adjacent
hardware write can finish the mapping early. The test compares the actual
interrupt return and continuation against the uninterrupted write. The IRQ
checks cover the live head/source paths, while real cold Fresh enters with I
set.

Root Mesen now confirms one natural mushroom spawn and maturation with the
corrected candidate, receipt
`e84eb0071223d51db24848c6e293b8b80e2c3ee44fb8178ea766d1ea98006bbb`.
Root also cleared 1-1 into active 1-2 with both lives on the head and flower
image, receipt
`635fb94109e1559337a1342761fef5820697ba4cd704f11c82d156d54ba04779`.
The separate maturity change qualifies collection through the native actor
handler.

Commands, each reserving one file and producing zero:

```
python -B tools/audit/run_bounded_build_v1.py --output build/metal-head-cpu-1112 --max-files 1 --timeout 600 -- python -B tools/audit/check_metal_head_bridge_1112.py
python -B tools/audit/run_bounded_build_v1.py --output build/metal-head-cpu-1112 --max-files 1 --timeout 600 -- python -B tools/audit/check_metal_head_bridge_1112.py --faults-only
```
