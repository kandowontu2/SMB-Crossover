# Metal Storm native sprite reservation — November 2

The installed MMC5 nightly now uses SHA256 `1cd8e192ee4bee33dfe0d9c737bec097e1cf2339e0b9f77353fd5194f2530f55`. The actual Downloads
launch passes the same cold-menu, idle/walk and OAM checks as the candidate.
The file was replaced directly, with no backup or sidecar patch.

The renderer was reserving player sprites through a null pose pointer. Its
first byte happened to be175, so the allocation advanced by a non-multiple of
four and eventually rotated tile/attribute/position bytes into the wrong OAM
fields. The visible body appeared displaced and scrambled. The private graphics
worker also supplied a pointer into a cache bank that did not remain mapped.

Movement and drawing now establish a zero-length reservation using the stable
native ObjectMetasprite byte. The original actor, sprite packets, shot logic
and physics stay intact. Six renderer bytes are added inside the existing
3072-byte allocation; genuine references are relocated and both full cookies
updated. No additional resident storage, RAM or helper platform is used.

Verification includes16 real public movement equivalence cases, every one of
32 single-byte full-header corruptions, and174 actual IRQ plus174 busy-NMI
interruption/return cases. A real cold native run observes74 aligned draw,
reservation and emission calls. The full non-shortcut route reaches active1-2
in5587physicalframes with a genuine native enemy defeat and lives2→2.

Performance in the empty opening remains120 Main updates per180 physical
idle frames and27/40 walking frames. This repair does not claim reduced lag.
The visible sprite is now coherent at its native position. The MARIO HUD name
and incorrect player palette remain open, along with original audio, upgrades,
gravity-related escape cases and shortcut/mode testing.

Compact source and evidence: `docs/qa/checkpoints/2026-11-02/metal-reservation-v42/`.
