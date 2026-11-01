# Thomas: four native moving platforms and safe melee

All four prelisted1-1 pipe assists now use ordinary SMB vertical platform25:
native initialization, AI, support, carry and rendering. Existing level tiles
and the original27px donor jump stay unchanged. Importing completed native
carry before the next actor update and honoring native grounded state fixes
boarding/riding. The genuine donor jump-reset routine ends a landed jump.

A single cold controller-byte route clears pipes448/608/736/912, reachesX960
and defeats three enemies. All2073accepted actor frames match the original
donor instructions with the declared host projection. These are CPU-model
checks, not Mesen, raster or whole-stage qualification.

The original combat cut really reachedSP119 and corrupted stack-resident SMC.
The initial constructor-stack explanation was wrong: constructor entry was
safe. The final fix moves the exact12byte melee save, outgoing A and status
to its ownC860..C86D context during the unchanged native defeat/drop call.
Actual NMI and legally nested IRQ cuts now reach minimumSP131 and restore
registers, maps,33SMC bytes, borrowedR0..R7 and the live melee context exactly.
The newer220-frame combat check explicitly testsC860..C86D; the older route
checker tested the unusedC850gap and must not be cited for that context.

Original body CHR and native PRG instruction bytes remain exact; own cookie
digest changes authenticate the rebuilt kernel. Kernel6141/6144bytes fits.
New debug output keeps symbols while dropping regenerable bulk line records.
Rejected constructor-detachment and the first A/P-incomplete melee experiment
are not the implementation. The installed74-character ROM is unchanged.
