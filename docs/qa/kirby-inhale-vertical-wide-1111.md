# Kirby inhale vertical wraparound

Current-ROM CPU replays used the actual Kirby menu selection, Start path,
parser, and Main. The scenes supplied actor and player coordinates. The
controller created the B edge and Kirby's code determined the outcome.

Across both facings, Easy and Hard, and grounded, rising, and descending
states, the 48 forward fresh-B cases had 24 immediate captures, 12
protected body overlaps, and 12 cases without a native overlap. None
lost health. The Easy descending no-B control stomped the same target.
Fresh B in that geometry captured it before the native stomp. Grounded
rear contact still caused injury, including with the opposite direction
and B pressed together, because the inhale kept Kirby's existing facing.
A real Up input followed by fresh B while inflated spawned an air puff.

The directed failure is separate from those working cases. At Y237 on
native Y page 1, fresh B could capture a Goomba at Y0 on the same page
when the horizontal gap was six pixels. The eight-bit subtraction
wrapped a separation of 237 pixels into the inhale window. In both modes
and both facings, the actual capture ran at opening age 8 and erased the
Goomba. This fixture establishes the faulty capture through Main. A
natural occurrence has yet to be observed.

The proposal keeps the same mouth center at player Y plus eight and the
same inclusive twelve-pixel vertical range. It subtracts both bytes of
the native world coordinates. A visible-page enemy may still be within
reach of a player just across a Y page boundary. The patch relocates the
unchanged six-byte pull-target routine into existing unreachable padding
and rewrites the adjacent 35-byte range. Three private calls follow the
updated addresses. The red-shell contact helper at `$AB19` is disjoint.

On exact parent `b1d449eb`, the in-memory `a1305ec9` candidate changes
38 bytes. All four directed wrap captures are rejected. The 200,911
coordinate cases include all 196,608 low-byte pairs across player pages
0, 1, and 2, and cover 210 valid top and 10 valid bottom page crossings.
The paired Main tests matched across 120 first updates, eight held or
released B sequences, and eight directional B edges. The real handler
tests passed 26 lag-NMI cuts, 26 scanline IRQ cuts, and one nested IRQ.

The red-shell and inhale changes also compose in memory into the
191-edit `852712c9` nightly on that same parent. The
[combined nightly report](kirby-red-sweep-1111.md) records the installed
controller-only Mesen replays.

- Assembly `tools/reference/kirby_inhale_vertical_wide_1111.s`
- Builder and tests `tools/audit/check_kirby_inhale_vertical_wide_1111.py`
